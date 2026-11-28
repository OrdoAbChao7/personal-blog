# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Primary audience is AI Agent and LLM engineering internship interviewers and technical hiring teams evaluating whether an undergraduate candidate ships real, verifiable production code rather than toy demos. Secondary audience includes open-source maintainers and engineering peers.

## Product Purpose

Serve as JJ Lab — a verifiable personal engineering portfolio, open-source proof dossier, and technical notebook for 陈俊杰 (JJ / OrdoAbChao7, Wuhan University of Technology '28, Optoelectronic Information Science & Engineering). Success means a technical interviewer can verify open-source maintainership, system architecture, test evidence, and engineering rigor within the first minute and jump directly to PRs, repositories, or contact.

## Positioning

Every claim on the site resolves directly to reproducible code, upstream merged PRs, regression test counts, and live local token-usage telemetry — bridging AI Agent / Hybrid RAG software systems with optical-sensing and ESP32 edge-AI hardware engineering.

## Operating Context

Static Astro 5 + MDX site deployed via GitHub Actions to GitHub Pages (`https://ordoabchao7.github.io/personal-blog/`). Visitors arrive from GitHub profile, resume, or PR links on desktop or mobile browsers. Content lives in `content/projects/`, `content/engineering/YYYY/`, `content/thinking/YYYY/`, and `public/data/usage.json` (synced daily from local ledger).

## Capabilities and Constraints

- Preserve Light + Dark theme toggle (`[data-theme='light'|'dark']` + `localStorage`).
- Preserve Chinese / English UI language toggle (`data-i18n` + `src/lib/i18n.ts`).
- Preserve `/usage` Token Usage dashboard and homepage usage summary (`public/data/usage.json`, `schemaVersion: 4`).
- Preserve Astro 5 static SSG + MDX Content Collections (`src/content/config.ts`) + native CSS tokens (`src/styles/tokens.css`, no Tailwind, React, or new frontend frameworks) and progressive Mermaid diagram rendering (`MermaidInit.astro`).
- Desktop `SidePhotos` polaroid decoration is not required to be preserved in the redesign.
- Redesign direction constraint from user: stronger authentic tech/engineering style while explicitly avoiding generic AI-generated template look.

## Brand Commitments

Name: `JJ Lab` (`Hi, I'm JJ.` / `OrdoAbChao7`). Core verifiable identity: `HKUDS / DeepTutor` Core Maintainer; 10 merged upstream PRs across 7 repositories (`HKUDS/DeepTutor`, `n8n-io/n8n`, `morluto/rea`, `StarTrail-org/PixelRAG`, `Draculabo/AntigravityManager`, `XiaoDuoYa/codex-with-chatgpt`, `MrcolorH/antigravity-skin`). Craft bar commitment (chosen canon reference): **Linear** and **Vercel** — high-precision monochrome hierarchy, crisp 1px hairline borders, restrained single-accent blue links, strong typographic discipline, and zero AI-template gloss.

## Evidence on Hand

- Real project MDX case studies in `content/projects/` (`open-source-contributions.mdx`, `county-research-ai.mdx`, `lingshan-rag.mdx`, `courselm.mdx`, `microglow-translate.mdx`, `mathmodel-ai.mdx`, `chinese-evidence-retrieval-lab.mdx`).
- Real engineering logs in `content/engineering/2026/` and thinking essay in `content/thinking/2026/learning-system.mdx`.
- Real live token telemetry JSON in `public/data/usage.json` (updated 2026-11-27, 116,501 requests, 27.57B tokens).
- Absence: Do not fabricate stars, external testimonials, employer logos, or unverified benchmark numbers.

## Product Principles

- Evidence before claims: every capability links to a real PR, test count, or reproducible artifact.
- Precision over decoration: technical clarity and scanability outrank ornamental fluff.
- Dual-domain authenticity: honor both software/AI systems engineering and optical/embedded hardware rigor.
- Fast static delivery: keep pages lightweight, accessible, and legible across light/dark and zh/en.
