# Diagram spike brief and prompts

## Shared brief

Explain HELIX's current solution architecture to developers and conference
attendees. Preserve these entities: Software team, Agent runtime, HELIX routing
skill, Artifact catalog, Project scope (.helix.yml), Project documents.

Preserve directed relationships: team asks runtime; runtime loads skill; catalog
guides skill; scope bounds skill; skill authors/reconciles documents; documents
govern authorized runtime execution. Group only catalog and skill inside HELIX.
The catalog summarizes templates, prompts, metadata, and mode contracts. These
are conceptual actions/information, not executable calls by Markdown documents.
Use a readable overview, retain editability, and name deliberate simplifications.
The governing source is ../solution-overview.md and ../architecture.md.

## 1. Infographic Architect

Use the supplied architecture-infographic workflow, visual grammar, template
catalog, and QA checklist. Select the three-column methodology composition and
adapt its structure to team/runtime, portable HELIX content, and project
artifacts. Favor strong typographic hierarchy, a blue primary path, teal return
flow, and whitespace. Author original SVG geometry with the shared six entities
and relationships; do not import the unrelated sample's memory/learning systems.
Render a 16:9 PNG and inspect actual output. Run the supplied SVG linter and
triage its heuristic warnings visually.

## 2. Eraser Diagrams

Use @eraserlabs/diagrams 0.2.0, not a hand-drawn imitation. Author JSON entities
and connections, including a HELIX Group and child containerId fields. Use stock
Shape/Group/Textbox components, clean typography, a document shape, and explicit
ports. Let Eraser measure labels and route relationships. Start with defaults,
then refine fills, borders, and spacing. Export native JSON, measured JSON,
HTML, and PNG. Report renderer warnings and editability limitations.

## 3. D2 / TALA

Use D2 0.9.0 and the actual TALA engine. First render the shared graph using
automatic layout; retain that evidence. If it is unsuitable for presentation,
make a second source that pins node positions with top/left while TALA handles
sizing and connections. Use an actual HELIX container and labeled dashed
constraints. Export SVG, and render a browser PNG for inspection.

## 4. Visual Explainer

Follow the skill's Blueprint dark register, diagram guidance, and six-step
mechanism explanation. Build one offline HTML page with inline SVG and editable
text, a warm accent for the skill/active path, and controls to highlight each
relationship. Keep the whole architecture available in Overview. Support
keyboard arrows, reduced motion, and visible captions. Inspect the actual page
and exercise every step plus reset. This is prompt-guided original authoring,
not a prebuilt layout engine.

## 5. Beautiful Mermaid

Use beautiful-mermaid 1.1.3 to render the shared Mermaid graph. Explicitly declare
both skill and catalog inside the HELIX subgraph. Choose a coordinated light
palette and comfortable node/layer spacing. Preserve native SVG, render it in a
browser (including CSS variable colors), and check containment/direction.

## Shared review

Use the C4 diagram checklist as a semantic aid: scope, entity names/types,
relationships/directions, ownership boundary, notation, and understandable terms.
This is a conceptual solution view rather than a strict C4 container diagram.
Do not invent hosting technologies or runtime services to fill a checklist.
Record what the renderers actually did; do not claim a conference audience test.
