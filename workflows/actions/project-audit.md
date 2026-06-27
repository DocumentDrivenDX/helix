# HELIX Action: Project Audit

You are answering one operator question on entry to a project with stale context:
**where does this project actually stand?** Are the specs aligned with the
implementation, is the implementation complete, is it well tested, and are the
tests aligned with the acceptance criteria — and therefore, what is the next safe
action?

Project-audit is a **composition entry-point**, not a new analysis. It runs the
existing health and alignment actions and synthesizes one state report with a
recommended next mode. It does not re-implement what `check` and
`reconcile-alignment` already do.

## Action Input

You may receive:

- an optional **scope** (a feature, an area, or the whole project — default: whole
  project)
- `--quick` to run only the artifact-health pass (`check`) and skip the deeper
  acceptance-criteria reconciliation, when a fast orientation is enough

## Authority Hierarchy

1. Product Vision
2. Product Requirements
3. Feature Specs / User Stories
4. Architecture / ADRs
5. Solution / Technical Designs
6. Test Plans / Tests
7. Implementation Plans
8. Source Code / Build Artifacts

## STEP 0 - Bootstrap

0. **Context Recovery**: Re-read AGENTS.md so project instructions are fresh.
1. Resolve the project HELIX root and the audit scope. If no HELIX docs exist at
   all, this is not an audit target — route to `genesis` (new project) or
   `backfill` (undocumented existing code) and say so.

## STEP 1 - Artifact Health (compose `check`)

Run the `check` action over the scope to assess artifact health: which artifacts
exist, which are stale or missing, ratchet status and trend, and whether the
artifact graph is internally consistent. Carry its **findings** forward — do not
restate the `check` contract here.

`check` emits a mandatory `NEXT_ACTION:` decision code as its first line. Project-
audit consumes check's analysis as **intermediate input**, not as the verdict: the
synthesized `NEXT:` in STEP 3 (which also weighs the alignment pass) is the
operative recommendation and supersedes check's `NEXT_ACTION:` when they differ.

## STEP 2 - Spec ↔ Implementation ↔ Test Alignment (compose `reconcile-alignment`)

Unless `--quick`: run `reconcile-alignment` over the scope to answer the alignment
questions directly:

- **Specs aligned with implementation?** — does the code match what the governing
  artifacts say, or has one drifted from the other?
- **Implementation complete?** — every governing acceptance criterion implemented,
  or are there UNIMPLEMENTED / stubbed paths (the `scope-discipline` hollow-path
  signal)?
- **Well tested?** — acceptance criteria classified SATISFIED vs. TESTED_NOT_
  PASSING / UNTESTED, and any `ASSERTED_UNBACKED` phantom claims (a doc claiming a
  test that does not exist).
- **Tests aligned with the ACs?** — do the tests that exist actually exercise the
  criteria they claim, or are they testing something adjacent?

Carry `reconcile-alignment`'s classifications forward; do not duplicate its steps.

## STEP 3 - Synthesize State + Next Action

From the two passes, produce one **state report**:

- the health summary (artifacts present/stale/missing, ratchet trend)
- the alignment summary (AC satisfaction counts, drift found, phantom claims,
  hollow/stubbed paths)
- the single most important gap, and the **recommended next mode** to close it
  (e.g. `evolve` if specs are stale, `frame`/`design` if authority is missing,
  the runtime build loop if ready work exists, `converge` if recent work is
  unreviewed, `decompose-module` if a god-file dominates).

The audit **reports**; it does not fix. Its output is the orientation that tells
the operator (or the next action) what to do — fixing is the recommended mode's
job.

## Output

Report:

1. Scope audited and whether `--quick` was used.
2. Artifact-health summary (from `check`).
3. Alignment summary (from `reconcile-alignment`): AC satisfaction, drift,
   phantom claims, hollow paths.
4. The top gap and the recommended next mode.

Then emit the machine-readable trailer:

```
AUDIT_STATUS: HEALTHY|DRIFTED|INCOMPLETE|BLOCKED
SCOPE: <scope>
ARTIFACTS_STALE: N
AC_SATISFIED: N/M
PHANTOM_CLAIMS: N
NEXT: <recommended-mode>
```

- `HEALTHY`: artifacts current, ACs largely satisfied, no phantom claims — next is
  normally continued execution.
- `DRIFTED`: specs and implementation diverge — next is normally `evolve` or
  `align`.
- `INCOMPLETE`: governing ACs unimplemented/untested, or hollow paths — next is
  normally the build loop or `converge`.
- `BLOCKED`: no HELIX docs to audit — next is `genesis` or `backfill`.

## Runtime Integration Appendix

- Project-audit composes `check` (STEP 1) and `reconcile-alignment` (STEP 2) and
  writes no new artifact type — its synthesis can be recorded as an
  alignment-review note (`docs/helix/06-iterate/alignment-reviews/`) when a durable
  record is wanted.
- It is the orientation entry-point for a project with stale context; the actions
  it recommends own the actual changes.
