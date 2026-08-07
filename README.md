# JJ Lab

> Technology, Investment & Thinking — 一个个人实验室

JJ Lab 不是博客，而是「个人实验室的对外接口」：展示做过的项目、解决工程问题的过程、对技术趋势的理解，以及对产业和投资的分析。最终形成 **个人网站 + 技术作品集 + 知识管理系统 + 投资研究库 + 思想档案** 的复合体。

## 定位

| 维度 | 说明 |
|---|---|
| 技术探索 | AI、智能硬件、光电传感 |
| 工程实践 | 端侧 ML、嵌入式调试、踩坑记录 |
| 投资研究 | 县域产业、产业链分析、研究框架 |
| 个人成长 | 长期知识积累与成长轨迹 |

## 技术栈

- **框架**: [Astro 5](https://astro.build)（静态优先，零 JS by default）
- **内容**: Content Collections + MDX（Zod 类型安全）
- **样式**: 原生 CSS + 设计 token（CSS 变量）
- **主题**: 浅色优先，支持一键切换深色（CSS 变量 + localStorage 持久化，首屏防闪烁）
- **国际化**: 中/英 UI 切换（字典文件 + `data-i18n` 属性客户端替换，内容不翻译）
- **字体**: Inter（正文，400 字重为主）+ JetBrains Mono（真实技术参数/日期/标签）
- **代码高亮**: Shiki（github-dark）
- **语言**: TypeScript（strict 模式）

> 选 Astro 而非 Next.js 的理由：内容驱动的静态站，Astro 默认零 JS、Content Collections 类型安全、按需引入交互岛，对个人实验室场景更合适。

## 设计语言

年轻工程师实验室风，反 AI 模板。视觉参考 Linear / Vercel / GitHub 的冷峻克制感，结构参考 bmpi.dev 的「自我介绍式首页 + 无卡片列表」。

- **配色 · 浅色优先**：默认浅色（bg `#FAFAFA` / elevated `#FFFFFF`），深色作为切换态保留
- **强调色 · 锌黑系**：主强调用 `#18181B`（不是色相，是黑色），hover 变纯黑。**禁止**蓝色、紫色、渐变、玻璃拟态
- **状态色 · 仅用于色点**：Building 琥珀 `#CA8A04` / Shipped 绿 `#16A34A` / Archived 灰 `#71717A` / Idea 红 `#DC2626`
- **布局 · 960px 容器**：列表用分隔线而非卡片，无背景框/边框/阴影
- **圆角 · 克制**：3-4px
- **排版 · 字重层级**：标题用 400-500 字重 + 字号差异建立层级，不用大字重；行高 1.7（relaxed）
- **Nav · static 不吸顶**：去掉 backdrop-filter，文字链接式切换按钮（Light/Dark、EN/中）

所有 token 定义在 [src/styles/tokens.css](src/styles/tokens.css)，改一处全站生效。

## 快速开始

```bash
# 安装依赖
npm install

# 启动开发服务器（http://localhost:4321/）
npm run dev

# 构建生产版本到 dist/
npm run build

# 本地预览构建产物
npm run preview
```

环境要求：Node.js ≥ 18.14.1（推荐 20+）。

## 项目结构

```
JJ-blog/
├── astro.config.mjs           # Astro 配置（MDX + Shiki）
├── tsconfig.json              # strict 模式
├── package.json
├── content/                   # 内容源（MDX）
│   ├── projects/              # 项目作品
│   ├── research/              # 技术与社会思考
│   └── engineering/2026/      # 工程日志（按年分桶）
└── src/
    ├── content/config.ts      # 3 个 collection 的 Zod schema
    ├── lib/
    │   ├── content.ts         # 数据查询封装（排序/过滤/格式化）
    │   └── i18n.ts            # 中/英 UI 文案字典
    ├── layouts/
    │   └── BaseLayout.astro   # 全局布局（Nav + Footer + 防闪烁 + i18n 引擎）
    ├── components/            # 复用组件
    │   ├── Nav.astro  Footer.astro
    │   ├── ThemeToggle.astro  LangToggle.astro   # 文字链接式切换（Light/Dark、EN/中）
    │   ├── Tag.astro  StatusDot.astro            # 去卡片化的 mono 标签 / 状态色点
    │   ├── PostCard.astro  ProjectCard.astro     # 列表项（非卡片，hover 左 2px 色条）
    │   └── AreaCard.astro  SectionHeader.astro   # 已弃用（首页改版后不再引用）
    ├── pages/
    │   ├── index.astro        # 首页（3 模块：自我介绍 / 正在构建 / 近期写作）
    │   ├── projects/{index,[...slug]}.astro
    │   ├── research/{index,[...slug]}.astro
    │   └── engineering/{index,[...slug]}.astro
    └── styles/
        ├── tokens.css         # 设计 token（浅色优先 / 锌黑系 / 960px / 状态色点）
        └── global.css         # reset + prose 排版（去卡片化代码块）
```

## 内容管理

所有内容位于 `content/`，按类型分目录，使用 MDX。每篇 frontmatter 由 Zod schema 校验，构建期报错。

### 新建一篇项目

在 `content/projects/` 新建 `xxx.mdx`：

```yaml
---
title: 项目名
description: 一句话描述
category: hardware        # hardware | software | research
techStack:
  - ESP32-S3
  - TinyML
status: building          # idea | building | shipped | archived
github: https://github.com/...
demo: https://...
featured: true
startDate: '2026-03'
endDate: null             # 进行中填 null
date: '2026-03-01'        # 排序用
draft: false
---

正文（支持 MDX 组件）...
```

### 新建一篇研究文章

`content/research/xxx.mdx`：

```yaml
---
title: 文章标题
description: 摘要
category: ai-trend        # ai-trend | society | startup | tech-analysis
date: '2026-08-01'
tags: [ai-agent, vertical]
featured: false
draft: false
---
```

### 新建一篇工程日志

`content/engineering/YYYY/xxx.mdx`（按年分桶）：

```yaml
---
title: 日志标题
description: 摘要
hardware: ESP32-S3 + AS7263
software: PlatformIO + Edge Impulse
difficulty: 4            # 1-5
date: '2026-08-05'
tags: [embedded, nir]
draft: false
---
```

> `draft: true` 的内容不会出现在任何页面（构建期过滤）。

## 页面与路由

| 路由 | 说明 |
|---|---|
| `/` | 首页：自我介绍 / 正在构建（项目列表）/ 近期写作（研究 + 工程列表） |
| `/projects` | 项目列表（无卡片，状态色点 · 名称 · 技术栈 · 日期） |
| `/projects/[slug]` | 项目详情（含 techStack、status、GitHub 链接） |
| `/research` | 研究文章（按 category 分组，无卡片列表） |
| `/research/[slug]` | 文章详情（含目录 TOC + 阅读进度条） |
| `/engineering` | 工程日志（含难度条、HW/SW 环境标签） |
| `/engineering/YYYY/[slug]` | 日志详情 |

首页与列表页均为 960px 宽无卡片列表，hover 时左侧出现 2px 锌黑色条。

## 设计系统

- **主题**: 浅色优先（默认浅色：bg `#FAFAFA` / elevated `#FFFFFF`；深色：`#0A0A0A` / `#111111`）
- **强调色**: 锌黑 `#18181B`（hover → `#000000`），非色相
- **状态色**: 仅用于色点，不用于文字。Building 琥珀 `#CA8A04` / Shipped 绿 `#16A34A` / Archived 灰 `#71717A` / Idea 红 `#DC2626`
- **间距**: 8 倍数（4 / 8 / 12 / 16 / 24 / 32 / 48 / 64）
- **圆角**: 3-4px（`--radius-sm` / `--radius-md`）
- **容器**: `--container-max: 960px` / `--container-narrow: 680px`
- **字体**: Inter（正文，400 字重为主）+ JetBrains Mono（元信息/代码/真实技术参数）
- **质感参考**: Linear / Vercel / GitHub（冷峻克制，反 AI 模板）

**禁止**：蓝色、紫色、渐变、玻璃拟态、卡片背景框/阴影、大字重标题、装饰性 mono。

### 主题与语言切换

- **主题切换**：导航栏右侧 `Light`/`Dark` 文字链接（无按钮边框）。状态持久化在 `localStorage.theme`（`light` | `dark`，默认 `light`）。`BaseLayout` 内联一段 `is:inline` 脚本，在首次绘制前读取 `localStorage` 并设置 `document.documentElement.dataset.theme`，避免刷新闪烁。
- **语言切换**：导航栏右侧 `EN`/`中` 文字链接，仅切换 **UI 外壳文案**（导航、首页自我介绍、区块标题、页头/页脚），MDX 内容保持中文不翻译。状态持久化在 `localStorage.lang`（`zh` | `en`）。
- **i18n 机制**：所有需翻译的元素带 `data-i18n="key"` 属性，字典在 [src/lib/i18n.ts](src/lib/i18n.ts)。`BaseLayout` 末尾的 `<script>` 在首屏加载时按 `localStorage.lang` 替换文案，切换时调用 `window.__applyLang(next)` 全量替换并派发 `lang:applied` 事件。新增 UI 文案时，在字典里加一对 key，再在元素上挂 `data-i18n` 即可。

## 开发命令

| 命令 | 作用 |
|---|---|
| `npm run dev` | 启动开发服务器（热重载） |
| `npm run build` | 构建到 `dist/` |
| `npm run preview` | 预览构建产物 |
| `npm run astro` | Astro CLI 入口 |

## 部署

构建产物为纯静态文件，可部署到任意静态托管：

- **Vercel**: 连接仓库，框架选 Astro，自动构建
- **Cloudflare Pages**: 构建命令 `npm run build`，输出目录 `dist`
- **Netlify**: 同上

部署前在 `astro.config.mjs` 把 `site` 改为正式域名。

## 当前进度（V1）

**已实现**: Home / Projects / Research / Engineering（4 板块 + 6 篇示例内容）+ 浅色优先主题 + 深浅切换 + 中英 UI 切换 + 自我介绍式首页 + 无卡片列表

**暂缓到 V2**: Investment / Knowledge / Timeline / About / 全站搜索 / RSS / OG 图

## 作者

**JJ** · 武汉理工大学 · 光电信息科学与工程

研究方向：AI 工程 · 智能硬件 · 光电技术 · 产业研究
