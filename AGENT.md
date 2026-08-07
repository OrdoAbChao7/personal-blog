# AGENT.md — AI 协作指南

> 本文档供 AI agent / 助手在修改本项目时阅读，提供关键上下文、技术约束与避坑指南。
> 人类可读版本见 [README.md](./README.md)。

## 项目本质

JJ Lab 是 **Astro 5 驱动的内容型个人网站**（非博客模板、非 Web App）。核心是 Content Collections + MDX 的静态内容站，静态优先（SSG），按需引入交互岛。理解这一点是所有修改的前提。

- 不是 SaaS，没有数据库、鉴权、API routes
- 不是 SPA，没有客户端路由
- 80% 是静态内容展示，交互仅限少量客户端 `<script>`

## 关键技术约束（必须遵守）

### 1. 框架锁定：Astro 5

- **不要迁移 Next.js**。已评估过，Astro 对内容驱动场景更合适（零 JS 默认、Content Collections 类型安全、按需岛）
- 版本：Astro 5.18.x，使用 **Content Layer API**（新 loader 体系）

### 2. Content Layer API 的三个坑（高频踩雷）

| 错误写法 | 正确写法 | 说明 |
|---|---|---|
| `entry.render()` | `render(entry)` | Astro 5 废弃了 entry 上的 render 方法，改用从 `'astro:content'` 导入的 `render` 函数 |
| `[...slug].astro` 不写 `getStaticPaths` | 必须导出 `getStaticPaths()` | SSG 模式下动态路由必须声明静态路径，否则报 `GetStaticPathsRequired` |
| 用文件名当 id | `entry.id` 是相对 base 的路径 | glob loader 的 id 含子目录，如 `content/engineering/2026/x.mdx` 的 id 是 `2026/x` |

### 3. 内容 Schema 不可破坏

- 所有 schema 在 [src/content/config.ts](src/content/config.ts)，用 Zod
- 修改 schema 后，**所有现有 MDX 的 frontmatter 必须兼容**，否则构建失败
- 新增字段必须 `.default()` 或 `.optional()`，保证向后兼容

### 4. 样式栈锁定

- **原生 CSS + CSS 变量 token**，定义在 [src/styles/tokens.css](src/styles/tokens.css)
- **不要引入** Tailwind / CSS-in-JS / CSS 框架
- 组件样式用 `<style>` 局部作用域（Astro 默认 scoped）
- 改样式优先改 token，而非逐处硬编码

#### 设计语言约束（V1 改版后必须遵守）

- **浅色优先**：默认 `data-theme='light'`，防闪烁脚本默认值也是 `light`。深色作为切换态保留，不是默认
- **锌黑系强调**：主强调色 `--color-accent: #18181B`（黑色，不是色相），hover → `#000000`
- **状态色仅用于色点**：`--color-building`/`--color-shipped`/`--color-archived`/`--color-idea` 只用于 `.dot-*`，不用于文字或大色块
- **禁止**：蓝色、紫色、渐变、玻璃拟态（backdrop-filter）、卡片背景框/阴影、大字重标题（>500）、装饰性 mono
- **去卡片化**：列表用分隔线（`border-bottom`），不用 `background`/`border`/`border-radius`/`box-shadow` 包裹项。hover 反馈用左侧 2px 色条（`border-left: 2px solid var(--color-accent)`），不变色
- **960px 容器**：`--container-max: 960px`，列表页与首页共用
- **字重层级**：标题 400-500 字重 + 字号差异，不用 600/700；正文 400；行高 1.7
- **圆角 3-4px**：`--radius-sm: 3px` / `--radius-md: 4px`，不要用 `--radius-lg` 或 `--radius-full`（已废弃）
- **Nav static**：不吸顶、无 backdrop-filter、无 `position: sticky`
- **切换按钮文字链接式**：ThemeToggle 显示 `Light`/`Dark` 文字，LangToggle 显示 `EN`/`中` 文字，均无按钮边框/背景

### 5. 组件栈锁定

- 用原生 `.astro` 组件，**不要**引入 React/Vue/Svelte（V1 无交互岛需求）
- 客户端 JS 用 `<script>` 标签（Astro 会打包），无需框架
- 字体走 Google Fonts CDN，不用 @fontsource

## 文件组织规则

| 目录 | 职责 | 修改原则 |
|---|---|---|
| `content/` | 内容源（MDX） | 一篇一文件，按 collection 分目录 |
| `src/content/config.ts` | schema 定义 | 改这里要同步检查所有 MDX |
| `src/lib/content.ts` | 数据查询封装 | 页面不要直接调 `getCollection`，用这里的封装函数 |
| `src/layouts/` | 布局 | 全站只有一个 `BaseLayout` |
| `src/components/` | 复用组件 | 一组件一文件，scoped 样式 |
| `src/pages/` | 路由 | 文件即路由，动态路由用 `[...slug]` |
| `src/styles/` | 全局样式 | `tokens.css`（变量）+ `global.css`（reset+prose） |

## 数据流

```
content/**/*.mdx
      │
      ▼  glob loader 加载
Astro Content Collections
      │
      ▼  Zod schema 校验（构建期）
src/lib/content.ts 封装（排序/过滤 draft/格式化）
      │
      ▼
.astro 页面 frontmatter 调用 → 模板渲染
      │
      ▼
静态 HTML 输出到 dist/
```

**关键**：`src/lib/content.ts` 的封装函数（`getProjects` / `getResearch` / `getEngineering`）已处理 `draft` 过滤和日期排序，页面直接用，不要再手写过滤逻辑。

## 三个 Collection 的 Schema 速查

### projects
`title` `description` `category`(hardware|software|research) `techStack`[] `status`(idea|building|shipped|archived) `github`? `demo`? `cover`? `featured`(bool) `startDate`? `endDate`? `date` `draft`(bool)

### research
`title` `description`? `category`(ai-trend|society|startup|tech-analysis) `date` `tags`[] `cover`? `featured`(bool) `draft`(bool)

### engineering
`title` `description`? `hardware`? `software`? `difficulty`(1-5) `date` `tags`[] `draft`(bool)

## 页面修改检查清单

新增或修改页面时逐项确认：

- [ ] 继承 `BaseLayout`，传入 `active` 属性（Nav 高亮当前板块）
- [ ] 列表页用 `src/lib/content.ts` 的封装函数，不直接调 `getCollection`
- [ ] 详情页（`[...slug]`）必须导出 `getStaticPaths()`
- [ ] 详情页渲染 MDX 用 `render(entry)`，不是 `entry.render()`
- [ ] 新增 collection 字段后跑 `npm run build` 验证所有 MDX 兼容
- [ ] 样式改动优先改 `tokens.css` 变量，不硬编码
- [ ] 不引入新依赖（框架/CSS 库/字体包），除非用户明确要求

## V1 / V2 边界（不要越界）

**V1 已实现**：Home / Projects / Research / Engineering + 浅色优先主题 + 深浅切换 + 中英 UI 切换 + 自我介绍式首页（3 模块）+ 无卡片列表

**V2 暂缓**（不要主动实现，除非用户明确要求）：
- Investment / Knowledge / Timeline / About 四个板块
- 全站搜索（Pagefind）
- RSS（@astrojs/rss）
- OG 图自动生成
- 知识图谱可视化
- 部署配置

## 已知问题

| 问题 | 状态 | 处理时机 |
|---|---|---|
| 4 个 npm 漏洞（2 low 2 high） | 不阻塞开发 | V2 统一 `npm audit fix` |
| `astro.config.mjs` 的 `site` 是占位 `https://jjlab.dev` | 部署前替换 | 部署时 |
| 首页有调试用 `console.log`（数据加载日志） | 开发期保留 | 上线前移除或加 `import.meta.env.DEV` 守卫 |

## 调试日志约定

首页 [src/pages/index.astro](src/pages/index.astro) 含两层调试日志：

1. **服务端**（frontmatter `console.log`）→ 输出到 dev 终端，验证数据加载顺序（building → research → engineering，4 阶段）
2. **客户端**（`<script>` 中 `console.log`）→ 输出浏览器 console，验证 DOM 渲染（3 模块：Intro / Currently / Recent writing）

上线前应用 `import.meta.env.DEV` 守卫包裹，或直接移除：
```ts
if (import.meta.env.DEV) {
  console.log(...);
}
```

## 常用命令

```bash
npm run dev        # 开发服务器 http://localhost:4321/
npm run build      # 构建到 dist/（同时校验所有 MDX schema）
npm run preview    # 预览构建产物
```

`npm run build` 是最有效的验证手段——任何 schema 不匹配、类型错误、路由问题都会在构建期暴露。

## 设计决策记录

| 决策 | 理由 |
|---|---|
| Astro 而非 Next.js | 内容驱动静态站，Astro 零 JS + 类型安全 collection 更合适 |
| 浅色优先（V1 改版） | 反 AI 模板的深色科技风，年轻工程师实验室气质；Linear/Vercel/GitHub 的冷峻克制感 |
| 锌黑系强调 `#18181B` | 不是色相是黑色，比蓝色更克制；hover 变纯黑建立隐式层级 |
| 去卡片化列表 | 反 AI 模板的核心——不用背景框/边框/阴影包裹项，用分隔线建立节奏，hover 用左 2px 色条 |
| 960px 容器 | 收窄阅读宽度，bmpi.dev 式的自我介绍式首页结构 |
| 状态色仅用于色点 | 颜色只承载语义（building/shipped/archived/idea），不承载美学 |
| engineering 按年分桶 | 避免单目录文件爆炸 |
| timeline 用 YAML 而非 MDX（V2） | 事件是结构化短数据，无需富文本 |
| 原生 CSS 而非 Tailwind | 设计 token 已够用，避免框架依赖与类名膨胀 |

## 修改本项目的正确姿势

1. 先读 [README.md](./README.md) 理解项目定位
2. 改内容 → 直接编辑 `content/*.mdx`，遵守对应 schema
3. 改样式 → 改 `src/styles/tokens.css` 的变量
4. 改组件 → 改 `src/components/*.astro`，保持 scoped 样式
5. 加页面 → 在 `src/pages/` 新建，继承 `BaseLayout`
6. 改完跑 `npm run build` 验证
