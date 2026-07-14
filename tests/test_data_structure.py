#!/usr/bin/env python3
"""验证 A 股投资仪表板数据文件结构"""
import json
import os
import sys

BASE = r"E:\投资工具自用"
DATA_DIR = os.path.join(BASE, "data")
errors = []

def check_file(path, name, expected_type=list):
    """检查 JSON 文件格式"""
    full = os.path.join(DATA_DIR, path) if not path.startswith(BASE) else path
    if not os.path.exists(full):
        errors.append(f"MISSING: {full}")
        return None
    try:
        with open(full, encoding="utf-8") as f:
            data = json.load(f)
        key = list(data.keys()) if isinstance(data, dict) else f"list[{len(data)}]"
        print(f"  [OK] {name}: {key}")
        return data
    except Exception as e:
        errors.append(f"PARSE ERROR: {full} -> {e}")
        return None

print("=" * 60)
print("A 股投资仪表板 — 数据文件结构验证")
print("=" * 60)

# 1. factors.json
print("\n[1] data/factors.json")
d = check_file("factors.json", "factors.json")
if d:
    print(f"      success: {d.get('success')}")
    print(f"      composite: {d.get('composite')}")
    print(f"      factors count: {len(d.get('factors', []))}")
    print(f"      is_live: {d.get('is_live')}")
    factors = d.get("factors", [])
    for f_item in factors:
        print(f"      - {f_item.get('id')}: {f_item.get('label')} (score={f_item.get('score')})")

# 2. volume_monitor.json
print("\n[2] data/volume_monitor.json")
d = check_file("volume_monitor.json", "volume_monitor.json")
if d:
    print(f"      success: {d.get('success')}")
    print(f"      is_trading: {d.get('is_trading')}")
    print(f"      total: {d.get('total')}")
    print(f"      data count: {len(d.get('data', []))}")
    print(f"      update_time: {d.get('update_time')}")

# 3. industry_chain_config.json
print("\n[3] industry_chain_config.json (root)")
path = os.path.join(BASE, "industry_chain_config.json")
d = check_file(path, "industry_chain_config.json", expected_type=dict)
if d:
    industries = d.get("industries", [])
    print(f"      industries count: {len(industries)}")

# 4. 检查 HTML 引用完整性
print("\n[4] index.html 资源引用检查")
html_path = os.path.join(BASE, "index.html")
if os.path.exists(html_path):
    with open(html_path, encoding="utf-8") as f:
        html = f.read()
    refs = [
        ("styles.css", '<link.*?href="styles.css"'),
        ("app.js", '<script.*?src="app.js"'),
    ]
    import re
    for name, pattern in refs:
        if re.search(pattern, html):
            print(f"  [OK] {name} referenced in index.html")
        else:
            errors.append(f"MISSING REFERENCE: {name} not found in index.html")
else:
    errors.append(f"MISSING: {html_path}")

# 5. 检查 SPA 页面路由
print("\n[5] SPA 页面路由检查")
pages = ["home", "volume", "industry", "review", "review_summary", "history"]
js_path = os.path.join(BASE, "app.js")
with open(js_path, encoding="utf-8") as f:
    js = f.read()
for page in pages:
    if page in js:
        print(f"  [OK] '{page}' route found in app.js")
    else:
        errors.append(f"MISSING ROUTE: '{page}' not found in app.js")

# 总结
print("\n" + "=" * 60)
if errors:
    print(f"发现 {len(errors)} 个问题:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print("所有数据文件结构验证通过!")
    sys.exit(0)
