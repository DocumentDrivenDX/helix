---
ddx:
  id: helix.workflow.quickstart
  depends_on:
    - helix.workflow
  review:
    self_hash: ed890bff9d7718cc5d832b2024f1e7d7c01028c62ee62dbe3718634db566d26e
    deps:
      helix.workflow: 1b6caaf3ebc6950bc4fff314e09bc0ee1b71deaa9223a4a70a13f399291ad98c
    reviewed_at: "2026-05-26T03:19:52Z"
---
# HELIX Workflow Quick Start Guide

Use this guide to start a repo on the current HELIX contract without learning
the whole workflow tree first. The methodology body below is runtime-neutral.
For DDx-specific bootstrap, queue control, and validation commands, see
[docs/install/ddx.md](../docs/install/ddx.md).

## Start Here

Read these files in order when you need the canonical contract:

1. [README.md](README.md) — high-level model, artifact authority
   hierarchy, and runtime boundary
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
`workflows/activities/<activity>/artifacts/` when HELIX is installed
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

## Runtime Integration

The bootstrap, queue-control, manual-loop, and validation commands for a given
runtime live in that runtime's install guide. For DDx-specific commands, see
[docs/install/ddx.md](../docs/install/ddx.md). For the runtime-neutral execution
model, read [EXECUTION.md](EXECUTION.md).
