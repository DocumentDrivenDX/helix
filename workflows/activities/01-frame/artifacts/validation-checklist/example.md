---
ddx:
  id: example.validation-checklist.depositmatch
  depends_on:
    - example.prd.depositmatch
    - example.pr-faq.depositmatch
    - example.feature-registry.depositmatch
    - example.research-plan.depositmatch
    - example.risk-register.depositmatch
    - example.security-requirements.depositmatch
    - example.threat-model.depositmatch
    - example.stakeholder-map.depositmatch
  review:
    self_hash: f44b1be941f157ee20ca0791996de7a86d851392579ee74ed772b9f9a07dd0f0
    deps:
      example.feature-registry.depositmatch: 227c7c30edf5318187982fad9b7c868365600d4ffb8f92da25b1f932769dddb8
      example.pr-faq.depositmatch: 102ec8dcd77efb43d6a73143dc4dbfeb1fc95b0ab516a593166bb8b12dd70686
      example.prd.depositmatch: c9c24e1694af4548a6deaad8d92059e365da110148bd9adc44d8640dff9770a4
      example.research-plan.depositmatch: e1bd75c90a2407b8d84770a3d822fa64fc9b90fe1d36cfef5f5d615bf6ba6e06
      example.risk-register.depositmatch: 4cfb9a77765bfa4a63e8ad9d98a656bb5c9b9bfb5c5569389cb8cf73e8c1c3ba
      example.security-requirements.depositmatch: 2a1f7efe6e55c1edaa67b76e5a11a49be55e4420d9adc456be5482d417312a43
      example.stakeholder-map.depositmatch: 7a1136a9797454fae7cd398a1eeded819f907aae48866461d6640c2bdcae892c
      example.threat-model.depositmatch: 28c760cff8d40eab543a794535603b0a70e333e9cd808c45c23b885e621e7602
    reviewed_at: "2026-05-15T04:11:24Z"
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
