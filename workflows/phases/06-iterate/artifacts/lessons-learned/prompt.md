# Lessons Learned Generation

## Required Inputs
- `docs/helix/06-iterate/metrics-dashboard.md` - Production metrics
- `docs/helix/06-iterate/feedback-analysis.md` - User feedback
- Project retrospective notes

## Produced Output
- `docs/helix/06-iterate/lessons-learned.md` - Documented learnings

## Prompt

Document only the lessons that should change future behavior.

Use production metrics, feedback, and retrospective notes to capture the iteration summary, what worked, what did not work, estimation misses, technical debt, process changes, and recurring patterns. Keep each item short and tied to a concrete follow-up.

Use the template at `workflows/phases/06-iterate/artifacts/lessons-learned/template.md`.

## Completion Criteria
- [ ] Both successes and failures documented with root causes
- [ ] Candidate backlog issues identified for actionable follow-up
- [ ] Recurring patterns flagged for systemic fixes
