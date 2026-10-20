# HELIX Microsite — Design Language

> Source of truth for all visual and structural decisions on the HELIX microsite (`website/`).
> Hugo + hextra theme. Deployed at https://documentdrivendx.github.io/helix/

---

## Core Metaphor

**The DNA double helix as human–AI dance.**

Two strands wind around each other — neither leads, neither follows alone. The base-pair rungs between them are the collaboration moments: intent, review, correction, approval. This is the visual and conceptual spine of everything on the site.

- **Human strand** — terracotta coral (`#C44B2F`) — organic, intentional, steering
- **AI strand** — indigo (`#3B6BA8`) — precise, continuous, executing; echoes DDx's Cold Steel Blue
- **Rungs** — the handoff moments — rendered as connecting bridges between the two strands, using a neutral that glows in accent colors at interaction points

---

## Color Tokens

HELIX complements DDx's industrial palette (Cold Steel / Aged Brass / Iron Gray on parchment) with
a biological palette: terracotta coral (human) + indigo (AI) + violet (connection). The indigo
echoes DDx's steel-blue family — they read as related. Coral and violet are HELIX-only territory.

### Brand Colors

| Token | Light value | Dark value | Role |
|---|---|---|---|
| `--helix-human` | `#C44B2F` | `#E07A5F` | Human strand — terracotta coral, organic, warm |
| `--helix-ai` | `#3B6BA8` | `#6B9FD4` | AI strand — indigo, echoes DDx steel-blue family |
| `--helix-connect` | `#6842A8` | `#9B74D4` | Rung/handoff — violet, bridges coral ↔ indigo |

### Gradient System

All feature card gradients use `radial-gradient(ellipse at 50% 80%, …, transparent)`.

| Name | Stops | Used for |
|---|---|---|
| `gradient-ai` | `rgba(59,107,168,0.15)` → transparent | AI/docs feature cards |
| `gradient-connect` | `rgba(104,66,168,0.15)` → transparent | Authority/process cards |
| `gradient-human` | `rgba(196,75,47,0.12)` → transparent | Human/progress cards |

### Neutral Scale

Inherits hextra's Tailwind neutral scale. No overrides needed — the brand colors provide all differentiation.

---

## Typography

### Font Stack

| Role | Font | Fallback |
|---|---|---|
| Headlines (`h1`–`h3`) | **Space Grotesk** | system-ui, sans-serif |
| Body / prose | **Inter** | system-ui, sans-serif |
| Code / monospace | **JetBrains Mono** | monospace |

Hextra loads Inter by default. Space Grotesk for headlines gives HELIX a technical-but-distinct personality without diverging from the functional sans-serif family.

### Type Scale (key levels)

| Level | Size | Weight | Line-height | Letter-spacing |
|---|---|---|---|---|
| `display-lg` | 3.5rem | 700 | 1.1 | -0.03em |
| `display-md` | 2.25rem | 700 | 1.15 | -0.02em |
| `headline` | 1.5rem | 600 | 1.3 | -0.01em |
| `body-lg` | 1.125rem | 400 | 1.7 | 0 |
| `body-md` | 1rem | 400 | 1.65 | 0 |
| `label` | 0.875rem | 500 | 1.4 | 0.01em |
| `mono` | 0.875rem | 400 | 1.6 | 0 |

---

## Shape & Spacing

- **Roundness**: 8px (`ROUND_EIGHT`) — functional, not precious. Cards, buttons, code blocks.
- **Feature cards**: 12px — slightly softer for the home page marketing context.
- **Spacing unit**: 4px base. Key intervals: 4, 8, 12, 16, 24, 32, 48, 64, 96.
- **Max content width**: 72rem (already set in hextra config)
- **Max page width**: 90rem (already set)

---

## Motion

Philosophy: **slow, deliberate, purposeful**. HELIX is an autopilot, not an entertainer. Motion should feel like watching a controlled system work, not a product trying to impress.

### Hero SVG animation

- Strand rotation: `360deg` over `12s`, `linear`, `infinite` — imperceptible moment-to-moment, satisfying over time
- Rung pulse: opacity `0.4 → 1.0 → 0.4` over `3s`, staggered by index — mimics base-pair "activation"
- Shimmer sweep: subtle `linearGradient` opacity shift, `6s` ease-in-out

### Global motion rules

```css
@media (prefers-reduced-motion: reduce) {
  /* All HELIX animations pause — no fallback degraded state, just stopped */
  [data-helix-animate] {
    animation: none !important;
    transition: none !important;
  }
}
```

### Hover / interaction

- Links: `color` transition `150ms ease`
- Cards: `transform: translateY(-2px)` + `box-shadow` lift `200ms ease`
- Buttons: `background` shift `120ms ease`
- No bouncy easing — use `ease` or `ease-out` only

---

## Component Patterns

### Hero section

Structure (top to bottom):
1. Badge (`hextra/hero-badge`) — "Open Source" chip
2. **Hero visual** — DNA SVG, centered, `max-width: 320px`, floats right on `md+` or centers on mobile
3. Headline (`hextra/hero-headline`)
4. Subtitle (`hextra/hero-subtitle`)
5. CTA buttons (`hextra/hero-button`)
6. Feature grid (`hextra/feature-grid`)

The SVG sits alongside the text on desktop (two-column), stacks above on mobile. It should not compete with the headline — it complements it.

### Feature cards

Existing pattern: `radial-gradient(ellipse at 50% 80%, rgba(…), transparent)`. Keep exactly. The gradient washes are intentionally subtle — they create warmth without screaming color.

### Glossary cards

Use hextra `{{< cards >}}` / `{{< card >}}` for the top-level index. Each artifact subpage gets:
- Short 1–2 sentence description (prose, not bullets)
- Full worked example in a fenced code block or blockquote
- "Template" and "Prompt" links in a small footer row

---

## Conceptual model — kinds of work, not steps

The seven HELIX activities (Discover, Frame, Design, Test, Build, Deploy, Iterate) name kinds of work, connected by an authority order. Work moves between them in every direction. Layout decisions across the site should reflect this:

- **No "Phase N" prefixes.** Activity names stand on their own. Numeric ordering in directory names is a reading convenience.
- **Cross-activity links surface authority and dependency**, not "previous" / "next." A failing test points at a design gap; a metric points at a PRD; never at an adjacent step.
- **No left-to-right pipelines in visualizations.** Prefer radial, grid, or table layouts. Arrows that imply temporal order are misleading.
- **The DNA double-helix metaphor is the shape to lean on.** Two strands, intertwined, both moving, both load-bearing.

Where activities are listed, group artifacts under the activity name without a number prefix (e.g., `## Discover`, not `## Phase 0 — Discover`).

---

## Site Architecture (current state)

The microsite has six top-level sections, ordered by typical reader journey:

| Section | Purpose | Audience |
|---|---|---|
| `/why/` | What HELIX is, the thesis, principles | First-time visitor evaluating |
| `/artifacts/` | This project's actual governing artifacts (HELIX's own dogfood) | Reader wanting a worked example |
| `/artifact-types/` | HELIX's catalog of artifact categories (PRD, ADR, vision, etc.) | Practitioner looking up a type |
| `/concerns/` | Cross-cutting concerns catalog | Practitioner selecting standards |
| `/use/` | Getting started, workflow guide | Adopter onboarding |
| `/reference/` | Glossary (activities, actions, concepts), CLI, skills | Practitioner reference |

### The Artifacts vs. Artifact Types split

This split is load-bearing:

- **Artifact type** = a category HELIX defines (template + prompt + quality criteria + position in the authority order). Methodology-level. Reusable across projects.
- **Artifact** = an instance in a specific project (a real markdown file written from a type's template).

`/artifact-types/` documents the categories; `/artifacts/` shows what they look like in practice. Each artifact-type page links to its instances in this project; each artifact instance links back to its type.

### Content generation

Two deterministic generators produce machine-authored content; never edit the output directly:

| Generator | Source | Destination |
|---|---|---|
| `scripts/generate-reference.py` | `workflows/phases/*/artifacts/*/` (types + concerns) | `website/content/artifact-types/`, `website/content/concerns/` |
| `documentor record` | `docs/helix/` (this project's instances) | `website/content/artifacts/` |

Both wipe their destinations before each run and emit byte-identical output for identical input. Both are project-agnostic — `--source`, `--dest`, `--project` flags let other HELIX-shaped projects reuse them.

### Navigation labels

| Menu label | Path | Notes |
|---|---|---|
| Why HELIX | `/why` | Thesis + principles + who it's for |
| Artifacts | `/artifacts` | This project's actual instances, activity-grouped |
| Artifact Types | `/artifact-types` | Catalog of categories, activity-grouped |
| Concerns | `/concerns` | Cross-cutting concerns catalog |
| Use HELIX | `/use` | Getting started + workflow |
| Reference | `/reference` | Glossary, CLI, skills |
| GitHub | external | Source link |

### URL conventions

- No phase-number prefix in URLs (`/artifacts/product-vision/`, not `/artifacts/00-discover/product-vision/`).
- Activity affiliation surfaces in page frontmatter (`activity: Discover`) and landing-page grouping, not in URLs.
- All old URLs redirect via Hugo aliases (`/docs/glossary/phases` → `/reference/glossary/activities` etc.). Pre-existing inbound links don't break.

---

## Reusable layout patterns

Where the same concept appears across pages, prefer a shortcode or partial over repeated prose:

| Pattern | Implementation | Where used |
|---|---|---|
| Activity callout | `{{< activity name="Discover" >}}` (shortcode, TBD) | Activity affiliation on artifact pages |
| Loop visualization | Hero SVG partial; ASCII fallback for content pages | Workflow page, activities glossary |
| Card grid by activity | `{{< cards >}}` (hextra-native) | Artifact-type landing, artifact instance landing |
| Source identity callout | Generated by `documentor record` (preserves the source `ddx:` block) | Every artifact instance page |

Repeated phrases like "Phase 0 — Discover" or "the autopilot loop" should never appear as inlined prose — surface them through templates so they update in one place.

---

## Accessibility

- All SVG elements: `role="img"` + `<title>` + `aria-labelledby`
- Reduced motion: `@media (prefers-reduced-motion: reduce)` stops all animation
- Color contrast: brand colors used for decoration only — never as the sole carrier of information
- Focus rings: inherit hextra's defaults (do not suppress)
