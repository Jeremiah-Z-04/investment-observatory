#!/usr/bin/env python3
"""A 股投资仪表板 — 多视口截图测试
依赖: pip install playwright && playwright install chromium
"""
import os
import sys
import time
from pathlib import Path

BASE = Path(r"E:\投资工具自用")
SCREENSHOT_DIR = BASE / "tests" / "screenshots"
URL = "http://127.0.0.1:8769/index.html"

VIEWPORTS = [
    {"name": "desktop", "width": 1440, "height": 900},
    {"name": "mobile",  "width": 375,  "height": 812},
]

PAGES = ["home", "volume", "industry", "review", "review_summary", "history"]

def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def take_screenshots():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("[SKIP] playwright not installed. Run:")
        print("  pip install playwright")
        print("  playwright install chromium")
        return False

    ensure_dir(SCREENSHOT_DIR)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        results = []

        for vp in VIEWPORTS:
            context = browser.new_context(
                viewport={"width": vp["width"], "height": vp["height"]},
                device_scale_factor=1,
            )
            page = context.new_page()

            try:
                page.goto(URL, wait_until="networkidle", timeout=15000)
            except Exception as e:
                print(f"[WARN] networkidle timeout for {vp['name']}: {e}")
                # fallback: wait manually
                page.wait_for_timeout(5000)

            # 等待 ECharts 渲染 (SPA 初始化)
            page.wait_for_timeout(3000)

            # 对每个页面截图
            for pname in PAGES:
                safe_name = f"{vp['name']}_{pname}"
                path = SCREENSHOT_DIR / f"{safe_name}.png"

                try:
                    # 触发页面切换 (SPA S.nav)
                    if pname != 'home':
                        page.evaluate(f"if(typeof S !== 'undefined' && S.nav) S.nav('{pname}')")
                        page.wait_for_timeout(2000)

                    page.screenshot(path=str(path), full_page=False)
                    size = path.stat().st_size
                    results.append(f"  [OK] {safe_name}.png ({size:,} bytes)")
                except Exception as e:
                    results.append(f"  [FAIL] {safe_name}: {e}")

            context.close()

        browser.close()

    print(f"\n截图结果 ({len(results)} total):")
    for r in results:
        print(r)

    # 验证截图文件存在
    print(f"\n所有截图已保存到: {SCREENSHOT_DIR}")
    screenshots = sorted(SCREENSHOT_DIR.glob("*.png"))
    print(f"共 {len(screenshots)} 个截图文件")
    return True

def main():
    print("=" * 60)
    print("A 股投资仪表板 — 多视口截图测试")
    print(f"URL: {URL}")
    print(f"视口: {[(v['width'], v['height']) for v in VIEWPORTS]}")
    print(f"页面: {PAGES}")
    print("=" * 60)

    success = take_screenshots()
    if not success:
        print("\n截图测试跳过 — Playwright 未安装")
        sys.exit(0)
    sys.exit(0)

if __name__ == "__main__":
    main()
