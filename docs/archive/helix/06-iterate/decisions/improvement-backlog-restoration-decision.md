# Improvement Backlog — Restoration Decision

> Historical decision; superseded by the worked example at `docs/helix/06-iterate/improvement-backlog.md`.

`improvement-backlog` is restored as the canonical iterate-activity inventory of
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
- `docs/helix/06-iterate/security-metrics.md`
- tracker issues created from the iteration

## Minimum Prompt Bar

- Turn learnings into ranked follow-up work.
- Prefer tracker-backed items over vague ideas.
- Use evidence from metrics, security findings, and iteration follow-up issues.
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

The deleted `iteration-planning` artifact stays retired as a standalone
document. Its useful responsibility already lives here: the backlog must make
the next iteration candidate explicit and tie it to evidence-backed tracker
work.

If a team needs a separate meeting note or staffing worksheet, that may exist
locally, but it is not a canonical HELIX artifact. Reintroducing
`iteration-planning` would split one decision across two thin docs.
