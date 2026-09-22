# HELIX Action: Present

You are turning governed artifacts into a deck for people outside the
project. The contract is `workflows/modes/present.md`; this file is the step
detail. Scripts under `scripts/` beside the skill are optional: every step
names what to do by hand on a host without them.

## Action input

- a source scope (paths or artifact ids), or none (the flow root plus the
  methodology documents that define the product)
- the Brief fields, or as many as the request supplies

## STEP 1: Intake

Resolve, in this order: audience (who decides or acts), occasion (meeting,
send-ahead, board pack), the decision or action sought, time slot, kind
(`deck`, `one-pager`, or `brief`; `memo` resolves to `brief`; a mapping's
`default_kind` is the starting point), look, and constraints (brand, confidentiality, must-include,
must-omit). Pick the look by room and record it in the Brief: `editorial`
(serif display, dark ends, light content) for evaluation calls and board
packs, `technical` (one sans family, light throughout, square markers) for
engineering audiences, `bold` (dark throughout, the secondary hue leads) for
pitches and keynotes, `classic` (serif display, no marker shape) for
proposals and printed briefs. At `low` and `medium` autonomy ask for anything
missing in one message; at `high` infer from the artifacts and record each
inference under `## Assumptions and gaps`. A deliverable with no named
audience and no decision sought is not authored; that is a framing gap, and a
default.

## STEP 2: Scope and inventory

Breadth is a declared choice in the Brief, whatever sections a mapping
names. Resolve and record in the Brief: `scope`, `breadth` (`survey`, cover
the whole scope; or `deep-dive`, one capability or problem), `angle` (the
lens, when there is one), `must_cover` and `must_omit` (concept lists), and
`max_messages`.

Inventory the scope before choosing anything (`scripts/corpus-inventory.py
<scope>` when the host has scripts). Three passes, because a phrase count
alone misses two kinds of concept:

- Concepts: recurring phrases weighted by authority and spread, plus every
  heading of the top-ranked documents as an authority floor.
- Structure: the corpus's own shape read from the catalog (the authority
  chain, cross-layer propagation, gates and floors, what runs unasked),
  emitted as groups whatever the prose says. By hand: read the graph's ranks
  and edges (`workflows/graph.yml`), then each activity's gates in its
  `README.md`, then the concerns index; each layer, gate, and concern family
  is a candidate group.
- Roles and hand-offs: who approves, confirms, reviews, decides, stops,
  infers, records, so a theme carried by scattered role vocabulary still
  surfaces. By hand: grep the scope for actor nouns (operator, agent,
  reviewer, sponsor, runtime) and hand-off verbs (approve, confirm, review,
  decide, stop, infer, record) and cluster the hits by who does what to whom.

Cluster all of that into concept groups, typically five to nine and more
when the corpus is wide; name each group in the audience's words; rank the
groups by authority (what the vision and PRD say the product is) before
ranking by the decision. Structural groups, the roles group, and
authority-floor headings may be folded into a group and are otherwise
kept. Record the groups under `## Story` as a Concept coverage table:
every group is `covered` (with the message that carries it) or `omitted`
(with the reason: breadth, angle, audience, or budget). A survey covers every
group the authority rank puts in the top five; a deep-dive names the groups
it leaves out. `deliverable-mappings.yml` supplies section-to-unit shapes for
the artifact types it knows, as a floor to build on. Read every source
section you project. Content the deliverable needs that no artifact holds
(`gaps_to_ask`) becomes a question or a recorded assumption instead of an
invented fact.

## STEP 3: Storyboard

Choose the flow by occasion from the `deck-flows.yml` index
(`investor-pitch`, `evaluation-briefing`, `executive-status`, `proposal`,
`product-walkthrough`, `board-update`, `internal-alignment`,
`candidate-briefing`), then read that one flow's beats, transitions, and
checklist from its own file under `deliverables/flows/`; a `default_spine`
in `deliverable-mappings.yml` resolves through the index's `legacy_spines`
map, or a mapping may name a flow id directly. Then, before any body text:

- Distill. Write the one-sentence takeaway the audience should leave with;
  the three to five messages (up to `max_messages`) that make it true, drawn
  from the covered concept groups and ranked by how much each moves the
  audience's decision; and an evidence table with one row per message naming
  the source sections and the figure, example, or comparison each supplies.
  A message with no source section is a gap to ask about or an assumption to
  record. A concept group no message carries is `omitted` in
  the coverage table, with a reason; silent omission is the failure this step
  exists to prevent.
- Title every beat. One title per beat in the flow, each mapped to a
  message, with a one-line note of the exhibit that will prove it. In a flow
  with `heading_style: label` the title is the beat's `heading` (a plain
  section label) and the finding goes in the first sentence of the body;
  otherwise the title is a claim. Optional
  beats enter only when a message needs them; required beats no source can
  fill become a question or a recorded assumption. Cut beats in the flow's
  `keep_when_short` order when the slot is tight; keep one beat per slide
  into one slide.
- Horizontal-logic test (claim titles only; label headings skip it). Read
  the titles in order. Each title answers the
  question the previous title raised and sets up the next; the last content
  title is the ask in the takeaway's words; a reader of the titles alone can
  state the argument and the decision. Rewrite titles until it passes.
- Headline pass. Detect with a prose tool that has a headline target, when
  the host has one, or with the `title.slop` and `horizontal_logic` checks in
  `scripts/check-deliverable.py`, or by hand against the rule list: name
  each offending title by rule (contrastive reversal, colon list, imperative
  chain, listicle, stacked negation, forced triplet, flattery, aphorism,
  universal claim, mannered phrase, inventory count, hedge, over-length).
  Rewrite: each title is one sentence with a subject, a verb, and one
  concrete noun, inside `title_words_target` and `title_words_max` in
  `slide-patterns.yml` (one line at title size); it carries the unit's number
  when that number is an outcome the source states, and leaves catalog sizes
  (how many templates, modes, hosts) to the body; no filler adverb; it says
  what something does. Read the titles aloud in
  order so each connects to its neighbor. Re-run until clean. A body written
  under a slop title inherits its shape, so titles are fixed first.

Record the flow, takeaway, messages with evidence, the beat-to-title table,
and the test result under `## Story`. Only then write bodies.

## STEP 4: Pattern selection

Give each unit one pattern from the beat's allowed set in the chosen flow's
file, chosen by content shape from `slide-patterns.yml`, honoring that file's
limits and `density` block and the time budget (`slides_per_minute_of_talk`
with `default_length_budget` in `deck-flows.yml`; the flow's
`keep_when_short` order when the slot is tight). A unit that overflows its
pattern's limits becomes two units. Vary the page: a run of
claim-evidence slides alternates the visual's side; a relationship (a stack,
a loop, a hub) is a `diagram`; a pivot in the argument may
be a `statement`; icons name parts (a layer, a spoke, a column, a step); the
only decorative icon is the hero marker on the end slides, one icon for the
deck's subject.

## STEP 5: Write the script

Use the `deliverable` template with the `human-facing` voice: claim titles,
bodies inside the pattern limits, a visual specification per unit in the
`visual-specs.md` grammar (`kind: <kind> | <field>: <value>. <what it shows,
its series, and its source>`; "chart" alone fails the gate), speaker notes carrying the
detail the slide omits, and a Sources appendix mapping every figure and claim
to a governing artifact section. Each body proves its title and nothing
else; one number per beat, the rest in notes; callbacks use the earlier
slide's words. Subset the sources when the audience needs less, and keep
every sentence consistent with them. No HELIX vocabulary in bodies: artifact IDs, activity
names, work-item terms, and acceptance-criterion codes live only in the
Sources appendix and the frontmatter.

Then the shape pass, with the same prose tool's slide target when the host
has one (over the script, or over the rendered `.pptx`, whose text it reads
shape by shape), else the `shape.slop` and `restatement` checks in
`scripts/check-deliverable.py`, else by hand: a bullet, card label, caption,
or verdict may not be a category label, a self-justifying section, an
all-caps label, an invented status, a marketing adjective, a closer (a
reversal or an aphorism), or a second sentence that explains the first; and
no two shapes on one slide may say the same thing, which is how bullets that
restate the visual are caught. Sync the titles-only list under `## Story`
with the unit headings.

## STEP 6: Theme

Resolve palette and typography from the project's `design-system` artifact
when it declares them, else `theme.yml`, and apply the Brief's look. One hue
dominates; the secondary supports; the accent is rare. Charts follow the
theme's categorical order and the host's data-visualization rules when
available.

## STEP 7: Render

Targets: a slide file (`.pptx`) from the script (`scripts/render-deck.js`
when the host has node and the slide library it needs; else the host's
presentation tooling), plus a PDF whenever the host can export one. Record
each rendered path in `authoring.export` (several paths are allowed) and
under `## Render`. Without a renderer, or a rasterizer for the visual check,
the script is still produced: record under `## Render` which targets were
not produced and why, name the host that can render it, and run the gate on
the produced set.

## STEP 8: Pre-flight gate

The deliverable is not done until every check passes; a failure loops back
to step 3, 5, or 7:

- Script checks (`scripts/check-deliverable.py <script>`, or by hand): every
  unit has a claim title, a pattern, a visual, notes, and sources; no
  placeholder text; no HELIX vocabulary in bodies; word and bullet limits per
  pattern; density rules; every number in a body appears in Sources.
- Titles and shapes: the headline pass is clean, no consecutive titles fail
  horizontal logic, every shape passes the shape pass, no slide carries a
  restatement.
- Horizontal logic: re-run the titles-only read on the finished script; the
  titles still form the argument and end in the ask. A failure goes back to
  step 3.
- Vertical logic: every body proves its title with the evidence on the
  slide, and every title is proven by its body. A title the body cannot
  prove is rewritten to what the body proves, or the unit is cut.
- Fidelity: each claim in the script traces to the cited source section and
  does not contradict it. Re-read the source for every stat callout.
- Voice: the `human-facing` profile, checked with the host's prose lint when
  available and by a read-aloud pass.
- Visual: render every produced slide to an image (`scripts/deck-qa.py`
  when the host has a slide-to-PDF converter and a PDF rasterizer; else the
  presentation tooling's export) and look at each one for overflow,
  collisions, orphan bullets, unreadable contrast, or a missing visual. Fix
  and re-render. A deck nobody looked at is not finished. On a script-only
  run this check and the file check warn, naming the missing tool, and the
  Render section says so.
- File: the produced `.pptx` opens and validates with the host's checker.
- Flow checklist: every item in the chosen flow's `checklist`, in its own
  file under `deliverables/flows/`, holds.
- Coverage: every concept group in the inventory is marked covered or
  omitted with a reason; every `must_cover` concept is covered by a message;
  no `must_omit` concept appears in a title or body; a `survey` covers at
  least five groups. The script checks read the Brief and the coverage table
  and fail on any of these.

## STEP 9: Hand-off

Save the script under the flow root (default
`06-iterate/deliverables/DEL-<nnn>-<slug>.md`) with `ddx.links` to every
source artifact and `authoring.export` pointing at the renders. Report: the
takeaway sentence, the titles-only outline, assumptions and gaps, gate
results, and where the files are. Do not present the deck as approved; it is
`draft` until a person reviews it like any artifact.
