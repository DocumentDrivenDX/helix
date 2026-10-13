# Practices: Verification

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
