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
surface on 2026-04-11.

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
| **FEAT-002** HELIX CLI | PARTIAL | The governing docs now treat `helix run` / `helix build` as compatibility surfaces over DDx-managed execution. Remaining work is implementation-proof and wrapper-correctness follow-ons (`helix-4243dd31`, `helix-ded1e007`, `helix-30814e44`, `helix-fb2ccbb1`, `helix-af902886`). |
| **FEAT-003** First-Class Principles | COMPLETE | Defaults, bootstrap, and workflow references are in place; no live queue item currently targets FEAT-003 directly. |
| **FEAT-004** Plugin Packaging | PARTIAL | `.claude-plugin/plugin.json`, `hooks/hooks.json`, `bin/helix`, and `tests/validate-skills.sh` exist; no dedicated open packaging bead is live right now, so remaining risk sits in wrapper-compatibility proof rather than package layout. |
| **FEAT-005** Execution-Backed Output | PARKED | The feature remains specified, but no current open bead is scoped directly to execution-backed output while the queue prioritizes DDx-managed execution-contract alignment. |
| **FEAT-006** Concerns & Context Digest | DIVERGENT | Concern docs and prompt references exist, but live propagation gaps remain open in the queue (`helix-674b1b42`, `helix-691d18c0`, `helix-d9f93a59`). |
| **FEAT-007** Microsite and Demos | PARTIAL | The site and demos ship, but the live queue still carries demo and public-site proof work (`helix-438c8a07`, `helix-39fc1526`, `helix-71aab0f0`). |
| **FEAT-011** Slider Autonomy | PARTIAL | `helix input` and `--autonomy` are live in `scripts/helix`; the design-layer boundary is converging and the remaining gaps are explicit follow-on beads for wrapper correctness, public contract cleanup, and proof-lane stability (`helix-f3062aa2`, `helix-4243dd31`, `helix-ded1e007`, `helix-30814e44`, `helix-fb2ccbb1`). |

## Live Queue Snapshot

Snapshot rebuilt on 2026-04-11 from `ddx bead status` plus targeted refreshes
of the DDx-execution migration chain:

- `30` open
- `28` ready
- `2` blocked

### DDx Execution-Contract Chain

| Issue | Priority | Parent | Dependency | Focus |
|-------|----------|--------|------------|-------|
| `helix-f3062aa2` | P0 | `helix-13cfe23f` | none | Align the governing planning stack and implementation plan around `execute-loop` / `execute-bead` |
| `helix-4243dd31` | P0 | `helix-13cfe23f` | `helix-f3062aa2` | Consume the bead DDx actually executed before HELIX applies bookkeeping |
| `helix-ded1e007` | P0 | `helix-13cfe23f` | `helix-f3062aa2` | Reject closed or non-ready explicit selectors before `execute-bead` dispatch |
| `helix-30814e44` | P0 | `helix-13cfe23f` | none | Reconcile stage-stance docs with wrapper model-override reality |
| `helix-fb2ccbb1` | P1 | `helix-13cfe23f` | none | Restore deterministic proof for the DDx-agent dry-run lane |
| `helix-af902886` | P1 | `helix-13cfe23f` | none | Isolate the `helix start` wrapper test from live repo state |

Recently landed decisions in this chain:

- `helix-a938e147` closed the stage-stance design question by keeping stance in
  HELIX prompts while DDx owns concrete model policy.
- Public docs and demos were moved to the `helix input` + `ddx agent execute-loop`
  default path under `helix-d903a854`; remaining work is proof and runtime drift,
  not reopening that default-path decision.

## Build Sequencing

| Order | Area | Governing Artifacts | Notes |
|-------|------|-------------------|-------|
| 1 | Redesign execution contract around DDx | FEAT-002, FEAT-011, TD-002, TD-011, CONTRACT-001, TP-002 | Land the governing-doc alignment first (`helix-f3062aa2`), then keep the remaining build beads explicitly ordered beneath the execution-contract epic so wrapper fixes implement the settled contract instead of re-deciding it in code. |
| 2 | Proof shipped entry surfaces | FEAT-002, FEAT-004, FEAT-011, TD-002, TD-003, TD-011, TP-002 | Close deterministic proof gaps for `bin/helix`, `helix input`, `execute-loop` bookkeeping, selector validation, and the DDx dry-run harness before adding more command-surface drift. |
| 3 | Make concern-aware steering real | FEAT-006, `docs/helix/01-frame/concerns.md`, concern-resolution guidance | Propagate current context digests into live beads and preserve `area:*` metadata so review-filed work re-enters the queue with the right practices. |
| 4 | Repair deploy artifact contract consistency | Deploy artifact metadata/templates, review findings | Resolve ordering contradictions and missing artifact references before extending deploy docs further. |
| 5 | Restore the public site proof lane | FEAT-007, site concerns, Playwright/Hugo verification | Fix route/search regressions and extend deterministic site coverage so the published docs lane is green again. |
| 6 | Finish design-taxonomy follow-ons | Artifact hierarchy, design artifact docs, workspace-state design work | Complete the deleted-artifact audit, first-class contract support, and workspace-state modeling before new artifact types are introduced. |
| 7 | Stage DDx tier-policy adoption behind queue-contract stabilization | DDx tier-policy/model-catalog contract | Keep `helix-81c0c0df` queued as a cross-phase follow-on while higher-priority execution-contract work lands first. |

## Verification Expectations

| Area | Required Verification |
|------|-----------------------|
| Wrapper / workflow contract changes | `bash tests/helix-cli.sh`; `git diff --check`; verify DDx alpha command help/contract assumptions against local `ddx agent execute-bead --help` and `ddx agent execute-loop --help` |
| Plugin packaging and published skill surface | `bash tests/validate-skills.sh`; plugin manifest validation; targeted wrapper/package smoke checks when plugin-surface follow-on work reopens |
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
