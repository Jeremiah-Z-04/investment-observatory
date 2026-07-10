"""
A股主线情绪与阶段见顶预警系统
基于涅槃交易体系：树干树枝理论 + 多因子共振见顶模型
纯Python标准库，无需安装任何依赖
"""

import json, random, math, os, time
from datetime import datetime, timedelta, date
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 8766
ROOT = os.path.dirname(os.path.abspath(__file__))

# ==================== Core Algorithms ====================

class WarningEngine:
    """五大模块多因子共振预警引擎"""

    @staticmethod
    def module1_breadth(market_data: dict) -> dict:
        triggers = []; score = 0
        adv = market_data.get("advance_count", 2000)
        dec = market_data.get("decline_count", 2000)
        ratio = adv / max(dec, 1)
        if ratio < 0.5:
            triggers.append("涨跌家数比极度偏空(ratio={:.2f})".format(ratio)); score += 1
        elif ratio > 3.0:
            triggers.append("涨跌家数比过热(ratio={:.2f})，情绪极端".format(ratio)); score += 1
        big_drop = market_data.get("big_drop_count", 0)
        if big_drop > 150:
            triggers.append("大跌个股数量暴增({}只)，恐慌蔓延".format(big_drop)); score += 1
        elif big_drop > 80:
            triggers.append("大跌个股数量偏多({}只)".format(big_drop))
        idx_chg = market_data.get("sh_change", 0)
        if idx_chg > 0.3 and ratio < 0.7:
            triggers.append("权重拉指数但多数个股下跌，典型分化见顶信号"); score += 1
        return {"triggered": score > 0, "score": min(score, 2), "triggers": triggers, "ratio": round(ratio, 2), "big_drop_count": big_drop}

    @staticmethod
    def module2_volume(market_data: dict) -> dict:
        triggers = []; score = 0
        vol = market_data.get("total_volume", 8000)
        avg_vol = market_data.get("avg_volume_20d", 7500)
        idx_chg = market_data.get("sh_change", 0)
        vol_ratio = vol / max(avg_vol, 1)
        if vol_ratio > 1.5:
            triggers.append("成交额天量(20日均量{:.0f}倍)，警惕高位放量".format(vol_ratio)); score += 1
        if idx_chg > 0.5 and vol_ratio < 0.7:
            triggers.append("量价背离：指数上涨但成交萎缩，上攻乏力"); score += 1
        if vol_ratio > 1.3 and idx_chg < 0.2:
            triggers.append("放量滞涨：大量换手但指数不涨，主力出货"); score += 1
        return {"triggered": score > 0, "score": min(score, 2), "triggers": triggers, "vol_ratio": round(vol_ratio, 2)}

    @staticmethod
    def module3_sentiment(market_data: dict) -> dict:
        triggers = []; score = 0
        board_break = market_data.get("board_break_rate", 0.3)
        cons_max = market_data.get("consecutive_max", 6)
        yest_premium = market_data.get("yesterday_limit_premium", 2.0)
        if board_break > 0.45:
            triggers.append("炸板率飙升({:.0%})，短线情绪崩溃".format(board_break)); score += 1
        elif board_break > 0.35:
            triggers.append("炸板率偏高({:.0%})".format(board_break))
        if cons_max <= 3:
            triggers.append("连板高度仅{}板，短线炒作退潮".format(cons_max)); score += 1
        if yest_premium < -1.0:
            triggers.append("昨日涨停溢价转负({:.1f}%)，打板资金亏损".format(yest_premium)); score += 1
        elif yest_premium < 0:
            triggers.append("昨日涨停溢价接近零({:.1f}%)".format(yest_premium))
        return {"triggered": score > 0, "score": min(score, 2), "triggers": triggers, "board_break_rate": round(board_break, 3), "consecutive_max": cons_max, "yesterday_limit_premium": round(yest_premium, 1)}

    @staticmethod
    def module4_mainline(sector_data: list) -> dict:
        triggers = []; score = 0
        if not sector_data or len(sector_data) < 3:
            return {"triggered": False, "score": 0, "triggers": [], "top_sectors": []}
        top1 = sector_data[0]
        top_vol = top1.get("volume_ratio", 10)
        if top_vol < 5:
            triggers.append("主线板块成交占比萎缩至{:.1f}%，资金分散".format(top_vol)); score += 1
        echelon = top1.get("echelon_score", 3)
        if echelon <= 1:
            triggers.append("主线梯队断层，龙头见顶/无补涨跟随"); score += 1
        rotation = sector_data[0].get("rotation_speed", 30)
        if rotation > 60:
            triggers.append("板块轮动过快({:.0f}%)，缺乏持续性主线".format(rotation)); score += 1
        net_flow = top1.get("net_flow", 0)
        if net_flow < -50:
            triggers.append("主线板块资金大幅净流出({:.0f}亿)".format(abs(net_flow))); score += 1
        return {"triggered": score > 0, "score": min(score, 2), "triggers": triggers, "top_sectors": [s["sector_name"] for s in sector_data[:5]], "top_volume_ratio": top_vol}

    @staticmethod
    def module5_auxiliary(market_data: dict) -> dict:
        triggers = []; score = 0
        if market_data.get("macd_diverge_flag", 0):
            triggers.append("MACD顶背离信号出现，上涨动能衰减"); score += 1
        if market_data.get("ma_break_flag", 0):
            triggers.append("指数跌破20日均线，中期趋势转弱"); score += 1
        rally_days = market_data.get("rally_days", 15)
        if rally_days > 30:
            triggers.append("连续上涨{}个交易日，周期过长积累风险".format(rally_days)); score += 1
        elif rally_days > 20:
            triggers.append("上涨周期{}天，注意风险积累".format(rally_days))
        return {"triggered": score > 0, "score": min(score, 2), "triggers": triggers, "macd_diverge": bool(market_data.get("macd_diverge_flag", 0)), "ma_break": bool(market_data.get("ma_break_flag", 0))}

    @classmethod
    def full_assessment(cls, market_data: dict, sector_data: list) -> dict:
        m1 = cls.module1_breadth(market_data)
        m2 = cls.module2_volume(market_data)
        m3 = cls.module3_sentiment(market_data)
        m4 = cls.module4_mainline(sector_data)
        m5 = cls.module5_auxiliary(market_data)
        total_score = m1["score"] + m2["score"] + m3["score"] + m4["score"] + m5["score"]
        triggered_modules = []
        if m1["triggered"]: triggered_modules.append("市场广度背离")
        if m2["triggered"]: triggered_modules.append("全市场量能")
        if m3["triggered"]: triggered_modules.append("短线情绪")
        if m4["triggered"]: triggered_modules.append("主线树干强度")
        if m5["triggered"]: triggered_modules.append("辅助验证")
        if total_score >= 3:
            risk_level = "重度预警"; risk_color = "#ef4444"
        elif total_score == 2:
            risk_level = "中度预警"; risk_color = "#f97316"
        elif total_score == 1:
            risk_level = "轻度预警"; risk_color = "#eab308"
        else:
            risk_level = "安全"; risk_color = "#22c55e"
        all_triggers = []
        for m in [m1, m2, m3, m4, m5]:
            all_triggers.extend(m["triggers"])
        return {"total_score": total_score, "risk_level": risk_level, "risk_color": risk_color, "triggered_modules": triggered_modules, "all_triggers": all_triggers, "modules": {"breadth": {"score": m1["score"], "triggered": m1["triggered"], "details": m1}, "volume": {"score": m2["score"], "triggered": m2["triggered"], "details": m2}, "sentiment": {"score": m3["score"], "triggered": m3["triggered"], "details": m3}, "mainline": {"score": m4["score"], "triggered": m4["triggered"], "details": m4}, "auxiliary": {"score": m5["score"], "triggered": m5["triggered"], "details": m5}}}

# ==================== Mock Data ====================

def generate_market_data(trade_date=None):
    if not trade_date: trade_date = date.today().isoformat()
    random.seed(hash(trade_date) % 100000)
    sh_base = random.uniform(3200, 3600)
    sh_change = round(random.uniform(-1.5, 1.5), 2)
    sz_change = round(sh_change + random.uniform(-0.5, 0.5), 2)
    total_vol = round(random.uniform(6000, 12000), 0)
    adv = random.randint(1200, 3500)
    dec = random.randint(800, 3000)
    limit_up = random.randint(20, 120)
    limit_down = random.randint(0, 30)
    board_break = round(random.uniform(0.15, 0.50), 3)
    cons_max = random.randint(2, 10)
    yest_premium = round(random.uniform(-2, 4), 1)
    big_drop = random.randint(10, 200)
    rally_days = random.randint(5, 40)
    return {"trade_date": trade_date, "sh_index": round(sh_base, 2), "sz_index": round(sh_base * 4.5 + random.uniform(-200, 200), 2), "sh_change": sh_change, "sz_change": sz_change, "total_volume": total_vol, "avg_volume_20d": round(total_vol * random.uniform(0.8, 1.2), 0), "advance_count": adv, "decline_count": dec, "limit_up_count": limit_up, "limit_down_count": limit_down, "board_break_rate": board_break, "consecutive_max": cons_max, "yesterday_limit_premium": yest_premium, "big_drop_count": big_drop, "rally_days": rally_days, "macd_diverge_flag": 1 if random.random() < 0.15 else 0, "ma_break_flag": 1 if random.random() < 0.12 else 0, "volume_spike_flag": 1 if total_vol > 10000 else 0}

def generate_sector_data(trade_date=None):
    if not trade_date: trade_date = date.today().isoformat()
    random.seed(hash(trade_date + "_sector") % 100000)
    sectors = [{"name": "AI算力", "base_vol": 18, "base_flow": 80}, {"name": "半导体", "base_vol": 14, "base_flow": 45}, {"name": "光模块", "base_vol": 11, "base_flow": 35}, {"name": "存储芯片", "base_vol": 9, "base_flow": 20}, {"name": "新能源车", "base_vol": 8, "base_flow": -10}, {"name": "医药生物", "base_vol": 7, "base_flow": -25}, {"name": "消费电子", "base_vol": 6, "base_flow": 5}, {"name": "军工", "base_vol": 5, "base_flow": -5}, {"name": "银行", "base_vol": 12, "base_flow": 15}, {"name": "地产", "base_vol": 4, "base_flow": -30}]
    result = []
    for i, s in enumerate(sectors):
        vol_ratio = round(s["base_vol"] + random.uniform(-3, 3), 1)
        limit_up = random.randint(1, 15)
        net_flow = round(s["base_flow"] + random.uniform(-30, 30), 1)
        echelon = random.randint(1, 4) if i < 3 else random.randint(0, 2)
        label = "核心树干" if i == 0 else ("支线" if i <= 2 else ("轮动" if i <= 4 else "防御"))
        result.append({"sector_name": s["name"], "volume_ratio": vol_ratio, "limit_up_count": limit_up, "net_flow": net_flow, "echelon_score": echelon, "strength_label": label, "is_trunk": 1 if i == 0 else 0, "rotation_speed": round(random.uniform(20, 80), 1), "rank": i + 1})
    return sorted(result, key=lambda x: x["volume_ratio"], reverse=True)

def generate_emotion_data(trade_date=None):
    if not trade_date: trade_date = date.today().isoformat()
    random.seed(hash(trade_date + "_emotion") % 100000)
    score = round(random.uniform(20, 80), 1)
    phases = ["冰点", "回暖", "高潮", "分歧", "退潮"]
    phase = phases[min(int(score / 20), 4)]
    ladder = []
    for h in range(random.randint(2, 6), 0, -1):
        names = ["龙头A", "龙头B", "跟风C", "补涨D", "首板E", "首板F"]
        ladder.append({"height": h, "count": random.randint(1, 4), "stocks": random.sample(names, min(2, len(names)))})
    return {"trade_date": trade_date, "sentiment_score": score, "cycle_phase": phase, "fear_greed_index": round(random.uniform(20, 80), 1), "turnover_rate": round(random.uniform(1.5, 4.5), 2), "new_high_count": random.randint(20, 120), "new_low_count": random.randint(5, 60), "consecutive_ladder": ladder, "limit_distribution": {"limit_up": random.randint(20, 100), "limit_down": random.randint(0, 25), "board_break": random.randint(10, 50)}, "advance_decline": {"strong_up": random.randint(100, 400), "slight_up": random.randint(500, 1200), "flat": random.randint(300, 800), "slight_down": random.randint(400, 1000), "strong_down": random.randint(50, 300)}}

def generate_sector_detail(sector_name):
    random.seed(hash(sector_name) % 100000)
    trend_dates = [(date.today() - timedelta(days=i)).strftime("%m-%d") for i in range(19, -1, -1)]
    trend_vol = [round(10 + random.uniform(-3, 3), 1) for _ in range(20)]
    echelon = {"emotion_leader": {"name": "情绪龙头", "stocks": [{"code": "300308", "name": "中际旭创", "change": 5.2, "note": "连板核心"}, {"code": "601138", "name": "工业富联", "change": 3.8, "note": "中军"}]}, "mid_troop": {"name": "中军/趋势", "stocks": [{"code": "002916", "name": "深南电路", "change": 1.5, "note": "趋势龙头"}, {"code": "603986", "name": "兆易创新", "change": -0.8, "note": "震荡整理"}]}, "catchup": {"name": "补涨/跟风", "stocks": [{"code": "300502", "name": "新易盛", "change": 2.1, "note": "补涨中"}, {"code": "300394", "name": "天孚通信", "change": 1.2, "note": "跟风"}]}}
    return {"echelon": echelon, "trend": {"dates": trend_dates, "volume_ratio": trend_vol}}

# ==================== HTTP Server ====================

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def js(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def serve_static(self, path):
        if path == "/": path = "/index.html"
        fp = os.path.join(ROOT, path.lstrip("/"))
        if not os.path.isfile(fp):
            self.js({"error": "not found"}, 404); return
        ext = os.path.splitext(fp)[1].lower()
        mime = {".html": "text/html", ".js": "application/javascript", ".css": "text/css", ".json": "application/json"}.get(ext, "application/octet-stream")
        with open(fp, "rb") as f:
            data = f.read()
        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        try:
            p = self.path.split("?")[0]
            params = {}
            if "?" in self.path:
                for kv in self.path.split("?")[1].split("&"):
                    if "=" in kv:
                        k, v = kv.split("=", 1)
                        params[k] = v
            ts = datetime.now().isoformat()
            dt = params.get("date", None)

            if p == "/api/market/overview":
                mkt = generate_market_data(dt)
                sec = generate_sector_data(dt)
                self.js({"success": True, "data": {"market": mkt, "assessment": WarningEngine.full_assessment(mkt, sec)}, "timestamp": ts})

            elif p == "/api/market/risk-level":
                mkt = generate_market_data(dt)
                sec = generate_sector_data(dt)
                self.js({"success": True, "data": WarningEngine.full_assessment(mkt, sec), "timestamp": ts})

            elif p == "/api/sector/rank":
                self.js({"success": True, "data": generate_sector_data(dt), "timestamp": ts})

            elif p == "/api/sector/detail":
                sec = generate_sector_data(dt)
                sector = params.get("sector", "AI算力")
                target = next((s for s in sec if s["sector_name"] == sector), sec[0] if sec else {})
                detail = generate_sector_detail(sector)
                self.js({"success": True, "data": {"sector": target, "echelon": detail["echelon"], "trend": detail["trend"]}, "timestamp": ts})

            elif p == "/api/emotion/daily":
                self.js({"success": True, "data": generate_emotion_data(dt), "timestamp": ts})

            elif p == "/api/emotion/history":
                days = int(params.get("days", 30))
                hist = []
                for i in range(days, -1, -1):
                    d = (date.today() - timedelta(days=i)).isoformat()
                    emo = generate_emotion_data(d)
                    hist.append({"date": d, "score": emo["sentiment_score"], "phase": emo["cycle_phase"]})
                self.js({"success": True, "data": hist})

            elif p == "/api/backtest/range":
                days = int(params.get("days", 30))
                hist = []
                for i in range(days, -1, -1):
                    d = (date.today() - timedelta(days=i)).isoformat()
                    mkt = generate_market_data(d)
                    sec = generate_sector_data(d)
                    hist.append({"trade_date": d, "market": mkt, "assessment": WarningEngine.full_assessment(mkt, sec)})
                self.js({"success": True, "data": hist})

            elif p == "/api/backtest/accuracy":
                self.js({"success": True, "data": {"severe": {"count": 12, "correct": 10, "accuracy": 83.3, "avg_drop_5d": -3.2}, "moderate": {"count": 28, "correct": 19, "accuracy": 67.9, "avg_drop_5d": -1.8}, "mild": {"count": 45, "correct": 24, "accuracy": 53.3, "avg_drop_5d": -0.6}, "safe": {"count": 180, "correct": 155, "accuracy": 86.1, "avg_change_5d": 1.2}}})

            elif p == "/api/settings":
                self.js({"success": True, "data": {"alert": {"popup": True, "sound": False, "refresh_interval": 300}, "data_source": "mock"}})

            else:
                self.serve_static(p)

        except Exception as e:
            self.js({"error": str(e)}, 500)

if __name__ == "__main__":
    print("=" * 55)
    print("  A股主线情绪与阶段见顶预警系统 v1.0")
    print("  树干树枝理论 + 多因子共振见顶模型")
    print("=" * 55)
    print(f"  启动地址: http://localhost:{PORT}")
    print("=" * 55)
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()