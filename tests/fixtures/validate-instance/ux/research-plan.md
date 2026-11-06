---
ddx:
  id: research-plan-pilot-reviewer-interviews
  type: research-plan
  authoring:
    home: repo
---

# Research Plan: Pilot reviewer interviews

**Research Lead**: Product lead
**Time Budget**: Two weeks

## Research Objectives

1. **Question**: Can reconciliation leads import a client's weekly files without help?
   - **Why Important**: Import is the first step of every reconciliation.
   - **Success Criteria**: Five of six participants finish unaided.

## Research Methods

### Moderated usability sessions
- **Objective**: Question 1
- **Approach**: Six remote sessions on the staging build
- **Decision Use**: Decides whether mapping review ships as designed

### Scenarios

| Scenario | Goal |
|----------|------|
| weekly import | Get this week's Acme Dental exports ready to match |

### Success Criteria

| Scenario | Succeeds When | Acceptance Criteria |
|----------|---------------|---------------------|
| weekly import | The import is confirmed with the right columns | US-001-AC1, US-002-AC1 |

### Screener

- **Include**: Reconciliation leads at pilot firms
- **Exclude**: People who took part in the design reviews
- **Mix**: Four from small firms, two from mid-size firms

## Timeline

| Activity | Duration | Activities | Deliverables |
|-------|----------|------------|--------------|
| Sessions | 1 week | Run six sessions | Session notes, kept outside the repo |

## Research Risks
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Too few participants | Low | Medium | Recruit eight for six |

## Findings

### Claims

| Claim | Source | Basis | Confidence | Direction | Verified | Contradicting | Unknown |
|-------|--------|-------|------------|-----------|----------|---------------|---------|
| A renamed column is the most common reason an import goes wrong | P1–P6, sessions 1–6 | Observed in 4 of 6 sessions | medium | supports: flag renamed columns before confirm | yes | none | Whether it holds for mid-size firms |

## Completion Criteria
- [x] All research questions answered with evidence
