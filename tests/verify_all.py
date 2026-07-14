#!/usr/bin/env python3
"""投资观察站 · 从服务器拉取页面验证"""
import json, sys, os
sys.path.insert(0, r"E:\投资工具自用")

# Verify data files
DATA_FILES = [
    ("data/factors.json", ["success", "composite", "factors"]),
    ("data/volume_monitor.json", ["success", "data"]),
    ("data/review_summary.json", ["success"]),
    ("data/review_stocks.json", []),
    ("data/factors_history.json", []),
    ("industry_chain_config.json", ["industries"]),
]

all_ok = True
for path, required_keys in DATA_FILES:
    full = os.path.join(r"E:\投资工具自用", path)
    try:
        with open(full, "r", encoding="utf-8") as f:
            data = json.load(f)
        missing = [k for k in required_keys if k not in data]
        if missing:
            print(f"  [WARN] {path}: missing keys {missing}")
            all_ok = False
        else:
            print(f"  [OK] {path}: {len(str(data))} bytes")
    except Exception as e:
        print(f"  [FAIL] {path}: {e}")
        all_ok = False

# Verify industry_chain_config structure
with open(r"E:\投资工具自用\industry_chain_config.json", "r", encoding="utf-8") as f:
    cfg = json.load(f)
ind = cfg.get("industries", [])
print(f"\n  产业链数量: {len(ind)}")
for i in ind:
    nodes = i.get("nodes", [])
    print(f"    - {i.get('name')}: {len(nodes)} nodes, boom={i.get('boom_score')}")

# HTTP check
try:
    import urllib.request
    for path in ["index.html", "styles.css", "app.js", "anime-plus.js"]:
        r = urllib.request.urlopen(f"http://127.0.0.1:8769/{path}")
        print(f"  [HTTP OK] /{path} -> {r.status} ({len(r.read())} bytes)")
except Exception as e:
    print(f"  [WARN] HTTP check failed: {e}")

print(f"\n{'='*60}")
print(f"结果: {'全部通过' if all_ok else '有问题需修复'}")
