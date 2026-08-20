<div align="center">
  <h1>JJ Lab</h1>

  [**English**](./README.md) | **中文**

  <p><b>一个围绕技术、工程实践与深度思考构建的个人实验室。</b></p>
</div>

---

## 项目概览

JJ Lab 是一个内容驱动的个人网站，结合了项目作品集、工程实践笔记和长文写作档案，记录 AI 工程、智能硬件、光电传感与个人学习系统等方向的探索。

网站由三个内容板块构成：

| 板块 | 作用 |
|---|---|
| **项目** | 展示产品、硬件与研究项目，并补充技术背景和项目图库。 |
| **工程** | 记录调试过程、实现笔记与可复用的技术经验。 |
| **思考** | 收录关于学习系统、技术与社会的长文写作。 |

## 功能特性

- 使用 Astro 构建静态站点，采用 MDX 内容集合与 Zod schema 校验。
- 浅色优先的视觉系统，支持深色模式和中英文 UI 标签切换。
- 兼顾桌面与移动设备的响应式阅读布局。
- 严格依据 Markdown 标题顺序和层级自动生成文章目录。
- 所有文章详情页均具备阅读进度条与阅读元信息。
- 支持项目图库及可复用的响应式 MDX 图片组件。
- 通过 GitHub Actions 自动部署至 GitHub Pages。

## 技术栈

| 层级 | 技术 |
|---|---|
| 框架 | [Astro 5](https://astro.build) |
| 内容 | Content Collections、MDX、Zod |
| 样式 | 原生 CSS 与设计 token |
| 语言 | 严格模式 TypeScript |
| 代码高亮 | Shiki |
| 部署 | GitHub Pages 与 GitHub Actions |

## 快速开始

```bash
# 安装依赖
npm install

# 启动本地开发服务器
npm run dev

# 构建生产版本
npm run build

# 本地预览构建结果
npm run preview
```

需要 Node.js 18.14.1 或更高版本；部署工作流使用 Node.js 22。

## 项目结构

```text
personal-blog/
├── content/
│   ├── projects/                 # 项目作品
│   ├── engineering/YYYY/         # 按年份归档的工程文章
│   └── thinking/YYYY/            # 按年份归档的思考文章
├── public/images/                # 静态图片资产库
│   ├── projects/
│   ├── articles/
│   └── common/
├── src/
│   ├── components/               # 复用 Astro 组件
│   ├── content/config.ts         # 内容集合 schema
│   ├── layouts/                  # 全局布局
│   ├── lib/                      # 内容、国际化、URL 和阅读工具
│   ├── pages/                    # Astro 路由
│   └── styles/                   # 设计 token 与全局样式
├── docs/image-management.md      # 图片资产管理说明
└── .github/workflows/deploy.yml  # GitHub Pages 部署工作流
```

## 内容写作

网站内容均使用 MDX 编写，并存放在 `content/` 中。每个内容条目的 frontmatter 都会在构建阶段接受校验。

### 新建一篇思考文章

创建 `content/thinking/YYYY/your-article.mdx`：

```mdx
---
title: 文章标题
description: 用一句话概括文章内容。
category: society
date: '2026-08-20'
tags:
  - learning
featured: false
draft: false
---

## 第一节

使用标准 Markdown 或 MDX 写作正文。
```

文章详情页会直接读取 Markdown 正文标题生成目录。请用 `##` 表示章节、用 `###` 表示子章节；不要在正文中手动编写目录。

### 添加项目图库

将图片放在 `public/images/projects/<project-slug>/`，并在项目 frontmatter 中填写图片路径：

```yaml
gallery:
  - /images/projects/example/cover.jpg
  - /images/projects/example/architecture.png
```

在 MDX 正文中插入图片时，推荐使用复用组件：

```mdx
import BlogImage from '@/components/BlogImage.astro';

<BlogImage
  src="/images/projects/example/cover.jpg"
  alt="简洁且准确的图片描述"
  caption="可选的图片图注。"
/>
```

图片目录、命名与优化规范详见 [`docs/image-management.md`](./docs/image-management.md)。

## 开发命令

| 命令 | 作用 |
|---|---|
| `npm run dev` | 启动热重载开发服务器。 |
| `npm run build` | 构建静态站点至 `dist/`。 |
| `npm run preview` | 本地预览生产构建结果。 |
| `npm run astro` | 运行 Astro CLI。 |

## 部署

向默认分支推送代码后，会触发 `.github/workflows/deploy.yml`。该工作流依次安装依赖、构建 Astro 站点、上传 `dist/` 并部署到 GitHub Pages。

## 许可证

本仓库用于个人网站与作品集展示。复用其中内容前，请先检查仓库文件及包含资产的许可情况。
