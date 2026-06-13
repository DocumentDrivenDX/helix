---
title: "Plan — integrate the measurement-discipline learnings into HELIX (2026-05-25)"
slug: plan-2026-05-25-measurement-discipline
weight: 570
activity: "Design"
source: "02-design/plan-2026-05-25-measurement-discipline.md"
generated: true
---

> **Example from HELIX's own docs.** This generated page comes from `docs/helix/`. Use it to see the method in practice; start with the [artifact-type catalog](/artifact-types/) for reusable templates. Historical plans and reports may describe retired architecture.

# Plan — integrate the measurement-discipline learnings into HELIX (2026-05-25)

## Context

The self-improvement experiment (plan-2026-05-24) taught us as much about *measuring* methodology
changes as about the changes. This plan encodes those measurement learnings so HELIX's own
iterate/measure machinery carries them. **Scope discipline (per the over-engineering concern): two
genuinely-new, high-leverage integrations (M1, M2); M3–M4 are light reinforcements of text already
committed in plan-2026-05-24.** Captured as the three buckets: docs/ specs · workflows/ · skill.

## Learnings → integrations

- **M1 — The regression bench is the durable asset.** "Same brief, bare prompt, compare to a recorded
  baseline" is how we cheaply tell whether a methodology change matters. Formalize it as a first-class
  HELIX experiment so it's reusable, not re-derived. *(Evidence: the bench separated real wins from noise
  and is the answer to "how do we know it's impactful.")*
- **M2 — A metric can lie; fix the instrument before trusting it.** The "prd 1/8" was a broken instrument
  (template↔meta drift), not a bad run. Generalize: template↔meta must agree, and a metric-definition
  must be verified against reality. *(Extends FEAT-016 artifact-honesty from artifacts to instruments.)*
- **M3 — Intrinsic gates are blocking; external adversarial review is advisory.** codex hung repeatedly;
  it can't be a hard gate. *(Reinforce convergence text already in evolve/fresh-eyes-review.)*
- **M4 — Verify-don't-trust + transient-retry in autonomous runs.** A pass reported "complete" after
  dying on an API overload; verification caught it. *(Reinforce the self-validation mode-gates already
  added to measure/implementation; add a transient-retry note to the run loop.)*

---

## Bucket 1 — docs/ specs

| # | Change | File(s) | Done when |
|---|--------|---------|-----------|
| M1 | Add the **regression-bench experiment** to the iterate methodology: bare-prompt re-run vs a committed baseline, install-the-improved-skill (no prompt-redirect confound), intrinsic metrics + cut-what-doesn't-move | extend `FEAT-014-workflow-coverage.md` (or `FEAT-016` cross-ref) | FEAT describes the bench experiment + its convergence/cut rule |
| M2 | **Instrument integrity** = artifact honesty applied to gates: template↔meta must agree; a metric-definition's measurement must be verified against reality | extend `FEAT-016-artifact-honesty.md` | FEAT covers template/meta agreement + metric reality-check |

## Bucket 2 — workflows/ actions + artifacts

| # | Change | File(s) | Done when |
|---|--------|---------|-----------|
| M1 | Add the regression-bench protocol to the experiment action (steps: record baseline → change → bare-prompt re-run with improved skill installed → score intrinsic metrics vs baseline → keep/cut) | `workflows/actions/experiment.md` | experiment.md documents the bench protocol |
| M1 | Bench-metric exemplar (the baseline→target table shape) in the metric-definition artifact | `workflows/activities/06-iterate/artifacts/metric-definition/{template.md,example.md}` | example shows a bench metric with baseline + measurement command |
| M2 | **Template↔meta agreement check** (a metric/instrument can't be trusted if the template it scores and its meta.yml `required_sections` disagree) | `workflows/actions/reconcile-alignment.md` (align/validate) | a fixture with drifted template/meta is flagged |
| M2 | metric-definition must name a **verified, reproducible** measurement (no asserted-but-unmeasured metric) | `workflows/activities/06-iterate/artifacts/metric-definition/{template.md,meta.yml}` | template requires a runnable measurement + last-verified note |
| M3 | Convergence: intrinsic gates (build/test/conformance/phantom-count) are blocking; external adversarial review is advisory, never a hard gate | `workflows/actions/fresh-eyes-review.md`, `evolve.md` | text states the advisory-vs-blocking split |
| M4 | The run/measure loop runs its gates itself and tolerates transient failures (retry; don't trust a self-reported "complete") | `workflows/actions/measure.md`, and the run/worker action if present | text added; no new machinery |

## Bucket 3 — skill (`skills/helix/SKILL.md`) — normative, runtime-neutral

| # | Change | Done when |
|---|--------|-----------|
| M1 | The `experiment` route mentions the regression-bench as the way to validate a methodology/skill change | SKILL.md experiment route references it |
| M3 | The review/converge routes state intrinsic-gates-blocking / external-review-advisory | SKILL.md reflects the split |

(No new runtime-specific assertions; no flattening the seven-activity loop; bench installs the improved skill rather than redirecting reads.)

---

## How we'll re-run the bench (validate THIS plan)

The app-building bench mainly validates M2's instrument fix + M4 directly; M1/M3 are validated by their own
presence + a self-test. After implementing:
1. **Re-run the clean bench** (`bin/rerun-clean.sh`, bare prompt, improved skill) and re-score the baseline table.
   Expect the **prd-conformance instrument now reads accurately** (the M2 fix → prd scores its true conformance,
   not a misleading 1/8), plus the prior wins reconfirm (concerns auto-selected, real UI, build first-try).
2. Confirm `workflows/actions/experiment.md` now yields a usable regression-bench protocol (M1) and the
   metric-definition exemplar exists.
3. Keep only what moved/clarified a metric; cut the rest. Note any NEEDS-OPERATOR.

## Invariants
- Runtime neutrality; no `Skill tool_use` in the skill body; don't flatten the loop.
- Fix instruments before trusting their metrics (M2 applied to ourselves).
- Keep `check-workflow-paths` happy (`.ddx/plugins/helix/workflows/` not bare `workflows/`); re-bless ddx hashes; commit unsigned only if the signer is unavailable (flag it).
