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
of record; rendered files (pptx, and pdf when the host exports one) are fidelity evidence
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
      - docs/helix/06-iterate/deliverables/assets/DEL-001-depositmatch-pilot.pdf
  links:
    - id: example.business-case.depositmatch
      kind: informed_by
    - id: example.product-vision.depositmatch
      kind: informed_by
---

# A three-month pilot wins back reviewer hours

## Brief

- **Audience**: the firm-owner sponsor and the two partners who approve product spend
- **Occasion**: monthly investment review, 20-minute slot, deck presented live then sent as PDF
- **Decision or action sought**: approve the three-month pilot budget and name who recruits pilot firms
- **Time slot or page budget**: 20 minutes, at most 10 content slides
- **Kind**: deck
- **Constraints**: no client names; figures marked as assumptions stay marked; house theme
- **Look**: editorial
- **Scope**: docs/helix/00-discover/business-case.md; docs/helix/00-discover/product-vision.md
- **Breadth**: deep-dive
- **Angle**: the investment decision
- **Must cover**: pilot scope; investment and breakeven; risks
- **Must omit**: none
- **Max messages**: 4
- **Takeaway**: a bounded CSV-first pilot is the cheapest way to learn whether reviewers trust suggested matches and whether firms will pay for the time saved

## Story

- **Flow**: proposal
- **Takeaway**: a bounded CSV-first pilot is the cheapest way to learn whether reviewers trust suggested matches and whether firms will pay
- **Messages** (ranked by how much each moves the decision to fund the pilot):
  1. Firms lose reviewer capacity to manual deposit matching every week, and the market is large enough to matter (evidence: docs/helix/00-discover/business-case.md#executive-summary; docs/helix/00-discover/business-case.md#opportunity-sizing)
  2. A CSV-first pilot learns about reviewer trust faster and cheaper than integrating bank feeds (evidence: docs/helix/00-discover/business-case.md#alternatives-considered)
  3. Year one costs $262,000 and the plan breaks even in month 18 if pilot conversion and pricing hold (evidence: docs/helix/00-discover/business-case.md#investment-required; docs/helix/00-discover/business-case.md#expected-roi)
  4. Three risks decide the pilot, each with a mitigation, and two conditions gate spend beyond it (evidence: docs/helix/00-discover/business-case.md#risk-assessment; docs/helix/00-discover/business-case.md#recommendation)
- **Beats and titles** (beat ids from the proposal flow in deck-flows.yml; titles written before any body):

  | # | Beat | Title (claim) | Message | Exhibit |
  |---|---|---|---|---|
  | 1 | recommendation | A three-month pilot wins back reviewer hours | takeaway | title slide |
  | 2 | situation | Firms spend $1.2B a year on reviewers matching deposits | M1 | two stat callouts |
  | 3 | complication | Firms lose reviewer capacity to manual deposit matching every week | M1 | three panels where evidence goes missing |
  | 4 | options-considered | A CSV-first pilot tests reviewer trust faster than bank feeds | M2 | two-column comparison with the do-nothing row |
  | 5 | recommended-option | Approve a pilot that shows reviewers the evidence | M2 | three-step process strip |
  | 6 | return | The pilot breaks even in month 18 on planned pricing | M3 | timeline to breakeven |
  | 7 | cost | The pilot costs $262,000 in year one | M3 | cost table with the total highlighted |
  | 8 | risks | Three risks decide the pilot, each with a mitigation | M4 | risk grid |
  | 9 | plan | Two conditions gate any spend beyond the pilot | M4 | checkpoint strip |
  | 10 | ask | Approve the pilot budget and name a recruiter | takeaway | ask band and steps |
  | 11 | sources | Sources | all | source table |

- **Concept coverage** (every concept group the inventory surfaced, in authority order):

  | # | Concept group | Authority | Status | Carried by / reason |
  |---|---|---|---|---|
  | 1 | Pilot scope: import, evidence-backed review, exception ownership | business case, vision | covered | M2 |
  | 2 | Market and opportunity sizing | business case | covered | M1 |
  | 3 | Investment and breakeven | business case | covered | M3 |
  | 4 | Risks and gating conditions | business case | covered | M4 |
  | 5 | Alternatives considered | business case | covered | M2 |
  | 6 | Strategic alignment with the firm's goals | business case | omitted | angle: the committee decides on cost and risk, and the goals row restates the pilot scope |
  | 7 | Product vision and positioning | vision | omitted | audience: the sponsor authored the vision; slide 3 carries the pain it names |

- **Horizontal-logic test**: pass. The titles move from the answer (1) through what the audience already accepts (2), what it costs them (3), the choices (4), what the pilot is (5), what it returns and costs (6, 7), what could go wrong (8, 9), and back to the ask (10); each shares a word with the one before, and the ask repeats "pilot" from the takeaway.

## Content

### 1. A three-month pilot wins back reviewer hours

**Pattern**: title
**Body**:
- Investment review, prepared for the sponsor and approving partners
**Visual**: kind: none | icon: search. Full-bleed dark surface with the deck title lower-left, the hero marker on the right carrying the deck's one icon, and the review date beneath
**Notes**: Open with the takeaway sentence from the brief. Say up front that the ask comes on the last slide and takes two decisions.
**Sources**: S1

### 2. Firms spend $1.2B a year on reviewers matching deposits

**Pattern**: stat-callout
**Body**:
- $1.2B spent yearly on reconciliation labor and tools across small firms
- $180M of that sits in firms of the size we can serve
- Both figures are planning assumptions until the research plan validates them
**Visual**: kind: stat | stats: $1.2B / spent yearly on reconciliation labor and tools across 60,000 small firms; $180M / within reach at the 9,000 firms of the size we can serve | label: planning assumption. Two stat callouts from the opportunity sizing, $1.2B in the primary hue and $180M in the secondary hue, the firm counts as baseline captions
**Notes**: The total assumes 60,000 small bookkeeping firms spending about $20,000 a year each. The reachable slice is the 9,000 firms with five to twenty-five staff. Say plainly that confidence is low and that the pilot is partly how we raise it.
**Sources**: S3, S4

### 3. Firms lose reviewer capacity to manual deposit matching every week

**Pattern**: claim-evidence
**Body**:
- Deposit matching is a weekly chore that competes with client work
- A reviewer reconciles each deposit by hand against three separate sources
- The reasoning behind a match lives in one person's head once the sheet closes
- Saved hours count for an owner only when the result can be checked afterwards
**Visual**: kind: panels | items: Exports / matching happens across exports, bank statements, and email threads; Spreadsheet / closing it throws away the evidence behind each match; Audit / owners pay for saved time only when they can audit the result. Three panels standing in for the annotated matching-spreadsheet screenshot, each marking a place evidence goes missing
**Notes**: Keep this to the lived experience; the sponsor knows the pain. The point is that time saved without an audit trail is not something a firm will pay for.
**Sources**: S5

### 4. A CSV-first pilot tests reviewer trust faster than bank feeds

**Pattern**: two-column-comparison
**Body**:
- CSV-first: learns about reviewer trust in weeks; needs pilot recruiting and careful data handling
- Bank feeds first: stronger automation story; longer build, higher integration risk, slower learning
- Doing nothing for a quarter: rejected; every reviewer hour stays lost to manual matching
- Verdict: CSV-first, because the open question is reviewer trust
**Visual**: kind: two-column | left: CSV-first pilot | right: Bank feeds first | rows: Learns about reviewer trust in weeks / Stronger automation story; Needs pilot recruiting and careful data handling / Longer build and higher integration risk; Against doing nothing, saves the quarter of manual matching / Against doing nothing, saves nothing until the build lands | prefer: left | verdict: CSV-first, because the open question is reviewer trust. Two columns from the alternatives table in the business case with the check mark on the preferred column and the do-nothing baseline as the last row
**Notes**: The alternatives table in the business case also rejects spreadsheet templates, which keep no evidence; mention them only if asked. The comparison is about what we learn fastest, and doing nothing learns nothing.
**Sources**: S5, S6

### 5. Approve a pilot that shows reviewers the evidence

**Pattern**: claim-evidence
**Body**:
- The pilot builds three things and nothing else
- Reviewers see the evidence behind every suggested match before approving it
- Every exception has a named owner instead of a shared spreadsheet
- Spend beyond the pilot waits for two measured conditions
**Visual**: kind: process-flow | steps: Import; Review; Own exceptions | highlight: 2 | caption: reviewers see the evidence first. Three-step process strip drawn from the pilot scope in the business case, with the review step highlighted
**Notes**: This is what the committee is buying. The next two slides say what it returns and what it costs; the two after that say what could go wrong and when we would stop.
**Sources**: S1, S2

### 6. The pilot breaks even in month 18 on planned pricing

**Pattern**: claim-evidence
**Body**:
- Year one revenue of $120,000 leaves a $142,000 shortfall we fund deliberately
- Breakeven arrives in month 18 if pilot conversion and pricing hold
- The three-year return rests on pricing the pilot has not yet validated
**Visual**: kind: timeline | milestones: Pilot starts; Year one closes with $120,000 revenue; Breakeven in month 18; Three-year return | now: 1 | marker: today | caption: the shortfall is funded until month 18 | side: left. Net line over three years drawn from the expected ROI section, with the breakeven month marked in the secondary hue
**Notes**: The model is in the expected ROI section: revenue ramps with pilot conversion, and the three-year return depends on the price point the pilot tests. Lead with the breakeven month; the return figure waits for a partner to ask.
**Sources**: S8

### 7. The pilot costs $262,000 in year one

**Pattern**: table
**Body**:
- Year one: $180,000 development, $12,000 infrastructure, $40,000 go-to-market, $30,000 operations
- Development takes $180,000 of the $262,000 total
**Visual**: kind: table | columns: Year one line / Amount | rows: Development / $180,000; Infrastructure / $12,000; Go-to-market / $40,000; Operations / $30,000; Total / $262,000 | highlight: 5. Five-row cost table for year one from the investment section with the total row highlighted
**Notes**: Years two and three are in the appendix source; do not present them unless a partner asks. Lead with the year-one number the committee approves.
**Sources**: S7

### 8. Three risks decide the pilot, each with a mitigation

**Pattern**: risk-matrix
**Body**:
- Exports vary too much: recruit pilots across three accounting systems, map per client
- Reviewers distrust suggestions: show evidence before approval, require reviewer acceptance
- Firms will not pay enough: validate willingness to pay before widening scope
**Visual**: kind: risk-grid | risks: Exports vary too much / high / medium; Reviewers distrust suggestions / medium / high; Firms will not pay enough / medium / high. Likelihood-by-impact grid from the risk assessment with the three risks as numbered dots and the mitigations from the body keyed by number on the right
**Notes**: The export-variability risk is the most likely and the one the recruiter can reduce before build starts, which is why the ask names a recruiter. The business case names no risk owners; the ask has the committee name one.
**Sources**: S9

### 9. Two conditions gate any spend beyond the pilot

**Pattern**: process-flow
**Body**:
- Recruit at least five pilot firms before expanding beyond import and review
- Both measures are read at the two-month checkpoint, before any expansion decision
- A paid product waits until weekly reconciliation falls under 3 minutes per client
**Visual**: kind: process-flow | steps: Recruit five firms; Read two measures; Expand or stop | highlight: 2 | caption: the two-month checkpoint is where the committee can stop the pilot. Three-step checkpoint strip from the recommendation's conditions, with the 3-minute paid-product target in the body
**Notes**: These are the conditions in the business case recommendation. They are the sponsor's protection against scope creep and the team's protection against building on unvalidated demand.
**Sources**: S2, S10

### 10. Approve the pilot budget and name a recruiter

**Pattern**: ask-next-steps
**Body**:
- Approve the year-one pilot budget of $262,000 today
- Name the partner who recruits five pilot firms, by month end
- Product lead reports median reconciliation time at the two-month checkpoint
**Visual**: kind: none | ask: Fund the pilot and name the recruiter today | owners: investment committee; a named partner; product lead | dates: today; month end; two-month checkpoint | consequence: No decision today delays the pilot a full quarter and keeps firms in manual matching. Ask band in the secondary hue carrying the decision, then three numbered steps with owner and date columns filled from the body
**Notes**: Stop talking after the ask. If the committee wants the three-year numbers, they are in the appendix source and the business case.
**Sources**: S7, S10

### 11. Sources

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
| S9 | Risks: CSV exports vary (high, medium); reviewers distrust suggested matches (medium, high); firms will not pay enough (medium, high), each with the mitigation quoted, each graded for likelihood and impact | docs/helix/00-discover/business-case.md#risk-assessment |
| S10 | Paid product path if weekly reconciliation time falls below 3 minutes per client; recommended next steps with owners and dates: the investment committee approves the year-one budget today, a named partner recruits five pilot firms by month end, the product lead reports reconciliation time at the two-month checkpoint | docs/helix/00-discover/business-case.md#executive-summary, docs/helix/00-discover/business-case.md#recommendation |

## Assumptions and gaps

- **Assumption**: the committee approves year-one spend only; years two and three are informational. Inferred from the occasion (monthly investment review). The sponsor should confirm.
- **Gap**: the business case names no pilot recruiter; the ask has the committee name one instead of inventing an owner.
- **Gap**: the business case names no owner per risk, which the proposal flow's checklist asks for; the risk slide carries mitigations only, and the ask names the recruiter who reduces the export risk.
- **Gap**: no artifact holds the review date or presenter; both come from the meeting invite at render time.

## Render

- **Theme**: deliverables/theme.yml (no project design-system declared), editorial look
- **Targets**: docs/helix/06-iterate/deliverables/assets/DEL-001-depositmatch-pilot.pptx, docs/helix/06-iterate/deliverables/assets/DEL-001-depositmatch-pilot.pdf
- **Gate**: script checks pass (check-deliverable.py, 0 blocking); titles and shapes pass (title.slop, horizontal_logic, shape.slop, and restatement report nothing); horizontal logic pass; vertical logic pass; fidelity pass (every stat callout re-read against the business case); voice pass (prose lint with the Helix styles, 0 errors); visual: every slide rendered to an image and inspected on 2026-09-10, one overflow on slide 7 fixed by shortening the second bullet; file: presentation validator pass; flow checklist: pass except risk owners, which no source names (recorded under Assumptions and gaps); coverage: 7 groups, 5 covered, 2 omitted with reasons, every must-cover concept carried, no must-omit concepts
``````

</details>

## Reference

<table class="helix-reference-table">
<tbody>
<tr><th>Activity</th><td><a href="../../../reference/glossary/activities/"><strong>Iterate</strong></a> — Measure, align, and improve. Close the feedback loop back into the planning strand.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/06-iterate/deliverables/DEL-[nnn]-[slug].md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Deliverable Generation Prompt&#10;&#10;You are writing the script for a deck, brief, or one-pager that projects&#10;governed HELIX artifacts for people outside the project. Follow the&#10;`present` mode contract (`modes/present.md`; step detail in&#10;`actions/present.md`). This prompt covers what the script itself must&#10;contain. The three kinds share this prompt and template; §Writing a&#10;document applies only to `brief` and `one-pager`.&#10;&#10;Write the script in the register of the `human-facing` profile&#x27;s `sample`&#10;paragraph in `voice.yml`. Read it before you write a title. The guidance&#10;files you read while working are written in that register too; echo their&#10;sound, and do not echo their instructions into the reader&#x27;s page.&#10;&#10;## Before writing&#10;&#10;- Confirm the Brief fields: audience, occasion, decision sought, time slot or&#10;  page budget, kind, constraints, look, takeaway. At `low`/`medium` autonomy, ask&#10;  for missing fields in one message. At `high`, infer and record each&#10;  inference under Assumptions and gaps. No audience or no decision sought&#10;  means stop; there is nothing to present yet.&#10;- Declare the scope, breadth, angle, must-cover and must-omit concepts, and&#10;  max messages in the Brief. Then inventory the whole scope&#10;  (`scripts/corpus-inventory.py`, or the by-hand recipe in&#10;  `actions/present.md`) and cluster what recurs into concept groups,&#10;  typically five to nine and more when the corpus is wide, named in the&#10;  audience&#x27;s words and ranked by authority. Every group ends up in the&#10;  Story&#x27;s Concept coverage table as covered or omitted with a reason. Choose&#10;  breadth in the Brief; a mapping cannot choose it for you.&#10;- Read every source section you will project. Then find the source type&#x27;s&#10;  entry in `deliverable-mappings.yml` and read its `units` list top to&#10;  bottom. Each entry names a unit id, the source sections it draws from, its&#10;  pattern, a title hint, and the kinds it belongs to in `include_in`.&#10;  **Filter that list to the units whose `include_in` contains the kind you&#10;  are writing.** The filtered list, in the mapping&#x27;s order, is your draft&#10;  outline. A `deck` keeps every unit; a `brief` or `one-pager` keeps a&#10;  subset, and the gap between them is deliberate. Merge units when several&#10;  sources apply to one entry. Resolve each `gaps_to_ask` item for the source&#10;  type.&#10;- Choose the flow by occasion from `deliverables/deck-flows.yml` (the&#10;  reasoning is in `deliverables/deck-craft.md`), then read the chosen flow&#x27;s&#10;  own file under `deliverables/flows/`. `legacy_spines` maps a mapping&#x27;s&#10;  `default_spine` to the flow that replaced it. The flow sets beat order and&#10;  the headline register (recommendation, situation, cost, risks, ask) for&#10;  every kind; a document follows a flow the same way a deck does.&#10;&#10;## Storyboard (before any body text)&#10;&#10;This is the outline, and it is the same work for a deck, a brief, and a&#10;one-pager. &quot;Slide&quot; below means &quot;unit&quot;. The beat-to-title table is the&#10;document&#x27;s section list, in order, with its argument tested before any body&#10;prose exists.&#10;&#10;- Distill: write the takeaway sentence; then three to five messages that&#10;  make it true, ranked by how much each moves the audience&#x27;s decision; then&#10;  the evidence for each message as source sections and the one figure,&#10;  example, or comparison the unit will carry. A message without a source&#10;  section becomes a gap or a recorded assumption.&#10;- Map each unit from your filtered outline to the flow&#x27;s beats: which beat&#10;  it answers, which message it carries, one line on its exhibit. Several&#10;  units can serve one beat, and every unit needs a beat, because the beat&#10;  gives its title a job (situation, cost, risk, ask). Include optional beats&#10;  only when a message needs them. Drop a whole unit before compressing two&#10;  into one.&#10;- Title the document. In a claim-title flow the H1 is a claim in the&#10;  takeaway&#x27;s words (&quot;A three-month pilot wins back reviewer hours&quot;). In a&#10;  `heading_style: label` flow the H1 names the subject and the role&#10;  (&quot;PostgreSQL as DepositMatch&#x27;s system of record&quot;) and unit titles are the&#10;  flow&#x27;s `heading` labels. No count in a title in either style; the gate&#10;  blocks &quot;three of five&quot;.&#10;- Run the horizontal-logic test on claim titles (label headings skip it):&#10;  read the titles in order. Each answers the&#10;  question the previous title raised; the last content title is the ask in&#10;  the takeaway&#x27;s words; the titles alone give the argument. Rewrite until it&#10;  passes. When two adjacent titles share no word because the beats change&#10;  topic, record that under Story and leave the titles as they are; the&#10;  `horizontal_logic` gate finding is a warning for this reason.&#10;- Run the headline pass on the titles (the rule list is in&#10;  `actions/present.md` step 3) before any body is written. Then read the&#10;  set aloud once more. A title can pass every rule and still be one nobody&#10;  would say; rewrite it for the reader and rerun the rules. After any single&#10;  fix, reread the whole set.&#10;- Check every title and every `ask-next-steps` line against the&#10;  `human-facing` avoid list in `voice.yml`. The rules catch clichés and&#10;  labels; the list catches the bland title: a bureaucratic noun standing in&#10;  for a plain verb (&quot;before the decision closes&quot; for &quot;before deciding&quot;), an&#10;  empty precision-adjective on a plain noun (&quot;bounded tests&quot; for &quot;tests&quot;), a&#10;  generic command heading (&quot;Fund the initiative&quot; for what the money buys).&#10;  A mapping&#x27;s `title_hint` says what the unit proves; write the title&#10;  yourself.&#10;- Record flow, takeaway, messages with evidence, the beat-to-title table,&#10;  and the test result under Story.&#10;&#10;## Writing the script&#10;&#10;- One pattern per unit, from the beat&#x27;s allowed set in the flow file,&#10;  chosen by content shape from `slide-patterns.yml`. Stay inside the&#10;  pattern&#x27;s limits and the `density` block there; an overflowing unit&#10;  becomes two units.&#10;- Each body proves its title and nothing else. One number per beat; the&#10;  rest goes to notes. Callbacks use the earlier slide&#x27;s words.&#10;- Bodies are in the `human-facing` voice: plain words, one idea per bullet,&#10;  active verbs, concrete consequences, sentence variety. Say what a thing&#10;  is and does. Keep HELIX and engineering vocabulary out of bodies:&#10;  artifact IDs, activity names, work-item terms, acceptance-criterion codes,&#10;  and the source artifact&#x27;s own type name (&quot;component profile&quot;) belong in&#10;  Sources and the frontmatter. Define or drop any term the audience would&#10;  not use.&#10;- Say what the piece asks for once, in the ask unit. Sentences about what&#10;  the piece is doing, avoiding, or declining to recommend go nowhere on the&#10;  page.&#10;- End the ask on its last step. A closing line that restates the point as a&#10;  maxim is cut, whatever it says.&#10;- Visual lines open with a spec in the `visual-specs.md` grammar, then say&#10;  what the visual shows, its series or elements, and the source it is drawn&#10;  from: `**Visual**: kind: table | columns: Week / Median minutes | rows: 1 /&#10;  41; 8 / 12 | highlight: 2. Median reconciliation minutes per client, weeks&#10;  1 to 8, from the pilot metrics table`. &quot;Chart&quot; or &quot;diagram&quot; alone is a gate&#10;  failure; a line without a spec renders as a placeholder panel. Name the&#10;  rival, the product, or the team in a column header; a generic header&#10;  (&quot;Nearest rival&quot;) under a heading that names it reads as evasion.&#10;- Notes carry the supporting detail the slide omits, in the same voice, so a&#10;  reader of the script alone can present it.&#10;- Every number in a body appears in Sources with the governing artifact&#10;  path and section. Subset the source when the audience needs less. Keep a&#10;  sourced figure as the source states it.&#10;- Deck order: title, optional agenda (10 or more slides), content units in&#10;  the flow&#x27;s beat order, ask-next-steps, appendix-sources. A flow whose `ask`&#10;  beat is `required: false` (a reference such as candidate-briefing) ends on&#10;  its last content unit, then appendix-sources.&#10;- Every owner, date, duration, likelihood, or impact on the page comes from&#10;  a source section, or it goes under Assumptions and gaps with the reason.&#10;  The gate blocks an `owners:`, `dates:`, or risk-grade value it cannot find&#10;  in either place. When the record names no owner or date, the piece has no&#10;  ask.&#10;- A reference piece keeps the record&#x27;s shape: what the thing is, what the&#10;  record shows on each criterion the decision uses, what the record leaves&#10;  out, the named alternatives on the same criteria, what the record cannot&#10;  settle. Carry the record&#x27;s own status words (met, unknown, not published)&#10;  and add none.&#10;&#10;## Writing a document (one-pager or brief)&#10;&#10;Same script format, units, patterns, and Sources discipline as a deck, with&#10;three differences.&#10;&#10;- **The title unit&#x27;s Body is the introduction.** Write three to five&#10;  sentences, one per bullet; `render-doc.js` joins them into one paragraph.&#10;  For a reference (candidate-briefing), lift the source&#x27;s Need and Required&#10;  Capabilities: we need a [role] for [use cases] so that [goals]; it must&#10;  [capabilities]; we evaluated [candidate] against those and found [the&#10;  verdict in plain words]. For a persuasive document, open with the reader&#x27;s&#10;  situation and the stakes, then the finding. Write it the way the `sample`&#10;  paragraph in `voice.yml` reads.&#10;  The Brief&#x27;s `Audience` and `Decision or action sought` fields steer your&#10;  writing and do not appear on the page. A single bullet renders as a short&#10;  dek line, enough only when the reader already has the context.&#10;- **Pattern choice has a layout consequence for `one-pager`.** `table`,&#10;  `claim-evidence`, `stat-callout`, and a `claim-evidence` unit visualized&#10;  as `panels` or `icon-list` are single-column shapes and pack into the&#10;  page&#x27;s two-column grid. `two-column-comparison`, `risk-matrix`, and&#10;  `ask-next-steps` render full width below the grid, the ask always last.&#10;  Several single-column facts balance a page better than one wide comparison&#10;  alone.&#10;- **Kind controls the cut, and only the one-pager has a page budget.** A&#10;  `brief` carries the full argument and runs as many pages as the record&#10;  needs; a more detailed or more complex product needs more, and no page&#10;  count is fixed. A `one-pager` is the leave-behind cut on a single Letter&#10;  page, with `theme.yml`&#x27;s `max_words_one_pager` (450) as a warned budget. To&#10;  fit the one-pager, drop whole units (typically the evidence table and the&#10;  appendix) and keep the remaining bullets whole.&#10;- Render with `scripts/render-doc.js &lt;script.md&gt; &lt;out.html&gt; --kind&#10;  brief|one-pager [--pdf &lt;out.pdf&gt;]`; see `modes/present.md` §Kinds and&#10;  §Render toolchain.&#10;&#10;## After writing&#10;&#10;- Run the script checks (`scripts/check-deliverable.py`, or by hand) and&#10;  fix every blocking finding; then the shape pass over bullets, labels,&#10;  captions, and verdicts (`actions/present.md` step 5).&#10;- Re-run the horizontal-logic test on the finished titles, then the&#10;  vertical-logic test on every unit: the body proves the title and the title&#10;  is proven by the body. Rewrite the title to what the body proves, or cut&#10;  the unit.&#10;- Walk the flow&#x27;s `checklist` in its file under `deliverables/flows/`.&#10;- Check coverage: every must-cover concept is carried by a message, no&#10;  must-omit concept appears in a title or body, every inventory group has a&#10;  status, and a survey covers at least five groups.&#10;- Render (`.pptx` for a deck; HTML, and PDF when a host renders one, for a&#10;  document), then rasterize every produced slide or page to an image and&#10;  look at each one. Fix overflow, collisions, orphan bullets, poor contrast,&#10;  and missing visuals; re-render. Without a renderer or rasterizer, record&#10;  under Render which targets were not produced and why.&#10;- Fill the Render section with theme, targets, and the gate&#x27;s own output:&#10;  the blocking and warning counts and what each warning was. Leave&#10;  `status: draft`; a person approves the deliverable like any artifact.</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---&#10;ddx:&#10;  id: DEL-[nnn]&#10;  type: deliverable&#10;  activity: iterate&#10;  kind: [deck | one-pager | brief]&#10;  status: draft&#10;  authoring:&#10;    home: repo&#10;    export:&#10;      - [path to rendered .pptx, and .pdf when the host exports one]&#10;  links:&#10;    - id: [source artifact id]&#10;      kind: informed_by&#10;---&#10;&#10;# [Deck or document title: the takeaway as a claim]&#10;&#10;## Brief&#10;&#10;- **Audience**: [who decides or acts, by role; a name only when the name matters]&#10;- **Occasion**: [meeting, send-ahead, board pack, workshop]&#10;- **Decision or action sought**: [one sentence]&#10;- **Time slot or page budget**: [minutes or pages]&#10;- **Kind**: [deck | one-pager | brief]&#10;- **Constraints**: [brand, confidentiality, house rules]&#10;- **Look**: [editorial | technical | bold | classic; the theme&#x27;s font pairing, surfaces, and marker, chosen by room]&#10;- **Scope**: [paths or artifact ids the deliverable may draw on, for example docs/helix and workflows/README.md]&#10;- **Breadth**: [survey | deep-dive]&#10;- **Angle**: [the lens, or none]&#10;- **Must cover**: [concept; concept]&#10;- **Must omit**: [concept; concept, or none]&#10;- **Max messages**: [3 to 5]&#10;- **Takeaway**: [the one sentence the audience should leave with]&#10;&#10;## Story&#10;&#10;- **Flow**: [flow id from deck-flows.yml, chosen by occasion]&#10;- **Takeaway**: [the sentence every title builds to; same words as the Brief]&#10;- **Messages** (three to five claims that make the takeaway true, ranked by the audience&#x27;s decision; each with the source sections that prove it):&#10;  1. [message as a claim] (evidence: [path#section], [figure or example it supplies])&#10;  2. [message as a claim] (evidence: [path#section], [...])&#10;  3. [...]&#10;- **Beats and titles** (one row per beat in the flow; titles written before any body):&#10;&#10;  | # | Beat | Title (claim) | Message | Exhibit |&#10;  |---|---|---|---|---|&#10;  | 1 | [beat name] | [claim title] | [M1] | [one line: what will prove the title] |&#10;  | 2 | [beat name] | [claim title] | [M2] | [...] |&#10;  | [n] | ask | [the ask as a claim] | [takeaway] | [ask band, steps with owners and dates] |&#10;&#10;- **Concept coverage** (every concept group the inventory surfaced, in authority order; nothing is omitted silently):&#10;&#10;  | # | Concept group | Authority | Status | Carried by / reason |&#10;  |---|---|---|---|---|&#10;  | 1 | [group name in the audience&#x27;s words] | [vision, PRD, design, ...] | covered | [M1] |&#10;  | 2 | [group name] | [...] | omitted | [breadth, angle, audience, or budget: one line] |&#10;&#10;- **Horizontal-logic test**: [pass, or the titles rewritten to make it pass: each title answers the question the previous one raised; the titles alone give the argument and the ask]&#10;&#10;## Content&#10;&#10;### 1. [Claim title]&#10;&#10;**Pattern**: [pattern id from slide-patterns.yml]&#10;**Body**:&#10;- [evidence bullet within the pattern&#x27;s limits]&#10;- [evidence bullet]&#10;**Visual**: [kind: &lt;kind&gt; | &lt;field&gt;: &lt;value&gt; | &lt;field&gt;: &lt;value&gt;. what it shows, the series or elements, the source it is drawn from; grammar and kinds in deliverables/visual-specs.md]&#10;**Notes**: [speaker notes: the detail the slide omits, in the same voice]&#10;**Sources**: [S1, S2]&#10;&#10;### 2. [Claim title]&#10;&#10;**Pattern**: [pattern id]&#10;**Body**:&#10;- [...]&#10;**Visual**: [...]&#10;**Notes**: [...]&#10;**Sources**: [S3]&#10;&#10;### [n]. [The ask as a claim]&#10;&#10;**Pattern**: ask-next-steps&#10;**Body**:&#10;- [next step, owner, date]&#10;- [next step, owner, date]&#10;**Visual**: [ask band plus numbered steps with owner and date columns]&#10;**Notes**: [...]&#10;**Sources**: [S1]&#10;&#10;## Sources&#10;&#10;| Id | Claim or figure | Governing artifact and section |&#10;|---|---|---|&#10;| S1 | [claim or number as it appears in the body] | [path#section] |&#10;| S2 | [...] | [...] |&#10;&#10;## Assumptions and gaps&#10;&#10;- **Assumption**: [what was inferred, from what, and who should confirm it]&#10;- **Gap**: [content the deliverable needed that no artifact holds; how it was handled]&#10;&#10;## Render&#10;&#10;- **Theme**: [project design-system | deliverables/theme.yml]&#10;- **Targets**: [pptx path], [pdf path, or which target was not produced and why]&#10;- **Gate**: script checks [pass/fail with check ids]; titles and shapes [headline pass, horizontal_logic, shape pass, restatement]; horizontal logic [pass]; vertical logic [pass]; fidelity [pass]; voice [pass]; visual [every produced slide rendered to an image and inspected on &lt;date&gt;, or the missing tool]; file [validator result]; flow checklist [pass, or the item and its recorded gap]; coverage [groups covered / omitted, must-cover carried, must-omit absent]</code></pre></details></td></tr>
</tbody>
</table>
