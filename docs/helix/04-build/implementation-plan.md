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
| **FEAT-004** Plugin Packaging | PARTIAL | `.claude-plugin/plugin.json`, `hooks/hooks.json`, `bin/helix`, and `tests/validate-skills.sh` exist; no dedicated open packaging bead is live right now, so remaining risk sits in wrapper-compatibility proof rather than package layout. |
| **FEAT-005** Execution-Backed Output | PARKED | The feature remains specified, but no current open bead is scoped directly to execution-backed output while the queue prioritizes DDx-managed execution-contract alignment. |
| **FEAT-006** Concerns & Context Digest | DIVERGENT | Concern docs and prompt references exist, but live propagation gaps remain open in the queue (`helix-674b1b42`, `helix-691d18c0`, `helix-d9f93a59`). |
| **FEAT-007** Microsite and Demos | PARTIAL | The site and demos ship, but the live queue still carries demo and public-site drift fixes (`helix-438c8a07`, `helix-7d158bdf`, `helix-d903a854`). |
| **FEAT-011** Slider Autonomy | PARTIAL | `helix input` and `--autonomy` are live in `scripts/helix`; the current queue is still converging the DDx-managed execution model across design and wrapper behavior (`helix-13cfe23f`, `helix-a938e147`, `helix-4243dd31`, `helix-ded1e007`). |

## Live Queue Snapshot

Snapshot rebuilt on 2026-04-10 from `ddx bead status` and
`ddx bead list --status open --json` after `helix-c3ff5fdf` moved to
`in_progress` for this refresh pass:

- `28` open
- `26` ready
- `2` blocked

### Ready build backlog

| Issue | Priority | Focus |
|-------|----------|-------|
| `helix-09f1b7ca` | P0 | Align the iterate gate tracker path with the built-in bead store |
| `helix-1356be0a` | P0 | Remove the stale "every issue is execution-ready" claim from triage |
| `helix-4243dd31` | P0 | Preserve the actual DDx-executed bead across `execute-loop` bookkeeping |
| `helix-438c8a07` | P0 | Update the `helix-concerns` demo finding command to include area labels |
| `helix-66c50c8e` | P0 | Reconcile `docs/README.md` legacy-structure claims with the live repo |
| `helix-674b1b42` | P0 | Restore scope area labels and concern context on new align beads |
| `helix-691d18c0` | P0 | Support project-local custom concerns during digest refresh |
| `helix-7d158bdf` | P0 | Make Pages demo recording fail when wrapped demo commands fail |
| `helix-bec526ad` | P0 | Reclaim reused in-progress governing beads during align execution |
| `helix-c28ea8af` | P0 | Align `HELIX_TRACKER_DIR` defaults with the built-in bead store |
| `helix-cd418cd7` | P0 | Align `monitoring-setup` docs with the optional runbook contract |
| `helix-d2146c63` | P0 | Align `workflows/DDX.md` deploy row with the four-surface contract |
| `helix-d903a854` | P0 | Update public quickstarts and demos for the DDx queue-drain default |
| `helix-d9f93a59` | P0 | Allow explicit digest-omission rationale in the validator |
| `helix-ded1e007` | P0 | Reject closed or non-ready explicit selectors before `helix build` dispatch |
| `helix-e3988823` | P0 | Point `docs/README.md` workflow references at `workflows/references/` |
| `helix-5129f35d` | P1 | Resolve CRM request scope against the current HELIX repo vision |
| `helix-9230fd5b` | P1 | Frame greenfield CRM scope from sparse intake |
| `helix-af902886` | P1 | Isolate the `helix start` wrapper test from live repo state |
| `helix-db7d13a9` | P1 | Govern the sparse "Design a CRM" intake without drifting repo scope |
| `helix-fb2ccbb1` | P1 | Fix the `ddx-agent` dry-run hang in `tests/helix-cli.sh` |

### Design backlog

| Issue | Priority | Focus |
|-------|----------|-------|
| `helix-13cfe23f` | P0 | Align HELIX execution docs to shipped `ddx agent execute-loop` / `execute-bead` |
| `helix-a938e147` | P0 | Decide whether HELIX exposes stage personalities over DDx-managed execution |
| `helix-1940a77b` | P2 | Add first-class contract artifact support in design |

### Frame backlog

| Issue | Priority | Focus |
|-------|----------|-------|
| `helix-dfddd64b` | P1 | Clarify the CRM intake target before creating frame/design artifacts |

### Blocked backlog

| Issue | Priority | Focus |
|-------|----------|-------|
| `helix-7e8a9c4b` | P2 | Decompose CRM design into execution-ready beads once upstream CRM planning is ready |
| `helix-8944c622` | P2 | Draft the initial CRM solution design once framing dependencies clear |

### Cross-Phase backlog

| Issue | Priority | Focus |
|-------|----------|-------|
| `helix-81c0c0df` | P1 | Consume DDx tier policy backed by the `ddx-agent` model catalog |

## Build Sequencing

| Order | Area | Governing Artifacts | Notes |
|-------|------|-------------------|-------|
| 1 | Redesign execution contract around DDx | FEAT-002, FEAT-011, TD-002, TD-011, CONTRACT-001, TP-002 | Align governing docs so HELIX supervision delegates managed execution to DDx, with `execute-loop` as the queue-drain contract and `execute-bead` as the bounded primitive. Decide which HELIX entry surfaces remain worth keeping once direct agent-plus-tracker use is common. |
| 2 | Proof shipped entry surfaces | FEAT-002, FEAT-004, FEAT-011, TD-002, TD-003, TD-011, TP-002 | Close deterministic proof gaps for `bin/helix`, `helix input`, and the dry-run harness before adding more command-surface drift. |
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
