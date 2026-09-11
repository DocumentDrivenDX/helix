---
title: "Deliverable"
linkTitle: "Deliverable"
slug: deliverable
activity: "Iterate"
artifactRole: "supporting"
weight: 90
generated: true
---

## Purpose

A human-facing projection of governed artifacts: the script for a deck,
one-pager, or brief, written in the human-facing voice with claim titles,
a visual per unit, speaker notes, and a Sources appendix tracing every
figure to a governing artifact section. The Markdown script is the document
of record; rendered files (pptx, html, pdf, docx) are fidelity evidence
listed in `authoring.export`. Produced by the `present` mode.

## Example

<details open>
<summary>Show a worked example of this artifact</summary>

``````markdown
---
ddx:
  id: example.deliverable.depositmatch-pilot-deck
  type: deliverable
  activity: iterate
  kind: deck
  status: draft
  authoring:
    home: repo
    export:
      - docs/helix/06-iterate/deliverables/assets/DEL-001-depositmatch-pilot.pptx
      - docs/helix/06-iterate/deliverables/assets/DEL-001-depositmatch-pilot.html
      - docs/helix/06-iterate/deliverables/assets/DEL-001-depositmatch-pilot.pdf
  links:
    - id: example.business-case.depositmatch
      kind: informed_by
    - id: example.product-vision.depositmatch
      kind: informed_by
---

# A three-month pilot can win back reviewer hours at bookkeeping firms

## Brief

- **Audience**: the firm-owner sponsor and the two partners who approve product spend
- **Occasion**: monthly investment review, 20-minute slot, deck presented live then sent as PDF
- **Decision or action sought**: approve the three-month pilot budget and name who recruits pilot firms
- **Time slot or page budget**: 20 minutes, at most 10 content slides
- **Kind**: deck
- **Constraints**: no client names; figures marked as assumptions stay marked; house theme
- **Takeaway**: a bounded CSV-first pilot is the cheapest way to learn whether reviewers trust suggested matches and whether firms will pay for the time saved

## Story

- **Spine**: pyramid
- **Titles-only read**:
  1. A three-month pilot can win back reviewer hours at bookkeeping firms
  2. Approve a three-month pilot that shows reviewers the evidence behind each match
  3. Firms spend $1.2B a year on deposit matching; $180M is reachable
  4. Firms lose reviewer capacity to manual deposit matching every week
  5. A CSV-first pilot tests reviewer trust faster than bank feeds
  6. Year one costs $262,000; the pilot plan breaks even in month 18
  7. Three risks decide the pilot, and each one has a mitigation
  8. Two conditions gate any spend beyond the pilot
  9. Approve the pilot budget and name a pilot recruiter by month end
  10. Sources

## Content

### 1. A three-month pilot can win back reviewer hours at bookkeeping firms

**Pattern**: title
**Body**:
- Investment review, prepared for the sponsor and approving partners
**Visual**: kind: none. Full-bleed dark surface with the deck title lower-left, the hollow marker motif on the right, and the review date beneath
**Notes**: Open with the takeaway sentence from the brief. Say up front that the ask comes on the last slide and takes two decisions.
**Sources**: S1

### 2. Approve a three-month pilot that shows reviewers the evidence behind each match

**Pattern**: claim-evidence
**Body**:
- The pilot builds three things and nothing else
- Reviewers see the evidence behind every suggested match before approving it
- Every exception has a named owner instead of a shared spreadsheet
- Spend beyond the pilot waits for two measured conditions
**Visual**: kind: process-flow | steps: Import; Review; Own exceptions | highlight: 2 | caption: reviewers see the evidence first. Three-step process strip drawn from the pilot scope in the business case, with the review step highlighted
**Notes**: This is the answer-first slide. The rest of the deck supports it: the size of the problem, why this scope, what it costs, what could go wrong, and what we need today.
**Sources**: S1, S2

### 3. Firms spend $1.2B a year on deposit matching; $180M is reachable

**Pattern**: stat-callout
**Body**:
- $1.2B spent yearly on reconciliation labor and tools across small firms
- $180M of that sits in firms of the size we can serve
- Both figures are planning assumptions until the research plan validates them
**Visual**: kind: stat | stats: $1.2B / spent yearly on reconciliation labor and tools across 60,000 small firms; $180M / within reach at the 9,000 firms of the size we can serve | label: planning assumption. Two stat callouts from the opportunity sizing, $1.2B in the primary hue and $180M in the secondary hue, the firm counts as baseline captions
**Notes**: The total assumes 60,000 small bookkeeping firms spending about $20,000 a year each. The reachable slice is the 9,000 firms with five to twenty-five staff. Say plainly that confidence is low and that the pilot is partly how we raise it.
**Sources**: S3, S4

### 4. Firms lose reviewer capacity to manual deposit matching every week

**Pattern**: claim-evidence
**Body**:
- Deposit matching is a weekly chore that competes with client work
- Matching happens across exports, bank statements, and email threads
- Closing the spreadsheet throws away the evidence behind each match
- Firm owners pay for saved time only when they can audit the result
**Visual**: kind: panels | items: Exports / matching happens across exports, bank statements, and email threads; Spreadsheet / closing it throws away the evidence behind each match; Audit / owners pay for saved time only when they can audit the result. Three panels standing in for the annotated matching-spreadsheet screenshot, each marking a place evidence goes missing
**Notes**: Keep this to the lived experience; the sponsor knows the pain. The point is that time saved without an audit trail is not something a firm will pay for.
**Sources**: S5

### 5. A CSV-first pilot tests reviewer trust faster than bank feeds

**Pattern**: two-column-comparison
**Body**:
- CSV-first: learns about reviewer trust in weeks; needs pilot recruiting and careful data handling
- Bank feeds first: stronger automation story; longer build, higher integration risk, slower learning
- Spreadsheet templates: cheapest; keeps no evidence and does not reduce context switching
- Verdict: CSV-first, because the open question is trust, not automation
**Visual**: kind: two-column | left: CSV-first pilot | right: Bank feeds first | rows: Learns about reviewer trust in weeks / Stronger automation story; Needs pilot recruiting and careful data handling / Longer build and higher integration risk; Answers the open question first / Slower learning about the open question | prefer: left | verdict: CSV-first, because the open question is trust, not automation. Two columns from the alternatives table in the business case with the check mark on the preferred column
**Notes**: The alternatives table in the business case also rejects doing nothing for a quarter; mention it only if asked. The comparison is about what we learn fastest.
**Sources**: S6

### 6. Year one costs $262,000; the pilot plan breaks even in month 18

**Pattern**: table
**Body**:
- Year one: $180,000 development, $12,000 infrastructure, $40,000 go-to-market, $30,000 operations
- Year one revenue of $120,000 leaves a $142,000 shortfall we fund deliberately
- Breakeven arrives in month 18 if pilot conversion and pricing hold
**Visual**: kind: table | columns: Year one line / Amount | rows: Development / $180,000; Infrastructure / $12,000; Go-to-market / $40,000; Operations / $30,000; Total / $262,000 | highlight: 5. Five-row cost table for year one from the investment section with the total row highlighted; the month-18 breakeven stays in the body
**Notes**: Years two and three are in the appendix source; do not present them unless a partner asks. The three-year return figure depends on pricing we have not validated, so lead with the year-one number the committee approves.
**Sources**: S7, S8

### 7. Three risks decide the pilot, and each one has a mitigation

**Pattern**: risk-matrix
**Body**:
- Exports vary too much: recruit pilots across three accounting systems, map per client
- Reviewers distrust suggestions: show evidence before approval, require reviewer acceptance
- Firms will not pay enough: validate willingness to pay before widening scope
**Visual**: kind: risk-grid | risks: Exports vary too much / high / medium; Reviewers distrust suggestions / medium / high; Firms will not pay enough / medium / high. Likelihood-by-impact grid from the risk assessment with the three risks as numbered dots and the mitigations from the body keyed by number on the right
**Notes**: The export-variability risk is the most likely and the one the recruiter can reduce before build starts, which is why the ask names a recruiter.
**Sources**: S9

### 8. Two conditions gate any spend beyond the pilot

**Pattern**: claim-evidence
**Body**:
- Recruit at least five pilot firms before expanding beyond import and review
- Measure median reconciliation time and suggestion accuracy during the first two months
- A paid product waits until weekly reconciliation falls under 3 minutes per client
**Visual**: kind: panels | items: Five pilot firms / recruited before expanding beyond import and review; Two measures / median reconciliation time and suggestion accuracy in the first two months. Two condition cards from the recommendation, with the 3-minute paid-product target in the body
**Notes**: These are the conditions in the business case recommendation. They are the sponsor's protection against scope creep and the team's protection against building on unvalidated demand.
**Sources**: S2, S10

### 9. Approve the pilot budget and name a pilot recruiter by month end

**Pattern**: ask-next-steps
**Body**:
- Approve the year-one pilot budget of $262,000 today
- Name the partner who recruits five pilot firms, by month end
- Product lead reports median reconciliation time at the two-month checkpoint
- No decision today delays the pilot a full quarter and keeps firms in manual matching
**Visual**: kind: none | owners: investment committee; a named partner; product lead | dates: today; month end; two-month checkpoint. Ask band in the secondary hue, then three numbered steps with owner and date columns filled from the body
**Notes**: Stop talking after the ask. If the committee wants the three-year numbers, they are in the appendix source and the business case.
**Sources**: S7, S10

### 10. Sources

**Pattern**: appendix-sources
**Body**:
- Every figure and claim above maps to a section of the business case or product vision listed below
**Visual**: kind: none. Two-column source list in caption size, claim on the left, artifact section on the right
**Notes**: Not presented.
**Sources**: S1

## Sources

| Id | Claim or figure | Governing artifact and section |
|---|---|---|
| S1 | Recommended investment is a three-month pilot build for CSV import, evidence-backed match review, and exception ownership | docs/helix/00-discover/business-case.md#executive-summary |
| S2 | Decision: Conditional Go; conditions: recruit at least five pilot firms; measure median reconciliation time and suggestion acceptance accuracy during the first two months | docs/helix/00-discover/business-case.md#recommendation |
| S3 | TAM $1.2B annual workflow spend: 60,000 small bookkeeping firms x $20,000; planning assumption, low confidence | docs/helix/00-discover/business-case.md#opportunity-sizing |
| S4 | SAM $180M: 9,000 firms with five to twenty-five employees x $20,000; medium confidence | docs/helix/00-discover/business-case.md#opportunity-sizing |
| S5 | Firms are losing reviewer capacity to manual deposit matching; firm owners will pay for auditability plus time saved | docs/helix/00-discover/business-case.md#executive-summary, docs/helix/00-discover/product-vision.md#positioning |
| S6 | Alternatives: CSV-first pilot (carry forward), bank feed and accounting sync first (reject for v1), spreadsheet templates (reject), do nothing for one quarter (reject) | docs/helix/00-discover/business-case.md#alternatives-considered |
| S7 | Year one: development $180,000, infrastructure $12,000, go-to-market $40,000, operations $30,000; total costs $262,000 | docs/helix/00-discover/business-case.md#investment-required, docs/helix/00-discover/business-case.md#expected-roi |
| S8 | Year one revenue $120,000, net $142,000 shortfall (shown as -$142,000); breakeven month 18; confidence low until the pilot validates conversion and pricing | docs/helix/00-discover/business-case.md#expected-roi |
| S9 | Risks: CSV exports vary (high, medium); reviewers distrust suggested matches (medium, high); firms will not pay enough (medium, high), each with the mitigation quoted | docs/helix/00-discover/business-case.md#risk-assessment |
| S10 | Paid product path if weekly reconciliation time falls below 3 minutes per client | docs/helix/00-discover/business-case.md#executive-summary |

## Assumptions and gaps

- **Assumption**: the committee approves year-one spend only; years two and three are informational. Inferred from the occasion (monthly investment review). The sponsor should confirm.
- **Gap**: the business case names no pilot recruiter; the ask has the committee name one instead of inventing an owner.
- **Gap**: no artifact holds the review date or presenter; both come from the meeting invite at render time.

## Render

- **Theme**: deliverables/theme.yml (no project design-system declared)
- **Targets**: docs/helix/06-iterate/deliverables/assets/DEL-001-depositmatch-pilot.pptx, docs/helix/06-iterate/deliverables/assets/DEL-001-depositmatch-pilot.html, docs/helix/06-iterate/deliverables/assets/DEL-001-depositmatch-pilot.pdf
- **Gate**: script checks pass (check-deliverable.py, 0 blocking); fidelity pass (every stat callout re-read against the business case); voice pass (Vale Helix styles, 0 errors); visual: every slide rendered to an image and inspected on 2026-09-10, one overflow on slide 6 fixed by shortening the third bullet; file: presentation validator pass, HTML page renders with no console errors
``````

</details>

## Reference

<table class="helix-reference-table">
<tbody>
<tr><th>Activity</th><td><a href="../../../reference/glossary/activities/"><strong>Iterate</strong></a> — Measure, align, and improve. Close the feedback loop back into the planning strand.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/06-iterate/deliverables/DEL-[nnn]-[slug].md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Deliverable Generation Prompt&#10;&#10;You are writing the script for a deck, one-pager, or brief that projects&#10;governed HELIX artifacts for people outside the project. Follow the `present`&#10;mode contract (`modes/present.md`); this prompt covers what the script itself&#10;must contain.&#10;&#10;## Before writing&#10;&#10;- Confirm the Brief fields: audience, occasion, decision sought, time slot or&#10;  page budget, kind, constraints, takeaway. At `low`/`medium` autonomy, ask&#10;  for missing fields in one message. At `high`, infer and record each&#10;  inference under Assumptions and gaps. No audience or no decision sought&#10;  means stop; there is nothing to present yet.&#10;- Read every source section you will project. Use `deliverable-mappings.yml`&#10;  for the source type; merge units when several sources apply. Note&#10;  `gaps_to_ask` for the source type and resolve each one.&#10;- Choose the flow by occasion from `deliverables/deck-flows.yml`; the&#10;  reasoning is in `deliverables/deck-craft.md`.&#10;&#10;## Storyboard (before any body text)&#10;&#10;- Distill: write the takeaway sentence; then three to five messages that&#10;  make it true, ranked by how much each moves the audience&#x27;s decision; then&#10;  the evidence for each message as source sections and the one figure,&#10;  example, or comparison the slide will carry. A message without a source&#10;  section is a gap or an assumption, not a slide.&#10;- Title every beat in the flow with a claim, mapped to a message, with a&#10;  one-line note of the exhibit. Include optional beats only when a message&#10;  needs them. Cut beats in the flow&#x27;s `keep_when_short` order when the slot&#10;  is tight; never compress two beats into one slide.&#10;- Run the horizontal-logic test: read the titles in order. Each answers the&#10;  question the previous title raised; the last content title is the ask in&#10;  the takeaway&#x27;s words; the titles alone give the argument. Rewrite until&#10;  it passes.&#10;- Record flow, takeaway, messages with evidence, the beat-to-title table,&#10;  and the test result under Story.&#10;&#10;## Writing the script&#10;&#10;- One pattern per unit, from the beat&#x27;s allowed set in `deck-flows.yml`,&#10;  chosen by content shape from `slide-patterns.yml`. Stay inside the&#10;  pattern&#x27;s limits; an overflowing unit becomes two units. Keep the density&#10;  rules: no three consecutive units of one pattern, at most one stat callout&#10;  per section, a visual on every content unit.&#10;- Each body proves its title and nothing else. One number per beat; the&#10;  rest goes to notes. Callbacks use the earlier slide&#x27;s words.&#10;- Bodies are in the `human-facing` voice: plain words, one idea per bullet,&#10;  active verbs, concrete consequences, sentence variety. No HELIX or&#10;  engineering vocabulary in bodies: artifact IDs, activity names, work-item&#10;  terms, and acceptance-criterion codes belong only in Sources and the&#10;  frontmatter. Define or drop any term the audience would not use.&#10;- Visual lines say what the visual shows, its series or elements, and the&#10;  source it is drawn from (&quot;bar chart of median reconciliation minutes per&#10;  client, weeks 1 to 8, from the pilot metrics table&quot;). &quot;Chart&quot; or &quot;diagram&quot;&#10;  alone is a gate failure.&#10;- Notes carry the supporting detail the slide omits, in the same voice, so a&#10;  reader of the script alone can present it.&#10;- Every number in a body appears in Sources with the governing artifact&#10;  path and section. Subset the source when the audience needs less; never&#10;  contradict it, and never round a sourced figure into a different claim.&#10;- Deck order: title, optional agenda (10 or more slides), content units in&#10;  the flow&#x27;s beat order, ask-next-steps, appendix-sources. One-pager and&#10;  brief: takeaway, sections, ask, sources footer.&#10;&#10;## After writing&#10;&#10;- Run the script checks (`scripts/check-deliverable.py`) and fix every&#10;  blocking finding.&#10;- Re-run the horizontal-logic test on the finished titles, then the&#10;  vertical-logic test on every unit: the body proves the title and the title&#10;  is proven by the body. Rewrite the title to what the body proves, or cut&#10;  the unit.&#10;- Walk the flow&#x27;s `checklist` in `deck-flows.yml`.&#10;- Render to the targets, then render every slide or page to an image and&#10;  look at each one. Fix overflow, collisions, orphan bullets, poor contrast,&#10;  and missing visuals; re-render.&#10;- Fill the Render section with theme, targets, and gate results. Leave&#10;  `status: draft`; a person approves the deliverable like any artifact.</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---&#10;ddx:&#10;  id: DEL-[nnn]&#10;  type: deliverable&#10;  activity: iterate&#10;  kind: [deck | one-pager | brief]&#10;  status: draft&#10;  authoring:&#10;    home: repo&#10;    export:&#10;      - [path to rendered .pptx / .html / .pdf / .docx]&#10;  links:&#10;    - id: [source artifact id]&#10;      kind: informed_by&#10;---&#10;&#10;# [Deck or document title: the takeaway as a claim]&#10;&#10;## Brief&#10;&#10;- **Audience**: [who decides or acts; role, not name, unless a name matters]&#10;- **Occasion**: [meeting, send-ahead, board pack, workshop]&#10;- **Decision or action sought**: [one sentence]&#10;- **Time slot or page budget**: [minutes or pages]&#10;- **Kind**: [deck | one-pager | brief]&#10;- **Constraints**: [brand, confidentiality, must-include, must-omit]&#10;- **Takeaway**: [the one sentence the audience should leave with]&#10;&#10;## Story&#10;&#10;- **Flow**: [flow id from deck-flows.yml, chosen by occasion]&#10;- **Takeaway**: [the sentence every title builds to; same words as the Brief]&#10;- **Messages** (three to five claims that make the takeaway true, ranked by the audience&#x27;s decision; each with the source sections that prove it):&#10;  1. [message as a claim] (evidence: [path#section], [figure or example it supplies])&#10;  2. [message as a claim] (evidence: [path#section], [...])&#10;  3. [...]&#10;- **Beats and titles** (one row per beat in the flow; titles written before any body):&#10;&#10;  | # | Beat | Title (claim) | Message | Exhibit |&#10;  |---|---|---|---|---|&#10;  | 1 | [beat name] | [claim title] | [M1] | [one line: what will prove the title] |&#10;  | 2 | [beat name] | [claim title] | [M2] | [...] |&#10;  | [n] | ask | [the ask as a claim] | [takeaway] | [ask band, steps with owners and dates] |&#10;&#10;- **Horizontal-logic test**: [pass, or the titles rewritten to make it pass: each title answers the question the previous one raised; the titles alone give the argument and the ask]&#10;&#10;## Content&#10;&#10;### 1. [Claim title]&#10;&#10;**Pattern**: [pattern id from slide-patterns.yml]&#10;**Body**:&#10;- [evidence bullet within the pattern&#x27;s limits]&#10;- [evidence bullet]&#10;**Visual**: [what it shows, the series or elements, the source it is drawn from]&#10;**Notes**: [speaker notes: the detail the slide omits, in the same voice]&#10;**Sources**: [S1, S2]&#10;&#10;### 2. [Claim title]&#10;&#10;**Pattern**: [pattern id]&#10;**Body**:&#10;- [...]&#10;**Visual**: [...]&#10;**Notes**: [...]&#10;**Sources**: [S3]&#10;&#10;### [n]. [The ask as a claim]&#10;&#10;**Pattern**: ask-next-steps&#10;**Body**:&#10;- [next step, owner, date]&#10;- [next step, owner, date]&#10;- [what happens if no decision]&#10;**Visual**: [ask band plus numbered steps with owner and date columns]&#10;**Notes**: [...]&#10;**Sources**: [S1]&#10;&#10;## Sources&#10;&#10;| Id | Claim or figure | Governing artifact and section |&#10;|---|---|---|&#10;| S1 | [claim or number as it appears in the body] | [path#section] |&#10;| S2 | [...] | [...] |&#10;&#10;## Assumptions and gaps&#10;&#10;- **Assumption**: [what was inferred, from what, and who should confirm it]&#10;- **Gap**: [content the deliverable needed that no artifact holds; how it was handled]&#10;&#10;## Render&#10;&#10;- **Theme**: [project design-system | deliverables/theme.yml]&#10;- **Targets**: [pptx path], [html path], [pdf path]&#10;- **Gate**: script checks [pass/fail with check ids], horizontal logic [pass], vertical logic [pass], fidelity [pass], voice [pass], visual [every slide rendered to an image and inspected on &lt;date&gt;], file [validator result]</code></pre></details></td></tr>
</tbody>
</table>
