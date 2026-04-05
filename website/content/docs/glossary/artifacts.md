---
title: Artifacts
weight: 2
prev: /docs/glossary/phases
next: /docs/glossary/actions
---

# HELIX Artifacts

Every HELIX artifact type, organized by the phase that produces it. Each artifact has a template and prompt in `workflows/phases/`.

## Authority Order

When artifacts disagree, resolve the conflict using this precedence (highest first):

1. Product Vision
2. Product Requirements (PRD)
3. Feature Specs / User Stories
4. Architecture / ADRs
5. Solution Designs / Technical Designs
6. Test Plans / Tests
7. Implementation Plans
8. Source Code / Build Artifacts

Higher-order artifacts govern lower-order artifacts. Source code is evidence of implementation, not the source of truth for requirements.

---

## Discover (Phase 0)

| Artifact | Location | Purpose |
|----------|----------|---------|
| **Product Vision** | `docs/helix/00-discover/product-vision.md` | Mission, positioning, target market, success metrics, and why now |
| **Business Case** | `docs/helix/00-discover/` | Financial and strategic justification for the project |
| **Competitive Analysis** | `docs/helix/00-discover/` | Landscape of alternatives and differentiation |
| **Opportunity Canvas** | `docs/helix/00-discover/` | Structured opportunity assessment |

## Frame (Phase 1)

| Artifact | Location | Purpose |
|----------|----------|---------|
| **PRD** | `docs/helix/01-frame/prd.md` | Problem, goals, requirements (P0/P1/P2), personas, constraints, acceptance sketches |
| **Feature Spec** | `docs/helix/01-frame/features/FEAT-NNN-*.md` | One capability: requirements, stories, edge cases, success metrics |
| **User Story** | `docs/helix/01-frame/user-stories/US-NNN-*.md` | One vertical slice: Given/When/Then acceptance criteria, test scenarios |
| **Principles** | `docs/helix/01-frame/principles.md` | Design and engineering values that guide judgment calls |
| **Concerns** | `docs/helix/01-frame/concerns.md` | Active cross-cutting technology and quality declarations |
| **Risk Register** | `docs/helix/01-frame/` | Identified risks with likelihood, impact, and mitigation |
| **Threat Model** | `docs/helix/01-frame/` | STRIDE-based threat analysis |
| **Security Requirements** | `docs/helix/01-frame/` | Security and compliance requirements |
| **Feasibility Study** | `docs/helix/01-frame/` | Technical feasibility assessment |
| **Stakeholder Map** | `docs/helix/01-frame/` | Stakeholders, their interests, and influence |
| **PR/FAQ** | `docs/helix/01-frame/` | Working-backwards press release and FAQ |
| **Research Plan** | `docs/helix/01-frame/` | Structured research approach for unknowns |
| **Parking Lot** | `docs/helix/01-frame/` | Ideas explicitly deferred for future consideration |
| **Validation Checklist** | `docs/helix/01-frame/` | Phase exit criteria |
| **Feature Registry** | `docs/helix/01-frame/` | Index of all feature specs |

## Design (Phase 2)

| Artifact | Location | Purpose |
|----------|----------|---------|
| **Architecture** | `docs/helix/02-design/architecture.md` | System-level architecture and component relationships |
| **ADR** | `docs/helix/02-design/adr/ADR-NNN-*.md` | Architecture Decision Record: question, alternatives, decision, rationale |
| **Solution Design** | `docs/helix/02-design/solution-designs/SD-NNN-*.md` | Feature-level design: chosen approach for a capability |
| **Technical Design** | `docs/helix/02-design/technical-designs/TD-NNN-*.md` | Story-level slice: one bounded implementation unit |
| **Proof of Concept** | `docs/helix/02-design/` | Spike to validate a technical approach |
| **Tech Spike** | `docs/helix/02-design/` | Focused investigation of a technical question |
| **Auth Design** | `docs/helix/02-design/` | Authentication and authorization architecture |
| **Data Design** | `docs/helix/02-design/` | Data model, storage, and migration strategy |
| **UX Design** | `docs/helix/02-design/` | User experience flows and interaction design |
| **Security Architecture** | `docs/helix/02-design/` | Defense-in-depth design with security controls |
| **Data Protection** | `docs/helix/02-design/` | Data classification, encryption, and privacy design |
| **Contracts** | `docs/helix/02-design/` | API and interface contracts |

## Test (Phase 3)

| Artifact | Location | Purpose |
|----------|----------|---------|
| **Test Plan** | `docs/helix/03-test/test-plans/TP-*.md` | Feature-level test strategy: what to test, how, at what level |
| **Story Test Plan** | `docs/helix/03-test/` | Story-level test approach inheriting from the feature test plan |
| **Test Procedures** | `docs/helix/03-test/` | Step-by-step manual or automated test execution guides |
| **Test Suites** | `tests/` | Executable test code organized by level (unit, integration, e2e) |
| **Security Tests** | `docs/helix/03-test/` | Security-specific test procedures and automation |

## Build (Phase 4)

| Artifact | Location | Purpose |
|----------|----------|---------|
| **Implementation Plan** | `docs/helix/04-build/implementation-plan.md` | Work breakdown, dependency ordering, parallel tracks |
| **Story Implementation Plan** | `docs/helix/04-build/` | Story-level implementation approach |
| **Build Procedures** | `docs/helix/04-build/` | Build, CI, and packaging procedures |
| **Secure Coding** | `docs/helix/04-build/` | Secure coding guidelines and patterns |

## Deploy (Phase 5)

| Artifact | Location | Purpose |
|----------|----------|---------|
| **Deployment Checklist** | `docs/helix/05-deploy/` | Pre-deployment verification steps |
| **Launch Checklist** | `docs/helix/05-deploy/` | Go-live readiness criteria |
| **Runbook** | `docs/helix/05-deploy/` | Operational procedures for the running system |
| **Release Notes** | `docs/helix/05-deploy/` | User-facing changelog for each release |
| **Monitoring Setup** | `docs/helix/05-deploy/` | Dashboards, alerts, and observability configuration |
| **Security Monitoring** | `docs/helix/05-deploy/` | Security-specific monitoring and incident response |
| **GTM Plan** | `docs/helix/05-deploy/` | Go-to-market strategy and execution |
| **Story Deployment Plan** | `docs/helix/05-deploy/` | Story-level rollout approach |

## Iterate (Phase 6)

| Artifact | Location | Purpose |
|----------|----------|---------|
| **Alignment Review** | `docs/helix/06-iterate/alignment-reviews/AR-*.md` | Top-down reconciliation of plan vs. implementation |
| **Backfill Report** | `docs/helix/06-iterate/backfill-reports/BF-*.md` | Documentation reconstruction from evidence |
| **Feedback Analysis** | `docs/helix/06-iterate/` | Structured analysis of user or stakeholder feedback |
| **Improvement Backlog** | `docs/helix/06-iterate/` | Prioritized list of improvements from iteration |
| **Lessons Learned** | `docs/helix/06-iterate/` | Post-iteration retrospective findings |
| **Metrics Dashboard** | `docs/helix/06-iterate/` | Metric definitions and dashboard configuration |
| **Metric Definition** | `docs/helix/06-iterate/metrics/*.yaml` | Individual metric: name, unit, direction, command, tolerance |
| **Iteration Planning** | `docs/helix/06-iterate/` | Plan for the next development cycle |
