---
ddx:
  id: FEAT-016
  status: draft
  depends_on:
    - helix.prd
  review:
    self_hash: 226872932728d635279abac06206be77cee1075d787aae7760010941adb9c1e1
    deps:
      helix.prd: 2b22383538b33c6ecee57f43d85128dfef7d56254766b757aa36439e35f2bfc9
    reviewed_at: "2026-05-25T16:26:54Z"
---

# Feature Specification: FEAT-016 — Artifact Honesty (Claims-vs-Reality)

**Feature ID**: FEAT-016
**Status**: Draft
**Priority**: P0
**Owner**: HELIX maintainers

## Overview

The dominant artifact defect surfaced by adversarial review is not a missing
section — it is a **phantom claim**: a template-conformant artifact that asserts
something untrue about reality. It names a test that was never written, cites a
coverage figure no tool produced, or claims an emitted metric that nothing
emits. Template-conformance checks (FEAT-008) cannot catch this, because the
artifact is perfectly well-formed; it just lies.

FEAT-016 makes **artifact honesty** a first-class, enforced property: every
artifact assertion about a test, a coverage figure, or an emitted
metric/signal must resolve to something that actually exists. Unbacked claims
are classified `ASSERTED_UNBACKED` and gated by a zero-floor ratchet. This is
*global* artifact honesty — it spans every artifact type, not just test plans —
which is why it is its own feature rather than a clause inside FEAT-008 or
FEAT-014.

## Problem Statement

- **Current situation**: HELIX classifies acceptance criteria as `SATISFIED`,
  `TESTED_NOT_PASSING`, `UNTESTED`, or `UNIMPLEMENTED`. `UNTESTED` is *honest*
  about a gap. None of these catch an artifact that *claims* coverage it does
  not have. External reviewers repeatedly caught "the docs claim tests that
  don't exist"; HELIX did not catch it internally.
- **Pain points**:
  1. **Phantom tests** — an artifact references `tests/foo.spec.ts::bar` that is
     not in the suite.
  2. **Invented metrics** — "123 unit + 32 e2e, WCAG AA" stated with no run that
     produced those numbers.
  3. **Fabricated coverage figures** — "82% line coverage" with no coverage tool
     wired.
  4. **Conformance blindness** — a well-formed artifact passes template checks
     while asserting untruths, so the defect ships.
- **Desired outcome**: a claims-vs-reality check that verifies every such
  assertion against the implementation, test suite, or emitted telemetry, and a
  zero-floor ratchet that blocks any phantom claim from landing.

## Functional Requirements

### FR-1: ASSERTED_UNBACKED classification

The reconcile-alignment acceptance-criteria classification gains a sixth class,
`ASSERTED_UNBACKED`: an artifact *claims* a criterion is satisfied, names a test
covering it, or states a coverage figure or emitted metric, but verification
against the implementation finds no backing reality. It is a
traceability-**honesty** defect, distinct from `UNTESTED` (which is honest about
the gap).

### FR-2: Claims-vs-reality check

Every artifact assertion about a test, a coverage figure, or an emitted
metric/signal must be verified against reality: the named test exists and runs,
the figure was produced by a real measurement, the metric is actually emitted. A
claim with no backing is classified `ASSERTED_UNBACKED`.

### FR-3: Zero-floor phantom-claim ratchet

The count of `ASSERTED_UNBACKED` claims is a ratchet with a permanent floor of
**zero**. Any phantom claim is a blocking regression regardless of the
acceptance-satisfaction floor. It is resolved only by making the claim true (add
the test, emit the metric, run the measurement) or by deleting the claim from
the artifact — **never** by weakening or removing the check.

### FR-4: Enforcement points

The check runs at the same gates as the acceptance-criteria ratchet:
reconcile-alignment (Step 3 classification / Step 7 regression item), the Build
verification step, and the Check artifact-health step. Adopting projects wire
the zero-floor enforcement into the same gate as their acceptance-criteria
ratchet.

### FR-5: Scope is all artifact types

The honesty rule applies to any HELIX artifact that can assert a test, figure,
or signal — PRDs, feature specs, designs, test plans, alignment reports, and
status notes — not only test-layer artifacts.

### FR-6: Instrument integrity (honesty applied to the gates themselves)

Artifact honesty extends from artifacts to the **instruments that score them**.
A gate can lie exactly as an artifact can, and a metric read off a broken
instrument is a phantom claim about reality. Two instrument-integrity rules:

1. **Template↔meta agreement.** An artifact is scored against its `template.md`
   (the sections it must contain) and its `meta.yml` (`required_sections`,
   quality checks). When those two **disagree** — the template carries a section
   the meta does not require, or the meta requires a section the template omits
   — the conformance score they jointly produce is untrustworthy. The "prd
   scored 1/8" finding was this defect: the instrument was drifted, not the
   artifact bad. Template↔meta drift is a blocking instrument-integrity finding,
   resolved by reconciling the two — never by trusting the misleading score.
2. **Verified, reproducible measurement.** A metric definition must name a
   measurement command that has **actually been run and confirmed** to emit the
   stated value, with the run recorded in `last_verified`. An
   asserted-but-unmeasured metric — a number with no run behind it — is
   `ASSERTED_UNBACKED` exactly like a phantom test. The metric-definition
   `command_verified` quality check enforces this.

## Non-Functional Requirements

- **No new measurement infrastructure**: the check reuses the existing
  alignment classification and the ratchet pattern in `workflows/ratchets.md`.
  HELIX defines the contract; adopting projects supply the enforcement command.
- **Determinism**: a claim is `ASSERTED_UNBACKED` only when its referent is
  verifiably absent — not when verification is merely inconclusive (that stays
  `UNTESTED` or a manual-check note).

## Acceptance Criteria

| AC ID | Given | When | Then |
|-------|-------|------|------|
| FEAT-016-AC1 | an artifact naming a test that does not exist in the suite | reconcile-alignment Step 3 runs | the criterion is classified `ASSERTED_UNBACKED`, not `UNTESTED` |
| FEAT-016-AC2 | one or more `ASSERTED_UNBACKED` claims in scope | the phantom-claim ratchet evaluates | the result is a blocking regression even if the acceptance-satisfaction floor is met |
| FEAT-016-AC3 | an `ASSERTED_UNBACKED` finding | it is resolved | resolution is either making the claim true or deleting it — the check is never relaxed |
| FEAT-016-AC4 | a PRD or design (non-test artifact) that cites an invented coverage figure | the claims-vs-reality check runs | the claim is flagged `ASSERTED_UNBACKED` |
| FEAT-016-AC5 | an artifact whose `template.md` and `meta.yml` `required_sections` disagree | reconcile-alignment scores its conformance | template↔meta drift is flagged as a blocking instrument-integrity finding, not reported as a low conformance score for the artifact |
| FEAT-016-AC6 | a metric definition whose `command` was never run (no `last_verified`) | the metric-definition `command_verified` check runs | the metric is flagged `ASSERTED_UNBACKED` (asserted-but-unmeasured), not trusted as a measurement |

## Relationships

- **Cross-referenced by FEAT-008** — template quality catches *missing or
  weak* sections; FEAT-016 catches *well-formed but untrue* assertions. The two
  are complementary halves of artifact quality.
- **Cross-referenced by FEAT-014** — workflow coverage proves HELIX behaves
  correctly; FEAT-016 is the honesty property those behaviors must preserve.

## Edge Cases and Error Handling

- **Inconclusive verification** — when a claim cannot be confirmed *or* refuted
  (e.g. an external system is unavailable), it is not `ASSERTED_UNBACKED`; record
  it as a manual check.
- **Aspirational/planned claims** — a criterion marked `planned` is design
  intent, not a claim of current reality, and is not `ASSERTED_UNBACKED`.

## Success Metrics

- `ASSERTED_UNBACKED` count stays at zero on every gated change.
- Phantom-claim classes are caught internally by HELIX rather than by an
  external reviewer.

## Constraints and Assumptions

- The check is a HELIX contract, not a shipped script. Enforcement commands and
  floor fixtures live in adopting projects (consistent with `ratchets.md`).

## Dependencies

- **helix.prd** — alignment-quality and artifact-quality goals.
- **FEAT-008** — template-conformance quality (complementary; FEAT-008 cross-refs FEAT-016).
- **FEAT-014** — workflow coverage (honesty is the preserved property; FEAT-014 cross-refs FEAT-016).

## Out of Scope

- A general fact-checker for prose claims unrelated to tests/figures/metrics.
- Automatic remediation (deciding whether to write the test or delete the claim
  is human/triage work).

## References

- [Reconcile-alignment action](../../../workflows/actions/reconcile-alignment.md) — `ASSERTED_UNBACKED` classification and claims-vs-reality check
- [Quality ratchets](../../../workflows/ratchets.md) — phantom-claim zero-floor sub-ratchet
- [FEAT-008: Artifact Template Quality](FEAT-008-artifact-template-quality.md)
- [FEAT-014: Workflow Coverage](FEAT-014-workflow-coverage.md)
