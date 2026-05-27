# Concern: Verification

## Category
quality-attribute

## Areas
all

## Boundary

This concern is the **evidence gate**, not a second test strategy. Three
distinct concerns own three distinct things, and `verification` must not
duplicate the other two:

- **`testing`** owns *test strategy and discipline* — what to test, at which
  layer, with stubs over mocks and fakers over fixtures, and the
  always-pass/trace-to-AC rules.
- **`e2e-framework`** (the slot, default `e2e-playwright`) owns the *end-to-end
  tooling* — the browser runner, config, video/trace artifacts, and the
  run-core-flow gate.
- **`verification`** owns one thing the other two do not state: **work is NOT
  DONE until observed evidence of the running system exists.** It is the gate
  that refuses "I wrote the code and the unit tests pass" as a completion
  claim. It composes on top of `testing` and `e2e-framework`; it does not
  re-specify how to write tests or which e2e tool to use.

## Components

- **Re-review before done**: an adversarial second pass against the acceptance
  criteria and integration risks — not a self-affirming "looks good to me".
- **Whole-stack exercise**: the real user flows are driven against the running
  system (the full stack from user action to datastore and back), not a
  green unit suite standing in for the system.
- **Recorded evidence artifacts**: the concrete observations that prove the
  work runs — captured, not asserted from memory.
- **Verify-don't-trust**: never report a result that was not observed.

## Constraints

### Not done until observed evidence exists

- "Done" means the whole stack was exercised with **recorded evidence**, not
  that a unit suite is green. A passing unit layer is necessary, not
  sufficient.
- Before claiming completion, an agent must produce the evidence artifacts in
  `practices.md`: the command run + its exit status, the target URL/env, the
  core flows exercised, and a short re-review checklist against the ACs and
  integration risks.
- This catches **locally-correct / globally-wrong** work: components that pass
  in isolation but fail when composed into the running system.

### Verify, don't trust (extends testing's always-pass and measure's M4)

- Never assert a result you did not observe. A "complete", a "200 OK", a
  "tests pass", or a coverage figure must come from an actual run you watched
  finish, not from expectation. This extends the measure action's
  verify-don't-trust rule (it re-runs gates itself rather than accepting a
  self-reported "complete") from the metric layer to the completion claim.
- An autonomous pass can report success and still have died mid-run. Treat a
  self-reported "done" as a hypothesis to verify, never as evidence.

### Re-review is adversarial, not confirmatory

- The re-review pass actively looks for the ways the change is wrong:
  unhandled error paths, untouched integration seams, ACs that the
  implementation skirts rather than satisfies.
- Re-review happens against the governing acceptance criteria and the
  integration risks the change touches — not against the author's own mental
  model of "what I meant to build".

## Exceptions (honored in concern-resolution and at the gate)

The evidence gate adapts to work where full-stack e2e is not the right proof.
Record which exception applies and why:

- **Library / docs-only / non-buildable work** — there is no running stack to
  exercise. The evidence is the layer that *does* exist: the library's tests
  run green (with their command + exit status recorded), or the docs build /
  link-check passes. Full-stack e2e is not required and its absence is not a
  gap.
- **Products where full-stack e2e is genuinely infeasible** — e.g. the system
  depends on an external service that cannot be stood up locally, or hardware
  that cannot be emulated. Record the specific reason, and substitute the
  strongest observable evidence available (integration against a stub of the
  boundary, a recorded manual run). An unrecorded "e2e is hard" is not an
  exception — the reason must be written down.

A recorded exception relaxes *which* evidence is required, never the
verify-don't-trust rule: even under an exception, no result is asserted that
was not observed.

## Drift Signals (anti-patterns to reject in review)

- "Done" / "complete" claimed with only a unit suite green and no
  whole-stack run → not done; produce the evidence artifacts
- A reported result (status code, flow outcome, metric) with no recorded run
  behind it → verify-don't-trust violation; re-run and observe
- A self-review that only confirms the author's intent → replace with an
  adversarial re-review against ACs + integration risks
- "e2e is infeasible" with no recorded reason → record the reason or produce
  the evidence
- Components pass in isolation, system never exercised end-to-end →
  locally-correct / globally-wrong; exercise the running stack

## When to use

Every **buildable** product, regardless of language, framework, or domain.
High autonomy auto-selects this concern for buildable products (see
`workflows/references/concern-resolution.md`), honoring the
exceptions above. Compose with `testing` (strategy) and the `e2e-framework`
slot (tooling); `verification` adds the evidence gate on top — it does not
replace either.

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- TEST_PLAN: whole-stack evidence gate per AC — command + exit status, target env, flows, adversarial re-review
- ADR: any recorded exception (library/docs-only or full-stack-e2e-infeasible) and its substitute evidence

## ADR References
