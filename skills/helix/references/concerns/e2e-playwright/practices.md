# Practices: e2e-playwright

## Run the core flow (coverage, not configuration)

Selecting this concern — adding `@playwright/test`, a `playwright.config.ts`, and
a `.spec` file — is **not** e2e coverage. Coverage means **at least one core
user-flow has a browser e2e test that actually RUNS GREEN against the running
app**. A spec that is written but never executed, or that passes only because it
asserts nothing, does not count. The gate is verification, not the presence of a
config:

1. Start the app (`webServer` in `playwright.config.ts`, or start it manually).
2. Run the e2e suite (`npx playwright test`) so the browser drives a core
   user-flow against the live app.
3. The core-flow test must pass — exit 0 with a real assertion on the end state.

If the e2e suite was never run against the running app, the AC the flow backs is
`UNTESTED` (see reconcile-alignment Acceptance Criteria Validation), not covered.

## Assert the current-location cue (mechanized visual-cue gate)

For a UI web app, the browser e2e MUST assert the current-location cue, not
eyeball it: navigate to a route, then assert that the active nav item carries
**`aria-current="page"`** for **≥1 route**. This assertion is **required and
non-optional**.

- Use the **portable** assertion (works across Playwright versions): locate the
  active nav link, then `await expect(activeNavItem).toHaveAttribute('aria-current', 'page')`.
  (The `getByRole(..., { current: 'page' })` option exists only in newer
  Playwright — don't rely on it.)
- An active class or style MAY be asserted *additionally* (e.g. a stable
  token/class contract) but is **never a substitute** for the `aria-current`
  assertion — assert the semantic state first.
- **No pixel/screenshot assertions for this gate.** Screenshot baselines remain
  fine for general visual regression, but the current-location cue is verified
  by asserting the semantic state (and optionally a stable class/token), never
  by a rendered-image comparison.

This is the same requirement stated by the `ux-radix` concern's current-location
feedback rule, and it feeds the `verification` gate
(`workflows/concerns/verification/practices.md`): the
operator's "clicking Invoices gives no feedback" bug becomes a failing e2e
assertion until the cue exists.

## Requirements (Frame activity)
- Identify all user-facing pages and workflows that need testing
- Define what "test data" means for this project — what states must the UI show?
- Determine visual regression strategy: which pages get screenshot baselines?
- Decide on browser matrix: Chromium only, or cross-browser?

## Design
- Tests live in `<project-root>/e2e/` or `website/e2e/` for microsites
- One test file per feature area or page group
- Use `test.describe()` blocks to group related tests
- Use `test.step()` for every meaningful action — produces structured logs
- Test data is deterministic and committed (or seeded deterministically)
- Screenshot baselines committed under `e2e/*.spec.ts-snapshots/`
- Video recording enabled for all tests — `video: 'on'` in config

## Implementation
- Install: `npm install -D @playwright/test && npx playwright install`
- Configure `playwright.config.ts` with video, trace, and reporter settings
- Write tests that use real browser interactions (click, type, navigate)
- Use Playwright's locator API: `getByRole()`, `getByText()`, `getByLabel()`
- Prefer semantic selectors over CSS selectors or test-ids
- Every test should:
  1. Navigate to the page
  2. Verify key content is visible
  3. Capture a full-page screenshot for visual regression
- Workflow tests should:
  1. Start at the entry point
  2. Perform the user's action sequence
  3. Verify the end state
  4. Capture screenshots at key steps

## Test Data
- **Static sites**: ensure content files cover all page types, shortcodes,
  navigation levels, and edge cases. Add a "kitchen sink" test page if needed
  that exercises every component
- **Web apps**: create a seed script (e.g., `scripts/seed-test-data.sh`) that
  populates deterministic fake data. Run before tests. Include:
  - Empty states (zero items)
  - Populated states (10+ items)
  - Error states (invalid data, missing fields)
  - Edge cases (long text, special characters, large numbers)
- **Never test against production data** — always use controlled test data

## Testing
- Run locally: `npx playwright test` (starts dev server automatically)
- Update screenshots: `npx playwright test --update-snapshots`
- Review screenshots in PR diffs — screenshot changes must be intentional
- Run in CI: same command, upload `test-results/` and `playwright-report/`
  as artifacts
- After dependency updates (Playwright, browser, framework), re-baseline
  screenshots and review

## Video Review
- Videos are generated in `test-results/<test-name>/video.webm`
- Review videos when:
  - A test fails and the error message isn't clear
  - Updating screenshot baselines (watch the video to verify visual changes)
  - Debugging flaky tests (video shows timing/race conditions)
- In CI, upload `test-results/` as a build artifact for post-hoc review

## Demo reels — delegated to `demo-playwright`

Scripted walkthrough videos (viewport, pacing, narrative structure,
post-processing) belong to `demo-playwright`. Select that concern alongside
this one when a reel is needed; do not author demo specs here.

## Quality Gates
- At least one core user-flow has a browser e2e test that **runs green against
  the running app** (the run-core-flow gate above — selecting the tool is not
  coverage)
- `npx playwright test` passes with zero failures
- All screenshot baselines are committed and up-to-date
- Every navigable page has at least one test
- The browser e2e asserts `aria-current="page"` on the active nav item for ≥1
  route (required; an active class/style only as an additional assertion, never
  a substitute; no screenshot assertions for this cue)
- Every user-facing workflow has at least one end-to-end test
- Video recording is enabled (not disabled for speed)
- No tests skip or are marked `.only`

## CI Integration
- Run Playwright tests after the build step
- Upload `test-results/` and `playwright-report/` as artifacts
- Fail the build on any test failure
- Cache Playwright browsers to speed up CI
- For static sites: build first (`hugo --gc --minify`), then serve and test
