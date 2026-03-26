# Metrics Dashboard Generation

## Required Inputs
- Application performance monitoring data
- Infrastructure monitoring data
- User analytics
- Business metrics
- Previous dashboard (if available) for trend comparison

## Produced Output
- `docs/helix/06-iterate/metrics-dashboard.md` - Current metrics dashboard

## Prompt

Create a concise metrics dashboard that turns raw data into decisions.

Focus on the few business, technical, and quality metrics that matter most, plus anomalies, actions, and week-over-week change. Avoid vanity metrics and explain why each change matters.

Use the template at `workflows/phases/06-iterate/artifacts/metrics-dashboard/template.md`.

## Completion Criteria
- [ ] All metrics have current values and trends
- [ ] Anomalies are explained
- [ ] Recommendations are specific and actionable
- [ ] Historical comparison provides context
