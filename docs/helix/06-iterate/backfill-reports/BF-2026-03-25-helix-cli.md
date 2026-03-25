# HELIX Backfill Report: helix-cli

**Backfill Date**: 2026-03-25
**Scope**: helix-cli
**Status**: complete
**Research Epic**: hx-b74450af
**Research Beads**: hx-1a64fba4, hx-d6ebac33, hx-f6a7c00b, hx-bd7799c2, hx-3967ea91
**Primary Evidence Baseline**: `scripts/helix`, `scripts/tracker.sh`, `scripts/install-local-skills.sh`, `tests/helix-cli.sh`, `README.md`, `workflows/EXECUTION.md`, `workflows/REFERENCE.md`, `workflows/QUICKSTART.md`

## Backfill Metadata

- **Reviewer / Author**: Codex
- **Run Trigger**: Explicit `helix-cli` backfill request on 2026-03-25
- **Authority Baseline**: Product Vision -> PRD -> Feature Specs / User Stories -> Architecture / ADRs -> Solution / Technical Designs -> Test Plans / Tests -> Implementation Plans -> Source Code
- **Confidence Scale**: HIGH / MEDIUM / LOW
- **Upstream Beads References**: hx-b74450af, hx-1a64fba4, hx-d6ebac33, hx-f6a7c00b, hx-bd7799c2, hx-3967ea91

## Scope and Evidence Baseline

### Scope Definition

- Wrapper entrypoint and queue controller in `scripts/helix`
- Built-in tracker library in `scripts/tracker.sh`
- Local skill and launcher installer in `scripts/install-local-skills.sh`
- Deterministic wrapper harness in `tests/helix-cli.sh`
- Operator-facing command docs in `README.md`, `workflows/EXECUTION.md`, `workflows/REFERENCE.md`, and `workflows/QUICKSTART.md`

### Evidence Surveyed

- `scripts/helix:15-94`, `scripts/helix:250-305`, `scripts/helix:381-519`, `scripts/helix:542-570`, `scripts/helix:677-760`
- `scripts/tracker.sh:7-49`, `scripts/tracker.sh:52-224`, `scripts/tracker.sh:265-420`
- `scripts/install-local-skills.sh:4-67`
- `tests/helix-cli.sh:347-447`, `tests/helix-cli.sh:563-665`, `tests/helix-cli.sh:721-937`, `tests/helix-cli.sh:978-1010`
- `README.md:10-24`, `README.md:36-50`
- `workflows/EXECUTION.md:27-52`, `workflows/EXECUTION.md:142-203`, `workflows/EXECUTION.md:229-297`
- `workflows/REFERENCE.md:47-80`, `workflows/REFERENCE.md:107-154`
- `workflows/QUICKSTART.md:77-130`

## Recursive Coverage

### Coverage Ledger

| Scope Node | Node Type | Review Bead | Coverage Status | Files / Paths Covered | Notes |
|------------|-----------|-------------|-----------------|-----------------------|-------|
| helix-cli | root | hx-b74450af | complete | `scripts/`, `tests/`, selected root and `workflows/` docs | Scope limited to the wrapper CLI subsystem explicitly requested by the user |
| helix-cli/runtime | file-set | hx-1a64fba4 | complete | `scripts/helix`, `scripts/tracker.sh` | Reviewed command surface, loop control, prompt building, and tracker semantics |
| helix-cli/installer | file-set | hx-d6ebac33 | complete | `scripts/install-local-skills.sh` | Reviewed skill linking and launcher installation behavior |
| helix-cli/tests | file-set | hx-f6a7c00b | complete | `tests/helix-cli.sh` | Reviewed deterministic coverage for wrapper contracts |
| helix-cli/docs | file-set | hx-bd7799c2 | complete | `README.md`, `workflows/EXECUTION.md`, `workflows/REFERENCE.md`, `workflows/QUICKSTART.md` | Reviewed operator-facing command docs and validation guidance |
| helix-cli/consolidation | consolidation | hx-3967ea91 | complete | `docs/helix/**` backfill outputs | Synthesized reviewed evidence into canonical subsystem artifacts |

### Explicit Exclusions

| Path | Reason Excluded | Impact on Confidence |
|------|------------------|----------------------|
| `docs/demos/helix-quickstart/recordings/*` | Binary/demo capture assets do not define wrapper behavior or canonical CLI requirements | LOW |
| `skills/**` | Skills invoke workflow behavior but were outside the requested `helix-cli` backfill scope | LOW |

### Consolidation Chain

| Child Node | Parent Consolidation Node | Status |
|------------|---------------------------|--------|
| helix-cli/runtime | helix-cli/consolidation | complete |
| helix-cli/installer | helix-cli/consolidation | complete |
| helix-cli/tests | helix-cli/consolidation | complete |
| helix-cli/docs | helix-cli/consolidation | complete |
| helix-cli/consolidation | helix-cli | complete |

## Current-State Summary

### Observed Product Behavior

The repository ships a Bash wrapper CLI that exposes HELIX execution,
planning, review, tracker, and experiment commands from one entrypoint. The
wrapper builds prompts for documented HELIX actions, supports Codex and Claude
as agent backends, offers dry-run output, records session logs, exposes a
built-in JSONL tracker as `helix tracker`, and installs a local launcher via
`scripts/install-local-skills.sh`.

### Observed Architecture and Runtime Shape

The runtime is split between `scripts/helix` for dispatch/orchestration,
`scripts/tracker.sh` for tracker persistence and dependency-aware queue logic,
`scripts/install-local-skills.sh` for setup, and `tests/helix-cli.sh` for
deterministic wrapper validation. Command docs in `README.md` and `workflows/`
describe the same command family and reinforce the bounded loop model.

### Operational and Delivery Context

The wrapper expects a local git checkout, Bash, and `jq`. Agent execution
depends on either `codex` or `claude`; swarm mode additionally depends on
`ntm` and `tmux`. Wrapper behavior changes are validated with
`bash tests/helix-cli.sh`, while docs-only backfill work can be checked with
`git diff --check`.

### Evidence vs Inference Notes

- Direct evidence: the command surface, prompt text, tracker storage path, log
  path, and installer launcher are directly defined in `scripts/helix`,
  `scripts/tracker.sh`, and `scripts/install-local-skills.sh`.
- Direct evidence: deterministic tests assert help output, queue behavior,
  backfill trailer enforcement, installer behavior, and experiment safeguards in
  `tests/helix-cli.sh`.
- Medium-confidence inference: the intended audience is repository operators and
  AI-assisted sessions; this is inferred from the CLI surface, action prompts,
  and test harness rather than a dedicated product artifact.

## Artifact Inventory and Gaps

| Artifact Slot | Current State | Action | Confidence | Evidence |
|---------------|---------------|--------|------------|----------|
| Product Vision | missing for this subsystem | defer | LOW | No scope-specific vision artifact found; only implementation and operator docs were available |
| PRD | missing for this subsystem | defer | LOW | No scope-specific requirements doc found before backfill |
| Feature Spec | missing | create | HIGH | `scripts/helix:40-94`, `README.md:36-50`, `workflows/EXECUTION.md:154-183` |
| Technical Design | missing | create | HIGH | `scripts/helix:109-239`, `scripts/tracker.sh:52-420`, `scripts/install-local-skills.sh:4-67` |
| Test Plan | missing | create | HIGH | `tests/helix-cli.sh:347-447`, `tests/helix-cli.sh:563-665`, `tests/helix-cli.sh:721-937` |
| Implementation Plan | missing | create | HIGH | `workflows/REFERENCE.md:149-154`, `scripts/helix:451-519`, `scripts/install-local-skills.sh:35-67` |
| Backfill Report | missing | create | HIGH | Current action output and reviewed evidence set |

## Confidence Ledger

| Area | Statement | Confidence | Evidence | Notes |
|------|-----------|------------|----------|-------|
| Command surface | `helix-cli` includes `run`, `implement`, `check`, `align`, `backfill`, `plan`, `polish`, `next`, `review`, `experiment`, `spawn`, `tracker`, and `help` | HIGH | `scripts/helix:42-69`, `README.md:38-50` | Directly declared in wrapper usage and repo docs |
| Queue control | `run` is bounded by dependency-aware ready work and a queue-drain `check` pass | HIGH | `scripts/helix:677-760`, `tests/helix-cli.sh:571-581`, `workflows/EXECUTION.md:43-52` | Code and tests agree |
| Tracker semantics | The repository-local tracker stores JSONL issues and derives ready/blocked state from dependency closure | HIGH | `scripts/tracker.sh:7-49`, `scripts/tracker.sh:265-343`, `tests/helix-cli.sh:361-383` | Direct implementation plus test corroboration |
| Installation | The installer links HELIX skills and writes `~/.local/bin/helix` to exec the repo wrapper | HIGH | `scripts/install-local-skills.sh:35-67`, `tests/helix-cli.sh:650-665` | Direct implementation plus test corroboration |
| Repo-level tracker narrative | HELIX methodology docs still reference upstream `bd` heavily while this repository's operational instructions require `helix tracker` | MEDIUM | `AGENTS.md:6-8`, `AGENTS.md:31-32`, `scripts/helix:299-303`, `workflows/EXECUTION.md:45-52`, `workflows/REFERENCE.md:82-94` | Documented divergence; resolved conservatively by scoping artifacts to the wrapper subsystem |

## Guidance Gates

### Questions Raised

No user guidance gate blocked drafting for the requested `helix-cli` scope. The
repo-level tracker narrative divergence was recorded for follow-up instead of
being canonized as a scope-wide product decision.

| Decision Area | Ambiguity | Evidence | Default Interpretation | User Guidance Needed |
|---------------|-----------|----------|------------------------|----------------------|
| none | none blocking this scope | n/a | n/a | no |

### Guidance Received

| Decision Area | User Direction | Date | Applied To |
|---------------|----------------|------|------------|
| Tracker backend for this run | Use `helix tracker` subcommands instead of `bd` in this repository | 2026-03-25 | research execution and backfill report |

## Backfilled Artifacts

| Artifact | Status | Confidence | Basis | Notes |
|----------|--------|------------|-------|-------|
| `docs/helix/01-frame/features/helix-cli.md` | created | HIGH | wrapper usage, command docs, tracker and backfill behavior | Scoped to observable subsystem behavior |
| `docs/helix/02-design/technical-designs/helix-cli.md` | created | HIGH | wrapper implementation, tracker library, installer, harness | Captures components and runtime surfaces only |
| `docs/helix/03-test/test-plans/helix-cli.md` | created | HIGH | deterministic harness and validation docs | Does not overstate live-agent coverage |
| `docs/helix/04-build/implementation-plans/helix-cli.md` | created | HIGH | wrapper code boundaries and validation guidance | Preserves deterministic test gate as implementation rule |
| `docs/helix/06-iterate/backfill-reports/BF-2026-03-25-helix-cli.md` | created | HIGH | current backfill execution | Durable record for this run |

## Assumption Ledger

| Assumption | Confidence | Affected Artifacts | Confirmation Status | Next Action |
|------------|------------|--------------------|---------------------|-------------|
| The requested scope is the wrapper CLI subsystem, not the full HELIX methodology stack | HIGH | all backfilled artifacts | confirmed by user-provided scope | none |
| Wrapper command docs and tests are sufficient to backfill subsystem-level feature, design, test, and build docs without creating a repo-wide PRD | MEDIUM | feature/design/test/build docs | pending broader planning work | keep scope-specific; defer higher-authority repo artifacts |
| Repo-level `bd` references in workflow docs should be treated as broader methodology context rather than helix-cli subsystem requirements for this run | MEDIUM | backfill report, feature spec | pending reconciliation | create follow-up documentation bead |

## Follow-Up Beads

| Bead ID | Type | HELIX Labels | Goal | Dependencies | Why It Exists |
|---------|------|--------------|------|--------------|---------------|
| hx-100d3ffa | task | `helix`, `phase:review`, `kind:review`, `area:helix-cli`, `area:docs` | Reconcile built-in tracker guidance for this repo with HELIX docs that still center `bd` for operator examples | none | Backfill found a documented divergence that did not block subsystem artifact creation |

## Next Recommended Steps

1. Reconcile the repo-local `helix tracker` contract against command docs that still present `bd` as the primary operator path.
2. If broader HELIX product framing is needed, author higher-authority discover/frame artifacts before expanding backfill beyond `helix-cli`.
3. Keep `bash tests/helix-cli.sh` as the required gate for any future wrapper behavior changes.
