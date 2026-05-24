---
ddx:
  id: ADR-003
  depends_on:
    - helix.prd
    - FEAT-011
---
# ADR-003: Autonomy is a Three-Position Spectrum, Not a Fixed Level

| Date | Status | Deciders | Related | Confidence |
|------|--------|----------|---------|------------|
| 2026-05-24 | Proposed | HELIX maintainers | FEAT-011, TD-011, PRD | High |

## Context

| Aspect | Description |
|--------|-------------|
| Problem | A max-autonomy "one-shot a working app" build showed HELIX needs a governed way to say *how much* a runtime should pause for human confirmation. The `low`/`medium`/`high` vocabulary already existed in `workflows/actions/input.md`, but the governing feature (FEAT-011) and design (TD-011) were removed in the scope collapse (823aa1ac), so the policy was dangling and unauditable. |
| Current State | The PRD now states autonomy is "a first-class, controllable spectrum (review-every-edit → full one-shot)" and that HELIX "will not flatten the seven-activity loop into one generic prompt." Nothing recorded *why* the spectrum has exactly three positions, how the active level is resolved, or what a high-autonomy run may never do. |
| Requirements | HELIX must express an autonomy policy that a capable runtime honors, with a fixed vocabulary, a deterministic resolution order, and two invariants: a hard stop no level may pass, and a guarantee that autonomy never collapses the activity loop. The policy must be runtime-neutral — no `CLAUDE.md` dependency, no runtime config schema. |

## Decision

We adopt a **three-position autonomy spectrum** — `low`, `medium`, `high`,
default `medium` — that controls **checkpoint density only**. The level changes
how often a workflow pauses for confirmation; it never changes which activities
run or whether a hard stop is honored.

We fix the resolution precedence as: **per-invocation override → governing
artifact frontmatter / project policy → runtime default (`medium`)**. The
autonomy signal lives only in runtime-neutral artifacts. `CLAUDE.md` and
runtime-specific instruction files are explicitly excluded from the chain.

We bind two invariants to every level:

- **Hard stop** — true higher/equal-authority contradictions, unauthorized
  destructive actions, and human-only decisions stop the workflow at any level.
  High autonomy raises the *pause* threshold, never the *stop* floor.
- **Never collapse the loop** — autonomy changes pause frequency, not the
  seven-activity loop. A high-autonomy run executes the same activities a
  low-autonomy run would.

At `high`, a workflow additionally **infers concern selection** when none is
declared, recording the inference as an assumption rather than pausing to ask.

**Key Points**: three fixed positions | precedence chain excludes CLAUDE.md |
checkpoint density only | hard stop + never-collapse-loop invariants | high
autonomy infers concerns

## Alternatives

| Option | Pros | Cons | Evaluation |
|--------|------|------|------------|
| Single fixed behavior (always-ask or always-autonomous) | Simplest to describe | Contradicts the PRD spectrum goal; unusable for both learning and one-shot contexts | Rejected: PRD requires a spectrum |
| Numeric/continuous slider (0–100) | Fine-grained | No meaningful semantics per value; impossible to test deterministically; invites per-step bikeshedding | Rejected: three positions are testable and sufficient |
| New vocabulary (`ask-first`/`guided`/`yolo`) | Evocative | Forks the existing `low`/`medium`/`high` already used in `input.md`, creating drift | Rejected: reuse the established vocabulary |
| Store autonomy in `CLAUDE.md` / runtime config | Convenient per-runtime | Breaks runtime-neutrality (PRD R-4); same project would behave differently across runtimes | Rejected: signal must be runtime-neutral |
| **Three positions, precedence chain, two invariants** | Reuses existing vocab, testable, runtime-neutral, auditable | Requires restoring FEAT-011/TD-011 and re-blessing CONTRACT-002 | **Selected: smallest governed policy that satisfies the PRD** |

## Consequences

| Type | Impact |
|------|--------|
| Positive | The autonomy policy is governed, auditable, and ratchet-able instead of dangling. |
| Positive | The same project behaves identically across runtimes because the signal is runtime-neutral. |
| Positive | High autonomy becomes safe to use: the hard-stop and never-collapse-loop invariants bound what it may do. |
| Positive | Concern inference at high autonomy turns the previously inert concerns library into a default behavior. |
| Negative | Every action that can pause must resolve the level at bootstrap — a small recurring authoring cost. |
| Neutral | HELIX still ships no execution engine; the runtime supplies the agency the policy describes. |

## Risks

| Risk | Prob | Impact | Mitigation |
|------|------|--------|------------|
| "More autonomy" is read as "skip activities" | M | H | FR-5 never-collapse-loop invariant stated in FEAT-011, TD-011, skill, and here |
| Autonomy signal leaks into CLAUDE.md | M | M | Precedence chain explicitly excludes it; runtime-neutrality is a PRD-measured metric |
| Inferred concerns diverge from real needs | M | M | Inference recorded as an assumption; alignment review flags drift |
| High autonomy bypasses a true contradiction | L | H | Hard-stop invariant applies at every level; tested via the workflow-coverage harness |

## Validation

| Success Metric | Review Trigger |
|----------------|----------------|
| No dangling FEAT-011 / TD-011 references remain | Any action or contract still cites a missing autonomy artifact |
| Active level resolves deterministically by the precedence chain | An action resolves autonomy from `CLAUDE.md` or a runtime config |
| High-autonomy runs infer concerns and still honor hard stops | A high-autonomy run overwrites `concerns.md` or passes a hard stop |
| Every required activity runs at every level | A high-autonomy run skips an activity or flattens the loop |

## References

- [PRD](../../01-frame/prd.md) — autonomy spectrum goal and seven-activity-loop guarantee
- [FEAT-011: Slider Autonomy](../../01-frame/features/FEAT-011-slider-autonomy.md)
- [TD-011: Slider Autonomy Implementation](../technical-designs/TD-011-slider-autonomy-implementation.md)
- [Input action](../../../workflows/actions/input.md)
