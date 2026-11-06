# Practices: Verification

Apply the evidence gate defined in `concern.md`.

## Plan the proof

Before Build, use `workflows/concerns/testing/practices.md` to scope proof to
the governing requirements, claimed capability and failure risk. Identify the
changed core flows, integration seams and observable outcomes. Use the layer
that detects each material failure; an internal rule may need unit coverage,
while a changed runtime boundary needs its real client and applicable
rejection/failure proof. Plan affected downstream-consumer checks and any
substitute proof. Keep a required running system reachable with its start command
and seed data. Planned proof is not a passing run.

## Completion contract

Use the existing Story Test Plan's Acceptance Criteria Test Mapping, test-source
`@covers` citations and observed run reports. Other requirement types use their
existing acceptance records and stable IDs; do not create a second per-criterion
matrix. Reuse tests that already supply the required proof; one test can cover
multiple criteria. Adding another layer or matrix requires a distinct unresolved
risk or claim. Simplifying a mechanism can remove the need for its private-detail
tests while retaining proof of the governing outcomes. Test names follow
`workflows/concerns/testing/practices.md`.

Before claiming completion, make an adversarial review pass against the
governing criteria and integration risks. Check:

- Each mapped test exists, cites its criterion, asserts its actual outcome and
  ran successfully at the required layer. Names, citations and a green aggregate
  exit do not prove a skipped, deselected or unreported test ran.
- Changed core flows and integration boundaries ran on the running system via
  the appropriate harness in `workflows/concerns/testing/practices.md`, including
  each applicable material guard/negative branch. Internal rules, refactors and
  mechanical updates may use sufficient regression, unit or compile checks.
  Do not duplicate every criterion at runtime or invent a rejection branch.
  Missing required proof leaves the affected claim `UNTESTED`.
- When the change affects a named downstream integration, that consumer pulled
  the change and exercised its integration.
  An external/client-facing boundary needs its real client handshake/login on
  the real address; a localhost stub cannot prove that boundary works.
- The build honors selected concerns and slots. An affected UI core flow ran green using
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
docs build/link-check; there is no running stack to invent. Selecting sufficient
proof for internal or mechanical work is ordinary scoping, not an exception that
needs a record. If required full-stack E2E is
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
