---
ddx:
  id: DEL-001
  type: deliverable
  activity: iterate
  kind: brief
  status: draft
  authoring:
    home: repo
    export: publications/DEL-001-test-publication.pdf
  links:
    - id: DB-001
      kind: informed_by
    - id: component-profile-nodejs-reusable
      graph: synaptiq-atlas
      kind: informed_by
      authority: advisory
---

# Test publication built from a decision brief

Synthetic test data for the HELIX scenario test.

## Brief

- **Audience**: test reader
- **Occasion**: test
- **Decision or action sought**: none
- **Time slot or page budget**: 1 page
- **Kind**: brief
- **Constraints**: none
- **Look**: classic
- **Scope**: DB-001
- **Breadth**: survey
- **Angle**: none
- **Must cover**: the recommendation
- **Must omit**: none
- **Max messages**: 1
- **Takeaway**: stub takeaway

## Story

- **Flow**: proposal
- **Takeaway**: stub takeaway
- **Messages**:
  1. Stub message (evidence: DB-001#recommendation)
- **Horizontal-logic test**: pass.

## Content

### 1. Stub claim title

**Pattern**: claim-evidence
**Body**:
- Stub evidence
**Visual**: kind: none | icon: check. Text only
**Notes**: Stub.
**Sources**: S1

## Sources

| Id | Claim or figure | Governing artifact and section |
|---|---|---|
| S1 | Stub | DB-001#recommendation |

## Assumptions and gaps

- **Assumption**: none.
- **Gap**: none.

## Render

- **Theme**: deliverables/theme.yml
- **Targets**: not produced in this fixture
- **Gate**: not run in this fixture
