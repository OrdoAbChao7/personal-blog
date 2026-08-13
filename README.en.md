# JJ Lab

> Technology, investment, and thinking — a personal laboratory on the web.

[中文文档](README.md)

JJ Lab is not only a blog. It is the public interface of a personal laboratory: a place to present projects, engineering problem-solving, technology observations, industry and investment research, and a long-term archive of ideas.

## Purpose

| Area | Focus |
|---|---|
| Technology exploration | AI, intelligent hardware, and optoelectronic sensing |
| Engineering practice | Edge ML, embedded development, debugging notes, and implementation learnings |
| Industry research | County-level industry, supply-chain analysis, and research frameworks |
| Long-term learning | Personal knowledge accumulation and development trajectory |

## Technology stack

| Layer | Choice |
|---|---|
| Framework | [Astro 5](https://astro.build), static-first with minimal client JavaScript |
| Content | Content Collections and MDX with Zod type validation |
| Styling | Native CSS and reusable design tokens |
| Theme | Light-first design with a persistent light/dark toggle |
| Interface localization | Chinese/English UI dictionaries with `data-i18n` replacement |
| Fonts | Inter for body copy and JetBrains Mono for technical values and metadata |
| Highlighting | Shiki with the GitHub Dark theme |
| Language | TypeScript in strict mode |

The project intentionally uses Astro rather than a heavier application framework because the site is content-driven, benefits from static output, and only needs interactive islands where they add value.

## Design principles

JJ Lab uses a restrained young-engineer laboratory style rather than a generic AI-template aesthetic. It favors a 960 px content container, divider-based lists instead of card-heavy layouts, a light-first theme, zinc-black emphasis, small corner radii, and typography-led hierarchy.

The visual system is defined in [src/styles/tokens.css](src/styles/tokens.css). Shared tokens allow a coherent update across the site from a single source of truth.

## Quick start

### Requirements

- Node.js 18.14.1 or later; Node.js 20+ is recommended.
- npm or a compatible package manager.

### Install and run

```bash
git clone https://github.com/OrdoAbChao7/personal-blog.git
cd personal-blog
npm install
npm run dev
```

The development server is available at `http://localhost:4321/`.

| Command | Purpose |
|---|---|
| `npm run dev` | Start the development server with hot reload. |
| `npm run build` | Build the production site into `dist/`. |
| `npm run preview` | Preview the production build locally. |
| `npm run astro` | Run the Astro CLI. |

## Repository structure

```text
JJ-blog/
├── astro.config.mjs           # Astro configuration
├── tsconfig.json              # Strict TypeScript configuration
├── package.json
├── content/                   # MDX source content
│   ├── projects/              # Project work
│   ├── research/              # Technology and society research
│   └── engineering/2026/      # Engineering logs grouped by year
└── src/
    ├── content/config.ts      # Zod schemas for content collections
    ├── lib/
    │   ├── content.ts         # Query, sorting, filtering, and formatting utilities
    │   └── i18n.ts            # Chinese/English UI dictionary
    ├── layouts/BaseLayout.astro
    ├── components/            # Shared navigation, footer, toggles, tags, and list items
    ├── pages/                 # Home, projects, research, and engineering routes
    └── styles/                # Design tokens and global prose styles
```

## Content authoring

All site content lives in `content/` and is authored in MDX. Zod schemas validate frontmatter at build time.

### Add a project

Create `content/projects/<slug>.mdx`:

```yaml
---
title: Project title
description: A concise description
category: hardware        # hardware | software | research
techStack:
  - ESP32-S3
  - TinyML
status: building          # idea | building | shipped | archived
github: https://github.com/...
demo: https://...
featured: true
startDate: '2026-03'
endDate: null
date: '2026-03-01'
draft: false
---

Your MDX content goes here.
```

### Add research or engineering content

Place research writing in `content/research/` and engineering notes in `content/engineering/YYYY/`. Frontmatter is validated by the relevant content collection schema. Content with `draft: true` is filtered out at build time.

## Routes

| Route | Description |
|---|---|
| `/` | Personal introduction, active projects, and recent writing |
| `/projects` | Project list |
| `/projects/[slug]` | Project detail page |
| `/research` | Research writing grouped by category |
| `/research/[slug]` | Research article with table of contents and reading progress |
| `/engineering` | Engineering log index |
| `/engineering/YYYY/[slug]` | Individual engineering log |

## Theme and interface language

The navigation provides text-based `Light` / `Dark` and `EN` / `中` toggles. Theme state is stored in `localStorage.theme`; language state is stored in `localStorage.lang`.

The current localization system translates the **site interface** — navigation, home introduction, section labels, page headings, and footer copy. It deliberately does not translate MDX article content automatically. Translating editorial content requires a separate review process to retain technical accuracy and authorial voice.

To add a new UI string, add a Chinese/English pair to [src/lib/i18n.ts](src/lib/i18n.ts), then attach the corresponding `data-i18n` key to the target element.

## Deployment

The build output is static and can be deployed to any static host.

| Platform | Configuration |
|---|---|
| Vercel | Connect the repository and select Astro. |
| Cloudflare Pages | Build command: `npm run build`; output directory: `dist`. |
| Netlify | Build command: `npm run build`; output directory: `dist`. |

Before publishing, update `site` in `astro.config.mjs` to the production domain.

## Current scope

Version 1 includes the home page, projects, research, engineering logs, a light-first visual system, a persistent dark mode, Chinese/English interface switching, and several example content items. Investment pages, a knowledge base, timeline, about page, search, RSS, and Open Graph image generation are planned for a future iteration.

## Contributing

Contributions that improve content architecture, accessibility, build reliability, or documentation are welcome. Keep visual changes consistent with the existing design constraints: no gradient-heavy or glassmorphism styling, no card-heavy layouts, and no automatic translation of editorial content without review.

## Author

**JJ** — Wuhan University of Technology, Optoelectronic Information Science and Engineering.

Focus areas include AI engineering, intelligent hardware, optoelectronic technology, and industry research.
