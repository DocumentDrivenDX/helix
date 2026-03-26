# Security Metrics Generation

## Required Inputs
- Security monitoring and incident data
- Vulnerability scan results
- Compliance audit findings
- Previous security metrics report (if available)

## Produced Output
- `docs/helix/06-iterate/security-metrics.md` - Security metrics report

## Prompt

Create a concise security metrics report that drives follow-up work.

Focus on incident response, vulnerabilities, application security, compliance posture, trends, and the few recommendations that justify action. Keep the report short and avoid repeating raw data in prose.

Use the template at `workflows/phases/06-iterate/artifacts/security-metrics/template.md`.

## Completion Criteria
- [ ] All metric categories populated with current data
- [ ] Trends compared against previous periods
- [ ] Recommendations are prioritized and actionable
- [ ] Root cause analysis included for incidents
