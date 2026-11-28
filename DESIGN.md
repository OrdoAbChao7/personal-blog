---
name: JJ Lab
description: Precision monochrome engineering portfolio, open-source proof dossier, and technical notebook.
colors:
  precision-cobalt: "#0070f3"
  precision-cobalt-hover: "#005cc5"
  precision-cobalt-dark: "#3291ff"
  canvas-white: "#ffffff"
  surface-subtle: "#fafafa"
  surface-hover: "#f4f4f5"
  hairline-border: "#e4e4e7"
  hairline-strong: "#d4d4d8"
  ink-primary: "#0a0a0a"
  ink-secondary: "#52525b"
  ink-tertiary: "#71717a"
  obsidian-bg: "#0a0a0a"
  obsidian-elevated: "#111111"
  status-shipped: "#16a34a"
  status-building: "#ca8a04"
  status-archived: "#71717a"
  status-idea: "#dc2626"
typography:
  display:
    fontFamily: "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif"
    fontSize: "clamp(2.25rem, 4vw, 3rem)"
    fontWeight: 600
    lineHeight: 1.08
    letterSpacing: "-0.04em"
  headline:
    fontFamily: "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif"
    fontSize: "1.5rem"
    fontWeight: 600
    lineHeight: 1.15
    letterSpacing: "-0.025em"
  title:
    fontFamily: "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif"
    fontSize: "1.125rem"
    fontWeight: 600
    lineHeight: 1.15
    letterSpacing: "-0.02em"
  body:
    fontFamily: "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.7
    letterSpacing: "0em"
  label:
    fontFamily: "JetBrains Mono, Berkeley Mono, Fira Code, Consolas, monospace"
    fontSize: "0.75rem"
    fontWeight: 500
    lineHeight: 1.45
    letterSpacing: "0.04em"
rounded:
  xs: "4px"
  sm: "6px"
  md: "8px"
  lg: "10px"
  full: "999px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "24px"
  xl: "32px"
  2xl: "48px"
  3xl: "64px"
components:
  button-primary:
    backgroundColor: "{colors.ink-primary}"
    textColor: "{colors.canvas-white}"
    rounded: "{rounded.sm}"
    padding: "8px 15px"
  button-secondary:
    backgroundColor: "{colors.canvas-white}"
    textColor: "{colors.ink-primary}"
    rounded: "{rounded.sm}"
    padding: "8px 15px"
  project-card:
    backgroundColor: "{colors.canvas-white}"
    textColor: "{colors.ink-primary}"
    rounded: "{rounded.md}"
    padding: "24px"
  tag-chip:
    backgroundColor: "{colors.surface-subtle}"
    textColor: "{colors.ink-tertiary}"
    rounded: "{rounded.xs}"
    padding: "2px 7px"
---

# Design System: JJ Lab

## Overview

**Creative North Star: "Precision Engineering Dossier"**

JJ Lab is a technical portfolio and engineering notebook calibrated to the Linear and Vercel craft bar: razor-sharp monochrome contrast, `1px` hairline structural grids, tabular monospace telemetry, and zero decorative AI-template gloss. Every surface prioritizes immediate scannability for technical interviewers and engineering peers—letting merged PRs, regression test counts, and live token ledgers speak directly from the first viewport.

The system defaults to crisp daylight readability (`canvas-white`) with a first-class dark theme (`obsidian-bg`) and Chinese/English UI switching. Depth comes exclusively from hairline boundaries and restrained surface steps rather than drop shadows or frosted glass.

**Key Characteristics:**
- High-contrast monochrome foregrounds paired with `1px` hairline grid dividers.
- Single precision blue accent reserved strictly for interactive links, keyboard focus rings, and active verification tokens.
- Machined small radii (`4px`–`8px`) with tabular numerals (`tabular-nums`) on all metrics, dates, and PR identifiers.
- Zero gradient text, zero blur/glassmorphism, and zero ungrounded decorative badges.

## Colors

The palette is built on stark monochrome neutrals anchored by one calibrated cobalt blue interaction accent and four semantic status-dot hues.

### Primary
- **Precision Cobalt** (`colors.precision-cobalt`): Interactive links, PR hash chips, active focus outlines, and hover-state directional arrows.
- **Precision Cobalt Hover** (`colors.precision-cobalt-hover`): Hover state for text links and inline action triggers in light mode.
- **Precision Cobalt Dark** (`colors.precision-cobalt-dark`): High-legibility cobalt accent in dark mode (`[data-theme='dark']`).

### Neutral
- **Canvas White** (`colors.canvas-white`): Primary page background and elevated card surface in light mode.
- **Surface Subtle** (`colors.surface-subtle`): Recessed table headers, proof highlight strips, tag chip grounds, and row hover surfaces.
- **Surface Hover** (`colors.surface-hover`): Active navigation link fill and secondary button hover fill.
- **Hairline Border** (`colors.hairline-border`): Standard `1px` grid seams, vertical desktop container rails, and card/table outlines.
- **Hairline Strong** (`colors.hairline-strong`): Hover borders on interactive cards and separator slashes.
- **Ink Primary** (`colors.ink-primary`): Headings, primary metric figures, and high-contrast primary CTA background in light mode.
- **Ink Secondary** (`colors.ink-secondary`): Body prose, project descriptions, and contribution summaries.
- **Ink Tertiary** (`colors.ink-tertiary`): Dates, metadata keys, stack labels, and footer counts.
- **Obsidian Bg / Elevated** (`colors.obsidian-bg`, `colors.obsidian-elevated`): Dark-mode canvas and surface layers.

### Named Rules
**The Single-Accent Discipline Rule.** `precision-cobalt` never fills large decorative banners or primary CTA buttons; primary buttons stay solid monochrome (`ink-primary` in light mode, `#ededed` in dark mode) so cobalt signals purely clickable proof, links, and focus.

**The Semantic Dot Rule.** Status hues (`status-shipped`, `status-building`, `status-archived`, `status-idea`) appear strictly inside 6px circular `StatusDot` indicators—never as text colors or badge fills.

## Typography

**Display Font:** `Inter` (with system sans + CJK fallbacks)
**Body Font:** `Inter` (with `PingFang SC` / `Hiragino Sans GB` / `Microsoft YaHei`)
**Label/Mono Font:** `JetBrains Mono` (with `Berkeley Mono`, `Fira Code`, `Consolas`)

**Character:** Tight-tracked geometric sans-serif headings (`-0.02em` to `-0.04em`) establish authority without decorative serifs, paired with crisp `JetBrains Mono` tabular figures for every PR number, test count, token total, and stack identifier.

### Hierarchy
- **Display** (`600`, `clamp(2.25rem, 4vw, 3rem)`, `1.08` line-height, `-0.04em` tracking): Homepage `Hi, I'm JJ.` hero statement only.
- **Headline** (`600`, `1.5rem`, `1.15` line-height, `-0.025em` tracking): Major page titles and prose `h2` headings.
- **Title** (`600`, `1.125rem`, `1.15` line-height, `-0.02em` tracking): Section titles (`开源与维护`, `代表项目`) and project card titles.
- **Body** (`400`, `1rem`, `1.7` line-height): Reading measure capped around `54ch`–`700px` for comfortable bilingual scanning.
- **Label** (`500`, `0.75rem`, `0.04em` tracking, monospace): Table column headers, status strips, highlight bars, and tech tags.

### Named Rules
**The Tabular Telemetry Rule.** Every metric readout, date, PR chip, and footer counter applies `font-variant-numeric: tabular-nums` so numbers align cleanly across grids and rows.

## Layout

Centered `1000px` max container (`--container-max`) framed on desktop viewports (`>= 1060px`) by subtle `1px` left/right architectural hairline rails (`hairline-border`). Vertical rhythm steps through `48px` section blocks (`--space-7`) separated by full-width horizontal `1px` rules.

The hero opens with an asymmetric 2-column grid (`1.25fr 0.95fr`) pairing concise positioning and action controls on the left with a 2×2 hairline-divided proof matrix on the right, collapsing cleanly to 1 column below `820px`. Featured projects and `/projects` use a 2-column grid (`repeat(2, minmax(0, 1fr))`, collapsing below `720px`).

## Elevation & Depth

Flat by default: zero `box-shadow` elevation and zero backdrop blur anywhere in the system. Hierarchy is conveyed solely through `1px` hairline borders, `1px` internal grid gaps over `--color-border`, and subtle 2–4% surface shifts between `--color-bg`, `--color-bg-subtle`, and `--color-bg-hover`.

**The Hairline Grid Rule.** Multi-cell metric panels (`proof-matrix` and `UsageSummary`) achieve structural crispness by setting `gap: 1px` against a `hairline-border` container background rather than drawing floating individual boxes.

## Shapes

Machined, low-radius geometry throughout:
- **Tags & Chips** (`4px` / `rounded.xs`): Tech stack tags, PR hashes (`#1794`), and highlight proof strips.
- **Buttons & Controls** (`6px` / `rounded.sm`): Primary/secondary CTAs, nav active items, filter toggles, and theme/language switches.
- **Cards & Tables** (`8px` / `rounded.md`): Project cards, proof matrix, OSS ledger, writing lists, and Mermaid diagram frames.

## Components

### Buttons
- **Shape:** Compact machined rectangle (`6px` radius).
- **Primary:** Solid `ink-primary` fill (`#0a0a0a` light / `#ededed` dark) with inverted `canvas-white` text (`padding: 8px 15px`, `font-weight: 500`).
- **Secondary:** `canvas-white` fill with `1px solid` `hairline-border`, shifting to `surface-hover` and `hairline-strong` border on hover.
- **Focus:** `2px solid` `precision-cobalt` outline with `4px` offset via `:focus-visible`.

### Chips
- **Style:** `4px` radius monospace chips (`11px`, `padding: 2px 7px`) with `1px solid` `hairline-border` on `surface-subtle` or `canvas-white`.
- **PR Hash Chips:** Cobalt text (`precision-cobalt`) shifting to `precision-cobalt-muted` fill and cobalt border on hover.

### Cards / Containers
- **Corner Style:** `8px` radius (`rounded.md`).
- **Background:** `canvas-white` shifting to `surface-subtle` on interactive hover.
- **Shadow Strategy:** None; uses `1px solid` `hairline-border` shifting to `hairline-strong` on hover.
- **Internal Padding:** `24px` (`16px` on compact mobile viewports).

### Navigation
- Static top bar (`border-bottom: 1px solid` `hairline-border`), anchored by a `28px` solid-ink `JJ` mark (`4px` radius), compact `6px`-radius nav links, `/` mono divider, and `30px`-tall `EN`/`Dark` controls. Collapses into a clean 2-row grid below `900px`.

### Proof Matrix & Telemetry Bar
- Signature component combining `1px` hairline grid cells with oversized `600`-weight `tabular-nums` values and `11px` monospace labels linking directly to verifiable artifacts (`DeepTutor`, `10 PRs`, `299`, live Token Ledger).

## Do's and Don'ts

### Do:
- **Do** keep all data claims, PR numbers, and test counts linked to real repositories or MDX evidence.
- **Do** use `1px` `gap` grids (`background: var(--color-border)`) for multi-cell telemetry and proof matrices.
- **Do** keep `tabular-nums` enabled on every metric, date, and counter.
- **Do** support both `[data-theme='light']` and `[data-theme='dark']` via CSS custom properties in `src/styles/tokens.css`.

### Don't:
- **Don't** add gradient text, neon glows, heavy drop shadows, or `backdrop-filter` glassmorphism.
- **Don't** place kickers/eyebrows above section headings or decorative bars down the side of cards.
- **Don't** introduce Tailwind CSS or client-side UI frameworks (keep Astro 5 + scoped native CSS).
- **Don't** use status colors (`#16a34a`, `#ca8a04`) as full badge backgrounds or body text colors.
