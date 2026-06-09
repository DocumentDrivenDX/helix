---
title: "Security Metrics — HELIX 2026-Q2 (post-`v0.3.3`)"
slug: security-metrics
weight: 1050
activity: "Iterate"
source: "06-iterate/security-metrics.md"
generated: true
---
# Security Metrics — HELIX 2026-Q2 (post-`v0.3.3`)

> Illustrative example using representative measurements taken from the
> live HELIX repo around the `v0.3.3` release window. Exact counts reflect
> a single sampling period and will drift; the posture report's
> structure and decision logic are the canonical part. HELIX is a
> developer-local methodology framework, not a hosted service, so several
> traditional security-metric categories report N/A by design.

**Review Window**: 2026-04-01 → 2026-04-30
**Authority**: [`security-architecture.md`](/artifacts/security-architecture/),
[`security-owasp` concern](https://github.com/DocumentDrivenDX/helix/blob/main/workflows/concerns/security-owasp),
[`CONTRACT-001`](/artifacts/contracts/contract-001-ddx-helix-boundary/).

## Incident Response

| Metric | Current | Target | Trend |
|--------|---------|--------|-------|
| Mean Time to Detect (MTTD) | N/A — operator-driven detection | N/A | Stable |
| Mean Time to Respond (MTTR) | < 1 cycle (operator stops the run) | < 1 cycle | Stable |
| Incidents resolved within SLA | 0 / 0 incidents this period | 100% when applicable | N/A |
| False-positive alert rate | N/A — no automated paging | N/A | Stable |

**Incident Summary**

- Total incidents this period: 0
- Critical (required immediate response): 0
- Fully resolved: 0

**Root Causes** (critical and high only)

| Root Cause | Count | Mitigation Status |
|------------|-------|-------------------|
| (none this period) | 0 | N/A |

## Vulnerability Management

| Metric | Current | Target | Trend |
|--------|---------|--------|-------|
| Open critical vulnerabilities (direct deps) | 0 | 0 | Stable |
| Open high vulnerabilities (direct deps) | 0 | 0 | Stable |
| MTTR for critical vulns | N/A — none open | < 7 days when applicable | Stable |
| Patch compliance rate (HELIX direct deps) | 100% (all pinned via `go.mod` / `package.json`) | 100% | Stable |

HELIX direct dependency surface is small: Hugo (pinned in
`.github/workflows/pages.yml`), Hextra (`website/go.mod`), Playwright
(`website/package.json`), DDx (operator-installed, version-pinned). The
project does not run a continuous SCA scan; vulnerability tracking is
manual and bound to dependency-update beads.

## Application Security

| Metric | Value | Trend |
|--------|-------|-------|
| SAST findings (new this period) | 0 | Stable |
| DAST findings (new this period) | N/A — no hosted service | N/A |
| Dependency vulnerabilities (direct) | 0 | Stable |
| Security review coverage | All commits gated by `lefthook` pre-commit (`check-workflow-paths`, secret-pattern scan) | Stable |
| Secret-pattern matches in commits | 0 | Stable |
| Bare `workflows/` references in docs (forbidden by hook) | 0 (enforced by `check-workflow-paths`) | Stable |

## Compliance Status

| Requirement | Status | Open Gaps | Target Resolution |
|-------------|--------|-----------|-------------------|
| Boundary contract (CONTRACT-001) honored | Compliant | None — every doc audited 2026-05-01 references the post-DDx-migration substrate after the AR-2026-05-01 follow-ups | Sustained via the `/helix review` discipline |
| `security-owasp` concern coverage | Compliant on the developer-local surface; not applicable to hosted-service controls (no hosted service) | None | N/A |
| No secrets in repo | Compliant | None this period | Sustained via pre-commit secret scan |

## Security Posture Trend

- **Overall risk level**: Low — Trend: Stable
- **Summary**: HELIX is a developer-local framework; the active security
  surface is the operator's own model-provider key handling and the
  pre-commit guards that prevent secrets from being committed. Both held
  steady across the 2026-Q2 window. The largest residual risk is operator-
  introduced secrets in bead bodies, which is a contract-level concern,
  not a service-level one.

## Recommendations

| Recommendation | Priority | Rationale | Expected Impact |
|----------------|----------|-----------|-----------------|
| Add a continuous secret-pattern scan in CI (in addition to pre-commit) | Med | Pre-commit can be skipped (`--no-verify`); CI is the durable backstop | Catches any operator-bypassed secret leaks before they reach the public site |
| Wire a lightweight SCA scan (e.g. `govulncheck` for Go, `npm audit` for the website) into CI for the HELIX direct dep surface | Med | Vulnerability discovery is currently manual; small surface but worth automating | Earlier signal on Hextra / Hugo / Playwright vulns before they age |
| Document the `OPENROUTER_API_KEY` rotation cadence in the runbook | Low | Currently the runbook only describes how to react to auth failures, not preventive rotation | Reduces credential-age risk for long-lived operator setups |
| Add a deterministic test that asserts `ddx-server` binds to `127.0.0.1:7743` and refuses non-loopback bind without an explicit flag | Med | Security-architecture says this; nothing today tests it | Regression-protects the loopback-default posture |
