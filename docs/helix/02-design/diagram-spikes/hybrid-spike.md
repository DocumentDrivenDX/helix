---
ddx:
  id: helix.diagram-hybrid-spike
  type: tech-spike
  status: draft
  authoring:
    home: repo
---
# Technical spike: Visual Explainer style with Eraser geometry

## Objective

Combine the preferred dark presentation/walkthrough treatment with native Eraser
component measurement and connector routing. Produce a reviewable interactive
prototype and include it with the five earlier examples in a shareable PDF.

## Hypothesis

The presentation layer can change emphasis without moving or redrawing Eraser's
measured elements. Geometry remains stable while the walkthrough selects the
six relationships in HELIX's solution overview.

## Approach

`render-hybrid.mjs` renders `06-hybrid.json` with Eraser Diagrams 0.2.0. The JSON
uses Visual Explainer's dark Blueprint color roles. Eraser's native HTML,
embedded fonts, IDs, measured boxes, labels, masks, and routed connector paths
are retained. An HTML wrapper adds the heading, responsive scaling, captions,
keyboard-accessible buttons, and relationship focus. It does not redraw paths.

Entity positions are authored; this is not automatic node placement. Relationship
ports and one perimeter return-route guide are authored constraints. Native
measurement and routing still belong to Eraser. No new global dependencies or
production methodology changes are part of the spike.

## Findings

**FINDING 1**: The presentation/geometry boundary works for this example.
All six steps and the Overview reset pass browser checks. Entity bounds remain
identical before and after the walkthrough. The native renderer returns no
warnings. Evidence: `06-hybrid-result.json` and `06-hybrid-browser-checks.json`.

**FINDING 2**: A clean automatic route is not guaranteed for every relationship.
The first short return path crossed the scope constraint. A perimeter guide
moved it below the scope box. The final screenshot was visually reviewed;
label-to-node overlap checks report none. The automated check is not a proof
that all possible edge/edge or edge/label intersections are absent.

**FINDING 3**: Static and interactive delivery serve different review tasks.
The HTML demonstrates focus transitions. The nine-page PDF supplies the five
original comparisons, the hybrid overview and one active-step capture, provenance,
and team feedback questions. Static captures do not reproduce the controls.

## Analysis

Hypothesis: confirmed for the retained small graph. Opacity, color, border
emphasis, and external captions change; native geometry remains stable. More
complex topologies, font environments, and integration with a general HELIX
renderer remain untested. Current evidence supports feasibility, not adoption.

## Conclusions

The hybrid is a useful candidate for team review. Eraser improves component and
connector consistency, while the walkthrough adds presentation focus. Layout
intent, relationship routing constraints, and visual review still matter.

## Recommendations

**RECOMMENDATION**: Review the PDF and interactive prototype with the team before
changing the diagram standard. Gather specific defects and comprehension issues;
then test the chosen approach on a denser architecture and a failure scenario.

## Artifacts

- [Interactive hybrid](06-hybrid.html), [overview PNG](06-hybrid.png),
  [active-step PNG](06-hybrid-step.png), [editable JSON](06-hybrid.json).
- [Native measured geometry](06-hybrid-measured.json),
  [renderer outcome](06-hybrid-result.json),
  [browser checks](06-hybrid-browser-checks.json).
- [Render source](render-hybrid.mjs); use the optional dependencies declared in
  `package.json`, set `CHROMIUM_PATH`, then run `node render-hybrid.mjs`.
- [Shareable PDF](../../../../output/pdf/helix-architecture-diagram-review.pdf),
  built with [build-review-pdf.py](build-review-pdf.py) and ReportLab.

Source projects and versions are documented in the comparison README and PDF.
Upstream font/package notices are retained under `licenses/`. The prototype has
not undergone an independent comprehension test or venue projection trial.

## Verification

The final hybrid renderer reports zero warnings. Browser checks exercise all
six steps and reset, report no page errors or label/node overlaps, and confirm
stable entity geometry. Every PDF page was rasterized and visually inspected;
the nine-page document contains readable text and 12 external source links.
`just test` passes with the repository's optional tool/source skips, and
pre-commit checks pass. Generated PDFs are marked binary in Git so encoded
streams are not treated as prose or merged as text.
