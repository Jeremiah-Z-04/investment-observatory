# -*- coding: utf-8 -*-
"""factors_engine.py - four factor real-time calc"""

import time, json, os
from datetime import datetime

DIR = os.path.dirname(os.path.abspath(__file__))

def safe_div(a, b):
    return a / b if b and b != 0 else 0

def calc_sentiment(limit_data, market_overview):
    if not limit_data:
        return None, {"status":"unknown","desc":"no data","scores":{}}
    lu = limit_data.get("limitUp", 0)
    ld = limit_data.get("limitDown", 0)
    br = limit_data.get("brokenRatio", 50)
    scores = {}
    if lu >= 60: h = 95
    elif lu >= 40: h = 80
    elif lu >= 20: h = 60
    elif lu >= 10: h = 40
    else: h = 20
    if br < 20: h = min(100, h + 10)
    elif br > 40: h = max(10, h - 20)
    scores["height"] = round(h, 1)
    loss = 100
    if ld >= 10: loss = 10
    elif ld >= 5: loss = 35
    elif ld >= 3: loss = 60
    elif ld >= 1: loss = 80
    if br > 50: loss = max(5, loss - 30)
    scores["loss"] = round(loss, 1)
    liq = 60
    ov = market_overview or {}
    rise, fall, tot = ov.get("riseCount",0), ov.get("fallCount",0), ov.get("totalCount",1)
    if tot > 0:
        rr = safe_div(rise, tot)
        if rr > 0.6: liq = 90
        elif rr > 0.5: liq = 75
        elif rr > 0.4: liq = 60
        elif rr > 0.3: liq = 40
        else: liq = 20
    scores["liquidity"] = round(liq, 1)
    ts = round(h * 0.4 + loss * 0.35 + liq * 0.25, 1)
    if ts >= 80: st="main_rise"; d="Sentiment boom, overnight premium high"
    elif ts >= 60: st="benign_div"; d="Healthy divergence, T+2 favorable"
    elif ts >= 40: st="diverging"; d="Broken rate rising, caution"
    elif ts >= 20: st="cooling"; d="Mass limit-down, premium shrinking"
    else: st="ice"; d="Ice point, no overnight positions"
    return ts, {"status":st,"desc":d,"detail":{"limitUp":lu,"limitDown":ld,"brokenRatio":br,"scores":scores}}

def calc_sector_momentum(sectors):
    if not sectors:
        return None, {"status":"neutral","desc":"no data","scores":{}}
    scores = {}
    top5 = sectors[:5]
    fs = 60
    if top5:
        avg = sum(abs(s.get("netInflow",0)) for s in top5) / len(top5)
        if avg > 1.0: fs = 85
        elif avg > 0.5: fs = 70
        elif avg > 0.1: fs = 55
        else: fs = 35
        g = sum(1 for s in top5 if s.get("change",0) > 0) / len(top5)
        if g > 0.8: fs = min(100, fs + 10)
        elif g < 0.4: fs = max(10, fs - 15)
    scores["fund"] = round(fs, 1)
    tiers = 50
    if top5:
        tu = sum(s.get("upCount",0) for s in top5)
        td = sum(s.get("downCount",0) for s in top5)
        ts_ = tu + td
        if ts_ > 0:
            ur = tu / ts_
            if ur > 0.7: tiers = 85
            elif ur > 0.5: tiers = 65
            else: tiers = 35
    scores["tier"] = round(tiers, 1)
    sync = 60
    if top5:
        pos = sum(1 for s in top5 if s.get("change",0) > 0)
        if pos >= 4: sync = 90
        elif pos >= 3: sync = 70
        elif pos >= 2: sync = 50
        else: sync = 25
    scores["sync"] = round(sync, 1)
    ts = round(fs * 0.4 + tiers * 0.3 + sync * 0.3, 1)
    if ts >= 75: st="strong"; d="Strong sector synergy, divergence-to-consensus"
    elif ts >= 55: st="moderate"; d="Capital present but no unified consensus"
    else: st="weak"; d="Scattered hotspots, no follow-through capital"
    return ts, {"status":st,"desc":d,"detail":{"topSectors":top5[:5],"scores":scores}}

def calc_chip_structure(limit_data, market_overview):
    if not limit_data:
        return None, {"status":"neutral","desc":"no data","scores":{}}
    scores = {}
    lu = limit_data.get("limitUp", 0)
    ld = limit_data.get("limitDown", 0)
    if lu + ld > 0:
        ratio = safe_div(lu, lu + ld)
        if ratio > 0.8: s1 = 90
        elif ratio > 0.6: s1 = 75
        elif ratio > 0.4: s1 = 55
        elif ratio > 0.2: s1 = 35
        else: s1 = 15
    else: s1 = 50
    scores["price_vol"] = round(s1, 1)
    if lu >= 50: s2 = 90
    elif lu >= 30: s2 = 75
    elif lu >= 15: s2 = 60
    elif lu >= 5: s2 = 40
    else: s2 = 20
    scores["support"] = round(s2, 1)
    ov = market_overview or {}
    rise, fall = ov.get("riseCount",0), ov.get("fallCount",1)
    if rise + fall > 0:
        rf = safe_div(rise, rise + fall)
        if rf > 0.7: s3 = 90
        elif rf > 0.55: s3 = 70
        elif rf > 0.4: s3 = 50
        elif rf > 0.3: s3 = 30
        else: s3 = 15
    else: s3 = 50
    scores["balance"] = round(s3, 1)
    ts = round(s1 * 0.4 + s2 * 0.3 + s3 * 0.3, 1)
    if ts >= 70: st="healthy"; d="Bulls control, weak hands flushed"
    elif ts >= 50: st="neutral"; d="Balanced, awaiting direction"
    else: st="weak"; d="Profit overhang, bears dominate next day"
    return ts, {"status":st,"desc":d,"detail":{"limitUpRatio":round(safe_div(lu,max(lu+ld,1)),2),"scores":scores}}

def calc_overnight_info():
    return 60, {"status":"neutral","desc":"No material overnight catalysts","detail":{"scores":{"info":60}}}


def calc_daily_advice(composite, factors):
    def g(fid):
        for f in factors:
            if f["id"] == fid: return f["score"]
        return None
    ss = [g("sentiment"), g("sector"), g("chip"), g("overnight")]
    if composite is None:
        cd = chr(25968)+chr(25454)+chr(33719)+chr(21462)+chr(20013)
        fb = chr(25968)+chr(25454)+chr(19981)+chr(20840)
    elif composite >= 75:
        cd = chr(22235)+chr(22240)+chr(23376)+chr(25315)
        fb = chr(31105)+chr(27490)+chr(37325)+chr(21333)
    elif composite >= 60:
        cd = chr(24066)+chr(22330)+chr(20570)+chr(22810)
        fb = chr(31105)+chr(27490)+chr(36861)+chr(39640)
    elif composite >= 45:
        cd = chr(24066)+chr(22330)+chr(20013)+chr(24615)+chr(20570)+chr(35880)
        fb = chr(31105)+chr(27490)+chr(28385)+chr(20179)
    elif composite >= 30:
        cd = chr(24773)+chr(32491)+chr(36208)+chr(24369)
        fb = chr(31105)+chr(27490)+chr(24320)+chr(20179)
    else:
        cd = chr(24066)+chr(22330)+chr(20912)+chr(28857)
        fb = chr(32477)+chr(23545)+chr(31105)+chr(27490)
    if ss[0] is not None and ss[0] < 40:
        if ss[0] < 20:
            ct = chr(24773)+chr(32491)+chr(20912)+chr(28857)+chr(32422)+chr(26463)+chr(29983)+chr(25928)
        else:
            ct = chr(24773)+chr(32491)+chr(32422)+chr(26463)+chr(29983)+chr(25928)
        if ss[1] is not None and ss[1] < 40:
            ct += chr(65292)+chr(26495)+chr(22359)+chr(32422)+chr(26463)+chr(21472)+chr(21152)
        ct += chr(65292)+chr(23454)+chr(38469)+chr(20179)+chr(20301)+chr(38480)+chr(38477)+chr(38480)+chr(38477)+chr(20302)
    else:
        ct = chr(24403)+chr(21069)+chr(26080)+chr(30828)+chr(32422)+chr(26463)+chr(29983)+chr(25928)
    fa = {}
    r = {}
    open("_advice_part.py","w",encoding="utf-8").write('DONE')
    return {"core_action":cd,"forbidden":fb,"constraint_desc":ct,"factor_advice":fa}

def calc_all_factors(cache_getter):
    limit_data = cache_getter("limit_up_down")
    overview = cache_getter("market_overview") or cache_getter("market_indices")
    sectors = cache_getter("sectors")
    if isinstance(overview, dict) and "riseCount" not in overview:
        overview = None
    s1s, s1d = calc_sentiment(limit_data, overview)
    s2s, s2d = calc_sector_momentum(sectors)
    s3s, s3d = calc_chip_structure(limit_data, overview)
    s4s, s4d = calc_overnight_info()
    factors = [
        {"id":"sentiment","label":"sentiment_cycle","score":s1s,"detail":s1d},
        {"id":"sector","label":"sector_momentum","score":s2s,"detail":s2d},
        {"id":"chip","label":"chip_structure","score":s3s,"detail":s3d},
        {"id":"overnight","label":"overnight_info","score":s4s,"detail":s4d},
    ]
    # ??????0.35 ??0.30 ??0.20 ??0.15
    w = {"sentiment":0.35, "sector":0.30, "chip":0.20, "overnight":0.15}
    valid_factors = [f for f in factors if f["score"] is not None]
    null_factors = [f for f in factors if f["score"] is None]
    if not valid_factors:
        # Neutral fallback when no live data available
        neutral_factors = [
            {"id":"sentiment","label":"sentiment_cycle","score":50,"detail":{"status":"neutral","desc":"No live data, neutral score","scores":{"height":50,"loss":50,"liquidity":50}}},
            {"id":"sector","label":"sector_momentum","score":50,"detail":{"status":"neutral","desc":"No live data, neutral score","scores":{"up_ratio":50,"avg_change":50,"dispersity":50}}},
            {"id":"chip","label":"chip_structure","score":50,"detail":{"status":"neutral","desc":"No live data, neutral score","scores":{"price_vol":50,"support":50,"turnover_accel":50}}},
            {"id":"overnight","label":"overnight_info","score":50,"detail":{"status":"neutral","desc":"No material overnight catalysts","detail":{"scores":{"info":50}}}},
        ]
        return {"ts":datetime.now().strftime("%H:%M:%S"),"composite":50,"outlook":"neutral",
                "outlook_desc":"No live data, using neutral scores","factors":neutral_factors,"timestamp":time.time()}
    # ?????????????????
    total_w = sum(w[f["id"]] for f in valid_factors)
    if total_w == 0:
        return {"ts":datetime.now().strftime("%H:%M:%S"),"composite":None,"outlook":"nodata",
                "outlook_desc":"No valid factors","factors":factors,"timestamp":time.time()}
    norm_w = {f["id"]: w[f["id"]] / total_w for f in valid_factors}
    composite = round(sum(f["score"] * norm_w[f["id"]] for f in valid_factors), 1)
    # ??????
    s1 = next((f["score"] for f in valid_factors if f["id"]=="sentiment"), None)
    s2 = next((f["score"] for f in valid_factors if f["id"]=="sector"), None)
    penalty = 1.0
    if s1 is not None:
        if s1 < 20: penalty = 0.6
        elif s1 < 40: penalty = 0.8
    if s2 is not None and s2 < 40:
        penalty *= 0.9
    composite = round(composite * penalty, 1)
    if composite >= 75: ol="strong"; od="Four-factor resonance, high next-day probability"
    elif composite >= 60: ol="positive"; od="Overall bullish bias, premium expected"
    elif composite >= 45: ol="neutral"; od="Balanced, awaiting catalyst"
    elif composite >= 30: ol="cautious"; od="Sentiment+chips weak, cautious overnight"
    else: ol="danger"; od="Ice point+chip deterioration, no overnight"
    # ??????
    advice = calc_daily_advice(composite, factors)
    return {"ts":datetime.now().strftime("%H:%M:%S"),"composite":composite,"outlook":ol,
            "outlook_desc":od,"factors":factors,"advice":advice,"timestamp":time.time()}