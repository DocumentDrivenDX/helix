# Present

Use to turn governed artifacts into a deck a client, sponsor, or executive
can read or watch on the first try. Output: a `deliverable` artifact (a
governed Markdown script, the document of record) plus rendered files
(fidelity evidence). Engage on: deck, slides, pitch, board or exec update,
memo, client-ready or customer-facing document, "make this presentable".

Reference data (`deliverables/` in the bound catalog, via §Catalog
Resolution): `slide-patterns.yml` (patterns; the single owner of limits and
density), `deck-flows.yml` (beats, `default_length_budget`, transitions,
checklist per occasion), `deck-craft.md` (the reasoning), `visual-specs.md`
(the `**Visual**` spec grammar), `deliverable-mappings.yml` (source sections
to units), `theme.yml` (palette, typography, looks). Voice: `human-facing` in
`voice.yml`. Procedure: `workflows/actions/present.md` (step detail; this
file is the contract).

## Intake

In order: audience (who decides or acts), occasion, the decision or action
sought, time slot, kind (`deck`; `memo` and a mapping's `default_kind:
one-pager` resolve to `deck` for now), look (`editorial`, `technical`,
`bold`, `classic`, by room from `theme.yml`), constraints (brand,
confidentiality, must-include, must-omit). At `low` and `medium` autonomy
ask for what is missing in one message; at `high` infer and record each
inference under `## Assumptions and gaps`. No audience and no decision
sought: not authored; a framing gap, not a default. Breadth is declared in
the Brief, never inherited from a mapping: `scope`, `breadth` (`survey` or
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

`scripts/render-deck.js` (beside this skill) needs node with `pptxgenjs`;
`scripts/deck-qa.py` rasterizes through LibreOffice and `pdftoppm`; icons
through `rsvg-convert` or ImageMagick (without one, a badge shows its
number). Without a tool the script is still produced: `## Render` records
which targets were not produced and why, and the gate runs on the produced
set; the visual and file checks and `rendered_and_inspected` in `meta.yml`
warn and name the missing tool rather than block. HTML is not a target until
a renderer exists.

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

| Kind | Shape | Budget |
|---|---|---|
| `deck` | title, optional agenda, content slides, ask, appendix | `default_length_budget` in `deck-flows.yml`; `content_slides_max` in `slide-patterns.yml` without an explicit exception |

`one-pager` and `brief` are a backlog item
(`docs/helix/06-iterate/improvement-backlog.md`): no document flow, no
section patterns, no renderer, and no kind-aware checks exist, so `meta.yml`
keeps them in `kind.enum` as planned and this mode does not author them.

## Not this mode

- Editing a governing artifact because the deck revealed a gap: route to
  `evolve` or `align` with the gap as evidence, then re-present.
- Decks a client edits live in a shared tool stay `authoring.home:
  external-tool`; `present` can draft the script they start from.
- Marketing copy without a governing artifact behind it: frame first.
