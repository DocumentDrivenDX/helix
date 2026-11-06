# Technology Assessment Generation Prompt

Compare technologies on stated criteria from reusable technology briefs, and
state findings a later decision can rely on.

## Storage Location

Store at: `docs/helix/00-discover/technology-assessment-TA-{number}-{subject}.md`,
or the path the flow's graph profile sets for this type (`locations:`).

## Purpose

Answers: **How do these technologies compare on these criteria, on the
evidence we hold?** It is reusable: no project, client, or deployment context
appears in it.

## Role Boundary

A [[component-profile]] with `scope: reusable` records one technology; the
assessment compares several and cites each brief by pinned revision rather
than restating it. A [[decision-brief]] recommends for one context; the
assessment never does. A [[position-paper]] argues a stance; the assessment
reports. If a reader needs "so which one", the assessment ends and a
Decision Brief begins.

## Method

1. **State the scope** and the technologies, including the version lines.
2. **Define the criteria** before grading, from concerns where one applies.
3. **Read each brief.** Grade every technology on every criterion from a
   brief section; where no brief speaks, write Unknown.
4. **Compare** in one table, cells citing sources.
5. **Write findings** only where criteria separate the technologies.
6. **Record disagreement.** When two sources conflict, cite both, link with
   `contradicts`, and leave the conflict open until new evidence settles it.
7. **Pin the briefs** before publishing.

## Writing for the reviewer

Findings are claims with citations after them. Do not rank, score, or
recommend. A tie or an unknown is a finding.

## Inputs

- Reusable technology briefs for each technology
- Concerns that define criteria
