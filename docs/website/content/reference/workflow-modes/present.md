---
title: "Present"
slug: present
weight: 160
generated: true
---

Generated from [`workflows/modes/present.md`](https://github.com/DocumentDrivenDX/helix/blob/main/workflows/modes/present.md), the mode contract the HELIX skill loads. Edit that file, not this page.

Use to turn governed artifacts into something a person outside the project
can read or watch: a deck, a one-pager, or a brief, worth showing a client,
sponsor, or executive on the first try. The output is a `deliverable`
artifact (a governed Markdown script) plus rendered files. The script is the
document of record; renders are fidelity evidence.

Engage on: deck, slides, pitch, board or exec update, one-pager, brief, memo,
client-ready or customer-facing document, "make this presentable".

Reference data (resolved via §Catalog Resolution, `deliverables/` in the
bound catalog): `theme.yml` (palette, typography, layout limits),
`slide-patterns.yml` (pattern catalog, density rules), `deck-flows.yml`
(ordered beats, budgets, and transition rules per occasion),
`deck-craft.md` (the reasoning behind the flows and the storyboard tests),
and `deliverable-mappings.yml` (which sections of which source types feed
which units). Voice: the `human-facing` profile in `voice.yml`.

## Contract

1. **Intake.** Resolve, in this order: audience (who decides or acts),
   occasion (meeting, send-ahead, board pack), the decision or action sought,
   time slot or page budget, kind (`deck` | `one-pager` | `brief`), and
   constraints (brand, confidentiality, must-include, must-omit). At `low`
   and `medium` autonomy ask for anything missing in one message; at `high`
   infer from the artifacts and record each inference under `## Assumptions
   and gaps`. A deliverable with no named audience and no decision sought is
   not authored; that is a framing gap, not a default.
2. **Scope and inventory.** Breadth is a declared choice, never an
   accident of which sections a mapping names. Resolve and record in the
   Brief: `scope` (the paths or artifact ids the deliverable may draw on;
   default the flow root plus the methodology documents that define the
   product), `breadth` (`survey`, cover the whole scope; or `deep-dive`,
   one capability or problem), `angle` (the lens, when there is one),
   `must_cover` and `must_omit` (concept lists), and `max_messages`. Then
   inventory the scope before choosing anything: run
   `scripts/corpus-inventory.py <scope>` (beside this skill; by hand on
   hosts without scripts) to list every document by authority with its
   section claims and the concepts that recur across documents. Cluster
   the concepts into five to nine groups, name each group in the audience's
   words, and rank the groups by authority (what the vision and PRD say the
   product is) before ranking by the decision. Record the groups under
   `## Story` as a Concept coverage table: every group is marked `covered`
   (with the message that carries it) or `omitted` (with the reason:
   breadth, angle, audience, or budget). A survey covers every group the
   authority rank puts in the top five; a deep-dive names the groups it
   leaves out. `deliverable-mappings.yml` still supplies section-to-unit
   shapes for the artifact types it knows, as a floor, not a ceiling.
   Read every source section you project. Content the deliverable needs
   that no artifact holds (`gaps_to_ask`) becomes a question or a recorded
   assumption, never an invented fact.
3. **Storyboard.** Choose the flow by occasion from `deck-flows.yml`
   (`investor-pitch`, `evaluation-briefing`, `executive-status`, `proposal`,
   `product-walkthrough`, `board-update`, `internal-alignment`); a
   `default_spine` in `deliverable-mappings.yml` resolves through the file's
   `legacy_spines` map. Then, before any body text:
   - Distill. Write the one-sentence takeaway the audience should leave
     with; the three to five messages (up to `max_messages`) that make it
     true, drawn from the covered concept groups and ranked by how much
     each moves the audience's decision; and an evidence table with one row
     per message naming the source sections and the figure, example, or
     comparison each supplies. A message with no source section is a gap to
     ask about or an assumption to record, not a message. A concept group
     no message carries is `omitted` in the coverage table, with a reason;
     silent omission is the failure this step exists to prevent.
   - Title every beat. One claim title per beat in the flow, each mapped to
     a message, with a one-line note of the exhibit that will prove it.
     Optional beats enter only when a message needs them; required beats no
     source can fill become a question or a recorded assumption.
   - Horizontal-logic test. Read the titles in order. Each title answers the
     question the previous title raised and sets up the next; the last
     content title is the ask in the takeaway's words; a reader of the
     titles alone can state the argument and the decision. Rewrite titles
     until it passes. Only then write bodies.
   Record the flow, takeaway, messages with evidence, and the beat-to-title
   table under `## Story`.
4. **Pattern selection.** Give each unit one pattern from the beat's allowed
   set in `deck-flows.yml`, chosen by content shape from
   `slide-patterns.yml`, honoring the density rules (no three consecutive
   units of one pattern, at most one stat callout per section, a visual on
   every content slide) and the time budget (`slides_per_minute_of_talk`,
   with the flow's `keep_when_short` order when the slot is tight). A unit
   that overflows its pattern's limits is two units, not a denser slide.
5. **Write the script** in the `deliverable` template with the
   `human-facing` voice: claim titles, bodies inside the pattern limits, a
   visual specification per unit (what the chart or diagram shows, its
   series and source, not just "chart"), speaker notes carrying the detail
   the slide omits, and a Sources appendix mapping every figure and claim to
   a governing artifact section. Each body proves its title and nothing
   else; one number per beat, the rest in notes. Subset the sources when
   the audience needs less; never contradict them. No HELIX vocabulary in
   bodies: artifact IDs, activity names, work-item terms, and
   acceptance-criterion codes live only in the Sources appendix and the
   frontmatter.
   Then run the titles through the headline pass before touching bodies
   again. Detect: a prose tool with a headline target (Sloptimizer's
   `slop-audit.sh --target headline`) or, on hosts without one, the
   `title.slop` and `horizontal_logic` checks in `scripts/check-deliverable.py`
   name each offending title by rule: contrastive reversal, colon list,
   imperative chain, listicle, stacked negation, forced triplet, flattery,
   aphorism, universal claim, over-length. Rewrite: each title is one
   sentence with a subject, a verb, and one concrete noun, under 10 words
   where possible, carrying the unit's number when the source states one,
   saying what something does rather than what it is not; read the titles
   aloud in order so each connects to its neighbor. Validate: re-run the pass
   until it is clean and sync the titles-only list under `## Story` with the
   unit headings. A body written under a slop title inherits its shape, so
   titles are fixed first.
6. **Theme.** Resolve palette and typography from the project's
   `design-system` artifact when it declares them, else `theme.yml`. One hue
   dominates; the secondary supports; the accent is rare. Charts follow the
   theme's categorical order and the host's data-visualization rules when
   available.
7. **Render.** Targets are equal: a slide file (`.pptx`) through the host's
   presentation tooling and a self-contained HTML page for the browser, each
   from the same script, plus a PDF whenever the host can export one. A
   one-pager or brief renders to a document (`.docx` or HTML) and PDF. Record
   each rendered path in `authoring.export` (several paths are allowed) and
   under `## Render`. On a host with no rendering tooling, stop after the
   script and say which host can render it.
8. **Pre-flight gate.** The deliverable is not done until every check
   passes; a failure loops back to step 3, 5, or 7, never to "good enough":
   - Script checks (`scripts/check-deliverable.py <script>` beside this
     skill, or by hand on hosts without scripts): every unit has a claim
     title, a pattern, a visual, notes, and sources; no placeholder text; no
     HELIX vocabulary in bodies; word and bullet limits per pattern; density
     rules; every number in a body appears in Sources.
   - Titles: the headline pass is clean (`title.slop` reports nothing) and
     no consecutive titles fail `horizontal_logic`.
   - Horizontal logic: re-run the titles-only read on the finished script;
     the titles still form the argument and end in the ask. A failure goes
     back to step 3.
   - Vertical logic: every body proves its title with the evidence on the
     slide, and every title is proven by its body. A title the body cannot
     prove is rewritten to what the body proves, or the unit is cut.
   - Fidelity: each claim in the script traces to the cited source section
     and does not contradict it. Re-read the source for every stat callout.
   - Voice: the `human-facing` profile, checked with the host's prose lint
     when available (Vale with the Helix styles) and by a read-aloud pass.
   - Visual: render every slide or page to an image and look at each one for
     overflow, collisions, orphan bullets, unreadable contrast, or a missing
     visual. Fix and re-render. A deck nobody looked at is not finished.
   - File: the rendered file opens and validates with the host's checker
     (for `.pptx`, the presentation tooling's validator; for HTML, the page
     renders without console errors).
   - Flow checklist: every item in the chosen flow's `checklist` in
     `deck-flows.yml` holds.
   - Coverage: every concept group in the inventory is marked covered or
     omitted with a reason; every `must_cover` concept is covered by a
     message; no `must_omit` concept appears in a title or body; a `survey`
     covers at least five groups. `check-deliverable.py` reads the Brief and
     the coverage table and fails on any of these.
9. **Hand-off.** Save the script under the flow root (default
   `06-iterate/deliverables/DEL-<nnn>-<slug>.md`) with `ddx.links` to every
   source artifact and `authoring.export` pointing at the renders. Report:
   the takeaway sentence, the titles-only outline, assumptions and gaps,
   gate results, and where the files are. Do not present the deck as
   approved; it is `draft` until a person reviews it like any artifact.

## Kinds

| Kind | Shape | Budget |
|---|---|---|
| `deck` | title, optional agenda, content slides, ask, appendix | `slides_per_minute_of_talk` × slot; at most 12 content slides without an explicit exception |
| `one-pager` | takeaway, 3 to 6 sections, ask, sources footer | `max_words_one_pager` from the theme |
| `brief` | takeaway, up to 8 sections with headings as claims, ask, sources | 2 to 4 pages |

## Not this mode

- Editing a governing artifact because the deck revealed a gap: route to
  `evolve` or `align` with the gap as evidence, then re-present.
- Decks a client edits live in a shared tool: those stay `authoring.home:
  external-tool` per the conventions; `present` can draft the script they
  start from.
- Marketing copy without a governing artifact behind it: there is nothing to
  project; frame first.
