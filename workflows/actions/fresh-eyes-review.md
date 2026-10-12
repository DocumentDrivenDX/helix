# HELIX Action: Fresh-Eyes Review

Review the plan, artifact, code change, or implementation named by the user.
Stay within that scope. Review is read-only unless the user authorizes edits.

## Select the target

The target may be a document, a change set, a work item, or a list of files.
Inspect the current content and, for a change review, the relevant changed
lines. Read governing requirements, decisions, and tests that can affect the
result. Do not cite repository history in the report.

## Review

Check the target for:

- correctness against its governing requirements and decisions;
- missing error, boundary, integration, or recovery behavior relevant to scope;
- security and active concern practices where applicable;
- test quality and whether tests exercise the behavior they claim to cover;
- unsupported claims about tests, coverage, or metrics.

For completion reviews, follow the existing acceptance mapping and test-source
citations to actual assertions and observed run results. Assess behavior-based
names separately from stable citations; preserve legacy valid citations in names.
Check tested revision/diff, command/exit, environment, executed scope and result
retention per the verification practices. Skipped, stale or expired runs leave
claims unverified. Normal reports suffice; supplemental observations are
conditional on proof gaps outside that reporting path. No extra file is required.

Skip checks that do not apply to the target. Do not infer that an accepted ADR
has been implemented; compare its direction with code only when implementation
is in scope. Preserve user-authorized stop rules.

Report actionable findings first. For each, provide location, category,
severity, explanation, and evidence. Separate confirmed defects from uncertain
observations and optional improvements. If no findings remain, say what scope
you reviewed and what evidence supports the result. A factual claim about a
test, metric, or measurement must point to the test or observation behind it.

Do not revise artifacts automatically. Recommend follow-ups when they would
help.

## Optional structured report

When requested, summarize status and findings using
`workflows/modes/_report.md`. Include only applicable checks; do not add empty
dimensions or `N/A` entries for ceremony.

## Source-Code Boundary Baseline

Apply `modularity-and-encapsulation` per the source-code baseline in
`workflows/references/concern-resolution.md` and the matching mode contract.
Preserve its applicability, adoption escape path, legacy-validity distinction,
style compatibility and evidence requirements throughout this procedure.

## OpenTelemetry Diagnostic Alignment

When selected `o11y-otel` practices apply, check their Artifact Impact against
owning artifacts. Compare templates, prompts, examples and quality checks when
the catalog is in scope: conditional trace context, pre-sink privacy, transport
ownership, bounded retrieval and capture-loss disclosures must agree. Exact
shared telemetry/query surfaces belong in Contracts, not story TDs. Inspect
actual receiver/correlation, duplicate-ingestion and failure evidence before
accepting an implementation claim; JSONL parsing and quiet console output are
insufficient. Report missing adoption/evidence without silently re-selecting
concerns or claiming the adopting-project pilot ran.

## UX and package alignment

For affected UI work, apply ux-interaction-patterns and the selected component
owner, per workflows/references/ux-evidence.md. For plan reviews, verify STP
UX Coverage resolves to concrete planned tests/assertions/commands; do not
require future passing results. For implementation/completion reviews, verify
IDs resolve to real tests with meaningful assertions and AC citations. Review
pattern applicability, visible current location, keyboard/modality/focus,
async duplicate guards, validation and recovery, and destructive policy.
For completion claims require observed runtime outcomes; coverage structure
is not behavioral proof.
For packaged-design-system, inspect actual availability/compatibility evidence,
installed-version documentation, token references and component ownership.
For plans inspect the declared supplied/project check commands and evidence
capture; for completion inspect observed results and reviewed findings/exceptions.
Do not assume a package includes lint/audit tooling. Report missing evidence;
never invent a consumer test run from HELIX's catalog tests.
