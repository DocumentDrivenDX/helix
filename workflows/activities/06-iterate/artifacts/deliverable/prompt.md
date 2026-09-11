# Deliverable Generation Prompt

You are writing the script for a deck, one-pager, or brief that projects
governed HELIX artifacts for people outside the project. Follow the `present`
mode contract (`modes/present.md`); this prompt covers what the script itself
must contain.

## Before writing

- Confirm the Brief fields: audience, occasion, decision sought, time slot or
  page budget, kind, constraints, takeaway. At `low`/`medium` autonomy, ask
  for missing fields in one message. At `high`, infer and record each
  inference under Assumptions and gaps. No audience or no decision sought
  means stop; there is nothing to present yet.
- Read every source section you will project. Use `deliverable-mappings.yml`
  for the source type; merge units when several sources apply. Note
  `gaps_to_ask` for the source type and resolve each one.
- Pick the story spine by occasion and write the takeaway sentence first.

## Writing the script

- Titles are claims that build to the takeaway. Test: read only the titles;
  if they do not tell the story, rewrite them before writing bodies.
- One pattern per unit, chosen by content shape from `slide-patterns.yml`.
  Stay inside the pattern's limits; an overflowing unit becomes two units.
  Keep the density rules: no three consecutive units of one pattern, at
  most one stat callout per section, a visual on every content unit.
- Bodies are in the `human-facing` voice: plain words, one idea per bullet,
  active verbs, concrete consequences, sentence variety. No HELIX or
  engineering vocabulary in bodies: artifact IDs, activity names, work-item
  terms, and acceptance-criterion codes belong only in Sources and the
  frontmatter. Define or drop any term the audience would not use.
- Visual lines say what the visual shows, its series or elements, and the
  source it is drawn from ("bar chart of median reconciliation minutes per
  client, weeks 1 to 8, from the pilot metrics table"). "Chart" or "diagram"
  alone is a gate failure.
- Notes carry the supporting detail the slide omits, in the same voice, so a
  reader of the script alone can present it.
- Every number in a body appears in Sources with the governing artifact
  path and section. Subset the source when the audience needs less; never
  contradict it, and never round a sourced figure into a different claim.
- Deck order: title, optional agenda (10 or more slides), content units,
  ask-next-steps, appendix-sources. One-pager and brief: takeaway, sections,
  ask, sources footer.

## After writing

- Run the script checks (`scripts/check-deliverable.py`) and fix every
  blocking finding.
- Render to the targets, then render every slide or page to an image and
  look at each one. Fix overflow, collisions, orphan bullets, poor contrast,
  and missing visuals; re-render.
- Fill the Render section with theme, targets, and gate results. Leave
  `status: draft`; a person approves the deliverable like any artifact.
