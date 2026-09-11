# HELIX on DDx

DDx (Document-Driven Development Experience) is the HELIX reference
runtime. This page is the home for all DDx-specific packaging, naming,
and invocation detail: the concrete `ddx` commands that realize the
runtime-neutral actions the methodology describes. What HELIX is, the
marker, catalog resolution, autonomy, and verification are in the
[install guide](README.md).

> **Boundary.** HELIX provides the artifact catalog, the routing skill,
> and the artifact schema. DDx provides the work-item tracker, the
> execution loop, dispatch, and evidence capture. See
> [CONTRACT-003](../helix/02-design/contracts/CONTRACT-003-ddx-adapter-boundary.md)
> for the full adapter boundary. Nothing on this page is a HELIX
> requirement; another runtime supplies its own equivalents (or none).

## Install

```bash
ddx bead init        # create the tracker workspace (once per repo)
ddx install helix    # clone HELIX into ~/.ddx/plugins/helix/
ddx doctor           # verify and repair the install
```

`ddx install helix` uses the Claude Code plugin format, so the same tree
also serves as a `claude --plugin-dir` target. The catalog source that
HELIX docs call `workflows/` is vendored at `<plugin-root>/workflows/`
(for example `.ddx/plugins/helix/workflows/`). The install also links the
`helix` skill into `~/.agents/skills` and `~/.claude/skills`; `ddx doctor`
creates missing plugin symlinks and skill links in the target repo. Refresh
a local snapshot with `ddx install helix --force`.

A DDx-managed HELIX project layout:

```
project-root/
├── .ddx/                    # DDx workspace (beads, plugins, hooks)
│   ├── beads.jsonl          # Work-item tracker storage
│   └── plugins/helix/       # Installed HELIX content
├── .agents/skills/          # Published HELIX skills (project-level)
├── skills/                  # Skill sources for the HELIX package
└── docs/helix/              # Canonical HELIX activity artifacts
```

Installers and plugins must preserve `.agents/skills/`, `skills/`, and
`workflows/` together. DDx-installed templates live at
`workflows/activities/<activity>/artifacts/<type>/template.md`; the
refinement template at `workflows/templates/refinement-log.md`.

## DDx stores work items as beads

DDx's concrete work item is the bead. Where the portable methodology says
"work item", DDx means a bead. Beads are stored in `.ddx/beads.jsonl` and
managed through `ddx bead`:

```bash
ddx bead ready                  # open beads with all deps satisfied
ddx bead ready --execution      # the next execution-ready bead
ddx bead show <id>
ddx bead dep tree <id>
ddx bead blocked --json
ddx bead update <id> --claim    # claim a bead to prevent concurrent work
ddx bead close <id>             # close with evidence
ddx bead status
ddx bead import --from jsonl --file .ddx/beads.jsonl
ddx bead export
```

DDx owns bead storage, lifecycle (open → executing → closed), and queue
ordering (`ReadyExecution()`). HELIX content describes the shape of a
well-formed work item; DDx stores, claims, and closes it. See
`ddx bead --help` for the full tracker surface.

## The execution loop (`ddx work`)

The portable methodology's "the runtime executes ready work items, one
bounded pass at a time" maps to:

```bash
ddx work                # drain the ready queue end-to-end under DDx control
ddx work --once         # run exactly one bounded build pass, then exit
ddx bead execute <id>   # single-bead managed execution
```

`ddx work` loops only while true ready HELIX execution work exists, runs
one bounded build pass at a time, emits `NEXT_ACTION` codes that the
operator or wrapping skill interprets, and stops on `WAIT`, `BACKFILL`,
`GUIDANCE`, or `STOP`. DDx owns bead selection, managed-worktree
execution, close-with-evidence, retry suppression, and orphan recovery.

Execution-ready beads must carry deterministic acceptance and
success-measurement criteria: exact commands, named checks, or observable
repo state that DDx-managed execution can use to decide success without
hidden human interpretation.

### Queue guard

Guard an autonomous loop on true ready work with `ddx bead ready`
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

Without `ddx work`, substitute
`ddx bead execute "$(ddx bead ready --json --execution | ddx jq -r '.[0].id')"`
for `ddx work --once` in the same loop.

After each `ddx work --once --json`, the HELIX skill parses
`results[].bead_id` and `results[].status` and applies post-cycle
supervisory policy to the bead DDx actually executed.

## Operator entrypoints

Operators reach HELIX modes through the unified `/helix <mode>` skill in
the agent harness (`/helix input "<intent>"`, `/helix design [scope]
--rounds N`, `/helix polish --rounds N`, `/helix experiment --close`, and
the rest of the routing table in the skill) and reach the runtime through
`ddx work` (queue drain), `ddx bead execute <id>` (one bead),
`ddx bead create "Title" ...` (well-structured work items), and
`ddx doctor` (verify and repair the install).

### Decision guide

- Starting new work or a large scope: `/helix design`, then `/helix polish`,
  then `ddx work`.
- Starting from sparse user intent instead of a pre-shaped issue:
  `/helix input`, setting autonomy when needed.
- Ready execution issues exist: `ddx work`.
- Work lacks design authority for safe execution: `/helix design`, or let
  `/helix check` dispatch it.
- Specs changed and open work needs refinement before implementation:
  `/helix polish`, or let `/helix check` dispatch it.
- No ready execution issue, but the planning stack exists and next work is
  unclear: `/helix align` and record the review output.
- Canonical docs are missing or too incomplete to execute safely:
  `/helix backfill`.
- Work exists but is blocked or already in progress: stop and wait.
- The queue drains: `/helix check`, not a blind loop and not an ad hoc
  ready-list loop.
- After implementing an issue: `/helix review`.

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
- `ddx bead ready`, `ddx bead blocked`, and `ddx bead dep tree` replace
  custom HELIX status fields for queue inspection.

DDx-managed HELIX execution categories use native bead types, parents,
dependencies, `spec-id`, and labels rather than custom queue files.
Labels are triage and traceability conventions, not portable HELIX
methodology:

- `helix` marks HELIX-managed issues; `activity:build` is story-level
  implementation, `activity:deploy` rollout work, `activity:iterate` and
  `kind:backlog` prioritized follow-up, `kind:review` reconciliation or
  audit, and `kind:planning` plus `action:<name>` a work-item-governed
  planning action such as `align`, `design`, or `polish`.
- Other activity and kind labels: `activity:frame`, `activity:design`,
  `activity:test`, `kind:build`, `kind:deploy`.
- Traceability: `story:US-XXX`, `feature:FEAT-XXX`, `area:<name>`,
  `source:metrics`.

## Validation

When changing skill packaging docs or the DDx execution contract, the
deterministic harnesses are:

```bash
bash tests/validate-skills.sh
git diff --check
```

The recorded DDx integration scenarios live in `tests/workflows/ddx/`.

## See also

- [`workflows/README.md`](../../workflows/README.md): runtime-neutral
  methodology overview.
- [`workflows/references/bead-first.md`](../../workflows/references/bead-first.md):
  the portable work-item acquisition pattern.
- [CONTRACT-003](../helix/02-design/contracts/CONTRACT-003-ddx-adapter-boundary.md):
  the DDx adapter boundary.
- [`docs/resources/agents/ddx-plugins.md`](../resources/agents/ddx-plugins.md):
  DDx plugin mechanism research notes.
- [Install guide](README.md)
