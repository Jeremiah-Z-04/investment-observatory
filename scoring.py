# -*- coding: utf-8 -*-
"""
主线赛道五维量化打分引擎 v2.0
五维：供需缺口(25%) + 订单能见度(25%) + 业绩兑现(20%) + 政策红利(15%) + 中长期资金(15%)
附加：产业链位置加减分 + 风险扣分
"""

import json, os, time

CFG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scoring_config.json")

# ===== 子项打分函数 =====

def score_gap_rate(pct):
    """供需缺口幅度打分"""
    if pct > 30: return 100
    if pct >= 20: return 85
    if pct >= 10: return 70
    if pct >= 0: return 50
    return 30

def score_order_backlog(months):
    """产品订单排产周期打分"""
    if months > 18: return 100
    if months >= 12: return 85
    if months >= 6: return 70
    if months >= 3: return 50
    return 30

def score_spot_price_mom(pct):
    """现货月度环比涨价打分"""
    if pct > 10: return 100
    if pct >= 5: return 85
    if pct >= 0: return 70
    if pct >= -5: return 50
    return 30

def score_order_revenue_ratio(ratio):
    """在手订单/去年营收比分"""
    if ratio > 3: return 100
    if ratio >= 2: return 85
    if ratio >= 1: return 70
    if ratio >= 0.5: return 50
    return 30

def score_customer_concentration(pct):
    """前5大客户集中度打分（越低越好）"""
    if pct < 50: return 100
    if pct <= 70: return 85
    if pct <= 90: return 70
    return 50

def score_overseas_revenue(pct):
    """境外大客户营收占比打分"""
    if pct > 50: return 100
    if pct >= 30: return 85
    if pct >= 10: return 70
    return 30

def score_profit_growth(pct):
    """年度净利润增速打分"""
    if pct > 200: return 100
    if pct >= 100: return 85
    if pct >= 50: return 70
    if pct >= 30: return 50
    return 30

def score_peg(peg):
    """PEG打分"""
    if peg < 0.5: return 100
    if peg <= 1: return 85
    if peg <= 1.5: return 70
    if peg <= 2: return 50
    return 30

def score_earnings_surprise(pct):
    """财报超预期打分"""
    if pct > 30: return 100
    if pct >= 10: return 85
    if pct >= 0: return 70
    if pct >= -10: return 50
    return 30

def score_national_strategy(yes):
    """十五五/国家级重点产业"""
    return 100 if yes else 50

def score_industry_fund(yes):
    """国家产业基金/专项补贴"""
    return 100 if yes else 50

def score_localization_gap(pct):
    """国产化提升空间打分"""
    if pct > 70: return 100
    if pct >= 50: return 85
    if pct >= 30: return 70
    return 50

def score_northbound_monthly(pct):
    """北向资金月度净流入/流通市值"""
    if pct > 2: return 100
    if pct >= 1: return 85
    if pct >= 0: return 70
    if pct >= -1: return 50
    return 30

def score_mutual_fund_qoq(pct):
    """公募基金季度持仓占比环比"""
    if pct > 2: return 100
    if pct >= 1: return 85
    if pct >= 0: return 70
    if pct >= -1: return 50
    return 30

def score_etf_growth(pct):
    """行业ETF月度份额增速"""
    if pct > 10: return 100
    if pct >= 5: return 85
    if pct >= 0: return 70
    if pct >= -5: return 50
    return 30


# ===== 主线综合打分 =====

def score_thread(thread_cfg):
    """对单条主线进行五维打分，返回完整结果"""
    s = thread_cfg.get("supply", {})
    o = thread_cfg.get("order", {})
    p = thread_cfg.get("profit", {})
    po = thread_cfg.get("policy", {})
    f = thread_cfg.get("fund", {})

    # 五维各3项子分
    supply_sub = [
        score_gap_rate(s.get("gap_rate", 0)),
        score_order_backlog(s.get("order_backlog_months", 0)),
        score_spot_price_mom(s.get("spot_price_mom_pct", 0))
    ]
    order_sub = [
        score_order_revenue_ratio(o.get("order_revenue_ratio", 0)),
        score_customer_concentration(o.get("top5_concentration_pct", 100)),
        score_overseas_revenue(o.get("overseas_revenue_pct", 0))
    ]
    profit_sub = [
        score_profit_growth(p.get("net_profit_growth_pct", 0)),
        score_peg(p.get("peg_ratio", 2)),
        score_earnings_surprise(p.get("earnings_surprise_pct", 0))
    ]
    policy_sub = [
        score_national_strategy(po.get("national_strategy", False)),
        score_industry_fund(po.get("industry_fund", False)),
        score_localization_gap(po.get("localization_gap_pct", 0))
    ]
    fund_sub = [
        score_northbound_monthly(f.get("northbound_monthly_pct", 0)),
        score_mutual_fund_qoq(f.get("mutual_fund_qoq_pct", 0)),
        score_etf_growth(f.get("etf_growth_monthly_pct", 0))
    ]

    # 各维度得分 = 子项平均
    dims = {
        "supply": round(sum(supply_sub) / 3),
        "order": round(sum(order_sub) / 3),
        "profit": round(sum(profit_sub) / 3),
        "policy": round(sum(policy_sub) / 3),
        "fund": round(sum(fund_sub) / 3),
    }

    # 基准分 = 加权求和
    W = {"supply": 0.25, "order": 0.25, "profit": 0.20, "policy": 0.15, "fund": 0.15}
    base_score = sum(dims[k] * W[k] for k in dims)

    # 产业链位置加减分
    chain_bonus_map = {"upstream_core": 5, "midstream": 0, "downstream_app": -5}
    chain_bonus = chain_bonus_map.get(thread_cfg.get("chain_position", "midstream"), 0)

    # 风险扣分
    risk_penalty = 0
    risk_level = thread_cfg.get("policy_risk", "none")
    risk_map = {"high": -10, "medium": -5, "low": 0, "none": 0}
    risk_penalty += risk_map.get(risk_level, 0)

    # 估值泡沫扣分（基于PEG推测，实际应读取动态PE）
    peg = p.get("peg_ratio", 1.5)
    if peg > 2 or (p.get("net_profit_growth_pct", 0) < 10):
        risk_penalty += -10
    elif peg > 1.5:
        risk_penalty += -5

    # 最终得分
    final_score = base_score + chain_bonus + risk_penalty
    final_score = max(0, min(100, round(final_score)))

    # 赛道等级
    if final_score >= 85:
        tier = "main"; tier_label = "主线核心赛道"
        action = "重仓配置"
        stage = "第二阶段初期"
    elif final_score >= 75:
        tier = "branch"; tier_label = "支线优质赛道"
        action = "分批小仓"
        stage = "第二阶段中期"
    elif final_score >= 65:
        tier = "swing"; tier_label = "题材震荡赛道"
        action = "短线博弈"
        stage = "第一阶段末期"
    else:
        tier = "avoid"; tier_label = "非景气赛道"
        action = "回避"
        stage = "第一阶段初期"

    return {
        "id": thread_cfg["id"],
        "name": thread_cfg["name"],
        "codes": thread_cfg.get("codes", []),
        "total": final_score,
        "baseScore": round(base_score),
        "chainBonus": chain_bonus,
        "riskPenalty": risk_penalty,
        "dims": dims,
        "dimSubs": {
            "supply": supply_sub, "order": order_sub,
            "profit": profit_sub, "policy": policy_sub, "fund": fund_sub
        },
        "tier": tier,
        "tierLabel": tier_label,
        "stage": stage,
        "action": action,
        "chainPosition": thread_cfg.get("chain_position", ""),
        "riskLevel": risk_level,
    }


def load_config(config_path=None):
    if config_path is None:
        config_path = CFG_PATH
    import json
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

def score_all(config_path=None):
    """对所有主线打分，返回排序后的列表"""
    if config_path is None:
        config_path = CFG_PATH
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    results = [score_thread(t) for t in cfg["threads"]]
    results.sort(key=lambda x: x["total"], reverse=True)
    for i, r in enumerate(results):
        r["rank"] = i + 1
    
    # Inject subSegments into each thread
    sub_segments_map = {
        "AI算力配套": [
            {"name": "服务器整机", "en": "Server Assembly", "reason": "云厂商大单最先锁定营收，业绩最先兑现", "reasonEn": "Cloud orders lock revenue first"},
            {"name": "高速PCB", "en": "High-Speed PCB", "reason": "整机订单后3-6个月下达采购，技术壁垒优于整机", "reasonEn": "PCB orders follow server by 3-6mo"},
            {"name": "AI高端铜箔", "en": "AI Copper Foil", "reason": "PCB量产后方采购，需求滞后但价格弹性最优", "reasonEn": "Copper foil after PCB production"},
            {"name": "液冷散热", "en": "Liquid Cooling", "reason": "装配收尾环节，渗透率缓慢，放量最滞后", "reasonEn": "Final assembly, slow penetration"},
        ],
        "存储芯片": [
            {"name": "HBM封装测试", "en": "HBM Packaging", "reason": "AI需求爆发，先进封装产能最先满载", "reasonEn": "AI demand surge, packaging capacity fills first"},
            {"name": "DDR5内存接口芯片", "en": "DDR5 Interface Chips", "reason": "服务器平台切换驱动，量价齐升", "reasonEn": "Platform transition drives volume+price"},
            {"name": "存储模组", "en": "Storage Modules", "reason": "原厂涨价传导，库存收益兑现但滞后", "reasonEn": "Price hikes pass through, inventory gains lag"},
            {"name": "存储晶圆制造", "en": "Storage Wafer Fab", "reason": "扩产周期长，业绩释放最晚", "reasonEn": "Long expansion cycle, latest earnings"},
        ],
        "光芯片/光模块": [
            {"name": "800G光模块", "en": "800G Optical Modules", "reason": "云厂商直接采购，订单锁定最快", "reasonEn": "Direct procurement, fastest order lock"},
            {"name": "高速光芯片", "en": "High-Speed Optical Chips", "reason": "模块需求拉动备货，产能瓶颈推升盈利", "reasonEn": "Module demand pulls chip build, capacity boosts profit"},
            {"name": "光器件/组件", "en": "Optical Components", "reason": "模块组装前采购，交付短但竞争激烈", "reasonEn": "Pre-assembly procurement, short cycle"},
            {"name": "光纤连接器/MPO", "en": "Fiber Connectors", "reason": "部署后配套布线，需求滞后，放量最慢", "reasonEn": "Post-deployment cabling, slowest ramp"},
        ],
        "国产半导体设备": [
            {"name": "刻蚀/薄膜沉积设备", "en": "Etch/Deposition", "reason": "晶圆厂扩产核心，订单优先，营收确认快", "reasonEn": "Core expansion, prioritized orders"},
            {"name": "清洗/涂胶显影设备", "en": "Clean/Track Equipment", "reason": "配套核心工艺，交付短但受整线制约", "reasonEn": "Supporting core, short delivery"},
            {"name": "测试/分选设备", "en": "Test/Sort Equipment", "reason": "芯片量产后方采购，验证周期长", "reasonEn": "Post-production procurement, long qual"},
            {"name": "离子注入/量测设备", "en": "Implant/Metrology", "reason": "技术壁垒最高，国产替代最慢", "reasonEn": "Highest barrier, slowest substitution"},
        ],
        "华为昇腾产业链": [
            {"name": "昇腾AI服务器整机", "en": "Ascend AI Servers", "reason": "华为直接出货，订单集中，营收最先", "reasonEn": "Huawei direct shipment, revenue first"},
            {"name": "服务器电源/散热模组", "en": "Power/Cooling Modules", "reason": "整机配套采购，量随服务器同步增长", "reasonEn": "Supporting procurement, grows with servers"},
            {"name": "高速连接器/PCB", "en": "Connectors/PCB", "reason": "服务器量产后批量订单，国产替代加速", "reasonEn": "Batch orders post production"},
            {"name": "国产AI芯片封测", "en": "AI Chip Packaging", "reason": "自给率提升缓慢，产能利用率滞后整机", "reasonEn": "Self-sufficiency improves slowly"},
        ],
    }
    for t in results:
        if t["name"] in sub_segments_map:
            t["subSegments"] = sub_segments_map[t["name"]]
    
    return {
        "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
        "threads": results,
        "weights": cfg["_meta"]["weights"],
        "updateCycle": cfg["_meta"]["updateCycle"],
    }


def get_thread_detail(thread_id, config_path=None):
    """获取单条主线详细打分明细"""
    if config_path is None:
        config_path = CFG_PATH
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    for t in cfg["threads"]:
        if t["id"] == thread_id:
            return score_thread(t)
    return None


if __name__ == "__main__":
    result = score_all()
    print(json.dumps(result, ensure_ascii=False, indent=2))