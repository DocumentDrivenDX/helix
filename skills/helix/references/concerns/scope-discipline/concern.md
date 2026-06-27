# Concern: Scope Discipline

## Category
quality-attribute

## Areas
all

## Boundary

This concern is the **scope gate**: it refuses work that is the wrong *size* —
either hollow (under-delivered but claimed done) or padded (over-delivered beyond
what was requested). It is the methodology home for YAGNI / KISS / "do only what
was asked".

It composes with `verification` and does not duplicate it:

- **`verification`** owns *did it run* — observed evidence that the built system
  works end-to-end.
- **`scope-discipline`** owns *is it the right size* — the change delivers exactly
  what the governing acceptance criteria asked for, with no hollow placeholders
  standing in for unfinished work and no unrequested scope bolted on.

A change can pass `verification` (the happy path runs) and still fail
`scope-discipline` (it shipped a stubbed branch, or it gold-plated three features
nobody asked for). Both gates are required.

## Components

- **No hollow completeness**: the path the acceptance criteria exercise contains
  no stubs, `TODO`/`FIXME`-as-work-marker, `unimplemented!()`/`panic!("not
  implemented")`/`NotImplementedError`, empty handler bodies, or "facade"
  wrappers with nothing behind them.
- **No gold-plating**: no feature, abstraction, configuration surface, or
  refactor the work item did not request — built because it "might be useful" or
  "while we're here".
- **No pre-release legacy shims**: backward-compat aliases, fallbacks, and
  deprecation shims are not added for consumers that do not exist yet.
- **Bounded blast radius**: the change touches the files the work item scopes,
  not an incidental codemod sweep across the tree.
- **Recorded scope**: what is in scope and what is explicitly a non-goal is
  written down, so "done" is measured against a stated boundary, not a mood.

## Constraints

### Build exactly what was requested — no less

- A work item is **not done** when the path its acceptance criteria exercise
  still contains an incompleteness marker (stub, `unimplemented!`, `TODO`/`FIXME`
  describing unfinished behavior, empty body returning a placeholder). Hollow
  completeness — code that compiles and a unit asserts the stub — is the failure
  this catches.
- "Facade", "for now", "placeholder", "wire up later", and "stubbed for the
  demo" describing **shipped, done-claimed** work are completion-honesty defects.
  Either finish the implementation, or leave the criterion honestly unsatisfied
  and tracked — never claim done over a placeholder.

### Build exactly what was requested — no more

- Do not add features, options, abstraction layers, or configuration the
  governing acceptance criteria did not ask for. Speculative generality is scope
  the operator did not approve; it is removed, not justified after the fact.
- Do not retreat from a requested capability under an unrequested constraint
  (e.g. shipping a flow read-only "for security" when the AC requires writes).
  A capability the AC requires is in scope; narrowing it is a scope change that
  needs an explicit, recorded tradeoff — not a silent default.
- Pre-release software has no released consumers: do not add legacy-compatibility
  shims, aliases, or fallbacks "to be safe". Cut the old path in the same change
  that introduces the new one.

### Bounded blast radius

- The diff is scoped to the work item. A change that rewrites or sweeps files
  outside the item's stated scope (a tree-wide `sed`, an opportunistic rename)
  is reverted to scope; the off-scope edit becomes its own tracked item if it is
  worth doing.

## Exceptions (honored in concern-resolution and at the gate)

Phased delivery is legitimate when it is **recorded**, not improvised:

- **Explicitly phased placeholder** — a stub is acceptable only when it is (1)
  named in the implementation plan as a deliberate phase boundary, (2) tracked by
  a follow-up work item, and (3) **not** covered by an acceptance criterion that
  is claimed satisfied. An unrecorded stub on a done-claimed path is a defect, not
  a phase.
- **Requested scope reduction** — narrowing a capability is allowed when the
  operator requested it or an acceptance constraint forces it, and the reduction
  is recorded (in `concerns.md` / an ADR) with its reason. An unrecorded "I made
  it read-only for safety" is not an exception.

A recorded exception relaxes *what* is in scope, never the honesty rule: a
placeholder is never reported as a satisfied criterion.

## Drift Signals (anti-patterns to reject in review)

- Stub / `unimplemented!()` / `TODO`-as-unfinished-work on a path an acceptance
  criterion claims to satisfy → hollow completeness; finish it or stop claiming
  done.
- "facade" / "for now" / "placeholder" / "wire up later" describing shipped work
  → completion-honesty defect; finish or track-and-don't-claim.
- A legacy-compat alias, fallback, or shim added with no released consumer →
  pre-release gold-plating; cut it and the old path together.
- A feature, option, or abstraction the acceptance criteria never asked for →
  YAGNI violation; remove it.
- A requested capability shipped disabled / read-only "for security" with no
  recorded tradeoff → unrequested scope retreat; restore it or record the change.
- A diff that edits files outside the work item's stated scope (tree-wide sweep,
  drive-by rename) → blast-radius; revert to scope.

## When to use

Every **buildable** implementation work item, regardless of language, framework,
or domain. High autonomy auto-selects this concern for buildable products (see
`workflows/references/concern-resolution.md`), honoring the exceptions above.
Compose with `verification` (evidence that it runs) — `scope-discipline` adds the
size gate on top; it does not replace verification's evidence requirement.

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- IMPLEMENTATION_PLAN: the scope boundary — what is in scope, and the explicit non-goals the change must not build
- TEST_PLAN: no acceptance criterion is satisfied by a stubbed / placeholder path; incompleteness markers on AC-exercised code are a blocking finding
- ADR: any recorded exception (explicitly phased placeholder, or requested scope reduction) and its reason

## ADR References
