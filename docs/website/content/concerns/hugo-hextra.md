---
title: "Microsite (Hugo + Hextra)"
slug: hugo-hextra
generated: true
aliases:
  - /reference/glossary/concerns/hugo-hextra
---

**Category:** Documentation & Demos · **Areas:** all

## Description

## Category
microsite

## Areas
all

## Components

- **Static site generator**: Hugo (extended edition)
- **Theme**: Hextra (`github.com/imfing/hextra`), imported as a Hugo Module
- **Content format**: Markdown with YAML frontmatter
- **Deployment**: GitHub Pages via GitHub Actions
- **E2E testing**: Playwright with screenshot snapshots

## Constraints

- All site content lives under `website/` in the project root
- Hugo Module system for theme management — not git submodules, not manual copy
- Hextra theme provides layout, navigation, search, and responsive design — do
  not duplicate what the theme already does
- `go.mod` and `go.sum` in `website/` pin the theme version
- No custom CSS unless Hextra genuinely cannot achieve the design goal
- Markdown content must render correctly without the theme (readable on GitHub)
- `enableGitInfo: true` — Hugo uses git metadata for last-modified dates;
  CI must checkout with `fetch-depth: 0`
- `goldmark.renderer.unsafe: true` — allows raw HTML in markdown for shortcodes
- Hugo version pinned in CI workflow — do not rely on ambient `hugo` from PATH
- When governing artifacts change (new features, renamed commands, changed
  workflow rules, new artifact types), the corresponding microsite pages must
  be updated in the same pass — not deferred to a separate task

## Content Guidelines

Every microsite must include at minimum:

| Page | Path | Purpose |
|------|------|---------|
| Home | `content/_index.md` | Hero, value prop, feature grid, CTA |
| Getting Started | `content/docs/getting-started.md` | Install, first-run, quickstart |
| Core Concepts | `content/docs/<topic>/_index.md` | One section per major concept |
| CLI Reference | `content/docs/cli/_index.md` | Complete command reference |
| Demo | `content/docs/demos/_index.md` | Embedded terminal recordings |

### Home page pattern

Use `layout: hextra-home` and Hextra shortcodes. **Spacing is critical** —
the hero section must breathe. Use Hextra's `hx-` Tailwind utilities for
vertical rhythm between hero elements:

```markdown
---
title: Project Name
layout: hextra-home
---

{{</* hextra/hero-badge link="https://github.com/org/repo" */>}}
  <span>Open Source</span>
  {{</* icon name="arrow-circle-right" attributes="height=14" */>}}
{{</* /hextra/hero-badge */>}}

<div class="hx-mt-6 hx-mb-6">
{{</* hextra/hero-headline */>}}
  Tagline line one.&nbsp;<br class="sm:hx-block hx-hidden" />Tagline line two.
{{</* /hextra/hero-headline */>}}
</div>

<div class="hx-mb-12">
{{</* hextra/hero-subtitle */>}}
  One-sentence description of the project.
{{</* /hextra/hero-subtitle */>}}
</div>

<div class="hx-mb-12">
{{</* hextra/hero-button text="Get Started" link="docs/getting-started" */>}}
{{</* hextra/hero-button text="Learn More" link="docs/concepts" style="alt" */>}}
</div>

<div class="hx-mt-8"></div>

{{</* hextra/feature-grid */>}}
  {{</* hextra/feature-card title="Feature" subtitle="Description" */>}}
{{</* /hextra/feature-grid */>}}

<div class="hx-mt-16"></div>

## Below-the-fold section
```

#### Landing page spacing rules

| Element | Class | Purpose |
|---------|-------|---------|
| Hero headline wrapper | `hx-mt-6 hx-mb-6` | Breathing room above and below headline |
| Hero subtitle wrapper | `hx-mb-12` | Generous gap before CTA buttons |
| CTA button wrapper | `hx-mb-12` | Prevent buttons from crowding the feature grid |
| Spacer before feature grid | `hx-mt-8` | Visual separation between hero and features |
| Spacer before below-fold section | `hx-mt-16` | Clear break before secondary content |

**Do not** use `hx-mb-6` between CTA buttons and the feature grid — it looks
cramped. Use `hx-mb-12` on the button wrapper plus a `hx-mt-8` spacer div.

#### Feature card pattern

Use `hx-aspect-auto md:hx-aspect-[1.1/1]` and `max-md:hx-min-h-[340px]` on
the top row of feature cards to ensure consistent height. Use radial gradient
backgrounds for visual distinction:

```
style="background: radial-gradient(ellipse at 50% 80%,rgba(72,120,198,0.15),hsla(0,0%,100%,0));"
```

### Documentation page pattern

```markdown
---
title: Page Title
weight: 1
prev: /docs
next: /docs/next-section
---
```

Use `weight` for sidebar ordering, `prev`/`next` for sequential navigation.

### Shortcode preference

Use Hextra built-in shortcodes before creating custom ones:

- `hextra/hero-*` — landing page components
- `hextra/feature-grid` / `hextra/feature-card` — feature showcase
- `cards` / `card` — documentation index grids
- `tabs` / `tab` — tabbed content blocks
- `icon` — inline SVG icons

Only create a custom shortcode in `layouts/shortcodes/` when no Hextra
component covers the need (e.g., `asciinema.html` for terminal recordings).

## Hugo Configuration Pattern

```yaml
baseURL: https://<org>.github.io/<project>/
languageCode: en-us
title: <PROJECT> — <tagline>

module:
  imports:
    - path: github.com/imfing/hextra

enableRobotsTXT: true
enableGitInfo: true

markup:
  goldmark:
    renderer:
      unsafe: true
  highlight:
    noClasses: false

params:
  navbar:
    displayTitle: true
    displayLogo: false
  page:
    width: wide
  footer:
    displayCopyright: true
    displayPoweredBy: false
  editURL:
    enable: true
    base: https://github.com/<org>/<project>/edit/main/website/content
```

## E2E Testing Pattern

Playwright tests live at `website/e2e/` with `website/package.json`:

```json
{
  "name": "<project>-website-tests",
  "private": true,
  "type": "module",
  "scripts": {
    "test:e2e": "playwright test",
    "test:screenshots": "playwright test --update-snapshots"
  },
  "devDependencies": {
    "@playwright/test": "^1.59.1"
  }
}
```

Tests should verify:
- Homepage loads with hero content and feature cards
- Each documentation page loads and has expected headings
- Navigation links work
- Screenshot snapshots for visual regression

## CI/CD Pattern

GitHub Actions workflow for GitHub Pages deployment:

1. Trigger: successful test workflow on main + version tags + manual dispatch
2. Install Hugo (extended, pinned version) and Go
3. Checkout with `fetch-depth: 0` (required for `enableGitInfo`)
4. Build: `hugo --gc --minify` in `website/` directory
5. Deploy to GitHub Pages

## Drift Signals (anti-patterns to reject in review)

- CLI command added or changed without updating CLI Reference page → update the docs
- New artifact type in `workflows/activities/` without a glossary entry → add it
- Feature spec created or evolved without updating the microsite → update it
- Install process changed without updating Getting Started → fix it
- Demo reel recorded but not copied to `website/static/demos/` → publish it
- `hx-mb-6` between CTA buttons and feature grid on landing page → use `hx-mb-12` + `hx-mt-8` spacer
- Custom CSS when Hextra utility classes would suffice → use `hx-` classes
- Missing `_index.md` in a content section → add it for proper sidebar nav
- Hardcoded URLs instead of Hugo `relref` or `ref` → use Hugo link functions

## When to use

Any project that needs a public-facing documentation site. The Hugo + Hextra
pattern provides search, responsive design, dark mode, and navigation with
minimal configuration.

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- ADR: Hugo (extended) + Hextra theme via Hugo Modules, GitHub Pages deploy, as the microsite stack
- TD: website/ layout, pinned theme/Hugo versions, Hugo config (enableGitInfo, unsafe HTML)

## Practices by activity

Agents working in any of these activities inherit the practices below through runtime work context, such as a DDx bead context digest.

## Requirements (Frame activity)
- Define the site's target audience and what content they need
- List the documentation sections required (at minimum: getting started, concepts, CLI reference)
- Determine whether demo recordings are needed (see `demo-asciinema` concern)
- Decide on deployment target (default: GitHub Pages at `<org>.github.io/<project>`)

## Design
- Site lives in `website/` subdirectory — not the repo root
- Use Hugo Module system for Hextra theme (`go.mod` + `go.sum`)
- Navigation structure defined in `hugo.yaml` `menu.main` section
- Content hierarchy mirrors sidebar navigation — `_index.md` files create sections
- Prefer Hextra shortcodes over custom HTML for maintainability
- Static assets (images, recordings, downloads) go in `website/static/`
- Custom shortcodes only when Hextra has no equivalent

## Implementation
- Initialize with `hugo new site website` then add `go.mod` with Hextra import
- Pin Hextra version in `go.mod` — update deliberately, not automatically
- Pin Hugo version in CI — use the same version locally and in GitHub Actions
- Every content page needs YAML frontmatter with at minimum `title` and `weight`
- Section index pages (`_index.md`) use `cards` shortcode to link child pages
- Home page uses `layout: hextra-home` with hero and feature-grid shortcodes
- Menu items use `pageRef` for internal links, `url` for external (GitHub icon)
- Set `params.editURL.base` to enable "Edit this page" links
- Keep content readable as plain markdown — someone reading on GitHub should
  understand the docs even without Hextra rendering

## Content Authoring
- Write for the getting-started reader first — assume no prior knowledge of the project
- Getting Started page must get a user from zero to working in under 5 minutes
- CLI Reference must document every command with examples
- Use `tabs` shortcode for platform-specific instructions (macOS/Linux/Docker)
- Use `cards` shortcode for index pages that link to child content
- Embed terminal recordings with `asciinema` shortcode (see `demo-asciinema` concern)
- Include version badge on homepage hero using `hextra/hero-badge`
- Feature cards should each describe one capability with a concrete benefit

## Artifact-to-Docs Sync

The microsite must reflect the current state of the project's governing
artifacts. When artifacts are created, renamed, removed, or materially
changed, the corresponding microsite pages must be updated as part of the
same evolution or build pass.

### What triggers a docs update

Any change to a HELIX artifact that is surfaced on the microsite:
- New or renamed CLI commands → update CLI Reference
- New, renamed, or removed features → update glossary/artifacts page
- Changed activities, authority hierarchy, or workflow rules → update workflow page
- New or changed artifact types → update glossary/artifacts with description
  from `workflows/activities/*/artifacts/<name>/meta.yml` (description field)
  and `workflows/activities/*/artifacts/<name>/prompt.md` (Purpose section)
- New or changed concerns → update glossary/concerns page
- Changed install process → update Getting Started
- New demo reels → update Demos page and copy cast/video files to
  `website/static/demos/`

### Glossary generation from artifact metadata

Each HELIX artifact type has structured metadata at
`workflows/activities/<NN>-<activity>/artifacts/<name>/`:

| File | What it provides |
|------|-----------------|
| `meta.yml` | Name, description, dependencies, validation rules, relationships |
| `prompt.md` | Purpose section — 2-3 paragraphs explaining what the artifact is, why it matters, and how it fits the authority hierarchy |
| `template.md` | The structure to fill in |
| `example.md` | A concrete example |

The glossary artifacts page (`website/content/docs/glossary/artifacts.md`)
must include a substantive description for each artifact — not just a one-line
purpose. Pull the description from `meta.yml` and the Purpose section of
`prompt.md`. The reader should understand what each artifact is, when to
create one, and how it relates to artifacts above and below it in the
authority hierarchy.

### When evolve or frame changes artifacts

When the HELIX skill runs `evolve` or `frame` mode and creates or modifies a
governing artifact that is documented on the microsite, the agent must also
update the corresponding microsite page. This is not a separate task — it is
part of completing the evolution. The concern makes this a requirement, not a
suggestion.

Specifically:
- If a new artifact type is added to `workflows/activities/`, add it to the
  glossary artifacts page with its description from `meta.yml`/`prompt.md`
- If an artifact's purpose or scope changes, update the glossary entry
- If a skill mode is added or its behavior changes, update the relevant
  reference page
- If installation steps change, update Getting Started

## Testing
- Playwright e2e tests in `website/e2e/` verify page loads and navigation
- Screenshot snapshot tests catch visual regressions after theme updates
- Test every section landing page and the homepage
- Run `hugo --gc --minify` locally before pushing to catch build errors
- After Hextra version bumps, run screenshot update and review diffs

## Quality Gates
- `hugo --gc --minify` builds without errors or warnings
- `playwright test` passes (if e2e tests exist)
- No broken internal links (Hugo reports these as build warnings)
- Content files have valid YAML frontmatter

## Deployment
- GitHub Actions deploys on successful test + push to main
- Hugo build uses `--gc --minify` with `HUGO_ENVIRONMENT=production`
- Checkout must use `fetch-depth: 0` for git-based last-modified dates
- Cache Hugo modules in CI for faster builds
- Enable concurrent deployment protection to prevent race conditions
