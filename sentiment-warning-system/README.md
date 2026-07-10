# A股主线情绪与阶段见顶预警系统

基于涅槃交易体系「树干树枝理论 + 多因子共振见顶模型」，实时识别主线强度、情绪周期、大盘见顶风险。

## 快速启动

`ash
# 1. 进入项目目录
cd sentiment-warning-system

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动后端 (端口 8766)
python main.py

# 4. 浏览器打开
http://localhost:8766
`

## 技术栈

| 层 | 技术 |
|---|------|
| 前端 | Vue3 + Element Plus + ECharts (CDN) |
| 后端 | Python FastAPI |
| 数据库 | SQLite (自动创建) |
| 数据 | 内置模拟数据 + 预留真实API接口 |

## 五大预警模块

| 模块 | 核心指标 | 权重 |
|------|---------|------|
| 市场广度背离 | 涨跌家数比、权重小票分化、大跌个股数 | 2分 |
| 全市场量能 | 天量判断、量价背离、成交集中度 | 2分 |
| 短线情绪 | 炸板率、连板高度、涨停溢价、大面股 | 2分 |
| 主线树干强度 | 板块成交占比、梯队完整度、资金流向 | 2分 |
| 辅助验证 | MACD顶背离、均线破位、上涨周期 | 2分 |

风险分级：1分=轻度(黄) / 2分=中度(橙) / ≥3分=重度(红)

## API 接口

| 路径 | 说明 |
|------|------|
| /api/market/overview | 大盘核心数据 + 风险评估 |
| /api/market/risk-level | 风险等级 + 触发明细 |
| /api/sector/rank | 板块强度排名 |
| /api/sector/detail | 单板块详情 + 梯队 |
| /api/emotion/daily | 情绪指标全量数据 |
| /api/emotion/history | 历史情绪曲线 |
| /api/backtest/range | 历史预警回测 |
| /api/backtest/accuracy | 预警准确率统计 |

API 文档：http://localhost:8766/docs

## 替换真实数据

修改 main.py 中 generate_market_data() 等函数，接入 TuShare/AkShare 等数据源即可。
