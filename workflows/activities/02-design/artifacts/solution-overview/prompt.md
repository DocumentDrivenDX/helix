# Solution Overview authoring prompt

Explain the overall solution to a new developer before they read detailed designs.
This is a navigational projection of governing artifacts, not a new source of
requirements or structural decisions. Link to Architecture, requirements,
and relevant contracts. Identify current versus proposed views and uncertainty.
Use one readable system map with labeled arrows, boundaries, and a legend.
For content libraries or batch tools, draw actual content and execution actors;
do not invent services to fill a conventional architecture diagram.
Name concrete source locations and two or three critical flows. Link to a
walkthrough and developer guide. Define unfamiliar vocabulary locally.
Keep setup commands in the developer guide and structural decisions in Architecture.
Name update triggers and the maintainer role. Check every source link.

## Presentation visual quality

For conference or flagship visuals, apply `workflows/references/diagram-design.md`.
Start with the audience, one question, one takeaway, and semantic entities/edges.
Keep a maintainable semantic view and create an editable vector presentation
view when precise composition is needed. Use a named boundary, deliberate
hierarchy, readable labels, and consistent color/connector roles. Retain source
paths in adjacent prose. Render and inspect at full and preview sizes; correct
collisions before delivery. Record export provenance, semantic parity, deliberate
omissions, review evidence, and limits. Do not equate a successful export with
readability or an unperformed audience trial. This is an optional delivery
profile, not a new requirement for every reference diagram.

For a developer-facing HTML field guide, use the architecture field guide profile
and reusable prompt in `workflows/references/diagram-design.md`. Start with
`workflows/references/architecture-plate.html`; replace all worked-example facts.
Keep the numbered walkthrough, sources, limits, offline delivery, mobile and
print review. Reference HTML supplies styling ideas, never project authority.
