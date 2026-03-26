# Feedback Analysis Generation

## Required Inputs
- User feedback from all available channels (in-app, support, reviews, community)
- Previous feedback analysis (if available) for trend comparison

## Produced Output
- `docs/helix/06-iterate/feedback-analysis.md` - Synthesized feedback report

## Prompt

Synthesize user feedback into a concise, decision-oriented report.

Focus on recurring patterns, user impact, and the next action. Keep one-off comments out unless they explain a broader trend.

Produce:

1. Summary: volume, overall sentiment, trend, top themes
2. Key findings: recurring patterns with frequency, sentiment, impact, and action
3. Requests and pain points: prioritized by volume and severity
4. What users like: patterns worth protecting
5. Recommendations: critical, high-value, and quick wins
6. Previous actions: whether last cycle's changes helped

Keep the report short and specific.

Use the template at `workflows/phases/06-iterate/artifacts/feedback-analysis/template.md`.

## Completion Criteria
- [ ] Patterns identified across multiple feedback sources
- [ ] Recommendations are prioritized and actionable
- [ ] Previous actions are evaluated for effectiveness
- [ ] Candidate backlog issues identified for follow-up work
