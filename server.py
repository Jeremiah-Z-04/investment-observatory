import http.server, os, json, time, urllib.request, ssl
import dataservice, factors_engine, datetime, review_rules

PORT = 8765
DIR = os.path.dirname(os.path.abspath(__file__))
MIME = {".html":"text/html",".js":"application/javascript",".css":"text/css",".json":"application/json"}

def _fetch(url, timeout=8):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Referer": "https://data.eastmoney.com/"
    })
    resp = urllib.request.urlopen(req, timeout=timeout, context=ctx)
    return json.loads(resp.read().decode())

def fetch_market_indices():
    try:
        sh = _fetch("https://push2his.eastmoney.com/api/qt/stock/kline/get?secid=1.000001&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57&klt=101&fqt=0&end=20500101&lmt=5")
        sz = _fetch("https://push2his.eastmoney.com/api/qt/stock/kline/get?secid=0.399001&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57&klt=101&fqt=0&end=20500101&lmt=5")
        sh_kl = sh.get("data",{}).get("klines",[])
        sz_kl = sz.get("data",{}).get("klines",[])
        if sh_kl and sz_kl:
            sh_last = sh_kl[-1].split(",")
            sz_last = sz_kl[-1].split(",")
            sh_price = float(sh_last[2]) if len(sh_last)>2 else 0
            sz_price = float(sz_last[2]) if len(sz_last)>2 else 0
            sh_chg = round((float(sh_last[2])/float(sh_last[1])-1)*100,2) if len(sh_last)>2 and float(sh_last[1])>0 else 0
            sz_chg = round((float(sz_last[2])/float(sz_last[1])-1)*100,2) if len(sz_last)>2 and float(sz_last[1])>0 else 0
            if len(sh_kl)>=5:
                prices = [float(k.split(",")[2]) for k in sh_kl[-5:]]
                tracked_chg = round((prices[-1]/prices[-2]-1)*100,2) if len(prices)>=2 else -1.27
            else:
                tracked_chg = -1.27
            return [{"name":"\u4e0a\u8bc1\u6307\u6570","price":f"{sh_price:.2f}","change":sh_chg},{"name":"\u6df1\u8bc1\u6210\u6307","price":f"{sz_price:.2f}","change":sz_chg}], tracked_chg
    except Exception as e:
        import datetime as _dt2; open(os.path.join(DIR,"server_error.log"),"a",encoding="utf-8").write(f"[{_dt2.datetime.now().strftime(chr(37)+chr(72)+chr(58)+chr(37)+chr(77)+chr(58)+chr(37)+chr(83))}] Index fetch failed: {e}\n")
    return None, None

def fetch_northbound_total():
    try:
        d = _fetch("https://push2.eastmoney.com/api/qt/kamt.kline/get?fields1=f1,f2,f3,f4&fields2=f51,f52,f53,f54,f55,f56&klt=101&lmt=5")
        hk2sh = d.get("data",{}).get("hk2sh",[])
        hk2sz = d.get("data",{}).get("hk2sz",[])
        net = 0.0
        if hk2sh:
            parts = hk2sh[-1].split(",")
            net += abs(float(parts[2]))/1e8 if len(parts)>2 else 0
        if hk2sz:
            parts = hk2sz[-1].split(",")
            net += abs(float(parts[2]))/1e8 if len(parts)>2 else 0
        return round(net, 1) if net > 0 else 12.5
    except Exception as e:
        import datetime as _dt2; open(os.path.join(DIR,"server_error.log"),"a",encoding="utf-8").write(f"[{_dt2.datetime.now().strftime(chr(37)+chr(72)+chr(58)+chr(37)+chr(77)+chr(58)+chr(37)+chr(83))}] Northbound failed: {e}\n")
    return 12.5

def build_nb_sectors(nb_total):
    total = max(nb_total, 1.0)
    weight = total / 25.0
    return [
        {"sector":"AI\u7b97\u529b/\u5149\u6a21\u5757","net":round(8.0*weight,1),"ratio":f"{round(8.0*weight/total*100,1)}%","topStock":"\u4e2d\u9645\u65ed\u521b"},
        {"sector":"\u534a\u5bfc\u4f53\u8bbe\u5907","net":round(5.5*weight,1),"ratio":f"{round(5.5*weight/total*100,1)}%","topStock":"\u5317\u65b9\u534e\u521b"},
        {"sector":"\u5b58\u50a8\u82af\u7247","net":round(4.0*weight,1),"ratio":f"{round(4.0*weight/total*100,1)}%","topStock":"\u5146\u6613\u521b\u65b0"},
        {"sector":"PCB/\u94dc\u7b94","net":round(-2.5*weight,1),"ratio":f"-{round(2.5*weight/total*100,1)}%","topStock":"\u6df1\u5357\u7535\u8def"},
        {"sector":"\u6d88\u8d39\u7535\u5b50","net":round(-5.0*weight,1),"ratio":f"-{round(5.0*weight/total*100,1)}%","topStock":"\u7acb\u8baf\u7cbe\u5bc6"},
        {"sector":"\u9762\u677f/\u663e\u793a","net":round(-3.0*weight,1),"ratio":f"-{round(3.0*weight/total*100,1)}%","topStock":"\u4eac\u4e1c\u65b9A"},
    ]


# ====== History Tracker ======
import threading
class HistoryTracker:
    def __init__(self, max_points=180):
        self._data = []
        self._lock = threading.Lock()
        self._max = max_points
    def add(self, entry):
        import time
        with self._lock:
            entry["_ts"] = time.time()
            self._data.append(entry)
            cutoff = time.time() - 1800
            self._data = [d for d in self._data if d.get("_ts",0) > cutoff]
            if len(self._data) > self._max:
                self._data = self._data[-self._max:]
    def get_trend(self):
        with self._lock:
            result = []
            for d in self._data:
                entry = {"ts": int(d.get("_ts",0)*1000), "composite": d.get("composite",0)}
                for f in d.get("factors", []):
                    entry[f["id"]] = f["score"]
                result.append(entry)
            return result

history = HistoryTracker()
# ====== Industry Chain Config Loader ======
INDUSTRY_CONFIG_FILE = os.path.join(DIR, "industry_chain_config.json")

def load_industry_config():
    try:
        with open(INDUSTRY_CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"[industry] config load error: {e}")
        return {"industries": []}

def save_industry_config(data):
    try:
        with open(INDUSTRY_CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
    except Exception as e:
        print(f"[industry] config save error: {e}")

def get_node_upstream_downstream(nodes, node_id):
    node = None
    for n in nodes:
        if n["id"] == node_id:
            node = n
            break
    if not node:
        return {"upstream": [], "downstream": []}
    upstream = []
    if node.get("parent_id"):
        for n in nodes:
            if n["id"] == node["parent_id"]:
                upstream.append({"id": n["id"], "name": n["name"]})
                break
    downstream = []
    for n in nodes:
        if n.get("parent_id") == node_id:
            downstream.append({"id": n["id"], "name": n["name"]})
    return {"upstream": upstream, "downstream": downstream}


# Seed with initial data point so trend chart not empty
history.add({"composite":50,"outlook":"neutral","factors":[{"id":"sentiment","score":50},{"id":"sector","score":50},{"id":"chip","score":50},{"id":"overnight","score":50}]})

class H(http.server.BaseHTTPRequestHandler):
    def log_message(self,*a): pass
    def js(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type","application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin","*")
        self.send_header("Content-Length",str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def serve_file(self, path):
        if path == "/": path = "/index.html"
        safe = path.lstrip("/")
        if ".." in safe:
            self.js({"error":"forbidden"},403)
            return
        fp = os.path.join(DIR, safe)
        if not os.path.isfile(fp):
            self.js({"error":"not found"},404)
            return
        with open(fp,"rb") as f:
            data = f.read()
        ext = os.path.splitext(fp)[1].lower()
        self.send_response(200)
        self.send_header("Content-Type", MIME.get(ext, "application/octet-stream"))
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        try:
            p = self.path.split("?")[0]
            ts = time.strftime("%H:%M:%S")
            if p == "/api/ping":
                self.js({"status":"ok","time":ts})
            elif p == "/api/sectors":
                sc = dataservice.cache.get("sectors")
                if sc and sc.get("data"):
                    self.js({"success":True,"data":sc["data"],"ts":sc.get("snapshot_time",ts)})
                else:
                    self.js({"success":True,"data":[],"ts":ts})
            elif p == "/api/review/stocks":
                rs = dataservice.cache.get("review_stocks")
                if rs and rs.get("data"):
                    d = rs["data"]
                    # 排序处理
                    import urllib.parse as up2
                    qs2 = up2.parse_qs(self.path.split("?")[1] if "?" in self.path else "")
                    sort_by = (qs2.get("sort") or [""])[0]
                    sort_limit = int((qs2.get("limit") or ["0"])[0]) if (qs2.get("limit") or [""])[0].isdigit() else 20
                    rlist = d.get("list", [])
                    if sort_by == "amount":
                        rlist = sorted(rlist, key=lambda x: float(x.get("amount",0) or 0), reverse=True)
                    elif sort_by == "change":
                        rlist = [s for s in rlist if not (s.get("name","").startswith("N") or s.get("name","").startswith("C") or "ST" in s.get("name",""))]
                        rlist = sorted(rlist, key=lambda x: float(x.get("change",0) or 0), reverse=True)
                    if sort_limit > 0 and len(rlist) > sort_limit:
                        rlist = rlist[:sort_limit]
                    self.js({"success":True,"data":rlist,"update_time":d.get("update_time",ts),"ts":ts,"stale":rs.get("stale",False),"data_source":d.get("source","fallback")})
                else:
                    self.js({"success":True,"data":[],"update_time":ts,"ts":ts})
            elif p == "/api/volume/monitor":
                try:
                    is_tr = dataservice.is_trading_time()
                    if is_tr:
                        # Read from cache (periodically updated by bg thread)
                        tl, yl, combined_list, ds, snap = [], [], [], "fallback", None
                        cached_vm = dataservice.cache.get("volume_monitor")
                        cached_data = cached_vm.get("data", {}) if cached_vm and isinstance(cached_vm, dict) else {}
                        if isinstance(cached_data, dict):
                            tl = cached_data.get("today_list", []) or []
                            yl = cached_data.get("yesterday_list", []) or []
                            if tl:
                                combined_list = tl
                                ds = cached_data.get("data_status", "live")
                            elif yl:
                                combined_list = yl
                                ds = cached_data.get("data_status", "yesterday")
                        # Fallback to snapshot if cache is empty
                        if not combined_list:
                            snap = dataservice.load_latest_snapshot()
                            snap_list = (snap or {}).get("volume_monitor_list", []) or []
                            if snap_list:
                                yl = snap_list
                                combined_list = snap_list
                                ds = "close"
                        vm_ts = time.strftime("%H:%M:%S")
                        self.js({
                            "success": True,
                            "is_trading": True,
                            "data_status": ds,
                            "update_time": vm_ts,
                            "total": len(tl) + len(yl),
                            "data": {
                                "list": combined_list,
                                "today_list": tl,
                                "yesterday_list": yl,
                                "yesterday_date": (snap or {}).get("date", ""),
                                "yesterday_total": len(yl)
                            }
                        })
                    else:
                        # Non-trading: return cached data (prefer cache, fallback snapshot)
                        vm_list = []
                        snap = None
                        cached_vm = dataservice.cache.get("volume_monitor")
                        cd = cached_vm.get("data", {}) if cached_vm and isinstance(cached_vm, dict) else {}
                        if isinstance(cd, dict):
                            vm_list = cd.get("today_list", []) or cd.get("yesterday_list", []) or []
                        if not vm_list:
                            snap = dataservice.load_latest_snapshot()
                            if snap and snap.get("volume_monitor_list"):
                                vm_list = snap["volume_monitor_list"]
                        self.js({
                            "success": True,
                            "is_trading": False,
                            "data_status": "close",
                            "update_time": (snap or {}).get("update_time", ts),
                            "total": len(vm_list),
                            "data": {
                                "list": vm_list,
                                "today_list": [],
                                "yesterday_list": vm_list,
                                "yesterday_date": (snap or {}).get("date", ""),
                                "yesterday_total": len(vm_list)
                            }
                        })
                except Exception as e:
                    import traceback; traceback.print_exc()
                    self.js({"success": False, "error": str(e), "data": {"list": []}}, 500)

            elif p == "/api/factors":
                try:
                    # Try live data first, fall back to snapshot for non-trading hours
                    # Unified data entry: live during trading, snapshot otherwise
                    _ldd = dataservice.get_market_data("limit_stats")
                    _ov = dataservice.get_market_data("market_overview")
                    _idx = dataservice.get_market_data("market_indices")
                    _nb_raw = dataservice.get_market_data("northbound")
                    _nb = _nb_raw.get("data", 0) if isinstance(_nb_raw, dict) else (_nb_raw or 0)
                    _factors = dataservice.get_market_data("factors_score") or {}
                    composite = _factors.get("composite", 50) if _factors else 50
                    # Build market dict
                    limit_up = int((_ldd or {}).get("limitUp", 0) or 0)
                    limit_down = int((_ldd or {}).get("limitDown", 0) or 0)
                    bomb_rate = round(float((_ldd or {}).get("brokenRatio", 0.0) or 0.0), 1)
                    turnover = round(float((_idx or {}).get("trackedVolume", 0) or 0), 1)
                    nb_net = round(float(_nb), 1) if isinstance(_nb, (int,float)) else 0
                    max_board = int((_ldd or {}).get("maxBoardHeight", 0) or 0)
                    market = {
                        "limit_up_count": limit_up,
                        "limit_down_count": limit_down,
                        "bomb_rate": bomb_rate,
                        "turnover_total": turnover,
                        "northbound_net": nb_net,
                        "max_board_height": max_board
                    }
                    # For factor engine, create a compat cache getter
                    def _cache_or_snapshot(key):
                        # Handle limit_up_down from Sina data
                        if key == "limit_up_down":
                            try:
                                sc = dataservice.cache.get("review_stocks")
                                if sc and sc.get("data"):
                                    sdata = sc["data"]
                                    if isinstance(sdata, list) and len(sdata) > 50:
                                        up = sum(1 for s in sdata if float(s.get("change",0) or 0) >= 9.5)
                                        dn = sum(1 for s in sdata if float(s.get("change",0) or 0) <= -9.5)
                                        rise = sum(1 for s in sdata if float(s.get("change",0) or 0) > 0)
                                        fall = sum(1 for s in sdata if float(s.get("change",0) or 0) < 0)
                                        total_amt = sum(float(s.get("amount",0) or 0) for s in sdata) / 1e8
                                        val = {
                                            "limitUp": up, "limitDown": dn,
                                            "limit_up_count": up, "limit_down_count": dn,
                                            "up_count": rise, "down_count": fall,
                                            "riseCount": rise, "fallCount": fall,
                                            "turnover_total": round(total_amt, 1),
                                            "bomb_rate": 0, "bomb_count": 0, "brokenRatio": 0,
                                            "yest_premium": 0, "max_board_height": 0
                                        }
                                        dataservice.cache.set("limit_up_down", val, "limit_up_down")
                                        return val
                            except:
                                pass
                        # Handle market_overview / market_indices from limit_up_down
                        if key in ("market_overview", "market_indices"):
                            lud = dataservice.cache.get("limit_up_down")
                            if lud and lud.get("data"):
                                d = lud["data"]
                                result = {
                                    "riseCount": d.get("rise_count", d.get("up_count", 0)),
                                    "fallCount": d.get("fall_count", d.get("down_count", 0)),
                                    "trackedVolume": d.get("turnover_total", 0),
                                    "turnover_total": d.get("turnover_total", 0),
                                    "sh_change": d.get("sh_change", 0)
                                }
                                return result
                        # Handle sectors - return list
                        if key == "sectors":
                            return []
                        # Handle northbound
                        if key == "northbound":
                            return {"data": 0}
                        # Fallback
                        val = dataservice.get_market_data(key)
                        return val
                    result = factors_engine.calc_all_factors(_cache_or_snapshot)
                    import sys
                    sys.stderr.write(f"[debug] factors result: composite={result.get('composite')}, factors={len(result.get('factors',[]))}\n")
                    composite = result.get("composite", 50)
                    outlook = result.get("outlook", "neutral")
                    factors = result.get("factors", [])
                    prev_snap = dataservice.get_latest_snapshot()
                    prev_day = None
                    if prev_snap:
                        prev_day = prev_snap.get("data", {}).get("market", {})
                    advice = {}
                    if hasattr(factors_engine, "calc_daily_advice"):
                        try:
                            advice = factors_engine.calc_daily_advice(composite, factors)
                        except:
                            advice = {}
                    is_live = dataservice.is_trading_time()
                    data_tip = "实时数据" if is_live else ("收盘数据" + ((" " + prev_snap.get("date","")) if prev_snap else ""))
                    history.add({"composite": composite, "outlook": outlook, "factors": factors}); dataservice.cache.set("factors_history", history._data[:], "news")
                    self.js({"success": True, "composite": composite, "outlook": outlook,
                        "outlook_desc": result.get("outlook_desc", ""),
                        "factors": factors, "market": market, "advice": advice,
                        "prev_day": {"composite_score": composite, "market": prev_day} if prev_day else None,
                        "is_live": is_live, "ts": time.strftime("%H:%M:%S"),
                        "data_tip": data_tip})
                except Exception as e:
                    import traceback; traceback.print_exc()
                    self.js({"success": False, "error": str(e)})
            elif p == "/api/factors/history":
                try:
                    data = history.get_trend()
                    if not data or len(data) < 2:
                        # Fall back to snapshot trend data
                        snap = dataservice.load_latest_snapshot()
                        if snap and snap.get("trend_history"):
                            data = snap["trend_history"]
                    self.js({"success": True, "data": data})
                except Exception as e:
                    self.js({"success": False, "error": str(e), "data": []})
            elif p == "/api/industry/chain":
                config = load_industry_config()
                self.js({"success": True, "data": config, "ts": ts})
            elif p.startswith("/api/industry/node/"):
                node_id = p.split("/")[-1]
                if node_id in ("node", ""):
                    self.js({"success": False, "error": "invalid node id"})
                else:
                    config = load_industry_config()
                    found = None
                    for ind in config.get("industries", []):
                        for n in ind.get("nodes", []):
                            if n["id"] == node_id:
                                rel = get_node_upstream_downstream(ind["nodes"], node_id)
                                n["upstream"] = rel["upstream"]
                                n["downstream"] = rel["downstream"]
                                found = {"node": n, "industry": {"id": ind["id"], "name": ind["name"]}}
                                break
                        if found:
                            break
                    if found:
                        self.js({"success": True, "data": found, "ts": ts})
                    else:
                        self.js({"success": False, "error": "node not found"})
            elif p == "/api/events":
                self.js({"success":True,"data":[
                    {"date":"06-03","title":"\u82f1\u4f1f\u8fbeGTC\u5927\u4f1a","impact":"high","type":"conference"},
                    {"date":"06-10","title":"HBM\u5b63\u5ea6\u8c03\u4ef7\u7a97\u53e3","impact":"high","type":"pricing"},
                    {"date":"06-15","title":"\u5de5\u4fe1\u90e8AI\u4ea7\u4e1a\u653f\u7b56","impact":"medium","type":"policy"},
                ]})
            elif p == "/api/companies":
                self.js({"success":True,"data":[]})
            elif p == "/api/tracking":
                try:
                    with open(os.path.join(DIR,"tracking_config.json"),"r",encoding="utf-8") as f:
                        self.js({"success":True,"data":json.load(f),"ts":ts})
                except Exception:
                    self.js({"success":True,"data":{},"ts":ts})
            elif p == "/api/stock/search":
                import urllib.parse
                kw = urllib.parse.parse_qs(self.path.split("?")[1] if "?" in self.path else "").get("keyword", [""])[0]
                if not kw:
                    self.js({"success":False,"error":"keyword required"})
                else:
                    try:
                        url = "https://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=20&po=1&np=1&fields=f12,f14,f100&fid=f12&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23&fl=" + urllib.parse.quote(kw)
                        d = dataservice._fetch_json(url)
                        stocks = []
                        if d and d.get("data",{}).get("diff"):
                            for it in d["data"]["diff"]:
                                code = str(it.get("f12",""))
                                name = it.get("f14","")
                                industry = it.get("f100","")
                                if code and name:
                                    stocks.append({"code":code,"name":name,"industry":industry,"market":"sz" if code.startswith(("0","3")) else "sh" if code.startswith(("6","9")) else "bj"})
                        self.js({"success":True,"data":stocks,"ts":ts})
                    except Exception as e:
                        self.js({"success":False,"error":str(e)})
            elif p == "/api/review/watchlist":
                import urllib.parse as up
                wf = os.path.join(DIR, "review_watchlist.json")
                if self.command == "GET":
                    if os.path.exists(wf):
                        wdata = json.load(open(wf, "r", encoding="utf-8"))
                        self.js({"success":True,"data":wdata.get("list",[]),"ts":ts})
                    else:
                        # Default list from fallback
                        fb = dataservice._get_fallback_review_stocks()
                        self.js({"success":True,"data":fb.get("list",[]),"ts":ts})
            elif self.path.startswith("/api/review/watchlist/add"):
                try:
                    params = up.parse_qs(self.path.split("?")[1] if "?" in self.path else "")
                    codes = params.get("code", [])
                    if not codes:
                        self.js({"success":False,"error":"code required"})
                    else:
                        if os.path.exists(wf):
                            wdata = json.load(open(wf, "r", encoding="utf-8"))
                        else:
                            wdata = {"list":[]}
                        existing = {s["code"] for s in wdata["list"]}
                        added = 0
                        for code in codes:
                            if code not in existing:
                                wdata["list"].append({"code":code,"name":"","price":0,"change":0,"amount":0,"turnover":0,"sector":""})
                                existing.add(code)
                                added += 1
                        json.dump(wdata, open(wf, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
                        self.js({"success":True,"added":added,"total":len(wdata["list"]),"ts":ts})
                except Exception as e:
                    self.js({"success":False,"error":str(e)})
            elif self.path.startswith("/api/review/watchlist/remove"):
                try:
                    params = up.parse_qs(self.path.split("?")[1] if "?" in self.path else "")
                    codes = params.get("code", [])
                    if not codes:
                        self.js({"success":False,"error":"code required"})
                    else:
                        if os.path.exists(wf):
                            wdata = json.load(open(wf, "r", encoding="utf-8"))
                        else:
                            wdata = {"list":[]}
                        before = len(wdata["list"])
                        codes_set = set(codes)
                        wdata["list"] = [s for s in wdata["list"] if s["code"] not in codes_set]
                        removed = before - len(wdata["list"])
                        json.dump(wdata, open(wf, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
                        self.js({"success":True,"removed":removed,"total":len(wdata["list"]),"ts":ts})
                except Exception as e:
                    self.js({"success":False,"error":str(e)})
            elif p.startswith("/api/stock/"):
                code = p.split("/")[-1]
                if code in ("stock", ""):
                    self.js({"success":False,"error":"invalid code"})
                else:
                    result = factors_engine.calc_all_factors(lambda k: (dataservice.cache.get(k) or {}).get("data"))
                    self.js({"success":True,"code":code,"ts":ts,"composite":result.get("composite",50),"outlook":result.get("outlook","neutral"),"factors":result.get("factors",[])})

            elif p == "/api/review/summary":
                self._handle_review_summary()
            else:
                self.serve_file(p)
        except Exception as e:
            self.js({"error":str(e)},500)
    def _handle_stock_info(self):
        """Return single stock info from cache (for 次日作战计划)"""
        try:
            from urllib.parse import urlparse, parse_qs
            params = parse_qs(urlparse(self.path).query)
            code = (params.get("code") or [""])[0]
            if not code:
                self.js({"success": False, "error": "code required"}, 400)
                return
            rs_data = dataservice.cache.get("review_stocks")
            rs_list = ((rs_data or {}).get("data", {}) or {}).get("list", []) or []
            stock = None
            for s in rs_list:
                if s.get("code", "") == code:
                    stock = s
                    break
            if not stock:
                sec_data = dataservice.cache.get("sectors")
                sec_list = (sec_data or {}).get("data", []) or []
                self.js({"success": True, "code": code, "found": False, "sectors": [s.get("sector","") for s in sec_list[:5]]})
                return
            self.js({
                "success": True, "code": code, "found": True,
                "name": stock.get("name", ""),
                "price": stock.get("price", 0),
                "change": stock.get("change", 0),
                "amount": stock.get("amount", 0),
                "sector": stock.get("sector", ""),
                "turnover": stock.get("turnover", 0)
            })
        except Exception as e:
            self.js({"success": False, "error": str(e)}, 500)

    def _calc_sentiment_phase(self, m):
        luc = m.get("limit_up_count", 0)
        ldc = m.get("limit_down_count", 0)
        br = m.get("bomb_rate", 50)
        prem = m.get("yest_premium", 0)
        mh = m.get("max_board_height", 0)
        if luc < 20 or ldc > 15 or (prem is not None and prem < -2):
            return chr(20912)+chr(28857), chr(20111)+chr(38065)+chr(25928)+chr(24212)
        if luc > 80 or (br > 30 and prem is not None and prem < 1):
            return chr(39640)+chr(28526), chr(20111)+chr(38065)+chr(25928)+chr(24212)
        if ldc > 10 or (prem is not None and prem < 0):
            return chr(36864)+chr(28526), chr(20111)+chr(38065)+chr(25928)+chr(24212)
        if luc > 50 and (prem is not None and prem > 3) and mh >= 4:
            return chr(20027)+chr(21319), chr(36186)+chr(38065)+chr(25928)+chr(24212)
        if 25 <= luc <= 45 and prem is not None and 1 <= prem <= 3:
            return chr(21551)+chr(21160), chr(36186)+chr(38065)+chr(25928)+chr(24212)
        return chr(33391)+chr(24615)+chr(20998)+chr(27491), chr(20013)+chr(24615)

    def _calc_trend_days(self):
        snapshots = getattr(dataservice, "_load_snapshots", lambda: {})()
        if not snapshots:
            return 1, chr(36186)+chr(38065)+chr(25928)+chr(24212)
        dates = sorted(snapshots.keys())
        recent = dates[-5:] if len(dates) >= 5 else dates
        pos_days = 0; neg_days = 0
        for d in reversed(recent):
            mkt = snapshots[d].get("market", {})
            luc = mkt.get("limit_up_count", 0)
            br = mkt.get("bomb_rate", 50)
            if luc > 30 and br < 25:
                pos_days += 1; neg_days = 0
            elif luc < 20:
                neg_days += 1; pos_days = 0
            else:
                break
        if pos_days > 0:
            return pos_days, chr(36186)+chr(38065)+chr(25928)+chr(24212)
        return max(neg_days, 1), chr(20111)+chr(38065)+chr(25928)+chr(24212)

    def _handle_review_summary(self):
        try:
            ts = time.strftime("%H:%M:%S")
            sc = dataservice.cache.get("review_stocks")
            sdata = []
            if sc and sc.get("data"):
                d = sc["data"]
                if isinstance(d, list) and len(d) > 50:
                    sdata = d
            luc = sum(1 for s in sdata if float(s.get("change",0) or 0) >= 9.5)
            ldc = sum(1 for s in sdata if float(s.get("change",0) or 0) <= -9.5)
            rise = sum(1 for s in sdata if float(s.get("change",0) or 0) > 0)
            fall = sum(1 for s in sdata if float(s.get("change",0) or 0) < 0)
            total_amt = sum(float(s.get("amount",0) or 0) for s in sdata)
            total_amt_yi = round(total_amt / 1e8, 1) if total_amt else 0
            stocks_with_sector = [s for s in sdata if s.get("sector")]
            _idx = dataservice.get_market_data("market_indices", {}) or {}
            _ov = dataservice.get_market_data("market_overview", {}) or {}
            sh_chg = round(float(_ov.get("sh_change", 0) or 0), 2)
            sz_chg = round(float(_ov.get("sz_change", 0) or 0), 2)
            cyb_chg = round(float(_ov.get("cyb_change", 0) or 0), 2)
            if sh_chg == 0 and sz_chg == 0:
                _indices = _idx.get("indices", [])
                for ind in _indices:
                    n = ind.get("name", "")
                    if "上证" in n or "上证" in n:
                        sh_chg = round(float(ind.get("change",0) or 0), 2)
                    elif "深证" in n or "深证" in n:
                        sz_chg = round(float(ind.get("change",0) or 0), 2)
                    elif "创业" in n or "创业" in n:
                        cyb_chg = round(float(ind.get("change",0) or 0), 2)
            turnover_total = round(float(_idx.get("trackedVolume", 0) or 0), 1)
            if not turnover_total: turnover_total = total_amt_yi
            yest_prem_data = dataservice.cache.get("yest_limit_up_premium")
            yest_prem = None
            if yest_prem_data and yest_prem_data.get("data") is not None:
                yest_prem = round(float(yest_prem_data["data"]), 2)
            market = {"sh_change": sh_chg, "sz_change": sz_chg, "cyb_change": cyb_chg, "turnover_total": turnover_total, "up_count": rise, "down_count": fall, "limit_up_count": luc, "limit_down_count": ldc, "bomb_rate": 0.0, "yest_premium": yest_prem, "max_board_height": 0}
            limit_up_candidates = [s for s in sdata if float(s.get("change",0) or 0) >= 9.5]
            board_stocks = sorted([{"code": s.get("code",""), "name": s.get("name",""), "board_count": 1, "sector": s.get("sector","")} for s in limit_up_candidates[:30]], key=lambda x: -x["board_count"])
            rs_sorted_amount = sorted(sdata, key=lambda x: -(float(x.get("amount",0) or 0)))
            top_amount = [{"code": s.get("code",""), "name": s.get("name",""), "change": s.get("change",0), "amount": round(float(s.get("amount",0) or 0)/1e8,1), "sector": s.get("sector","")} for s in rs_sorted_amount[:20]]
            filtered_for_change = [s for s in sdata if not (s.get("name","") or "").startswith("N") and not (s.get("name","") or "").startswith("*") and not "ST" in ((s.get("name","") or "").upper())]
            rs_sorted_change = sorted(filtered_for_change, key=lambda x: -(float(x.get("change",0) or 0)))
            top_change = [{"code": s.get("code",""), "name": s.get("name",""), "change": s.get("change",0), "sector": s.get("sector","")} for s in rs_sorted_change[:20]]
            phase, effect = self._calc_sentiment_phase(market)
            days, _ = self._calc_trend_days()
            sector_map = {}
            for s in stocks_with_sector:
                sec = s.get("sector", "") or ""
                if sec:
                    if sec not in sector_map: sector_map[sec] = {"stocks": [], "total_change": 0, "count": 0}
                    sector_map[sec]["stocks"].append(s.get("name",""))
                    sector_map[sec]["total_change"] += float(s.get("change",0) or 0)
                    sector_map[sec]["count"] += 1
            sorted_sectors = sorted(sector_map.items(), key=lambda x: -x[1]["count"])
            core_sectors = []
            for sec_name, sec_data in sorted_sectors[:3]:
                sec_stocks_sorted = sorted(sec_data["stocks"], key=lambda n: -(float(next((s.get("change",0) for s in sdata if s.get("name","") == n), 0) or 0)))
                core_sectors.append({"topic": sec_name, "stocks": sec_stocks_sorted[:5], "count": sec_data["count"]})
            survivor_stocks = []
            _sorted_by_vol = sorted(limit_up_candidates, key=lambda x: -(float(x.get("volume",0) or 0)))
            for s in _sorted_by_vol[:15]:
                name = s.get("name", ""); code = s.get("code", ""); sec = s.get("sector", "") or ""
                if code and name:
                    tag = "连板活口" if float(s.get("change",0) or 0) >= 9.9 else "首板涨停"
                    unique_guess = sec + "领涨" if sec else "涨停板"
                    survivor_stocks.append({"code": code, "name": name, "tag": tag, "uniqueness": unique_guess})
            wind_vane = "关注市场竞价强度，如高开放量则确认主线延续"
            if core_sectors:
                top_sec = core_sectors[0]["topic"]
                wind_vane = "关注" + top_sec + "板块竞价强度，如高开放量则确认主线延续"
            is_live = dataservice.is_trading_time()
            result = {"success": True, "update_time": ts, "is_live": is_live, "market": market, "board_stocks": board_stocks[:20], "top_amount": top_amount, "top_change": top_change, "survivor_stocks": survivor_stocks[:10], "sentiment_stage": phase, "effect_type": effect, "effect_days": days, "core_sectors": core_sectors, "wind_vane": wind_vane}
            self.js(result)
        except Exception as e:
            import traceback as _tb
            self.js({"success": False, "error": str(e), "tb": _tb.format_exc()[:500]}, 500)


    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            if length > 0:
                body = json.loads(self.rfile.read(length).decode("utf-8"))
            else:
                body = {}
            p = self.path.split("?")[0]

            ldd = dataservice.get_market_data("limit_stats", {}) or {}
            ov = dataservice.get_market_data("market_overview", {}) or {}
            idx = dataservice.get_market_data("market_indices", {}) or {}
            sec_raw = dataservice.get_market_data("sectors", []) or []
            sec_list = sec_raw if isinstance(sec_raw, list) else (sec_raw.get("list", []) if isinstance(sec_raw, dict) else [])
            rs_raw = dataservice.get_market_data("all_stocks", []) or []
            rs_list = rs_raw if isinstance(rs_raw, list) else (rs_raw.get("list", []) if isinstance(rs_raw, dict) else [])
            up_stocks = ldd.get("limitUpStocks", []) or []
            bomb_stocks = ldd.get("bombStocks", []) or []

            sentiment = review_rules.calc_sentiment_stage({
                "limit_up_count": ldd.get("limit_up_count", 0) or 0,
                "limit_down_count": ldd.get("limit_down_count", 0) or 0,
                "bomb_rate": float(ldd.get("bomb_rate", 0.0) or 0.0),
                "yest_premium": ldd.get("yestPremium", 0) or 0,
                "max_board_height": ldd.get("maxBoardHeight", 0) or 0
            })

            if p == "/api/review/generate1":
                rs_sorted_amount = sorted(rs_list, key=lambda x: -(x.get("amount", 0) or 0))
                rs_sorted_change = sorted(rs_list, key=lambda x: -(x.get("change", 0) or 0))
                top_change = [{"code":s.get("code",""),"name":s.get("name",""),"change":s.get("change",0),"sector":s.get("sector","")} for s in rs_sorted_change[:20]]
                market = {
                    "limit_up_count": ldd.get("limit_up_count", 0) or 0,
                    "limit_down_count": ldd.get("limit_down_count", 0) or 0,
                    "bomb_rate": round(float(ldd.get("bomb_rate", 0.0) or 0.0), 1),
                    "yest_premium": ldd.get("yestPremium", 0) or 0,
                    "max_board_height": ldd.get("maxBoardHeight", 0) or 0,
                    "turnover_total": idx.get("trackedVolume", 0) or 0,
                    "up_count": ov.get("riseCount", 0) or 0,
                    "down_count": ov.get("fallCount", 0) or 0,
                }
                core_sectors = review_rules.calc_core_sectors(top_change)
                survivors = review_rules.calc_survivor_stocks(up_stocks, bomb_stocks)
                wind_vane = review_rules.calc_wind_vane(core_sectors, sec_list)
                text = review_rules.format_template1(market, sentiment, core_sectors, survivors, wind_vane)
                self.js({"success": True, "text": text})

            elif p == "/api/review/generate2":
                targets = body.get("targets", [])
                risk_threshold = float(body.get("risk_threshold", 5000))
                sector_map = {}
                sector_stocks = {}
                for s in rs_list:
                    sec = s.get("sector", "") or ""
                    if sec:
                        sector_map[s.get("code","")] = sec
                        if sec not in sector_stocks:
                            sector_stocks[sec] = []
                        sector_stocks[sec].append(s)
                battle = review_rules.gen_battle_plan(targets, risk_threshold, sector_map, sector_stocks)
                text = review_rules.format_template2(battle["text"])
                self.js({"success": True, "text": text})

            elif p == "/api/review/generate3":
                cost = float(body.get("cost", 0))
                price = float(body.get("price", 0))
                situation = body.get("situation", "")
                sector_limit_count = int(body.get("sector_limit_count", 0))
                diag = review_rules.calc_intraday_diagnosis(cost, price, situation, sector_limit_count, sentiment["stage"])
                text = review_rules.format_template3(diag)
                self.js({"success": True, "text": text})

            else:
                self.js({"success": False, "error": "unknown endpoint"}, 404)
        except Exception as e:
            import traceback
            self.js({"success": False, "error": str(e)}, 500)
    @staticmethod
    def _fast_fetch(url, timeout=4):
        import urllib.request as _ur
        import ssl as _ssl
        try:
            _ctx = _ssl.create_default_context()
            _ctx.check_hostname = False
            _ctx.verify_mode = _ssl.CERT_NONE
            _req = _ur.Request(url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://data.eastmoney.com/"})
            _resp = _ur.urlopen(_req, timeout=timeout, context=_ctx)
            return json.loads(_resp.read().decode())
        except:
            return None

class RS(http.server.ThreadingHTTPServer):
    allow_reuse_address = True

dataservice.start()

if __name__ == "__main__":
    import os; open(os.path.join(DIR,"server_ready.log"),"w").write("ready")
    RS(("0.0.0.0",PORT),H).serve_forever()
