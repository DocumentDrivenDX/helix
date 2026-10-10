# Concern: Formal Methods

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
