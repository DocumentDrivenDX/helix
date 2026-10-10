---
ddx:
  id: helix.design.formal-methods
  authoring:
    home: repo
---

# Design: Formal Methods Concern

## Scope and Authority

Implement the operator-approved proposal for an optional, composable
`formal-methods` concern. Authority is the implementation request, HELIX's
existing concern/practices resolution, and the technical-design boundary:
requirements govern behavior, shared Contracts govern exact interfaces, and
technical designs explain implementation. Bind the in-tree workflow catalog.

The deliverable is portable methodology, adoption guidance, and an executable
abstract worker-lease example. It does not modify or verify DDx runtime code.
No new exclusive slot, public skill, artifact type, universal formal gate, or
automatic migration is introduced. Existing unrelated working-tree changes
are excluded from the commit.

## Requirements and Decisions

| Requirement | Decision | Acceptance evidence |
|---|---|---|
| Optional, risk-based adoption | Select for critical interacting state/rules with costly failure; concurrency alone is insufficient | Positive and negative applicability, real concern injection tests |
| Graduated rigor | Precise specification, executable analysis, deductive proof; record scope-specific chosen level | Concern and practices distinguish evidence claims |
| Precise behavior | State, initial conditions, transitions, safety/liveness, assumptions, bounds, exclusions | Conditional TD section and reusable reference |
| Authority preserved | Derive properties from requirements; reference Contracts; reconcile contradictions | TD prompt and reference ownership rules |
| Model/code gap explicit | Map modeled actions to code/tests; mark illustrative/unmapped examples | Correspondence table and review obligations |
| Reproducible evidence | Record model/config revision, tool/version, commands, bounds and outcomes; unknown/incomplete is not pass | Evidence checklist and negative controls |
| Lifecycle propagation | Frame selection, Design analysis, Test derivation, Build correspondence, Deploy assumptions, Iterate invalidation | Activity-keyed practices and existing resolver |
| Bounded pilot | Finite two-worker lease model, fenced landing, timeout/reclaim/late return and lock lifetime | Exhaustive reachable-state exploration plus deliberate broken variants |

Use `areas: all` with explicit bounded applicability. A project selects the
concern once and records affected slices and rigor in existing Concerns fields;
unaffected slices retain applicability context and record a reason in acceptance
and evidence; that disposition satisfies propagation without an analyzer/proof
run. Tests must exercise a selected-but-unaffected item and preservation of scope
and rigor through existing Project Overrides into the digest. Do not introduce a resolver profile.
Formal analysis supplements testing and running-system verification.

## Polished Implementation Slices

This decomposition fulfills plan-first/polish for direct implementation; no
tracker mutation was requested. Each slice has concrete files and checks.

| Slice | Depends on | Files and outcome | Check |
|---|---|---|---|
| 1. Concern contract | None | `workflows/concerns/formal-methods/{concern,practices}.md`: boundaries, selection, rigor, artifact impact, evidence and drift | Review applicability, authority and assurance language |
| 2. Adoption integration | 1 | `workflows/references/formal-methods.md`, `workflows/references/concern-resolution.md`, TD template/prompt/meta: conditional obligations through existing concern mechanism | Real selected/unselected/override digest tests; catalog validation |
| 3. Executable example | 1 | `workflows/references/formal-methods/lease_model.py` and README: finite model, invariants, replayable counterexamples and assumptions | Correct variant passes; unfenced and lock-held variants report targeted violations with replayable traces via actual command |
| 4. Regression and publication | 2, 3 | `tests/test_formal_methods.py`, `justfile`, generated concern/catalog pages and published design/index (including downstream weight updates) | Focused tests, full `just test`, generated reference, diff check, pre-commit |

## Pilot Boundaries

Model one bead, two workers, at most two claims using monotonically increasing
attempt tokens, abstract atomic tracker/git mutations, and interleaved harness
wait/return/timeout. The bound permits claim A, expire A, claim B, return A.
Check exclusive valid ownership, stale landing rejection and no mutation lock
across a harness wait. Explore all reachable states without a depth cutoff.
Counterexample traces must be replayable through the same transition relation.
Track each worker's token separately from authoritative lease validity; exclusive
ownership is a representation invariant, while stale landing compares the
returning token and validity with current authority. Require reachable witnesses
for valid landing and claim A → expire A → claim B → late return A. A checker
error or incomplete exploration is a distinct outcome, never a property violation
or pass. Verify packaged model presence and execution from the catalog floor.

Timeout release is an enabled modeled transition, not a proof of eventual
release in production. Real clocks, crashes, file locks, external side effects,
watchdog scheduling, and repeated-wedge parking are excluded. Document liveness
properties and required fairness assumptions as unverified obligations; do not
claim safety enumeration proves them. Measure pilot state counts, shortest
counterexamples, runtime, and discovered specification gaps. A real DDx adoption
would separately map the model to implementation and exercise regressions.

## Review and Verification

Before implementation, request an Astra Ultra adversarial review of this plan.
Resolve blocking findings and explicitly disposition warnings. After implementation,
request Astra Ultra review against this design, the complete scoped diff and
recorded check results. Repair material findings and re-review as needed.
Keep review outcomes in this document; do not infer approval from silence.

Required gates: `python3 tests/test_formal_methods.py`, `just test`,
`git diff --check`, and enabled pre-commit checks. Regenerate the website reference
from canonical source, retaining only this scope's generated changes. Do not
overwrite or commit unrelated templates, graph changes, or user files.

## Risks and Rollback

Over-selection is controlled by concrete risk signals and explicit exclusions.
False assurance is controlled by bounded claims, vacuity checks, negative
controls, and a correspondence obligation. Model drift invalidates previous
evidence on affected changes. Heavy tooling is chosen per project, never added
as a HELIX installation dependency. Rollback is a normal revert of this additive
change, preserving history and unrelated work.

## Plan Review Disposition

Astra Ultra round 1 requested changes: targeted mutant failures and positive
reachability witnesses; explicit selected-but-unaffected propagation. Both are
now acceptance obligations above. Warnings on scalar-owner vacuity and dirty
generation are addressed by separate worker tokens/validity, explicit property
limits, a saved baseline diff/status, targeted publication, and scoped staging.
The pilot moved under shared references so installation bundles carry it.

Astra Ultra round 2 approved the amended plan with no remaining blocking
findings. Implementation follows the four slices above.

## Implementation Evidence

Astra Ultra's final implementation review approved the scoped change with no
blocking findings. Two warnings were fixed and re-reviewed: specification-only
rigor now explicitly needs semantic review rather than an analyzer/negative
control run, and regression assertions compare the real model hash and complete
serialized replay states. The follow-up verdict was APPROVE.

Observed pilot: safe variant completed all 70 reachable states and 109
transitions with no safety violations and all three replayed witnesses. The
unfenced variant violated `stale_landing_rejected` with a five-action trace;
lock-held violated `no_lock_across_wait` with a two-action trace. Liveness remains
NOT_CHECKED and production correspondence UNMAPPED. These are model results,
not a DDx runtime verification claim.

`python3 tests/test_formal_methods.py` passed all eight tests, including selected,
unselected, override, unaffected-slice and installed-floor cases. A full
`just test` run against committed HELIX plus only this scope passed (exit 0),
using the existing Python environment with PyYAML. Optional deck rendering and
signing lanes reported skips because their tools were unavailable; those results
are not claimed as verified. The combined working tree still fails the same
preexisting migration-design example identifier check seen in the baseline.
Its 21 preexisting changed files remain byte-identical to the preservation
baseline. No unrelated tracker, template, graph or slot changes are included.

Website output is generated from canonical sources: formal concern/index,
changed Concerns/TD catalog pages, and this published design/index. Adding a
published design requires weight-only updates to later generated artifacts.
Formal metadata checks are semantic review obligations, not automated theorem
proving or a newly implemented instance-validator rule.

Astra Ultra approved all 41 final scoped paths after publication review, with
no outstanding findings. All 26 changed website projections match fresh
canonical generation on the isolated scoped tree. `git diff --cached --check`
and enabled `lefthook run pre-commit` passed. The existing advisory CC revalidation
hook reports a missing retired script but is non-blocking by its configured rule.
