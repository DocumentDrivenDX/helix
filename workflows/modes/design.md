# Design

Use when the requested change needs design authority before implementation.

1. Read the requested scope and the governing artifacts that can affect it.
   Read implementation, tests, concerns, and existing work only when relevant
   to the design question.
2. Draft the applicable requirements, decisions, interfaces, failure behavior,
   security, tests, dependencies, risks, and observability. Omit sections that
   do not apply; do not add empty data-model or security sections for ceremony.
3. Preserve acceptance criteria and give each implementation slice a
   verifiable outcome. Validate dependency references before writing.
4. Resolve material unknowns with evidence or a bounded spike; state unresolved
   assumptions and ask for decisions that affect the design.
5. Stop when the design is implementable and no material ambiguity remains.
   Treat a requested round count as an upper bound, not a minimum.
6. Derive ordered work items only when the user requests them or the runtime
   requires them.

## Source-Code Boundaries

For handwritten source, apply `modularity-and-encapsulation`: Architecture records Module Boundaries per its practices; Contracts own exact shared interfaces, and TD applies the map. Name actual modules, owned types, public APIs, allowed/forbidden imports, integration owners, construction policy, and a concrete project boundary command. Review semantic correctness; instance structure alone cannot establish readiness.

Procedure: `workflows/actions/plan.md` supplies additional detail.
