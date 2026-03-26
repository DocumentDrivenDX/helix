---
name: helix-align
description: Run the HELIX alignment action. Use when the user wants `helix align` behavior.
argument-hint: "[scope]"
---

# Align

Use this skill for repo-wide or area-scoped reconciliation reviews.

## When To Use

- the user asks for an alignment review, reconciliation, traceability audit, or drift analysis
- the project uses HELIX artifacts or a similar planning stack
- the user wants deterministic follow-up work in the tracker (`helix tracker`)
- the review should produce one durable consolidated report plus ephemeral review/execution issues

## Startup

Reference docs:

- `workflows/actions/reconcile-alignment.md`
- `workflows/templates/alignment-review.md`
- `workflows/TRACKER.md`

## Core Rules

- Review top-down, not code-first.
- Planning intent comes from canonical artifacts, not from implementation.
- Use the HELIX authority order from the references.
- Use the built-in tracker only: `helix tracker` issues, parents, dependencies, `spec-id`, and labels.
- Create or reconcile one review epic plus one review issue per functional area.
- Create execution issues only after the consolidated report exists.

## Output Model

Produce:

1. Review epic in the tracker
2. Review issues in the tracker
3. Durable report at `docs/helix/06-iterate/alignment-reviews/AR-YYYY-MM-DD[-scope].md`
4. Execution issues only for approved gaps

## Required Evidence

Every non-trivial finding must cite:

- planning evidence
- implementation evidence
- a classification
- a recommended resolution direction

Use these references as needed:

- [review-flow.md](references/review-flow.md)
- [alignment-report.md](references/alignment-report.md)
- [tracker.md](references/tracker.md)
