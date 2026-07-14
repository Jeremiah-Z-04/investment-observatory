# 投资观察站 · DESIGN.md

> 基于 iOS 级量化工具设计规范与 UI 样板图生成。  
> 主色调：品牌蓝 `#4F7DF3` · 语义涨跌：红涨 `#FF4D4F` / 绿跌 `#22C55E`。  
> 适用于 AI 编程代理（Cursor / Claude Code / Google Stitch）消费。

---

## 1. Visual Theme & Atmosphere

### 设计哲学

构建一个**面向 A 股短线交易者的专业暗色数据座舱**。设计语言强调：

- **冷静与精准**：以深蓝色品牌色传递理性决策中枢的气质，替代高饱和暖色，降低长时间盯盘的眼部负担。
- **数据优先**：所有视觉装饰服务于信息读取效率，关键信号不被遮挡。
- **有温度的科技**：玻璃拟态与柔和非线性动效让面板像活的仪器，而非冰冷的报表。
- **中国市场语义**：红涨绿跌作为视觉母语贯穿始终，零学习成本。

### 视觉基调

专业金融、冷静科技、暗色座舱、高信息密度、可视化驱动。

### 核心视觉特征关键词

1. **Deep Navy** — 深海军蓝/近黑背景，降低视觉疲劳，强化蓝色品牌光晕。
2. **Cobalt Accent** — 钴蓝品牌色作为核心强调色，象征理性、决策、科技。
3. **Glassmorphism Lite** — 轻量级毛玻璃与顶部高光，建立悬浮层级感。
4. **Data-First** — 图表、进度、评分是视觉主角，装饰极简。
5. **Subtle Glow** — 仅在焦点元素使用柔和蓝色辉光，避免霓虹泛滥。

### 光影与质感

- 背景：深色渐变（`#0B0F19` → `#111827`），无纹理，保持干净。
- 卡片：半透明深色表面（`rgba(30, 41, 59, 0.82)`）+ 1px 细边框 + 顶部内高光。
- 交互态：hover 时边框亮度提升，按钮/卡片出现蓝色光晕。
- 图表：使用渐变填充、圆润折线、低饱和度边缘。

---

## 2. Color Palette & Roles

### Primary Colors / 品牌主色

| Token | HEX | CSS 变量 | 使用场景 |
|-------|-----|----------|----------|
| 品牌主色 | `#4F7DF3` | `--accent` | 主按钮、高亮、进度条、评分、激活态 |
| 品牌浅蓝 | `#7A9DF8` | `--accent-light` | 悬浮、焦点、渐变终点 |
| 品牌深蓝 | `#3B63D9` | `--accent-dark` | 按下、深色强调 |
| 品牌辉光 | `rgba(79, 125, 243, 0.25)` | `--accent-glow` | 柔和光晕、焦点阴影 |
| 品牌弱背景 | `rgba(79, 125, 243, 0.12)` | `--accent-subtle` | 选中态背景、标签背景 |

### Brand & Dark / 品牌深色变体

| Token | HEX | CSS 变量 | 使用场景 |
|-------|-----|----------|----------|
| 最深背景 | `#0B0F19` | `--slate-950` / `--bg` | 页面主背景 |
| 主表面 | `#111827` | `--slate-900` | 侧边栏、深层表面 |
| 卡片表面 | `#1E293B` | `--slate-800` / `--surface-solid` | 卡片、面板背景 |
| 边框灰 | `#334155` | `--slate-700` | 边框、分隔线 |

### Accent / Interactive / 强调与交互色

| Token | HEX | CSS 变量 | 使用场景 |
|-------|-----|----------|----------|
| 信息提示 | `#38BDF8` | `--info` | 信息标签、辅助指标 |
| 信息弱背景 | `rgba(56, 189, 248, 0.12)` | `--info-soft` | 信息提示背景 |
| 警告/中性 | `#F59E0B` | `--warn` | 警告、中等风险、中性状态 |
| 警告弱背景 | `rgba(245, 158, 11, 0.12)` | `--warn-soft` | 警告标签背景 |

### Neutral / Gray Scale / 中性灰阶

| Token | HEX | CSS 变量 | 使用场景 |
|-------|-----|----------|----------|
| 主文字 | `#F1F5F9` | `--text-primary` | 标题、重要数值 |
| 次要文字 | `#94A3B8` | `--text-secondary` | 副标题、说明 |
| 辅助文字 | `#64748B` | `--text-tertiary` | 时间戳、占位符 |
| 深色反色 | `#0F172A` | `--text-inverse` | 浅色背景上的文字 |

### Surface & Borders / 表面与边框

| Token | HEX / RGBA | CSS 变量 | 使用场景 |
|-------|------------|----------|----------|
| 卡片表面 | `rgba(30, 41, 59, 0.82)` | `--surface` | 卡片背景 |
| 抬升表面 | `rgba(51, 65, 85, 0.88)` | `--surface-raised` | 悬浮、弹层、下拉 |
| 玻璃底色 | `rgba(255, 255, 255, 0.04)` | `--glass` | 玻璃拟态按钮、输入框 |
| 玻璃边框 | `rgba(255, 255, 255, 0.08)` | `--glass-border` | 默认边框 |
| 强玻璃边框 | `rgba(255, 255, 255, 0.14)` | `--glass-border-strong` | 悬停边框 |
| 顶部高光 | `rgba(255, 255, 255, 0.06)` | `--glass-highlight` | 卡片顶部内高光 |

### Semantic Colors / 语义色（A股红涨绿跌）

| Token | HEX | CSS 变量 | 使用场景 |
|-------|-----|----------|----------|
| 涨 / 红 | `#FF4D4F` | `--up` | 上涨、positive、涨停、高风险 |
| 涨弱背景 | `rgba(255, 77, 79, 0.12)` | `--up-soft` | 上涨背景、淡红填充 |
| 跌 / 绿 | `#22C55E` | `--down` | 下跌、negative、跌停、低风险 |
| 跌弱背景 | `rgba(34, 197, 94, 0.12)` | `--down-soft` | 下跌背景、淡绿填充 |
| 成功 | `#22C55E` | `--down` | 成功状态复用绿色 |
| 危险 | `#FF4D4F` | `--up` | 危险/错误复用红色 |

### Shadow Colors / 阴影色

| Token | HEX / RGBA | CSS 变量 | 使用场景 |
|-------|------------|----------|----------|
| 小阴影 | `rgba(0, 0, 0, 0.15)` | `--shadow-sm` | 标签、小按钮 |
| 中阴影 | `rgba(0, 0, 0, 0.18)` | `--shadow-md` | 卡片默认投影 |
| 大阴影 | `rgba(0, 0, 0, 0.28)` | `--shadow-lg` | 模态、抽屉、侧边栏 |
| 蓝色辉光 | `rgba(79, 125, 243, 0.25)` | `--shadow-glow` | 焦点环、按钮光晕 |
| 内高光 | `inset 0 1px 0 rgba(255,255,255,0.06)` | `--shadow-inner-highlight` | 卡片顶部高光 |

---

## 3. Typography Rules

### Font Family

| 用途 | 字体栈 |
|------|--------|
| 标题 / Display | `"SF Pro Display", -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif` |
| 正文 / Text | `"SF Pro Text", -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif` |
| 数字 / Mono | `"SF Mono", "SF Pro Text", ui-monospace, monospace`（使用 `font-variant-numeric: tabular-nums`） |

### Type Scale

| Token | Font Size | Font Weight | Line Height | Letter Spacing | 用途 |
|-------|-----------|-------------|-------------|----------------|------|
| `--text-4xl` | 48px / 3rem | 700 | 1.1 | -0.02em | 综合评分 Hero |
| `--text-3xl` | 32px / 2rem | 700 | 1.15 | -0.01em | 大标题、指数价格 |
| `--text-2xl` | 24px / 1.5rem | 700 | 1.2 | -0.01em | 页面标题 |
| `--text-xl` | 20px / 1.25rem | 700 | 1.3 | -0.01em | 卡片标题、区域标题 |
| `--text-lg` | 17px / 1.0625rem | 600 | 1.4 | 0 | 小标题、导航品牌 |
| `--text-base` | 15px / 0.9375rem | 500 | 1.5 | 0 | 正文、按钮 |
| `--text-sm` | 13px / 0.8125rem | 500 | 1.5 | 0 | 辅助文字、表头 |
| `--text-xs` | 12px / 0.75rem | 500 | 1.4 | 0.01em | 标签、脚注、时间戳 |

### 设计哲学

- **字重克制**：标题 700，正文 500，避免过细字重导致可读性下降。
- **数字等宽**：所有价格、涨跌幅、成交量使用 `tabular-nums`，确保列对齐。
- **负字距标题**：大号数字与标题使用轻微负字距，提升紧凑感与专业度。
- **行高宽松**：正文 1.5，降低高密度信息阅读压力。

---

## 4. Component Stylings

### Buttons

```css
/* Primary */
.btn-primary {
  background: linear-gradient(135deg, var(--accent), var(--accent-light));
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  padding: 10px 18px;
  font-weight: 600;
  box-shadow: 0 4px 12px var(--accent-glow);
  transition: all 200ms var(--ease-out-quart);
}
.btn-primary:hover { background: var(--accent-light); transform: translateY(-1px); }
.btn-primary:active { transform: scale(0.97); }

/* Secondary */
.btn-secondary {
  background: var(--glass);
  color: var(--text-primary);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-sm);
  padding: 10px 18px;
  font-weight: 600;
  transition: all 200ms var(--ease-out-quart);
}
.btn-secondary:hover { background: var(--surface-raised); border-color: var(--glass-border-strong); }

/* Ghost */
.btn-ghost {
  background: transparent;
  color: var(--text-secondary);
  border: 1px solid transparent;
  border-radius: var(--radius-sm);
  padding: 10px 18px;
  font-weight: 600;
}
.btn-ghost:hover { background: var(--glass); color: var(--text-primary); }

/* Danger */
.btn-danger {
  background: var(--up-soft);
  color: var(--up);
  border: 1px solid rgba(255, 77, 79, 0.3);
  border-radius: var(--radius-sm);
  padding: 10px 18px;
  font-weight: 600;
}
.btn-danger:hover { background: rgba(255, 77, 79, 0.2); }
```

### Cards

```css
.card {
  background: var(--surface);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  box-shadow: var(--shadow-sm), var(--shadow-inner-highlight);
  transition: transform 200ms var(--ease-out-quart),
              border-color 200ms var(--ease-out-quart),
              box-shadow 200ms var(--ease-out-quart);
}
.card:hover {
  transform: translateY(-2px);
  border-color: var(--glass-border-strong);
  box-shadow: var(--shadow-md), var(--shadow-inner-highlight);
}
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-4);
  padding-bottom: var(--space-3);
  border-bottom: 1px solid var(--glass-border);
}
.card-title {
  font-size: var(--text-lg);
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: var(--space-2);
}
```

### Inputs

```css
.input {
  background: var(--glass);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-sm);
  padding: 10px 14px;
  color: var(--text-primary);
  font-size: var(--text-sm);
  transition: border-color 200ms var(--ease-out-quart),
              box-shadow 200ms var(--ease-out-quart);
}
.input:focus {
  outline: none;
  border-color: var(--accent-light);
  box-shadow: 0 0 0 3px var(--accent-glow);
}
.input::placeholder { color: var(--text-tertiary); }
```

### Navigation

```css
.nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  font-size: var(--text-sm);
  font-weight: 500;
  cursor: pointer;
  position: relative;
  transition: all 200ms var(--ease-out-quart);
}
.nav-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%) scaleY(0);
  width: 3px;
  height: 20px;
  border-radius: 0 2px 2px 0;
  background: var(--accent);
  transition: transform 300ms var(--ease-out-expo);
}
.nav-item.active {
  background: var(--accent-subtle);
  color: var(--accent-light);
}
.nav-item.active::before { transform: translateY(-50%) scaleY(1); }
```

### Badges / Tags

```css
.tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: var(--radius-pill);
  font-size: var(--text-xs);
  font-weight: 600;
}
.tag-blue { background: var(--accent-subtle); color: var(--accent-light); }
.tag-green { background: var(--down-soft); color: var(--down); }
.tag-red { background: var(--up-soft); color: var(--up); }
.tag-yellow { background: var(--warn-soft); color: var(--warn); }
.tag-gray { background: var(--glass); color: var(--text-secondary); }
.tag-dot { width: 6px; height: 6px; border-radius: 50%; background: currentColor; }
```

### Modals / Dialogs

```css
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(11, 15, 25, 0.72);
  backdrop-filter: blur(8px);
  z-index: 200;
  opacity: 0;
  transition: opacity 300ms var(--ease-out-quart);
}
.modal-backdrop.active { opacity: 1; }
.modal-content {
  background: var(--surface-raised);
  border: 1px solid var(--glass-border-strong);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  padding: var(--space-6);
  max-width: 520px;
  transform: scale(0.92) translateY(20px);
  transition: transform 400ms var(--ease-out-expo);
}
.modal-backdrop.active .modal-content { transform: scale(1) translateY(0); }
```

---

## 5. Layout Principles

### Spacing System

基于 4pt 网格：

| Token | Value |
|-------|-------|
| `--space-1` | 4px |
| `--space-2` | 8px |
| `--space-3` | 12px |
| `--space-4` | 16px |
| `--space-5` | 20px |
| `--space-6` | 24px |
| `--space-8` | 32px |
| `--space-10` | 40px |
| `--space-12` | 48px |

### Grid System

- 主内容区使用 12 列 CSS Grid。
- 大卡片默认 `col-4`（桌面），平板 `col-6`，移动端 `col-12`。
- 卡片间距：`gap: var(--space-4)`（16px）。

### Container

- 无全局 max-width，内容占满主区域。
- 主内容区内边距：`var(--space-6)`（24px）。
- 侧边栏宽度：`var(--sidebar-width)`（240px），平板压缩至 64px，移动端隐藏改为底部导航。

### Section Spacing

- 页面标题区与卡片区之间：24px。
- 卡片组内部：16px。
- 卡片内部标题与内容：16px。
- 表单/表格组之间：16px。

### 留白哲学

- 深色背景下通过“大边框半径 + 半透表面 + 内高光”创造呼吸感，而非单纯依赖白色留白。
- 卡片之间保持 16px 统一间隙，形成可预测的视觉节奏。
- 避免在卡片内堆叠多层嵌套，信息密度通过字体层级与颜色对比控制。

---

## 6. Depth & Elevation

### Shadow System

```css
--shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.15);
--shadow-md: 0 4px 12px rgba(0, 0, 0, 0.18);
--shadow-lg: 0 12px 32px rgba(0, 0, 0, 0.28);
--shadow-glow: 0 0 20px rgba(79, 125, 243, 0.25);
--shadow-inner-highlight: inset 0 1px 0 rgba(255, 255, 255, 0.06);
```

### Surface Layers

| Layer | Token | 用途 |
|-------|-------|------|
| Background | `--bg` | 页面最深背景 |
| Surface | `--surface` | 卡片、面板 |
| Elevated | `--surface-raised` | 悬浮、下拉、弹层 |
| Overlay | `--glass` +  backdrop-filter | 模态遮罩、玻璃按钮 |

### Z-index Scale

| 层级 | 值 | 用途 |
|------|-----|------|
| 背景 | 0 | 页面内容 |
| 顶部栏 | 50 | `.main-header` sticky |
| 侧边栏 | 100 | `.sidebar` |
| 下拉/浮层 | 150 | 下拉菜单、提示 |
| 模态遮罩 | 200 | `.modal-backdrop` |
| 通知 | 250 | Toast 通知 |
| Loading | 1000 | 全屏加载 |

### Backdrop Effects

```css
.sidebar {
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
}
.main-header {
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}
.modal-backdrop {
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}
```

---

## 7. Do's and Don'ts

### Do's

1. **使用蓝色品牌色作为唯一主强调色**，仅在涨跌、风险等级使用红/绿语义色。
2. **保持卡片统一半径 16px、小控件 8px**，形成一致的圆角语言。
3. **所有数字使用 tabular-nums**，确保表格与指标列对齐。
4. **hover 时仅提升边框亮度与微抬升**，避免强烈发光或颜色突变。
5. **使用非线性 Expo 缓动**（cubic-bezier(0.16, 1, 0.3, 1)）做入场与切换。
6. **数据更新时使用数字滚动 + 脉冲反馈**，让用户感知到实时变化。
7. **尊重 `prefers-reduced-motion`**，在减少动效模式下关闭位移动画，保留透明度过渡。
8. **所有可点击区域最小 44px**，确保移动端可盲操。

### Don'ts

1. **不要使用纯黑 `#000000` 或纯白 `#FFFFFF`** 作为背景/表面色，使用深蓝灰系列。
2. **不要滥用霓虹渐变或大面积发光**，蓝色辉光仅用于焦点元素。
3. **不要使用等宽字体作为正文字体**，仅用于数字。
4. **不要在一个屏幕内使用超过 3 种主色**，避免视觉混乱。
5. **不要动画化 `width`、`height`、`left`、`top` 等布局属性**，只动画 `transform` / `opacity`。
6. **不要让移动端隐藏关键功能**，所有模块需支持响应式重排。
7. **不要使用弹跳/弹性缓动做长距离动画**，仅在按钮按压反馈使用短弹簧。
8. **不要让空状态只显示“暂无数据”**，提供 actionable 提示或占位骨架。

---

## 8. Responsive Behavior

### Breakpoints

| 断点 | 宽度 | 行为 |
|------|------|------|
| Mobile | < 768px | 底部 Tab 导航，卡片单列，侧边栏隐藏 |
| Tablet | 768px - 1023px | 侧边栏压缩为 64px（图标-only），卡片双列 |
| Desktop | 1024px - 1439px | 完整侧边栏 240px，卡片 4/6 列自适应 |
| Wide | ≥ 1440px | 完整侧边栏，卡片 col-4 三列布局 |

### Touch Targets

- 导航项高度：44px。
- 按钮最小高度：40px。
- 图标按钮：36px × 36px。
- 表格行高：44px。

### 折叠策略

- 桌面：左侧固定导航 + 主内容网格。
- 平板：侧边栏宽度压缩，显示图标，隐藏文字标签。
- 移动端：
  - 侧边栏完全隐藏，通过汉堡菜单可临时展开。
  - 底部出现 5 项固定 Tab 导航（看板、量能、产业、复盘、历史）。
  - 卡片全部单列，指数条水平滚动。
  - 产业逻辑改为全宽桑基图/树图。

### Font Scaling

- 桌面使用固定 rem 字号，确保座舱 UI 空间确定性。
- 移动端标题字号缩小一级（`--text-4xl` → 40px），正文保持可读。
- 支持浏览器默认字号缩放，不强制固定 px。

---

## 9. Agent Prompt Guide

### Quick Reference

- 主色：`--accent #4F7DF3`，浅蓝 `--accent-light #7A9DF8`。
- 涨跌：`--up #FF4D4F`（涨），`--down #22C55E`（跌）。
- 卡片：`--surface` 背景，`--radius-lg` 圆角，`--glass-border` 边框。
- 动画：`easeOutExpo`（cubic-bezier(0.16, 1, 0.3, 1)），500ms 入场，200ms 状态切换。
- 字体：标题 `SF Pro Display`，正文 `SF Pro Text`，数字 `SF Mono` + `tabular-nums`。
- 布局：12 列 Grid，间距 16px，侧边栏 240px，主内容 padding 24px。

### Component Prompts

1. **生成一个蓝色主按钮**：`创建一个 primary 按钮，使用 #4F7DF3 渐变背景，白色文字，8px 圆角，hover 微抬升，active scale(0.97)，带蓝色辉光。`
2. **生成一个数据卡片**：`创建一个卡片组件，使用 --surface 半透明背景、16px 圆角、1px --glass-border 边框、顶部内高光，hover 时边框提亮并 translateY(-2px)。`
3. **生成一个 tag 标签**：`创建一个 capsule 标签组件，支持 blue/green/red/yellow/gray 五种类型，左侧 6px 圆点，使用对应语义色的 soft 背景。`
4. **生成一个导航项**：`生成左侧导航项，默认灰色文字，active 状态左侧 3px 蓝色指示灯 + 浅蓝背景，使用 anime.js 滑动指示灯。`
5. **生成一个数值指标卡**：`生成指标卡组件，包含标签、大数值（tabular-nums）、涨跌幅（红涨绿跌），数值更新时使用数字滚动动画。`
6. **生成一个进度条**：`生成进度条，蓝色填充，高度 6px，圆角 3px，背景为 rgba(255,255,255,0.05)。`

### Iteration Guide

1. **先确认颜色**：所有新生成的组件必须使用 `--accent` 蓝色，而非橙色或紫色。
2. **再确认字体**：数字必须 `font-variant-numeric: tabular-nums`。
3. **动效一致性**：入场动画统一使用 `easeOutExpo`，时长 500ms；状态切换 200ms。
4. **响应式优先**：每个新模块必须在 desktop/tablet/mobile 三种宽度下检查布局。
5. **减少动效**：所有动画需包装在 `prefers-reduced-motion` 媒体查询中做降级。
6. **数据空状态**：每个数据区域需提供加载态、空状态、错误状态三种视觉。
7. **图表主题**：ECharts 图表使用透明背景，坐标轴 `--text-tertiary`，网格线 `--glass-border`。
8. **语义色不可逆**：中国市场始终红涨绿跌，不要反着用。
9. **圆角体系**：卡片 16px，按钮/输入 8px，标签 pill，不要混用。
10. **Z 层级检查**：新浮层需明确 z-index，避免覆盖冲突。
