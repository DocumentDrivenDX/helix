---
title: "Demo Reels (Playwright)"
slug: demo-playwright
generated: true
aliases:
  - /reference/glossary/concerns/demo-playwright
---

**Category:** Documentation & Demos · **Areas:** ui, frontend

## Description

## Category
demo

## Areas
ui, frontend

## Components

- **Recording tool**: Playwright — headless browser automation with video capture
- **Output**: WebM video files (Playwright native) and/or MP4 (via ffmpeg)
- **Playback**: `<video>` embed in microsite, or converted to GIF for README
- **Reproducible capture**: Scripted Playwright spec that drives the UI walkthrough
- **Demo scripts**: Playwright test files that exercise the app and narrate visually

## Constraints

- Demo reels are Playwright specs in `tests/e2e/` with a `reel` prefix or
  tag — they are both valid E2E tests and visual recordings
- Video recording is always-on for reel specs (not just on-failure)
- Reel specs run against a seeded database with realistic demo data — the
  same seed data used for E2E tests
- Recordings must be reproducible — re-running the reel spec should produce
  equivalent output
- Do not record manual browser sessions — always use a scripted reel spec
- Viewport: 1280x720 (720p) for consistent framing across machines
- No audio — the visual flow must be self-explanatory
- Pacing: include deliberate pauses (`page.waitForTimeout`) between actions
  so the viewer can follow at 1x speed

## Demo Reel Requirements

### Reel spec conventions

- File pattern: `tests/e2e/00-reel.spec.ts` (numbered to run first, before
  mutation-heavy tests that might dirty the seed data)
- Structured as `test.describe` blocks, one per section/act
- Each test within a describe block is one scene in the reel
- Scenes execute sequentially (`test.describe.serial`) — the reel tells a
  story with state building across scenes
- Include visual narration via injected overlay text or page titles between
  scenes — the viewer should understand what is being demonstrated

### Narrative structure

A demo reel tells a story, parallel to `demo-asciinema`:

1. **Setup** — Show the app's landing state, dashboard, or login
2. **Navigation** — Demonstrate moving between modules/sections
3. **Search** — Show finding data via search, filters, or command palette
4. **Editing** — Create, update, or delete entities through forms
5. **Verification** — Show the result: updated list, success state, changed data
6. **Summary** — Return to dashboard or overview showing the final state

### What to include in a reel

- The app's primary user journey from start to finish
- Real UI interactions that a user would perform (clicks, typing, navigation)
- Visible data that proves the app works (populated tables, completed forms)
- Transitions between major sections showing the app's breadth
- Loading states and confirmations — the viewer sees what the user sees

### What NOT to include

- Login flows (pre-authenticate or use seeded session)
- Long waits for API responses (seed data should be local/fast)
- Error states (unless error handling IS the demo topic)
- Browser chrome, DevTools, or console output
- Tooltips or hover states that flash too quickly to read at 1x

## Playwright Configuration for Reels

```typescript
// playwright.config.ts — reel-specific settings
const reelConfig = {
  use: {
    video: {
      mode: "on",           // always record for reel specs
      size: { width: 1280, height: 720 },
    },
    viewport: { width: 1280, height: 720 },
    launchOptions: {
      slowMo: 50,           // slight delay between actions for visual flow
    },
  },
};
```

Or per-spec override in the reel file:

```typescript
test.use({
  video: { mode: "on", size: { width: 1280, height: 720 } },
});
```

## Video Post-Processing

After the reel spec runs, Playwright writes `.webm` files to the test
output directory (`test-results/`).

Post-processing steps:

1. **Extract**: Copy the `.webm` from `test-results/` to
   `docs/demos/<name>/recordings/`
2. **Convert** (optional): `ffmpeg -i reel.webm -c:v libx264 reel.mp4` for
   broader browser support
3. **Trim** (optional): Cut dead time at start/end with ffmpeg
4. **GIF** (optional): `ffmpeg -i reel.webm -vf "fps=10,scale=640:-1" reel.gif`
   for README embedding (keep under 5MB)
5. **Copy to microsite**: Place in `website/static/demos/` for embedding

## Microsite Embedding

Use a standard HTML5 video element or a Hugo shortcode:

```html
<video autoplay loop muted playsinline width="100%">
  <source src="/demos/app-reel.mp4" type="video/mp4">
  <source src="/demos/app-reel.webm" type="video/webm">
</video>
```

Or a Hugo shortcode (create `layouts/shortcodes/demo-video.html`):

```markdown
{{</* demo-video src="app-reel" */>}}
```

## Drift Signals (anti-patterns to reject in review)

- Manual screen recording instead of scripted Playwright spec → automate it
- Reel spec with `video: "off"` or `video: "retain-on-failure"` → must be `"on"`
- Reel spec that depends on external services without seed data → seed locally
- Video with browser chrome visible → use headless or fullscreen viewport
- Reel with no pauses between actions → add `waitForTimeout` for pacing
- Screenshot-only demo → use video for multi-step workflows

## When to use

Any project with a web UI that needs to demonstrate functionality to users,
stakeholders, or evaluators. The web equivalent of `demo-asciinema` — scripted,
reproducible, and version-controlled. Composes with `e2e-playwright` for the
testing infrastructure and `ux-radix` for the interaction patterns being
demonstrated.

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- ADR: Playwright reel specs (video capture, seeded data, fixed viewport) as the demo-reel mechanism

## Practices by activity

Agents working in any of these activities inherit the practices below via the bead's context digest.

## Requirements (Frame activity)
- Identify which user journeys need demo reels — prioritize the "first
  impression" experience (dashboard → search → create → verify)
- Define the narrative arc: what should the viewer understand after watching?
- Determine target audience: evaluators seeing the product for the first
  time, or users learning a specific workflow?
- Ensure seed data exists that makes the demo look realistic (real names,
  realistic numbers, populated lists)

## Design
- One reel per major workflow or product area — do not combine unrelated
  features into one recording
- Reel spec lives alongside E2E tests: `tests/e2e/00-reel.spec.ts`
- Numbered `00-` prefix so it runs first, before mutation-heavy tests
- Sequential scenes within `test.describe.serial` blocks — each scene
  builds on the previous state
- Narrative structure: Landing → Navigate → Search → Edit → Verify → Summary
- Viewport: 1280x720 (720p) — consistent across all recordings
- Pacing: 500-1000ms pause between major actions via `page.waitForTimeout`

## Implementation

### Reel spec structure

```typescript
import { test } from "@playwright/test";

test.use({
  video: { mode: "on", size: { width: 1280, height: 720 } },
  viewport: { width: 1280, height: 720 },
});

test.describe.serial("Product Demo Reel", () => {
  test("Act 1: Dashboard overview", async ({ page }) => {
    await page.goto("/");
    await page.waitForTimeout(1000);  // let viewer absorb the layout
    // assert key elements visible
  });

  test("Act 2: Navigate to module", async ({ page }) => {
    await page.goto("/");
    await page.click('[data-testid="nav-finance"]');
    await page.waitForTimeout(500);
  });

  test("Act 3: Search for entity", async ({ page }) => {
    await page.goto("/finance");
    await page.keyboard.press("Meta+k");  // command palette
    await page.waitForTimeout(300);
    await page.fill('[role="combobox"]', "Orbital");
    await page.waitForTimeout(500);
    // select result, navigate
  });

  test("Act 4: Edit entity", async ({ page }) => {
    // create or update via form
    await page.waitForTimeout(500);
  });

  test("Act 5: Verify result", async ({ page }) => {
    // show updated list, success toast, changed data
    await page.waitForTimeout(1000);
  });
});
```

### Seed data requirements

- Reel specs run against the same seeded database as E2E tests
- Seed data must look realistic: real company names, plausible addresses,
  varied statuses, enough rows to fill tables without looking empty
- Deterministic seeds (fixed UUIDs, `ON CONFLICT DO NOTHING`) so reels
  are reproducible
- Include multiple entity states (draft, pending, approved, completed) to
  show workflow progression

### Pacing guidelines

| Action | Pause after |
|--------|------------|
| Page navigation | 1000ms |
| Modal/dialog open | 500ms |
| Form field fill | 300ms per field |
| Button click (submit) | 500ms |
| Search result appear | 500ms |
| Success confirmation | 1000ms |
| Section transition | 1500ms |

### Visual narration

Since there is no audio, the UI itself must tell the story:

- Use page titles and breadcrumbs to show location
- Ensure visible feedback for every action (toasts, status changes, count
  updates)
- Fill forms with readable demo data (not "test123" — use "Orbital Dynamics
  Corp", "Q4 2026 Revenue Accrual")
- If the app has a command palette, show it — it demonstrates power-user
  capability

## Recording

1. **Ensure seed data**: `bun run seed` or `bun run demo` to populate the database
2. **Run the reel spec with video**:
   ```bash
   bun run test:e2e -- tests/e2e/00-reel.spec.ts
   ```
3. **Extract video**: Playwright writes `.webm` to `test-results/`
4. **Convert** (optional):
   ```bash
   ffmpeg -i test-results/.../video.webm -c:v libx264 -crf 23 reel.mp4
   ```
5. **Copy to microsite**: `cp reel.mp4 website/static/demos/`
6. **Embed**: Use `demo-video` shortcode or `<video>` tag
7. **Commit**: Both the source recordings and microsite copy

Steps 1-3 are fully autonomous — an agent or CI job can run them without
human interaction as long as the app and database are running.

## Testing

- Reel specs are valid E2E tests — they assert correctness, not just
  visual appearance
- Run reel specs in CI without video (`video: "off"`) as a smoke test
- Run with video locally or in a scheduled CI job to regenerate recordings
- After UI changes that affect the demo flow, re-record and review

## Quality Gates

- Reel spec passes (exit 0) — broken demos must not produce recordings
- Video file exists and is playable
- Video is under 30MB for web embedding (compress further with ffmpeg if
  needed)
- All scenes in the reel exercise real functionality against seeded data
- Demo page in microsite loads and plays the video

## Maintenance

- Re-record after major UI changes, navigation restructuring, or data
  model changes
- Keep seed data aligned with the reel script — if the reel searches for
  "Orbital Dynamics", the seed must contain that entity
- When the reel drifts from the actual app behavior, treat it as a bug —
  either the reel or the app needs fixing
- Reel specs are executable documentation — they must stay correct
