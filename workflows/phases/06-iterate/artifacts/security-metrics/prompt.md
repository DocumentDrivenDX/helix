# Security Metrics Prompt

Create a security metrics report for one iteration.

## Required Inputs
- Security monitoring and incident data for the iteration period
- Vulnerability scan results (SAST, DAST, dependency scans)
- Compliance audit findings, if applicable
- Previous security metrics report for trend comparison

## Produced Output
- `docs/helix/06-iterate/security-metrics.md`

## Focus

Report on security posture across four areas: incident response, vulnerability
management, application security, and compliance. For each area, state the
current value, the target, and the trend. Do not repeat raw data in prose —
summarize what the numbers mean and what action they justify.

Trend comparison against the previous period is required. If no prior report
exists, note the baseline and set targets for the next iteration.

Every recommendation must be specific enough to become a tracker issue. Vague
recommendations ("improve security posture") are not acceptable.

## Completion Criteria
- [ ] All four metric areas populated with current data
- [ ] Trend column populated for each metric (or baseline set if first report)
- [ ] At least one recommendation per area that is actionable as a tracker issue
- [ ] Root cause included for any critical or high-severity incidents
- [ ] Report covers the same iteration period as `metrics-dashboard.md`

Use the template at `.ddx/plugins/helix/workflows/phases/06-iterate/artifacts/security-metrics/template.md`.
