# Plan — aggressive-verification concern + AC-citation traceability (2026-05-25)

## Context

Operator directive: agents default to "write some code and call it good." Drive them to **aggressively
verify** — re-review + end-to-end tests of the **entire stack** (real user flows against the running system),
to catch **locally-correct / globally-wrong**. The it.25 re-bench proved the e2e-run-gate works (both runtimes
now end-to-end-completeness=VERIFIED), and surfaced a sibling gap: **AC→test traceability is uneven** — claude
cites AC IDs in tests (22/22), codex writes good behavioral tests that don't cite the AC ID (0/25, untraceable).

This plan makes aggressive verification a first-class, always-on **concern**, and makes AC→test coverage
machine-checkable by requiring tests to **cite the AC they cover**.

Scope-disciplined: one new concern + one traceability tightening of the existing AC-coverage check. No new
machinery beyond the concern library + the check we already extended in it.25.

## Changes

- **V1 — `verification` concern (always-on, areas: all) = the EVIDENCE GATE.** Explicit boundary (codex fix 1):
  `testing` owns test strategy/frameworks; `e2e-framework` owns the e2e tooling; **`verification` owns "not
  done until observed evidence exists."** Its practices require, before "done", concrete **evidence
  artifacts** (codex fix 5): the command run + exit status, the target URL/env, the core flows exercised, and
  a short **re-review checklist** against ACs + integration risks. Encodes: re-review before done (adversarial,
  not self-check); verify-don't-trust (never assert an unobserved result — extends M4); "done" = whole stack
  exercised with recorded evidence, not unit-green. Auto-selected at high autonomy for buildable products —
  **with exceptions** (codex fix 6): library/docs-only/non-buildable work, and products where full-stack e2e
  is genuinely infeasible (record why).
- **V2 — AC-citation traceability (an ADDITIONAL gate, not a replacement).** Preserve the existing coverage
  semantics (a test must *exercise* the AC, *pass*, and the implementation must satisfy it — codex fix 2); on
  top of that, a covering test must **cite the AC ID in a canonical, parseable syntax** (e.g. a structured tag
  `@covers US-001-AC3`, stable AC IDs — codex fix 4), so traceability is machine-checkable, not guessed.
  Classification (codex fix 3): a test that exercises+passes but doesn't cite → **`UNCITED_COVERAGE`
  (UNTRACEABLE)**, rolled up as "not covered for AC *traceability*" (distinct from `UNTESTED` — the fix is
  *add the citation*, not write a new test). A test that *cites* an AC but does NOT exercise it →
  `ASSERTED_UNBACKED` (existing honesty failure mode). Fixes codex's 0/25 untraceable vs claude's 22/22.

## Bucket 1 — docs/ specs

| # | Change | File(s) | Done when |
|---|--------|---------|-----------|
| V1 | Govern the verification concern: aggressive end-to-end verification is a required discipline (re-review, full-stack e2e runs green, verify-don't-trust, done=stack-exercised) | extend `FEAT-010-testing-strategy-templates.md` (or note a new verification FEAT if cleaner) | FEAT describes the verification discipline + that it's a concern |
| V2 | AC→test coverage requires the test to CITE the AC ID | extend `FEAT-010` (+ cross-ref `FEAT-016` honesty) | FEAT states tests must cite the AC they cover |

## Bucket 2 — workflows/ concern + actions + artifacts

| # | Change | File(s) | Done when |
|---|--------|---------|-----------|
| V1 | New concern `verification/` (concern.md + practices.md): Category quality-attribute, Areas all. **Boundary**: testing=strategy, e2e-framework=tooling, verification=evidence-gate ("not done until observed evidence exists"). Practices require evidence artifacts (command+exit, URL/env, flows exercised, re-review checklist), verify-don't-trust, done=stack-exercised. **Exceptions**: library/docs-only/non-buildable, e2e-infeasible (record why) | `workflows/concerns/verification/{concern.md,practices.md}` | concern exists as an evidence gate with exceptions |
| V1 | High-autonomy concern-resolution auto-selects `verification` for buildable products (honor the exceptions) | `workflows/references/concern-resolution.md` | resolution lists verification + its exceptions |
| V2 | Acceptance Criteria Validation: KEEP exercise+pass+satisfy; ADD a canonical AC-ID citation requirement. New classifications: `UNCITED_COVERAGE` (exercises+passes but no citation → not covered for traceability, fix=add citation) vs `ASSERTED_UNBACKED` (cites but doesn't exercise) | `workflows/actions/reconcile-alignment.md` | check adds citation gate + the two classifications, preserving existing semantics |
| V2 | story-test-plan: each AC row names the covering test AND that test cites the AC ID in the canonical syntax | `workflows/activities/03-test/artifacts/story-test-plan/{template.md,prompt.md}` | template requires canonically-cited tests |

## Bucket 3 — skill (`skills/helix/SKILL.md`) — normative, runtime-neutral

| # | Change | Done when |
|---|--------|-----------|
| V1 | Build/verify guidance: not "done" until re-reviewed + full stack exercised by a green e2e; verify-don't-trust | SKILL.md reflects the verification discipline |
| V2 | Tests must cite the AC ID they cover | SKILL.md states the citation rule |

## Bucket 4 — bench instrument (helix-yolo) — NON-NORMATIVE bench hygiene (codex fix 6)

| # | Change | File | Done when |
|---|--------|------|-----------|
| B1 | Refine `score.sh` start-smoke: run the app's own start script (preserve boot/seed) with a free-port override instead of a bare `next start` | `bin/score.sh` | **DONE + validated (now HTTP 200, was 500)** — not a methodology change |

## How we'll re-run the bench (validate THIS plan)

Parallel re-bench (claude + codex). Expect: both still end-to-end-completeness=VERIFIED, AND **codex's AC
coverage rises from 0/25** because tests now cite AC IDs (traceability becomes cross-runtime-consistent).
`verification` appears in both concerns.md selections. Keep only what moves a metric.

## Invariants
- Clear boundary: `testing`=strategy, `e2e-framework`=tooling, `verification`=evidence gate. No duplication.
- AC-citation is an ADDITIONAL gate on top of exercise+pass+satisfy — never a replacement. It makes coverage
  *traceable*, not *more numerous*. `UNCITED_COVERAGE` ≠ `UNTESTED` ≠ `ASSERTED_UNBACKED`.
- Honor exceptions: library/docs-only/non-buildable work and e2e-infeasible products (record the reason).
- Coverage is a floor (minimum rigor), not a cap.
- Runtime neutrality; no `Skill tool_use` in the skill; don't flatten the loop.
- Keep `check-workflow-paths` green; re-bless ddx hashes; codex-review this plan BEFORE (done: SOUND-WITH-FIXES,
  all 6 incorporated) and the diff AFTER.
