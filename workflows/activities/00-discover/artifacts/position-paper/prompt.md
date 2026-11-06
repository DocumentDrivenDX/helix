# Position Paper Generation Prompt

Argue one position for a named audience on cited evidence, with the strongest
objections answered and the limits stated.

## Storage Location

Store at: `docs/helix/00-discover/position-paper-PP-{number}-{subject}.md`,
or the path the flow's graph profile sets for this type (`locations:`).

## Purpose

Answers: **What do we think about this, why should the audience agree, and
what would make us wrong?** It takes a side. It is not tied to one client.

## Role Boundary

A [[technology-assessment]] reports findings and takes no side; the paper
argues from them and cites them by pinned revision. A [[decision-brief]]
recommends for one named context; the paper does not. A paper may inform a
brief; it never overrides a client's requirements or decisions. A
[[deliverable]] presents a paper to an audience; the paper is the source.

## Method

1. **State the thesis** as a claim a reader can reject.
2. **Name the audience and the stakes.**
3. **Build the argument** as ordered claims. Cite evidence for facts; label
   judgments as the author's.
4. **Find the strongest objections,** including any raised by the cited
   evidence, and answer each. An objection the evidence supports and the
   paper cannot answer belongs in Limits.
5. **State the limits:** what the paper does not claim and when it fails.
6. **Pin the evidence** before approval.

## Writing for the reader

Plain words, the thesis first. Do not present opinion as evidence, and do not
drop a fact because it hurts the case. A figure appears only with its source.

## Inputs

- Technology assessments and briefs the argument rests on
- The audience and what they decide
