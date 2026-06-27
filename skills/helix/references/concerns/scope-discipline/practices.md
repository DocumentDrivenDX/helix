# Practices: Scope Discipline

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
