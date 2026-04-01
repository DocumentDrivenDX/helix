---
dun:
  id: helix.implementation-plan
  depends_on:
    - helix.workflow
    - TP-002
    - TD-002
---
# Implementation Plan

## Scope

This build plan defines the current HELIX execution slices that are safe to
implement from the tracker, the governing artifacts each slice must satisfy,
and the ordering constraints that keep implementation aligned with the HELIX
authority stack.

**Governing Artifacts**:
- `docs/helix/01-frame/prd.md`
- `docs/helix/01-frame/features/FEAT-001-helix-supervisory-control.md`
- `docs/helix/01-frame/features/FEAT-002-helix-cli.md`
- `docs/helix/02-design/adr/ADR-001-supervisory-control-model.md`
- `docs/helix/02-design/solution-designs/SD-001-helix-supervisory-control.md`
- `docs/helix/02-design/technical-designs/TD-002-helix-cli.md`
- `docs/helix/03-test/test-plans/TP-002-helix-cli.md`
- `workflows/README.md`
- `workflows/EXECUTION.md`
- `workflows/TRACKER.md`

## Shared Constraints

- Keep execution tracker-first. Active work must be selected, claimed,
  revalidated, and closed through `helix tracker`.
- Keep `spec-id` anchored to the nearest governing artifact. Use issue
  descriptions or notes to cite this build plan in addition to upstream
  feature, design, and test references.
- Limit implementation to bounded slices that satisfy documented acceptance and
  deterministic verification. Do not fold design reconciliation or new product
  scope into build issues.
- Treat concurrent tracker or governing-artifact edits as material input.
  Re-read selected issues immediately before claim and before close.
- Use the maintained proof lane for HELIX contract changes:
  `bash tests/helix-cli.sh`, `bash tests/validate-skills.sh`, and
  `git diff --check`.

## Build Sequencing

| Order | Story / Area | Governing Artifacts | Depends On | Notes |
|------|---------------|---------------------|------------|-------|
| 1 | Repository build-plan foundation (`hx-f8bfa352`) | `workflows/README.md`, `workflows/TRACKER.md`, `TP-002`, this plan | None | Establish the missing canonical implementation-plan layer so later build issues can cite an authoritative 04-build artifact. |
| 2 | CLI review-status handling (`hx-c2c1557c`) | `FEAT-002`, `TD-002`, `TP-002`, this plan | 1 | Safe current execution slice. Must parse machine-readable review status and stop or redirect on findings. |
| 3 | Supervisory contract runtime follow-through (future build slice after `hx-a039f874`) | `helix.prd`, `FEAT-001`, `ADR-001`, `SD-001`, updated workflow contract, new or expanded tests | `hx-a039f874` closed, required test issue(s) ready | Do not implement broader supervisory behavior until the design-phase contract drift issue is resolved and concrete build/test slices exist. |

## Issue Decomposition

Story-level work is tracked via `helix tracker` in `.helix/issues.jsonl`.

**Per-issue requirements**:
- Labels must encode HELIX execution semantics, including `helix`,
  `phase:build`, and the appropriate area or feature labels.
- `spec-id` must point at the nearest governing artifact such as `TD-002` or
  a canonical workflow doc when the issue is documentation-only.
- `description` should list the full governing stack, including this build plan
  when the issue is an implementation slice covered here.
- Dependencies must be encoded with `helix tracker dep add`, not implied in
  prose alone.
- Acceptance must name deterministic verification expectations before the issue
  is claimed for execution.

| Story / Area | Goal | Dependencies |
|--------------|------|--------------|
| Repository build-plan foundation (`hx-f8bfa352`) | Create the missing `docs/helix/04-build/implementation-plan.md` artifact and define current execution ordering. | None |
| FEAT-002 review handling (`hx-c2c1557c`) | Make `helix run` interpret machine-readable review results safely and prove the behavior in deterministic tests. | Build plan present; governed by `TD-002` and `TP-002`. |
| FEAT-001 supervisory contract follow-through | Land future bounded build slices only after workflow/design reconciliation defines the exact runtime and test contract. | `hx-a039f874` or equivalent design/test refinement work. |

## Verification Expectations

| Slice | Required Verification |
|-------|-----------------------|
| Repository build-plan foundation | `bash tests/helix-cli.sh`; `bash tests/validate-skills.sh`; `git diff --check` |
| FEAT-002 review handling | `bash tests/helix-cli.sh`; focused inspection of review-handling cases in `tests/helix-cli.sh`; `git diff --check` |
| Future supervisory runtime slices | Canonical wrapper harness plus any new deterministic design-trigger coverage required by the governing test plan |

## Quality Gates

- [ ] Failing or governing tests exist before implementation starts for code changes.
- [ ] All required HELIX verification commands pass before a build issue closes.
- [ ] Issue metadata cites the governing artifacts and, when applicable, this
      build plan.
- [ ] Behavior or contract changes update the canonical HELIX docs explicitly.
- [ ] Follow-on work outside the current issue scope is captured as new tracker
      issues instead of absorbed silently.

## Risks

| Risk | Impact | Response |
|------|--------|----------|
| Runtime work lands against stale workflow contract docs | High | Keep broader supervisory runtime work blocked on design reconciliation issue `hx-a039f874`. |
| Build issues cite only one artifact and lose traceability to the full authority stack | Medium | Require descriptions or notes to list the feature, design, test, and implementation-plan references together. |
| Concurrent refinement changes issue structure during execution | High | Revalidate immediately before claim and before close, and refuse stale claim/close behavior. |

## Exit Criteria

- [ ] `docs/helix/04-build/implementation-plan.md` exists as the canonical
      04-build artifact.
- [ ] Current ready build work is sequenced against governing requirements,
      designs, tests, and tracker dependencies.
- [ ] Open implementation issues that fit this plan cite it alongside their
      nearer governing artifacts.
- [ ] Verification expectations are explicit enough for bounded issue closure.
