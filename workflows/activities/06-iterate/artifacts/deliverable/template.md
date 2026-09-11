---
ddx:
  id: DEL-[nnn]
  type: deliverable
  activity: iterate
  kind: [deck | one-pager | brief]
  status: draft
  authoring:
    home: repo
    export:
      - [path to rendered .pptx / .html / .pdf / .docx]
  links:
    - id: [source artifact id]
      kind: informed_by
---

# [Deck or document title: the takeaway as a claim]

## Brief

- **Audience**: [who decides or acts; role, not name, unless a name matters]
- **Occasion**: [meeting, send-ahead, board pack, workshop]
- **Decision or action sought**: [one sentence]
- **Time slot or page budget**: [minutes or pages]
- **Kind**: [deck | one-pager | brief]
- **Constraints**: [brand, confidentiality, must-include, must-omit]
- **Takeaway**: [the one sentence the audience should leave with]

## Story

- **Flow**: [flow id from deck-flows.yml, chosen by occasion]
- **Takeaway**: [the sentence every title builds to; same words as the Brief]
- **Messages** (three to five claims that make the takeaway true, ranked by the audience's decision; each with the source sections that prove it):
  1. [message as a claim] (evidence: [path#section], [figure or example it supplies])
  2. [message as a claim] (evidence: [path#section], [...])
  3. [...]
- **Beats and titles** (one row per beat in the flow; titles written before any body):

  | # | Beat | Title (claim) | Message | Exhibit |
  |---|---|---|---|---|
  | 1 | [beat name] | [claim title] | [M1] | [one line: what will prove the title] |
  | 2 | [beat name] | [claim title] | [M2] | [...] |
  | [n] | ask | [the ask as a claim] | [takeaway] | [ask band, steps with owners and dates] |

- **Horizontal-logic test**: [pass, or the titles rewritten to make it pass: each title answers the question the previous one raised; the titles alone give the argument and the ask]

## Content

### 1. [Claim title]

**Pattern**: [pattern id from slide-patterns.yml]
**Body**:
- [evidence bullet within the pattern's limits]
- [evidence bullet]
**Visual**: [what it shows, the series or elements, the source it is drawn from]
**Notes**: [speaker notes: the detail the slide omits, in the same voice]
**Sources**: [S1, S2]

### 2. [Claim title]

**Pattern**: [pattern id]
**Body**:
- [...]
**Visual**: [...]
**Notes**: [...]
**Sources**: [S3]

### [n]. [The ask as a claim]

**Pattern**: ask-next-steps
**Body**:
- [next step, owner, date]
- [next step, owner, date]
- [what happens if no decision]
**Visual**: [ask band plus numbered steps with owner and date columns]
**Notes**: [...]
**Sources**: [S1]

## Sources

| Id | Claim or figure | Governing artifact and section |
|---|---|---|
| S1 | [claim or number as it appears in the body] | [path#section] |
| S2 | [...] | [...] |

## Assumptions and gaps

- **Assumption**: [what was inferred, from what, and who should confirm it]
- **Gap**: [content the deliverable needed that no artifact holds; how it was handled]

## Render

- **Theme**: [project design-system | deliverables/theme.yml]
- **Targets**: [pptx path], [html path], [pdf path]
- **Gate**: script checks [pass/fail with check ids], horizontal logic [pass], vertical logic [pass], fidelity [pass], voice [pass], visual [every slide rendered to an image and inspected on <date>], file [validator result]
