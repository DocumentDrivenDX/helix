---
title: "Plan — decomposition/coverage determinism + e2e expectation (2026-05-25)"
slug: plan-2026-05-25-coverage-determinism
weight: 560
activity: "Design"
source: "02-design/plan-2026-05-25-coverage-determinism.md"
generated: true
---

> **Example from HELIX's own docs.** This generated page comes from `docs/helix/`. Use it to see the method in practice; start with the [artifact-type catalog](/artifact-types/) for reusable templates. Historical plans and reports may describe retired architecture.

# Plan — decomposition/coverage determinism + e2e expectation (2026-05-25)

## Context

The parallel claude+codex bench of the concern-slots work (PROGRESS iteration 24) converged perfectly on
the *stack and concerns* (both built a green react-nextjs SPA, identical 5 concerns, prd 8/8) — but diverged
~4× on **rigor**: claude produced 44 tests / 6 user stories / 3 ADRs / 13 routes; codex 10 / 3 / 1 / 1. Both
GREEN. "Green" hides how much rigor each runtime chose, because HELIX now pins stack + concerns but **not
depth**. This plan makes depth deterministic, the same way slots made stack-choice deterministic.

Scope-disciplined: two substantive changes (C1 coverage discipline, C2 e2e slot — reuses the slot machinery)
+ one bench-instrument fix (C3). ADR-per-decision is stated as an expectation, not hard-gated ("material" is
too fuzzy to gate deterministically — gating it would be over-engineering).

## Changes

- **C1 — Coverage discipline (a minimum-rigor FLOOR, not equal total depth).** Make decomposition + test
  coverage a checked floor, not runtime taste — extra stories/tests are always welcome (floor, not cap):
  (a) **every stable PRD functional requirement `FR-n` maps to ≥1 user story `US-n`** (a story should not
  bundle multiple unrelated FRs without explicit justification; requires stable `FR-n` IDs in the PRD/template
  or the mapping isn't reproducible); (b) **every acceptance criterion traces to ≥1 test that *exercises* it**
  — not merely a named test. Extends the existing AC-traceability check from *presence* to *coverage*, while
  preserving its existing adequacy semantics: a weak/irrelevant test is classified `UNTESTED` /
  `ASSERTED_UNBACKED`, not counted as covered. **Default severity: blocking**, with one escape hatch — an
  explicitly reviewed exception ("manual verification accepted" / "non-automatable AC") recorded with
  evidence. Never silently pass an untested AC. *(codex-review fixes 1-4)*
- **C2 — e2e expectation via a slot, AND a run core-flow gate.** Neither runtime selected `e2e-playwright`;
  codex referenced playwright anyway, claude did 0 e2e — and our bench never *ran* a browser e2e, so neither
  run was verifiably exercised through a browser. Two parts: (i) add an **`e2e-framework` exclusive slot**
  (default `e2e-playwright`), a UI web app must fill it — reusing the slot resolution + integrity machinery;
  `e2e-kind` stays a separate infra-domain concern (areas api,infra), not a member. (ii) **Selecting the tool
  is not coverage** — require **at least one core user-flow to be covered by a browser e2e test that actually
  RUNS green against the running app**, as a verification gate (not just a config + a `.spec` file). *(codex
  fix 5 + operator: "thoroughly evaluate the app by driving a browser")*
- **C3 — bench-instrument fix (helix-yolo, not the methodology).** `score.sh` (a) reports global *distinct*
  AC refs (dedupes AC1/AC2 across stories), undercounting — switch to **per-story AC coverage + whether each
  AC has a test**; and (b) never runs the e2e suite — add a step that **starts the app and runs the e2e
  framework (browser) against it**, reporting the result, so the bench can see browser-coverage directly.

## Bucket 1 — docs/ specs

| # | Change | File(s) | Done when |
|---|--------|---------|-----------|
| C1 | Decomposition rule: one user story per PRD functional requirement; ADR per material decision (expectation, not gate) | extend `FEAT-008-artifact-template-quality.md` | FEAT states story-per-FR + ADR-per-decision |
| C1 | Coverage rule: every AC traces to ≥1 test (blocking coverage gap if not) | extend `FEAT-010-testing-strategy-templates.md` | FEAT states AC→test coverage |
| C2 | `e2e-framework` exclusive slot + default `e2e-playwright`; a UI web app fills it | extend `FEAT-006` (slots) + `FEAT-010` (e2e expectation) | FEAT-006 lists the slot; FEAT-010 states the e2e expectation |

## Bucket 2 — workflows/ actions + artifacts + concerns

| # | Change | File(s) | Done when |
|---|--------|---------|-----------|
| C1 | PRD/template: stable `FR-n` IDs on functional requirements (so FR→story is reproducible) | `workflows/activities/01-frame/artifacts/prd/{template.md,prompt.md}` | functional requirements carry stable `FR-n` IDs |
| C1 | user-stories template/prompt: every `FR-n` maps to ≥1 `US-n` (no bundling unrelated FRs without justification), stable `US-n`/`AC-m` IDs | `workflows/activities/01-frame/artifacts/user-stories/{template.md,prompt.md}` | template requires the FR→story mapping |
| C1 | Extend **Acceptance Criteria Validation** from presence to **coverage**: every `FR-n` has ≥1 story; every AC has ≥1 test that *exercises* it (weak/irrelevant → `UNTESTED`/`ASSERTED_UNBACKED`, not covered). Blocking, with a recorded reviewed-exception escape hatch | `workflows/actions/reconcile-alignment.md` | check flags an FR with no story, an AC with no exercising test; honors a recorded exception |
| C1 | story-test-plan: every AC row names the **behavior/assertion** the test makes (not just a test name) | `workflows/activities/03-test/artifacts/story-test-plan/{template.md,prompt.md}` | per-AC rows require a named assertion |
| C2 | Add `e2e-framework: { exclusive: true }` + `defaults: e2e-framework: e2e-playwright` | `workflows/concerns/slots.yml` | slot + default present |
| C2 | `## Slot` = `e2e-framework` on the e2e-playwright concern | `workflows/concerns/e2e-playwright/concern.md` | concern declares the slot |
| C2 | Concern-resolution: a web app with a UI fills `e2e-framework` (override→default→assumption); **≥1 core user-flow must have a browser e2e test that runs green** against the running app | `workflows/references/concern-resolution.md` + e2e-playwright `practices.md` | resolution names e2e-framework + the run-core-flow gate |

## Bucket 3 — skill (`skills/helix/SKILL.md`) — normative, runtime-neutral

| # | Change | Done when |
|---|--------|-----------|
| C1 | Frame/test guidance: one story per FR; every AC has a test | SKILL.md reflects the coverage floor |
| C2 | A UI web app fills the e2e-framework slot (default e2e-playwright) | SKILL.md reflects the e2e expectation |

## Bucket 4 — bench instrument (helix-yolo)

| # | Change | File | Done when |
|---|--------|------|-----------|
| C3 | Per-story AC coverage + AC-has-test (not a global distinct count) | `bin/score.sh` | scorecard shows per-story AC coverage |
| C3 | Start the app + RUN the e2e framework (browser) against it; report pass/fail | `bin/score.sh` | scorecard shows a real browser-e2e result |

## How we'll re-run the bench (validate THIS plan)

Re-run the PARALLEL bench (claude + codex, bin/rerun-clean.sh + bin/rerun-codex.sh, scored by the updated
score.sh). Expect the **rigor gap to narrow**: both runtimes produce ≥1 story per PRD FR, every AC has an
exercising test, and **both fill the new `e2e-framework` slot AND a core-flow browser e2e RUNS green** (the
new score.sh e2e step shows it) — so codex no longer green-at-10-tests/3-stories/0-verified-e2e while claude
is at 44/6/0-e2e. Compare the iteration-24 numbers to the new ones; keep only what moved a metric.

## Invariants
- "slot" not "role"; e2e-framework reuses the keyed-defaults + integrity machinery (duplicate-key check
  applies — keep the check slot-agnostic, don't hard-code slot names).
- Coverage is a *floor* (minimum rigor), not a cap and not a promise of equal total depth — flag MISSING
  required coverage only; never punish a runtime for MORE rigor.
- An untested AC blocks green UNLESS a reviewed exception (manual/non-automatable) is recorded with evidence.
- Selecting an e2e tool ≠ e2e coverage: a core user-flow must have a browser e2e test that actually runs green.
- ADR-per-decision is an expectation, not a hard gate (no fuzzy "material" gating).
- Runtime neutrality; no `Skill tool_use` in the skill; don't flatten the loop.
- Keep `check-workflow-paths` green; re-bless ddx hashes; codex-review this plan BEFORE and the diff AFTER.
