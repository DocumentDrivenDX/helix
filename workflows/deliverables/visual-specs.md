# Visual specs for deliverable scripts

The `**Visual**` line of a deliverable unit can open with a small structured
spec so the renderer (`skills/helix/scripts/render-deck.js`) draws the visual
instead of guessing from prose. Prose after the spec is the description for
people and stays required: it says what the visual shows and where it comes
from, which is what `check-deliverable.py` reads.

## Grammar

```
**Visual**: kind: <kind> | <field>: <value> | <field>: <value>. <prose description>
```

- Fields are separated by ` | ` (space, pipe, space). The first field is
  always `kind`.
- A list value separates items with `;` (`steps: Write the brief; Check alignment`).
- A cell inside a list item separates parts with ` / ` (`rows: Today / With HELIX`).
- Indexes are 1-based (`highlight: 2` means the second step).
- The spec ends at the first `. ` after the last field, or at the end of the
  line. Do not put a period inside a field value; use a comma or a semicolon.
- Do not use square brackets anywhere on the line; the script checker reads
  them as placeholders.

## Kinds

| Kind | Fields | Draws |
|---|---|---|
| `process-flow` | `steps` (3 to 5), `highlight` (index), `caption` (under the highlighted step), `details` (one per step; falls back to body bullets whose prefix before `:` matches a step) | Chevron flow left to right in the primary hue; the highlighted step in the secondary hue |
| `timeline` | `milestones` (3 to 6), `now` (index of the present), `marker` (an annotation under the present), `caption` | A horizontal line with milestone dots; labels alternate above and below |
| `two-column` | `left`, `right` (headers), `rows` (`left cell / right cell` per item; falls back to body bullets prefixed with the header text), `prefer` (`left` or `right`), `verdict`, `icons` (`left icon; right icon`) | Two cards with parallel rows; the preferred side carries check marks |
| `table` | `columns` (`a / b / c`), `rows` (`a / b / c` per item; falls back to body bullets split at the first `:`), `highlight` (row index) | A native table with a filled header row and one highlighted row |
| `stat` | `stats` (`value / caption` per item, at most 3), `label` (small text under every caption, for example `target`), `icons` (one per stat) | Cards with the value at stat-callout size |
| `panels` | `items` (`name / one-line detail` per item, at most 4), `icons` (one per item) | Cards in a row, each with an icon badge (or its number) |
| `boundary` | `outer`, `outer-note`, `inner`, `inner-note`, `caption` | An outer box wrapping an inner box, with arrows from the inner box outward |
| `helix` | `left`, `right` (strand names), `left-note`, `right-note`, `rungs` (the label on the rungs) | Two vertical strands joined by rungs |
| `risk-grid` | `risks` (`name / likelihood / impact` per item; likelihood and impact are `low`, `medium`, or `high`), `mitigations` (one per risk; falls back to body bullets split at the first `:`) | A 3x3 likelihood-by-impact grid with numbered dots, mitigations keyed by number |
| `layer-stack` | `layers` (3 to 6, top to bottom), `details` (one per layer; falls back to body bullets whose prefix before `:` matches a layer), `highlight` (index), `icons` (one per layer), `caption` | Full-width bands stacked top to bottom with arrows between them; the highlighted band in the support hue |
| `cycle` | `steps` (3 to 8), `highlight`, `icons` (one per step), `center` (a label inside the ring), `caption` | Nodes on a dashed ring with direction arrows between them; labels sit outward from each node |
| `hub` | `center` (the hub label), `spokes` (`label / one-line detail` per item, 3 to 8), `highlight`, `icons` (one per spoke), `caption` | One hub node fanning out to rows on the right, joined by a trunk line |
| `icon-list` | `items` (`icon / label / detail` per item, at most 8; falls back to body bullets split at the first `:`), `columns` (1 or 2) | Rows of icon badge, bold label, and muted detail |
| `none` | `owners`, `dates` (one per step, read by `ask-next-steps`); `ask` (read by `agenda`); `icon` (read by `title`, `section-divider`, and `statement` for the hero marker) | Nothing; the pattern's own typography is the visual (title, quote, stat-callout, ask-next-steps, appendix-sources) |

## Icons, placement, and looks

- `icons:` (a list, one per item) or `icon:` (one) names files from
  `skills/helix/scripts/icons/` without the extension: `layers`, `shield`,
  `agent`, `person`, `gate`, `check`, `alert`, `loop`, `route`, `search`,
  `presentation`, `flag`, `chart`, and the rest of the set (the directory
  lists them). The renderer rasterizes each icon in the badge's hue; on a
  host without `rsvg-convert` or ImageMagick the badge shows its number
  instead, so an icon never carries information the label does not.
- `side: left` on a `claim-evidence` unit puts the visual on the left and
  the bullets on the right; `split: narrow` or `split: wide` gives the
  bullets 4 or 6 of the 12 columns (default 5). Alternate sides across a
  run of claim-evidence slides.
- The Brief's `**Look**` line picks the deck's look from `theme.yml`
  (`editorial`, `technical`, `bold`, `classic`): the font pairing, whether
  the content slides sit on the light or the dark surface, the marker shape
  behind numbers and icons, and which hue leads. The renderer's `--look`
  flag overrides it for a second cut of the same script.

A `**Visual**` line without a spec still renders: the renderer draws a
placeholder panel holding the prose so the slide is honest about what is
missing, and `deck-qa.py` reports it.

## Examples

```
**Visual**: kind: process-flow | steps: Import; Review; Own exceptions | highlight: 2. Three-step strip drawn from the pilot scope in the business case, with the review step highlighted
```

```
**Visual**: kind: stat | stats: $1.2B / spent yearly on reconciliation labor and tools; $180M / sits in firms of the size we can serve | label: planning assumption. Two stat callouts from the opportunity sizing section
```

```
**Visual**: kind: two-column | left: CSV-first pilot | right: Bank feeds first | rows: Learns about reviewer trust in weeks / Stronger automation story; Needs pilot recruiting and careful data handling / Longer build and higher integration risk | prefer: left | verdict: CSV-first, because the open question is trust, not automation. Two columns from the alternatives table in the business case
```

```
**Visual**: kind: risk-grid | risks: Exports vary too much / high / medium; Reviewers distrust suggestions / medium / high; Firms will not pay enough / medium / high. Likelihood-by-impact grid from the risk assessment, mitigations from the body
```

```
**Visual**: kind: layer-stack | layers: Vision; Requirements; Designs; Tests; Code | highlight: 5 | icons: compass; target; puzzle; check; code | caption: a change enters at the top layer it touches and flows down. Five bands from the artifact hierarchy, details from the body
```

```
**Visual**: kind: hub | center: One skill | spokes: Frame / vision, requirements, stories; Align / drift, gaps, contradictions; Evolve / thread one change through; Present / decks, briefs, reports | icons: target; search; route; presentation | highlight: 2. Hub-and-spokes from the routing table, alignment highlighted
```
