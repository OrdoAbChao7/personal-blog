# 博客图片资产管理

本指南定义个人博客的图片资产目录、命名、MDX 使用方式和项目图库规范。目标是在不引入额外依赖的前提下，让项目展示、工程日志和思考文章拥有可维护、可检索并适合 GitHub Pages 部署的图片工作流。

## 目录结构

所有图片统一放在 `public/images/` 下。该目录中的资源会作为静态文件输出；页面和 MDX 中统一传入以 `/images/` 开头的逻辑路径，由组件和项目页自动处理博客的 GitHub Pages 子路径。

```text
public/images/
├── projects/                         # 项目展示图片
│   ├── microglow/                    # 与项目 slug 对应
│   │   ├── cover.jpg                 # 项目封面
│   │   ├── hardware/                 # 硬件照片
│   │   ├── architecture/             # 系统架构图
│   │   └── results/                  # 实验结果、动图或演示截图
│   └── county-research-ai/
├── articles/                         # 思考和工程文章图片
│   └── 2026/
│       └── learning-system/          # 与文章目录及 slug 对应
└── common/                           # Logo、默认封面等全局资源
```

| 原则 | 说明 |
|---|---|
| 按内容类型隔离 | `projects` 与 `articles` 分开，避免项目资源和文章配图混杂。 |
| 按 slug 聚类 | 每篇文章或每个项目拥有独立目录，删除内容时可同步清理其图片。 |
| 按用途细分 | 对硬件与 AI 项目使用 `hardware`、`architecture`、`results` 等子目录，方便持续补充资源。 |
| 公共资源最小化 | 仅将确实跨页面复用的资源放入 `common`，避免形成难以追溯来源的“杂项”目录。 |

## 文件命名

图片文件名必须使用**小写英文、数字和连字符**。不要使用空格、中文、`IMG_001` 或 `Screenshot` 等无意义名称。

| 场景 | 推荐文件名 |
|---|---|
| 硬件原型 | `microglow-hardware-prototype-v1.jpg` |
| 系统架构 | `microglow-system-architecture.png` |
| 模型实验结果 | `microglow-training-result.png` |
| 项目封面 | `cover.jpg` |
| 第一次测试截图 | `signal-capture-test-v1.png` |

建议使用 `[项目或模块]-[内容]-[版本或状态].[扩展名]` 的格式。照片优先使用 `.jpg` 或 `.webp`，架构图和文字密集截图优先使用 `.png`；上传前应压缩图片，避免将未处理的大尺寸原图直接提交到 Git 仓库。

## 在 MDX 中插入图片

### 推荐方式：`BlogImage` 组件

在 MDX 顶部使用稳定的 `@` 别名导入组件；该方式不受文章目录深度影响，且会自动处理响应式尺寸、懒加载、图注和 GitHub Pages 子路径。

```mdx
import BlogImage from '@/components/BlogImage.astro';

<BlogImage
  src="/images/projects/microglow/hardware/microglow-hardware-prototype-v1.jpg"
  alt="MicroGlow 的 ESP32-S3 与 VCNL4040 硬件原型"
  caption="图 1：MicroGlow 的第一版近红外传感硬件原型。"
/>
```

| 参数 | 是否必填 | 说明 |
|---|---:|---|
| `src` | 是 | 图片的逻辑路径，例如 `/images/projects/...`；也支持完整的 HTTPS 图片 URL。 |
| `alt` | 是 | 描述图片内容的替代文本，不能留空。 |
| `caption` | 否 | 显示在图片下方的图注。 |

`BlogImage` 组件会使用 `loading="lazy"`，并保持 `max-width: 100%` 和等比缩放；因此可以安全用于窄屏设备。对于简单且不需要图注的图片，也可以使用标准 Markdown 语法，但请优先使用组件以获得一致的部署路径和样式。

```mdx
![MicroGlow 硬件原型](/images/projects/microglow/hardware/microglow-hardware-prototype-v1.jpg)
```

## 项目图库

项目的 frontmatter 支持可选的 `gallery` 字段。项目详情页会在正文之后自动渲染响应式网格图库；用户可点击单张图片，在新标签页查看原图。

```mdx
---
title: MicroGlow Translate
description: 基于近红外非视觉感知与 TinyML 的可穿戴唇语识别翻译系统
category: hardware-ai
gallery:
  - /images/projects/microglow/hardware/microglow-hardware-prototype-v1.jpg
  - /images/projects/microglow/architecture/microglow-system-architecture.png
  - /images/projects/microglow/results/microglow-training-result.png
---
```

图库字段只需要填写图片路径；页面会自动完成懒加载、移动端网格适配以及 GitHub Pages 子路径处理。当前图库适合展示数量有限、与项目正文关联紧密的代表性图片。若图片需要逐张说明，应在正文中改用 `BlogImage` 组件并添加图注。

## 上传与发布工作流

1. 根据内容类型和 slug 创建目标目录，例如 `public/images/projects/microglow/hardware/`。
2. 在本地对图片压缩并使用规范文件名，再复制到目标目录。
3. 在 MDX 中使用 `BlogImage` 或将路径加入 `gallery`。
4. 本地运行 `npm run build`，检查图片路径和 MDX 编译是否正确。
5. 将图片文件、MDX 文件和相关代码在同一次提交中推送，以便 Git 历史能反映资源与内容的对应关系。

> 不要在 `src/` 或 `content/` 中随意堆放原始图片。属于文章或项目的图片应放在对应的 `public/images/` 子目录中；只有需要由 Astro 构建管道直接导入、处理的特殊资源，才应单独讨论是否迁移至 `src/assets/`。

## 尺寸与性能建议

| 图片类型 | 建议宽度 | 适用格式 | 说明 |
|---|---:|---|---|
| 项目封面 | 1600–2400 px | WebP/JPG | 保留足够清晰度，并在上传前压缩。 |
| 架构图/图表 | 1200–2000 px | PNG/SVG | 文字密集时避免过度压缩。 |
| 正文配图 | 1200–1600 px | WebP/JPG/PNG | 通常不需要上传高于 2K 的原图。 |
| 动态演示 | 尽量小于 10 MB | GIF/MP4 | 优先短时长、低帧率 GIF；较大的演示建议使用外部视频托管。 |

随着图库扩展，建议定期清理无引用图片，并在需要管理大体积素材时将原始文件迁移到专用对象存储或媒体服务；仓库中保留用于网页展示的优化版本。
