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

These practices define the **evidence gate**: what must exist before work is
called "done". They sit on top of `testing` (strategy) and the `e2e-framework`
slot (tooling) — they do not restate how to write tests or which e2e runner to
use. Their one job is to refuse a completion claim that has no observed
evidence behind it.

## Design

- Identify, during design, what "exercised end-to-end" means for this change:
  which real user flow(s) traverse the full stack, and what observable
  outcome proves each one ran. This is the evidence you will capture at done.
- Identify the integration seams the change touches — the boundaries where a
  locally-correct component can be globally wrong.
- If the change has a named downstream consumer in another repo, record the
  evidence you will need at done: the consumer pulled the change and exercised
  its integration. Local gate-green alone is not enough.
- If the work is library / docs-only / non-buildable, or full-stack e2e is
  genuinely infeasible, record the applicable exception (see `concern.md`) and
  the substitute evidence now, not at the gate.

## Implementation

- Build to the acceptance criteria, but treat "the code compiles and unit
  tests pass" as the *start* of verification, not the end.
- Keep the running system reachable: a start command (with seed data) that an
  agent can launch and exercise. The whole-stack evidence depends on it.

## The evidence gate (before claiming "done")

Work is **not done** until observed evidence of the running system exists.
Before reporting completion, produce these **evidence artifacts** — captured
from an actual run, never asserted from memory:

1. **Command + exit status** — the exact command(s) run to exercise the system
   (build, start, e2e suite, smoke) and the exit status each returned. A
   non-zero exit that was not investigated is not "done".
2. **Target URL / environment** — where the system was exercised: the base URL
   and port, the environment (local / container / CI), and the data state
   (seeded with what).
3. **Core flows + guard branches exercised** — the specific real user flow(s)
   driven against the running system end-to-end, **and, for each governing
   acceptance criterion, its guard/negative branch** (the rejection / failure /
   edge path: malformed or missing input, double-submit / idempotency,
   unauthorized, cross-tenant, out-of-window), with the observed outcome of each
   (what was seen, not what was expected). **Happy-path-green is not done** — a
   criterion whose guard branch was never driven on the running system is
   incomplete. Drive each through the harness its surface dictates (see
   the `testing` concern's practices, *Surface → real-path
   harness*; the `e2e-framework` slot owns the web runner).
4. **Selection↔build coherence** — the built system actually **honors the
   selected concerns and slots**. For each selected slot, the build uses that
   filler: e.g. a selected `frontend-framework: react-nextjs` means a real
   React/Next app exists (SSR/RSC is fine — the point is React/Next is *present*,
   not that rendering is client-side), and when a UI slot is selected a core
   user-flow has a **whole-stack end-to-end test that ran green against the
   running system**. That test is a **browser e2e** for a client-rendered UI, or
   an **HTTP+HTML-assertion e2e** for a server-rendered UI (drive the live server
   and assert the rendered markup, including a visible active state **and**
   `aria-current="page"` on the active nav item for ≥1 route where page
   navigation exists; otherwise record a concrete scoped exclusion). **Both are
   first-class — a server-rendered slice verified by
   an HTTP+HTML e2e is NOT a deviation** (the `e2e-framework` concern owns *how*
   and *which*; this gate only refuses-done without that running-system evidence).
   A selected slot the build silently abandoned — selecting `react-nextjs` then
   shipping a non-React app, or shipping **no** core-flow e2e at all — is what
   this catches.

A completion claim missing any of these is incomplete — the gate is not
"tests are green", it is "the stack was exercised, honors what was selected, and
here is the recorded evidence".

## Requirement-linked results

Use the existing Story Test Plan's Acceptance Criteria Test Mapping, test-source
`@covers` citations and observed test/run reports as the verification chain.
For work governed by another requirement type, use its existing mapping or
acceptance record and stable IDs. Do not create a second per-criterion matrix.
Tests name observable behavior and relevant conditions per the `testing`
practices; names and citations alone establish neither exercise nor success.

For each in-scope criterion, review that the mapped test exists, cites the
criterion, asserts its actual outcome and ran successfully at the required
layer. Automated real-surface tests can provide all running-system evidence;
when their reports capture the required proof, no supplemental record is needed.
A green aggregate exit does not prove a skipped, deselected or unreported test
ran. Missing, failing, skipped or stale results leave the claim unverified.

Reuse the normal CI/test/runtime report metadata for the tested revision,
command and exit status, environment/data state, executed tests and outcomes.
If testing a dirty checkout, identify the tested diff as well as its base commit.
Link the run from the mapping's existing Notes/Executable Proof or the existing
acceptance/closeout record; keep run metadata in its owning report. A newer
revision is not verified by an older run unless review establishes that the
relevant code, tests and environment are unchanged. Otherwise rerun.

Accepted references must remain accessible for the project's review/audit
retention period. Before ephemeral CI artifacts expire, retain the needed
report in an existing durable project/runtime location. Missing or expired
results are unknown until recovered or rerun. Raw console dumps are unnecessary
when a retained report contains the required facts. Do not retain credentials,
tokens or sensitive seed data; keep safe reproduction references.

## Supplemental observations (conditional)

Add a concise linked observation only when the normal test/reporting path
cannot capture the required proof: a manual interaction, hardware observation,
external handshake, downstream-consumer exercise or reviewed verification
exception. These are proof gaps, not exemptions from testing or a task-size rule.
A real-client integration report that captures the observation already suffices.

Use the existing mapping's Notes/Executable Proof, review/acceptance record or
an existing per-change evidence README beside screenshots/traces. A separate
per-change record is optional when the assets warrant it. Identify the criterion
and change, tested revision/diff, command or manual procedure, environment,
observed outcome and supporting artifacts. For exceptions include scope, owner,
rationale, reviewer/decision, strongest observed substitute and review/removal
trigger. An un-waived untested guard branch leaves its criterion `UNTESTED`.

HELIX requires no `verification-evidence.md`, replacement directory, index or
new evidence artifact. Preserve existing evidence and links as history; stop
mandatory appends. Move old sections only as a deliberate migration that repairs
their inbound links. File existence and mapping structure are not completion
proof. The runtime/adopting project executes checks; reviewers assess their
meaning and relevance to the change.

## Selected-stack changes are recorded, never silent

Under a large brief an agent may be tempted to quietly retreat from a selected
slot (drop React for a hand-rolled page, skip the e2e). That **silent retreat is
a defect** — a selected slot abandoned with no recorded decision and no evidence
the substitute still satisfies the selected concerns. Changing a selected stack
mid-build is allowed only as a **recorded deviation**: update the slot/concern
selection in `concerns.md`, state the reason tied to an acceptance constraint,
update the verification plan, and run the substitute evidence. (The
`verification` concern's exceptions — library / docs-only / non-buildable /
genuinely infeasible e2e, defined in this concern's `concern.md` — are recorded
the same way.)

## Verify, don't trust

- Never assert a result you did not observe. Re-run the gate and watch it
  finish rather than trusting a prior "complete". (This is measure's M4
  verify-don't-trust applied to the completion claim, not just the metric.)
- A self-reported "done" from an autonomous pass is a hypothesis. Confirm it
  by exercising the stack; a pass can report success and still have died
  mid-run.
- Distinguish a transient failure (API overload, network blip — retry) from a
  genuine failure (record it) before recording any outcome. Do not paper over
  a real failure as transient, and do not record a transient blip as a
  completion.

## Done = whole stack exercised with recorded evidence

- The completion bar is the whole stack exercised against real flows with the
  evidence artifacts above recorded — **not** a green unit suite.
- This is what catches locally-correct / globally-wrong work: each unit passes,
  but the composed running system was never driven, so the integration defect
  ships. Exercising the stack surfaces it before "done".

## Exceptions

Honor the exceptions in `concern.md` (library / docs-only / non-buildable;
e2e genuinely infeasible). Under a recorded exception:

- Substitute the strongest observable evidence that *does* exist (the library
  suite green with command + exit status; the docs build/link-check; an
  integration run against a stubbed boundary; a recorded manual run).
- Record which exception applies and why in the existing acceptance record,
  with the reviewed disposition and substitute evidence described above. An
  unrecorded "e2e is hard" is not an exception.
- The verify-don't-trust rule still holds: even the substitute evidence must
  be observed, never asserted.

## Quality Gates

- Whole-stack exercise recorded (or a recorded exception with substitute
  evidence) — not unit-green alone.
- All evidence artifacts present for buildable work: command + exit status,
  target URL/env, core flows **and each AC's guard/negative branch** exercised
  on the running system.
- Zero asserted-but-unobserved results — every reported outcome traces to a
  run that was watched finish.

## UX and package evidence

For affected interactive UI work, the STP UX Coverage map follows
workflows/references/ux-evidence.md and ux-interaction-patterns. Review actual
mapped test source/citations and observed interaction outcomes before done.
Legacy omission is structurally valid but is a readiness gap for new affected
work. With packaged-design-system, record installed versions and the project's
actual presentation/accessibility checks, command exits, route/theme coverage,
report paths and reviewed findings/exceptions. Use applicable supplied tools;
where none exist, define project checks. These do not replace keyboard, focus,
duplicate-submit, validation or recovery tests. Static/API-only work needs no
invented UI or package audit.
