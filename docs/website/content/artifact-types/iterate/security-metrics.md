---
title: "Security Metrics"
linkTitle: "Security Metrics"
slug: security-metrics
activity: "Iterate"
artifactRole: "supporting"
weight: 13
generated: true
---

## Purpose

Iteration-level security posture report that turns incidents, vulnerabilities,
control results, and compliance gaps into trend-backed improvement work.

## Example

<details open>
<summary>Show a worked example of this artifact</summary>

``````markdown
---
ddx:
  id: example.security-metrics.depositmatch
  depends_on:
    - example.metrics-dashboard.depositmatch.csv-import
    - example.monitoring-setup.depositmatch
    - example.security-tests.depositmatch
    - example.runbook.depositmatch
  review:
    self_hash: dbe60cb67a0fa6e2ec71dc36381bb2b8386de31e7d25978a3071b0f171688709
    deps:
      example.metrics-dashboard.depositmatch.csv-import: 55c3a758e5ff9beef2651c46bf668c6a31eab8be6a1f64662166de4135061398
      example.monitoring-setup.depositmatch: cd2e8ecd82900c19affde80ab89f2ad3e7f5ff19ab3956a8da5dcee8e710b4af
      example.runbook.depositmatch: 1f52bd1ba196f06837695269f3fee1829dd734eeccdb0ea4274c86c895270229
      example.security-tests.depositmatch: 00be76c876686ebff233fc3829f9df5f6458132e61f4f3d4a9243c7b3f017be8
    reviewed_at: "2026-05-15T04:11:24Z"
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
``````

</details>

## Reference

<table class="helix-reference-table">
<tbody>
<tr><th>Activity</th><td><a href="../../../reference/glossary/activities/"><strong>Iterate</strong></a> — Measure, align, and improve. Close the feedback loop back into the planning strand.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/06-iterate/security-metrics.md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Informs</th><td><a href="../../../artifact-types/iterate/improvement-backlog/">Improvement Backlog</a></td></tr>
<tr><th>HELIX documents</th><td><a href="https://github.com/DocumentDrivenDX/helix/blob/main/docs/helix/06-iterate/security-metrics.md"><code>docs/helix/06-iterate/security-metrics.md</code></a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Security Metrics Prompt&#10;&#10;Create a security metrics report for one iteration.&#10;&#10;For how this artifact relates to metric definitions, the metrics dashboard,&#10;and the improvement backlog, see the &quot;Metric Four-Way Slice&quot; section of&#10;`workflows/activities/06-iterate/README.md`.&#10;&#10;## Required Inputs&#10;- Security monitoring and incident data for the iteration period&#10;- Vulnerability scan results (SAST, DAST, dependency scans)&#10;- Compliance audit findings, if applicable&#10;- Previous security metrics report for trend comparison&#10;&#10;## Reference Anchors&#10;&#10;Use these local resource summaries as grounding:&#10;&#10;- `docs/resources/nist-cybersecurity-measurement-guidance.md` grounds&#10;  risk-based, trend-oriented security measurement.&#10;- `docs/resources/owasp-asvs.md` grounds application-security control coverage.&#10;- `docs/resources/google-sre-incident-management-guide.md` grounds incident&#10;  response measurement and follow-up.&#10;&#10;## Produced Output&#10;- `docs/helix/06-iterate/security-metrics.md`&#10;&#10;## Focus&#10;&#10;Report on security posture across four areas: incident response, vulnerability&#10;management, application security, and compliance. For each area, state the&#10;current value, the target, and the trend. Do not repeat raw data in prose —&#10;summarize what the numbers mean and what action they justify.&#10;Separate production security metrics from product outcome metrics unless the&#10;security signal directly changes operational risk.&#10;&#10;Trend comparison against the previous period is required. If no prior report&#10;exists, note the baseline and set targets for the next iteration.&#10;&#10;Every recommendation must be specific enough to become a tracker issue. Vague&#10;recommendations (&quot;improve security posture&quot;) are not acceptable.&#10;&#10;## Completion Criteria&#10;- [ ] All four metric areas populated with current data&#10;- [ ] Trend column populated for each metric (or baseline set if first report)&#10;- [ ] At least one recommendation per area that is actionable as a tracker issue&#10;- [ ] Root cause included for any critical or high-severity incidents&#10;- [ ] Report covers the same iteration period as `metrics-dashboard.md`&#10;- [ ] Raw scanner or incident output is summarized, not pasted wholesale&#10;&#10;Use the template at `workflows/activities/06-iterate/artifacts/security-metrics/template.md`.</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---&#10;ddx:&#10;  id: security-metrics&#10;---&#10;&#10;# Security Metrics - [Iteration / Date Range]&#10;&#10;## Incident Response&#10;&#10;| Metric | Current | Target | Trend |&#10;|--------|---------|--------|-------|&#10;| Mean Time to Detect (MTTD) | | | |&#10;| Mean Time to Respond (MTTR) | | | |&#10;| Incidents resolved within SLA | | | |&#10;| False-positive alert rate | | | |&#10;&#10;**Incident Summary**&#10;&#10;- Total incidents this period: [X]&#10;- Critical (required immediate response): [X]&#10;- Fully resolved: [X]&#10;&#10;**Root Causes** (critical and high only)&#10;&#10;| Root Cause | Count | Mitigation Status |&#10;|------------|-------|-------------------|&#10;| | | |&#10;&#10;## Vulnerability Management&#10;&#10;| Metric | Current | Target | Trend |&#10;|--------|---------|--------|-------|&#10;| Open critical vulnerabilities | | | |&#10;| Open high vulnerabilities | | | |&#10;| MTTR for critical vulns | | | |&#10;| Patch compliance rate | | | |&#10;&#10;## Application Security&#10;&#10;| Metric | Current | Target | Trend |&#10;|--------|---------|--------|-------|&#10;| SAST findings (new this period) | | | |&#10;| DAST findings (new this period) | | | |&#10;| Dependency vulnerabilities (direct) | | | |&#10;| Security review coverage | | | |&#10;&#10;## Compliance Status&#10;&#10;| Requirement | Status | Open Gaps | Target Resolution |&#10;|-------------|--------|-----------|-------------------|&#10;| | | | |&#10;&#10;## Security Posture Trend&#10;&#10;- **Overall risk level**: [Low / Medium / High] — Trend: [Improving / Stable / Declining]&#10;- **Summary**: [One sentence on direction and primary driver]&#10;&#10;## Recommendations&#10;&#10;Each recommendation must be specific enough to create a tracker issue.&#10;&#10;| Recommendation | Priority | Rationale | Expected Impact |&#10;|----------------|----------|-----------|-----------------|&#10;| | High / Med / Low | | |</code></pre></details></td></tr>
</tbody>
</table>
