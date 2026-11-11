---
ddx:
  id: SPIKE-XXX
  # scope: reusable   # a spike anyone can rerun from public inputs; see Scope kinds
  authoring:
    home: repo
  # links:
  #   - {id: <profile id>, kind: answers, question: <open question number>, rev: <pinned revision>}
---

# Technical Spike: {{spike_title}}

**Spike ID**: {{spike_id}} | **Lead**: {{spike_lead}} | **Time Budget**: {{time_budget}} | **Status**: [In Progress | Completed]

**Scope kinds** (`ddx.scope`). The default is a project's spike: this
template without Views Affected, with Test Setup and Reproduction optional.
`reusable` is a spike published as knowledge, for example in a technology
atlas: it runs on public inputs anyone can obtain, names no project or
client, and recommends nothing. It requires Test Setup, Views Affected, and
Reproduction, and omits Recommendations and Artifacts. A profile cites it as
a source of class `measured`.

## Objective

**Technical Question**: {{technical_uncertainty}}

**Goals**:
- [ ] [Specific goal 1]
- [ ] [Specific goal 2]

**Success Criteria**: Evidence gathered, recommendations with rationale, risks identified.

**Out of Scope**: Production implementation, comprehensive testing, optimization work.

## Hypothesis

**Primary**: [What we think we'll discover]
**Assumptions**: [Key assumptions]
**Expected Outcome**: [Anticipated result]

## Test Setup

What was measured and on what: the component and exact version, the
hardware or instance type, the configuration that differs from the default,
the data set and its size, and the date. A reader needs all of it to know
which configuration the result speaks for.

| Item | Value |
|------|-------|
| Component and version | [Name, version] |
| Environment | [Hardware or instance type, operating system] |
| Configuration | [Settings changed from the default, or *Defaults*] |
| Data | [Data set, size, and where it comes from] |
| Run on | [Date] |

## Approach

**Method**: [Prototype | Benchmark | Literature Review | Comparative Analysis | Integration Testing]

**Activities**:
| Day | Activity | Objective |
|-----|----------|-----------|
| 1 | [Activity] | [Goal] |
| 2 | [Activity] | [Goal] |

## Findings

**FINDING 1**: [Discovery]
- **Evidence**: [Concrete proof/data]
- **Implications**: [What this means]

### Measurements
| Metric | Approach A | Approach B | Notes |
|--------|------------|------------|--------|
| [Metric] | [Value] | [Value] | [Context] |

## Analysis

**Hypothesis**: CONFIRMED | PARTIALLY CONFIRMED | REJECTED
**Rationale**: [Evidence]

### Risks
| Risk | Prob | Impact | Mitigation |
|------|------|--------|------------|
| [Risk] | H/M/L | H/M/L | [Strategy] |

## Conclusions

**Primary Conclusion**: [Clear answer to the technical question]
**Confidence**: High | Medium | Low
**Limitations**: [What could not be determined]

## Views Affected

Reusable scope only. Which reader's answer the result changes in the
profile whose question this spike answers. One row per view; a view the
result does not touch says **No change**.

| View | What changes |
|------|--------------|
| Risk & Compliance | [What the result changes, or *No change*] |
| Finance | [What the result changes, or *No change*] |
| IT Operations | [What the result changes, or *No change*] |
| Apps Dev | [What the result changes, or *No change*] |

## Recommendations

Not at reusable scope: a published spike reports what it measured, and a
position paper or decision brief draws the advice.

**RECOMMENDATION**: [Specific, actionable recommendation]
- **Rationale**: [Why, based on evidence]
- **Next Steps**: [What needs to happen]
- **Concern Impact**: [Does this recommend adopting, rejecting, or modifying a
  concern? If so, an ADR should ratify the decision and the project concern
  document should be updated accordingly.]

## Reproduction

How to run it again: where the scripts are in the repository, the inputs
and how to obtain them, the commands in order, and how long a run takes.
At reusable scope every input is public.

1. [Command or step]

## Artifacts

- [Fixture, branch, benchmark, prototype, notes, or other evidence produced by
  the spike]
