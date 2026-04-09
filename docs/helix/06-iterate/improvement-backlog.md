# Improvement Backlog

`improvement-backlog` is restored as the canonical iterate-phase inventory of
prioritized follow-up work.

## Decision

This artifact is restored rather than retired. The current HELIX contract still
needs a durable place to summarize and rank improvement work, even though the
built-in tracker holds the executable tasks themselves.

## Why It Exists

- The tracker stores executable work items.
- The backlog summarizes and prioritizes those items.
- Iteration learnings should shape the next cycle without turning the backlog
  into a loose collection of notes.

## Canonical Inputs

- `docs/helix/06-iterate/metrics-dashboard.md`
- `docs/helix/06-iterate/lessons-learned.md`
- retrospective notes
- tracker issues created from the iteration

## Minimum Prompt Bar

- Turn learnings into ranked follow-up work.
- Prefer tracker-backed items over vague ideas.
- Use evidence from metrics, feedback, and retrospectives.
- Make the next iteration candidate obvious.
- Keep the backlog focused on prioritization, not implementation detail.

## Minimum Template Bar

- iteration or release identifier
- prioritization rules
- backlog table with tracker references
- evidence for each item
- explicit selection for the next iteration

## Canonical Replacement Status

`improvement-backlog` is not replaced by tracker primitives. The tracker is the
execution system; the backlog remains the prioritization surface that bridges
iteration learnings to the next planning pass.
