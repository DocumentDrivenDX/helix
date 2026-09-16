# Deliverable Generation Prompt

You are writing the script for a deck that projects governed HELIX
artifacts for people outside the project. Follow the `present` mode contract
(`modes/present.md`; step detail in `actions/present.md`); this prompt
covers what the script itself must contain. `one-pager` and `brief` are
planned kinds, not yet authored.

## Before writing

- Confirm the Brief fields: audience, occasion, decision sought, time slot or
  page budget, kind, constraints, look, takeaway. At `low`/`medium` autonomy, ask
  for missing fields in one message. At `high`, infer and record each
  inference under Assumptions and gaps. No audience or no decision sought
  means stop; there is nothing to present yet.
- Declare the scope, breadth, angle, must-cover and must-omit concepts, and
  max messages in the Brief; then inventory the whole scope
  (`scripts/corpus-inventory.py`, or the by-hand recipe in
  `actions/present.md`) and cluster what recurs into concept groups,
  typically five to nine and more when the corpus is wide, named in the
  audience's words and ranked by authority. Every
  group ends up in the Story's Concept coverage table as covered or omitted
  with a reason. Breadth is chosen, never inherited from a mapping.
- Read every source section you will project. Use `deliverable-mappings.yml`
  for the source type; merge units when several sources apply. Note
  `gaps_to_ask` for the source type and resolve each one.
- Choose the flow by occasion from `deliverables/deck-flows.yml`; the
  reasoning is in `deliverables/deck-craft.md`.

## Storyboard (before any body text)

- Distill: write the takeaway sentence; then three to five messages that
  make it true, ranked by how much each moves the audience's decision; then
  the evidence for each message as source sections and the one figure,
  example, or comparison the slide will carry. A message without a source
  section is a gap or an assumption, not a slide.
- Title every beat in the flow with a claim, mapped to a message, with a
  one-line note of the exhibit. Include optional beats only when a message
  needs them. Cut beats in the flow's `keep_when_short` order when the slot
  is tight; never compress two beats into one slide.
- Run the horizontal-logic test: read the titles in order. Each answers the
  question the previous title raised; the last content title is the ask in
  the takeaway's words; the titles alone give the argument. Rewrite until
  it passes.
- Run the headline pass on the titles (the rule list is in
  `actions/present.md` step 3) before any body is written.
- Record flow, takeaway, messages with evidence, the beat-to-title table,
  and the test result under Story.

## Writing the script

- One pattern per unit, from the beat's allowed set in `deck-flows.yml`,
  chosen by content shape from `slide-patterns.yml`. Stay inside the
  pattern's limits and the `density` block there; an overflowing unit
  becomes two units.
- Each body proves its title and nothing else. One number per beat; the
  rest goes to notes. Callbacks use the earlier slide's words.
- Bodies are in the `human-facing` voice: plain words, one idea per bullet,
  active verbs, concrete consequences, sentence variety. No HELIX or
  engineering vocabulary in bodies: artifact IDs, activity names, work-item
  terms, and acceptance-criterion codes belong only in Sources and the
  frontmatter. Define or drop any term the audience would not use.
- Visual lines open with a spec in the `visual-specs.md` grammar, then say
  what the visual shows, its series or elements, and the source it is drawn
  from: `**Visual**: kind: table | columns: Week / Median minutes | rows: 1 /
  41; 8 / 12 | highlight: 2. Median reconciliation minutes per client, weeks
  1 to 8, from the pilot metrics table`. "Chart" or "diagram" alone is a gate
  failure; a line without a spec renders as a placeholder panel.
- Notes carry the supporting detail the slide omits, in the same voice, so a
  reader of the script alone can present it.
- Every number in a body appears in Sources with the governing artifact
  path and section. Subset the source when the audience needs less; never
  contradict it, and never round a sourced figure into a different claim.
- Deck order: title, optional agenda (10 or more slides), content units in
  the flow's beat order, ask-next-steps, appendix-sources.

## After writing

- Run the script checks (`scripts/check-deliverable.py`, or by hand) and
  fix every blocking finding; then the shape pass over bullets, labels,
  captions, and verdicts (`actions/present.md` step 5).
- Re-run the horizontal-logic test on the finished titles, then the
  vertical-logic test on every unit: the body proves the title and the title
  is proven by the body. Rewrite the title to what the body proves, or cut
  the unit.
- Walk the flow's `checklist` in `deck-flows.yml`.
- Check coverage: every must-cover concept is carried by a message, no
  must-omit concept appears in a title or body, every inventory group has a
  status, and a survey covers at least five groups.
- Render to `.pptx` (and PDF when the host exports one), then render every
  produced slide to an image and look at each one. Fix overflow, collisions,
  orphan bullets, poor contrast, and missing visuals; re-render. Without a
  renderer or rasterizer, record under Render which targets were not
  produced and why.
- Fill the Render section with theme, targets, and gate results. Leave
  `status: draft`; a person approves the deliverable like any artifact.
