---
title: "Scope Discipline"
slug: scope-discipline
generated: true
aliases:
  - /reference/glossary/concerns/scope-discipline
---

**Category:** Quality Attributes · **Areas:** all

## Description

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

## Practices by activity

Agents working in any of these activities inherit the practices below through runtime work context, such as a DDx bead context digest.

These practices define the **scope gate**: the change is the right size — neither
hollow (a placeholder claimed done) nor padded (scope nobody requested). They sit
beside `verification` (which proves the system runs) and do not restate it.

## Design

- State the scope boundary for the work item before building: the capabilities
  the acceptance criteria require (in scope) and the **explicit non-goals** the
  change must not build. Record it in the implementation plan.
- If a phase boundary is genuinely needed (a deliberate stub with a follow-up
  item), name it now — which path is phased, which follow-up item tracks it, and
  which acceptance criteria it does **not** satisfy.

## Implementation

- Build to the acceptance criteria — not short of them, not past them.
- No incompleteness marker on a path an acceptance criterion exercises: no stub,
  no `unimplemented!()` / `panic!("not implemented")` / `NotImplementedError`, no
  `TODO`/`FIXME` standing in for unfinished behavior, no empty body returning a
  placeholder.
- No unrequested scope: do not add a feature, option, abstraction layer, or
  configuration surface the criteria did not ask for. "Might be useful later" is
  a follow-up item, not this change.
- Pre-release: cut the old path in the same change that replaces it. Do not add
  backward-compat aliases, fallbacks, or deprecation shims for consumers that do
  not exist yet.
- Keep the diff scoped to the work item. If a tree-wide fix is warranted, file it
  as its own item rather than sweeping it in.

## The scope gate (before claiming "done")

A completion claim is **incomplete** if any of these hold:

1. **Hollow path** — a path covered by a satisfied-claimed acceptance criterion
   contains an incompleteness marker. Resolve by finishing it, or by leaving the
   criterion honestly unsatisfied and tracked (never both done and stubbed).
2. **Unrequested scope** — the change builds a feature, option, or abstraction no
   acceptance criterion asked for. Resolve by removing it (or filing it as its own
   governed item if it is worth doing).
3. **Unrecorded scope reduction** — a requested capability shipped narrowed
   (disabled, read-only) with no recorded tradeoff. Resolve by restoring it or
   recording the reduction in `concerns.md` / an ADR.
4. **Off-scope blast radius** — the diff edits files outside the work item's
   stated scope. Resolve by reverting the off-scope edits.

Phased placeholders and requested scope reductions are allowed only as the
**recorded exceptions** in `concern.md` — a named stub with a tracked follow-up
item that no satisfied criterion depends on, or a scope reduction with a written
reason. An unrecorded stub or silent narrowing is a defect, not a phase.

## Verify against the boundary, don't trust the summary

This is the `verification` concern's verify-don't-trust rule applied to *size*
rather than *behavior*: verification asks whether the stack ran; scope-discipline
asks whether the change is the right size.

- An autonomous pass will describe its own output as "complete". Check the diff
  against the stated scope boundary rather than trusting the summary: does every
  satisfied criterion run real code, and did the change build only what was asked?
- Words the change uses about itself — "facade", "for now", "placeholder",
  "stubbed", "wire up later" — are signals to inspect the path, not to accept.

## Quality Gates

- Zero incompleteness markers (stub / `unimplemented!` / unfinished-`TODO` /
  placeholder body) on paths that satisfied acceptance criteria exercise — or a
  recorded phased-placeholder exception covering each.
- Zero unrequested features, options, or abstraction surfaces beyond the
  acceptance criteria.
- No pre-release legacy-compat shim, alias, or fallback without a released
  consumer.
- The change's diff is contained to the work item's stated scope.
