# Present

Use to turn governed artifacts into a deck, brief, or one-pager a client,
sponsor, or executive can read or watch on the first try. Output: a
`deliverable` artifact (a governed Markdown script, the document of record)
plus rendered files (fidelity evidence). Engage on: deck, slides, pitch,
board or exec update, memo, brief, one-pager, client-ready or
customer-facing document, "make this presentable".

Reference data (`deliverables/` in the bound catalog, via §Catalog
Resolution): `slide-patterns.yml` (patterns; the single owner of limits and
density), `deck-flows.yml` (the index of flows by occasion, plus
`default_length_budget` and `legacy_spines`; each flow's own beats,
transitions, and checklist live in `deliverables/flows/<id>.yml`; read the
index to choose, then read only the chosen flow), `deck-craft.md` (the
reasoning), `visual-specs.md` (the `**Visual**` spec grammar),
`deliverable-mappings.yml` (source sections to units), `theme.yml` (palette,
typography, looks). Voice: `human-facing` in `voice.yml`. Procedure:
`workflows/actions/present.md` (step detail; this file is the contract).

## Intake

In order: audience (who decides or acts), occasion, the decision or action
sought, time slot or page budget, kind (`deck`, `one-pager`, or `brief`; a
mapping's `default_kind` is the starting point, the Brief's own `Kind` line
or an explicit ask overrides it; `memo` resolves to `brief`), look
(`editorial`, `technical`, `bold`, `classic`, by room from `theme.yml`;
`classic` for a printed or filed document), constraints (brand,
confidentiality, must-include, must-omit). At `low` and `medium` autonomy
ask for what is missing in one message; at `high` infer and record each
inference under `## Assumptions and gaps`. No audience and no decision
sought: not authored; that is a framing gap. Breadth is declared in
the Brief, whatever the mapping suggests: `scope`, `breadth` (`survey` or
`deep-dive`), `angle`, `must_cover`, `must_omit`, `max_messages`.

## Steps

1. **Intake.** The fields above.
2. **Scope and inventory.** Three passes over the scope (recurring concepts,
   the corpus's structure, roles and hand-offs); cluster into groups,
   typically five to nine and more when the corpus is wide; rank by
   authority; every group is covered or omitted with a reason under `## Story`.
3. **Storyboard.** Flow by occasion; takeaway, messages, evidence table; a
   claim title per beat; the horizontal-logic test; the headline pass on the
   titles. No body text before this passes.
4. **Pattern selection.** One pattern per unit from the beat's allowed set,
   inside the limits and density in `slide-patterns.yml`.
5. **Write the script** in the `deliverable` template and the `human-facing`
   voice; then the shape pass over bullets, labels, captions, and verdicts.
6. **Theme.** The project's `design-system` artifact when it declares palette
   or typography, else `theme.yml`, with the Brief's look.
7. **Render.** `.pptx` from the script, plus PDF when the host can export one.
8. **Pre-flight gate.** Every check below; a failure loops to step 3, 5, or 7.
9. **Hand-off.** Save, link, report; `draft` until a person reviews it.

## Render toolchain

For `deck`: `scripts/render-deck.js` (beside this skill) needs node with
`pptxgenjs`; `scripts/deck-qa.py` rasterizes through LibreOffice and
`pdftoppm`; icons through `rsvg-convert` or ImageMagick (without one, a
badge shows its number). Without a tool the script is still produced: `##
Render` records which targets were not produced and why, and the gate runs
on the produced set; the visual and file checks and `rendered_and_inspected`
in `meta.yml` warn and name the missing tool.

For `brief` and `one-pager`: `scripts/render-doc.js` needs node alone
(icons are inlined SVG) and always produces the HTML. `--pdf <path>` also
exports a PDF through a local Chrome or Chromium in headless print-to-pdf
mode when one is found (`--chrome <path>` names it explicitly); otherwise
`## Render` records that the HTML alone was produced and why. The renderer
warns when an em dash reaches the page. Rasterize the PDF (`pdftoppm`, or any PDF viewer) and
look at every page before calling the render clean, the same discipline as
`deck-qa.py`'s slide-by-slide inspection.

## Gate

- Script checks: claim title, pattern, visual, notes, and sources per unit;
  no placeholders; no HELIX vocabulary in bodies; pattern limits and density;
  every number in a body appears in Sources.
- Titles and shapes: headline pass clean; no consecutive titles fail
  horizontal logic; every shape passes the shape pass; no restatement.
- Horizontal logic on the finished script; vertical logic on every unit.
- Fidelity: every claim traces to its cited section and does not contradict it.
- Voice: `human-facing`, by prose lint when available and a read-aloud pass.
- Visual: every produced slide rendered to an image and looked at.
- File: the produced `.pptx` opens and passes the host's validator.
- Flow checklist: every item of the chosen flow's `checklist` holds.
- Coverage: every group covered or omitted with a reason; `must_cover`
  carried; `must_omit` absent from titles and bodies; a survey covers five.

## Kinds

| Kind | Shape | Budget | Renderer |
|---|---|---|---|
| `deck` | title, optional agenda, content slides, ask, appendix | `default_length_budget` in `deck-flows.yml`; `content_slides_max` in `slide-patterns.yml` without an explicit exception | `scripts/render-deck.js` → `.pptx` |
| `brief` | masthead (title, byline, introduction) then numbered claim sections in reading order, then the appendix bibliography | no fixed page count; the renderer flows as many pages as the record needs, and a more detailed product needs more (`NFR-3`) | `scripts/render-doc.js --kind brief` → HTML, PDF when a local Chrome/Chromium is found |
| `one-pager` | masthead then a weight-balanced two-column grid of single-column "fact" units (table, claim-evidence, stat, panels, icon-list); a unit whose own visual is already two-part (`two-column-comparison`, `risk-matrix`) or the `ask-next-steps` unit spans full width below the grid | `max_words_one_pager` in `theme.yml` (450); the renderer counts words and warns past it | `scripts/render-doc.js --kind one-pager` → the same HTML/PDF path, forced to one Letter page |

Both document kinds share the deck's script format (frontmatter, Brief,
Story, `## Content` units, `## Sources`), the theme
(`deliverables/theme.yml`), and the Visual-spec grammar
(`deliverables/visual-specs.md`), so a deck and a document from one project
read as one system. `render-doc.js` needs no native dependency; icons are
inlined SVG. Pick the look by room as usual. For a printed or filed document
prefer `classic`, the look `theme.yml` names for proposals and printed
briefs; its bare-numeral marker switches card chrome off in favor of
rule-divided sections, closer to how a printed report is set.

**Headings follow the flow.** A deck or a persuasive document (proposal,
investor pitch, executive status) uses claim titles, and the H1 goes through
the same headline rules as every unit title. A reference flow declares
`heading_style: label` in its file under `deliverables/flows/`
(candidate-briefing does), and its headings are the plain section titles a
reader navigates by: Introduction, Background, Required capabilities, What it
is, Capability alignment, Competitive landscape, Open questions. The gate
reads the Story's `Flow` line, loads that file, and switches the title rules
accordingly; it blocks a count in any document title ("three of five") in
either style, because the finding belongs in the first sentence under the
heading.

**The title unit's Body is the introduction.** For a document kind, write
three to five sentences, one per bullet, joined into a paragraph by the
renderer. For a reference, the introduction is the need, the criteria, and
the finding in that order, lifted from the source's own Need and Required
Capabilities sections: we need a [role] for [use cases] so that [goals]; it
must [capabilities]; we evaluated [candidate] against those and found
[verdict in plain words]. For a persuasive document, open with the reader's
situation and the stakes, then the finding. The Brief's `Audience` and
`Decision or action sought` fields steer the writing and do not print;
`render-doc.js` adds no byline unless the Brief carries a `Byline` line or
`--byline` is passed. The introduction gets the same shape checks as a
bullet, plus a narration check: a sentence that starts "This brief checks"
or "This page names" blocks. A single bullet renders as a short dek line
under a deck's title slide; write the fuller introduction for `brief` and
`one-pager`.

**Nothing on the page the source does not state.** Every owner, date,
duration, likelihood, or impact in a Visual spec must appear in a Sources
row, the Brief, or an Assumptions entry; the gate blocks the rest
(`visual.unsourced`). A flow whose `ask` beat is `required: false` ends on
its last content unit; the gate accepts a deck that closes with
`appendix-sources` alone in that case.

## Not this mode

- Editing a governing artifact because the deck revealed a gap: route to
  `evolve` or `align` with the gap as evidence, then re-present.
- Decks a client edits live in a shared tool stay `authoring.home:
  external-tool`; `present` can draft the script they start from.
- Marketing copy without a governing artifact behind it: frame first.
