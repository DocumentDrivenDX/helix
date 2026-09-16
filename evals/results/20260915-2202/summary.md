# HELIX eval run 20260915-2202

Runner: `claude -p {prompt} --plugin-dir {repo} --output-format json --permission-mode acceptEdits --max-turns {max_turns} --allowedTools 'Skill,Read,Write,Edit,Glob,Grep,Bash(ls:*),Bash(cat:*),Bash(find:*),Bash(grep:*),Bash(python3 {repo}/skills/helix/scripts/:*)'`
Commit: `20315d5c`

| Brief | Mode | Checks | Rubric | Turns | Seconds | Cost USD |
|---|---|---|---|---|---|---|
| frame-prd-from-vision | frame | 5/5 | 8/8 | 62 | 449.9 | 6.31 |
| align-baseline | align | 5/5 | 6/8 | 17 | 315.3 | 2.72 |
| evolve-change-request | evolve | 4/4 | 8/8 | 55 | 251.1 | 3.14 |
| contradiction-mongodb | evolve | 3/3 | 6/6 | 22 | 115.7 | 1.75 |
| present-investor-deck | present | 3/4 | 6/8 | 44 | 527.1 | 5.72 |
| present-survey-deck | present | 3/4 | 8/8 | 62 | 920.3 | 7.91 |
| check-whats-next | check | 4/4 | 6/6 | 13 | 146.4 | 1.46 |
| ambiguous-request | check | 2/3 | 4/4 | 12 | 49.9 | 0.70 |
| validate-prd | validate | 4/4 | 5/6 | 32 | 232.2 | 2.48 |

## Failed checks

- **present-investor-deck** deliverable_gate: docs/helix/06-iterate/deliverables/DEL-001-recipehub-investor-evaluation.md: shape.slop: unit 5 bullet 'Every milestone here is a target, not a result': contrastive reversal ', not a'; state the positive claim; coverage.status: concept group 'Market size, revenue model, team, raise amount' has status 'gap'; use covered or omitted
- **present-survey-deck** deliverable_gate: docs/helix/06-iterate/deliverables/DEL-001-engineering-lead-survey.md: title.slop: unit 2 title: over-length (11 words); aim for 8 or fewer, hard stop 10; title.slop: unit 12 title: over-length (11 words); aim for 8 or fewer, hard stop 10
- **ambiguous-request** output_contains: missing ['?']

## Rubric notes

- **frame-prd-from-vision** item 1: 2 — The PRD summary, problem, goals, personas, and metrics explicitly carry the vision's positioning (mobile-first, ad-free, peer ratings, community sharing) and target market (amateur home cooks 25-55), states that each requirement traces to the vision's value propositions, and the one scope widening (report-and-hide moderation in P0) is transparently flagged as a judgment call rather than silently invented.
- **frame-prd-from-vision** item 2: 2 — A dedicated Non-Goals list names nine exclusions (grocery cart, native apps, import, monetization, personalization, video, localization, social features) that are consistent with the ad-free, mobile-first, community positioning, with the vision-mentioned cart moment explicitly parked rather than contradicted and each deferral tracked in the parking lot with rationale and revisit triggers.
- **frame-prd-from-vision** item 3: 2 — concerns.md exists with an Active Concerns table listing source, areas, rationale, and practices per concern, plus slot resolutions, an explicitly unfilled deploy-target slot, considered-and-rejected concerns with revisit triggers, and gaps routed to spikes.
- **frame-prd-from-vision** item 4: 2 — Unknowns are surfaced rather than fabricated: the problem's time/failure quantification is deferred to Open Questions, personas are marked unvalidated, deploy target is left unfilled as an open question, all slot fillers are labeled recorded assumptions to confirm, the 4.2 rating metric is flagged as a possible vanity metric, and the response closes with nine open questions and GUIDANCE_NEEDED status.
- **align-baseline** item 1: 2 — Every finding in the table and the YAML block cites an artifact path with specific line numbers or ranges (e.g. TD-recipe-store.md:108-119, ADR-001:28).
- **align-baseline** item 2: 1 — Findings F-1 through F-9 each carry destination_type, deliverable, next_mode, and evidence, but the YAML is cut off mid-F-10 so handoffs for F-10 through F-19 are not present in the evidence.
- **align-baseline** item 3: 2 — The report leads with a two-line verdict, a compact 19-row findings table, and a dimension table without quoting or restating artifact content, so a reviewer can scan it in well under ten minutes despite the YAML duplicating the table.
- **align-baseline** item 4: 1 — Findings are specific, internally consistent, and cross-reference each other coherently, but the fixture text is not included in the evidence so traceability to real lines cannot be confirmed.
- **evolve-change-request** item 1: 2 — ADR-001 status changed to Superseded with a dated banner, an updated Supersession section pointing to ADR-002, and the body preserved as decision history rather than rewritten.
- **evolve-change-request** item 2: 2 — TD-recipe-store moves its dependency to ADR-002 and rewrites strategy, schema dialect, pooling, transactions, Docker Compose Postgres, testing, cutover, and risks consistently with the PostgreSQL decision, removing all SQLite assumptions.
- **evolve-change-request** item 3: 2 — The response surfaces the pre-empted ADR-001 trigger, the $5k budget tension as a new PRD risk, the never-written runbook, the no-data-migration assumption, the depends_on vs links convention, and the Proposed status needing review, rather than hiding them.
- **evolve-change-request** item 4: 2 — The change starts at the PRD (Frame) technical context, constraints, and risks, then the ADR layer, then the technical design which cites ADR-002 and the FEAT NFR as governing, with lower artifacts inheriting from higher ones.
- **contradiction-mongodb** item 1: 2 — The response states up front that no file was written and names the contradiction with the PRD's SQLite choice and ADR-001 before any spec work.
- **contradiction-mongodb** item 2: 2 — It refuses to write a contradicting FEAT and routes to an operator decision followed by a superseding ADR-002 via the evolve path, or the smaller path of an NFR with ADR-001 review triggers.
- **contradiction-mongodb** item 3: 2 — It challenges the sharding and evolving-metadata drivers against the PRD's fixed recipe model, the 100-concurrent-user target, the single-server constraint, and the $5k cap, calling for a concrete concurrency or volume target.
- **present-investor-deck** item 1: 2 — The six content titles read as a complete narrative (bet, shift, pain, switch, cost and targets, ask) without any body text.
- **present-investor-deck** item 2: 1 — Titles and the brief are free of internal vocabulary and the response asserts clean bodies, but the slide bodies themselves are not visible in the truncated diff so the claim cannot be confirmed.
- **present-investor-deck** item 3: 2 — Every visible figure (six months, under $5,000, five milestones, first year) cites a PRD or vision anchor, and the four figures with no source (market size, revenue, team, raise) are explicitly declined rather than invented.
- **present-investor-deck** item 4: 1 — The ask names what (a second meeting to size the raise) and the beat table promises three steps with owners and dates plus an Assumptions and gaps section, but the owners, dates, and the list of inferred intake fields are not shown in the visible evidence.
- **present-survey-deck** item 1: 2 — The Story section's Concept coverage table lists groups sourced to vision, requirements (PRD), feature spec, decision record (ADR), and technical design, each marked covered with the carrying message and slide, and the final response states the one omitted group (technology stack) with a budget reason.
- **present-survey-deck** item 2: 2 — The five messages span product vision (M4), launch scope and recipe sharing (M3), the SQLite data decision and storage design (M2), open calls gating the build (M1), and success metrics (M5), not a single theme.
- **present-survey-deck** item 3: 2 — The Brief declares Breadth: survey and Must cover: product vision, the data decision, the recipe sharing feature, and the beats table maps vision to M4 (slides 4-5), the data decision to M2 (slide 8), and recipe sharing to M3 (slide 7).
- **present-survey-deck** item 4: 2 — Read in sequence the titles move from the five draft documents through the market, vision, launch scope, recipe sharing, the SQLite decision, the build path, open calls, and success numbers, ending in the ask to close the four calls and start the build at the schema, with only a sources appendix after.
- **check-whats-next** item 1: 2 — It names `align` as the single next mode, repeats it in the report's next_mode field, and each finding cites specific artifact paths with line numbers as evidence.
- **check-whats-next** item 2: 2 — The response quotes fixture-specific details (PostgreSQL DDL vs SQLite ADR, SHARE-04 draft contradiction, missing user-stories directory, ADR Proposed since 2026-05-01) with file:line references, showing it read the actual artifacts.
- **check-whats-next** item 3: 2 — It explicitly states a read-only pass with no files changed, and the empty workspace diff confirms no align or frame work was started.
- **ambiguous-request** item 1: 2 — The response asks the user to pick from a scoped list of concrete gaps grounded in the actual RecipeHub docs, including the recipe sharing feature spec and the unresolved users table/auth artifact.
- **ambiguous-request** item 2: 2 — It explicitly declines to guess, makes no edits (empty workspace diff), and only proposes a task conditionally pending the user's confirmation.
- **validate-prd** item 1: 1 — Structural fixes (FR IDs, type key, checklist items, label rename) were applied in place and judgment items like the quantified problem and named personas were handed off, but the agent also authored new content in place (an Open Questions entry and a metrics sentence in Summary), which are judgment edits rather than mechanical ones.
- **validate-prd** item 2: 2 — The diff shows all existing frontmatter keys, including legacy depends_on, unchanged in value and order, with only a new type key inserted.
- **validate-prd** item 3: 2 — Every finding F-0 through F-11 in the helix_report carries an Align taxonomy classification (ALIGNED, INCOMPLETE, UNDERSPECIFIED) and the summary tallies all six taxonomy buckets.
