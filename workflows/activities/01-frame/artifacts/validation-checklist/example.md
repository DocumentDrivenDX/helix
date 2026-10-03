---
ddx:
  id: example.validation-checklist.depositmatch
  authoring:
    home: repo
  depends_on:
    - example.prd.depositmatch
    - example.pr-faq.depositmatch
    - example.feature-registry.depositmatch
    - example.research-plan.depositmatch
    - example.risk-register.depositmatch
    - example.security-requirements.depositmatch
    - example.threat-model.depositmatch
    - example.stakeholder-map.depositmatch
---

# Frame Activity Validation Checklist

**Status**: [ ] Not Started | [ ] In Progress | [x] Complete
**Validated By**: Product Lead
**Date**: 2026-05-12
**Result**: [ ] Pass | [x] Conditional Pass | [ ] Fail

## Go / No-Go Gates

| Gate | Status | Evidence | Blocking Gap |
|------|--------|----------|--------------|
| Problem, goals, and success metrics are clear enough to judge outcomes | Pass | Product Vision, Opportunity Canvas, PR-FAQ | None |
| P0 scope is identified, prioritized, and separated from non-goals | Pass | PRD, Feature Registry, Parking Lot | None |
| Features and stories are traceable through IDs and links | Conditional | Feature Registry links FEAT-001; later features are pending | Complete trace links for FEAT-002 through FEAT-004 before design approval |
| Acceptance criteria are testable | Conditional | PRD and Security Requirements | Add story-level acceptance criteria for FEAT-002 and FEAT-003 before build |
| Major risks, dependencies, and external constraints are explicit | Pass | Risk Register, Compliance Requirements, Feasibility Study | None |
| Frame artifacts do not contradict each other | Pass | Parking Lot aligns with PRD non-goals and PR-FAQ v1 scope | None |
| Required stakeholders have reviewed the plan | Conditional | Stakeholder Map identifies required reviewers | Compliance/Legal signoff required before live-data design approval |

## Result

- [ ] **PASS**: Ready for Design activity
- [x] **CONDITIONAL PASS**: Proceed with noted conditions
- [ ] **FAIL**: Address blocking issues first

**Conditions/Notes**:
DepositMatch is ready to begin Design for the CSV-first pilot because the
customer problem, P0 scope, risks, security requirements, and deferred work are
clear. Design must not approve live-data onboarding until compliance/legal
review is complete, and build must not start for FEAT-002/FEAT-003 until their
story-level acceptance criteria are complete.

## Required Follow-Up

| Item | Owner | Due | Required Before |
|------|-------|-----|-----------------|
| Complete compliance/legal applicability review for live financial data | Compliance Officer / Legal Counsel | Before live-data design approval | Design approval |
| Complete trace links for FEAT-002, FEAT-003, and FEAT-004 | Product Lead | Before design approval | Design approval |
| Add story-level acceptance criteria for match review and exception queue | Product Lead | Before build planning | Build start |
| Confirm research plan recruiting and sample CSV intake path | Product Lead | Before design assumptions freeze | Design approval |
