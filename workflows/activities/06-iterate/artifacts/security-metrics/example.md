---
ddx:
  id: example.security-metrics.depositmatch
  authoring:
    home: repo
  depends_on:
    - example.metrics-dashboard.depositmatch.csv-import
    - example.monitoring-setup.depositmatch
    - example.security-tests.depositmatch
    - example.runbook.depositmatch
---

# Security Metrics - Pilot Iteration 1

## Incident Response

| Metric | Current | Target | Trend |
|--------|---------|--------|-------|
| Mean Time to Detect (MTTD) | baseline: 4 minutes for synthetic telemetry alert | under 5 minutes | baseline set |
| Mean Time to Respond (MTTR) | baseline: 18 minutes for synthetic import outage | under 30 minutes | baseline set |
| Incidents resolved within SLA | 1 of 1 synthetic incidents | 100% | baseline set |
| False-positive alert rate | 1 of 6 security alerts | under 20% | baseline set |

**Incident Summary**

- Total incidents this period: 1 synthetic restricted-telemetry drill.
- Critical (required immediate response): 0 production incidents.
- Fully resolved: 1 drill resolved through runbook.

**Root Causes** (critical and high only)

| Root Cause | Count | Mitigation Status |
|------------|-------|-------------------|
| none | 0 | no critical/high production incident this period |

## Vulnerability Management

| Metric | Current | Target | Trend |
|--------|---------|--------|-------|
| Open critical vulnerabilities | 0 | 0 | baseline set |
| Open high vulnerabilities | 1 development dependency | 0 before pilot go-live | baseline set |
| MTTR for critical vulns | not applicable | under 2 business days | baseline set |
| Patch compliance rate | 94% direct dependencies current | 95% before pilot go-live | baseline set |

## Application Security

| Metric | Current | Target | Trend |
|--------|---------|--------|-------|
| SAST findings (new this period) | 2 medium findings, both in non-production code paths | 0 high/critical, medium triaged within 5 days | baseline set |
| DAST findings (new this period) | not run; staging environment not stable | run before pilot go-live | baseline set |
| Dependency vulnerabilities (direct) | 1 high, 0 critical | 0 high/critical before pilot go-live | baseline set |
| Security review coverage | 5 of 5 high-risk controls mapped to tests | 100% high-risk controls | baseline set |

## Compliance Status

| Requirement | Status | Open Gaps | Target Resolution |
|-------------|--------|-----------|-------------------|
| FTC Safeguards applicability review | pending counsel | confirm pilot-data obligations | before live customer data |
| Restricted telemetry policy | implemented in tests, not production-proven | production log scan needs first live run | first pilot day |
| Support access auditability | implemented in tests | support grant review cadence not exercised | first weekly operations review |
| Source CSV retention | designed, not verified in production | retention job dry run needed | before second pilot customer |

## Security Posture Trend

- **Overall risk level**: Medium - Trend: baseline set.
- **Summary**: Security controls are test-mapped, but go-live remains blocked
  by one high dependency vulnerability, pending counsel review, and unproven
  production log scanning.

## Recommendations

Each recommendation must be specific enough to create a tracker issue.

| Recommendation | Priority | Rationale | Expected Impact |
|----------------|----------|-----------|-----------------|
| Upgrade or replace the high-risk direct dependency before pilot go-live | High | Direct high vulnerability violates go-live target | Removes release blocker |
| Run DAST against stable staging once deployment checklist passes | High | DAST has no baseline yet | Establishes API/browser attack-surface baseline |
| Exercise source CSV retention job with pilot fixtures | Medium | Retention control is designed but not production-verified | Reduces data-retention uncertainty |
| Add weekly support grant review to routine operations evidence | Medium | Support access control is test-covered but not operationally exercised | Improves support-access audit confidence |
