# Story Iteration Report Generation

## Storage Location

`docs/helix/06-iterate/IR-XXX-[story-name].md`

## Required Inputs
- User story (US-XXX) with acceptance criteria
- Deployment issues and observation period data
- Production metrics for the story

## Produced Output
- `docs/helix/06-iterate/IR-XXX-[story-name].md` - Post-deployment iteration report

## Prompt

Create a post-deployment iteration report for a single user story. Capture outcomes, learnings, and follow-up work concisely.

Produce:

1. **Story reference** - Link to user story, deployment issues, observation period
2. **Outcome summary** - Status (Success/Partial/Issues) and one-sentence takeaway
3. **Acceptance criteria review** - Target vs. actual for each criterion (Pass/Partial/Fail)
4. **Metrics and evidence** - Baseline, target, and actual values for relevant metrics
5. **What worked / what did not** - Patterns to repeat or avoid
6. **Issues and resolutions** - Each issue with impact, resolution, and follow-up flag
7. **Derived backlog issues** - Actionable follow-up as tracker issues (not prose tasks)
8. **Canonical updates** - Artifacts that need updating because reality diverged from specs

Use the template at `workflows/phases/06-iterate/artifacts/story-iteration-report/template.md`.

## Completion Criteria
- [ ] All acceptance criteria reviewed with actual outcomes
- [ ] Follow-up work captured as backlog issues
- [ ] Required canonical updates identified
