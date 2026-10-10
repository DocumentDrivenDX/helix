---
title: "Formal Methods"
slug: formal-methods
generated: true
aliases:
  - /reference/glossary/concerns/formal-methods
---

**Category:** Quality Attributes · **Areas:** all

## Description

## Category
quality-attribute

## Areas
all

## Boundary

This concern owns precise behavioral specifications and the assurance justified
by analyzing them. It makes critical state, rules, transitions and assumptions
explicit, and connects analysis results to implementation evidence.

Requirements and domain concerns own what the system must do. Architecture and
ADRs own system choices; Contracts own exact shared interfaces. Formal properties
derive from those authorities. A contradiction requires reconciliation, not
silently replacing a requirement with whichever property the checker can pass.

`concurrency-model` owns execution primitives, synchronization and bounds;
`testing` owns test strategy; `verification` owns observed completion evidence.
Formal analysis complements all three. A model result cannot establish that
the running implementation behaves like the model.

## Components

- **Behavioral specification**: state, initial conditions, allowed transitions,
  preconditions/postconditions and properties with stable identifiers.
- **Safety**: what must never happen; **liveness**: what must eventually happen,
  with environmental and scheduling/fairness assumptions stated separately.
- **Analysis**: reproducible model checking, constraint solving or checked
  proofs, selected for the risk and scope.
- **Correspondence**: model elements mapped to implementation locations,
  enforcing mechanisms and tests; residual gaps explicitly recorded.

## Constraints

### Choose rigor per affected slice

Record scope, risk, owner and one level in existing Project Concerns fields:

| Level | Required evidence | Permitted claim |
|---|---|---|
| Precise specification | Reviewed states/transitions/properties and assumptions | Behavior is specified; no machine-checked assurance |
| Executable analysis | Executable model, configuration and completed analysis | Named properties checked under the recorded model, assumptions and bounds |
| Deductive proof | Formal statements, proof artifacts and completed proof-checker run | Named obligations proved under the recorded logic and assumptions |

Precise specification may be useful without an analyzer. Raising the level is
a scoped decision, not a universal requirement. Affected slices must meet their
chosen level; unaffected slices retain the context and record why no analysis
applies. Do not require analyzer runs for those slices.

### Properties and results are bounded by their assumptions

Name state, initialization, transitions, excluded behavior, abstraction,
analysis bounds and environmental assumptions. Liveness must state fairness
(which enabled actions must eventually run), availability and time assumptions.
Do not infer liveness from a safety check or a finite trace enumeration.

Separate observed property violation, completed bounded check, checked proof,
and unknown/incomplete/error. Timeout, resource exhaustion, unsupported checks,
or unchecked proof obligations are not passes. A bounded absence of
counterexamples is not an unrestricted proof.

### Check the model can express the intended behavior

Require reachable witnesses for meaningful success and relevant failure/recovery
scenarios. Contradictory assumptions or an unreachable success transition can
make properties hold vacuously. Deliberately weaken a guard or property-relevant
mechanism and confirm the analyzer reports the intended violation, with a
replayable counterexample when supported. A tool crash is not a negative control.
For deductive work, check assumption consistency and representative valid cases;
identify unsupported negative controls as reviewed limitations.

### Keep analysis and implementation evidence connected

For every adopted property, map model state/actions to code, enforcement and
tests. Mark missing correspondence as a gap. Convert useful counterexamples
into implementation regressions where applicable; derived tests supplement
the implementation check, they do not prove refinement by themselves.

Record source/config revision or digest, tool/version, exact command, property
coverage, bounds, result and counterexamples. Changes to requirements, model,
assumptions, configuration, tool version or mapped code invalidate affected
evidence until reviewed and rechecked. Verification still requires its own
running-system evidence. Illustrative models carry no production assurance.

## Drift Signals (anti-patterns to reject in review)

- An informal state diagram called a machine-checked specification.
- A green bounded check reported as proof of production correctness.
- Fairness assumed silently, or safety enumeration presented as liveness proof.
- Properties pass only because success/recovery is unreachable.
- A broken variant crashes instead of producing its intended violation.
- A verified model has no reviewed implementation correspondence.
- Evidence refers to older properties, assumptions, tool/config or mapped code.
- Every concurrent feature is forced to adopt heavyweight proof tooling.
- An unaffected slice is blocked on an analyzer despite recorded exclusion.

## When to use

Select for a bounded slice when both signals exist: (1) correctness depends on
interacting states, event ordering or non-trivial rule combinations, and (2) a
violation has material cost or recurring defects show ordinary examples are
insufficient. Examples include lease/fencing protocols, financial conservation,
authorization combinations, coordination and retry/idempotency rules. An
explicit assurance requirement is also a selection signal.

Concurrency alone does not require selection. Skip routine CRUD, presentation,
static sites and straightforward sequential behavior without a critical rule
or assurance need. For an existing project propose adoption; do not silently
rewrite its concern selection. This is composable and has no exclusive slot.
Select tools per project; HELIX installs no solver or proof assistant.

## Artifact Impact

- FEAT: critical behavioral properties and their requirement authority, where applicable
- ADR: selected rigor/method, rationale, assumptions and any scoped exception
- TD: specification, analysis scope/evidence and implementation correspondence
- TEST_PLAN: derived tests, positive witnesses, negative controls and analysis commands for affected slices
- IMPLEMENTATION_PLAN: sequence modeling and enforcement before dependent readiness claims
- RUNBOOK: operational assumptions and response to violations, only for deployed affected behavior

## ADR References

Record costly assurance/tool choices and exceptions in the adopting project's
ADR. A material uncertainty about expressiveness, feasibility or model/code
correspondence requires a bounded tech spike before dependent design commits
to that choice. See `workflows/references/formal-methods.md` for the checklist
and an executable, explicitly abstract lease example.

## Practices by activity

Agents working in any of these activities inherit the practices below through runtime work context, such as a DDx bead context digest.

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
