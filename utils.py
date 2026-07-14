# -*- coding: utf-8 -*-
"""utils.py — 公共工具函数模块

提供跨模块共享的市场统计、数据转换等工具函数，
消除 server.py / build_data.py / dataservice.py 之间的重复代码。
"""

import ssl
import urllib.request
import json


def safe_fetch_json(url, timeout=8):
    """安全的 JSON HTTP 请求（使用默认 SSL 上下文）。

    Args:
        url: 请求 URL
        timeout: 超时秒数

    Returns:
        JSON 解析结果，失败返回 None
    """
    try:
        ctx = ssl.create_default_context()
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Referer": "https://data.eastmoney.com/"
        })
        resp = urllib.request.urlopen(req, timeout=timeout, context=ctx)
        return json.loads(resp.read().decode())
    except Exception:
        return None


def calc_market_stats(sdata):
    """从全量股票数据列表计算市场统计指标。

    统一 server.py 和 build_data.py 中重复的涨跌停/涨跌家数/成交额统计。

    Args:
        sdata: 股票数据列表，每项含 change, amount 字段

    Returns:
        字典: limitUp, limitDown, limit_up_count, limit_down_count,
              up_count, down_count, riseCount, fallCount,
              turnover_total, bomb_rate, brokenRatio, etc.
    """
    if not sdata or not isinstance(sdata, list):
        return {}
    up = sum(1 for s in sdata if float(s.get("change", 0) or 0) >= 9.5)
    dn = sum(1 for s in sdata if float(s.get("change", 0) or 0) <= -9.5)
    rise = sum(1 for s in sdata if float(s.get("change", 0) or 0) > 0)
    fall = sum(1 for s in sdata if float(s.get("change", 0) or 0) < 0)
    total_amt = sum(float(s.get("amount", 0) or 0) for s in sdata) / 1e8
    return {
        "limitUp": up,
        "limitDown": dn,
        "limit_up_count": up,
        "limit_down_count": dn,
        "up_count": rise,
        "down_count": fall,
        "riseCount": rise,
        "fallCount": fall,
        "turnover_total": round(total_amt, 1),
        "bomb_rate": 0,
        "bomb_count": 0,
        "brokenRatio": 0,
        "yest_premium": 0,
        "max_board_height": 0,
    }


def safe_float(val, default=0.0):
    """安全转换为 float，失败返回默认值。"""
    try:
        return float(val)
    except (TypeError, ValueError):
        return default
