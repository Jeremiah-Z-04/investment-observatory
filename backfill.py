# -*- coding: utf-8 -*-
"""
backfill.py -- 历史数据回补 / 脏数据清洗

背景（已用数据核实）：
- 本地 snapshots/*.json 两个文件均为种子/空数据，无可回补真实历史。
- data/factors_history.json 含 1 个真实历史因子点（约 2026-07-13 交易日）。
- Supabase 中 volume_alerts(69) 与 market_snapshots(3) 全部为非交易时段写入的
  夜间脏数据（闸门修复前累积），需清理；factor_scores 为正确的 24/7 流式，保留。

两种能力（幂等、可按日期去重、可重跑）：
  --clean-stale   删除 volume_alerts / market_snapshots 中"非交易时段"写入的脏行
  --backfill      把真实历史（factors_history + 本地真实快照）按正确日期补入 Supabase
  (无参数)         dry-run：只报告将要做什么，不改动数据

用法：
  python backfill.py            # 报告
  python backfill.py --clean-stale
  python backfill.py --backfill
  python backfill.py --all
"""
import os
import sys
import json
import glob
import time
import datetime

DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, DIR)

import supabase_service as ss


def in_trading(ts):
    """判断时间戳是否落在 A 股交易时段（工作日 9:30-11:30 / 13:00-15:00）。"""
    if not ts:
        return False
    try:
        t = ts.replace("Z", "+08:00")
        if "+" in t:
            t = t.split("+")[0]
        dt = datetime.datetime.strptime(t, "%Y-%m-%dT%H:%M:%S")
    except Exception:
        return False
    if dt.weekday() >= 5:
        return False
    h, m = dt.hour, dt.minute
    if (h == 9 and m >= 30) or h == 10 or (h == 11 and m <= 30):
        return True
    if h == 13 or h == 14 or (h == 15 and m == 0):
        return True
    return False


def is_seed(snap):
    """判断快照是否为空/种子数据（无可回补真实行情）。"""
    mo = snap.get("market_overview") or {}
    return (
        not (mo.get("turnover_total"))
        and len(snap.get("all_stocks") or []) == 0
        and len(snap.get("sectors") or []) == 0
        and len(snap.get("volume_monitor_list") or []) == 0
    )


def client():
    if not ss.init_supabase():
        print("[backfill] Supabase 未配置/未连接，中止")
        sys.exit(1)
    return ss._supabase


def plan_clean_stale(c):
    plan = {}
    for table, col in [("volume_alerts", "alert_time"), ("market_snapshots", "snapshot_time")]:
        rows = c._request("GET", "%s?select=id,%s&order=id.asc" % (table, col))
        stale = [r["id"] for r in rows if not in_trading(r.get(col))]
        plan[table] = (len(rows), stale)
    return plan


def do_clean_stale(c, dry=False):
    plan = plan_clean_stale(c)
    total = 0
    for table, (total_rows, stale_ids) in plan.items():
        print("[clean] %s: 共 %d 行, 其中非交易时段脏行 %d 行" % (table, total_rows, len(stale_ids)))
        if not stale_ids:
            continue
        if dry:
            print("        [dry-run] 将删除 ids: %s" % (",".join(str(i) for i in stale_ids)[:80]))
            continue
        before = len(c._request("GET", "%s?select=id" % table))
        ids = ",".join(str(i) for i in stale_ids)
        try:
            c._request("DELETE", "%s?id=in.(%s)" % (table, ids))
        except Exception as e:
            print("        [ERROR] DELETE 失败: %s" % e)
            continue
        after = len(c._request("GET", "%s?select=id" % table))
        removed = before - after
        if removed == 0:
            # Supabase RLS 经典坑：anon key 的 DELETE 返回 204 但 0 行被删
            print("        [BLOCKED] DELETE 返回成功但 0 行被删 —— RLS 策略拦截了 anon 删除。")
            print("                  解法二选一：")
            print("                  1) 在 .env 填入 SUPABASE_SERVICE_ROLE_KEY（绕过 RLS），重跑本脚本；")
            print("                  2) Supabase Dashboard > Table Editor > 该表 > RLS 策略，为 anon 角色添加 DELETE 权限。")
        else:
            total += removed
            print("        [done] 实际删除 %d 行" % removed)
    if not dry:
        print("[clean] 共实际清理 %d 行脏数据" % total)


def date_exists(c, table, date_str):
    r = c._request("GET", "%s?select=id&date=eq.%s&limit=1" % (table, date_str))
    return bool(r)


def do_backfill(c, dry=False):
    inserted = 0
    # 1) factor_scores from data/factors_history.json
    fh_path = os.path.join(DIR, "data", "factors_history.json")
    if os.path.exists(fh_path):
        try:
            fh = json.load(open(fh_path, encoding="utf-8"))
            pts = (fh.get("data") if isinstance(fh, dict) else fh) or []
        except Exception as e:
            pts = []
            print("[backfill] 读取 factors_history.json 失败: %s" % e)
        for pt in pts:
            ts = pt.get("ts")
            if not ts:
                continue
            dt = datetime.datetime.fromtimestamp(ts / 1000)
            date_str = dt.strftime("%Y-%m-%d")
            rec = dt.strftime("%Y-%m-%dT%H:%M:%S+08:00")
            if date_exists(c, "factor_scores", date_str):
                print("[backfill] factor_scores %s 已存在，跳过" % date_str)
                continue
            row = {
                "recorded_at": rec,
                "date": date_str,
                "composite": pt.get("composite"),
                "sentiment": pt.get("sentiment"),
                "sector": pt.get("sector"),
                "chip": pt.get("chip"),
                "overnight": pt.get("overnight"),
                "outlook": "backfilled",
            }
            if dry:
                print("[dry-run] 将补入 factor_scores %s: composite=%s" % (date_str, row["composite"]))
                continue
            if c.insert("factor_scores", row) is not None:
                inserted += 1
                print("[backfill] factor_scores %s 已补入 (composite=%s)" % (date_str, row["composite"]))
            else:
                print("[backfill] factor_scores %s 补入失败" % date_str)

    # 2) 本地真实快照回补（跳过种子 / 跳过今天，避免与实时流重复）
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    for f in sorted(glob.glob(os.path.join(DIR, "snapshots", "snapshot_*.json"))):
        try:
            snap = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        date_str = snap.get("date")
        if not date_str or date_str == today:
            continue
        if is_seed(snap):
            print("[backfill] %s 为种子数据，跳过" % os.path.basename(f))
            continue
        # market_snapshots
        mo = snap.get("market_overview") or {}
        if mo.get("turnover_total") and not date_exists(c, "market_snapshots", date_str):
            if not dry:
                c.insert("market_snapshots", {
                    "snapshot_time": date_str + "T15:00:00+08:00",
                    "date": date_str,
                    "sh_change": mo.get("sh_change"),
                    "sz_change": mo.get("sz_change"),
                    "cyb_change": mo.get("cyb_change"),
                    "turnover_total": mo.get("turnover_total"),
                    "rise_count": mo.get("up_count"),
                    "fall_count": mo.get("down_count"),
                })
                inserted += 1
            print("[backfill] market_snapshots %s %s" % (date_str, "(dry)" if dry else "已补入"))
        # sector_rankings
        secs = snap.get("sectors") or []
        if secs and not date_exists(c, "sector_rankings", date_str):
            if not dry:
                batch = [{
                    "recorded_at": date_str + "T15:00:00+08:00",
                    "date": date_str,
                    "sector_name": str(s.get("name", s.get("sector", ""))),
                    "sector_code": str(s.get("code", "")),
                    "change_pct": s.get("change"),
                    "net_amount": s.get("net_amount"),
                    "ranking": i + 1,
                } for i, s in enumerate(secs[:50])]
                c.insert("sector_rankings", batch)
                inserted += 1
            print("[backfill] sector_rankings %s %s" % (date_str, "(dry)" if dry else "已补入"))
        # volume_alerts
        va = snap.get("volume_monitor_list") or []
        if va and not date_exists(c, "volume_alerts", date_str):
            if not dry:
                batch = [{
                    "alert_time": date_str + "T15:00:00+08:00",
                    "date": date_str,
                    "code": str(a.get("code", "")),
                    "name": str(a.get("name", "")),
                    "price": a.get("price"),
                    "change": a.get("change"),
                    "volume": a.get("volume"),
                    "amount": a.get("amount"),
                    "sector": str(a.get("sector", "")),
                    "ratio": a.get("ratio"),
                } for a in va[:50]]
                c.insert("volume_alerts", batch)
                inserted += 1
            print("[backfill] volume_alerts %s %s" % (date_str, "(dry)" if dry else "已补入"))

    if not dry:
        print("[backfill] 共补入 %d 行历史数据" % inserted)


def main():
    args = sys.argv[1:]
    mode = "dry"
    if "--clean-stale" in args:
        mode = "clean"
    if "--backfill" in args:
        mode = "back" if mode == "dry" else "all"
    if "--all" in args:
        mode = "all"

    c = client()
    print("=== backfill 模式: %s ===" % mode)
    if mode in ("clean", "all"):
        do_clean_stale(c, dry=False)
    if mode in ("back", "all"):
        do_backfill(c, dry=False)
    if mode == "dry":
        print("--- dry-run: 清洗计划 ---")
        do_clean_stale(c, dry=True)
        print("--- dry-run: 回补计划 ---")
        do_backfill(c, dry=True)


if __name__ == "__main__":
    main()
