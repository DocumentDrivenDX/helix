# Formal Methods Adoption

Apply this reference when `formal-methods` is selected for a named slice. It is
a checklist for adoption, not a new artifact type or mandatory activity for
every project. The owning technical design holds the specification; keep the
executable model/config/proofs in its referenced repository directory.

## Scope and Authority

Record the risk, affected slice, owner, chosen rigor and exclusions in existing
Project Concerns Why Active / Key Practices fields. Carry a concise scope/rigor
note through Project Overrides when downstream context needs it. A selected
concern with `areas: all` reaches every work area; each work item's acceptance
and evidence must either realize the affected obligation or record why the
slice is unaffected. The latter needs no analyzer/proof run.

For the heading-and-bullet compact-context format, a scope override can be:

```markdown
## Active Concerns
- formal-methods

## Project Overrides
### formal-methods
- Scope lease lifecycle; executable analysis; authority the lease technical design.
```

Use the adopting runtime's supported selection/override representation. Table
authoring and bullet context parsing are different surfaces; verify the runtime
actually carries the scope note, rather than assuming every parser reads both.

Properties derive from feature/story requirements and domain rules. Reference
their authority; do not silently strengthen or weaken it. Contracts own exact
shared API/event/schema/CLI semantics. Technical designs may formalize internal
behavior and reference those Contracts, without copying normative wire surfaces.
System-wide models are referenced by relevant designs; a dedicated artifact
type is deferred until independent lifecycle/traceability needs justify one.

## Specification Checklist

1. Scope, critical risks, requirement references and property identifiers.
2. State domains and initial conditions, including invalid/absent state.
3. Transitions: actor, guard/precondition, atomicity, effect/postcondition and
   rejected transitions. Model failures, retries and recovery where relevant.
4. Safety properties (never) and liveness properties (eventually), explicitly
   separate. State fairness, environmental availability and timing assumptions.
5. Abstraction: omitted behavior, finite domains, temporal/depth/resource bounds
   and the argument for preserving the properties of interest.
6. Chosen assurance level and method, owned model/config/proof files, commands
   and results. Distinguish reviewed specification from mechanical assurance.
7. Non-vacuity: reachable success and relevant recovery/failure scenarios,
   assumption consistency, targeted negative controls or reviewed limitations.
8. Correspondence and residual risks, with implementation evidence still needed.

## Evidence Record

Use an existing design/verification-evidence location. For each analysis record:

| Field | Required content |
|---|---|
| Identity | Requirement/property IDs; model, configuration and mapped source revisions or digests |
| Tool | Tool/version and relevant runtime/dependency versions |
| Reproduction | Exact command, environment, complete config and input references |
| Scope | Domains, bounds, assumptions, abstractions, exclusions and property coverage |
| Outcome | Reviewed specification, completed bounded check, checked proof, violation, or unknown/incomplete/error |
| Non-vacuity | Reachable witnesses, negative-control result and replay evidence where supported |
| Correspondence | Code/enforcement/test mapping and reviewed residual gaps |
| Review | Reviewer, decision, limitations, and changes that require rechecking |

A timeout or resource cutoff leaves unchecked obligations unknown. A completed
check applies only to the explored model/configuration; do not imply unrestricted
proof or production correctness. Proofs apply under stated logic and assumptions.
Store counterexample traces and preserve stale results as history.

## Correspondence Checklist

| Property / model element | Requirement authority | Code / enforcing mechanism | Tests / observed evidence | Gap or reviewed limitation |
|---|---|---|---|---|
| [Property ID, state or action] | [Feature/story/Contract reference] | [Actual file/symbol/revision] | [Named test and result] | [Unmapped, abstraction or residual risk] |

Review whether modeled atomic actions match real transaction/lock boundaries,
whether guards use authoritative state, and whether failures between operations
are represented. A test derived from a model is useful but does not by itself
establish that every implementation behavior refines that model.

## Methods and Tool Choice

Use the smallest method that addresses the critical question. State machines
and contracts can sharpen prose without machine checking. TLA+/TLC can check
models of state-transition specifications; Alloy can find instances and
counterexamples to relational/temporal assertions under recorded scopes. These
are examples, not dependencies or exclusive slots. Pin the actual tool and
configuration chosen by the adopting project. [TLC model documentation](https://nightly.tlapl.us/doc/model/model.html),
[Alloy language specification](https://alloytools.org/spec.html).

Deductive proof is appropriate when a bounded search cannot support the required
claim and checked proofs are feasible. Record the proof system, assumptions and
unchecked obligations; do not call an informal argument a checked proof.

## Lease-Lifecycle Pilot

The [abstract lease example](formal-methods/README.md) ships a standard-library
Python state explorer and deliberate broken variants. It models two workers,
one bead and two claims. It checks safety within that finite model and records
reachable successful landing and timeout/reclaim/late-return witnesses.

The example is inspired by worker leases; it does not inspect DDx code or prove
DDx correct. Production clocks, crashes, filesystem locks, external side effects,
watchdog fairness and repeated-wedge parking remain outside its model. Liveness
requires separate analysis; eventual timeout release is an unverified obligation.

For a real adoption, first map the lease/token authority, timeout and landing
transactions to code. Derive regressions from the stale-return counterexample,
exercise the actual system, and model additional failure windows as needed.
Measure modeling effort, explored states, analysis runtime, actionable gaps and
regressions against ordinary design/review effort. Retain the method when its
findings justify maintenance cost; do not present hypothetical savings as results.
