# ADR-014: Deferred: architecture-style slot occupants remain four separate concerns

| Date | Status | Deciders | Related | Confidence |
|------|--------|----------|---------|------------|
| 2026-05-30 | Deferred | HELIX maintainers | concerns/onion-architecture, concerns/clean-architecture, concerns/hexagonal-architecture, concerns/classic-layered, ADR-006 | Medium |

## Context

| Aspect | Description |
|--------|-------------|
| Problem | The architecture-style slot has four occupants (`onion-architecture`, `clean-architecture`, `hexagonal-architecture`, `classic-layered`) that sustain substantial content overlap by necessity — they are mutually exclusive at composition time and share the same shape (layering, dependency direction, boundary rules). The audit asked whether they should collapse into one concern with four variants, or remain as four separate concerns. |
| Current State | Each occupant ships its own `concern.md` + `practices.md`. The orthogonality audit classified the cluster as by-design slot competition. The verbosity attributed to these concerns is largely a consequence of the concern file shape (boundary restated in `concern.md`, `practices.md` "Boundary with neighbors", and Constraints/Drift Signals/Quality Gates), which is addressed separately by the concern file shape ADR. |
| Requirements | The audit needs a recorded decision so Phase 3 can proceed without re-opening this question. The decision must respect the audit's scope (it does not own the slot model itself). |

## Decision

We defer the question of whether the four architecture-style concerns collapse
into one concern with four variants. For this audit, the four concerns remain
separate — each keeps its own `concern.md` + `practices.md` and follows the
concern file shape ADR so the boundary is stated once.

The question of per-occupant concern vs one concern with variants touches the
**slot model itself**, which is broader than this audit's scope. Collapsing
the architecture-style slot now would impose a shape on the other slot
families — language-runtime (`go-std` / `python-uv` / `rust-cargo` / `scala-sbt`
/ `typescript-bun`), e2e-framework (`e2e-kind` / `e2e-playwright`), and
demo-framework (`demo-asciinema` / `demo-playwright`) — without the
methodology-level analysis that decision warrants. That analysis is a separate
follow-up audit of the slot model, not a finding of the artifact-types-and-
concerns audit.

The plan's Open Questions section preserves the question for that follow-up.

**Key Points**: defer — not reject | four occupants remain separate concerns
for now | the slot-model decision is its own audit | concern file shape ADR
handles the restated-boundary verbosity independently

## Alternatives

| Option | Pros | Cons | Evaluation |
|--------|------|------|------------|
| Collapse the four architecture-style concerns into one concern with four variants | Removes the most-visible content overlap; one canonical boundary statement | Imposes a per-slot shape decision (variant container) on language-runtime, e2e-framework, and demo-framework slots without the broader methodology analysis; reshapes the slot model from inside one audit | Rejected for now: out of scope for this audit |
| Keep four separate concerns but rewrite each to be a thin delta against an "architecture-style overview" parent concern | Reduces restatement; preserves per-occupant addressability | Introduces a parent/child shape that the slot model doesn't currently support; same methodology-shape consequence as the collapse option | Rejected for now: same scope problem |
| **Keep the four concerns separate; defer the slot-model question to a dedicated follow-up audit** | Respects audit scope; lets the concern file shape ADR address the verbosity root cause without prejudging the slot model; preserves the question for the right venue | The visible content overlap persists until the slot-model audit lands | **Selected: scope-respecting deferral** |

## Consequences

| Type | Impact |
|------|--------|
| Positive | Phase 3 of the audit does not collapse these four concerns; each keeps its own `concern.md` + `practices.md`. |
| Positive | The slot-model decision is preserved for an audit that can analyze all four slot families coherently (architecture-style, language-runtime, e2e-framework, demo-framework). |
| Positive | The concern file shape ADR addresses the restated-boundary verbosity independently of the slot-model question, so the architecture-style concerns benefit from that fix without prejudging this one. |
| Negative | The visible content overlap among onion / clean / hexagonal / classic-layered persists until the slot-model audit lands. |
| Negative | Readers comparing the four occupants still navigate four separate files rather than one variant document. |
| Neutral | The architecture-style slot remains mutually exclusive at composition time; readers still pick exactly one. |

## Risks

| Risk | Prob | Impact | Mitigation |
|------|------|--------|------------|
| The deferred question is forgotten and the four concerns drift further apart | M | M | Plan's Open Questions section records the question; the follow-up slot-model audit picks it up |
| Editors trim restatement per-file in ways that re-introduce drift between the four occupants | M | M | The concern file shape ADR enforces "boundary stated once"; per-occupant trims reference-not-restate the slot's shared shape |
| The slot-model audit collapses the architecture-style slot later and invalidates per-occupant edits made in the meantime | L | M | Phase 3 edits to these four concerns are limited to file-shape compliance, not structural rewrites |

## Validation

| Success Metric | Review Trigger |
|----------------|----------------|
| The four architecture-style concerns each comply with the concern file shape ADR (boundary stated once) | A subsequent audit finds restated boundary prose across the four occupants |
| The plan's Open Questions section preserves the slot-model question for a follow-up audit | The question is silently dropped without an audit landing |
| Phase 3 does not include structural rewrites of these four concerns | A Phase 3 commit collapses or restructures the architecture-style slot |

## References

- Plan: docs/helix/02-design/plan-2026-05-30-artifact-types-and-concerns-audit.md (Open Questions item 7)
- ADR-006: Concern boundary lives once
- workflows/concerns/onion-architecture/
- workflows/concerns/clean-architecture/
- workflows/concerns/hexagonal-architecture/
- workflows/concerns/classic-layered/
