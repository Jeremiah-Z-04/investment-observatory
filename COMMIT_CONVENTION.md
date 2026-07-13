# 投资观察站 — Commit Message 规范

## 格式

```
<type>(<scope>): <subject>

[body]

[footer]
```

## Type 类型

| 类型 | 含义 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat(dashboard): 新增北向资金净流入图表` |
| `fix` | Bug修复 | `fix(api): 修复东方财富接口超时处理` |
| `refactor` | 代码重构 | `refactor(scoring): 优化五维打分计算逻辑` |
| `perf` | 性能优化 | `perf(data): 减少行情数据缓存过期时间` |
| `style` | 样式调整 | `style(theme): 调整深色主题对比度` |
| `docs` | 文档更新 | `docs(readme): 补充数据服务使用说明` |
| `chore` | 构建/工具 | `chore(ci): 更新 GitHub Actions 部署流程` |
| `data` | 数据更新 | `data(scores): 更新主线赛道打分配置` |
| `config` | 配置变更 | `config(thres): 调整冰点涨停阈值` |
| `test` | 测试相关 | `test(scoring): 添加五维打分单元测试` |

## Scope 范围

| 范围 | 说明 |
|------|------|
| `dashboard` | 四因子看板 |
| `industry` | 产业逻辑页面 |
| `review` | 复盘工具 |
| `volume` | 量能监测 |
| `scoring` | 五维打分引擎 |
| `api` | 数据接口/服务端 |
| `data` | 数据层 |
| `ui` | 用户界面 |
| `theme` | 主题样式 |
| `ci` | CI/CD |
| `hooks` | Git hooks |
| `docs` | 文档 |

## Subject 规则

- 使用中文或英文，保持项目一致性（推荐中文）
- 不超过 50 个字符
- 不以句号结尾
- 使用祈使语气："新增"而非"新增了"

## Body 规则（可选）

- 详细描述变更原因和上下文
- 每行不超过 72 个字符
- 与 subject 之间空一行

## Footer 规则（可选）

- `BREAKING CHANGE:` 表示不兼容变更
- `Closes #123` 关联 Issue
- `Refs #456` 引用相关 Issue

## 示例

### 简单修复
```
fix(api): 修复行情数据请求超时未重试的问题
```

### 新功能（含详细说明）
```
feat(scoring): 新增存储芯片赛道 HBM 细分链条打分

在原有五维打分基础上，新增 HBM 封装测试、DDR5 接口芯片、
存储模组、晶圆制造四个产业链环节的子评分维度。
每个环节按业绩兑现时间线排列，便于择时判断。
```

### 破坏性变更
```
refactor(data): 重构数据缓存结构，变更 JSON Schema

BREAKING CHANGE: factors.json 字段名由 camelCase 改为 snake_case，
所有引用该文件的前端组件需同步更新。
```
