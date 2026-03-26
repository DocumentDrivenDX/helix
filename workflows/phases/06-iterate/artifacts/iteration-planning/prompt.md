# Iteration Planning Generation

## Required Inputs
- `docs/helix/06-iterate/improvement-backlog.md` - Improvement backlog
- backlog issues in tracker
- `docs/helix/06-iterate/lessons-learned.md` - Lessons learned
- Resource availability

## Produced Output
- `docs/helix/06-iterate/next-iteration.md` - Next iteration plan

## Prompt

Plan the next iteration by selecting a small coherent set of backlog issues.

Keep the plan focused on scope, goals, sequencing, required canonical updates, risks, and measurable success criteria. Express in-scope work as issue IDs, not prose task lists.

Use the template at `workflows/phases/06-iterate/artifacts/iteration-planning/template.md`.
Use HELIX tracker guidance at `workflows/TRACKER.md`.

## Completion Criteria
- [ ] Scope is well-defined
- [ ] In-scope work is expressed as issue IDs
- [ ] Goals are measurable
- [ ] Resources allocated
- [ ] Risks identified with mitigations
