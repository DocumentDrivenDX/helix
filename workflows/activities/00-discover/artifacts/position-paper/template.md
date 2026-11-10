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
---

# PP-[number]: [The position as a claim]

## Thesis

**Thesis**: [The position in one or two sentences, as a claim a reader can
disagree with.]

## Audience and Stakes

Who the paper is for and what they decide or do differently if persuaded.
Name the audience by role, and say what is at stake for them.

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

What the paper does not claim, and the conditions under which the thesis
would not hold.

## Evidence

| Reference | Kind | Revision | Used for |
|-----------|------|----------|----------|
| [Assessment, brief, or source] | [kind] | [revision or digest] | [claim] |
