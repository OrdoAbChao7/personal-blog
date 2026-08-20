<div align="center">
  <h1>JJ Lab</h1>

  **English** | [**中文**](./README_zh-CN.md)

  <p><b>A personal lab for technology, engineering practice, and reflective writing.</b></p>
</div>

---

## Overview

JJ Lab is a content-driven personal website that combines a project portfolio, engineering notes, and a long-form writing archive. It documents work in AI engineering, intelligent hardware, optical sensing, and personal learning.

The site is organized around three content areas:

| Area | Purpose |
|---|---|
| **Projects** | Product, hardware, and research projects with technical context and galleries. |
| **Engineering** | Debugging records, implementation notes, and reproducible technical lessons. |
| **Thinking** | Long-form writing about learning systems, technology, and society. |

## Features

- Astro static site with MDX-based content collections and Zod schema validation.
- Light-first visual system with optional dark mode and Chinese/English interface labels.
- Responsive layouts for desktop and mobile readers.
- Automatic table of contents generated directly from Markdown heading order and levels.
- Reading progress bar and reading metadata for article pages.
- Project galleries and reusable responsive MDX image component.
- GitHub Pages deployment through GitHub Actions.

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | [Astro 5](https://astro.build) |
| Content | Content Collections, MDX, Zod |
| Styling | Native CSS and design tokens |
| Language | TypeScript with strict configuration |
| Code highlighting | Shiki |
| Deployment | GitHub Pages and GitHub Actions |

## Quick Start

```bash
# Install dependencies
npm install

# Start the local development server
npm run dev

# Create the production build
npm run build

# Preview the production output
npm run preview
```

Use Node.js 18.14.1 or later; Node.js 22 is used in the deployment workflow.

## Project Structure

```text
personal-blog/
├── content/
│   ├── projects/                 # Project case studies
│   ├── engineering/YYYY/         # Engineering notes, grouped by year
│   └── thinking/YYYY/            # Long-form writing, grouped by year
├── public/images/                # Static blog image library
│   ├── projects/
│   ├── articles/
│   └── common/
├── src/
│   ├── components/               # Shared Astro components
│   ├── content/config.ts         # Collection schemas
│   ├── layouts/                  # Global layouts
│   ├── lib/                      # Content, i18n, URL, and reading helpers
│   ├── pages/                    # Astro routes
│   └── styles/                   # Tokens and global styles
├── docs/image-management.md      # Image asset management guide
└── .github/workflows/deploy.yml  # GitHub Pages deployment
```

## Writing Content

All site content is written in MDX and stored in `content/`. Every entry has frontmatter that is validated during the build.

### Add a Thinking Article

Create `content/thinking/YYYY/your-article.mdx`:

```mdx
---
title: Your article title
description: A concise summary of the article.
category: society
date: '2026-08-20'
tags:
  - learning
featured: false
draft: false
---

## First section

Write the article in standard Markdown or MDX.
```

The article detail page automatically creates its table of contents from the Markdown headings. Use `##` for sections and `###` for subsections; do not write a manual table of contents in the body.

### Add a Project Gallery

Place images under `public/images/projects/<project-slug>/` and add paths in the project frontmatter:

```yaml
gallery:
  - /images/projects/example/cover.jpg
  - /images/projects/example/architecture.png
```

For inline MDX images, use the reusable component:

```mdx
import BlogImage from '@/components/BlogImage.astro';

<BlogImage
  src="/images/projects/example/cover.jpg"
  alt="A concise description of the image"
  caption="Optional image caption."
/>
```

See [`docs/image-management.md`](./docs/image-management.md) for directory, naming, and optimization conventions.

## Development Commands

| Command | Purpose |
|---|---|
| `npm run dev` | Start the development server with hot reload. |
| `npm run build` | Build the static site into `dist/`. |
| `npm run preview` | Preview the production build locally. |
| `npm run astro` | Run the Astro CLI. |

## Deployment

Pushes to the default branch trigger `.github/workflows/deploy.yml`. The workflow installs dependencies, builds the Astro site, uploads `dist/`, and deploys it to GitHub Pages.

## License

This repository is intended as a personal website and portfolio. Review the repository files and included asset licenses before reusing its content.
