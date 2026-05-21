---
ddx:
  id: helix.workflow.quickstart
  depends_on:
    - helix.workflow
  review:
    self_hash: 376d677e73edbdc44dd24bdf39cb5499c2d7c07dbcafe5e4dc14a8bec50e97f2
    deps:
      helix.workflow: 1225132b3050598055eacb5462639824d78ac204cca2cbeda3611766532e79c8
    reviewed_at: "2026-05-15T04:11:24Z"
---
# HELIX Workflow Quick Start Guide

Use this guide to start a repo on the current HELIX contract without learning
the whole workflow tree first. The methodology body below is runtime-neutral.
For DDx-specific bootstrap, queue control, and validation commands, see the
[DDx Integration Appendix](#ddx-integration-appendix) at the end of this file.

## Start Here

Read these files in order when you need the canonical contract:

1. [README.md](README.md) — high-level model, authority order, and runtime
   boundary
2. [REFERENCE.md](REFERENCE.md) — activity summary, methodology actions, and
   decision guide
3. [conventions.md](conventions.md) — documentation layout and naming
4. The runtime integration appendix for your runtime (see [DDX.md](DDX.md) for
   the DDx reference integration)

Use the bounded action prompts only when you are doing the corresponding work:

- [implementation.md](actions/implementation.md)
- [check.md](actions/check.md)
- [reconcile-alignment.md](actions/reconcile-alignment.md)
- [backfill-helix-docs.md](actions/backfill-helix-docs.md)

## Build The Canonical Planning Stack

Prompts and templates live under
`.ddx/plugins/helix/workflows/activities/<activity>/artifacts/` when HELIX is installed
as a DDx plugin. Other runtimes may resolve the same content from their own
package layout. Use them to draft or refine the canonical docs under
`docs/helix/`.

Typical order:

1. Optional discovery in `docs/helix/00-discover/`
   Capture product vision, business case, and opportunity context when needed.
2. Frame in `docs/helix/01-frame/`
   Write the PRD, feature specs, user stories, and supporting requirement docs.
3. Design in `docs/helix/02-design/`
   Define architecture, ADRs, contracts, feature-level solution designs, and
   story-level technical designs.
4. Test in `docs/helix/03-test/` and `tests/`
   Write the test plan and failing tests before implementation.
5. Build in `docs/helix/04-build/` plus the runtime's work-item tracker
   Keep project build guidance in docs and story-level execution work in the
   runtime tracker.
6. Deploy in `docs/helix/05-deploy/` plus the runtime tracker
   Keep rollout docs canonical and rollout tasks in the tracker.
7. Iterate in `docs/helix/06-iterate/`
   Capture backlog, lessons, reviews, and the explicit next-cycle selection.

## Create Execution Work

HELIX execution runs through the runtime's native work-item tracker, not
HELIX-specific task files. Build, deploy, and iterate execution work items
should:

- use the runtime's native issue types and dependencies
- cite the governing canonical docs (e.g. via `spec-id` or the issue
  description)
- carry at least one activity label (`activity:build`, `activity:deploy`, etc.) when the
  runtime supports labels
- stay small enough to close independently

See the runtime integration appendix for the concrete commands and conventions
your tracker uses.

## Run The Queue

Once execution work exists, the runtime owns queue selection, claim/execute/
close mechanics, and orphan recovery. HELIX governs:

- what counts as an execution-ready work item (deterministic acceptance and
  success-measurement criteria)
- which methodology action to run when the ready queue drains (build, design,
  polish, align, backfill, wait, guidance, stop)
- when to file follow-up work as durable tracker items rather than prose-only
  memory

Execution rules:

- Execute one ready work item at a time.
- When the ready queue drains, run the bounded `check` action to decide the
  next step.
- Run alignment only when the plan exists but the next work set is unclear.
- Run backfill only when the canonical stack is missing or too weak.
- Do not drive the queue with an unfiltered ready-list loop.

## Common Next Steps

- Need artifact structure or naming rules:
  Read [conventions.md](conventions.md) and the relevant activity README.
- Need queue behavior:
  See the runtime integration appendix.
- Need a top-down audit:
  Run alignment with [reconcile-alignment.md](actions/reconcile-alignment.md).
- Need missing docs reconstructed:
  Run backfill with [backfill-helix-docs.md](actions/backfill-helix-docs.md).

## DDx Integration Appendix

The commands and paths below apply to DDx-managed HELIX installations. They
are not required to understand or adopt the HELIX methodology.

### Bootstrap A Repo

```bash
ddx bead init
ddx install helix
ddx doctor
```

Notes:

- `ddx bead init` creates the tracker workspace.
- `ddx install helix` creates `~/.ddx/plugins/helix` and installs the HELIX
  skill into `~/.agents/skills` and `~/.claude/skills`.
- `ddx doctor` verifies and repairs the installation — creates missing
  `.ddx/plugins/helix` symlinks and skill links in the target repo.
- The repo exposes the unified `helix` agent skill at `.agents/skills` and
  `.claude/skills` (symlinks to `skills/`).
- For Claude Code: `claude --plugin-dir /path/to/helix` discovers skills
  automatically without manual install.

### DDx execution commands

Preferred DDx commands:

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

### Minimal Operator Loop

If you are not using `ddx work`, use the bounded manual loop from
[EXECUTION.md](EXECUTION.md):

```bash
while [ "$(ddx bead ready --json | awk 'found || /^[{[]/ { found=1; print }' | ddx jq 'length')" -gt 0 ]; do
  ddx bead execute "$(ddx bead ready --json --execution | ddx jq -r '.[0].id')"
done

/helix check
```

### Validation

When you change skill packaging docs or the workflow contract, run:

```bash
bash tests/validate-skills.sh
git diff --check
```

For DDx tracker labels, issue examples, and full queue/loop semantics, read
[EXECUTION.md](EXECUTION.md) and run `ddx bead --help`.
