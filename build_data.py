import os, json, sys, time as _time

DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
sys.path.insert(0, DIR)

print("[build] Starting...")

# Import and run a shortened fetch
import dataservice

# Quick fetch: just call unified_refresh once
try:
    elapsed = dataservice.unified_refresh()
    print(f"[build] unified_refresh: {elapsed:.1f}s")
except Exception as e:
    print(f"[build] unified_refresh error: {e}")

# Short wait for background thread
_time.sleep(3)

cache = dataservice.cache

# ---- Helper: get stock data ----
def _get_stocks():
    sc = cache.get("review_stocks")
    if sc and sc.get("data"):
        d = sc["data"]
        if isinstance(d, list) and len(d) > 50:
            return d
    return []

# ---- 1. factors.json ----
print("[build] factors.json...")
try:
    import factors_engine
    _ldd = dataservice.get_market_data("limit_stats") or {}
    _idx = dataservice.get_market_data("market_indices") or {}
    market = {
        "limit_up_count": int((_ldd or {}).get("limit_up_count", 0) or 0),
        "limit_down_count": int((_ldd or {}).get("limit_down_count", 0) or 0),
        "bomb_rate": round(float((_ldd or {}).get("bomb_rate", 0.0) or 0.0), 1),
        "turnover_total": round(float((_idx or {}).get("trackedVolume", 0) or 0), 1),
        "northbound_net": 0.0, "max_board_height": 0
    }
    def _co(key):
        if key == "limit_up_down":
            sdata = _get_stocks()
            if sdata:
                up = sum(1 for s in sdata if float(s.get("change",0) or 0) >= 9.5)
                dn = sum(1 for s in sdata if float(s.get("change",0) or 0) <= -9.5)
                rise = sum(1 for s in sdata if float(s.get("change",0) or 0) > 0)
                fall = sum(1 for s in sdata if float(s.get("change",0) or 0) < 0)
                ta = sum(float(s.get("amount",0) or 0) for s in sdata) / 1e8
                v = {"limitUp": up, "limitDown": dn, "limit_up_count": up, "limit_down_count": dn, "up_count": rise, "down_count": fall, "riseCount": rise, "fallCount": fall, "turnover_total": round(ta, 1), "bomb_rate": 0, "bomb_count": 0, "brokenRatio": 0, "yest_premium": 0, "max_board_height": 0}
                cache.set("limit_up_down", v, "limit_up_down")
                return v
        return {}
    result = factors_engine.calc_all_factors(_co)
    factors_data = {"success": True, "composite": result.get("composite", 50), "outlook": result.get("outlook", "neutral"), "outlook_desc": result.get("outlook_desc", ""), "factors": result.get("factors", []), "market": market, "is_live": False, "ts": _time.strftime("%H:%M:%S"), "data_tip": "\u6536\u76d8\u6570\u636e"}
    with open(os.path.join(DATA_DIR, "factors.json"), "w", encoding="utf-8") as f: json.dump(factors_data, f, ensure_ascii=False)
    print(f"  composite={result.get('composite')}")
except Exception as e: print(f"  error: {e}")

# ---- 2. factors_history.json ----
print("[build] factors_history.json...")
try:
    hist_raw = cache.get("factors_history")
    hist_list = (hist_raw.get("data") if isinstance(hist_raw, dict) else []) or []
    hist_clean = []
    for h in hist_list:
        if isinstance(h, dict):
            entry = {"composite": h.get("composite", 50)}
            for f in h.get("factors", []): entry[f.get("id", "")] = f.get("score", 50)
            if h.get("_ts"): entry["ts"] = int(h["_ts"] * 1000)
            hist_clean.append(entry)
    if not hist_clean:
        try:
            fp = os.path.join(DATA_DIR, "factors.json")
            if os.path.exists(fp):
                fd = json.load(open(fp, "r", encoding="utf-8"))
                he = {"composite": fd.get("composite", 50), "ts": int(_time.time() * 1000)}
                for fi in fd.get("factors", []): he[fi.get("id","")] = fi.get("score", 50)
                hist_clean = [he]
        except:
            pass
    with open(os.path.join(DATA_DIR, "factors_history.json"), "w", encoding="utf-8") as f: json.dump({"success": True, "data": hist_clean}, f, ensure_ascii=False)
    print(f"  {len(hist_clean)} points")
except Exception as e: print(f"  error: {e}")

# ---- 3. volume_monitor.json ----
print("[build] volume_monitor.json...")
try:
    cached_vm = cache.get("volume_monitor")
    cd = cached_vm.get("data", {}) if isinstance(cached_vm, dict) else {}
    if isinstance(cd, dict): tl = cd.get("today_list", []) or []; yl = cd.get("yesterday_list", []) or []
    else: tl, yl = [], []
    combined = tl or yl
    vol_data = {"success": True, "is_trading": False, "data_status": "live" if tl else ("yesterday" if yl else "close"), "update_time": _time.strftime("%H:%M:%S"), "total": len(tl) + len(yl), "data": {"list": combined, "today_list": tl, "yesterday_list": yl}}
    with open(os.path.join(DATA_DIR, "volume_monitor.json"), "w", encoding="utf-8") as f: json.dump(vol_data, f, ensure_ascii=False)
    print(f"  {len(tl)} today, {len(yl)} yesterday")
except Exception as e: print(f"  error: {e}")

# ---- 4. review_summary.json ----
print("[build] review_summary.json...")
try:
    sdata = _get_stocks()
    if sdata:
        luc = sum(1 for s in sdata if float(s.get("change",0) or 0) >= 9.5)
        ldc = sum(1 for s in sdata if float(s.get("change",0) or 0) <= -9.5)
        rise = sum(1 for s in sdata if float(s.get("change",0) or 0) > 0)
        fall = sum(1 for s in sdata if float(s.get("change",0) or 0) < 0)
        ta = sum(float(s.get("amount",0) or 0) for s in sdata)
        ty = round(ta / 1e8, 1) if ta else 0
        market = {"sh_change": 0.0, "sz_change": 0.0, "cyb_change": 0.0, "turnover_total": ty, "up_count": rise, "down_count": fall, "limit_up_count": luc, "limit_down_count": ldc, "bomb_rate": 0.0, "yest_premium": None, "max_board_height": 0}
        luc_stocks = [s for s in sdata if float(s.get("change",0) or 0) >= 9.5]
        board_stocks = sorted([{"code": s.get("code",""), "name": s.get("name",""), "board_count": 1, "sector": s.get("sector","")} for s in luc_stocks[:30]], key=lambda x: -x["board_count"])
        rs_sorted_amount = sorted(sdata, key=lambda x: -(float(x.get("amount",0) or 0)))
        top_amount = [{"code": s.get("code",""), "name": s.get("name",""), "change": s.get("change",0), "amount": round(float(s.get("amount",0) or 0)/1e8,1), "sector": s.get("sector","")} for s in rs_sorted_amount[:20]]
        ffc = [s for s in sdata if not (s.get("name","") or "").startswith("N") and not "ST" in ((s.get("name","") or "").upper())]
        rs_sc = sorted(ffc, key=lambda x: -(float(x.get("change",0) or 0)))
        top_change = [{"code": s.get("code",""), "name": s.get("name",""), "change": s.get("change",0), "sector": s.get("sector","")} for s in rs_sc[:20]]
        stage = "\u542f\u52a8"
        if luc < 20 or ldc > 15: stage = "\u51b0\u70b9"
        elif luc > 80: stage = "\u9ad8\u6f6e"
        elif ldc > 10: stage = "\u9000\u6f6e"
        elif luc > 50: stage = "\u4e3b\u5347"
        sws = [s for s in sdata if s.get("sector")]
        sm = {}
        for s in sws:
            sec = s.get("sector","") or ""
            if sec:
                if sec not in sm: sm[sec] = {"stocks": [], "count": 0}
                sm[sec]["stocks"].append(s.get("name","")); sm[sec]["count"] += 1
        ss = sorted(sm.items(), key=lambda x: -x[1]["count"])
        cs = [{"topic": sn, "stocks": sd["stocks"][:5], "count": sd["count"]} for sn, sd in ss[:3]]
        sv = []
        for s in sorted(luc_stocks, key=lambda x: -(float(x.get("volume",0) or 0)))[:15]:
            name, code, sec = s.get("name",""), s.get("code",""), s.get("sector","") or ""
            if code and name: sv.append({"code": code, "name": name, "tag": "\u9996\u677f\u6da8\u505c", "uniqueness": sec + "\u9886\u6da8" if sec else "\u6da8\u505c\u677f"})
        wv = "\u5173\u6ce8\u5e02\u573a\u7ade\u4ef7\u5f3a\u5ea6"
        if cs: wv = "\u5173\u6ce8" + cs[0]["topic"] + "\u677f\u5757\u7ade\u4ef7\u5f3a\u5ea6"
        rd = {"success": True, "update_time": _time.strftime("%H:%M:%S"), "is_live": False, "market": market, "board_stocks": board_stocks[:20], "top_amount": top_amount, "top_change": top_change, "survivor_stocks": sv[:10], "sentiment_stage": stage, "effect_type": "\u8d5a\u94b1\u6548\u5e94", "effect_days": 1, "core_sectors": cs, "wind_vane": wv}
        with open(os.path.join(DATA_DIR, "review_summary.json"), "w", encoding="utf-8") as f: json.dump(rd, f, ensure_ascii=False)
        print(f"  {len(board_stocks)} boards, {len(cs)} sectors")
    else: print("  no stock data")
except Exception as e: print(f"  error: {e}")

# ---- 5. review_stocks.json ----
print("[build] review_stocks.json...")
try:
    rs_raw = cache.get("review_stocks")
    rs_list = rs_raw.get("data", []) if isinstance(rs_raw, dict) else (rs_raw or [])
    if not isinstance(rs_list, list): rs_list = []
    with open(os.path.join(DATA_DIR, "review_stocks.json"), "w", encoding="utf-8") as f: json.dump({"success": True, "list": rs_list, "total": len(rs_list)}, f, ensure_ascii=False)
    print(f"  {len(rs_list)} stocks")
except Exception as e: print(f"  error: {e}")

# ---- 6. stock_search.json ----
print("[build] stock_search.json...")
try:
    codes = []
    for c in sorted(dataservice._STOCK_NAMES.keys()):
        codes.append({"code": c, "name": dataservice._STOCK_NAMES[c], "sector": dataservice._guess_sector(c)})
    with open(os.path.join(DATA_DIR, "stock_search.json"), "w", encoding="utf-8") as f: json.dump({"success": True, "list": codes}, f, ensure_ascii=False)
    print(f"  {len(codes)} stocks")
except Exception as e: print(f"  error: {e}")

print(f"[build] Done at {_time.strftime('%H:%M:%S')}")

# ---- 7-10. Static history data from Supabase (for GitHub Pages) ----
try:
    import supabase_service
except ImportError:
    supabase_service = None

if supabase_service:
    supabase_service.init_supabase()
    if supabase_service.is_available():
        # 7. history_factors.json
        print("[build] history_factors.json (from Supabase)...")
        try:
            hf = supabase_service.query_factor_history(limit=500)
            with open(os.path.join(DATA_DIR, "history_factors.json"), "w", encoding="utf-8") as f:
                json.dump({"success": True, "data": hf, "source": "supabase"}, f, ensure_ascii=False)
            print(f"  {len(hf)} records")
        except Exception as e:
            print(f"  error: {e}")

        # 8. history_volume.json
        print("[build] history_volume.json (from Supabase)...")
        try:
            hv = supabase_service.query_volume_alerts(limit=200)
            with open(os.path.join(DATA_DIR, "history_volume.json"), "w", encoding="utf-8") as f:
                json.dump({"success": True, "data": hv, "source": "supabase"}, f, ensure_ascii=False)
            print(f"  {len(hv)} records")
        except Exception as e:
            print(f"  error: {e}")

        # 9. history_snapshots.json
        print("[build] history_snapshots.json (from Supabase)...")
        try:
            hs = supabase_service.query_market_snapshots(days=30, limit=200)
            with open(os.path.join(DATA_DIR, "history_snapshots.json"), "w", encoding="utf-8") as f:
                json.dump({"success": True, "data": hs, "source": "supabase"}, f, ensure_ascii=False)
            print(f"  {len(hs)} records")
        except Exception as e:
            print(f"  error: {e}")

        # 10. history_sectors.json
        print("[build] history_sectors.json (from Supabase)...")
        try:
            hse = supabase_service.query_sector_rankings(limit=100)
            with open(os.path.join(DATA_DIR, "history_sectors.json"), "w", encoding="utf-8") as f:
                json.dump({"success": True, "data": hse, "source": "supabase"}, f, ensure_ascii=False)
            print(f"  {len(hse)} records")
        except Exception as e:
            print(f"  error: {e}")
    else:
        print("[build] Supabase not available, skipping history data")
else:
    print("[build] supabase_service not imported, skipping history data")
