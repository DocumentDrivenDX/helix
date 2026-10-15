---
ddx:
  id: helix.diagram-toolkit-spikes
  type: tech-spike
  status: draft
  authoring:
    home: repo
---
# Technical spike: architecture diagram toolkits

## Objective

Determine which existing prompts/toolkits improve HELIX's solution overview for
conference presentation and developer orientation. Produce reviewable outputs
from five approaches against the same six-entity/six-relationship brief.

Scope: bounded local prototypes and comparison. No production adoption, template
changes, global skill installation, live external model service, or publication.
The existing overview remains unchanged. [Open review gallery](index.html).

## Hypothesis

A composition-oriented skill will outperform an automatic renderer for a talk;
a component renderer will offer better repeatability and revision support.
Automatic layout will need art direction for a slide-sized composition.

## Approach

Initial capability/quality priority: Infographic Architect → Eraser → D2/TALA →
Visual Explainer → Beautiful Mermaid. All five were tried sequentially, with
local rendering and one or more correction passes. See [exact brief and prompts](prompts.md).
These are individual capability spikes, not statistically controlled benchmarks;
font, aspect ratio, styling knobs, and amount of manual work differ by approach.

| Approach | Actual mechanism exercised | Editable evidence |
|---|---|---|
| Infographic Architect | Original SVG authored using its skill, composition patterns, and QA guidance | SVG; PNG; prompt |
| Eraser 0.2.0 | Installed Node renderer, stock components, native containment, measured geometry and edge routing | JSON; measured JSON; HTML; PNG |
| D2 0.9.0 / TALA | Actual binary, automatic layout then pinned composition | D2 sources; SVG; PNG |
| Visual Explainer | Original HTML/SVG authored using skill + Blueprint/diagram guidance | Interactive HTML; overview PNG; highlighted-step PNG |
| Beautiful Mermaid 1.1.3 | Actual package renderer with explicit theme/layout options | Mermaid source; SVG; PNG |

## Findings

**FINDING 1**: **Infographic Architect gives useful composition guidance.** The three-column
   method pattern can be adapted to HELIX's ownership boundaries without copying
   the sample's unrelated architecture. It still requires manual geometry and
   typography decisions. The upstream linter gave 11 initial heuristic warnings (nine after semantic
   grouping and separator cleanup); visual
   inspection found long-label/stack overlap warnings and return-label masking
   acceptable here. The result is an original prompt-guided drawing, not an
   independent tool generating a layout.
**FINDING 2**: **Eraser reliably measures and routes this example.** Both passes returned
   `ok: true` and zero warnings. Default gray/blue fills and shadows looked generic;
   the second pass uses plain white entities, an emphasized skill, and muted
   borders. JSON/HTML retain editability; this tested API exports HTML/PNG/JSON,
   not SVG. [Renderer result](02-eraser-result.json).
**FINDING 3**: **TALA's automatic layout was a poor fit for a conference slide.** It placed
   the graph vertically. The retained [automatic output](03-d2-tala-auto.svg) makes
   that visible. Pinning nodes produced a usable landscape version while TALA
   still routed edges. A long relationship label needed wrapping. This is evidence
   for layout control, not evidence that auto-layout solves presentation design.
**FINDING 4**: **Visual Explainer is the strongest talk/onboarding candidate in my judgment.**
   The dark Blueprint composition and active-path focus make the mechanism easier
   to present. It is still manually authored from prompts. The six-step controls,
   final step, and Overview reset pass browser checks; zero page errors and no
   text outside the SVG canvas were observed. Motion is disabled under reduced
   motion. HTML is the editable source; the PNG is a captured overview.
**FINDING 5**: **Beautiful Mermaid is the fastest route to a restrained documentation view.**
   The output is compact and fully generated from short text, but its default
   thin lines, small labels, and very wide aspect ratio do not deliver conference
   composition. Explicitly declaring the skill inside the subgraph corrected an
   initial ownership-boundary issue. It is the lowest-effort revision path here.

## Analysis

Hypothesis: partially confirmed. Prompt-guided composition offers more control
for presentation. Eraser provides the best tested component/routing foundation;
TALA needs positional constraints for this graph. These observations apply to
this one small solution view, not every architecture topology or feature of
these tools.

The C4 checklist was applied as a semantic review aid: all final outputs contain
six named entities, all six directed relationships, and a HELIX boundary around
catalog and skill. Guidance/constraints use dashed relationships. Technology
protocols are omitted because these are conceptual interactions, not network
calls. Beautiful Mermaid relies on the gallery for diagram title/scope. No strict
C4 container-diagram conformance is claimed.

## Conclusions

My current preference: Visual Explainer for presenting an explanation; Infographic
Architect for a static slide; Eraser for a maintainable component system. D2/TALA
is promising when layout constraints can be authored; Beautiful Mermaid suits
reference documentation. Confidence: medium for this example, low for a general
project-wide choice before more diagram types are tried.

## Recommendations

**RECOMMENDATION**: Review the outputs before changing HELIX's standard again. Compare the static
Infographic version with Visual Explainer's Overview and active-path steps.
If one direction wins, test it against a denser system map and a sequence/failure
walkthrough. Any toolkit adoption remains a separate design decision.

## Artifacts

- [Review gallery](index.html), with all five previews and editable links.
- [Infographic SVG](01-infographic-architect.svg) and [PNG](01-infographic-architect.png).
- [Eraser JSON](02-eraser.json), [HTML](02-eraser.html), [PNG](02-eraser.png),
  [measured JSON](02-eraser-measured.json), [render script](render-eraser.mjs).
- [D2 source](03-d2-tala.d2), [SVG](03-d2-tala.svg), [PNG](03-d2-tala.png),
  and retained [automatic-layout source](03-d2-tala-auto.d2).
- [Interactive Visual Explainer](04-visual-explainer.html), [overview](04-visual-explainer.png),
  and [highlighted-step capture](04-visual-explainer-step.png).
- [Mermaid source](05-beautiful-mermaid.mmd), [SVG](05-beautiful-mermaid.svg),
  [PNG](05-beautiful-mermaid.png), [render script](render-mermaid.mjs).

## Provenance and reproduction

- [Infographic Architect](https://github.com/SizeSStudio/infographic-architect),
  source snapshot `b3dd7e5`: skill, visual grammar, template catalog, QA guidance.
  Referenced as guidance; no upstream SVG/template code was copied.
- [Eraser Diagrams](https://github.com/eraserlabs/eraser-diagrams), npm 0.2.0.
  MIT; rendered HTML embeds the stock font files for portable output.
  Upstream package and font notices are retained in `licenses/`.
- [D2](https://github.com/d2lang/d2), macOS ARM64 binary v0.9.0 with TALA.
  Source-generated SVG retains its bundled renderer/font output; bundled
  third-party notices are retained in `licenses/`.
- [Visual Explainer](https://github.com/nicobailon/visual-explainer), source snapshot
  `69cd739`: skill, style guide, and diagram reference. Original HTML/SVG authored
  from guidance; it is self-contained and uses host fonts with fallbacks.
- [Beautiful Mermaid](https://github.com/lukilabs/beautiful-mermaid), npm 1.1.3, MIT.
- [C4 review checklist](https://c4model.com/diagrams/checklist), used for semantic review.

Optional rendering dependencies are pinned in this directory's `package.json`;
no project/global dependencies were installed. Node packages and downloaded
sources used for the trial live in a temporary workspace. For reproduction,
install dependencies locally in this directory, provide `CHROMIUM_PATH`, and run
`node render-eraser.mjs` / `node render-mermaid.mjs`. Set `SPIKE_NODE_MODULES` only
when using an alternate installed dependency directory. D2 requires its own binary:
`d2 --layout=tala 03-d2-tala.d2 03-d2-tala.svg`.

Render original SVGs using a browser or Sharp. Beautiful Mermaid uses CSS variables;
its PNG should be captured in a browser. The HTML preview works offline. No venue
projection, independent audience-comprehension test, performance benchmark, or
cross-platform font test was performed. Package/source downloads used network
access; rendering used local assets. Validation: all five gallery previews load, every gallery destination resolves,
and the interactive six-step walkthrough/reset passes without browser errors.
The tech-spike instance validator reports zero findings. `just test`,
`git diff --check`, and pre-commit checks pass. Optional deck-rendering and
Innsigle lanes skip unavailable tools; the external headline source comparison
skips its absent checkout. The pre-commit advisory historical revalidation path
is missing and configured nonblocking. The gallery was inspected as a rendered
contact sheet, and each individual final preview was inspected.
