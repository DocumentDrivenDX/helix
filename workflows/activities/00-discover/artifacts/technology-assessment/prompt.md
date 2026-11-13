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
reports, and gives no criterion a weight: how much each counts is the
paper's judgement. If a reader needs "so which one", the assessment ends and a
Decision Brief begins.

## Method

1. **State the scope** and the technologies, including the version lines.
2. **Define the criteria** before grading, from concerns where one applies.
3. **Read each brief.** Grade every technology on every criterion from a
   brief section; where no brief speaks, write Unknown.
4. **Compare** in one table, cells citing sources. To keep the ratings as
   data, put them in an `assessment:` front matter block (criteria ids from
   `criteria.yml` at the flow root, a one-line finding or a stated gap for every criterion
   and subject) and run `assessment-tables.py --write`; the Criteria and
   Comparison tables are generated from it.
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

## An assessment of a practice

Set `ddx.scope: practice` when the subject is a practice that no technology
assessment covers. Rate nothing: there are no criteria, subjects, or ratings,
and no Criteria, Technologies, Comparison, or Evidence section. Write Scope,
then Findings grouped by reader, then Contradictions and Gaps, then numbered
Sources cited at the clause. Say how each claimed benefit is supported: by
argument, by reported use, or by a named study. Where a technology assessment
already covers the subject, put the explanation of the practice at the front
of that assessment and write no second document.
