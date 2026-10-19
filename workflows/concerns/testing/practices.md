# Practices: Testing

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

The harness that *proves* a behavior depends on the surface it lives on. Drive
each acceptance criterion's real path **and its guard/negative branch** through
the harness its surface dictates. (Choosing the harness is a testing-strategy
decision; the `verification` concern's evidence gate only refuses "done" without
the resulting running-system evidence.)

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
