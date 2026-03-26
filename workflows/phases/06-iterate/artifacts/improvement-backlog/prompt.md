# Improvement Backlog Generation

## Required Inputs
- `docs/helix/06-iterate/lessons-learned.md` - Lessons learned
- `docs/helix/06-iterate/feedback-analysis.md` - User feedback
- `docs/helix/06-iterate/metrics-dashboard.md` - Production metrics

## Produced Output
- `docs/helix/06-iterate/improvement-backlog.md` - Prioritized backlog index
- tracker issues labeled `helix`, `phase:iterate`, `kind:backlog`

## Prompt

Create the next improvement backlog as a concise, tracker-backed index.

Use the source documents to identify only actionable follow-up work. Create or update one backlog issue per actionable item, and keep observations, risks, and open questions out of the issue list.

In the index, prioritize the issues and note which ones need canonical artifact updates before execution.

Use the index template at:
`workflows/phases/06-iterate/artifacts/improvement-backlog/template.md`

Use tracker guidance at:
`workflows/TRACKER.md`

## Completion Criteria
- [ ] All improvement sources reviewed
- [ ] Every actionable item has a backlog issue
- [ ] Issues are prioritized consistently in the index
- [ ] Dependencies are identified
- [ ] The index references issue IDs explicitly
