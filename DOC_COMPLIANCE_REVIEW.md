# 项目文档 vs 当前代码 · 符合性核查

> 核查时间：2026-07-14
> 核查范围：用户提供的《项目文档》（一、概述 / 二、功能模块 / 三、底层机制 / 四、部署方案 / 五、验收标准）对照 `E:\投资工具自用` 当前代码（`server.py` / `dataservice.py` / `factors_engine.py` / `review_rules.py` / `app.js` / `build_data.py` / `.github/workflows/deploy.yml` / `volume_history.json` / `snapshots/`）。

## 一、总体结论

| 维度 | 结论 |
|------|------|
| 算法 / 业务逻辑（因子权重、量能规则、快照命名、双数据源） | ✅ 高度符合 |
| 模块功能存在性（四因子 / 量能 / 盘后 / 产业 / 复盘 / 历史） | ✅ 功能均存在 |
| 部署方案（平台、频率、快照自动化） | ❌ 多处不符 |
| 模块数量与结构 | ❌ 文档漏列"历史数据"独立模块 |
| 数据规模（量能历史天数、股票覆盖） | ⚠️ 与文档描述有差距 |
| 复盘模板文案 | ⚠️ 框架一致、具体措辞不同 |

**一句话**：算法层可以放心，文档需要按"实际部署形态 + 现有数据规模 + 真实模块结构"重写第 2 / 4 章。

---

## 二、✅ 完全符合（可信任）

1. **纯规则化、无大模型** — 全部为固定公式，无 LLM 调用。✅
2. **双数据源自动切换 + `get_market_data()` 统一入口** — `dataservice.py:1006` 定义统一函数；`server.py` 的 `/api/factors` 交易时段取实时、非交易时段降级快照（`is_trading_time()`）。✅
3. **轻量化 JSON、无强制数据库依赖** — `supabase_service.py` 仅用标准库（`urllib` 调 REST），且 `server.py:3-6` 用 `try/except` 可选导入，未配置时自动降级。✅
4. **四因子权重 35/30/20/15** — `factors_engine.py:194`：`w = {"sentiment":0.35,"sector":0.30,"chip":0.20,"overnight":0.15}`。✅
5. **顶部 6 个市场指标卡** — `/api/factors` 返回 `limit_up_count / limit_down_count / bomb_rate / turnover_total / northbound_net / max_board_height`。✅
6. **综合概率卡（核心操作 / 禁忌 / 约束）** — `factors_engine.py:140-175` `calc_daily_advice` 输出 `core_action / forbidden / constraint_desc`；`outlook_desc` "Balanced, awaiting catalyst" 与文档示例 48 分完全一致（`:226`）。✅
7. **量能筛选：任意 1 天 ≥ 2 倍即触发** — `dataservice.py:425-426`：`any(today_vol >= v * 2 for v in hist_vols)`。✅ 与文档 2.2.1 一致。
8. **放量倍数 = 当日量 / 前 N 日均量** — `dataservice.py:429-430`：`ratio = today_vol / avg_hist`。✅ 与文档 2.2.2 一致。
9. **单位统一"手"→ 展示"万手"、代码 6 位纯数字** — `dataservice.py:106`（注释 Volume in 手）、`:139`（`len(code)!=6 or not code.isdigit()` 过滤）。✅
10. **收盘快照命名 `snapshot_YYYYMMDD.json`** — `dataservice.py:967`；`snapshots/` 目录下确有 `snapshot_20260714.json`。✅
11. **盘后复盘 3 子 Tab + 模板生成** — `server.py` 暴露 `/api/review/generate1/2/3`，`review_rules.py` 对应 `format_template1/2/3`。✅
12. **GitHub Actions 自动更新 + 手动触发 + 仅工作日** — `deploy.yml`：`schedule cron '1-5'`、`workflow_dispatch`、`push` 触发。✅
13. **前端原生 HTML/CSS/JS 无框架** — `index.html` / `app.js` / `styles.css` 无任何框架依赖。✅
14. **深色科技风 / 蓝紫主色 / 玻璃拟态** — 文档 1.2 描述与近期 redesign（`DESIGN_SYSTEM.md` / `styles.css`）一致。✅

---

## 三、❌ 不符合（需改文档）

### 1. 模块数量：文档 5 个，实际 6 个
文档第 2 章只列 2.1–2.5（四因子 / 量能 / 盘后复盘 / 产业 / 复盘工具），**漏列独立的"历史数据"模块**。
实际 `app.js` 导航为 6 项（`app.js:8-13`）：
`home`(四因子看板) · `volume`(量能监测) · `industry`(产业逻辑) · `review_summary`(盘后复盘) · `review`(复盘工具) · **`history`(历史数据)**。
> 文档把"历史数据查询"塞进 2.5 复盘工具，但代码里它是独立顶级模块（4 个 Tab：因子趋势 / 量能 / 快照 / 板块）。

### 2. 部署平台：文档写 Cloudflare Pages，实际是 GitHub Pages
文档 4.1："托管在 **Cloudflare Pages**"。
实际 `.github/workflows/deploy.yml` 用的是 `actions/deploy-pages@v4` + `actions/configure-pages@v5` + `upload-pages-artifact` —— 这是 **GitHub Pages**，不是 Cloudflare。

### 3. 更新频率：文档每 15 分钟，实际每 30 分钟
文档 4.2："上午盘 / 下午盘 **每 15 分钟**更新一次"。
实际 cron 为 `*/30 1-7 * * 1-5`（即北京时 9:00–15:00 **每 30 分钟**），且**没有单独的 15:35 收盘快照任务**。

### 4. 收盘快照的"CI 自动生成"不成立
文档 3.2 / 4 声称"每日收盘后 15:35 自动生成 `snapshot_YYYYMMDD.json`"。
实际 `build_data.py`（CI 调用的脚本）**只生成 `data/*.json`**（factors / volume_monitor / review_* / stock_search / history_*），**不生成 `snapshot_YYYYMMDD.json`**。快照目前由**本地常驻运行的服务器**（`dataservice.build_daily_snapshot`）生成。这意味着在"纯静态免费部署"路径下，快照不会被每日生成/提交，历史回溯的快照来源会缺失。

---

## 四、⚠️ 部分符合 / 需澄清

### 5. 复盘模板文案不一致
文档 2.3.2 给出固定模板（【盘后快速复盘】/ `A. 当前情绪周期阶段：…` / `题材逻辑：主线…带动支线…` / `明天开盘第一眼必须看：…的竞价强度`）。
实际 `review_rules.format_template1`（`review_rules.py:326-357`）结构同属 A/B/C/D 四段，但**措辞、编号、字段不同**：
- 标题为【A. 情绪周期阶段】而非"当前情绪周期阶段："
- 无"题材逻辑：主线…带动支线…"固定句
- 无"明天开盘第一眼必须看"固定句，仅【D. 明日风向标】
- 活口条目格式为 `名称（代码）— 标签 — 辨识度`
> 结论：框架一致，具体文案与文档模板不同，文档要么同步代码、要么明确"模板以代码为准"。

### 6. `volume_history.json` 规模与文档不符
文档 3.3："全市场个股近 **20 个交易日的日成交量数据**"。
实际 `volume_history.json` 结构为 `{days:[8天], stocks:{749只}}` —— **仅 8 天、749 只股票**（非 20 天、非全市场 ~5000 只）。量能监测功能可用，但历史窗口与覆盖度小于文档描述。

### 7. 产业逻辑（2.4）子功能未完全对应
代码 `app.js` 产业模块以"**产业链上下游映射**"为核心（`renderIndustryChain` / `industry_chain_config.json`）。文档还列"行业板块涨幅榜""题材概念分类（科技/消费/周期/金融）"——这两项在代码中是否作为独立视图呈现**待确认**；且 **industry 模块在静态部署下缺数据**：`build_data.py` 未生成 industry 静态文件，`app.js:377` 回退路径会请求 `data/industry_chain.json`（仓库中并不存在，真实文件在根目录 `industry_chain_config.json`），静态模式下产业页可能加载失败。

### 8. 北向资金数据真实性风险
文档将"北向资金（亿）"列为 6 大核心实时指标之一。但沪深港通**实时净买额自 2024-08 起已停止披露**，代码虽保留 `_fetch_northbound_flow`（`dataservice.py:784`），实际大概率长期为 0 或占位值。属于"文档承诺了现实已不可得的数据"问题。

### 9. 历史数据中心静态数据强依赖 Supabase
`app.js` 的 `history/factors|volume|snapshots|sectors` 在静态模式下读 `data/history_*.json`，而 `build_data.py` 这些文件**全部来自 `supabase_service` 查询**。若未配置 Supabase，这些静态文件为空/报错（如 `history_sectors` 返回 `error:"Supabase not configured"`），历史模块在免费静态部署下不完整。

### 10. 综合概率卡字段命名差异
文档 2.1.2 列"仓位建议 / 风险等级 / 核心操作 / 禁忌提示"。代码 `advice` 对象含 `core_action`（核心操作）/ `forbidden`（禁忌）/ `constraint_desc`（约束），但**无独立的"仓位建议(%)""风险等级"字段**——二者可能由前端按 composite 分数区间推导，文档应说明来源。

### 11. 节假日处理
文档 4.2："周末、节假日自动不执行"。cron `1-5` 仅排除周六日，**不包含法定节假日**（如调休工作日仍会跑、节假日不跑但实时接口也会失败降级），与"节假日自动不执行"表述略有出入。

---

## 五、建议修改优先级

| 优先级 | 修改项 | 改文档 or 改代码 |
|--------|--------|------------------|
| P0 | 部署平台 Cloudflare → GitHub Pages；频率 15→30 分钟 | 改文档 |
| P0 | 模块数 5→6，单独列出"历史数据"模块 | 改文档 |
| P0 | 澄清快照由"常驻服务器"生成，纯静态部署不会自动生成快照 | 改文档 |
| P1 | `volume_history` 8 天 / 749 只 → 改为如实描述，或扩充数据 | 文档+数据 |
| P1 | 北向资金标注"已停披，可能为占位值" | 改文档 |
| P1 | 历史模块静态数据依赖 Supabase，需注明或补充生成逻辑 | 文档+脚本 |
| P2 | 复盘模板文案与 `format_template1` 对齐 | 文档 or 代码 |
| P2 | 产业模块静态数据缺失（industry_chain 静态化） | 改脚本 |
| P2 | 综合概率卡字段命名对齐 | 文档 or 代码 |

---

## 六、附：关键证据索引

- 因子权重 `factors_engine.py:194`
- 量能 2 倍规则 `dataservice.py:425-426`；倍数 `:429-430`；单位 `:106`；代码 `:139`
- 快照命名 `dataservice.py:967`；目录 `snapshots/snapshot_20260714.json`
- 统一入口 `dataservice.py:1006`；交易时段判断 `dataservice.py:941`
- 部署 `deploy.yml`（GitHub Pages，cron `*/30 1-7 * * 1-5`）
- 静态映射 `app.js:361-381`（含 `history/*` → `data/history_*.json`）
- 量能历史规模 `volume_history.json`（`days` 8 项 / `stocks` 749 项）
- 复盘模板 `review_rules.py:326-357`
