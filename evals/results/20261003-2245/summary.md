# HELIX eval run 20261003-2245

Runner: `claude -p {prompt} --plugin-dir {repo} --output-format json --permission-mode acceptEdits --max-turns {max_turns} --allowedTools 'Skill,Read,Write,Edit,Glob,Grep,Bash(ls:*),Bash(cat:*),Bash(find:*),Bash(grep:*),Bash(python3 {repo}/skills/helix/scripts/:*)'`
Commit: `023e6d14`

| Brief | Mode | Checks | Rubric | Turns | Seconds | Cost USD |
|---|---|---|---|---|---|---|
| narrow-desired-state-edit | evolve | 3/3 | 6/6 | 10 | 25.0 | 0.71 |
| accepted-decision-before-code | review | 3/3 | 6/6 | 10 | 43.4 | 0.83 |
| explicit-implementation-audit | project-audit | 3/3 | 6/6 | 10 | 31.4 | 0.76 |
| frame-prd-from-vision | frame | 5/5 | 6/8 | 43 | 246.7 | 4.57 |
| align-baseline | align | 4/5 | 6/8 | 11 | 138.2 | 1.71 |
| evolve-change-request | evolve | 4/4 | 6/8 | 41 | 134.5 | 2.21 |
| contradiction-mongodb | evolve | 3/3 | 6/6 | 17 | 46.3 | 1.76 |
| present-investor-deck | present | 3/4 | 5/8 | 34 | 224.3 | 3.44 |
| present-survey-deck | present | 4/4 | 8/8 | 38 | 359.8 | 5.12 |
| check-whats-next | check | 4/4 | 6/6 | 9 | 61.0 | 1.15 |
| ambiguous-request | check | 3/3 | 4/4 | 10 | 23.4 | 0.77 |
| validate-prd | validate | 4/4 | 5/6 | 28 | 122.3 | 2.11 |

## Failed checks

- **align-baseline** output_contains: missing ['ALIGNED']
- **present-investor-deck** deliverable_gate: docs/helix/06-iterate/deliverables/DEL-001-investor-business-case.md: visual.unsourced: unit 6 names date 'At the second meeting' that no Sources row or Assumptions entry states

## Rubric notes

- **narrow-desired-state-edit** item 1: 2 — The diff adds the 1–120 character title rule to SHARE-01, SHARE-02 and SHARE-08 plus a matching acceptance row and edge case, and leaves every other requirement unchanged.
- **narrow-desired-state-edit** item 2: 2 — Only the feature spec was edited and the only other source mentioned is the directly related technical design's title limit, with no sign of auditing unrelated decisions or code, though the evidence has no tool trace to confirm what was read.
- **narrow-desired-state-edit** item 3: 2 — The response concisely reports the edit and its locations and flags the one downstream conflict in a single note, with no migration ledger and no delivery-status assessment.
- **accepted-decision-before-code** item 1: 2 — The response opens by stating that absence of code does not invalidate the accepted ADR, which records a desired state that is simply unbuilt.
- **accepted-decision-before-code** item 2: 2 — All findings address ambiguities or inconsistencies in the decision text (triggers, definitions, deployment model, durability, validation method), with none faulting missing implementation; the runbook note is about the ADR's wording.
- **accepted-decision-before-code** item 3: 2 — The response does not request an implementation-status table or any new tracking artifact, and no edits were made.
- **explicit-implementation-audit** item 1: 2 — It states outright that ADR-001 is not implemented and that the repo holds no code or tests of any kind, listing the absent source, migrations, dependencies and test files.
- **explicit-implementation-audit** item 2: 2 — It treats the decision as recorded and Accepted and carried through the docs, and frames the gap purely as missing implementation evidence, though it never says explicitly that the decision itself remains valid.
- **explicit-implementation-audit** item 3: 2 — It claims no delivery, leaves the ADR intact with no edits or tracker items, and limits its extra observations to ADR-related doc inconsistencies without demanding further audits.
- **frame-prd-from-vision** item 1: 1 — Core P0s (discover, save, rate, share, mobile-first, dietary search) and the three vision metrics trace to the vision's positioning and amateur-home-cook market, but the PRD also adds scope the vision does not supply — an invented secondary persona, three self-proposed metrics, follows, and anonymous reading — albeit flagged as assumptions.
- **frame-prd-from-vision** item 2: 2 — The PRD has an explicit Non-Goals section with eight items (native apps, advertising, third-party checkout, editorial content, meal planning, messaging, video, localization), each bounded and consistent with the ad-free, mobile-first, community-sourced vision.
- **frame-prd-from-vision** item 3: 2 — concerns.md is written with slot selections, active concerns, sources, evidence, and explicit not-selected concerns with reasons, all recorded as assumptions awaiting confirmation.
- **frame-prd-from-vision** item 4: 1 — The final response reports 13 open questions and labels key readings (cart, anonymous reading, moderation, proposed metrics, missing baseline) as assumptions or open questions, but several unknowns were still resolved by invention in the body (specific metric targets, PostgreSQL 16, the Marcus persona) and the Open Questions section itself is not visible in the truncated diff.
- **align-baseline** item 1: 2 — Every finding visible in the helix_report carries an artifact path, a line range and path:line evidence entries, though the prose tables themselves give only finding IDs.
- **align-baseline** item 2: 1 — Most high-severity gaps have evidence plus a concrete handoff (destination, deliverable, next mode), but F-6 and F-7 have no handoff or next step, and the recommended-next-step section does not address F-11 to F-16.
- **align-baseline** item 3: 2 — The report is three compact tables of one-line findings, a short next-step paragraph and a structured YAML block, with no restating of artifact content, so it is reviewable in under ten minutes.
- **align-baseline** item 4: 1 — The findings are specific, internally consistent and cite exact lines, with no sign of fabrication, but the fixture text is not in the supplied evidence and the report is truncated, so traceability cannot be confirmed.
- **evolve-change-request** item 1: 1 — ADR-001 was rewritten in place with the title and decision replaced rather than superseded by a new ADR, though the revision is explicitly noted in the Supersession section, Current State, and a retained rejected-alternative row, so it is not silent.
- **evolve-change-request** item 2: 2 — The TD replaces SQLite throughout with PostgreSQL, drops the write queue for a bounded connection pool, adds a database-access port, a 100-concurrent-publisher acceptance criterion, and updated dependencies and risks consistent with the revised ADR.
- **evolve-change-request** item 3: 2 — The response and artifacts surface the unplanned port of existing SQLite-backed auth, the production-vs-all-environments assumption, the unevidenced cost figure, the unselected provider as a PRD open question, and the blocked file rename.
- **evolve-change-request** item 4: 1 — The PRD, ADR and TD were all updated and vision/FEAT were checked, covering the authority chain, but the reported order puts the ADR before the PRD and the evidence does not demonstrate that edits were applied top-down.
- **contradiction-mongodb** item 1: 2 — The response opens by saying no spec was written and names ADR-001's SQLite selection, the PRD's 'Database: SQLite' line and the SQL-based TD as the conflicts, with no files changed.
- **contradiction-mongodb** item 2: 2 — It declines to write a contradicting spec and routes the conflict to an explicit user decision, proposing ADR-002 superseding ADR-001 plus PRD and TD amendments only if the user confirms the override.
- **contradiction-mongodb** item 3: 2 — It challenges day-one sharding against the recorded scale (10,000 monthly users, 500+ recipes, at most 100 concurrent users, single-server and under-$5k constraints) and says nothing in the vision or PRD calls for that scale, though it does not describe the vision's target market itself.
- **present-investor-deck** item 1: 2 — The seven slide titles are full claims that read in sequence as problem, solution, target, cost, and ask, with only the closing 'Sources' slide being a label.
- **present-investor-deck** item 2: 1 — The brief and outline exclude the technology stack and use plain investor language, but the diff is cut off before the slide bodies, so they cannot be checked.
- **present-investor-deck** item 3: 1 — The headline figures (10,000 users, six months, under $5,000, 500 recipes) cite source sections and the response says nothing was invented, but the per-slide bodies and source table are not visible to confirm every number.
- **present-investor-deck** item 4: 1 — The ask names a what (a second meeting with the revenue model and raise amount), but owners are partly inferred and there is no calendar date, and the visible assumptions flag the inferred flow, ask, and owners without clearly naming inferred intake fields such as audience, look, or max messages.
- **present-survey-deck** item 1: 2 — The Story section's concept coverage table lists vision, requirements (PRD), feature specification, decision record (ADR) and technical design as covered with a carrying message, and marks the tech-stack row as omitted with a budget reason; the table is cut off after row 10 in the evidence.
- **present-survey-deck** item 2: 2 — The five messages cover the cook's problem and vision (M5), launch requirements and targets (M4), the recipe sharing feature and its store design (M3), the SQLite decision (M2), and open questions and conflicts (M1).
- **present-survey-deck** item 3: 2 — The Brief states 'Breadth: survey' and 'Must cover: product vision; the data decision; recipe sharing feature', and these are carried by M5, M2 and M3 respectively, each with its own slides.
- **present-survey-deck** item 4: 2 — The titles run from the cook's problem through the launch, the feature, targets, the data decision, the design, conflicts and review triggers to the ask 'The questions blocking the build are yours to close', followed only by a sources appendix.
- **check-whats-next** item 1: 2 — The response names a single next mode (align, restated as next_mode: align in the helix_report) and backs each finding with concrete evidence paths under docs/helix/.
- **check-whats-next** item 2: 2 — Findings cite fixture-specific details (ADR-001 SQLite vs gen_random_uuid(), SHARE-02/04/06/07/08, DELETE /api/v1/recipes/{id}, S3 public-read, 500 seeded recipes) that could only come from reading the artifacts.
- **check-whats-next** item 3: 2 — The response states it changed nothing and is a read-only check, and the workspace diff is empty, so the align work was not started.
- **ambiguous-request** item 1: 2 — The response ends with a scoped clarifying question and grounds it in the fixture's actual contents, listing specific recipe/user intersections from the RecipeHub docs (missing users spec, ownership rules, draft status, concurrent-user numbers).
- **ambiguous-request** item 2: 2 — It explicitly states nothing was changed, the workspace diff is empty, and it offers candidate interpretations rather than inventing and executing a task.
- **validate-prd** item 1: 1 — Structural fixes (FR subsystem headings and IDs, label rename, summary metrics) were made in place and eight judgment findings were left open with handoffs or next steps, but the run also reworded the Goals and deleted the whole Review Checklist section, which are content edits beyond purely mechanical fixes.
- **validate-prd** item 2: 2 — The diff contains no hunks touching the frontmatter, and the report states the legacy ddx.depends_on key was deliberately left unmigrated.
- **validate-prd** item 3: 2 — All thirteen findings carry an Align classification (INCOMPLETE, DIVERGENT or UNDERSPECIFIED), and the summary counts also cover STALE_PLAN and BLOCKED.
