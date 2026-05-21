---
ddx:
  id: example.stakeholder-map.depositmatch
  depends_on:
    - example.opportunity-canvas.depositmatch
    - example.compliance-requirements.depositmatch
    - example.risk-register.depositmatch
  review:
    self_hash: 7a1136a9797454fae7cd398a1eeded819f907aae48866461d6640c2bdcae892c
    deps:
      example.compliance-requirements.depositmatch: ec7fb87a927f7e53a9c323e9af8ee73d667e4520ab596c130077d332d2783c9f
      example.opportunity-canvas.depositmatch: 75303097bfeeed0272bd68f90ef887f9a5e646a1272f9a57ccd0d899ae17497a
      example.risk-register.depositmatch: 4cfb9a77765bfa4a63e8ad9d98a656bb5c9b9bfb5c5569389cb8cf73e8c1c3ba
    reviewed_at: "2026-05-15T04:11:24Z"
---

# Stakeholder Map

**Status**: Review
**Last Updated**: 2026-05-12

## Primary Stakeholders (High Influence, High Interest)

### Product Lead

- **Role**: Owns pilot scope, customer validation, and PRD readiness.
- **Interest**: Proving the core reconciliation workflow without expanding v1.
- **Influence**: High
- **Concerns**: Scope creep into bank feeds, ledger writeback, or broad
  accounting replacement.
- **Success Criteria**: PRD scope maps to pilot evidence and measurable success
  metrics.
- **Communication**: Weekly pilot readiness review.
- **Contact Channel**: Product review meeting / product planning issue.

### Engineering Lead

- **Role**: Owns technical feasibility, security requirements, and delivery
  design.
- **Interest**: Keeping CSV import, matching, and audit logs buildable in the
  three-month pilot.
- **Influence**: High
- **Concerns**: CSV variability, cross-firm data isolation, and support access
  controls.
- **Success Criteria**: P0 features can be designed and tested without hidden
  integration dependencies.
- **Communication**: Weekly design/risk review.
- **Contact Channel**: Engineering planning issue / architecture review.

### Compliance Officer / Legal Counsel

- **Role**: Owns regulatory applicability review and data-handling constraints.
- **Interest**: Confirming whether FTC Safeguards, state privacy, or contractual
  duties affect live-data pilot scope.
- **Influence**: High
- **Concerns**: Live financial data uploaded before controls and agreements are
  approved.
- **Success Criteria**: Compliance Requirements gaps closed before pilot
  onboarding.
- **Communication**: Counsel-review checkpoint before live-data pilot.
- **Contact Channel**: Compliance review issue / counsel checkpoint.

### Pilot Firm Reconciliation Lead

- **Role**: Primary user and evidence source for workflow validation.
- **Interest**: Reducing weekly reconciliation time without losing reviewer
  control.
- **Influence**: High for product fit; low for internal budget.
- **Concerns**: Match evidence, exception ownership, CSV setup burden, and
  auditability.
- **Success Criteria**: Weekly reconciliation below 3 minutes per client with
  trusted suggestions.
- **Communication**: Research interview, pilot onboarding, weekly feedback.
- **Contact Channel**: Pilot feedback session / customer interview notes.

## Secondary Stakeholders (Variable Influence/Interest)

### Operations Lead

- **Role**: Owns pilot support process and onboarding load.
- **Interest**: Keeping CSV mapping and support access manageable.
- **Influence**: Medium
- **Engagement Level**: Consult
- **Contact Channel**: Pilot operations review.

### Sponsor / Finance Lead

- **Role**: Owns investment continuation and pilot budget.
- **Interest**: Business Case confidence, willingness to pay, and cost to
  support.
- **Influence**: High
- **Engagement Level**: Inform / Consult at gates
- **Contact Channel**: Monthly sponsor review.

### Security Champion

- **Role**: Reviews security requirements, threat model, and security tests.
- **Interest**: Preventing cross-firm exposure and sensitive-data leakage.
- **Influence**: Medium
- **Engagement Level**: Collaborate on security artifacts
- **Contact Channel**: Security review issue.

## RACI Matrix

| Activity/Decision | Product Lead | Engineering Lead | Compliance/Legal | Pilot Firm Lead | Sponsor |
|-------------------|--------------|------------------|------------------|-----------------|---------|
| PRD scope approval | A | R | C | C | I |
| CSV import feasibility | C | A/R | I | C | I |
| Live-data pilot approval | C | R | A | I | I |
| Pilot success metrics | A/R | C | C | C | I |
| Budget continuation | R | C | C | I | A |
| Release readiness | A | R | C | I | I |

**R** = Responsible | **A** = Accountable | **C** = Consulted | **I** = Informed

## Power/Interest Grid

```
High Power  | Keep Satisfied      | Manage Closely
            | - Sponsor           | - Product Lead
            |                     | - Engineering Lead
            |                     | - Compliance/Legal
            |---------------------|-------------------
Low Power   | Monitor             | Keep Informed
            | - Support Ops       | - Pilot Firm Leads
            |                     | - Security Champion
            Low Interest          High Interest
```

## Communication Plan

| Stakeholder Group | Channel | Frequency | Content | Owner |
|-------------------|---------|-----------|---------|-------|
| Product + Engineering | Pilot readiness review | Weekly | Scope, risks, import findings, security work | Product Lead |
| Compliance/Legal | Counsel checkpoint | Before live-data pilot, then as needed | Applicability gaps, data handling, vendor review | Compliance Officer |
| Pilot Firm Leads | Interview / pilot feedback session | During research and weekly pilot | Workflow pain, CSV samples, time saved, trust concerns | Product Lead |
| Sponsor / Finance | Sponsor review | Monthly or gate-based | Business Case confidence, pricing signal, pilot cost | Product Lead |

### Escalation Path

1. Artifact owner resolves routine disagreements.
2. Product Lead decides scope tradeoffs within approved pilot boundaries.
3. Compliance/Legal has stop authority for live-data use.
4. Sponsor decides funding continuation or project stop when risk exceeds pilot
   appetite.
