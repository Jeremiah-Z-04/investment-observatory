# -*- coding: utf-8 -*-
"""review_rules.py - 盘后复盘阈值化规则函数，所有参数集中管理"""
import json, os, datetime, random, math
from collections import Counter

DIR = os.path.dirname(os.path.abspath(__file__))

# ====== 配置区：所有阈值集中管理 ======
THRESHOLDS = {
    "sentiment": {
        "freeze_limit_up_max": 20,       # 冰点：涨停<=20
        "freeze_limit_down_min": 15,     # 冰点：跌停>=15
        "freeze_premium_max": -2.0,      # 冰点：溢价<=-2%
        "startup_limit_up_min": 25,      # 启动：涨停>=25
        "startup_limit_up_max": 45,      # 启动：涨停<=45
        "startup_premium_min": 1.0,      # 启动：溢价>=1%
        "startup_premium_max": 3.0,      # 启动：溢价<=3%
        "surge_limit_up_min": 50,        # 主升：涨停>=50
        "surge_premium_min": 3.0,        # 主升：溢价>=3%
        "surge_board_min": 3,            # 主升：连板梯队>=3层
        "climax_limit_up_min": 80,       # 高潮：涨停>=80
        "climax_bomb_rate_min": 30.0,    # 高潮：炸板率>=30%
        "retreat_limit_down_min": 10,    # 退潮：跌停>=10
        "retreat_premium_max": 0.0,      # 退潮：溢价<=0%
    },
    "survivor": {
        "turnover_rate_min": 15.0,       # 换手率阈值%
        "volume_ratio_min": 2.0,         # 放量倍数阈值
    },
    "auction": {
        "price_pct": 0.02,              # 竞价达标：高开2%
        "volume_pct": 0.05,             # 竞价达标：量=昨日5%
    },
    "diagnosis": {
        "strong_zone_min": -2.0,         # 格局：跌幅<2%
        "medium_zone_max": -5.0,         # 清仓：跌幅>5%
        "sector_strong_min": 5,          # 格局：板块涨停>=5
        "sector_medium_min": 2,          # 减仓：板块涨停>=2
    }
}

# ====== 情绪周期判断 ======
SENTIMENT_DAYS_CACHE = {}

def calc_sentiment_stage(market, prev_market=None):
    u"""判断情绪周期阶段
    market: {limit_up_count, limit_down_count, bomb_rate, yest_premium, max_board_height}
    prev_market: 上一个交易日的market数据，用于对比
    返回: {stage, effect_type, effect_days, desc}
    """
    up = market.get("limit_up_count", 0) or 0
    down = market.get("limit_down_count", 0) or 0
    bomb = market.get("bomb_rate", 0) or 0
    premium = market.get("yest_premium", 0) or 0
    board = market.get("max_board_height", 0) or 0
    
    t = THRESHOLDS["sentiment"]
    
    # 判断当前阶段
    stage = "neutral"
    reasons = []
    
    if down >= t["freeze_limit_down_min"] or premium <= t["freeze_premium_max"] or up <= t["freeze_limit_up_max"]:
        stage = "freeze"
        reasons.append("冰点")
    elif up >= t["climax_limit_up_min"] and bomb >= t["climax_bomb_rate_min"]:
        stage = "climax"
        reasons.append("高潮")
    elif down >= t["retreat_limit_down_min"] and premium <= t["retreat_premium_max"]:
        stage = "retreat"
        reasons.append("退潮")
    elif up >= t["surge_limit_up_min"] and premium >= t["surge_premium_min"]:
        stage = "surge"
        reasons.append("主升")
    elif up >= t["startup_limit_up_min"] and premium >= t["startup_premium_min"]:
        stage = "startup"
        reasons.append("启动")
    
    # 效应类型
    if stage in ("surge", "climax", "startup"):
        effect_type = "赚钱效应"
    elif stage in ("retreat", "freeze"):
        effect_type = "亏钱效应"
    else:
        effect_type = "混沌期"
    
    # 效应天数
    effect_days = 1
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    if today_str in SENTIMENT_DAYS_CACHE:
        cached = SENTIMENT_DAYS_CACHE[today_str]
        if cached.get("stage") == stage:
            effect_days = cached.get("days", 0) + 1
    SENTIMENT_DAYS_CACHE[today_str] = {"stage": stage, "days": effect_days}
    
    stage_names = {"freeze":"冰点","startup":"启动","surge":"主升","climax":"高潮","retreat":"退潮","neutral":"混沌"}
    stage_name = stage_names.get(stage, "混沌")
    
    return {
        "stage": stage,
        "stage_name": stage_name,
        "effect_type": effect_type,
        "effect_days": effect_days,
        "desc": f"当前处于{stage_name}阶段，{effect_type}第{effect_days}天"
    }

# ====== 核心题材归纳 ======
def calc_core_sectors(top_stocks):
    u"""归纳核心题材
    top_stocks: 涨幅前20个股列表，每项含 {name, sector, change}
    返回: [{topic, level, leader, followers}]
    """
    if not top_stocks:
        return []
    # 按板块分组
    sector_stocks = {}
    for s in top_stocks:
        sec = (s.get("sector") or "").strip()
        if not sec:
            continue
        if sec not in sector_stocks:
            sector_stocks[sec] = []
        sector_stocks[sec].append(s)
    # 按个股数排序取top3
    sorted_sectors = sorted(sector_stocks.items(), key=lambda x: -len(x[1]))
    result = []
    levels = ["主线题材", "支线题材", "补涨题材"]
    for i, (sec, stocks) in enumerate(sorted_sectors[:3]):
        sorted_stocks = sorted(stocks, key=lambda x: -(x.get("change", 0) or 0))
        leader = sorted_stocks[0].get("name", "") if sorted_stocks else ""
        followers = [s.get("name", "") for s in sorted_stocks[1:]]
        result.append({
            "topic": sec,
            "level": levels[i] if i < len(levels) else "其他",
            "count": len(stocks),
            "leader": leader,
            "followers": followers
        })
    return result

# ====== 活口筛选 ======
def calc_survivor_stocks(limit_up_stocks, bomb_stocks, volume_data=None):
    u"""筛选活口个股
    limit_up_stocks: 涨停股列表 [{code, name, board, change}]
    bomb_stocks: 炸板股列表 [{code, name}]
    返回: [{code, name, tag, uniqueness}]
    """
    t = THRESHOLDS["survivor"]
    result = []
    # 从涨停股中找活口
    for s in (limit_up_stocks or [])[:30]:
        code = s.get("code", "")
        name = s.get("name", "")
        board = s.get("board", 0) or 0
        if not code or not name:
            continue
        tags = []
        uniqueness = ""
        if board >= 2:
            tags.append("连板")
            # 板块唯一涨停
            if board >= 3:
                uniqueness = "连板高度标"
            else:
                uniqueness = "板块核心"
        else:
            tags.append("首板涨停")
            uniqueness = "新方向首板"
        result.append({
            "code": code, "name": name,
            "tag": "/".join(tags) if tags else "涨停",
            "uniqueness": uniqueness or "活跃标的"
        })
    return result[:10]

# ====== 明日风向标 ======
def calc_wind_vane(core_sectors, sector_list, northbound_data=None):
    u"""判断明日风向标
    core_sectors: calc_core_sectors返回的核心题材
    sector_list: 板块涨幅榜 [{sector, change, net_amount}]
    返回: 重点观察板块名称
    """
    if core_sectors:
        return core_sectors[0]["topic"]
    if sector_list:
        return sector_list[0].get("sector", "")
    return "市场整体情绪"

# ====== 竞价达标线 ======
def calc_auction_line(code, price_data=None, volume_data=None):
    u"""计算个股竞价达标线
    返回: {target_price, target_volume, price_pct, volume_pct}
    """
    t = THRESHOLDS["auction"]
    # 从价格数据取昨收
    close_price = 0.0
    yest_volume = 0.0
    if price_data and code in price_data:
        close_price = float(price_data[code].get("price", 0))
    if volume_data and code in volume_data:
        stock_vols = volume_data.get(code, {})
        if stock_vols:
            dates = sorted(stock_vols.keys())
            if dates:
                yest_volume = float(stock_vols[dates[-1]])
    target_price = round(close_price * (1 + t["price_pct"]), 2) if close_price > 0 else 0
    target_volume = int(yest_volume * t["volume_pct"]) if yest_volume > 0 else 0
    return {
        "code": code,
        "target_price": target_price,
        "target_volume": target_volume,
        "price_desc": f"高开{round(t['price_pct']*100)}%以上：≥{target_price}元" if target_price else "暂无数据",
        "volume_desc": f"竞价量达昨日{round(t['volume_pct']*100)}%：≥{target_volume}手" if target_volume else "暂无数据"
    }

# ====== 作战计划生成 ======
def gen_battle_plan(target_stocks, risk_threshold, sector_map=None, sector_stocks=None):
    u"""生成次日作战计划
    target_stocks: [{code, name}] 目标股列表
    risk_threshold: 成交额风控阈值(亿)
    sector_map: {code: sector} 个股所属板块映射
    sector_stocks: {sector: [{code, name, amount}]} 板块内个股
    返回: 完整作战计划文本
    """
    if not target_stocks:
        return {"text": "请先输入目标个股", "sections": {}}
    
    lines = []
    lines.append("【A. 竞价达标线】")
    for i, stk in enumerate(target_stocks[:3]):
        code = stk.get("code", "")
        name = stk.get("name", code)
        # 用昨日收盘价模拟
        close_price = 20.0  # fallback
        target_p = round(close_price * 1.02, 2)
        target_v = "待计算"
        sector = (sector_map or {}).get(code, "未知")
        lines.append(f"  {name}({code}) 所属板块:{sector}")
        lines.append(f"    达标价格：≥{target_p}元（高开2%）")
        lines.append(f"    达标成交量：{target_v}")
    
    lines.append("")
    lines.append("【B. 三种情景操作指令】")
    lines.append("  情景一·竞价达标+板块有个股助攻：")
    for stk in target_stocks[:3]:
        nm = stk.get("name", stk.get("code", ""))
        lines.append(f"    {nm}开盘回踩不破分时均线，仓位分批建仓，封板加仓；止损设在成本价-3%")
    lines.append("  情景二·竞价不达标：")
    lines.append("    放弃打板操作，观望为主，不主动进场")
    lines.append("  情景三·盘中炸板急跌：")
    for stk in target_stocks[:3]:
        nm = stk.get("name", stk.get("code", ""))
        lines.append(f"    {nm}破分时均线减半仓，跌幅超-3%无条件清仓")
    
    lines.append("")
    lines.append("【C. 备胎方案】")
    # 找同板块成交额最大的中军
    for stk in target_stocks[:3]:
        code = stk.get("code", "")
        sec = (sector_map or {}).get(code, "")
        if sec and sector_stocks and sec in sector_stocks:
            candidates = sorted(sector_stocks[sec], key=lambda x: -(x.get("amount", 0) or 0))
            if candidates:
                zj = candidates[0]
                lines.append(f"  {sec}板块中军：{zj.get('name','')} 成交额{zj.get('amount',0)}亿")
                break
    lines.append("  创业板弹性标的：关注板块内20cm标的竞价异动")
    
    lines.append("")
    lines.append("【D. 强制风控线】")
    lines.append(f"  两市成交额低于{risk_threshold}亿 → 全部作废，空仓")
    lines.append("  *以上均为盘前推演，不构成投资建议")
    
    return {"text": "\n".join(lines), "sections": {"A": "竞价达标线", "B": "作战指令", "C": "备胎", "D": "风控"}}

# ====== 盘中诊断 ======
def calc_intraday_diagnosis(cost, price, situation, sector_limit_count, sentiment_stage):
    u"""盘中突发诊断
    cost: 成本价
    price: 现价
    situation: 情况类型 (bomb:炸板 / break:跌破均线 / outflow:大单出逃)
    sector_limit_count: 板块涨停数
    sentiment_stage: 情绪阶段 (freeze/startup/surge/climax/retreat/neutral)
    返回: {action, reason}
    """
    t = THRESHOLDS["diagnosis"]
    cost_f = float(cost) if cost else 0
    price_f = float(price) if price else 0
    if cost_f <= 0:
        return {"action": "数据不足", "reason": "请补充成本价"}
    loss_pct = round((price_f - cost_f) / cost_f * 100, 2)
    
    strong_sentiments = ("surge", "climax")
    weak_sentiments = ("retreat", "freeze")
    
    # 判断操作
    action = "观望"
    reasons = []
    
    if sentiment_stage in strong_sentiments and sector_limit_count >= t["sector_strong_min"] and loss_pct > t["strong_zone_min"]:
        action = "格局持有"
        reasons.append(f"大盘情绪强({sentiment_stage})")
        reasons.append(f"板块强势({sector_limit_count}只涨停)")
        reasons.append(f"当前浮亏{abs(loss_pct)}%，在承受范围内")
    elif sentiment_stage in weak_sentiments and sector_limit_count <= t["sector_medium_min"] and loss_pct <= t["medium_zone_max"]:
        action = "清仓"
        reasons.append(f"大盘情绪弱({sentiment_stage})")
        reasons.append(f"板块涨停仅{sector_limit_count}只")
        reasons.append(f"跌幅{abs(loss_pct)}%，触发风控线")
    elif sector_limit_count < t["sector_strong_min"] and loss_pct < t["strong_zone_min"]:
        action = "减半仓"
        reasons.append(f"情绪中性或板块走弱")
        reasons.append(f"当前浮亏{abs(loss_pct)}%，降低仓位观察")
    else:
        action = "持有观察"
        reasons.append("综合评估暂无明确风险信号")
        reasons.append(f"当前浮亏{abs(loss_pct)}%，继续持有观察")
    
    return {
        "action": action,
        "loss_pct": loss_pct,
        "reason": "；".join(reasons)
    }

# ====== 模板文本生成 ======
def format_template1(market, sentiment, core_sectors, survivors, wind_vane):
    u"""生成模板1：盘后快速复盘完整文本"""
    lines = []
    lines.append("【A. 情绪周期阶段】")
    lines.append(f"  当前阶段：{sentiment.get('stage_name','未知')}")
    lines.append(f"  效应类型：{sentiment.get('effect_type','未知')}第{sentiment.get('effect_days',0)}天")
    lines.append(f"  涨停{market.get('limit_up_count',0)}家 / 跌停{market.get('limit_down_count',0)}家")
    lines.append(f"  炸板率{market.get('bomb_rate',0)}% / 昨日涨停溢价{market.get('yest_premium','--')}%")
    lines.append(f"  最高连板{market.get('max_board_height',0)}板")
    lines.append("")
    lines.append("【B. 核心题材归纳】")
    if core_sectors:
        for sec in core_sectors:
            lines.append(f"  {sec['level']}：{sec['topic']}（{sec['count']}只）")
            lines.append(f"    龙头：{sec['leader']}")
            if sec['followers']:
                lines.append(f"    跟风：{' '.join(sec['followers'][:5])}")
    else:
        lines.append("  暂无明确核心题材")
    lines.append("")
    lines.append("【C. 今日活口筛选】")
    if survivors:
        for s in survivors[:8]:
            lines.append(f"  {s['name']}（{s['code']}）— {s['tag']} — {s['uniqueness']}")
    else:
        lines.append("  暂无活口标的")
    lines.append("")
    lines.append("【D. 明日风向标】")
    lines.append(f"  {wind_vane}")
    lines.append("")
    lines.append("—— 推演参考，不构成投资建议 ——")
    return "\n".join(lines)

def format_template2(battle_plan_text):
    u"""生成模板2：次日作战计划"""
    return battle_plan_text

def format_template3(diagnosis):
    u"""生成模板3：盘中突发诊断"""
    lines = []
    lines.append(f"【操作建议】{diagnosis.get('action','--')}")
    lines.append(f"【当前浮亏】{abs(diagnosis.get('loss_pct',0))}%")
    lines.append(f"【诊断理由】{diagnosis.get('reason','--')}")
    lines.append("")
    lines.append("—— 推演参考，不构成投资建议 ——")
    return "\n".join(lines)
