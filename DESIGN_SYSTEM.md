# 投资观察站 · UI 设计系统

> 版本：1.0  
> 对标：Apple iOS 级非线性动画与触感反馈  
> 动画引擎：anime.js 3.x

## 1. 设计哲学

- **克制的高级感**：少用发光、渐变与重阴影，依靠材质、圆角、间距建立层次。
- **数据优先**：所有装饰服务于阅读效率，不遮挡关键信号。
- **有温度的科技**：玻璃拟态与柔和过渡让面板像活的仪器，而非冰冷的报表。
- **一致的非线性动效**：所有运动使用基于物理的缓动，避免匀速与弹跳。

## 2. 色彩系统

### 2.1 原色板（Primitive）

| Token | 值 | 用途 |
|-------|-----|------|
| `--slate-950` | `#0B0F19` | 最深背景 |
| `--slate-900` | `#111827` | 主表面 |
| `--slate-800` | `#1E293B` | 卡片/面板 |
| `--slate-700` | `#334155` | 边框、分隔 |
| `--slate-500` | `#64748B` | 次要文字 |
| `--slate-400` | `#94A3B8` | 占位、禁用 |
| `--slate-200` | `#E2E8F0` | 浅色文字 |
| `--slate-50` | `#F8FAFC` | 浅色背景 |

### 2.2 品牌与语义色

| Token | 值 | 用途 |
|-------|-----|------|
| `--accent` | `#4F7DF3` | 主品牌、交互、高亮 |
| `--accent-light` | `#7A9DF8` | 悬浮、焦点 |
| `--accent-glow` | `rgba(79, 125, 243, 0.25)` | 柔和辉光 |
| `--up` | `#FF4D4F` | 涨（中国红） |
| `--down` | `#22C55E` | 跌（中国绿） |
| `--warn` | `#F59E0B` | 警告、中性 |
| `--info` | `#38BDF8` | 信息提示 |

### 2.3 表面色（Surface & Glass）

| Token | 值 | 用途 |
|-------|-----|------|
| `--surface` | `rgba(30, 41, 59, 0.85)` | 卡片背景 |
| `--surface-raised` | `rgba(51, 65, 85, 0.9)` | 抬升表面 |
| `--glass` | `rgba(255, 255, 255, 0.06)` | 玻璃拟态 |
| `--glass-border` | `rgba(255, 255, 255, 0.10)` | 玻璃边框 |
| `--glass-highlight` | `rgba(255, 255, 255, 0.08)` | 顶部高光 |

## 3. 字体系统

### 3.1 字体栈

- **标题**：`"SF Pro Display", -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif`
- **正文**：`"SF Pro Text", -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif`
- **数字**：`"SF Mono", "SF Pro Text", ui-monospace, monospace`（使用 tabular-nums）

### 3.2 字号比例（固定 rem）

| Token | 值 | 用途 |
|-------|-----|------|
| `--text-xs` | `0.75rem` | 标签、脚注 |
| `--text-sm` | `0.875rem` | 辅助文字 |
| `--text-base` | `1rem` | 正文 |
| `--text-lg` | `1.125rem` | 小标题 |
| `--text-xl` | `1.25rem` | 区域标题 |
| `--text-2xl` | `1.5rem` | 大标题 |
| `--text-3xl` | `2rem` | 核心指标 |
| `--text-4xl` | `3rem` | 主分数 |

## 4. 间距系统

基于 4pt 网格：

| Token | 值 |
|-------|-----|
| `--space-1` | `4px` |
| `--space-2` | `8px` |
| `--space-3` | `12px` |
| `--space-4` | `16px` |
| `--space-5` | `20px` |
| `--space-6` | `24px` |
| `--space-8` | `32px` |
| `--space-10` | `40px` |
| `--space-12` | `48px` |

## 5. 圆角与阴影

| Token | 值 | 用途 |
|-------|-----|------|
| `--radius-sm` | `8px` | 小按钮、标签 |
| `--radius-md` | `12px` | 卡片 |
| `--radius-lg` | `16px` | 大面板、模态 |
| `--radius-xl` | `24px` | 特殊浮层 |
| `--shadow-sm` | `0 1px 2px rgba(0,0,0,0.15)` | 默认阴影 |
| `--shadow-md` | `0 4px 12px rgba(0,0,0,0.2)` | 悬浮卡片 |
| `--shadow-lg` | `0 12px 32px rgba(0,0,0,0.3)` | 模态、抽屉 |
| `--shadow-glow` | `0 0 20px var(--accent-glow)` | 焦点辉光 |

## 6. 动效系统

### 6.1 缓动曲线

| Token | 曲线 | 用途 |
|-------|------|------|
| `--ease-out-expo` | `cubic-bezier(0.16, 1, 0.3, 1)` | 元素进入、页面切换 |
| `--ease-out-quart` | `cubic-bezier(0.25, 1, 0.5, 1)` | 状态变化、悬浮 |
| `--ease-in-out` | `cubic-bezier(0.65, 0, 0.35, 1)` | 开关、切换 |
| `--ease-spring` | `cubic-bezier(0.34, 1.56, 0.64, 1)` | 按钮按压（极短） |

### 6.2 时长

| Token | 值 | 用途 |
|-------|-----|------|
| `--duration-instant` | `100ms` | 按钮按压、色闪 |
| `--duration-fast` | `200ms` | 悬浮、开关 |
| `--duration-normal` | `300ms` | 卡片展开、面板切换 |
| `--duration-slow` | `500ms` | 页面入场、hero 揭示 |
| `--duration-number` | `800ms` | 数字滚动 |

### 6.3 anime.js 动画规范

所有动画统一通过 `A` 命名空间调用：

```javascript
A.enter(el, delay);           // 元素入场：translateY(16px) + opacity 0 -> 1
A.fadeIn(el, delay);          // 纯淡入
A.slideUp(el, delay);         // 上滑揭示
A.scaleIn(el, delay);         // 缩放进入
A.stagger(container, selector); // 子元素 staggered 入场
A.number(el, from, to);       // 数字滚动
A.pulse(el);                  // 数据刷新脉冲
A.ripple(e);                  // 按钮涟漪
A.press(el);                  // 按压反馈
A.pageTransition(from, to);   // 页面切换
A.modalIn(el);                // 模态进入
A.modalOut(el);               // 模态退出
A.tabIndicator(el);           // tab 指示器滑动
```

## 7. 组件规范

### 7.1 卡片（Card）

- 背景：`--surface`
- 圆角：`--radius-md`
- 边框：`1px solid var(--glass-border)`
- 顶部高光：`inset 0 1px 0 var(--glass-highlight)`
- 悬浮：translateY(-2px) + shadow-md + 边框亮度提升
- 按压：scale(0.995)

### 7.2 按钮

- 主按钮：`--accent` 背景，白色文字，无边框
- 次按钮：透明背景，`--glass-border` 边框
- 幽灵按钮：透明背景，悬停出现微弱背景
- 圆角：`--radius-sm`
- 按压：scale(0.96) + 亮度变化，使用 anime.js spring

### 7.3 导航

- 左侧固定导航栏
- 项目高度 44px，确保可点击区域
- 激活状态：左侧 3px 指示灯 + 背景高亮
- 切换时指示灯滑动（anime.js 控制 left/width）

### 7.4 表格

- 表头：小字、浅色、底部 1px 分隔
- 行高 44px，悬停高亮
- 数值列右对齐，使用 tabular-nums
- 新行进入：staggered slideUp

### 7.5 标签（Tag）

- 小圆角胶囊
- 仅用于状态、分类、强度等级
- Semantic colors 与背景透明度结合

## 8. 响应式策略

- 桌面：左侧固定导航 + 主内容区
- 平板：导航宽度压缩，卡片网格自动调整
- 移动端：底部 Tab 导航，卡片单列

## 9. 无障碍

- 所有交互元素可键盘访问
- 焦点环：`box-shadow: 0 0 0 3px var(--accent-glow)`
- 支持 `prefers-reduced-motion`：禁用位移、保留透明度渐变
- 最小对比度 4.5:1
