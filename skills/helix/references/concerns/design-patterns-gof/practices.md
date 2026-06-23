# Practices: Design Patterns (Gang of Four)

These practices govern **when and how** a GoF pattern is applied so the codebase
gains a shared vocabulary without acquiring speculative indirection. They sit
beside `domain-driven-design` (domain semantics), `onion-architecture` (layering),
and `enterprise-integration-patterns` (cross-system messaging) — they do not
restate those concerns. Their one job is to keep patterns **earned, named, and
simple**.

## Choosing a pattern

- A pattern MUST be introduced only against a **named recurring problem** that
  exists now — duplication to remove, or a real variability/extension point — and
  the **intent MUST be recorded** (the catalog row in `concern.md` it satisfies,
  in a code comment, the PR/work-item, or an ADR).
- The pattern chosen MUST match the recorded trigger (use the intent table): use
  Strategy for interchangeable algorithms, Adapter for an interface mismatch,
  Observer for one-to-many change notification, and so on — not whichever pattern
  is most familiar.
- You SHOULD prefer the **simplest construct** that solves the problem (a plain
  function, a direct call, a `switch`, a value) and escalate to a pattern only
  when a concrete force demands the indirection. KISS/YAGNI win ties.
- You SHOULD NOT introduce a pattern "for future flexibility" before the second
  concrete use exists. Refactor *to* the pattern when the recurrence appears, not
  in anticipation of it.

## Applying a pattern

- A pattern that is introduced MUST **remove duplication or absorb a real
  variability point** — indirection that does neither is a finding, not a feature.
- The implementation SHOULD use the host language's idiomatic form of the pattern
  (e.g. a first-class function or closure for a single-method Strategy; a context
  manager / `with`-block where the language offers one) rather than a verbose
  textbook transliteration. The vocabulary matters; the boilerplate does not.
- A pattern's name SHOULD appear where it aids the reader (type/class name, a
  brief comment) so the shared vocabulary is visible — but the name MUST reflect
  the mechanic actually present (no "StrategyFactory" with a single hardcoded
  branch).

## Staying in your lane

- When the construct carries business meaning, the **domain role** (Factory,
  Repository, Domain Event) MUST be named per `domain-driven-design`; GoF
  vocabulary describes only the implementing mechanic. A GoF pattern MUST NOT
  invent a domain concept the ubiquitous language does not name.
- A GoF pattern MUST stay **within a layer**; it MUST NOT be promoted to the
  application's macro architecture (that is `onion-architecture`) nor restate the
  dependency rule.
- A collaboration that crosses a **process/system boundary** MUST be treated as
  `enterprise-integration-patterns`, not modeled as an intra-process GoF Mediator
  or Adapter.

## Constraining global state

- **Singleton** SHOULD be avoided as ambient global state. The single instance
  SHOULD be passed via dependency injection / composition rather than reached for
  statically. Where exactly-one is a genuine enforced invariant, the Singleton
  MUST be justified with a recorded reason.

## Quality Gates

- Every pattern present traces to a **named recurring problem with recorded
  intent** — no speculative pattern survives review.
- Every pattern present **removes duplication or absorbs a real variability
  point**; indirection that does neither is removed (collapsed to the simplest
  construct).
- Pattern names match the mechanic actually implemented — no misnamed or
  single-branch "patterns".
- No GoF pattern stands in for domain modeling, macro layering, or cross-system
  messaging (those route to `domain-driven-design`, `onion-architecture`,
  `enterprise-integration-patterns`).
- No Singleton used as ambient global state; the single instance is injected, or
  a true exactly-one invariant is recorded.
