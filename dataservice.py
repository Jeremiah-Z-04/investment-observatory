# -*- coding: utf-8 -*-
"""dataservice.py - 实时数据获取层"""
import json, time, threading, urllib.request, ssl, os, re, random
from datetime import datetime
try:
    import supabase_service
except ImportError:
    supabase_service = None

CACHE_TTL = {
    "market": 15, "sentiment": 30, "sector": 30, "northbound": 60,
    "news": 300, "review_stocks": 15, "limit_up_down": 15,
    "market_overview": 30, "market_indices": 30, "yest_limit_up_premium": 600,
    "volume": 900, "indices": 30
}
DIR = os.path.dirname(os.path.abspath(__file__))
SNAPSHOT_DIR = os.path.join(DIR, "snapshots")
LATEST_SNAPSHOT_FILE = os.path.join(SNAPSHOT_DIR, "latest_snapshot.json")
VOLUME_HISTORY_FILE = os.path.join(DIR, "volume_history.json")
VOLUME_YESTERDAY_FILE = os.path.join(DIR, "volume_yesterday.json")
STOCK_INFO_CACHE_FILE = os.path.join(DIR, "stock_info_cache.json")
SNAPSHOT_FILE = os.path.join(DIR, "daily_snapshots.json")

_ssl_ctx = ssl._create_unverified_context()

def _fetch_json(url, timeout=8, retries=2):
    for i in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Referer": "https://data.eastmoney.com/"
            })
            resp = urllib.request.urlopen(req, timeout=timeout, context=_ssl_ctx)
            return json.loads(resp.read().decode("utf-8"))
        except:
            if i < retries:
                time.sleep(0.5)
    return None

class DataCache:
    def __init__(self):
        self._data = {}
        self._ttl = {}
        self._lock = threading.Lock()
    def set(self, key, data, ttl_group="market"):
        with self._lock:
            self._data[key] = data
            self._ttl[key] = (time.time(), CACHE_TTL.get(ttl_group, 60))
    def get(self, key):
        with self._lock:
            if key not in self._data:
                return {"data": None, "ts": 0, "stale": True}
            ts, ttl = self._ttl[key]
            stale = time.time() - ts > ttl
            return {"data": self._data[key], "ts": ts, "stale": stale}
    def get_or_default(self, key, default=None):
        d = self.get(key)
        return d["data"] if d["data"] is not None else default

cache = DataCache()

# ====== JSON persistence ======
def _load_json(path, default=None):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default if default is not None else {}

def _save_json(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
    except:
        pass

def _load_volume_history():
    return _load_json(VOLUME_HISTORY_FILE, {"days": [], "stocks": {}})

def _save_volume_history(data):
    _save_json(VOLUME_HISTORY_FILE, data)

def _load_yesterday_volume_breakout():
    return _load_json(VOLUME_YESTERDAY_FILE, {"date": "", "list": [], "total": 0})

def _load_stock_info_cache():
    return _load_json(STOCK_INFO_CACHE_FILE, {})

def _save_stock_info_cache(data):
    _save_json(STOCK_INFO_CACHE_FILE, data)

def _load_snapshots():
    return _load_json(SNAPSHOT_FILE, {})

def _save_snapshots(data):
    existing = _load_snapshots()
    if isinstance(data, dict) and len(data) == 1:
        existing.update(data)
    else:
        existing = data if isinstance(data, dict) else {}
    _save_json(SNAPSHOT_FILE, existing)

# ====== Market Data Functions ======
def fetch_all_a_shares_realtime():
    """Fetch ALL A-shares with strict field mapping. Volume in 手, amount in 元."""
    try:
        all_stocks = []
        pn = 1
        # East Money API: fs covers 沪深主板+科创板+创业板+北交所
        # ut/invt are required for reliable access during trading hours
        base_url = ("https://push2.eastmoney.com/api/qt/clist/get"
                    + "?ut=fa5fd1943c7b386f172d6893dbfd32bb"
                    + "&invt=2"
                    + "&fltt=2"
                    + "&fields=f2,f3,f5,f6,f12,f14,f100"
                    + "&fid=f3"
                    + "&fs=m:0+t:6,m:0+t:13,m:1+t:2,m:1+t:23,m:0+t:80,m:1+t:80")
        while True:
            url = base_url + "&pn=" + str(pn) + "&pz=1000&po=1&np=1"
            d = _fetch_json(url, timeout=3)
            if d is None:
                break
            diff = d.get("data", {}).get("diff")
            if not diff:
                break
            items = diff
            for item in items:
                # Strict field mapping: f12=code, f14=name, f2=price, f3=change%, f5=volume(手), f6=amount(元), f100=sector
                code_raw = item.get("f12")
                name_raw = item.get("f14")
                price_raw = item.get("f2")
                change_raw = item.get("f3")
                volume_raw = item.get("f5")
                amount_raw = item.get("f6")
                sector_raw = item.get("f100")
                # Validation 1: code must be 6 digits
                code = str(code_raw).strip() if code_raw is not None else ""
                if len(code) != 6 or not code.isdigit():
                    continue
                # Validation 2: name must be non-empty and not ST/退
                name = str(name_raw).strip() if name_raw else ""
                if not name:
                    continue
                if name.startswith("*") or name.startswith("ST") or chr(36864) in name:
                    continue
                # Validation 3: price must be positive number
                if price_raw is None:
                    continue
                try:
                    price_f = float(price_raw)
                except (ValueError, TypeError):
                    continue
                if price_f <= 0:
                    continue
                # Validation 4: change percentage (allow 0)
                try:
                    change_f = round(float(change_raw), 2) if change_raw is not None else 0.0
                except (ValueError, TypeError):
                    change_f = 0.0
                # Validation 5: volume must be positive (unit: 手)
                if volume_raw is None:
                    continue
                try:
                    volume_f = float(volume_raw)
                except (ValueError, TypeError):
                    continue
                if volume_f <= 0:
                    continue
                # Validation 6: amount in 元
                try:
                    amount_f = float(amount_raw) if amount_raw is not None else 0.0
                except (ValueError, TypeError):
                    amount_f = 0.0
                sector = str(sector_raw).strip() if sector_raw else ""
                all_stocks.append({
                    "code": code,
                    "name": name,
                    "price": round(price_f, 2),
                    "change": change_f,
                    "volume": volume_f,
                    "amount": amount_f,
                    "sector": sector
                })
            if len(items) < 1000:
                break
            pn += 1
        # If East Money returned no data, try Sina as fallback (works in non-trading hours)
        if not all_stocks:
            print("[stocks] East Money returned empty, trying Sina fallback...")
            try:
                prefixes = {"6": "sh", "0": "sz", "3": "sz"}
                all_codes = []
                # Get stock codes from stock_info_cache or use core list
                stock_info = _load_stock_info_cache()
                if len(stock_info) > 50:
                    all_codes = list(stock_info.keys())
                else:
                    # Use the hardcoded stock list
                    for entry in [
                        "600519","000858","300750","000333","002415","600036","601318","600030","002594","601012",
                        "688981","688012","002371","300308","002463","300502","300124","002230","688111","600584",
                        "300476","000988","002475","603986","000725","300059","600887","600900","002837","688256",
                        "601899","600809","000568","600276","300760","002304","002714","300015","601888","600309",
                        "002352","300498","600690","002027","601166","600585","300413","002129","688169","600438",
                        "002460","601985","600031","002236","002241","600745","603501","688036","300433","002142",
                        "002916","600570","300253","002821","300529","300759","300347","688301","300122","300957",
                        "300896","300763","300454","300496","300624","300418","002555","002602","002841","300136",
                        "002938","300751","300776","300724","300748","688005","002920","300699","300604","002925",
                        "300207","300014","300450","300999","601633","002812","300568","300073","300037","002326",
                        "688779","300769","300432","002664","002738","300315","300296","300408","600166","000625",
                        "000651","000001","601398","601939","601288","601328","601857","600028","600941","601088",
                        "600886","600011","601668","002410","002405","002439","300212","300188","002368","300369",
                        "002649","300085","300075","688568","688777","300666","002484","688200",
                    ]:
                        all_codes.append(entry)
                batch_size = 100
                for i in range(0, len(all_codes), batch_size):
                    batch = all_codes[i:i+batch_size]
                    sina_list = []
                    for c in batch:
                        pfx = prefixes.get(c[0], "sz")
                        sina_list.append(pfx + c)
                    if not sina_list:
                        continue
                    url_s = "https://hq.sinajs.cn/list=" + ",".join(sina_list)
                    req_s = urllib.request.Request(url_s, headers={
                        "User-Agent": "Mozilla/5.0",
                        "Referer": "https://finance.sina.com.cn"
                    })
                    try:
                        resp_s = urllib.request.urlopen(req_s, timeout=8, context=_ssl_ctx)
                        text_s = resp_s.read().decode("gbk")
                        for raw_line in text_s.split("\n"):
                            raw_line = raw_line.strip()
                            if not raw_line or '="' not in raw_line:
                                continue
                            eq_idx = raw_line.find('="')
                            if eq_idx < 0:
                                continue
                            val_start = eq_idx + 2
                            val_end = raw_line.rfind('"')
                            if val_end <= val_start:
                                continue
                            data_str = raw_line[val_start:val_end]
                            parts = data_str.split(",")
                            if len(parts) < 32:
                                continue
                            name_s = parts[0].strip()
                            price_s = float(parts[3]) if parts[3] else 0
                            yest_close = float(parts[2]) if parts[2] else 0
                            change_s = round((price_s - yest_close) / yest_close * 100, 2) if yest_close > 0 else 0
                            volume_s_raw = float(parts[8]) if len(parts) > 8 and parts[8] else 0
                            # Sina JS batch volume is in 股 (shares), convert to 手 (lots)
                            volume_s = round(volume_s_raw / 100, 0) if volume_s_raw > 0 else 0
                            amount_s = float(parts[9]) if len(parts) > 9 and parts[9] else 0
                            code_s = raw_line.split("_")[-1].split("=")[0].rstrip("\"")
                            # Remove exchange prefix (sh/sz/bj)
                            for _pfx in ["sh","sz","bj"]:
                                if code_s.startswith(_pfx):
                                    code_s = code_s[len(_pfx):]
                                    break
                            if price_s <= 0 and volume_s <= 0:
                                continue
                            if name_s.startswith("*") or name_s.startswith("ST"):
                                continue
                            all_stocks.append({
                                "code": code_s,
                                "name": name_s,
                                "price": round(price_s, 2),
                                "change": round(change_s, 2),
                                "volume": volume_s,
                                "amount": amount_s,
                                "sector": ""
                            })
                    except:
                        continue
                    import time as _stime
                    _stime.sleep(0.1)
            except Exception as e:
                print("[stocks] Sina fallback error:", e)
        # Cache stock info for enrichment
        if all_stocks:
            try:
                stock_info = _load_stock_info_cache()
                changed = False
                for s in all_stocks:
                    code = s["code"]
                    if code not in stock_info or not stock_info[code].get("name"):
                        stock_info[code] = {
                            "name": s["name"],
                            "sector": s.get("sector", ""),
                            "price": s["price"],
                            "change": s["change"],
                            "amount": s.get("amount", 0)
                        }
                        changed = True
                if changed:
                    _save_stock_info_cache(stock_info)
            except:
                pass
        return all_stocks if all_stocks else None
    except Exception as e:
        print("[stocks] error:", e)
        return None
def _get_fallback_review_stocks():
    return {"list": [
        {"code":"300308","name":"中际旭创","sector":"光模块"},
        {"code":"002463","name":"沪电股份","sector":"PCB"},
        {"code":"300502","name":"新易盛","sector":"光模块"},
        {"code":"688981","name":"中芯国际","sector":"半导体"},
        {"code":"688012","name":"中微公司","sector":"半导体设备"},
        {"code":"002371","name":"北方华创","sector":"半导体设备"},
        {"code":"300124","name":"汇川技术","sector":"机器人"},
        {"code":"002230","name":"科大讯飞","sector":"AI应用"},
        {"code":"688111","name":"金山办公","sector":"AI应用"},
        {"code":"600584","name":"长电科技","sector":"半导体"},
        {"code":"300476","name":"胜宏科技","sector":"PCB"},
        {"code":"000988","name":"华工科技","sector":"光模块"},
        {"code":"002475","name":"立讯精密","sector":"消费电子"},
        {"code":"603986","name":"兆易创新","sector":"半导体"},
        {"code":"000725","name":"京东方A","sector":"面板"},
    ]}

# ====== Fetch fallback (Sina) ======
def _fetch_sina_all_shares_batch(codes_batch):
    """Fetch a batch of stocks from Sina (fallback). Volume in 手."""
    try:
        prefixes = {"6": "sh", "0": "sz", "3": "sz"}
        sina_codes = []
        for code in codes_batch:
            code_s = str(code).strip()
            if not code_s: continue
            prefix = prefixes.get(code_s[0], "sz")
            sina_codes.append(prefix + code_s)
        if not sina_codes:
            return []
        url = "https://hq.sinajs.cn/list=" + ",".join(sina_codes)
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://finance.sina.com.cn",
        })
        resp = urllib.request.urlopen(req, timeout=8, context=_ssl_ctx)
        text = resp.read().decode("gbk")
        result = []
        for raw_line in text.split("\n"):
            raw_line = raw_line.strip()
            if not raw_line:
                continue
            eq_idx = raw_line.find('="')
            if eq_idx < 0:
                continue
            try:
                val_start = eq_idx + 2
                val_end = raw_line.rfind('"')
                if val_end <= val_start:
                    continue
                data_str = raw_line[val_start:val_end]
                parts = data_str.split(",")
                if len(parts) < 30:
                    continue
                name = parts[0]
                price = float(parts[3]) if parts[3] else 0
                change = float(parts[2]) if parts[2] else 0
                volume = float(parts[8]) if len(parts) > 8 and parts[8] else 0
                code_in_line = raw_line.split("_")[-1].split("=")[0]
                if price <= 0 and volume <= 0:
                    continue
                if name.startswith("*") or name.startswith("ST"):
                    continue
                result.append({
                    "code": code_in_line, "name": name,
                    "price": round(price, 2), "change": round(change, 2),
                    "volume": volume,
                })
            except (ValueError, IndexError):
                continue
        return result
    except Exception as e:
        print("[sina] batch error:", e)
    return None


_volume_kline_cache = []


def calc_volume_monitor():
    """Volume monitor: today volume >= 2x ANY of the last 5 days.
    All volumes in 手. Selection: any day >= 2x. Ratio: today/avg."""
    stocks = fetch_all_a_shares_realtime()
    if not stocks:
        return _calc_volume_monitor_cached()
    import datetime as dt
    hist = _load_volume_history()
    today_str = dt.datetime.now().strftime("%Y-%m-%d")
    days_list = [d for d in hist.get("days", []) if d != today_str][-5:]
    stock_vol = hist.get("stocks", {})
    stock_info = _load_stock_info_cache()
    changed = False
    for s in stocks:
        code = s.get("code", "")
        vol = s.get("volume", 0)
        if code and vol > 0:
            if code not in stock_vol:
                stock_vol[code] = {}
            stock_vol[code][today_str] = round(float(vol), 0)
            changed = True
    if changed:
        hist["stocks"] = stock_vol
        _save_volume_history(hist)
    result = []
    now_ts = dt.datetime.now().strftime("%H:%M:%S")
    for s in stocks:
        code = s.get("code", "")
        name = s.get("name", "") or _STOCK_NAMES.get(code, "")
        today_vol = s.get("volume", 0)
        if today_vol <= 0 or not code or not name:
            continue
        if name.startswith("*") or name.startswith("ST") or chr(36864) in name:
            continue
        s_hist = stock_vol.get(code, {})
        hist_vols = [float(s_hist.get(d, 0)) for d in days_list if float(s_hist.get(d, 0)) > 0]
        if len(hist_vols) < 3:
            continue
        # Core rule: today_vol >= ANY day * 2
        if not any(today_vol >= v * 2 for v in hist_vols):
            continue
        # Ratio = today / avg of hist days (not min!)
        avg_hist = sum(hist_vols) / len(hist_vols)
        ratio = today_vol / avg_hist if avg_hist > 0 else 0
        # Sector from stock_info_cache (f100 is often empty from Sina)
        sector = s.get("sector", "") or stock_info.get(code, {}).get("sector", "") or _guess_sector(code)
        price = s.get("price", 0) or stock_info.get(code, {}).get("price", 0)
        chg = s.get("change", 0) or stock_info.get(code, {}).get("change", 0)
        result.append({
            "code": code, "name": name,
            "price": round(price, 2),
            "change": round(chg, 2),
            "volume": round(today_vol / 10000, 2),
            "amount": round((s.get("amount", 0) or 0) / 1e8, 2),
            "sector": sector,
            "ratio": round(ratio, 2),
            "trigger_time": now_ts
        })
    result.sort(key=lambda x: x["ratio"], reverse=True)
    return result[:200]

def _calc_volume_monitor_cached():
    """Compute volume monitor from cached volume_history only.
    Uses latest day in history as reference. All volumes in 手."""
    import datetime as dt
    hist = _load_volume_history()
    days = hist.get("days", [])
    stock_vol = hist.get("stocks", {})
    stock_info = _load_stock_info_cache()
    if len(days) < 6 or len(stock_vol) < 10:
        return None
    today_str = days[-1]
    prev_days = [d for d in days if d != today_str][-5:]
    result = []
    for code, data in stock_vol.items():
        td_vol = float(data.get(today_str, 0))
        if td_vol <= 0:
            continue
        hist_vols = [float(data.get(d, 0)) for d in prev_days if float(data.get(d, 0)) > 0]
        if len(hist_vols) < 3:
            continue
        # Core: today_vol >= ANY day * 2
        triggered = any(td_vol >= v * 2 for v in hist_vols)
        if not triggered:
            continue
        avg_hist = sum(hist_vols) / len(hist_vols)
        ratio = td_vol / avg_hist if avg_hist > 0 else 0
        info = stock_info.get(code, {})
        nm = info.get("name", "") or _STOCK_NAMES.get(code, "")
        if not nm:
            continue
        result.append({
            "code": code, "name": nm,
            "price": round((info.get("price", 0) or 0), 2),
            "change": round((info.get("change", 0) or 0), 2),
            "volume": round(td_vol / 10000, 2),
            "amount": round((info.get("amount", 0) or 0) / 1e8, 2),
            "sector": info.get("sector", "") or _guess_sector(code),
            "ratio": round(ratio, 2),
            "trigger_time": today_str
        })
    result.sort(key=lambda x: x["ratio"], reverse=True)
    return result[:200]

def fetch_volume_monitor():
    """Return volume data: today + yesterday lists."""
    import datetime as dt
    now = dt.datetime.now()
    today_list = []
    try:
        td = calc_volume_monitor()
        if td and len(td) > 0:
            today_list = td
    except:
        pass
    yesterday_data = _load_yesterday_volume_breakout() or {}
    yesterday_list = yesterday_data.get("list", []) if isinstance(yesterday_data, dict) else []
    # Enrich yesterday list with sector info
    if yesterday_list:
        stock_info = _load_stock_info_cache()
        for s in yesterday_list:
            code = s.get("code", "")
            if not s.get("name"):
                s["name"] = stock_info.get(code, {}).get("name", "") or _STOCK_NAMES.get(code, "")
            if not s.get("sector"):
                s["sector"] = stock_info.get(code, {}).get("sector", "") or _guess_sector(code)
    data_status = "live" if today_list else ("yesterday" if yesterday_list else "fallback")
    return {
        "is_trading": True,
        "data_status": data_status,
        "today_list": today_list,
        "yesterday_list": yesterday_list,
        "total": len(today_list) + len(yesterday_list),
        "update_time": dt.datetime.now().strftime("%H:%M:%S"),
        "yesterday_date": yesterday_data.get("date", "") if isinstance(yesterday_data, dict) else "",
        "yesterday_total": len(yesterday_list)
    }



# Stock name lookup (auto-generated from cache)
_STOCK_NAMES = {
    "600519": "贵州茅台",
    "000858": "五粮液",
    "300750": "宁德时代",
    "000333": "美的集团",
    "002415": "海康威视",
    "600036": "招商银行",
    "601318": "中国平安",
    "600030": "中信证券",
    "002594": "比亚迪",
    "601012": "隆基绿能",
    "688981": "中芯国际",
    "688012": "中微公司",
    "688041": "海光信息",
    "002371": "北方华创",
    "300308": "中际旭创",
    "002463": "沪电股份",
    "300502": "新易盛",
    "300124": "汇川技术",
    "002230": "科大讯飞",
    "688111": "金山办公",
    "300274": "阳光电源",
    "002837": "英维克",
    "688256": "寒武纪",
    "600584": "长电科技",
    "300476": "胜宏科技",
    "000988": "华工科技",
    "002475": "立讯精密",
    "603986": "兆易创新",
    "000725": "京东方A",
    "300059": "东方财富",
    "600887": "伊利股份",
    "600900": "长江电力",
    "688008": "澜起科技",
    "300033": "同花顺",
    "002850": "科达利",
    "300782": "卓胜微",
    "300661": "圣邦股份",
    "688072": "拓荆科技",
    "688595": "芯海科技",
    "603160": "汇顶科技",
    "300458": "全志科技",
    "688126": "沪硅产业",
    "688396": "华润微",
    "601899": "紫金矿业",
    "600809": "山西汾酒",
    "000568": "泸州老窖",
    "600276": "恒瑞医药",
    "300760": "迈瑞医疗",
    "002304": "洋河股份",
    "002714": "牧原股份",
    "300015": "爱尔眼科",
    "601888": "中国中免",
    "600309": "万华化学",
    "002352": "顺丰控股",
    "300498": "温氏股份",
    "600690": "海尔智家",
    "002027": "分众传媒",
    "601166": "兴业银行",
    "600585": "海螺水泥",
    "300413": "芒果超媒",
    "002129": "中环股份",
    "688169": "石头科技",
    "600438": "通威股份",
    "002460": "赣锋锂业",
    "601985": "中国核电",
    "600031": "三一重工",
    "002236": "大华股份",
    "002241": "歌尔股份",
    "600745": "闻泰科技",
    "603501": "韦尔股份",
    "688036": "传音控股",
    "300433": "蓝思科技",
    "002142": "宁波银行",
    "002916": "深南电路",
    "600570": "恒生电子",
    "300253": "卫宁健康",
    "002821": "凯莱英",
    "300529": "健帆生物",
    "300759": "康龙化成",
    "300347": "泰格医药",
    "688301": "奕瑞科技",
    "300122": "智飞生物",
    "300957": "贝泰妮",
    "300896": "爱美客",
    "300763": "锦浪科技",
    "300454": "深信服",
    "300496": "中科创达",
    "300624": "万兴科技",
    "300418": "昆仑万维",
    "002555": "三七互娱",
    "002602": "世纪华通",
    "002841": "视源股份",
    "300136": "信维通信",
    "002938": "鹏鼎控股",
    "300751": "迈为股份",
    "300776": "帝尔激光",
    "300724": "捷佳伟创",
    "300748": "金力永磁",
    "688005": "容百科技",
    "002920": "德赛西威",
    "300699": "光威复材",
    "300604": "长川科技",
    "002925": "盈趣科技",
    "300207": "欣旺达",
    "300014": "亿纬锂能",
    "300450": "先导智能",
    "300999": "金龙鱼",
    "601633": "长城汽车",
    "002812": "恩捷股份",
    "300568": "星源材质",
    "300073": "当升科技",
    "300037": "新宙邦",
    "002326": "永太科技",
    "688779": "长远锂科",
    "300769": "德方纳米",
    "300432": "富临精工",
    "002664": "信质电机",
    "002738": "中矿资源",
    "300315": "掌趣科技",
    "300296": "利亚德",
    "300408": "三环集团",
    "600166": "福田汽车",
    "000625": "长安汽车",
    "000651": "格力电器",
    "000001": "平安银行",
    "601398": "工商银行",
    "601939": "建设银行",
    "601288": "农业银行",
    "601328": "交通银行",
    "601857": "中国石油",
    "600028": "中国石化",
    "600941": "中国移动",
    "601088": "中国神华",
    "600886": "国投电力",
    "600011": "华能国际",
    "601668": "中国建筑",
    "002410": "广联达",
    "002405": "四维图新",
    "002439": "启明星辰",
    "300212": "易华录",
    "300188": "美亚柏科",
    "002368": "太极股份",
    "300369": "绿盟科技",
    "002649": "博彦科技",
    "300085": "银之杰",
    "300075": "数字政通",
    "688568": "中科星图",
    "688777": "中控技术",
    "300666": "江丰电子",
    "002484": "江海股份",
    "688200": "华峰测控",
    "301583": "N托伦斯",
    "688328": "深科达",
    "300861": "美畅股份",
    "688584": "上海合晶",
    "301326": "捷邦科技",
    "300656": "民德电子",
    "300487": "蓝晓科技",
    "300786": "国林科技",
    "688813": "泰金新能",
    "301310": "鑫宏业",
    "300667": "必创科技",
    "300969": "恒帅股份",
    "301590": "优优绿能",
    "688101": "三达膜",
    "301092": "争光股份",
    "600664": "哈药股份",
    "002121": "科陆电子",
    "002115": "三维通信",
    "002606": "大连电瓷",
    "600428": "中远海特",
    "002815": "崇达技术",
    "603559": "中通国脉",
    "000920": "沃顿科技",
    "600353": "旭光电子",
    "603929": "亚翔集成",
    "603137": "恒尚节能",
    "001359": "平安电工",
    "000887": "中鼎股份",
    "605178": "时空科技",
    "603155": "新亚强",
    "002552": "宝鼎科技",
    "002414": "高德红外",
    "001395": "亚联机械",
    "002185": "华天科技",
    "002479": "富春环保",
    "600293": "三峡新材",
    "301516": "中远通",
    "301117": "佳缘科技",
    "002346": "柘中股份",
    "300553": "集智股份",
    "603898": "好莱客",
    "000021": "深科技",
    "300323": "华灿光电",
    "000048": "京基智农",
    "688720": "艾森股份",
    "002364": "中恒电气",
    "000810": "创维数字",
    "688323": "瑞华泰",
    "002559": "亚威股份",
    "301550": "斯菱智驱",
    "301362": "民爆光电",
    "603083": "剑桥科技",
    "688333": "铂力特",
    "002409": "雅克科技",
    "300922": "天秦装备",
    "688376": "美埃科技",
    "600992": "贵绳股份",
    "603009": "北特科技",
    "300518": "新迅达",
    "301696": "三瑞智能",
    "688697": "纽威数控",
    "002989": "中天精装",
    "600962": "国投中鲁",
    "002902": "铭普光磁",
    "000977": "浪潮信息",
    "002281": "光迅科技",
    "003036": "泰坦股份",
    "002851": "麦格米特",
    "002623": "亚玛顿",
    "688502": "茂莱光学",
    "002876": "三利谱",
    "301123": "奕东电子",
    "301205": "联特科技",
    "301421": "波长光电",
    "688103": "国力电子",
    "300484": "蓝海华腾",
    "300873": "海晨股份",
    "688605": "先锋精科",
    "002579": "中京电子",
    "601168": "西部矿业",
    "603010": "万盛股份",
    "301093": "华兰股份",
    "688655": "迅捷兴",
    "603690": "至纯科技",
    "002167": "东方锆业",
    "688511": "天微电子",
    "300745": "欣锐科技",
    "300456": "赛微电子",
    "000006": "深振业Ａ",
    "688160": "步科股份",
    "301319": "唯特偶",
    "301529": "福赛科技",
    "301306": "西测测试",
    "300984": "金沃股份",
    "301200": "大族数控",
    "688558": "国盛智科",
    "300394": "天孚通信",
    "301566": "达利凯普",
    "301196": "唯科科技",
    "300429": "强力新材",
    "688123": "聚辰股份",
    "605376": "博迁新材",
    "601636": "旗滨集团",
    "600857": "宁波中百",
    "688238": "和元生物",
    "300255": "常山药业",
    "300071": "福石控股",
    "300105": "龙源技术",
    "300244": "迪安诊断",
    "688726": "拉普拉斯",
    "300184": "力源信息",
    "688202": "美迪西",
    "300911": "亿田智能",
    "301317": "鑫磊股份",
    "688061": "灿瑞科技",
    "300058": "蓝色光标",
    "688371": "菲沃泰",
    "688513": "苑东生物",
    "000573": "粤宏远Ａ",
    "002131": "利欧股份",
    "603578": "三星新材",
    "600410": "华胜天成",
    "002354": "天娱数科",
    "603223": "恒通股份",
    "002976": "瑞玛精密",
    "600360": "华微电子",
    "002929": "润建股份",
    "002038": "双鹭药业",
    "603270": "金帝股份",
    "603322": "超讯科技",
    "600396": "华电辽能",
    "002829": "星网宇达",
    "003020": "立方制药",
    "000892": "欢瑞世纪",
    "002681": "奋达科技",
    "600800": "渤海化学",
    "301178": "天亿马",
    "300657": "弘信电子",
    "688399": "XR硕世生",
    "301201": "诚达药业",
    "688221": "前沿生物-U",
    "001331": "胜通能源",
    "603183": "建研院",
    "688796": "百奥赛图",
    "300363": "博腾股份",
    "688293": "XD奥浦迈",
    "688722": "同益中",
    "688365": "光云科技",
    "002317": "众生药业",
    "603538": "美诺华",
    "688710": "益诺思",
    "300766": "每日互动",
    "301171": "易点天下",
    "688197": "首药控股-U",
    "301230": "泓博医药",
    "300886": "华业香料",
    "000933": "神火股份",
    "301231": "荣信文化",
    "300846": "首都在线",
    "603110": "东方材料",
    "002144": "宏达高科",
    "600986": "浙文互联",
    "002657": "中科金财",
    "688799": "华纳药厂",
    "002693": "双成药业",
    "688660": "电气风电",
    "002370": "亚太药业",
    "688336": "三生国健",
    "688031": "星环科技-U",
    "603127": "昭衍新药",
    "003001": "中岩大地",
    "300451": "创业慧康",
    "002828": "贝肯能源",
    "002970": "锐明技术",
    "002158": "汉钟精机",
    "000938": "紫光股份",
    "002402": "和而泰",
    "002044": "美年健康",
    "300872": "天阳科技",
    "300170": "汉得信息",
    "600718": "东软集团",
    "000620": "盈新发展",
    "300063": "天龙集团",
    "603211": "晋拓股份",
    "600821": "金开新能",
    "002838": "道恩股份",
    "301012": "扬电科技",
    "002774": "快意电梯",
    "600629": "华建集团",
    "002342": "巨力索具",
    "000995": "皇台酒业",
    "300517": "海波重科",
    "002881": "美格智能",
    "603286": "日盈电子",
    "301225": "恒勃股份",
    "301099": "雅创电子",
    "688222": "成都先导",
    "688319": "欧林生物",
    "000923": "河钢资源",
    "301161": "唯万密封",
    "300441": "鲍斯股份",
    "300115": "长盈精密",
    "688613": "奥精医疗",
    "603162": "海通发展",
    "605068": "明新旭腾",
    "300153": "科泰电源",
    "300440": "运达科技",
    "301596": "瑞迪智驱",
    "601858": "中国科传",
    "301218": "华是科技",
    "688610": "埃科光电",
    "603236": "移远通信",
    "603556": "海兴电力",
    "301333": "诺思格",
    "002219": "新里程",
    "688612": "威迈斯",
    "603882": "金域医学",
    "603682": "锦和商管",
    "000880": "潍柴重机",
    "301367": "瑞迈特",
    "600325": "华发股份",
    "600513": "联环药业",
    "000526": "学大教育"
}

# Stock sector lookup (auto-generated from cache)
_STOCK_SECTORS = {
    "600519": "白酒",
    "000858": "白酒",
    "300750": "锂电池",
    "000333": "家电",
    "002415": "安防",
    "600036": "银行",
    "601318": "保险",
    "600030": "券商",
    "002594": "汽车",
    "601012": "光伏",
    "688981": "半导体",
    "688012": "半导体设备",
    "688041": "半导体",
    "002371": "半导体设备",
    "300308": "光模块",
    "002463": "PCB",
    "300502": "光模块",
    "300124": "机器人",
    "002230": "AI应用",
    "688111": "AI应用",
    "300274": "光伏",
    "002837": "机器人",
    "688256": "AI芯片",
    "600584": "封测",
    "300476": "PCB",
    "000988": "光模块",
    "002475": "消费电子",
    "603986": "半导体",
    "000725": "面板",
    "300059": "券商",
    "600887": "食品",
    "600900": "电力",
    "688008": "半导体",
    "300033": "金融科技",
    "002850": "锂电池",
    "688072": "半导体设备",
    "688126": "半导体",
    "688396": "半导体",
    "601899": "有色",
    "600809": "白酒",
    "000568": "白酒",
    "600276": "医药",
    "300760": "医疗",
    "002304": "白酒",
    "002714": "养殖",
    "300015": "医疗",
    "601888": "免税",
    "600309": "化工",
    "002352": "物流",
    "300498": "养殖",
    "600690": "家电",
    "002027": "传媒",
    "601166": "银行",
    "300413": "传媒",
    "688169": "家电",
    "600438": "光伏",
    "002460": "锂电池",
    "601985": "电力",
    "002236": "安防",
    "002241": "消费电子",
    "600745": "消费电子",
    "603501": "半导体",
    "002142": "银行",
    "002916": "PCB",
    "600570": "金融科技",
    "300759": "医药",
    "300347": "医药",
    "300122": "医药",
    "300763": "光伏",
    "300624": "AI应用",
    "300418": "AI应用",
    "002555": "游戏",
    "002841": "教育",
    "300751": "光伏",
    "002920": "汽车电子",
    "601633": "汽车",
    "002812": "锂电池",
    "300315": "游戏",
    "000625": "汽车",
    "000651": "家电",
    "000001": "银行",
    "601398": "银行",
    "601939": "银行",
    "601288": "银行",
    "601328": "银行",
    "601857": "石油",
    "600028": "石化",
    "600941": "电信",
    "601088": "煤炭",
    "600886": "电力",
    "600011": "电力",
    "300188": "软件开发",
    "300369": "软件开发",
    "301583": "半导体",
    "688328": "专用设备",
    "300861": "通用设备",
    "688584": "半导体",
    "301326": "消费电子",
    "300656": "其他电子Ⅱ",
    "300487": "塑料",
    "300786": "环保设备Ⅱ",
    "688813": "专用设备",
    "301310": "汽车零部件",
    "300667": "通用设备",
    "300969": "汽车零部件",
    "301590": "其他电源设备Ⅱ",
    "688101": "环境治理",
    "301092": "塑料",
    "600664": "化学制药",
    "002121": "电网设备",
    "002115": "通信服务",
    "002606": "电网设备",
    "600428": "航运港口",
    "002815": "元件",
    "603559": "通信服务",
    "000920": "塑料",
    "600353": "其他电子Ⅱ",
    "603929": "专业工程",
    "603137": "装修装饰Ⅱ",
    "001359": "塑料",
    "000887": "汽车零部件",
    "605178": "专业工程",
    "603155": "化学制品",
    "002552": "元件",
    "002414": "军工电子Ⅱ",
    "001395": "专用设备",
    "002185": "半导体",
    "002479": "电力",
    "600293": "玻璃玻纤",
    "301516": "其他电源设备Ⅱ",
    "301117": "计算机设备",
    "002346": "电网设备",
    "300553": "通用设备",
    "603898": "家居用品",
    "000021": "消费电子",
    "300323": "光学光电子",
    "000048": "养殖业",
    "688720": "半导体",
    "002364": "其他电源设备Ⅱ",
    "000810": "黑色家电",
    "688323": "塑料",
    "002559": "通用设备",
    "301550": "汽车零部件",
    "301362": "照明设备Ⅱ",
    "603083": "通信设备",
    "688333": "通用设备",
    "002409": "半导体",
    "300922": "地面兵装Ⅱ",
    "688376": "环保设备Ⅱ",
    "600992": "通用设备",
    "603009": "汽车零部件",
    "300518": "互联网电商",
    "301696": "航空装备Ⅱ",
    "688697": "通用设备",
    "002989": "装修装饰Ⅱ",
    "600962": "农产品加工",
    "002902": "通信设备",
    "000977": "计算机设备",
    "002281": "通信设备",
    "003036": "专用设备",
    "002851": "其他电源设备Ⅱ",
    "002623": "光伏设备",
    "688502": "光学光电子",
    "002876": "光学光电子",
    "301123": "消费电子",
    "301205": "通信设备",
    "301421": "光学光电子",
    "688103": "其他电子Ⅱ",
    "300484": "自动化设备",
    "300873": "物流",
    "688605": "半导体",
    "002579": "元件",
    "601168": "工业金属",
    "603010": "化学制品",
    "301093": "医疗器械",
    "688655": "元件",
    "603690": "半导体",
    "002167": "小金属",
    "688511": "军工电子Ⅱ",
    "300745": "汽车零部件",
    "300456": "半导体",
    "000006": "房地产开发",
    "688160": "自动化设备",
    "301319": "电子化学品Ⅱ",
    "301529": "汽车零部件",
    "301306": "军工电子Ⅱ",
    "300984": "通用设备",
    "301200": "专用设备",
    "688558": "通用设备",
    "300394": "通信设备",
    "301566": "元件",
    "301196": "塑料",
    "300429": "电子化学品Ⅱ",
    "688123": "半导体",
    "605376": "金属新材料",
    "601636": "玻璃玻纤",
    "600857": "一般零售",
    "688238": "医疗服务",
    "300255": "化学制药",
    "300071": "广告营销",
    "300105": "其他电源设备Ⅱ",
    "300244": "医疗服务",
    "688726": "光伏设备",
    "300184": "其他电子Ⅱ",
    "688202": "医疗服务",
    "300911": "厨卫电器",
    "301317": "通用设备",
    "688061": "半导体",
    "300058": "广告营销",
    "688371": "电子化学品Ⅱ",
    "688513": "化学制药",
    "000573": "房地产开发",
    "002131": "通用设备",
    "603578": "家电零部件Ⅱ",
    "600410": "IT服务Ⅱ",
    "002354": "广告营销",
    "603223": "炼化及贸易",
    "002976": "汽车零部件",
    "600360": "半导体",
    "002929": "通信服务",
    "002038": "化学制药",
    "603270": "通用设备",
    "603322": "通信服务",
    "600396": "电力",
    "002829": "航天装备Ⅱ",
    "003020": "化学制药",
    "000892": "影视院线",
    "002681": "消费电子",
    "600800": "炼化及贸易",
    "301178": "IT服务Ⅱ",
    "300657": "元件",
    "688399": "医疗器械",
    "301201": "医疗服务",
    "688221": "化学制药",
    "001331": "燃气Ⅱ",
    "603183": "专业服务",
    "688796": "医疗服务",
    "300363": "医疗服务",
    "688293": "生物制品",
    "688722": "化学纤维",
    "688365": "IT服务Ⅱ",
    "002317": "中药Ⅱ",
    "603538": "化学制药",
    "688710": "医疗服务",
    "300766": "软件开发",
    "301171": "广告营销",
    "688197": "化学制药",
    "301230": "医疗服务",
    "300886": "化学制品",
    "000933": "工业金属",
    "301231": "出版",
    "300846": "IT服务Ⅱ",
    "603110": "化学制品",
    "002144": "纺织制造",
    "600986": "广告营销",
    "002657": "IT服务Ⅱ",
    "688799": "化学制药",
    "002693": "化学制药",
    "688660": "风电设备",
    "002370": "化学制药",
    "688336": "生物制品",
    "688031": "软件开发",
    "603127": "医疗服务",
    "003001": "专业工程",
    "300451": "软件开发",
    "002828": "油服工程",
    "002970": "计算机设备",
    "002158": "通用设备",
    "000938": "IT服务Ⅱ",
    "002402": "家电零部件Ⅱ",
    "002044": "医疗服务",
    "300872": "IT服务Ⅱ",
    "300170": "IT服务Ⅱ",
    "600718": "IT服务Ⅱ",
    "000620": "房地产开发",
    "300063": "广告营销",
    "603211": "汽车零部件",
    "600821": "电力",
    "002838": "塑料",
    "301012": "电网设备",
    "002774": "专用设备",
    "600629": "工程咨询服务Ⅱ",
    "002342": "通用设备",
    "000995": "白酒Ⅱ",
    "300517": "专业工程",
    "002881": "通信设备",
    "603286": "汽车零部件",
    "301225": "汽车零部件",
    "301099": "其他电子Ⅱ",
    "688222": "医疗服务",
    "688319": "生物制品",
    "000923": "冶钢原料",
    "301161": "工程机械",
    "300441": "通用设备",
    "300115": "消费电子",
    "688613": "医疗器械",
    "603162": "航运港口",
    "605068": "汽车零部件",
    "300153": "其他电源设备Ⅱ",
    "300440": "IT服务Ⅱ",
    "301596": "通用设备",
    "601858": "出版",
    "301218": "IT服务Ⅱ",
    "688610": "通用设备",
    "603236": "通信设备",
    "603556": "电网设备",
    "301333": "医疗服务",
    "002219": "医疗服务",
    "688612": "汽车零部件",
    "603882": "医疗服务",
    "603682": "一般零售",
    "000880": "通用设备",
    "301367": "医疗器械",
    "600325": "房地产开发",
    "600513": "化学制药",
    "000526": "教育"
}

def _guess_sector(code):
    """Guess sector from hardcoded map or stock prefix."""
    code_s = str(code).strip()
    if code_s in _STOCK_SECTORS:
        return _STOCK_SECTORS[code_s]
    if code_s.startswith("6"):
        return "主板"
    elif code_s.startswith("0"):
        return "主板"
    elif code_s.startswith("3"):
        return "创业板"
    elif code_s.startswith("4"):
        return "创业板"
    elif code_s.startswith("8"):
        return "创业板"
    return ""

def _fill_stock_names():
    """Populate stock_info_cache with hardcoded names for stocks without names."""
    info = _load_stock_info_cache()
    changed = False
    for code, name in _STOCK_NAMES.items():
        if code not in info or not info[code].get("name"):
            info[code] = {
                "name": name,
                "sector": info.get(code, {}).get("sector", ""),
                "price": info.get(code, {}).get("price", 0),
                "change": info.get(code, {}).get("change", 0),
                "amount": info.get(code, {}).get("amount", 0)
            }
            changed = True
    if changed:
        _save_stock_info_cache(info)
        print(f"[stock] names filled: {len([c for c in _STOCK_NAMES if c not in info or not info[c].get('name')])} new")

def _bg_expand_history():
    """Background thread: expand volume history to cover more stocks."""
    import time as _time
    import datetime as dt
    from urllib.request import urlopen, Request
    _time.sleep(30)
    try:
        stocks = fetch_all_a_shares_realtime()
        if not stocks:
            return
        hist = _load_volume_history()
        existing = set(hist.get("stocks", {}).keys())
        new_codes = [(s["code"], "1" if s["code"].startswith("6") else "0")
                     for s in stocks if s.get("code") and s["code"] not in existing]
        print(f"[volume] bg expand: {len(new_codes)} stocks without history")
        fetched = 0
        bg_deadline = _time.time() + 45
        for code, mkt in new_codes[:200]:
            if _time.time() > bg_deadline:
                break
            try:
                url = "https://push2his.eastmoney.com/api/qt/stock/kline/get?secid=" + mkt + "." + code + "&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57&klt=101&fqt=0&end=20500101&lmt=8"
                req = Request(url, headers={"User-Agent":"Mozilla/5.0","Referer":"https://data.eastmoney.com/"})
                resp = urlopen(req, timeout=3, context=_ssl_ctx)
                raw = json.loads(resp.read().decode("utf-8"))
                klines = raw.get("data",{}).get("klines",[])
                for kl in klines:
                    parts = kl.split(",")
                    d = parts[0]
                    v_raw = float(parts[5]) if len(parts)>5 and parts[5] else 0
                    if v_raw > 0:
                        if code not in hist["stocks"]:
                            hist["stocks"][code] = {}
                        hist["stocks"][code][d] = round(v_raw, 0)
                fetched += 1
            except:
                pass
            if fetched % 20 == 0 and fetched > 0:
                _save_volume_history(hist)
                _time.sleep(0.3)
        _save_volume_history(hist)
        _save_yesterday_volume_breakout()
        if fetched:
            print(f"[volume] bg expand done: +{fetched} stocks")
    except Exception as e:
        print("[volume] bg expand error:", e)

def get_latest_snapshot():
    """Return the latest daily snapshot with proper format."""
    import datetime as dt
    snapshots = _load_snapshots()
    if not snapshots:
        return None
    today = dt.datetime.now().strftime("%Y-%m-%d")
    # Return the previous trading day snapshot (not today)
    dates = sorted(snapshots.keys())
    if today in dates and len(dates) > 1:
        idx = dates.index(today)
        if idx > 0:
            return {"date": dates[idx-1], "data": {"market": snapshots[dates[idx-1]]}}
    elif dates:
        return {"date": dates[-1], "data": {"market": snapshots[dates[-1]]}}
    return None

# ====== Background Refresh ======


# ====== Unified Market Data Refresh ======
def _fetch_limit_stats():
    """Fetch limit-up/down stats from East Money API with ut+invt params."""
    try:
        # Fetch limit-up pool (涨幅>=9.5%)
        url_up = ("https://push2.eastmoney.com/api/qt/clist/get"
            + "?ut=fa5fd1943c7b386f172d6893dbfd32bb&invt=2&fltt=2"
            + "&pn=1&pz=500&po=1&np=1"
            + "&fs=m:0+t:6,m:0+t:13,m:1+t:2,m:1+t:23,m:0+t:80"
            + "&fields=f2,f3,f12,f14,f100,f105,f129"
            + "&fid=f3"
            + "&filter=(f105>=9.5)")
        # Fetch limit-down pool (涨幅<=-9.5%)
        url_down = ("https://push2.eastmoney.com/api/qt/clist/get"
            + "?ut=fa5fd1943c7b386f172d6893dbfd32bb&invt=2&fltt=2"
            + "&pn=1&pz=500&po=1&np=1"
            + "&fs=m:0+t:6,m:0+t:13,m:1+t:2,m:1+t:23,m:0+t:80"
            + "&fields=f2,f3,f12,f14,f100,f105,f129"
            + "&fid=f3"
            + "&filter=(f105<=-9.5)")
        
        up_data = _fetch_json(url_up, timeout=3)
        down_data = _fetch_json(url_down, timeout=3)
        
        up_items = []
        if up_data and up_data.get("data") and up_data["data"].get("diff"):
            for item in up_data["data"]["diff"]:
                name = str(item.get("f14", "") or "")
                code = str(item.get("f12", "") or "")
                change = float(item.get("f105", 0) or 0)
                board = int(float(item.get("f129", 0) or 0))
                if name.startswith("*") or name.startswith("ST") or chr(36864) in name:
                    continue
                if change < 9.5:
                    continue
                up_items.append({
                    "code": code, "name": name,
                    "change": round(change, 2),
                    "board": board,
                    "sector": str(item.get("f100", "") or "")
                })
        
        down_items = []
        if down_data and down_data.get("data") and down_data["data"].get("diff"):
            for item in down_data["data"]["diff"]:
                name = str(item.get("f14", "") or "")
                code = str(item.get("f12", "") or "")
                change = float(item.get("f105", 0) or 0)
                if name.startswith("*") or name.startswith("ST") or chr(36864) in name:
                    continue
                if change > -9.5:
                    continue
                down_items.append({
                    "code": code, "name": name,
                    "change": round(change, 2),
                    "sector": str(item.get("f100", "") or "")
                })
        
        limit_up_count = len(up_items)
        limit_down_count = len(down_items)
        bomb_count = max(0, int(limit_up_count * 0.08))
        bomb_rate = round(bomb_count / max(limit_up_count + bomb_count, 1) * 100, 1)
        max_board_height = max([s.get("board", 0) for s in up_items]) if up_items else 0
        yest_premium = round(sum(s.get("change", 0) for s in up_items[:20]) / max(len(up_items[:20]), 1), 2) if up_items else 0
        
        result = {
            "limitUp": limit_up_count,
            "limitDown": limit_down_count,
            "brokenRatio": bomb_rate,
            "maxBoardHeight": max_board_height,
            "yestPremium": yest_premium, "trackedVolume": 0,
            "bombCount": bomb_count,
            "limitUpStocks": up_items[:50],
            "limitDownStocks": down_items[:20],
            "totalEverUp": len([s for s in up_items if s.get("board", 0) >= 2])
        }
        cache.set("limit_up_down", result, "limit_up_down")
        if limit_up_count > 0 or limit_down_count > 0:
            _save_snapshots({datetime.now().strftime("%Y-%m-%d"): result})
        return result
    except Exception as e:
        pass  # [limit] API unavailable (non-trading hours)
        return None

def _fetch_market_indices():
    """Fetch SH/SZ/CYB index data + turnover."""
    try:
        url = ("https://push2.eastmoney.com/api/qt/ulist.np/get"
            + "?ut=fa5fd1943c7b386f172d6893dbfd32bb&invt=2&fltt=2"
            + "&secids=1.000001,0.399001,0.399006"
            + "&fields=f2,f3,f5,f6")
        d = _fetch_json(url, timeout=3)
        if d and d.get("data") and d["data"].get("diff"):
            items = d["data"]["diff"]
            indices = {}
            for item in items:
                code = str(item.get("f12", "") or "")
                change = round(float(item.get("f3", 0) or 0), 2)
                turnover = round(float(item.get("f6", 0) or 0) / 1e8, 1)
                if "000001" in code or "1.000001" in code:
                    indices["sh_change"] = change
                elif "399001" in code:
                    indices["sz_change"] = change
                elif "399006" in code:
                    indices["cyb_change"] = change
            total_turnover = sum(float(item.get("f6", 0) or 0) for item in items)
            indices["turnover_total"] = round(total_turnover / 1e8, 1)
            indices["trackedVolume"] = round(total_turnover / 1e8, 1)
            # Rise/fall counts for market_overview
            overview = _fetch_market_rise_fall()
            if overview:
                indices.update(overview)
            cache.set("market_indices", indices, "market_indices")
            return indices
    except Exception as e:
        print("[indices] error:", e)
    return None

def _fetch_market_rise_fall():
    """Fetch rise/fall counts from all-stocks data."""
    try:
        stocks = fetch_all_a_shares_realtime()
        if stocks:
            rise = sum(1 for s in stocks if s.get("change", 0) > 0)
            fall = sum(1 for s in stocks if s.get("change", 0) < 0)
            flat = max(0, len(stocks) - rise - fall)
            result = {
                "riseCount": rise, "fallCount": fall, "flatCount": flat,
                "totalCount": rise + fall + flat
            }
            cache.set("market_overview", result, "market_overview")
            return result
    except:
        pass
    return None

def _fetch_northbound_flow():
    """Fetch northbound capital flow."""
    try:
        url = ("https://push2.eastmoney.com/api/qt/kamt.rtmin/get"
            + "?ut=fa5fd1943c7b386f172d6893dbfd32bb&invt=2"
            + "&fields1=f1,f3,f5&fields2=f51,f52,f53,f54,f55")
        d = _fetch_json(url, timeout=3)
        if d and d.get("data"):
            # Extract net northbound flow
            sh_net = float(d["data"].get("sh_net", 0) or 0)
            sz_net = float(d["data"].get("sz_net", 0) or 0)
            total_net = round((sh_net + sz_net) / 1e8, 1)
            result = {"data": total_net, "sh_net": sh_net, "sz_net": sz_net}
            cache.set("northbound", result, "northbound")
            return result
    except Exception as e:
        print("[northbound] error:", e)
    return None

def _fetch_sector_data():
    """Fetch sector/industry data for sector momentum calculation."""
    try:
        url = ("https://push2.eastmoney.com/api/qt/clist/get"
            + "?ut=fa5fd1943c7b386f172d6893dbfd32bb&invt=2&fltt=2"
            + "&pn=1&pz=100&po=1&np=1"
            + "&fs=m:90+t:2"
            + "&fields=f2,f3,f12,f14,f62"
            + "&fid=f3")
        d = _fetch_json(url, timeout=3)
        if d and d.get("data") and d["data"].get("diff"):
            sectors = []
            for item in d["data"]["diff"]:
                sectors.append({
                    "code": str(item.get("f12", "") or ""),
                    "name": str(item.get("f14", "") or ""),
                    "change": round(float(item.get("f3", 0) or 0), 2),
                    "net_amount": round(float(item.get("f62", 0) or 0) / 1e8, 2)
                })
            cache.set("sectors", {"list": sectors, "total": len(sectors)}, "sector")
            return sectors
    except Exception as e:
        print("[sector] error:", e)
    return None

def _load_snapshot_yesterday():
    """Read yesterday snapshot for comparison."""
    import datetime as dt
    snapshots = _load_snapshots()
    today = dt.datetime.now().strftime("%Y-%m-%d")
    if today in snapshots and len(snapshots) > 1:
        # Find the previous trading day
        dates = sorted(snapshots.keys())
        idx = dates.index(today)
        if idx > 0:
            return snapshots[dates[idx-1]]
    return None

def unified_refresh():
    """Unified data refresh: fetch all market data and cache it."""
    import time as _stime
    cycle_start = _stime.time()
    try:
        # 1. Fast: Sina batch API (~350 stocks, 2s)
        stocks = fetch_all_a_shares_realtime()
        if stocks and len(stocks) > 50:
            cache.set("review_stocks", stocks, "review_stocks")
            up = sum(1 for s in stocks if s.get("change",0) >= 9.5)
            dn = sum(1 for s in stocks if s.get("change",0) <= -9.5)
            rise = sum(1 for s in stocks if s.get("change",0) > 0)
            fall = sum(1 for s in stocks if s.get("change",0) < 0)
            total_amt = sum(float(s.get("amount",0)) for s in stocks) / 1e8
            stats = {"limit_up_count":up,"limit_down_count":dn,
                "rise_count":rise,"fall_count":fall,
                "turnover_total":round(total_amt,1),
                "up_count":rise,"down_count":fall,
                "bomb_count":0,"bomb_rate":0,"max_board_height":0}
            cache.set("limit_up_down", stats, "limit_up_down")
            cache.set("market_overview", {
                "sh_change":0,"sz_change":0,"cyb_change":0,
                "turnover_total":round(total_amt,1),
                "riseCount":rise,"fallCount":fall,
                "up_count":rise,"down_count":fall,"northbound_flow":0
            }, "market")
            cache.set("market_indices", {
                "trackedVolume":round(total_amt,1),
                "riseCount":rise,"fallCount":fall
            }, "market_indices")
        # 2. Volume monitor
        try:
            vm_data = fetch_volume_monitor()
            if vm_data:
                cache.set("volume_monitor", vm_data, "volume")
        except:
            pass
        # 3. Slow bg: Sina full market (~5000 stocks)
        try:
            already = cache.get("sina_full_market")
            if not already or not already.get("data"):
                import threading
                def _bg_sina():
                    full, s = fetch_sina_market_all()
                    if full and len(full) > 100:
                        cache.set("review_stocks", full, "review_stocks")
                        cache.set("limit_up_down", s, "limit_up_down")
                        cache.set("market_overview", {
                            "sh_change":0,"sz_change":0,"cyb_change":0,
                            "turnover_total":s.get("turnover_total",0),
                            "riseCount":s.get("rise_count",0),"fallCount":s.get("fall_count",0),
                            "up_count":s.get("rise_count",0),"down_count":s.get("fall_count",0),
                            "northbound_flow":0
                        }, "market")
                        cache.set("sina_full_market", True, "market")
                threading.Thread(target=_bg_sina, daemon=True).start()
        except:
            pass
    except:
        pass
    elapsed = _stime.time() - cycle_start
    # === Supabase sync: factor scores (every cycle, active compute) ===
    if supabase_service and supabase_service.is_available():
        try:
            import factors_engine
            fct = factors_engine.calc_all_factors(
                lambda k: (cache.get(k) or {}).get("data")
            )
            if fct and fct.get("composite"):
                supabase_service.sync_factor_scores(
                    fct.get("composite", 50),
                    fct.get("factors", []),
                    fct.get("outlook", "neutral")
                )
        except:
            pass
    return elapsed


# Holidays for non-trading days
_HOLIDAYS = set()

def is_trading_time(now=None):
    import datetime as dt
    if now is None:
        now = dt.datetime.now()
    if now.weekday() >= 5:
        return False
    date_str = now.strftime("%Y-%m-%d")
    if date_str in _HOLIDAYS:
        return False
    h, m = now.hour, now.minute
    if (h == 9 and m >= 30) or h == 10 or (h == 11 and m <= 30):
        return True
    if h == 13 or h == 14 or (h == 15 and m == 0):
        return True
    return False

def _ensure_snapshot_dir():
    try:
        os.makedirs(SNAPSHOT_DIR, exist_ok=True)
    except:
        pass

def save_snapshot(data):
    _ensure_snapshot_dir()
    import datetime as dt
    now = dt.datetime.now()
    fname = "snapshot_" + now.strftime("%Y%m%d") + ".json"
    fpath = os.path.join(SNAPSHOT_DIR, fname)
    try:
        data["update_time"] = now.strftime("%H:%M:%S")
        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        with open(LATEST_SNAPSHOT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("[snapshot] saved: " + fname)
        _clean_old_snapshots()
    except Exception as e:
        print("[snapshot] save error: " + str(e))

def _clean_old_snapshots():
    try:
        _ensure_snapshot_dir()
        import datetime as dt
        cutoff = dt.datetime.now() - dt.timedelta(days=30)
        for f in os.listdir(SNAPSHOT_DIR):
            if f.startswith("snapshot_") and f.endswith(".json"):
                try:
                    d = f.replace("snapshot_", "").replace(".json", "")
                    fd = dt.datetime.strptime(d, "%Y%m%d")
                    if fd < cutoff:
                        os.remove(os.path.join(SNAPSHOT_DIR, f))
                except:
                    pass
    except:
        pass

def load_latest_snapshot():
    try:
        if os.path.exists(LATEST_SNAPSHOT_FILE):
            with open(LATEST_SNAPSHOT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except:
        pass
    return None

def get_market_data(key, default=None):
    _create_seed_snapshot()
    ck = {"all_stocks":"review_stocks","limit_stats":"limit_up_down","market_overview":"market_overview","market_indices":"market_indices","northbound":"northbound","sectors":"sectors","factors_score":"factors_score"}
    if not is_trading_time():
        snap = load_latest_snapshot()
        if snap and key in snap:
            val = snap[key]
            if key == "sectors" and isinstance(val, dict) and "list" in val:
                val = val["list"]
            return val
        if snap:
            return default
        # No snapshot - fall back to cache (if server has been running)
        ck_name = ck.get(key, key)
        cached = cache.get(ck_name)
        if cached and cached.get("data") is not None:
            val = cached["data"]
            if key == "sectors" and isinstance(val, dict) and "list" in val:
                val = val["list"]
            return val
        return default
    # Trading hours - read from live cache
    ck_name = ck.get(key, key)
    cached = cache.get(ck_name)
    if not cached:
        return default
    data = cached.get("data")
    if data is None:
        return default
    if key == "sectors" and isinstance(data, dict) and "list" in data:
        data = data["list"]
    return data

def _bg_refresh():
    """Main background refresh thread - unified 30s cycle."""
    import datetime as dt
    import time as _time
    while True:
        elapsed = unified_refresh()
        _time.sleep(max(5, 30 - elapsed))



def _try_save_snapshot():
    import datetime as dt
    now = dt.datetime.now()
    if now.weekday() >= 5:
        return
    try:
        ov = (cache.get("market_overview") or {}).get("data", {}) or {}
        ldd = (cache.get("limit_up_down") or {}).get("data", {}) or {}
        idx = (cache.get("market_indices") or {}).get("data", {}) or {}
        nb = (cache.get("northbound") or {}).get("data", 0) or 0
        sec_raw = (cache.get("sectors") or {}).get("data", {}) or {}
        sec = sec_raw.get("list", []) if isinstance(sec_raw, dict) else (sec_raw or [])
        rs = (cache.get("review_stocks") or {}).get("data", []) or []
        fct = (cache.get("factors_score") or {}).get("data", {}) or {}
        vm = cache.get("volume_monitor") or {}
        vm_raw = vm.get("data", {}) if isinstance(vm, dict) and isinstance(vm.get("data"), dict) else {}
        vm_today = vm_raw.get("today_list", []) if isinstance(vm_raw, dict) else []
        vm_yest = vm_raw.get("yesterday_list", []) if isinstance(vm_raw, dict) else []
        vm_list = (vm_today if vm_today else vm_yest) or []
        
        snapshot = {
            "date": now.strftime("%Y-%m-%d"),
            "market_overview": {
                "sh_change": ov.get("sh_change", 0),
                "sz_change": ov.get("sz_change", 0),
                "cyb_change": ov.get("cyb_change", 0),
                "turnover_total": idx.get("trackedVolume", 0) or 0,
                "up_count": ov.get("riseCount", 0) or 0,
                "down_count": ov.get("fallCount", 0) or 0,
                "northbound_flow": round(float(nb), 1) if isinstance(nb, (int,float)) else 0
            },
            "limit_stats": {
                "limitUp": ldd.get("limitUp", 0) or 0,
                "limitDown": ldd.get("limitDown", 0) or 0,
                "bombCount": ldd.get("bombCount", 0) or 0,
                "brokenRatio": round(float(ldd.get("brokenRatio", 0.0)), 1),
                "yestPremium": ldd.get("yestPremium", 0) or 0,
                "maxBoardHeight": ldd.get("maxBoardHeight", 0) or 0,
                "limit_up_count": ldd.get("limitUp", 0) or 0,
                "limit_down_count": ldd.get("limitDown", 0) or 0,
                "bomb_rate": round(float(ldd.get("brokenRatio", 0.0)), 1),
                "max_board_height": ldd.get("maxBoardHeight", 0) or 0
            },
            "factors_score": {
                "composite": fct.get("composite", 50),
                "sentiment": fct.get("sentiment", 50),
                "sector": fct.get("sector", 50),
                "chip": fct.get("chip", 50),
                "overnight": fct.get("overnight", 50)
            },
            "volume_monitor_list": vm_list,
            "board_stocks": [],
            "top_change": [],
            "top_amount": [],
            "sector_rank": [s.get("name","") for s in (sec[:20] if isinstance(sec, list) else [])],
            "all_stocks": rs,
            "market_indices": {
                "sh_change": ov.get("sh_change", 0),
                "sz_change": ov.get("sz_change", 0),
                "cyb_change": ov.get("cyb_change", 0),
                "turnover_total": idx.get("trackedVolume", 0) or 0,
                "trackedVolume": idx.get("trackedVolume", 0) or 0,
                "riseCount": ov.get("riseCount", 0) or 0,
                "fallCount": ov.get("fallCount", 0) or 0,
                "indices": [
                    {"name": "上证指数", "change": ov.get("sh_change", 0)},
                    {"name": "深证成指", "change": ov.get("sz_change", 0)},
                    {"name": "创业板指", "change": ov.get("cyb_change", 0)}
                ]
            },
            "northbound": {"data": round(float(nb), 1) if isinstance(nb, (int,float)) else 0},
            "sectors": sec.get("list", []) if isinstance(sec, dict) and "list" in sec else (sec[:100] if isinstance(sec, list) else [])
        }
        # Save trend history
        _trend_raw = cache.get("factors_history") or {}
        _trend_list = (_trend_raw.get("data") if isinstance(_trend_raw, dict) else []) or []
        _trend = []
        import time as _tm
        _cutoff = _tm.time() - 3600
        for _t in _trend_list:
            if isinstance(_t, dict) and _t.get("_ts", 0) > _cutoff:
                _entry = {"ts": int(_t["_ts"]*1000), "composite": _t.get("composite", 50)}
                for _f in _t.get("factors", []):
                    _entry[_f["id"]] = _f["score"]
                _trend.append(_entry)
        snapshot["trend_history"] = _trend

        # Build board_stocks from limitUpStocks
        up_stocks = ldd.get("limitUpStocks", []) or []
        board = []
        for s in up_stocks:
            bc = s.get("board", 0) or 0
            if bc >= 2:
                board.append({"code": s.get("code",""),"name": s.get("name",""),"board_count": bc})
        snapshot["board_stocks"] = sorted(board, key=lambda x: -x["board_count"])
        rs_sorted = sorted(rs, key=lambda x: -(x.get("amount",0) or 0))
        snapshot["top_amount"] = [{"code":s.get("code",""),"name":s.get("name",""),"change":s.get("change",0),"amount":s.get("amount",0),"sector":s.get("sector","")} for s in rs_sorted[:20]]
        rs_sorted2 = sorted(rs, key=lambda x: -(x.get("change",0) or 0))
        snapshot["top_change"] = [{"code":s.get("code",""),"name":s.get("name",""),"change":s.get("change",0),"sector":s.get("sector","")} for s in rs_sorted2[:20]]
        
        # Validate before saving
        rs_count = len(snapshot.get("all_stocks", []) or [])
        lu_count = int(snapshot.get("limit_stats", {}).get("limitUp", 0) or 0)
        vm_count = len(snapshot.get("volume_monitor_list", []) or [])
        turnover = float(snapshot.get("market_overview", {}).get("turnover_total", 0) or 0)
        is_valid = True
        if lu_count == 0 and turnover == 0:
            # No market data - only save if we actually have closing data
            # During non-trading hours the cache might be empty, skip saving empty data
            print("[snapshot] WARNING: limit_up=0 and turnover=0, skipping save to preserve existing snapshot")
            is_valid = False
        if is_valid:
            save_snapshot(snapshot)
            print("[snapshot] auto-saved at " + now.strftime("%H:%M:%S"))
            # === Supabase batch sync (every ~5 min) ===
            if supabase_service and supabase_service.is_available():
                try:
                    mo = snapshot.get('market_overview', {})
                    if mo:
                        supabase_service.sync_market_snapshot(mo)
                    vm_list = snapshot.get('volume_monitor_list', [])
                    if vm_list:
                        supabase_service.sync_volume_alerts(vm_list)
                    sec_list = snapshot.get('sectors', [])
                    if sec_list:
                        supabase_service.sync_sector_rankings(sec_list)
                except Exception as e2:
                    print("[supabase] batch sync error: " + str(e2))
        else:
            print("[snapshot] skipped (invalid data)")
    except Exception as e:
        print("[snapshot] auto-save error: " + str(e))

def _create_seed_snapshot():
    """Create a minimal seed snapshot if none exists."""
    snap = load_latest_snapshot()
    if snap:
        return
    import datetime as dt
    seed = {
        "date": dt.datetime.now().strftime("%Y-%m-%d"),
        "market_overview": {"sh_change": 0, "sz_change": 0, "cyb_change": 0, "turnover_total": 0, "up_count": 0, "down_count": 0, "northbound_flow": 0},
        "limit_stats": {"limitUp": 0, "limitDown": 0, "bombCount": 0, "brokenRatio": 0, "yestPremium": 0, "maxBoardHeight": 0, "limit_up_count": 0, "limit_down_count": 0, "bomb_count": 0, "bomb_rate": 0, "yest_premium": 0, "max_board_height": 0},
        "market_indices": {"sh_change": 0, "sz_change": 0, "cyb_change": 0, "turnover_total": 0, "trackedVolume": 0, "riseCount": 0, "fallCount": 0, "indices": [{"name":"上证指数","change":0},{"name":"深证成指","change":0},{"name":"创业板指","change":0}]},
        "northbound": {"data": 0},
        "sectors": [],
        "factors_score": {"composite": 50, "sentiment": 50, "sector": 50, "chip": 50, "overnight": 50},
        "trend_history": [],
        "all_stocks": [],
        "board_stocks": [],
        "top_change": [],
        "top_amount": [],
        "volume_monitor_list": []
    }
    save_snapshot(seed)
    print("[snapshot] seed snapshot created")

def start():
    # === Supabase init (optional, non-blocking) ===
    if supabase_service:
        supabase_service.init_supabase()
    # Always try to load latest snapshot into cache for fallback
    snap = load_latest_snapshot()
    if snap:
        cache.set("snapshot_loaded", snap, "market")
        # Pre-populate individual cache keys from snapshot
        if snap.get("market_overview"):
            cache.set("market_overview", snap["market_overview"], "market")
        if snap.get("limit_stats"):
            cache.set("limit_up_down", snap["limit_stats"], "limit_up_down")
        if snap.get("market_indices"):
            cache.set("market_indices", snap["market_indices"], "market_indices")
        if snap.get("northbound"):
            cache.set("northbound", snap["northbound"], "northbound")
        if snap.get("sectors"):
            cache.set("sectors", {"list": snap["sectors"], "total": len(snap["sectors"])}, "sector")
        if snap.get("all_stocks"):
            cache.set("review_stocks", snap["all_stocks"], "review_stocks")
        if snap.get("factors_score"):
            cache.set("factors_score", snap["factors_score"], "market")
        print("[snapshot] pre-loaded into cache: " + snap.get("date", ""))
    _init_volume_history()
    # Pre-compute volume monitor from cached data (no API calls at startup)
    try:
        cached_vm = _calc_volume_monitor_cached()
        yest_data = _load_yesterday_volume_breakout()
        yest_list = yest_data.get("list", []) if yest_data else []
        if cached_vm or yest_list:
            vm_data = {
                "is_trading": is_trading_time(),
                "data_status": "live" if cached_vm else "yesterday",
                "today_list": cached_vm or [],
                "yesterday_list": yest_list,
                "total": len(cached_vm or []) + len(yest_list),
                "update_time": time.strftime("%H:%M:%S"),
                "yesterday_date": yest_data.get("date", ""),
                "yesterday_total": len(yest_list)
            }
            cache.set("volume_monitor", vm_data, "volume")
            print(f"[volume] pre-computed: {len(cached_vm or [])} today + {len(yest_list)} yesterday")
    except:
        pass
    t = threading.Thread(target=_bg_refresh, daemon=True)
    t.start()
    import sys as _sys
    _mod = _sys.modules.get(__name__)
    if _mod and hasattr(_mod, "_volume_bg_update"):
        t2 = threading.Thread(target=_mod._volume_bg_update, daemon=True)
        t2.start()
    if _mod and hasattr(_mod, "_bg_expand_history"):
        t3 = threading.Thread(target=_mod._bg_expand_history, daemon=True)
        t3.start()
    disk = getattr(threading, "_ds_ready", False)
    open(os.path.join(DIR, "ds_ready.log"), "w").write("ready")

def _init_volume_history():
    """Initialize volume history. Only real data, no synthetic volumes."""
    hist = _load_volume_history()
    _fill_stock_names()
    if hist.get("stocks") and len(hist.get("stocks", {})) > 50:
        _save_yesterday_volume_breakout()
        return
    # Check if history file exists with data - if so, keep it
    existing_hist = _load_volume_history()
    if existing_hist.get("stocks") and len(existing_hist.get("stocks", {})) > 50:
        return
    print("[volume] no existing data, creating empty history...")
    import datetime as dt
    from urllib.request import urlopen, Request
    import time as _time
    hist = {"days": [], "stocks": {}}
    today = dt.datetime.now()
    last_dates = []
    for i in range(10):
        d = today - dt.timedelta(days=i)
        if d.weekday() < 5:
            last_dates.append(d.strftime("%Y-%m-%d"))
            if len(last_dates) >= 6: break
    last_dates.sort()
    hist["days"] = last_dates
    # Try K-line API for real data
    try:
        live_stocks = fetch_all_a_shares_realtime()
        if live_stocks and len(live_stocks) > 50:
            codes = [(s["code"], "1" if s["code"].startswith("6") else "0") for s in live_stocks if s.get("code")]
            for code, mkt in codes[:100]:
                try:
                    base_url = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
                    params = "?secid=" + mkt + "." + code
                    params += "&fields1=f1,f2,f3,f4,f5,f6"
                    params += "&fields2=f51,f52,f53,f54,f55,f56,f57"
                    params += "&klt=101&fqt=0&end=20500101&lmt=8"
                    req = Request(base_url+params, headers={"User-Agent":"Mozilla/5.0","Referer":"https://data.eastmoney.com/"})
                    resp = urlopen(req, timeout=3, context=_ssl_ctx)
                    raw = json.loads(resp.read().decode("utf-8"))
                    for kl in raw.get("data",{}).get("klines",[]):
                        parts = kl.split(",")
                        d = parts[0]
                        v_raw = float(parts[5]) if len(parts)>5 and parts[5] else 0
                        if v_raw > 0:
                            if code not in hist["stocks"]:
                                hist["stocks"][code] = {}
                            hist["stocks"][code][d] = round(v_raw, 0)
                except:
                    pass
                if len(hist["stocks"]) % 20 == 0 and len(hist["stocks"]) > 0:
                    _time.sleep(0.1)
    except:
        pass
    _save_volume_history(hist)
    if hist.get("stocks") and len(hist.get("stocks", {})) > 20:
        _save_yesterday_volume_breakout()
        print("[volume] init done: real data only")
    else:
        print("[volume] init done: no real data (non-trading hours)")
def _save_yesterday_volume_breakout():
    """Calculate yesterday volume breakout.
    Rule: yesterday_vol >= ANY prev day * 2. Ratio: yesterday_vol / avg.
    All volumes in 手. Output volume in 万手."""
    import datetime as dt
    try:
        hist = _load_volume_history()
        days = hist.get("days", [])
        if len(days) < 2:
            return
        yesterday = days[-1]
        prev_days = [d for d in days if d != yesterday][-5:]
        stock_info = _load_stock_info_cache()
        breakout = []
        for code, data in hist.get("stocks", {}).items():
            ref_vol = float(data.get(yesterday, 0))
            if ref_vol <= 0:
                continue
            hist_vols = [float(data.get(d, 0)) for d in prev_days if float(data.get(d, 0)) > 0]
            if len(hist_vols) < 3:
                continue
            # Core: ref_vol >= ANY day * 2
            if not any(ref_vol >= v * 2 for v in hist_vols):
                continue
            avg_hist = sum(hist_vols) / len(hist_vols)
            ratio = ref_vol / avg_hist if avg_hist > 0 else 0
            info = stock_info.get(code, {})
            breakout.append({
                "code": code, "name": info.get("name", "") or _STOCK_NAMES.get(code, ""),
                "price": round((info.get("price", 0) or 0), 2),
                "change": round((info.get("change", 0) or 0), 2),
                "volume": round(ref_vol / 10000, 2),
                "amount": round((info.get("amount", 0) or 0) / 1e8, 2),
                "ratio": round(ratio, 2),
                "sector": info.get("sector", "") or _guess_sector(code),
                "trigger_time": yesterday
            })
        breakout.sort(key=lambda x: -x["ratio"])
        _save_json(VOLUME_YESTERDAY_FILE, {
            "date": yesterday,
            "update_time": dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "list": breakout[:200],
            "total": len(breakout[:200])
        })
        if breakout:
            print(f"[volume] yesterday breakout saved: {len(breakout[:200])} stocks")
    except Exception as e:
        print("[volume] yesterday breakout error:", e)


