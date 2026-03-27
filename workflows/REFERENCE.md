---
dun:
  id: helix.workflow.reference
  depends_on:
    - helix.workflow
---
# HELIX Quick Reference Card

## Canonical Docs

- [README.md](README.md): high-level model and authority order
- [EXECUTION.md](EXECUTION.md): queue control and operator loop
- [TRACKER.md](TRACKER.md): built-in bead tracker mapping, backend contract, and labels
- [implementation.md](actions/implementation.md): one bounded execution pass
- [check.md](actions/check.md): queue-drain decision
- [reconcile-alignment.md](actions/reconcile-alignment.md): top-down review
- [backfill-helix-docs.md](actions/backfill-helix-docs.md): conservative reconstruction
- [plan.md](actions/plan.md): iterative design document creation
- [polish.md](actions/polish.md): issue refinement before implementation
- [fresh-eyes-review.md](actions/fresh-eyes-review.md): post-implementation review
- [experiment.md](actions/experiment.md): metric-driven optimization iteration
- [metric-definition.yaml](templates/metric-definition.yaml): shared metric definitions

## Phase Summary

| Phase | Primary Output | Main Location |
|---|---|---|
| Optional `00-discover` | vision and opportunity framing | `docs/helix/00-discover/` |
| `01-frame` | requirements and stories | `docs/helix/01-frame/` |
| `02-design` | architecture and design contracts | `docs/helix/02-design/` |
| `03-test` | test plans and failing tests | `docs/helix/03-test/`, `tests/` |
| `04-build` | project build guidance + execution issues | `docs/helix/04-build/`, `.helix/` |
| `05-deploy` | rollout docs + deploy issues | `docs/helix/05-deploy/`, `.helix/` |
| `06-iterate` | backlog, reports, follow-up planning | `docs/helix/06-iterate/` |

## Authority Order

1. Product Vision
2. Product Requirements
3. Feature Specs / User Stories
4. Architecture / ADRs
5. Solution / Technical Designs
6. Test Plans / Tests
7. Implementation Plans
8. Source Code / Build Artifacts

## Core Commands

### Bootstrap

```bash
helix tracker init
scripts/install-local-skills.sh
```

Installed agent skills mirror CLI commands exactly: `helix-<command>` maps to
`helix <command>`.

Canonical project package path: `./.agents/skills`
Canonical user install path: `~/.agents/skills`
Claude compatibility path: `~/.claude/skills`

### Execution Commands

```bash
helix run
helix implement
helix implement hx-abc123
helix check repo
helix align repo
helix backfill repo
```

### Planning and Quality Commands

```bash
helix plan [scope]                    # create design document
helix plan --rounds 8 auth            # more refinement rounds
helix polish [scope]                  # refine issues before implementation
helix polish --rounds 10              # more polish rounds
helix next                            # recommended next issue
helix review [scope]                  # fresh-eyes review of recent work
helix experiment [issue-id|goal]      # one experiment iteration
helix experiment --close              # squash-merge and close session
```

### Tracker

```bash
helix tracker ready --json
helix tracker update <id> --claim
helix tracker show <id>
helix tracker dep tree <id>
helix tracker blocked --json
helix tracker close <id>
helix tracker status
helix tracker import --from jsonl --file .beads/issues.jsonl
helix tracker export
```

See [TRACKER.md](TRACKER.md) for full tracker conventions and setup guidance.

## Tracker Labeling

Labels are organizational conventions for triage and traceability. They are
not required by the execution loop queue guard.

Recommended labels:
- `helix` -- identifies HELIX-managed issues (recommended, not required by the queue guard).
- Phase labels: `phase:build`, `phase:deploy`, `phase:iterate`, `phase:review`.
- Kind labels: `kind:build`, `kind:deploy`, `kind:backlog`, `kind:review`.
- Traceability labels: `story:US-XXX`, `feature:FEAT-XXX`, `area:<name>`, `source:metrics`.

## Decision Guide

- Starting new work or a large scope:
  run `helix plan`, then `helix polish`, then `helix run`.
- Ready execution issues exist:
  run `implementation` or `helix run`.
- No ready execution issue, but the planning stack exists and next work is
  unclear:
  run alignment.
- Canonical docs are missing or too incomplete to execute safely:
  run backfill.
- Work exists but is blocked or already in progress:
  stop and wait.
- The queue drains:
  run `check`, not a blind loop and not `helix tracker list --ready`.
- After implementing an issue:
  run `helix review` for fresh-eyes quality check.

## Artifact Inputs

Use the prompts and templates under:

- `workflows/phases/00-discover/artifacts/`
- `workflows/phases/01-frame/artifacts/`
- `workflows/phases/02-design/artifacts/`
- `workflows/phases/03-test/artifacts/`
- `workflows/phases/04-build/artifacts/`
- `workflows/phases/05-deploy/artifacts/`
- `workflows/phases/06-iterate/artifacts/`

Those artifact directories support the canonical docs under `docs/helix/`; they
do not replace the bounded execution contract.

## Output Reports

- Alignment reviews:
  `docs/helix/06-iterate/alignment-reviews/AR-YYYY-MM-DD[-scope].md`
- Backfill reports:
  `docs/helix/06-iterate/backfill-reports/BF-YYYY-MM-DD[-scope].md`

## Validation

When changing HELIX wrapper behavior or the execution contract:

```bash
bash tests/helix-cli.sh
git diff --check
```
