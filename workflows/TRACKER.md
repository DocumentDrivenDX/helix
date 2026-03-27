---
dun:
  id: helix.workflow.tracker
  depends_on:
    - helix.workflow
---
# HELIX Built-in Tracker

HELIX uses a built-in JSONL tracker for execution tracking. Issues are stored
in `.helix/issues.jsonl` and managed via `helix tracker` subcommands.

## Scope

This document owns HELIX's tracker conventions.

- Follow this file for labels, issue types, `spec-id`, and queue-query
  conventions.
- Follow [EXECUTION.md](EXECUTION.md) for loop control and action sequencing.
- If another HELIX document shows different tracker semantics, prefer this file
  and correct the drift there.

## Setup

The tracker initializes automatically with the HELIX workspace. Issues are
stored in `.helix/issues.jsonl` and committed to version control alongside the
project.

HELIX execution assumes a working tracker. If the tracker is missing or
unhealthy, stop immediately.

## Data Model

Each issue is a JSON object appended to `.helix/issues.jsonl` with these fields:

- `id`: unique issue identifier
- `type`: issue type such as `task`, `epic`, `chore`, or `decision`
- `status`: operational state such as `open`, `in_progress`, `deferred`, or `closed`
- `labels`: array of HELIX label strings
- `spec-id`: nearest governing canonical artifact
- `parent`: parent issue ID for grouping related work
- `deps`: array of blocking dependency IDs
- `description`: work contract and governing artifact references
- `design`: implementation approach
- `acceptance`: deterministic completion criteria
- `notes`: additional context
- `assignee`: owner identity when an issue is `in_progress`
- `created`: ISO-8601 timestamp for when the issue was created
- `updated`: ISO-8601 timestamp for the most recent mutation

## HELIX Mapping

Use tracker fields directly:

- `type`: use native issue types such as `task`, `epic`, `chore`, or `decision`
- `parent`: group related work under a review epic or other parent issue
- `deps` / `helix tracker dep add`: encode blocking dependencies
- `status`: use native operational states such as `open`, `in_progress`,
  `deferred`, and `closed`
- `spec-id`: point to the nearest governing canonical artifact
- `description`, `design`, `acceptance`, and `notes`: capture the work contract
- `assignee`: encode active ownership for claimed work
- `labels`: encode HELIX-specific execution semantics

Blocked work should be modeled with dependencies and surfaced through
`helix tracker blocked` / `helix tracker ready`, not with a custom HELIX status
taxonomy.

## Claim Semantics

`open` means the issue is available to be claimed. `in_progress` means the
issue is actively owned by one HELIX agent or operator session and should not
be treated as queue-ready. `deferred` means the work is intentionally
non-actionable for now. `closed` means the work is complete.

Claiming an issue must set `status = in_progress`, assign `assignee = helix`,
and update the issue timestamp. A claim is an advisory lock for execution, not a
generic “started work” marker.

Current ownership metadata:

- `assignee`: the agent or operator identity that owns the issue

Queue consumers must prefer tracker claim state over local process heuristics.
A live `in_progress` claim remains authoritative even if the original local
process cannot be observed directly. Additional lease metadata is recommended
future work, not current tracker behavior.

## Stale Claim Detection

A claim is stale only when ownership metadata is no longer trustworthy.

Treat a claim as stale only when explicit ownership metadata exists and becomes
untrustworthy, or when the user explicitly requests recovery.

Do not infer staleness from the absence of a matching local process alone.
Process absence is a hint, not proof.

When a claim is stale, the wrapper may reclaim it only if the partial work can
be attributed to that specific issue with enough confidence to preserve
unrelated changes.

## Safe Orphan Recovery

Recovery must be conservative and non-destructive.

Required rules:

- preserve unrelated local worktree changes
- only revert or re-open files that can reasonably be attributed to the stale
  issue
- never use a repository-wide rollback as the default recovery step
- stop and require guidance if attribution is unclear

Recommended recovery sequence:

1. Confirm the issue is stale by ownership metadata, not just process absence.
2. Inspect the dirty worktree and identify files plausibly owned by the issue.
3. If attribution is strong, complete the issue or revert only the issue-owned
   files and return the issue to `open`.
4. If attribution is weak, leave unrelated work intact and escalate.

## Verification Evidence Conventions

If a repository defines canonical verification wrappers or proof lanes, treat
them as the closure surface for the corresponding issue.

- Close execution issues from the repo-owned wrapper command and its retained
  artifacts, not from narrower package or file commands that were only used to
  debug the failure.
- When the canonical lane contradicts historical close evidence, reopen the
  issue immediately or create an explicit regression issue linked to the
  contradicted close evidence.
- Record the exact command, run date, exit status, and artifact paths reviewed
  in the issue close comment or regression note.

## HELIX Label Conventions

Labels are organizational conventions for triage and traceability. The
execution loop queue guard does not filter by label -- it uses all ready issues.

Recommended labels:

- `helix` -- identifies HELIX-managed issues; useful for triage and cross-repo queries
- one phase label: `phase:build`, `phase:deploy`, `phase:iterate`, or `phase:review`

Add labels as needed for traceability:

- `kind:build`, `kind:deploy`, `kind:backlog`, `kind:review`
- `story:US-XXX`
- `feature:FEAT-XXX`
- `source:metrics`, `source:feedback`, `source:retrospective`, `source:incident`
- area labels such as `area:auth` or `area:cli`

Use `--spec-id` for the closest governing artifact. Put the full authority
chain in the description when more than one canonical artifact governs the
work.

## HELIX Categories

| HELIX category | Issue type | Required labels | Typical governing refs |
|---|---|---|---|
| Story build work | `task` | `helix`, `phase:build`, `kind:build`, `story:US-XXX` | `FEAT-XXX`, `SD-XXX`, `TD-XXX`, `TP-XXX`, `implementation-plan.md` |
| Story deploy work | `task` | `helix`, `phase:deploy`, `kind:deploy`, `story:US-XXX` | deployment docs, related build issue IDs |
| Improvement backlog item | `task` or `chore` | `helix`, `phase:iterate`, `kind:backlog` | lessons learned, feedback, incidents, metrics |
| Review epic | `epic` | `helix`, `phase:review`, `kind:review` | review scope and governing artifacts |
| Review slice | `task` | `helix`, `phase:review`, `kind:review` | parent review epic plus scoped artifacts |

## Command Patterns

### Build Issue

```bash
helix tracker create "Implement US-036: list MCP servers CLI path" \
  --type task \
  --labels helix,phase:build,kind:build,story:US-036,feature:FEAT-001 \
  --spec-id TP-036 \
  --description "Governing artifacts: FEAT-001-mcp-server-management, SD-001-mcp-management, US-036, TD-036, TP-036, docs/helix/04-build/implementation-plan.md" \
  --design "Implement the CLI slice needed to satisfy the failing TP-036 tests." \
  --acceptance "TP-036 tests pass; no upstream artifact drift is introduced."
```

### Deploy Issue

```bash
helix tracker create "Roll out US-036: list MCP servers" \
  --type task \
  --labels helix,phase:deploy,kind:deploy,story:US-036 \
  --spec-id docs/helix/05-deploy/deployment-checklist.md \
  --description "Governing artifacts: deployment-checklist.md, monitoring-setup.md, runbook.md, build issue hx-a3f2dd" \
  --acceptance "Smoke checks pass, monitoring is clean, rollback trigger is documented." \
  --deps hx-a3f2dd
```

### Backlog Issue

```bash
helix tracker create "Reduce auth retry noise in logs" \
  --type chore \
  --labels helix,phase:iterate,kind:backlog,source:metrics,area:auth \
  --spec-id docs/helix/06-iterate/lessons-learned.md \
  --description "Derived from lessons learned and production metrics." \
  --acceptance "Retry logging volume drops without hiding actionable failures."
```

### Review Epic and Review Issues

```bash
review_epic=$(helix tracker create "HELIX alignment review: auth and session flow" \
  --type epic \
  --labels helix,phase:review,kind:review \
  --spec-id docs/helix/01-frame/prd.md \
  --silent)

helix tracker create "Review auth traceability and implementation drift" \
  --type task \
  --parent "$review_epic" \
  --labels helix,phase:review,kind:review,area:auth \
  --description "Review scope: auth requirements, design, tests, and implementation alignment."
```

## Daily Workflow

For operator-facing execution flow, bounded loop control, and Codex or Claude
automation patterns, see [EXECUTION.md](EXECUTION.md).

Use the `helix tracker` commands below when triaging or managing the queue
manually.

Find ready work:

```bash
helix tracker ready --json
helix tracker ready              # human-readable summary
```

Claim, inspect, and close work:

```bash
helix tracker update <id> --claim
helix tracker show <id>
helix tracker dep tree <id>
helix tracker close <id>
```

Check blocked work or epic progress:

```bash
helix tracker blocked
```

## What Not To Do

- Do not create custom issue file formats outside `.helix/issues.jsonl`.
- Do not invent `BEAD-###` identifiers; use native tracker issue IDs.
- Do not invent a parallel status model when upstream status plus dependencies
  already models the work.
- Do not clear or overwrite a live `in_progress` claim without stale-claim
  evidence.
