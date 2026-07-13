# 投资观察站 — Investment Observatory

> 汕头游资专用 · 四因子看板 + 量能监测 + 盘后复盘

## 项目简介

投资观察站是一套面向 A 股短线交易的实时监控与决策辅助系统，整合了四大核心因子（市场情绪、流动性、周期位置、龙头强度）与主线赛道五维量化打分引擎，帮助交易者快速把握市场节奏。

## 功能模块

| 模块 | 说明 |
|------|------|
| **四因子看板** | 市场情绪/流动性/周期位置/龙头强度 四维度实时监控 |
| **产业逻辑** | 产业链上下游关系可视化，支持供应链→制造→模组→终端追踪 |
| **复盘工具** | 基于阈值规则的盘后诊断（情绪周期/幸存者偏差/竞价分析） |
| **量能监测** | 实时成交量异常监控，历史量能对比 |
| **盘后复盘** | 自动化复盘总结生成 |
| **五维打分引擎** | 主线赛道量化评分（供需/订单/业绩/政策/资金） |

### 覆盖赛道

- AI 算力配套（服务器整机/高速PCB/AI铜箔/液冷散热）
- 存储芯片（HBM/DDR5/模组/晶圆）
- 光芯片/光模块（800G/光芯片/光器件/MPO连接器）
- 国产半导体设备（刻蚀/清洗/测试/离子注入）
- 华为昇腾产业链（服务器/电源/连接器/封测）

## 技术架构

```
投资工具自用/
├── index.html              # 前端主页面 (Vanilla JS + ECharts)
├── app.js                  # 前端核心逻辑 (~69KB)
├── server.py               # HTTP 数据服务器 (端口 8765)
├── dataservice.py          # 实时数据获取层 (东方财富API)
├── factors_engine.py       # 四因子实时计算引擎
├── scoring.py              # 主线赛道五维量化打分引擎
├── scoring_config.json     # 打分配置 (5条主线，15项指标)
├── review_rules.py         # 复盘阈值规则引擎
├── industry_chain_config.json  # 产业链配置
├── tracking_config.json    # 跟踪标的配置
├── i18n.json               # 中英文双语配置
│
├── build_data.py           # CI 静态数据构建脚本
├── .github/workflows/      # GitHub Pages 自动部署
│
├── sentiment-warning-system/  # 情绪预警子系统
├── data/                   # 静态数据文件
├── snapshots/              # 行情快照
│
├── VERSION                 # 语义化版本号
├── CHANGELOG.md            # 变更日志
├── COMMIT_CONVENTION.md    # 提交规范
├── .gitmessage             # 提交信息模板
├── .githooks/              # Git Hooks
└── README.md
```

### 技术栈

- **后端**: Python 3 (纯标准库，零依赖)
- **前端**: Vanilla JavaScript + ECharts 5.5
- **数据源**: 东方财富免费公开 API
- **部署**: GitHub Pages + GitHub Actions
- **缓存**: 内存缓存 + JSON 文件快照

## 快速开始

### 1. 启动数据服务器

```bash
# Windows 双击
启动.bat

# 或命令行
python server.py
```

服务器将在 `http://localhost:8765` 启动。

### 2. 打开前端

浏览器打开 `index.html`，页面将自动连接本地服务器获取实时数据。

### 3. 离线模式

未启动服务器时，页面自动降级为离线模式，使用本地缓存的 JSON 数据。

## Git 工作流

### 提交代码

```bash
# 方式1: 交互式提交 (推荐)
bash commit.sh          # Git Bash
commit.bat              # Windows CMD

# 方式2: 手动提交 (遵循规范)
git add .
git commit -m "feat(dashboard): 新增北向资金净流入图表"
```

### 提交规范

请遵循 [COMMIT_CONVENTION.md](./COMMIT_CONVENTION.md) 中定义的格式：

```
<type>(<scope>): <subject>
```

### Git Hooks

项目配置了自动检查：

- **pre-commit**: 禁止提交临时调试文件、`.pyc` 缓存
- **commit-msg**: 校验提交信息格式
- **post-commit**: 自动记录变更到 `COMMIT_LOG.txt`

### 版本号

版本号遵循语义化版本 (`MAJOR.MINOR.PATCH`)，记录在 `VERSION` 文件中。

## 数据说明

- 行情数据来自东方财富公开 API，仅供个人学习研究使用
- 五维打分配置 (`scoring_config.json`) 中各项参数需根据实际基本面数据定期更新
- 复盘阈值 (`review_rules.py`) 基于历史统计规律，需根据市场环境动态调整

## License

Private — 个人自用项目
