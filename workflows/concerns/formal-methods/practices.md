# Practices: Formal Methods

## Frame

- Apply formal methods only to recorded affected slices; preserve scope and rigor in context, with a reasoned non-applicability disposition elsewhere.
- Specify state, transitions, safety/liveness, assumptions and bounds; follow workflows/references/formal-methods.md and keep properties subordinate to requirements and Contracts.
- Record reproducible evidence and model/code correspondence; a bounded model pass is not production proof and never replaces running-system verification.
- Require meaningful success/recovery examples; executable analysis adds reachable witnesses and targeted negative controls, while error/timeout/incomplete analysis is not a pass.
- Recheck affected evidence when requirements, model, assumptions, tool/config or mapped code change; choose precise specification, executable analysis or deductive proof per slice.

Record scope, risk signal, owner and chosen level in Project Concerns Why Active /
Key Practices. Existing Project Overrides can carry project-specific scope and
rigor into compact context; point to the owning design for complete details.
Do not introduce slots, profile fields or an automatic resolver mechanism.

## Design

Write the conditional Formal Specification section of the owning technical
design. Shared interface definitions remain in Contracts; cross-component
policy remains in Architecture/SD/ADR. Give each property a stable identifier,
requirement reference and assurance level. Place executable model/config/proof
files beside the design or in its referenced repository directory.

Specify initial state, guards, transitions, effects and invalid transitions.
State safety separately from liveness and name fairness/environment assumptions.
Record bounds, excluded behavior and why the abstraction preserves properties
of interest. For executable analysis or deductive proof, choose an established
analyzer/proof checker appropriate to the slice; precise-only work requires
semantic review. Unresolved feasibility/correspondence questions go to a bounded spike.

## Test

The Test Plan names each property, analysis command and expected evidence at the
chosen level, plus implementation tests and residual gaps. Exercise meaningful
success, failure and recovery witnesses. For executable analysis, verify a
deliberately broken mechanism produces its intended property violation and
replay the trace where supported. Capture useful traces as regression scenarios.
For precise-only work, record semantic review instead of inventing a tool pass.

## Build

Implement the enforcing guards and map actual code locations/tests to model
elements. Review the mapping and rerun affected analysis before claiming its
level satisfied. Keep run metadata and results with verification evidence.
Do not substitute model-green for tests or full-system exercise. A fenced
landing model does not establish that external side effects are fenced.

## Deploy

For deployed affected behavior, check the environment meets assumptions (for
example lease authority, timer scheduling, delivery and storage atomicity).
Carry observable assumptions, violation symptoms and recovery into the Runbook
and monitoring plan. An assumption that cannot be observed needs reviewed
justification and residual risk; deployment does not automatically prove it.

## Iterate

Incidents and counterexamples refine governing requirements, model and tests.
Recheck affected evidence after model, assumptions, bounds, tool/config or mapped
implementation changes. Keep old results as history, clearly stale for current
claims. Revisit the selected level when risk or complexity changes.

## Review and Align

Check property authority, applicability and chosen level, non-vacuity,
reproducibility and correspondence. Separate model findings, implementation
findings and missing evidence. Preserve legacy artifact validity: adoption gaps
block dependent scoped readiness, not unrelated work or all old documents.

## Quality Gates

- Affected slices: chosen-level evidence is complete and current; failures and unknown/incomplete outcomes block that assurance claim.
- Precise-only: semantic review records states/transitions, property authority and assumptions; no machine-checked claim.
- Executable/proof: observed command and tool/config revision, checked properties, bounds/assumptions, witnesses and applicable negative controls.
- Implementation claim: reviewed correspondence and implementation verification remain required; model-only evidence is insufficient.
- Unaffected slices: recorded non-applicability reason in acceptance/evidence satisfies propagation; no analyzer/proof run is required.
