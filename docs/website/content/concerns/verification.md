---
title: "Verification"
slug: verification
generated: true
aliases:
  - /reference/glossary/concerns/verification
---

**Category:** Quality Attributes · **Areas:** all

## Description

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
- **Requirement-linked results**: existing mappings and test-source citations
  connect criteria to observed run reports. Supplemental observations cover
  proof gaps outside the normal reporting path; no extra file is mandatory.
- **Verify-don't-trust**: never report a result that was not observed.

## Constraints

### Not done until observed evidence exists

- "Done" means the whole stack was exercised with **recorded evidence**, not
  that a unit suite is green. A passing unit layer is necessary, not
  sufficient.
- Before claiming completion, an agent must produce the evidence artifacts in
  `practices.md`: the command run + its exit status, the target URL/env, and the
  core flows exercised, including each guard branch observed. Existing reports
  carry these facts and the tested revision; link them from the existing mapping
  or acceptance record. A cited test alone is not proof it ran and passed.
- If the change has a named downstream consumer in another repo, "done"
  requires evidence that the consumer pulled the change and its integration was
  exercised. Local gate-green alone is not enough.
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
- An agent/network-facing surface (MCP server, OAuth/SSO login, a remote
  endpoint) declared done on unit tests, with no real client ever completing the
  handshake/login against the real address → not done; the runtime boundary is
  exactly where unit-green hides the defect (the connection, the token exchange,
  the cert, localhost-vs-real-host). Drive a real client end-to-end before "done".
- A change with a named downstream consumer declared done on local gate-green
  alone, with no observed downstream-consumer evidence → not done; the consumer
  must pull the change and exercise the integration.

## When to use

Every **buildable** product, regardless of language, framework, or domain.
High autonomy auto-selects this concern for buildable products (see
`workflows/references/concern-resolution.md`), honoring the
exceptions above. Compose with `testing` (strategy) and the `e2e-framework`
slot (tooling); `verification` adds the evidence gate on top — it does not
replace either.

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- STORY_TEST_PLAN: existing AC/test mapping and citations link to observed run
  results; Notes/Executable Proof link supplemental observations only for proof
  gaps. Other requirement types use their existing acceptance records.
- TEST_PLAN: the layer allocation only
- IMPLEMENTATION_PLAN: scoped validation commands, run-result references and
  reviewed exceptions; no shared evidence file or duplicate mapping.

## ADR References

## Practices by activity

Agents working in any of these activities inherit the practices below through runtime work context, such as a DDx bead context digest.

Apply the evidence gate defined in `concern.md`.

## Plan the proof

Before Build, identify the change's core flows, integration seams, required
runtime harnesses and observable outcomes, including each governing acceptance
criterion's guard/negative branch. Plan any downstream-consumer exercise and
applicable exception/substitute proof now. Keep the running system reachable
with a start command and suitable seed data. Planned proof is not a passing run.

## Completion contract

Use the existing Story Test Plan's Acceptance Criteria Test Mapping, test-source
`@covers` citations and observed run reports. Other requirement types use their
existing acceptance records and stable IDs; do not create a second per-criterion
matrix. Test names follow `workflows/concerns/testing/practices.md`.

Before claiming completion, make an adversarial review pass against the
governing criteria and integration risks. Check:

- Each mapped test exists, cites its criterion, asserts its actual outcome and
  ran successfully at the required layer. Names, citations and a green aggregate
  exit do not prove a skipped, deselected or unreported test ran.
- Core flows and each AC's guard/negative branch ran on the running system via
  the surface-appropriate harness in `workflows/concerns/testing/practices.md`.
  Observe rejection/failure outcomes as well as success. An un-waived untested
  branch leaves its criterion `UNTESTED`; reviewed exclusions need substitute
  proof under the exception rules below. Unit-green alone is insufficient.
- A named downstream consumer pulled the change and exercised its integration.
  An external/client-facing boundary needs its real client handshake/login on
  the real address; a localhost stub cannot prove that boundary works.
- The build honors selected concerns and slots. A UI core flow ran green using
  browser E2E for client-rendered UI or HTTP+HTML assertions against the live
  server for server-rendered UI. Both are valid. Where page navigation exists,
  assert a visible active cue and `aria-current="page"` on at least one route;
  otherwise record a concrete scoped exclusion. See `workflows/references/ux-evidence.md`.
- Every claimed result came from an actual run observed to finish, never asserted
  from memory or another agent's completion claim. Investigate non-zero exits;
  distinguish transient failures from genuine defects before recording outcomes.

Changing a selected stack requires updating `concerns.md`, stating the reason
against an acceptance constraint, updating the verification plan and running the
substitute proof. A silent abandonment of a selected slot is a defect.

## Run references

Reuse normal CI/test/runtime reports and their metadata for the tested revision,
exact command and exit status, environment/data state (URL/port and seed inputs
where applicable), executed tests and outcomes. For a dirty checkout, identify
the tested diff and its base commit. Link the run from the existing mapping's
Notes/Executable Proof or acceptance/closeout record; keep metadata in its report.

An older run verifies a newer revision only when review establishes unchanged
relevant code, tests and environment. Otherwise rerun. Missing, failing, skipped
or stale results leave the claim unverified. Accepted references must remain
accessible for the project's review/audit retention period: retain needed reports
in an existing durable location before ephemeral CI artifacts expire. Missing or
expired results are unknown until recovered or rerun. Keep safe reproduction
references, without credentials, tokens or sensitive seed data.

Automated real-surface tests can supply all required proof. When normal reports
capture it, no supplemental record is needed. A real-client integration report
also suffices for external or downstream observations it captures.

## Supplemental observations and exceptions

Add a concise linked observation only when normal reporting cannot capture the
required proof, such as a manual interaction, hardware observation, external
handshake, downstream exercise or reviewed exception. Use existing Notes/
Executable Proof, a review/acceptance record or a per-change evidence README
beside its assets. A separate per-change record is optional. Identify the
criterion/change, tested revision/diff, command or manual procedure, environment,
observed outcome and supporting artifacts.

For library / docs-only / non-buildable work, use the applicable library suite or
docs build/link-check; there is no running stack to invent. If full-stack E2E is
genuinely infeasible or a branch is not applicable/automatable, record scope,
owner, rationale, reviewer/decision, strongest observable evidence available and
review/removal trigger. Substitute proof may be a boundary-stub integration or
manual run, but it too must be observed. An unrecorded "E2E is hard" is not an
exception.

HELIX requires no `verification-evidence.md`, replacement directory, index or
new evidence artifact. Preserve existing evidence and links as history; stop
mandatory appends. Migrate old sections only deliberately, repairing inbound
links. File existence and mapping structure prove no outcome: the runtime/
adopting project runs checks and reviewers assess their meaning.

## UX and package proof

Apply `workflows/references/ux-evidence.md` for
affected interactive UI work, including selected package versions, actual
presentation/accessibility checks, supported routes/themes and reviewed finding
or exception dispositions. Those checks do not replace interaction tests.
Legacy omission of UX Coverage remains structurally valid but is a readiness gap
for new affected work. Static/API-only work needs no invented UI or package audit.
