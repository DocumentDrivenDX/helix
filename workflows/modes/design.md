# Design

Use when the requested change needs design authority before implementation.

1. Read the requested scope and the governing artifacts that can affect it.
   Inspect the affected implementation, producers, consumers, tests and existing
   work before proposing interfaces or mechanisms. Keep the outcome bounded;
   mechanical propagation across callers is part of completing that outcome.
   Prefer evolving a clear existing concept over adding an overlapping one.
   Before defining a schema, structured interface, or domain model, apply
   `workflows/references/umf-schemas.md`: inspect UMF core, extensions, and domain
   packs; reuse or compose suitable definitions by default, and record specific
   gaps for alternatives. Declare applicable schema references for publication.
2. Draft the applicable requirements, decisions, interfaces, failure behavior,
   security, tests, dependencies, risks, and observability. Omit sections that
   do not apply; do not add empty data-model or security sections for ceremony.
3. Preserve acceptance criteria and give each implementation slice a
   verifiable outcome. Resolve dependencies that materially affect the slice;
   missing graph edges alone do not delay writing or implementation handoff.
4. Resolve material unknowns with evidence or a bounded spike; state unresolved
   assumptions. Check governing authority before asking. If a decision only the
   operator can make still blocks the design, ask, at any autonomy level; a guess
   recorded as an assumption is still a guess. Follow the skill's
   planning-question discipline. Route to `grill` when the operator asks for an
   interview or several open decisions interlock.
5. Stop when the design is implementable and no material ambiguity remains.
   Treat a requested round count as an upper bound, not a minimum.
6. Derive ordered work items only when the user requests them or the runtime
   requires them.

## Source-Code Boundaries

For handwritten source, apply `modularity-and-encapsulation`: Architecture records Module Boundaries per its practices; Contracts own exact shared interfaces, and TD applies the map. Name actual modules, owned types, public APIs, allowed/forbidden imports, integration owners, construction policy, and a concrete project boundary command. Review semantic correctness; instance structure alone cannot establish readiness.

When the project keeps an architecture model (`docs/helix/02-design/architecture-model.toml`, format in `workflows/references/architecture-model.md`), update it with the architecture: add or retire the elements and relations the change touches, each citing the code that shows it, and regenerate the views.

Procedure: `workflows/actions/plan.md` supplies additional detail.
