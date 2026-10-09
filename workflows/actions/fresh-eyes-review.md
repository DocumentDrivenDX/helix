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
