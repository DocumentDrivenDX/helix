# Practices: Verification

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
  locally-correct component can be globally wrong. These become the re-review
  checklist.
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
   incomplete. Drive each through the harness its surface dictates (the `testing`
   concern's *surface → real-path harness* mapping; the `e2e-framework` slot owns
   the web runner) — Playwright is not the universal verifier.
4. **Re-review checklist** — a short adversarial pass recorded against:
   - each governing acceptance criterion: was it actually satisfied by the
     running system, or only by the unit layer?
   - each integration risk / seam the change touched: was it exercised, or
     assumed?
5. **Selection↔build coherence** — the built system actually **honors the
   selected concerns and slots**. For each selected slot, the build uses that
   filler: e.g. a selected `frontend-framework: react-nextjs` means a real
   React/Next app exists (SSR/RSC is fine — the point is React/Next is *present*,
   not that rendering is client-side), and when a UI slot is selected a core
   user-flow has a **whole-stack end-to-end test that ran green against the
   running system**. That test is a **browser e2e** for a client-rendered UI, or
   an **HTTP+HTML-assertion e2e** for a server-rendered UI (drive the live server
   and assert the rendered markup, including a visible active state **and**
   `aria-current="page"` on the active nav item for ≥1 route). **Both are
   first-class — a server-rendered slice verified by
   an HTTP+HTML e2e is NOT a deviation** (the `e2e-framework` concern owns *how*
   and *which*; this gate only refuses-done without that running-system evidence).
   A selected slot the build silently abandoned — selecting `react-nextjs` then
   shipping a non-React app, or shipping **no** core-flow e2e at all — is what
   this catches.

A completion claim missing any of these five is incomplete — the gate is not
"tests are green", it is "the stack was exercised, honors what was selected, and
here is the recorded evidence".

Write this recorded bundle to the canonical path the build gate checks —
`docs/helix/04-build/verification-evidence.md` — so "done" is gated on its
presence plus an adversarial review, not asserted from memory (see the 04-build
`GATE.yaml` exit requirements). A guard branch that is genuinely not applicable
or not automatable carries a **recorded reviewed exception** (manual verification
accepted / non-automatable, with evidence — who verified, what was observed; the
same escape hatch reconcile-alignment's AC coverage floor uses), never a silent
omission; an un-waived untested guard branch leaves its acceptance criterion
`UNTESTED` in reconcile-alignment.

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
- Record which exception applies and why. An unrecorded "e2e is hard" is not
  an exception.
- The verify-don't-trust rule still holds: even the substitute evidence must
  be observed, never asserted.

## Quality Gates

- Whole-stack exercise recorded (or a recorded exception with substitute
  evidence) — not unit-green alone.
- All evidence artifacts present for buildable work: command + exit status,
  target URL/env, core flows **and each AC's guard/negative branch** exercised
  on the running system, re-review checklist.
- Zero asserted-but-unobserved results — every reported outcome traces to a
  run that was watched finish.
- Re-review pass recorded against the ACs and the integration seams the change
  touched.
