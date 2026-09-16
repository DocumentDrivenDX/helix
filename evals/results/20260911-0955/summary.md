# HELIX eval run 20260911-0955

Runner: `claude -p {prompt} --plugin-dir {repo} --output-format json --permission-mode acceptEdits --max-turns {max_turns} --allowedTools 'Skill,Read,Write,Edit,Glob,Grep,Bash(ls:*),Bash(cat:*),Bash(find:*),Bash(grep:*),Bash(python3:*),Bash(git:*)'`
Commit: `0756e5fa`

| Brief | Mode | Checks | Rubric | Turns | Seconds | Cost USD |
|---|---|---|---|---|---|---|
| frame-prd-from-vision | frame | 5/5 | 8/8 | 64 | 447.0 | 6.75 |
| align-baseline | align | 5/5 | 6/8 | 22 | 391.9 | 3.22 |
| evolve-change-request | evolve | 4/4 | 8/8 | 40 | 240.6 | 2.83 |
| contradiction-mongodb | evolve | 3/3 | 5/6 | 20 | 106.7 | 1.72 |
| present-investor-deck | present | 4/4 | 6/8 | 31 | 353.7 | 3.65 |
| check-whats-next | check | 4/4 | 6/6 | 13 | 124.1 | 1.48 |
| ambiguous-request | check | 3/3 | 4/4 | 9 | 45.4 | 0.71 |
| validate-prd | validate | 4/4 | 5/6 | 31 | 212.3 | 2.46 |

## Failed checks

None.

## Rubric notes

- **frame-prd-from-vision** item 1: 2 — The PRD links informed_by to recipe-app-vision and its summary, personas, goals, and non-goals explicitly reference vision elements (mobile-first, ad-free, home cooks 25-55, peer ratings, publishing, the grocery-cart scenario), with deferred scope pushed to non-goals rather than added as requirements.
- **frame-prd-from-vision** item 2: 2 — Nine explicit non-goals are listed with rationale, each consistent with the vision's ad-free, web-first, community-recipe positioning, and the cart-integration exclusion is tied directly back to the vision scenario.
- **frame-prd-from-vision** item 3: 2 — concerns.md records slot resolution, twenty active concerns with rationale, eight rejected concerns with revisit triggers, and marks every entry as an inference pending operator confirmation.
- **frame-prd-from-vision** item 4: 2 — Eleven open questions are recorded, missing baselines and product owner are flagged as open, leading-indicator targets are marked provisional, and datastore, deploy target, and architecture choices are labeled as assumptions needing ADRs rather than presented as settled.
- **align-baseline** item 1: 2 — Every finding in the table and YAML cites artifact:line references (e.g. F:50, T:107, A:26) plus full paths in the machine block, and N/A checks cite the shell commands used.
- **align-baseline** item 2: 1 — The visible YAML handoffs (F-1 to F-4) each carry destination_type, deliverable, next_mode, and evidence, but the block is truncated so the remaining 19 non-aligned findings cannot be confirmed, and the human-readable table carries no handoff fields at all.
- **align-baseline** item 3: 1 — The findings table and dimension table are dense and do not restate artifacts, but the YAML block repeats all 28 findings with the same claims and evidence, roughly doubling the length and pushing a full read past a quick review.
- **align-baseline** item 4: 2 — Findings are specific, quote concrete text (gen_random_uuid, max-age=300, status DEFAULT 'published'), reuse the same line references consistently across findings, cite ls and git ls-files for absence claims, and the empty workspace diff confirms no artifact was edited; the fixture text itself was not supplied to cross-check.
- **evolve-change-request** item 1: 2 — ADR-001 frontmatter and header status set to Superseded with an explicit forward reference to ADR-002 in the Supersession section, and the decision body was left intact per write-once policy.
- **evolve-change-request** item 2: 2 — TD-recipe-store now depends on ADR-002 and its scope, strategy, components, integration, security, performance, testing, rollback, sequence, prerequisites, risks, and checklist all reflect managed PostgreSQL with a bounded pool, with no residual SQLite assumptions.
- **evolve-change-request** item 3: 2 — The run explicitly records assumptions (no production SQLite data, unresolved provider, pool size), carries them as risks in ADR-002 and the TD, flags the nonexistent runbook ADR-001 cited, and lists unfiled follow-on work rather than silently absorbing these gaps.
- **evolve-change-request** item 4: 2 — Changes were applied PRD first, then ADR-001 supersession and ADR-002 creation, then the TD, with vision and FEAT examined and deliberately left unchanged with stated rationale.
- **contradiction-mongodb** item 1: 2 — The response cites ADR-001-sqlite by path and line, names the contradiction with the PRD and technical design, and explicitly states nothing was written before raising it.
- **contradiction-mongodb** item 2: 2 — It refuses to write a contradicting FEAT, proposes an evolve route with ADR-002 superseding ADR-001, and offers a Proposed-only ADR alternative, leaving the decision to the deciders.
- **contradiction-mongodb** item 3: 1 — It challenges the scale drivers against ADR-001's 100-user sizing, the PRD's single-server constraint, budget cap, and low scalability risk, but never checks them against the vision document's stated target market.
- **present-investor-deck** item 1: 2 — The seven titles read in sequence as a complete argument: what RecipeHub is, why now, who is hurt, what fixes it, why it wins, the ask, sources.
- **present-investor-deck** item 2: 1 — The one visible slide body and notes are clean of HELIX or engineering terms, but the remaining bodies are truncated and the sources slide is described as listing governing sections, which suggests file-path or HELIX section references an investor would not use.
- **present-investor-deck** item 3: 2 — Every number visible (10,000 monthly cooks, four sources, six months, under $5k) is tied to a named vision or PRD section, the response states all figures are labelled as targets, and no untraced number appears.
- **present-investor-deck** item 4: 1 — The ask names the action (a follow-up diligence meeting) and the exhibit promises dated steps with owners, but the ask slide body is not visible, and the assumptions list names missing source content (market, traction, revenue, team) rather than the inferred intake fields such as investor stage, live occasion, or decision sought.
- **check-whats-next** item 1: 2 — It names a single next mode, align, targeted at TD-recipe-store, and backs it with concrete file:line evidence paths for each finding.
- **check-whats-next** item 2: 2 — The response cites specific line numbers and content from the fixture's vision, PRD, FEAT, ADR, and TD files, such as gen_random_uuid at TD line 107 and the DELETE route at line 45, which could only come from reading the artifacts.
- **check-whats-next** item 3: 2 — It states no writes were made, the workspace diff is empty, and it only recommends the align work rather than performing it.
- **ambiguous-request** item 1: 2 — The response asks a scoped clarifying question anchored in concrete fixture contents: the FEAT-recipe-share spec, the users(id) foreign key, PRD personas, and user-scoped behaviors like saves, ratings, comments, and following.
- **ambiguous-request** item 2: 2 — The response explicitly declines to guess at a task, offers candidate interpretations without committing to one, and the workspace diff is empty, so nothing was edited.
- **validate-prd** item 1: 1 — Structural fixes (frontmatter, FR IDs, subsystem headings, checklist items) were mechanical and done in place, but the run also edited judgment content such as rescoping the Problem claim, rewriting the database risk mitigation, and adding success metrics to the Summary, which are framing decisions that should have been handed off.
- **validate-prd** item 2: 2 — The diff shows id, depends_on, and status left unchanged in order, with only type and authoring.home added.
- **validate-prd** item 3: 2 — Every finding F-1 through F-15 carries an ALIGNED, UNDERSPECIFIED, or INCOMPLETE classification and the summary block uses the Align taxonomy counts.
