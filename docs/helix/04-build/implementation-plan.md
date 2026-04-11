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

This build plan defines the current HELIX execution landscape: which features
are implemented, which have remaining work, what the governing artifacts are,
and what ordering constraints keep implementation aligned with the authority
stack.

**Governing Artifacts**:
- `docs/helix/01-frame/prd.md`
- `docs/helix/01-frame/concerns.md`
- `docs/helix/01-frame/features/FEAT-001-helix-supervisory-control.md`
- `docs/helix/01-frame/features/FEAT-002-helix-cli.md`
- `docs/helix/01-frame/features/FEAT-003-principles.md`
- `docs/helix/01-frame/features/FEAT-004-plugin-packaging.md`
- `docs/helix/01-frame/features/FEAT-005-execution-backed-output.md`
- `docs/helix/01-frame/features/FEAT-006-concerns-practices-context-digest.md`
- `docs/helix/01-frame/features/FEAT-007-microsite-and-demos.md`
- `docs/helix/01-frame/features/FEAT-011-slider-autonomy.md`
- `docs/helix/02-design/adr/ADR-001-supervisory-control-model.md`
- `docs/helix/02-design/solution-designs/SD-001-helix-supervisory-control.md`
- `docs/helix/02-design/solution-designs/SD-002-first-class-principles.md`
- `docs/helix/02-design/technical-designs/TD-002-helix-cli.md`
- `docs/helix/02-design/technical-designs/TD-003-helix-start-stop.md`
- `docs/helix/02-design/technical-designs/TD-011-slider-autonomy-implementation.md`
- `docs/helix/02-design/contracts/API-001-helix-tracker-mutation.md`
- `docs/helix/03-test/test-plans/TP-002-helix-cli.md`
- `workflows/README.md`
- `workflows/EXECUTION.md`
- `workflows/REFERENCE.md`

## Shared Constraints

- Keep execution tracker-first. Active work must be selected, claimed,
  revalidated, and closed through `ddx bead`.
- Keep `spec-id` anchored to the nearest governing artifact.
- Limit implementation to bounded slices that satisfy documented acceptance and
  deterministic verification. Do not fold design reconciliation or new product
  scope into build issues.
- Shape execution-ready work for DDx-managed queue draining: use explicit
  parents for grouped work, explicit dependencies for hard ordering, and
  measurable success criteria that let automation determine merge-and-close
  without hidden operator policy.
- Treat this plan as a queue snapshot, not a static roadmap. Rebuild it from
  `ddx bead status`, `ddx bead list --status open --json`, and
  `bash scripts/helix help` whenever tracker state or command surface changes.
- Use the proof lane for HELIX contract changes:
  `bash tests/helix-cli.sh`, `bash tests/validate-skills.sh`, and
  `git diff --check`.

## Current Command Surface

Validated against `bash scripts/helix help` and the local DDx alpha command
surface on 2026-04-10.

- Intake and planning: `input`, `frame`, `design`, `polish`, `triage`,
  `evolve`
- Execution and review: `run`, `build`, `check`, `align`, `backfill`,
  `review`, `experiment`, `next`
- Operator and packaging: `start`, `stop`, `status`, `commit`, `doctor`,
  `ddx bead`, `help`
- DDx execution substrate now available locally: `ddx agent execute-bead`
  (functional alpha) and `ddx agent execute-loop` (new queue-drain contract)
- HELIX command surfaces are increasingly entrypoints to prompts, policy, and
  compatibility behavior rather than the canonical owner of queue draining

## Feature Status

| Feature | Status | Current State / Remaining Work |
|---------|--------|--------------------------------|
| **FEAT-001** Supervisory Control | ALIGNED | Core bounded supervision remains governed by `TD-002` and `TP-002`, but the execution substrate boundary is shifting downward into DDx. |
| **FEAT-002** HELIX CLI | PARTIAL | `scripts/helix` exposes the expected command surface, but the governing plan must now converge on DDx-managed execution (`execute-bead`, then `execute-loop`) instead of treating wrapper-owned claim/close mechanics as the long-term contract. |
| **FEAT-003** First-Class Principles | COMPLETE | Defaults, bootstrap, and workflow references are in place; no live queue item currently targets FEAT-003 directly. |
| **FEAT-004** Plugin Packaging | PARTIAL | `.claude-plugin/plugin.json`, `hooks/hooks.json`, `bin/helix`, and `tests/validate-skills.sh` exist; the remaining gap is deterministic delegation coverage for the plugin wrapper (`helix-0d48272d`). |
| **FEAT-005** Execution-Backed Output | PARKED | The feature remains specified, but the prior blocked epic `helix-4dec7483` is already closed and no current open bead is carrying this work in the live queue snapshot. |
| **FEAT-006** Concerns & Context Digest | DIVERGENT | Concern docs and prompt references exist, but live bead propagation and area-label preservation are still open (`helix-7b3c6980`, `helix-3ad4ba25`). |
| **FEAT-007** Microsite and Demos | PARTIAL | The site and demos ship, but the current queue still carries route/search and Playwright coverage fixes (`helix-ae94e347`, `helix-f58a8717`). |
| **FEAT-011** Slider Autonomy | PARTIAL | `helix input` and `--autonomy` are live in `scripts/helix`; the current design now assumes DDx-managed queue drain (`execute-loop`) with `execute-bead` underneath, and the migration path remains open work. |

## Live Queue Snapshot

Snapshot rebuilt on 2026-04-10 from the open queue that remains after this
refresh bead closes:

- `27` open
- `27` ready
- `0` blocked

### Build backlog

| Issue | Priority | Focus |
|-------|----------|-------|
| `helix-0d48272d` | P0 | Add deterministic coverage for `bin/helix` delegation |
| `helix-11c498d6` | P0 | Fix secondary ADR discovery in the context-digest helper |
| `helix-15eff7dc` | P0 | Align monitoring-setup runbook contract with deploy ordering |
| `helix-19a0b99a` | P0 | Preserve override-specific digest guidance when the first bullet duplicates library content |
| `helix-268c54ee` | P0 | Reconcile the implementation-plan command surface with `bash scripts/helix help` |
| `helix-3ad4ba25` | P0 | Preserve `area:*` labels on review-filed findings |
| `helix-3c960e4b` | P0 | Add deterministic verification for `helix input` intake flow |
| `helix-414fe238` | P0 | Update the deploy phase glossary for the restored `release-notes` contract |
| `helix-41b86771` | P0 | Remove or restore deleted artifact types still named in supporting docs |
| `helix-512324ed` | P0 | Define story-keyed iterate evidence before retiring shared-IR state detection |
| `helix-6f9f8081` | P0 | Add deterministic validation for deploy artifact order consistency |
| `helix-ae94e347` | P0 | Fix broken glossary route in site search output |
| `helix-b7f0c18a` | P0 | Add deterministic coverage for deploy artifact order consistency |
| `helix-c1466715` | P0 | Align the deploy README with the restored `release-notes` contract |
| `helix-ef1cc923` | P0 | Prevent every story from matching ITERATE once `docs/helix/06-iterate/` exists |
| `helix-f58a8717` | P0 | Add Playwright coverage for microsite search workflow |
| `helix-f6c2b3a6` | P0 | Require `release-notes` in the deploy gate |
| `helix-fb2ccbb1` | P1 | Fix the `ddx-agent` dry-run hang in `tests/helix-cli.sh` |
| `hx-89d8e016` | P0 | Restore `security-metrics` in iterate state-machine artifacts |
| `hx-98076461` | P0 | Remove stale build-procedures reference in `docs/README.md` |
| `hx-f34fcaf1` | P0 | Close bead `helix-2a702709` after completed work |

### Design backlog

| Issue | Priority | Focus |
|-------|----------|-------|
| `helix-004375e5` | P0 | Review deleted artifact type: `gtm-plan` |
| `helix-05fa7338` | P0 | Review deleted artifact type: `launch-checklist` |
| `helix-1940a77b` | P2 | Add first-class contract artifact support in design |
| `helix-dd21cbaa` | P0 | Define the workspace-state transformation model for beads |
| `helix-fef22846` | P0 | Audit deleted HELIX artifact types for restoration or retirement |

### Blocked backlog

| Issue | Priority | Focus |
|-------|----------|-------|
| `helix-81c0c0df` | P1 | Blocked DDx tier-policy integration for model selection |

## Build Sequencing

| Order | Area | Governing Artifacts | Notes |
|-------|------|-------------------|-------|
| 1 | Redesign execution contract around DDx | FEAT-002, FEAT-011, TD-002, TD-011, CONTRACT-001, TP-002 | Align governing docs so HELIX supervision delegates managed execution to DDx, with `execute-loop` as the queue-drain contract and `execute-bead` as the bounded primitive. Decide which HELIX entry surfaces remain worth keeping once direct agent-plus-tracker use is common. |
| 2 | Proof shipped entry surfaces | FEAT-002, FEAT-004, FEAT-011, TD-002, TD-003, TD-011, TP-002 | Close deterministic proof gaps for `bin/helix`, `helix input`, and the dry-run harness before adding more command-surface drift. |
| 3 | Make concern-aware steering real | FEAT-006, `docs/helix/01-frame/concerns.md`, concern-resolution guidance | Propagate current context digests into live beads and preserve `area:*` metadata so review-filed work re-enters the queue with the right practices. |
| 4 | Repair deploy artifact contract consistency | Deploy artifact metadata/templates, review findings | Resolve ordering contradictions and missing artifact references before extending deploy docs further. |
| 5 | Restore the public site proof lane | FEAT-007, site concerns, Playwright/Hugo verification | Fix route/search regressions and extend deterministic site coverage so the published docs lane is green again. |
| 6 | Finish design-taxonomy follow-ons | Artifact hierarchy, design artifact docs, workspace-state design work | Complete the deleted-artifact audit, first-class contract support, and workspace-state modeling before new artifact types are introduced. |
| 7 | Defer blocked platform-policy work | DDx tier-policy/model-catalog contract | `helix-81c0c0df` remains blocked until DDx-side policy ownership is ready to consume. |

## Verification Expectations

| Area | Required Verification |
|------|-----------------------|
| Wrapper / workflow contract changes | `bash tests/helix-cli.sh`; `git diff --check`; verify DDx alpha command help/contract assumptions against local `ddx agent execute-bead --help` and `ddx agent execute-loop --help` |
| Plugin packaging and published skill surface | `bash tests/validate-skills.sh`; plugin manifest validation; deterministic `bin/helix` delegation coverage once `helix-0d48272d` lands |
| Concern / digest propagation | Targeted `ddx bead show` / `ddx bead list --status open --json` spot checks on updated beads; confirm explicit parents/dependencies on newly ordered follow-on work; `git diff --check` |
| Site / demo changes | `hugo --gc --minify` and `npx playwright test` under `website/`; `git diff --check` |
| Queue-refresh and doc-only updates | `git diff --check`; cross-check against `ddx bead status`, `ddx bead list --status open --json`, and `bash scripts/helix help` |

## Quality Gates

- [ ] Failing or governing tests exist before implementation starts for code changes.
- [ ] All required HELIX verification commands pass before a build issue closes.
- [ ] Issue metadata cites the governing artifacts and this build plan.
- [ ] Behavior or contract changes update the canonical HELIX docs explicitly.
- [ ] Follow-on work outside the current issue scope is captured as new tracker
      issues instead of absorbed silently.

## Risks

| Risk | Impact | Response |
|------|--------|----------|
| Queue state changes faster than docs do | Medium | Rebuild this plan from live `ddx bead` output whenever it is used to steer a new implementation pass. |
| FEAT-006 propagation can touch many live beads at once | Medium | Keep changes bounded by area, verify with tracker spot checks, and file follow-on beads instead of bulk-fixing unrelated drift. |
| FEAT-007 public-site proof remains partially red | Medium | Treat site verification failures as real backlog, not as tolerated noise; keep Hugo and Playwright in the proof lane for any site work. |
| FEAT-011 exposes shipped intake surfaces before deterministic proof is complete | Medium | Land harness coverage before expanding the `helix input` behavior further. |

## Exit Criteria

- [ ] Current open issues are sequenced with explicit governing artifacts and
      dependencies.
- [ ] This plan reflects the live tracker queue (no stale issue references).
- [ ] Verification expectations are explicit enough for bounded issue closure.
