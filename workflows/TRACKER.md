---
dun:
  id: helix.workflow.tracker
  depends_on:
    - helix.workflow
---
# HELIX Built-in Tracker

HELIX uses a built-in bead tracker for execution tracking. Canonical issues are
stored in `.helix/issues.jsonl` and managed via `helix tracker` subcommands.
The HELIX tracker is file-backed by design, but it must preserve explicit beads
interop with `bd`, `br`, and bead-compatible JSONL.

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

## Backend Contract

The built-in tracker is a minimal execution queue for HELIX. It is not a
general-purpose, multi-user issue system, and it does not auto-switch runtime
behavior based on which external bead tools happen to be installed locally.

Design constraints:

- canonical repo-local bead state in `.helix/issues.jsonl`
- low-concurrency operation by default
- deterministic CLI behavior that is easy to inspect, test, and commit
- compatibility with a single active implementation agent plus occasional
  concurrent queue management or triage work
- explicit import/export escape hatches for external bead tools

Out of scope for the built-in tracker:

- distributed coordination across machines
- high-contention, many-writer workloads
- rich server-style features such as comments, subscriptions, or live queries
- implicit backend selection based on ambient `bd` or `br` availability

If HELIX grows beyond those constraints, replace the tracker implementation
before extending the contract much further.

## Canonical Store And Interop

HELIX owns one canonical tracker store:

- `.helix/issues.jsonl`

HELIX must also preserve explicit beads interop surfaces:

- `helix tracker import`
  imports beads from `bd`, `br`, or bead-compatible JSONL into the canonical
  HELIX store
- `helix tracker export`
  exports the canonical HELIX store to bead-compatible JSONL for external tool
  import or recovery
- `helix tracker migrate`
  compatibility alias for `helix tracker import`

Interop rules:

- HELIX must not silently use `bd` or `br` as the live backing store just
  because they exist on `PATH`
- HELIX may read from live `bd` or `br` only through explicit import behavior
- the maintained outbound interchange format is bead-compatible JSONL
- if external bead tools are unavailable, HELIX must still function fully from
  `.helix/issues.jsonl`

## Backend Interface

Any HELIX tracker backend must implement the command behavior below. The shell
file-backed tracker is the reference implementation, but future backends must
preserve these semantics unless this document changes.

Required operations:

- `helix tracker init`
  ensures the canonical HELIX store exists
- `helix tracker create`
  creates one issue, returns its new issue ID on stdout, and persists the full
  canonical issue shape
- `helix tracker show <id> [--json]`
  returns one issue by ID or fails if the issue does not exist
- `helix tracker update <id> ...`
  mutates one existing issue, updates `updated`, and fails if the issue does
  not exist
- `helix tracker close <id>`
  equivalent to setting `status = closed`
- `helix tracker list [--status S] [--label L] [--json]`
  returns issues filtered only by the requested predicates
- `helix tracker ready [--json]`
  returns issues with `status = open` and no unclosed dependencies
- `helix tracker blocked [--json]`
  returns issues with `status = open` and at least one dependency not closed
- `helix tracker dep add <child> <parent>`
  adds one dependency edge without duplicating existing edges
- `helix tracker dep remove <child> <parent>`
  removes one dependency edge if present
- `helix tracker dep tree <id>`
  displays the issue and its direct dependency state for human inspection
- `helix tracker status [--json]`
  returns global counts derived from the canonical issue set
- `helix tracker import`
  imports external beads into canonical HELIX storage
- `helix tracker export`
  exports canonical HELIX storage to bead-compatible JSONL
- `helix tracker migrate`
  compatibility alias for `helix tracker import`

Required behavioral guarantees:

- canonical issue IDs are stable once created or imported
- all persisted issues conform to the canonical field set in this document
- `create`, `update`, `close`, `dep add`, `dep remove`, `import`, and `export`
  are mutation operations for locking purposes
- mutation commands fail rather than silently dropping requested changes
- `ready` and `blocked` semantics are dependency-aware and must not be
  reinterpreted by label or by a custom HELIX-only status taxonomy
- `update --claim` must set `status = in_progress`, set `assignee = helix`, and
  update `updated`
- imports may append to existing canonical state, but they must warn when doing
  so
- exports must preserve canonical tracker state without lossy translation in the
  maintained JSONL interchange format
- tracker-backed creation commands, including `helix tracker create` and
  `helix triage`, must fail closed when required HELIX steering fields are
  missing

Implementation-specific freedom:

- storage engine: JSONL, SQLite, Dolt, or another backend
- human-readable output formatting for non-JSON commands
- internal lock implementation
- internal query strategy

A backend must not change the meaning of tracker commands based on local tool
availability alone.

## Data Model

Each issue is a JSON object stored in `.helix/issues.jsonl` with these fields:

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
- `execution-eligible`: whether the issue is safe for automated execution selection
- `superseded-by`: replacement issue ID when a stale execution slice has been superseded
- `replaces`: prior issue ID that this issue replaces
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
- `execution-eligible`: keep refinement work visible in the tracker without making it runnable by `helix run`
- `superseded-by` / `replaces`: preserve explicit replacement traceability during refinement

The tracker is HELIX's steering wheel. Use these fields and relationships to
shape live execution rather than keeping separate TODO lists, hidden notes, or
unstructured handoff state.

Blocked work should be modeled with dependencies and surfaced through
`helix tracker blocked` / `helix tracker ready`, not with a custom HELIX status
taxonomy. When you need only execution-safe queue candidates, use
`helix tracker ready --execution`.

## Claim Semantics

`open` means the issue is available to be claimed. `in_progress` means the
issue is actively owned by one HELIX agent or operator session and should not
be treated as queue-ready. `deferred` means the work is intentionally
non-actionable for now. `closed` means the work is complete.

Claiming an issue must set `status = in_progress`, assign `assignee = helix`,
and update the issue timestamp. A claim is an advisory lock for execution, not a
generic “started work” marker.

This claim lock is separate from the tracker's file mutation lock. The claim
controls who owns the work. The file lock only serializes writes to
`.helix/issues.jsonl`.

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

## Concurrency Model

HELIX assumes most tracker use is single-threaded, but the tracker must safely
tolerate a small amount of concurrent local activity.

Supported case:

- one agent advancing implementation work while another local agent or operator
  inspects or mutates the queue

Required behavior:

- all tracker mutations must serialize through a repository-local lock
- file rewrites must be atomic so readers observe either the old state or the
  new state, never a partial file
- readers may remain lock-free if writes preserve whole-file atomicity
- malformed `.helix/issues.jsonl` state must fail closed for both reads and
  mutations rather than being rewritten opportunistically
- lock acquisition timeouts must surface the recorded lock-owner PID when
  available so operators can investigate before clearing `.helix/issues.lock`

Non-goals:

- fairness guarantees under contention
- stale lock recovery without operator judgment
- coordination across different machines that share a repository by syncing VCS
  state alone

## Lock Recovery

The repository-local tracker lock is a safety mechanism, not a lease system.
If a mutation command fails with a lock-timeout error, treat the lock as
possibly valid until you have checked it.

Recommended operator recovery steps:

1. Read the reported lock owner PID from the timeout message or from
   `.helix/issues.lock/pid`.
2. Check whether that process is still active and plausibly owns current
   tracker work.
3. If the process is still active, wait or stop; do not clear the lock.
4. If the process is gone and local tracker work is otherwise quiescent, remove
   `.helix/issues.lock` manually and retry the tracker command.
5. If ownership is unclear, stop and require guidance rather than forcing
   mutation through.

HELIX does not currently auto-break tracker locks. Manual recovery is
intentional because false-positive lock breaking can corrupt concurrent
operator or agent work.

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
- one phase label: `phase:frame`, `phase:design`, `phase:test`, `phase:build`, `phase:deploy`, `phase:iterate`, or `phase:review`

Add labels as needed for traceability:

- `kind:build`, `kind:deploy`, `kind:backlog`, `kind:review`
- `story:US-XXX`
- `feature:FEAT-XXX`
- `source:metrics`, `source:feedback`, `source:retrospective`, `source:incident`
- `review-finding` for actionable findings filed by the fresh-eyes review action
- `acceptance-failure` for acceptance check failures filed by the run loop
- area labels such as `area:auth` or `area:cli`

Use `--spec-id` for the closest governing artifact. Put the full authority
chain in the description when more than one canonical artifact governs the
work.

## Triage Validation

Tracker creation must validate required steering fields before a new issue is
written.

Required at create time:

- `helix` label
- one phase label: `phase:frame`, `phase:design`, `phase:test`, `phase:build`,
  `phase:deploy`, `phase:iterate`, or `phase:review`
- `--spec-id` for `task` issues
- deterministic `--acceptance` for `task` and `epic` issues
- dependencies, when provided, must reference existing issue IDs

Advisory but recommended:

- a `kind:*` label for execution and reporting clarity

Validation failures must stop issue creation instead of silently producing a
partially specified HELIX issue. `helix triage` is the preferred operator-facing
entrypoint because it guides users toward the required field set.

## HELIX Categories

| HELIX category | Issue type | Required labels | Typical governing refs |
|---|---|---|---|
| Design or artifact-evolution work | `task` | `helix`, `phase:design`, `kind:design` | `prd.md`, `FEAT-XXX`, `SD-XXX`, `TD-XXX`, `TP-XXX`, workflow docs |
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

For operator-facing execution flow, bounded loop control, and HELIX action
sequencing, see [EXECUTION.md](EXECUTION.md).

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

Import or export beads explicitly:

```bash
helix tracker import                 # auto: bd -> br -> .beads/issues.jsonl
helix tracker import --from bd
helix tracker import --from jsonl --file .beads/issues.jsonl
helix tracker export                # writes .beads/issues.jsonl
helix tracker export --stdout
```

## What Not To Do

- Do not create custom issue file formats outside `.helix/issues.jsonl`.
- Do not invent `BEAD-###` identifiers; use native tracker issue IDs.
- Do not invent a parallel status model when upstream status plus dependencies
  already models the work.
- Do not clear or overwrite a live `in_progress` claim without stale-claim
  evidence.
