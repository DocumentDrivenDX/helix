# HELIX on DDx

DDx (Document-Driven Development Experience) is the HELIX reference
runtime. This guide is the home for all DDx-specific packaging, naming,
and invocation detail. The portable HELIX methodology
([`workflows/README.md`](../../workflows/README.md),
[`workflows/EXECUTION.md`](../../workflows/EXECUTION.md), and the
[routing skill](../../skills/helix/SKILL.md)) describes *actions* in
runtime-neutral terms; this guide names the concrete `ddx` commands that
realize those actions when DDx is the runtime.

> **Boundary.** HELIX provides the artifact catalog, the routing skill,
> and the artifact schema. DDx provides the work-item tracker, the
> execution loop, dispatch, and evidence capture. See
> [CONTRACT-003](../helix/02-design/contracts/CONTRACT-003-ddx-adapter-boundary.md)
> for the full adapter boundary. Nothing on this page is a HELIX
> requirement — another runtime supplies its own equivalents (or none).

## Install

```bash
ddx install helix
```

`ddx install helix` clones HELIX into `~/.ddx/plugins/helix/` using the
Claude Code plugin format, so the same content serves both runtimes. In
a DDx install the catalog source that HELIX docs call `workflows/` is
vendored at `<plugin-root>/workflows/` — i.e. `.ddx/plugins/helix/workflows/`.

Verify the install:

```bash
ddx doctor
```

## DDx stores work items as beads

DDx's concrete work item is the **bead**. Where the portable methodology
says "work item", DDx means a bead. Beads are stored in `.ddx/beads.jsonl`
and managed through `ddx bead`:

```bash
ddx bead ready                  # open beads with all deps satisfied
ddx bead ready --execution      # the next execution-ready bead
ddx bead show <id>
ddx bead update <id> --claim    # claim a bead to prevent concurrent work
ddx bead close <id>             # close with evidence
ddx bead status
```

DDx owns bead storage, lifecycle (open → executing → closed), and queue
ordering (`ReadyExecution()`). HELIX content describes the shape of a
well-formed work item; DDx stores, claims, and closes it.

## The execution loop (`ddx work`)

The portable methodology's "the runtime executes ready work items, one
bounded pass at a time" maps to:

```bash
ddx work            # drain the ready queue end-to-end under DDx control
ddx work --once     # run exactly one bounded build pass, then exit
ddx bead execute <id>   # single-bead managed execution
```

`ddx work` loops only while true ready HELIX execution work exists, runs
one bounded build pass at a time, emits `NEXT_ACTION` codes that the
operator or wrapping skill interprets, and stops on `WAIT`, `BACKFILL`,
`GUIDANCE`, or `STOP`. DDx owns bead selection, managed-worktree
execution, close-with-evidence, retry suppression, and orphan recovery.

### Queue guard

Guard an autonomous loop on *true* ready work with `ddx bead ready`
(blocker-aware), not `ddx bead list --ready` (not equivalent):

```bash
ddx_ready_count() {
  # Strip advisory lines (e.g. upgrade notices) before piping to ddx jq.
  # awk skips lines until the first JSON delimiter, preserving multi-line JSON.
  ddx bead ready --json | awk 'found || /^[{[]/ { found=1; print }' | ddx jq 'length'
}
```

### Manual loop

The canonical DDx operator path once work is execution-ready:

```bash
while [ "$(ddx_ready_count)" -gt 0 ]; do
  ddx work --once
done

/helix check
```

After each `ddx work --once --json`, the HELIX skill parses
`results[].bead_id` and `results[].status` and applies post-cycle
supervisory policy to the bead DDx actually executed.

## Operator entrypoints

Operators interact with HELIX through the unified `/helix <mode>` skill in
agent harnesses (Claude Code, Codex, Gemini, etc.) and through DDx runtime
commands:

- `/helix input "<intent>"` — shape sparse intent into governed work
- `/helix align [scope]` — top-down reconciliation
- `/helix frame [scope]` — vision, PRD, feature specs
- `/helix design [scope]` — design documents
- `/helix evolve "<requirement>"` — thread a requirement through artifacts
- `/helix review [scope]` — fresh-eyes review after build
- `/helix check [scope]` — queue-drain decision
- `/helix polish [scope]` — refine work items before implementation
- `/helix experiment [scope]` — metric-driven optimization iteration
- `ddx work` — primary queue-drain substrate
- `ddx bead execute <id>` — single-bead managed execution
- `ddx bead create "Title" ...` — create well-structured tracker work items
- `ddx doctor` — verify and repair the HELIX install

## Work-item acquisition (bead-first under DDx)

The portable [bead-first reference](../../workflows/references/bead-first.md)
defines the runtime-neutral pattern: every action that modifies files is
governed by a work item. Under DDx the concrete commands are:

```bash
# Search for an existing governing bead
ddx bead list --status open --label kind:planning,action:<name> --json

# Claim it
ddx bead update <id> --claim

# Or create a new governing bead
ddx bead create "<action>: <scope description>" \
  --type task \
  --labels helix,activity:<appropriate-activity>,kind:planning,action:<name> \
  --set spec-id=<governing-artifact> \
  --description "<context-digest>...</context-digest>
<action-specific description of what this pass will do>" \
  --acceptance "<what done means for this action>"

# Close with evidence after measure/report
ddx bead close <id>
```

Planning-helix beads carry `kind:planning` plus `action:<name>` labels;
execution beads carry `activity:build`, `activity:deploy`, or
`activity:iterate`. `ddx bead create` bootstraps the bead graph and is the
one entry point exempt from requiring its own governing bead.

If execution order matters, encode it in the tracker: parent-child
structure for grouped scope and `ddx bead dep add <id> <dep-id>` for hard
prerequisites.

### Group related work into epics

Before a DDx run, group related work items into an epic so the runtime
stays on one coherent scope:

```bash
epic=$(ddx bead create "Epic: ..." --type epic ...)
ddx bead update hx-child1 --parent $epic
ddx bead update hx-child2 --parent $epic
ddx bead update hx-old --superseded-by hx-new
ddx bead close hx-old
```

## Review and acceptance findings

The review action files actionable findings as durable work items. Under
DDx these are beads with a `review-finding` label (plus a scope-appropriate
`area:*` label); acceptance-check failures are filed with
`acceptance-failure`. Query and resolve them like any other bead:

```bash
ddx bead list --label review-finding     # unresolved review findings
ddx bead list --label acceptance-failure  # unresolved acceptance failures
ddx bead close <id>                       # resolve a finding
```

## Model routing

When a HELIX skill mode dispatches planning, review, alignment, build, or
queue-steering work to DDx, stage tier intent is expressed with DDx routing
profiles (`--profile smart`, `--profile fast`, `--profile cheap`, or no
profile for DDx default policy). `--harness`, `--provider`, `--min-power`,
or `--max-power` may be passed when those values come from an operator flag,
environment variable, or work-item requirement. HELIX selects the stage and
the routing intent; the DDx agent service resolves the concrete
provider/model from its catalog. HELIX must not translate `smart` or `cheap`
into a provider-specific model name.

## Tracker conventions

- Work items are governed by the HELIX authority stack and should cite the
  canonical artifacts that authorize them.
- The tracker is the steering wheel for DDx execution: express
  decomposition, blockers, supersession, and follow-up work through tracker
  primitives, not out-of-band task lists.
- Closing a work item records completion; it does not redefine
  requirements, design, or tests. If execution changes behavior or scope,
  update the governing canonical artifacts explicitly.
- Execution-ready beads carry deterministic acceptance and
  success-measurement criteria — exact commands, named checks, or observable
  repo state DDx-managed execution can use to decide success without hidden
  human interpretation.

DDx-managed HELIX execution categories use native bead types, parents,
dependencies, `spec-id`, and labels rather than custom queue files:

- `activity:build` — story-level implementation work
- `activity:deploy` — rollout execution work
- `activity:iterate` and `kind:backlog` — prioritized follow-up work
- `kind:review` — reconciliation or audit work
- `kind:planning` plus `action:<name>` — work-item-governed planning actions
  such as `align`, `design`, or `polish`

## Quick-reference commands relocated from portable docs

The portable methodology docs describe runtime-neutral *actions*. The concrete
DDx commands that realize them are collected here so the portable docs can point
to one DDx home instead of carrying `ddx` command literals. Each subsection
names the source doc the commands were relocated from.

### From the HELIX Quick Reference Card (`workflows/REFERENCE.md`)

Bootstrap:

```bash
ddx bead init
ddx install helix
ddx doctor
```

The unified `helix` agent skill is published once per project; the operator
dispatches modes through `/helix <mode>`.

DDx execution commands:

```bash
/helix input "natural language request"
ddx work
ddx work --once
ddx bead execute hx-abc123
/helix check repo
/helix align repo
/helix backfill repo
/helix evolve "requirement description"
ddx bead create "Issue title" --type task --labels helix,activity:build
```

Preferred DDx operator path:

1. Use the `/helix input` skill mode for sparse intent.
2. Use `ddx work` queue execution for execution-ready work.
3. Use `/helix check`, `/helix review`, `/helix align`, `/helix design`, or
   `/helix polish` when HELIX must interpret or route the next action.

`ddx work` is the primary DDx queue-drain command for execution-ready beads.
`ddx bead execute <id>` runs one bounded bead. Execution-ready beads must carry
deterministic acceptance and success-measurement criteria: exact commands, named
checks, or observable repo state that DDx-managed execution can use to decide
success without hidden human interpretation.

Planning and quality commands:

```bash
/helix input "natural language request"
/helix input "natural language request" --autonomy high
/helix design [scope]
/helix design --rounds 8 auth
/helix polish [scope]
/helix polish --rounds 10
/helix review [scope]
/helix experiment [issue-id|goal]
/helix experiment --close
```

`/helix input` is the sparse-intent entrypoint for the autonomy-slider workflow.
`--autonomy` selects the HELIX-owned behavior contract (`low`, `medium`,
`high`); the expected default is `medium` when no override is supplied.

DDx tracker commands:

```bash
ddx bead ready --json
ddx bead update <id> --claim
ddx bead show <id>
ddx bead dep tree <id>
ddx bead blocked --json
ddx bead close <id>
ddx bead status
ddx bead import --from jsonl --file .ddx/beads.jsonl
ddx bead export
```

See `ddx bead --help` for full tracker conventions and setup guidance.

DDx tracker labeling — labels are organizational conventions for triage and
traceability; they are not part of the portable HELIX methodology. Recommended
DDx labels:

- `helix` identifies HELIX-managed issues in a DDx tracker.
- Activity labels: `activity:frame`, `activity:design`, `activity:test`,
  `activity:build`, `activity:deploy`, `activity:iterate`, `kind:review`.
- Kind labels: `kind:build`, `kind:deploy`, `kind:backlog`, `kind:review`.
- Traceability labels: `story:US-XXX`, `feature:FEAT-XXX`, `area:<name>`,
  `source:metrics`.

DDx-specific decision guide:

- Starting new work or a large scope: run `/helix design`, then `/helix polish`,
  then `ddx work`.
- Starting from sparse user intent instead of a pre-shaped issue: run `/helix
  input` and set autonomy when needed.
- Ready execution issues exist: use `ddx work` for queue draining.
- Work lacks design authority for safe execution: run `/helix design`, or let
  `/helix check` dispatch it.
- Specs changed and open work needs issue refinement before implementation: run
  `/helix polish`, or let `/helix check` dispatch it.
- No ready execution issue, but the planning stack exists and next work is
  unclear: run `/helix align` and record the review output.
- Canonical docs are missing or too incomplete to execute safely: run `/helix
  backfill`.
- Work exists but is blocked or already in progress: stop and wait.
- The queue drains: run `/helix check`, not a blind loop and not an ad hoc
  ready-list loop.
- After implementing an issue: run `/helix review`.

DDx validation commands — when changing skill packaging docs or the DDx
execution contract, the deterministic harnesses are:

```bash
bash tests/validate-skills.sh
git diff --check
```

### From the HELIX Workflow Quick Start (`workflows/QUICKSTART.md`)

Bootstrap a repo:

```bash
ddx bead init
ddx install helix
ddx doctor
```

Notes:

- `ddx bead init` creates the tracker workspace.
- `ddx install helix` installs the HELIX plugin into the DDx plugin directory
  and installs the HELIX skill into `~/.agents/skills` and `~/.claude/skills`.
- `ddx doctor` verifies and repairs the installation — creates missing plugin
  symlinks and skill links in the target repo.
- The repo exposes the unified `helix` agent skill at `.agents/skills` and
  `.claude/skills` (symlinks to `skills/`).
- For Claude Code: `claude --plugin-dir /path/to/helix` discovers skills
  automatically without manual install.

DDx execution commands:

```bash
ddx work
ddx bead execute <id>
/helix check repo
/helix align repo
/helix backfill repo
```

Tracker introspection:

```bash
ddx bead --help
ddx bead ready --json
ddx bead ready --execution
ddx bead show <id>
```

Minimal operator loop — if you are not using `ddx work`, use the bounded manual
loop:

```bash
while [ "$(ddx bead ready --json | awk 'found || /^[{[]/ { found=1; print }' | ddx jq 'length')" -gt 0 ]; do
  ddx bead execute "$(ddx bead ready --json --execution | ddx jq -r '.[0].id')"
done

/helix check
```

Validation — when you change skill packaging docs or the workflow contract, run:

```bash
bash tests/validate-skills.sh
git diff --check
```

### From the Artifact Hierarchy (`workflows/artifact-hierarchy.md`)

Under the DDx reference runtime, the queue controls for the artifact hierarchy
are:

```bash
# Inspect the current queue
ddx bead ready --json

# Execute one ready work item
ddx bead execute <id>

# Decide the next action when the queue drains
/helix check

# Drain the ready queue
ddx work
```

### From the Workflow Conventions (`workflows/conventions.md`)

DDx workspace layout — DDx installs HELIX content at `workflows/` and stores
work items in `.ddx/beads.jsonl`. A DDx-managed HELIX project layout includes
this workspace alongside `docs/helix/`:

```
project-root/
├── .ddx/                    # DDx workspace (beads, plugins, hooks)
│   ├── beads.jsonl          # Work-item tracker storage
│   └── plugins/helix/       # Installed HELIX content
├── .agents/skills/          # Published HELIX skills (project-level)
├── skills/                  # Skill sources for the HELIX package
└── docs/helix/              # Canonical HELIX activity artifacts
```

DDx shared workflow root — under DDx, the shared workflow resource root is
`workflows/`. Skills reference shared assets through that package-relative root.
Installers and plugins must preserve `.agents/skills/`, `skills/`, and
`workflows/` together.

DDx work-item tracker — DDx uses a JSONL-backed tracker. See `ddx bead --help`
for the full command surface. Common tracker introspection:

- `ddx bead ready`, `ddx bead blocked`, and `ddx bead dep tree` replace custom
  HELIX status fields for queue inspection.
- The `helix` label identifies HELIX-managed issues in a DDx tracker.

DDx template paths — DDx-installed templates live at:

- artifact templates: `workflows/activities/<activity>/artifacts/<type>/template.md`
- refinement template: `workflows/templates/refinement-log.md`

Example artifact bootstrap:

```bash
sed -n '1,120p' workflows/activities/01-frame/artifacts/prd/prompt.md
cp -f workflows/activities/01-frame/artifacts/prd/template.md \
      docs/helix/01-frame/prd.md
```

## See also

- [`workflows/README.md`](../../workflows/README.md) — runtime-neutral
  methodology overview.
- [`workflows/EXECUTION.md`](../../workflows/EXECUTION.md) — runtime-neutral
  execution-integration model (bead-first, measure, report, check routing).
- [`workflows/references/bead-first.md`](../../workflows/references/bead-first.md)
  — the portable work-item acquisition pattern.
- [CONTRACT-003](../helix/02-design/contracts/CONTRACT-003-ddx-adapter-boundary.md)
  — the DDx adapter boundary.
- [`docs/resources/agents/ddx-plugins.md`](../resources/agents/ddx-plugins.md)
  — DDx plugin mechanism research notes.
