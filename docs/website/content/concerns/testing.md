---
title: "Testing"
slug: testing
generated: true
aliases:
  - /reference/glossary/concerns/testing
---

**Category:** Quality Attributes · **Areas:** all

## Description

## Category
quality-attribute

## Areas
all

## Components

- **Philosophy**: Tests exist to find bugs in the code, not to prove it works
- **Strategy**: Multi-layer coverage with stubs over mocks, fake data over fixtures
- **Boundary testing**: Property-based, fuzz, chaos, and performance ratchets
- **Traceability**: Tests tied to acceptance criteria from governing artifacts

## Constraints

### Tests must always pass

- Investigate failures against governing intent; either the code or the test
  may be wrong. Do not preserve an obsolete mechanism solely to satisfy a test.
- Revise or consolidate tests coupled to superseded implementation details.
  Retire redundant tests when meaningful coverage remains, and remove tests for
  intentionally retired behavior with the authorized requirement change. When a
  retired test is mapped to an acceptance criterion, update its Story Test Plan
  row to the test that still covers it.
- Never skip, disable, or delete a test to hide a regression. `.skip` and
  `@Ignore` cannot substitute for resolving a failure.
- Never commit with failing tests. If you cannot fix the failure, leave the
  code uncommitted and report the blocker.
- Flaky tests are bugs. Investigate and fix the non-determinism (race
  conditions, time-dependence, shared state) — do not retry-loop around them.

### Tests identify issues in the code

- Tests encode expected behavior under governing requirements and can be
  revised when evidence shows they encode an unnecessary mechanism.
- Assess whether assertions detect a meaningful failure. A regression test can
  remain valuable without having failed in normal runs; test count and failure
  history alone do not establish value.
- Prioritize testing behavior (what the system does) over implementation
  (how it does it). Tests that break when you refactor internals without
  changing behavior are over-coupled.

### Tests trace to acceptance criteria

- Every acceptance criterion in a user story or feature spec should have at
  least one test that exercises it.
- Test names should read as behavior specifications: "creates an invoice
  when all line items are valid" not "test_create_invoice_3".
- Untested acceptance criteria are unverified requirements — they belong in
  the alignment review gap register.

### Stubs over mocks

- Prefer stubs (canned return values) over mocks (call-sequence assertions).
  Stubs test behavior; mocks test implementation.
- Use real implementations where practical: real databases via testcontainers
  or Docker Compose, real HTTP via local servers, real file systems via temp
  directories.
- Mock only at true system boundaries: third-party APIs, payment processors,
  email services, external auth providers.
- Never mock the thing you are testing. If you are testing a service, give it
  real (or stubbed) dependencies, not a mocked version of itself.

### Fake data over fixtures

- Generate test data with fakers (`@faker-js/faker`, `fake`, `proptest`
  strategies, `quickcheck` generators) — not static JSON fixtures.
- Fake data exposes hidden assumptions: hardcoded IDs, implicit ordering,
  length-dependent logic, locale-specific formatting.
- Seed fakers deterministically per test for reproducibility. Print the seed
  on failure so the exact data can be replayed.
- Factory functions over raw constructors: `createTestInvoice({ status: "draft" })`
  with defaults for everything not under test.

### Multi-layer coverage

- **Unit tests**: Pure functions, value objects, schema validation, business
  rules. Fast, no I/O.
- **Integration tests**: Service + real database, HTTP handler + real router,
  queue consumer + real queue. Test the contracts between components.
- **E2E tests**: Full stack from user action to database and back. Cover
  critical user journeys, not every edge case.
- **Contract tests**: API schema validation between services. Ensure
  producer and consumer agree on shape and semantics.
- Test the right things at the right layer. Do not duplicate unit-level
  assertions in E2E tests.

### Boundary testing

- **Property-based testing**: Define invariants ("output is always sorted",
  "round-trip encode/decode is identity") and let the framework generate
  hundreds of random inputs. Use `proptest`, `fast-check`, `hypothesis`, or
  `quickcheck`.
- **Fuzz testing**: Feed malformed, random, and adversarial inputs to
  parsers, validators, and serializers. Fuzz tests find crashes, panics,
  and undefined behavior that unit tests miss.
- **Chaos testing**: Inject failures (network partitions, disk full, OOM,
  slow responses, clock skew) into integration and E2E tests. Verify
  graceful degradation and recovery.
- **Performance ratchets**: Define quantitative floors for latency,
  throughput, memory, bundle size, or test duration. Commit floors to
  version control. CI fails if the metric regresses below the floor. See
  `workflows/ratchets.md` for the ratchet pattern.

## Drift Signals (anti-patterns to reject in review)

- `test.skip`, `.skip()`, `@Ignore`, `@Disabled` without a linked issue → remove or fix
- Mocking the database in integration tests → use a real database
- Mock-heavy tests that assert call order → replace with stubs and behavior assertions
- Static JSON fixture files → replace with factory functions using fakers
- Test named `test1`, `testHelper`, `it works` → rename to describe behavior
- `expect(true).toBe(true)` or tautological assertions → delete or replace with real assertion
- Commented-out tests → delete (git has the history)
- Retry loop around a flaky test → fix the flake
- No tests for a new feature → block the PR

## When to use

Every project. This concern is universal — it applies regardless of language,
framework, or domain. Compose with language-specific concerns
(`typescript-bun`, `rust-cargo`, etc.) for tooling-specific test practices.

## Artifact Impact

Apply these responsibilities in relevant existing artifacts or the acceptance
record. Concern selection alone does not require a new process document:
- TEST_PLAN: AC-class to primary-layer allocation, framework choice with cost, data strategy

## ADR References

## Practices by activity

Agents working in any of these activities inherit the practices below through runtime work context, such as a DDx bead context digest.

## Requirements (Frame activity)

- Every user story must have testable acceptance criteria
- Acceptance criteria must name observable outcomes. Use a failing test to
  establish a regression or new behavior when it supplies missing evidence;
  existing coverage may already verify a mechanical change or refactor.
- Non-functional requirements (latency, throughput, availability) must have
  measurable targets that become ratchet floors

## Verification scope

Choose verification from the in-scope requirements, claimed capability and
failure risk, not from a generic maturity checklist. For an initial public
interface, first prove an installed consumer can complete the promised core
workflow, including applicable rejection, authorization and data-integrity
behavior. Interface immaturity does not waive those checks.

Performance, chaos, cross-engine and independent-implementation campaigns are
release gates only when required by a governing criterion, an explicit support
claim, a concrete defect or a material failure risk. Otherwise defer them until
the usable interface is proven. Record that sequencing in the existing test or
implementation plan; do not invent a maturity artifact or weaken requirements.
A broad claim still requires broad proof; narrow the claim explicitly rather
than imply untested scale or interoperability is supported.

Inspect existing coverage and the affected system's actual operations before
adding tests or matrices. Boundary observations (generated SQL and query
measurements, network requests) can expose unnecessary mechanisms that passing
tests would preserve; remove those rather than test around them. Add tests for
distinct uncovered behavior or material failure risks. Weigh a test's fixtures,
helpers, runtime and maintenance against the distinct behavior it proves, and
prefer smaller verification at the layer that best detects the failure.

The strategy below applies where its behavior or risk is in scope. Periodic
campaigns are not a prerequisite for every implementation slice. Required
regression checks and the verification concern's observed-result gate remain.

## Design

- Identify test boundaries during design: what is unit-testable, what needs
  integration, what needs E2E
- Design for testability: dependency injection, pure functions, clear
  interfaces at system boundaries
- Each acceptance-criterion class maps to one primary layer
- Identify invariants for property-based testing during contract design
  ("this function is commutative", "serialization round-trips", "output
  length is bounded by input length")
- Identify failure modes for chaos testing: what happens when the database
  is slow, the queue is full, the external API returns 500

## Implementation

### Test structure
- One test file per module/component, co-located or in a parallel `test/`
  directory
- Test files named `<module>.test.<ext>` or `<module>_test.<ext>`
- Group related tests with `describe` / `context` / `mod tests`
- Keep each test focused on a meaningful behavior; related assertions may share
  one scenario when splitting would duplicate setup and evidence.

### Test names and requirement citations

Name the observable behavior and relevant condition or failure branch using
framework conventions: `TestClaim_RejectsAlreadyLeasedBead`,
`test_route_resolution_timeout_releases_lease`, or
`it("rejects a duplicate submission while pending", ...)`. Avoid vague names
such as `test_success`, `test_AC1` or names of private implementation steps.
Parameterized cases identify the condition in their reported case name.

Use stable story AC IDs in canonical source citations, for example:

```go
// @covers US-001-AC2
func TestClaim_RejectsAlreadyLeasedBead(t *testing.T) { /* assert outcome */ }
```

Prefer comments/annotations to putting IDs into function names. Existing valid
citations in test bodies, names or doc comments remain valid; no bulk rename is
required. A test covering multiple criteria cites each with its own `@covers`
tag. Non-story requirements use their existing IDs and project citation contract;
do not invent story IDs. The Story Test Plan owns the mapping, not another file.
Names and tags help discover coverage; review still checks meaningful assertions,
required runtime layers and observed passing results. See the `verification`
practices for run provenance and conditional supplemental observations.

### Test data
- Factory functions with sensible defaults:
  ```
  createTestUser({ role: "admin" })  // everything else has defaults
  ```
- Faker-generated values for strings, numbers, dates, emails, addresses
- Deterministic seeds: set per-test seed, log on failure for replay
- No shared mutable state between tests — each test sets up its own data

### Stubs and boundaries
- Stub at system boundaries: external HTTP APIs, email, SMS, payment
- Use real implementations for internal boundaries: real database, real
  queue, real file system (via temp directories)
- Dependency injection for swappable dependencies — not monkey-patching
  or module-level mocking
- For HTTP stubs: record/replay from real responses where possible, then
  maintain the fixtures as contract snapshots

### Property-based testing
- Define properties as pure boolean functions: `(input) => invariant(fn(input))`
- Select properties that hold for the required behavior, such as round-trip or
  idempotency. Do not generate properties or suites merely to fill categories.
- Shrink failing cases to minimal reproduction
- Run property tests in CI with enough iterations (100+ per property)

### Fuzz testing
- Fuzz all parsers, deserializers, and user-input validators
- Fuzz with both random byte sequences and structured mutation
- Corpus: seed with real-world examples, edge cases, and prior crash inputs
- Run fuzz campaigns periodically (nightly CI or dedicated fuzz job) — not
  necessarily on every PR

### Chaos testing
- Start with timeout and retry behavior: inject latency into stubs, verify
  the system retries or degrades gracefully
- Test circuit breakers: stub returns errors → verify fallback activates
- Test data integrity under failure: kill the process mid-transaction →
  verify no partial writes
- Scope chaos to integration/E2E tests — unit tests should be deterministic

### Performance ratchets
- Define floors for key metrics: P95 latency, test suite duration, bundle
  size, memory usage, query count
- Store floors in a committed file (e.g., `.ratchets.json`, `ratchets.toml`)
- CI measures and compares against floor; fails on regression
- Auto-bump floor when measured value exceeds it by the defined margin
- See `workflows/ratchets.md` for the full ratchet pattern and override
  protocol

## Testing pyramid

| Layer | What | Isolation |
|-------|------|-----------|
| Unit | Pure logic, schemas, value objects | Full |
| Integration | Service + real deps, API + DB | Partial |
| E2E | Full user journey, browser or CLI | None |
| Property | Invariants over random input | Full |
| Fuzz | Crash/panic discovery | Full |
| Chaos | Failure resilience | Partial |

## Surface → real-path harness

Choose the harness for the behavior and risk being verified. Changed user flows
and runtime boundaries need real-path evidence, including applicable material
failure branches. Internal criteria may be verified at a narrower layer; do not
repeat them through every surface or invent a guard branch for each criterion.

| Surface | Real-path harness |
|---|---|
| Web UI (client-rendered) | Playwright (the `e2e-framework` slot, default `e2e-playwright`) |
| Server-rendered web | HTTP request + HTML assertion against the live server |
| HTTP API / webhook | request client (curl/fetch): assert status code **and** body contract, including malformed / empty / unauthorized input |
| CLI | shell / `expect` driving the real binary, asserting exit status + output |
| TUI | `tmux` send-keys + capture-pane assertions |
| Backend job / worker / scheduler | integration test driving the real entry point (not a re-implementation) |

Playwright is the web filler, **not** the universal verifier — a CLI exercised
only by unit tests, or an API whose malformed-input branch is never POSTed, is
not verified.

## Quality Gates

- All tests pass — no exceptions, no skips without linked issues
- Performance ratchet: key metrics ≥ committed floor
- New features have tests tracing to acceptance criteria
- Property tests cover selected invariants where they add meaningful evidence
- No test mocks internal implementation — only system boundaries
