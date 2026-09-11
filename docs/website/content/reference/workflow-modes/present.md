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
`slide-patterns.yml` (pattern catalog, density rules, story spines), and
`deliverable-mappings.yml` (which sections of which source types feed which
units). Voice: the `human-facing` profile in `voice.yml`.

## Contract

1. **Intake.** Resolve, in this order: audience (who decides or acts),
   occasion (meeting, send-ahead, board pack), the decision or action sought,
   time slot or page budget, kind (`deck` | `one-pager` | `brief`), and
   constraints (brand, confidentiality, must-include, must-omit). At `low`
   and `medium` autonomy ask for anything missing in one message; at `high`
   infer from the artifacts and record each inference under `## Assumptions
   and gaps`. A deliverable with no named audience and no decision sought is
   not authored; that is a framing gap, not a default.
2. **Source selection.** Walk the flow's artifact graph from the governing
   artifacts. Use `deliverable-mappings.yml` for the source type(s) named or
   implied; when several sources apply (a status review draws on the
   iteration plan and the status report), merge their units and drop
   duplicates. Read every source section you project. Content the
   deliverable needs that no artifact holds (`gaps_to_ask`) becomes a
   question or a recorded assumption, never an invented fact.
3. **Story spine.** Pick the spine by occasion (`story_spines` in
   `slide-patterns.yml`): pyramid for decisions, situation-complication-
   resolution for proposals, plan-actual-next for status, problem-solution-
   evidence for walkthroughs. Write the one-sentence takeaway the audience
   should leave with, then the claim titles that build to it. Reading only
   the titles must tell the story; if it does not, rewrite the titles before
   touching bodies.
4. **Pattern selection.** Give each unit one pattern from
   `slide-patterns.yml` by content shape, honoring the density rules (no
   three consecutive units of one pattern, at most one stat callout per
   section, a visual on every content slide) and the time budget
   (`slides_per_minute_of_talk`). A unit that overflows its pattern's limits
   is two units, not a denser slide.
5. **Write the script** in the `deliverable` template with the
   `human-facing` voice: claim titles, bodies inside the pattern limits, a
   visual specification per unit (what the chart or diagram shows, its
   series and source, not just "chart"), speaker notes carrying the detail
   the slide omits, and a Sources appendix mapping every figure and claim to
   a governing artifact section. Subset the sources when the audience needs
   less; never contradict them. No HELIX vocabulary in bodies: artifact IDs,
   activity names, work-item terms, and acceptance-criterion codes live only
   in the Sources appendix and the frontmatter.
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
   passes; a failure loops back to step 5 or 7, never to "good enough":
   - Script checks (`scripts/check-deliverable.py <script>` beside this
     skill, or by hand on hosts without scripts): every unit has a claim
     title, a pattern, a visual, notes, and sources; no placeholder text; no
     HELIX vocabulary in bodies; word and bullet limits per pattern; density
     rules; every number in a body appears in Sources.
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
