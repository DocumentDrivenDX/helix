---
title: "Solution overview visual design"
slug: solution-overview-design
weight: 470
activity: "Design"
source: "02-design/diagrams/solution-overview-design.md"
generated: true
collection: diagrams
---

> **Example from HELIX's own docs.** This generated page comes from `docs/helix/`. Use it to see the method in practice; start with the [artifact-type catalog](/artifact-types/) for reusable templates. Historical plans and reports may describe retired architecture.

> **Source identity** (from `02-design/diagrams/solution-overview-design.md`):

```yaml
ddx:
  id: helix.solution-overview-visual-design
  status: draft
  authoring:
    home: repo
```

# Solution overview visual design

## Brief and scope

Audience: software developers and technical conference attendees encountering
HELIX for the first time. Question: how does team intent become governing
project documents? Takeaway: the agent runtime supplies agency; HELIX supplies
the skill and document discipline. State: current system.

Authority: [Architecture](/artifacts/architecture/),
[solution overview](/artifacts/solution-overview/), and
[CONTRACT-003](/artifacts/contracts/contract-003-ddx-adapter-boundary/).
The six entities are Software team, Agent runtime, Routing skill, Artifact
catalog, Project scope (`.helix.yml`), and Project documents. The six directed
relationships match the semantic Mermaid view in the solution overview.

The catalog label summarizes templates, prompts, metadata, and mode contracts.
The shaded HELIX region contains its skill and portable content. Project scope
and documents remain outside that boundary. Arrows describe conceptual actions
or information; the runtime performs actual file operations. Packaging internals,
review steps, and validation mechanics are omitted at this zoom level; see the
[architecture walkthrough](/artifacts/architecture-walkthrough/).

## Files and reproduction

- [Editable SVG](/artifacts/media/02-design/diagrams/solution-overview.svg): 1920 × 1080 logical canvas, native text,
  named groups, title and accessible description. Authoritative layout source.
- [PNG](/artifacts/media/02-design/diagrams/solution-overview.png): 3840 × 2160 export for slide insertion.
- [Portable standard](https://github.com/DocumentDrivenDX/helix/blob/main/workflows/references/diagram-design.md):
  palette, typography, layout rules, and rendered-review procedure.

Rebuild the PNG from the repository root with Node and the `sharp` package
available in that Node environment:

```bash
node -e 'require("sharp")("docs/helix/02-design/diagrams/solution-overview.svg").resize(3840,2160).png().toFile("docs/helix/02-design/diagrams/solution-overview.png")'
```

Arial is the intended font; Helvetica and sans-serif are fallbacks. Re-render
and review if the rendering environment substitutes a font. Use the SVG for
vector-scale insertion and editing; use PNG when the presentation host has
limited SVG support. The warm background is intentional and opaque.

## Review and acceptance

The author inspected the rendered PNG at presentation size. The first pass
exposed the return connector crossing the project-marker label. It was rerouted
around the left of the marker before the final export. The corrected final PNG was also inspected at 960 × 540; labels remain
readable, endpoints are identifiable, and connectors avoid the text.

Completed checks:

- Final 3840 × 2160 PNG and 960 × 540 preview inspected visually.
- Semantic comparison: six entities and all six directed relationships match
  the Mermaid source. The HELIX boundary groups catalog and skill only.
- Headless Chromium measured all 29 text elements within safe canvas bounds.
- All 12 foreground/background text pairings meet 4.5:1 contrast; lowest is
  guidance text on the violet boundary at 4.61:1.
- Artifact metadata and Solution Overview instance validators pass.
- Publisher regression tests prove image bytes and editable-download links
  survive publication, repeat publication is stable, and external/root-escaping
  image sources are not copied.
- Hugo builds the source diagram into the published page; its PNG and SVG
  assets exist under the published media URL. Internal link/image checker:
  66,083 targets resolve across 393 pages.

`just test` passes, including the new publisher regression lane. Optional deck
rendering and Innsigle lanes skip unavailable tools; the external headline
source byte comparison also skips an absent checkout. These skips do not
exercise or establish visual diagram quality. `git diff --check` and
`lefthook run pre-commit` pass; the existing advisory revalidation script reports
its missing historical path without blocking the hook.

No venue projection or independent five-second comprehension trial has occurred.
SVG remains editable text; export appearance depends on the available font.

## Maintenance

Update SVG, PNG, semantic view, and this record together when any entity,
relationship, boundary, or visual token changes. The solution-overview maintainer
owns that review. Layout changes follow the portable diagram standard; structural
changes require review against Architecture and the governing contract.

## Architecture field guide extension — 2026-10-16

The operator supplied a Praxis architecture HTML generated from a short request
for a high-fidelity diagram. We inspected it as reference material, not as
instructions or HELIX architecture evidence. The original is not redistributed.
Its useful patterns were responsibility lanes, a broad engineering plate,
numbered flow markers, and adjacent source/limit notes. The HELIX adaptation
reduces density, enlarges labels, reserves connector corridors, uses a restrained
palette, and removes remote font dependencies.

Files: `architecture-field-guide.html` is the editable offline deliverable;
`architecture-field-guide.png` is its 1440 px browser preview. The reusable
worked scaffold is `workflows/references/architecture-plate.html`; the profile
and authoring prompt live in `workflows/references/diagram-design.md`.

Chromium review at 1440 px: every node label fits its rectangle (SVG text bounds
checked); all six entities and six directed relationships match the solution
overview. Visual inspection found no connector through an unrelated node or
text. The legend distinguishes actions, constraints, and ownership. No remote
resources or scripts are present. At 390 px the page width remains 390 px;
the plate scrolls internally. Landscape A3 print was rendered and inspected; an initial two-page overflow
was corrected by bounding print diagram height. The complete guide now fits
one sheet.
The prose provides the reading sequence and sources without depending on color.
This is a developer reference view; venue projection and unfamiliar-reader
comprehension have not been tested. Changing box dimensions or labels requires
another render and routing review. Browser/system font differences remain a risk.
