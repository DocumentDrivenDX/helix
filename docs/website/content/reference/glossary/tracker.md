---
title: Tracker
weight: 6
prev: /reference/glossary/concepts
aliases:
  - /docs/glossary/tracker
---

# DDx Tracker

DDx is the reference runtime integration for HELIX. Its tracker stores work
items as **beads** in `.ddx/beads.jsonl`, managed via `ddx bead` subcommands.
HELIX can use those beads as runtime evidence and work handoff, but HELIX does
not require a tracker or ship one as part of the methodology.

## Beads

A bead is a DDx work item. In a HELIX project, a bead should cite the governing
artifact that authorizes the work.

| Field | Purpose |
|-------|---------|
| **id** | Unique identifier (e.g., `hx-407ed8b8`) |
| **title** | Short description of the work |
| **type** | `task`, `chore`, `epic`, `decision` |
| **status** | `open`, `in_progress`, `closed`, `deferred` |
| **priority** | Numeric priority (lower = higher priority) |
| **labels** | Organizational tags for triage and traceability |
| **spec-id** | Reference to the governing artifact (e.g., `FEAT-001`, `TD-003`) |
| **parent** | Parent epic or issue ID |
| **deps** | Dependency list: issues that must close before this one is ready |
| **acceptance** | Deterministic criteria that define "done" |
<!-- vale Helix.Hedges = NO -->
| **description** | Full description, often prefixed with [runtime work context](/reference/glossary/concepts/#runtime-work-context) |
<!-- vale Helix.Hedges = YES -->
| **notes** | Execution notes appended during work |

## Labels

Labels are organizational conventions for triage and traceability.

### Activity Labels

| Label | Meaning |
|-------|---------|
| `phase:frame` | Requirements and scoping work |
| `phase:design` | Architecture and design work |
| `phase:test` | Test creation work |
| `phase:build` | Implementation work |
| `phase:deploy` | Deployment and release work |
| `phase:iterate` | Review, improvement, and follow-up work |
| `phase:review` | Reconciliation or audit work |

### Kind Labels

| Label | Meaning |
|-------|---------|
| `kind:build` | Standard execution work |
| `kind:deploy` | Rollout work |
| `kind:backlog` | Prioritized follow-up |
| `kind:review` | Review or reconciliation |

### Area Labels

| Label | Meaning |
|-------|---------|
| `area:ui` | Frontend work |
| `area:api` | Backend/server work |
| `area:data` | Database/storage work |
| `area:infra` | Infrastructure/deployment work |
| `area:cli` | CLI tool work |

<!-- vale Helix.PassiveVoice = NO -->
Area labels let DDx and HELIX-aware agents match [concerns](/concerns/) to
runtime work. A `polish` pass may propose labels when a runtime uses beads.
<!-- vale Helix.PassiveVoice = YES -->

### Traceability Labels

| Label | Meaning |
|-------|---------|
| `story:US-NNN` | Links to a user story |
| `feature:FEAT-NNN` | Links to a feature spec |
| `source:metrics` | Discovered from metric analysis |
| `source:learnings` | Discovered from operational learnings |
| `review-finding` | Created by a fresh-eyes review |

## Common Commands

```bash
# Initialize the tracker
ddx bead init

# Create an issue
ddx bead create "Title" --type task --labels helix,phase:build \
  --spec-id FEAT-001 --acceptance "tests pass"

# View queue health
ddx bead status

# List ready issues
ddx bead ready --json

# Claim and work an issue
ddx bead update <id> --claim

# View an issue
ddx bead show <id> --json

# View dependency tree
ddx bead dep tree <id>

# Add a dependency
ddx bead dep add <id> --blocked-by <other-id>

# Close an issue
ddx bead close <id>

# View blocked issues
ddx bead blocked --json
```

## Queue Control

In DDx, the tracker queue can drive the [workflow loop](/use/workflow/):

1. The `helix` skill in `check` mode can inspect the ready queue and recommend the next action
2. `ddx work` claims and executes one ready issue
3. `ddx work` chains check and build until the queue drains

### Ready Queue

An issue is **ready** when:
- Status is `open` (not `in_progress`, `closed`, or `deferred`)
- All dependencies are `closed`
- It is an execution issue (not `phase:review`)

### Queue Drain

When the ready queue is empty:
- The HELIX skill in `check` mode determines whether this is true exhaustion or a planning gap
- `ALIGN` means planning exists but the next work set is unclear
- `DESIGN` means design authority is missing
- `POLISH` means issues need refinement
- `STOP` means there is genuinely no more work

## spec-id

The `spec-id` field links a bead to its governing artifact. This is how a DDx
runtime preserves traceability from execution back to HELIX requirements.

Examples:
- `spec-id: FEAT-001`: governed by feature spec 001
- `spec-id: TD-003`: governed by technical design 003
- `spec-id: US-042`: governed by user story 042

Runtime execution loads the governing artifact referenced by `spec-id` to
understand what the issue should accomplish and verify the work against
acceptance criteria.

## Dependency Management

DDx beads can declare dependencies on other DDx beads:

```bash
# B cannot start until A is closed
ddx bead dep add B --blocked-by A

# View the full dependency tree
ddx bead dep tree <id>
```

Dependencies affect the ready queue: a DDx bead with unresolved dependencies is
not ready. A HELIX `check` pass can consider dependency chains when
recommending which issue to work next in DDx.
