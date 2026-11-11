---
ddx:
  id: PP-[number]
  type: position-paper
  authoring:
    home: repo
  links:
    # - {id: <technology assessment id>, kind: supported_by, rev: <pinned revision>}
    # - {id: <technology brief id>, kind: supported_by, rev: <pinned revision>}
    # - {id: <other paper or assessment id>, kind: contradicts}
# Optional: stances as data. The Recommendations table below is then generated from it
# (`assessment-tables.py --write`).
# recommendations:
#   - subject: <technology brief id>
#     context: <the context the stance is for>
#     stance: recommended | conditional | watch | avoid
#     conditions: <required for conditional>
#     rationale: <why, in a sentence or two>
#     based_on: [{assessment: <assessment id>, criteria: [<criterion id>]}]
#     since: <date>
#     review_by: <date after since>
#     approved_by: <name>   # with approved_on, or neither: until then the stance is proposed
#     approved_on: <date>
# Optional: how much each criterion counts, as data. The Decision Criteria table below is then
# generated from it. A weight is the paper's judgement; an assessment and criteria.yml carry none.
# weights:
#   - criterion: <criterion id that a supported_by assessment has a finding for>
#     weight: decisive | important | minor
#     reason: <why it counts this much, in one line>
---

# PP-[number]: [The position as a claim]

## Thesis

**Thesis**: [The position in one or two sentences, as a claim a reader can
disagree with.]

## Audience and Stakes

Who the paper is for and what they decide or do differently if persuaded.
Name the audience by role, and say what is at stake for them.

## Decision Criteria

Only when the paper weighs the criteria its assessments rate. The table is
generated from `weights:`. A weight is decisive, important, or minor, never
a number, and it is the author's judgement: the reason says why.

| Criterion | Weight | Why |
|-----------|--------|-----|
| [Criterion] | [Decisive, Important, or Minor] | [Reason] |

## Argument

The case in order, each step a claim with its support. Label a claim of
judgment as the author's judgment; cite evidence for a claim of fact.

1. [Claim]. [Evidence, pinned revision, or "Author's judgment"]
2. [Claim]. [Evidence or "Author's judgment"]

## Objections and Answers

The strongest objections, including any the cited evidence raises.

| Objection | Answer | Evidence |
|-----------|--------|----------|
| [Objection] | [Answer] | [Source or "Author's judgment"] |

## Recommendations

Only when the paper advises a stance per technology and context. The table
is generated from `recommendations:`; the argument above is the case for it.

| Technology | Stance | Context | Conditions | Based on |
|------------|--------|---------|------------|----------|
| [Technology] | [Stance (Proposed or Approved)] | [Context] | [Conditions] | [Assessment id] |

## Limits of the Position

What the paper does not claim, in a sentence or two. Then when the other
option wins: one row per condition under which the thesis does not hold,
the option that wins under it, and the evidence (a pinned assessment's
rating, or "Author's judgment").

| Condition | Option that wins | Evidence |
|-----------|------------------|----------|
| [Condition] | [Option] | [Assessment id and criterion, or "Author's judgment"] |

## Transition Path

Optional: only when the position displaces something already in use. What
a team with the existing option does first, what can stay as it is, and
what would stop the move. Leave the section out when there is no incumbent.

## Evidence

| Reference | Kind | Revision | Used for |
|-----------|------|----------|----------|
| [Assessment, brief, or source] | [kind] | [revision or digest] | [claim] |
