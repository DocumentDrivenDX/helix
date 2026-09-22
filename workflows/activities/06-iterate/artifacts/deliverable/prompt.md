# Deliverable Generation Prompt

You are writing the script for a deck, brief, or one-pager that projects
governed HELIX artifacts for people outside the project. Follow the
`present` mode contract (`modes/present.md`; step detail in
`actions/present.md`). This prompt covers what the script itself must
contain. The three kinds share this prompt and template; §Writing a
document applies only to `brief` and `one-pager`.

Write the script in the register of the `human-facing` profile's `sample`
paragraph in `voice.yml`. Read it before you write a title. The guidance
files you read while working are written in that register too; echo their
sound, and do not echo their instructions into the reader's page.

## Before writing

- Confirm the Brief fields: audience, occasion, decision sought, time slot or
  page budget, kind, constraints, look, takeaway. At `low`/`medium` autonomy, ask
  for missing fields in one message. At `high`, infer and record each
  inference under Assumptions and gaps. No audience or no decision sought
  means stop; there is nothing to present yet.
- Declare the scope, breadth, angle, must-cover and must-omit concepts, and
  max messages in the Brief. Then inventory the whole scope
  (`scripts/corpus-inventory.py`, or the by-hand recipe in
  `actions/present.md`) and cluster what recurs into concept groups,
  typically five to nine and more when the corpus is wide, named in the
  audience's words and ranked by authority. Every group ends up in the
  Story's Concept coverage table as covered or omitted with a reason. Choose
  breadth in the Brief; a mapping cannot choose it for you.
- Read every source section you will project. Then find the source type's
  entry in `deliverable-mappings.yml` and read its `units` list top to
  bottom. Each entry names a unit id, the source sections it draws from, its
  pattern, a title hint, and the kinds it belongs to in `include_in`.
  **Filter that list to the units whose `include_in` contains the kind you
  are writing.** The filtered list, in the mapping's order, is your draft
  outline. A `deck` keeps every unit; a `brief` or `one-pager` keeps a
  subset, and the gap between them is deliberate. Merge units when several
  sources apply to one entry. Resolve each `gaps_to_ask` item for the source
  type.
- Choose the flow by occasion from `deliverables/deck-flows.yml` (the
  reasoning is in `deliverables/deck-craft.md`), then read the chosen flow's
  own file under `deliverables/flows/`. `legacy_spines` maps a mapping's
  `default_spine` to the flow that replaced it. The flow sets beat order and
  the headline register (recommendation, situation, cost, risks, ask) for
  every kind; a document follows a flow the same way a deck does.

## Storyboard (before any body text)

This is the outline, and it is the same work for a deck, a brief, and a
one-pager. "Slide" below means "unit". The beat-to-title table is the
document's section list, in order, with its argument tested before any body
prose exists.

- Distill: write the takeaway sentence; then three to five messages that
  make it true, ranked by how much each moves the audience's decision; then
  the evidence for each message as source sections and the one figure,
  example, or comparison the unit will carry. A message without a source
  section becomes a gap or a recorded assumption.
- Map each unit from your filtered outline to the flow's beats: which beat
  it answers, which message it carries, one line on its exhibit. Several
  units can serve one beat, and every unit needs a beat, because the beat
  gives its title a job (situation, cost, risk, ask). Include optional beats
  only when a message needs them. Drop a whole unit before compressing two
  into one.
- Title the document. In a claim-title flow the H1 is a claim in the
  takeaway's words ("A three-month pilot wins back reviewer hours"). In a
  `heading_style: label` flow the H1 names the subject and the role
  ("PostgreSQL as DepositMatch's system of record") and unit titles are the
  flow's `heading` labels. No count in a title in either style; the gate
  blocks "three of five".
- Run the horizontal-logic test on claim titles (label headings skip it):
  read the titles in order. Each answers the
  question the previous title raised; the last content title is the ask in
  the takeaway's words; the titles alone give the argument. Rewrite until it
  passes. When two adjacent titles share no word because the beats change
  topic, record that under Story and leave the titles as they are; the
  `horizontal_logic` gate finding is a warning for this reason.
- Run the headline pass on the titles (the rule list is in
  `actions/present.md` step 3) before any body is written. Then read the
  set aloud once more. A title can pass every rule and still be one nobody
  would say; rewrite it for the reader and rerun the rules. After any single
  fix, reread the whole set.
- Check every title and every `ask-next-steps` line against the
  `human-facing` avoid list in `voice.yml`. The rules catch clichés and
  labels; the list catches the bland title: a bureaucratic noun standing in
  for a plain verb ("before the decision closes" for "before deciding"), an
  empty precision-adjective on a plain noun ("bounded tests" for "tests"), a
  generic command heading ("Fund the initiative" for what the money buys).
  A mapping's `title_hint` says what the unit proves; write the title
  yourself.
- Record flow, takeaway, messages with evidence, the beat-to-title table,
  and the test result under Story.

## Writing the script

- One pattern per unit, from the beat's allowed set in the flow file,
  chosen by content shape from `slide-patterns.yml`. Stay inside the
  pattern's limits and the `density` block there; an overflowing unit
  becomes two units.
- Each body proves its title and nothing else. One number per beat; the
  rest goes to notes. Callbacks use the earlier slide's words.
- Bodies are in the `human-facing` voice: plain words, one idea per bullet,
  active verbs, concrete consequences, sentence variety. Say what a thing
  is and does. Keep HELIX and engineering vocabulary out of bodies:
  artifact IDs, activity names, work-item terms, acceptance-criterion codes,
  and the source artifact's own type name ("component profile") belong in
  Sources and the frontmatter. Define or drop any term the audience would
  not use.
- Say what the piece asks for once, in the ask unit. Sentences about what
  the piece is doing, avoiding, or declining to recommend go nowhere on the
  page.
- End the ask on its last step. A closing line that restates the point as a
  maxim is cut, whatever it says.
- Visual lines open with a spec in the `visual-specs.md` grammar, then say
  what the visual shows, its series or elements, and the source it is drawn
  from: `**Visual**: kind: table | columns: Week / Median minutes | rows: 1 /
  41; 8 / 12 | highlight: 2. Median reconciliation minutes per client, weeks
  1 to 8, from the pilot metrics table`. "Chart" or "diagram" alone is a gate
  failure; a line without a spec renders as a placeholder panel. Name the
  rival, the product, or the team in a column header; a generic header
  ("Nearest rival") under a heading that names it reads as evasion.
- Notes carry the supporting detail the slide omits, in the same voice, so a
  reader of the script alone can present it.
- Every number in a body appears in Sources with the governing artifact
  path and section. Subset the source when the audience needs less. Keep a
  sourced figure as the source states it.
- Deck order: title, optional agenda (10 or more slides), content units in
  the flow's beat order, ask-next-steps, appendix-sources. A flow whose `ask`
  beat is `required: false` (a reference such as candidate-briefing) ends on
  its last content unit, then appendix-sources.
- Every owner, date, duration, likelihood, or impact on the page comes from
  a source section, or it goes under Assumptions and gaps with the reason.
  The gate blocks an `owners:`, `dates:`, or risk-grade value it cannot find
  in either place. When the record names no owner or date, the piece has no
  ask.
- A reference piece keeps the record's shape: what the thing is, what the
  record shows on each criterion the decision uses, what the record leaves
  out, the named alternatives on the same criteria, what the record cannot
  settle. Carry the record's own status words (met, unknown, not published)
  and add none.

## Writing a document (one-pager or brief)

Same script format, units, patterns, and Sources discipline as a deck, with
three differences.

- **The title unit's Body is the introduction.** Write three to five
  sentences, one per bullet; `render-doc.js` joins them into one paragraph.
  For a reference (candidate-briefing), lift the source's Need and Required
  Capabilities: we need a [role] for [use cases] so that [goals]; it must
  [capabilities]; we evaluated [candidate] against those and found [the
  verdict in plain words]. For a persuasive document, open with the reader's
  situation and the stakes, then the finding. Write it the way the `sample`
  paragraph in `voice.yml` reads.
  The Brief's `Audience` and `Decision or action sought` fields steer your
  writing and do not appear on the page. A single bullet renders as a short
  dek line, enough only when the reader already has the context.
- **Pattern choice has a layout consequence for `one-pager`.** `table`,
  `claim-evidence`, `stat-callout`, and a `claim-evidence` unit visualized
  as `panels` or `icon-list` are single-column shapes and pack into the
  page's two-column grid. `two-column-comparison`, `risk-matrix`, and
  `ask-next-steps` render full width below the grid, the ask always last.
  Several single-column facts balance a page better than one wide comparison
  alone.
- **Kind controls the cut, and only the one-pager has a page budget.** A
  `brief` carries the full argument and runs as many pages as the record
  needs; a more detailed or more complex product needs more, and no page
  count is fixed. A `one-pager` is the leave-behind cut on a single Letter
  page, with `theme.yml`'s `max_words_one_pager` (450) as a warned budget. To
  fit the one-pager, drop whole units (typically the evidence table and the
  appendix) and keep the remaining bullets whole.
- Render with `scripts/render-doc.js <script.md> <out.html> --kind
  brief|one-pager [--pdf <out.pdf>]`; see `modes/present.md` §Kinds and
  §Render toolchain.

## After writing

- Run the script checks (`scripts/check-deliverable.py`, or by hand) and
  fix every blocking finding; then the shape pass over bullets, labels,
  captions, and verdicts (`actions/present.md` step 5).
- Re-run the horizontal-logic test on the finished titles, then the
  vertical-logic test on every unit: the body proves the title and the title
  is proven by the body. Rewrite the title to what the body proves, or cut
  the unit.
- Walk the flow's `checklist` in its file under `deliverables/flows/`.
- Check coverage: every must-cover concept is carried by a message, no
  must-omit concept appears in a title or body, every inventory group has a
  status, and a survey covers at least five groups.
- Render (`.pptx` for a deck; HTML, and PDF when a host renders one, for a
  document), then rasterize every produced slide or page to an image and
  look at each one. Fix overflow, collisions, orphan bullets, poor contrast,
  and missing visuals; re-render. Without a renderer or rasterizer, record
  under Render which targets were not produced and why.
- Fill the Render section with theme, targets, and the gate's own output:
  the blocking and warning counts and what each warning was. Leave
  `status: draft`; a person approves the deliverable like any artifact.
