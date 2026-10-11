# Review

Use for an explicitly requested fresh-eyes review of a plan, artifact, change,
or implementation.

1. Define the target and keep the review within that scope. Read the governing
   requirements, decisions, tests, and changed material that bear on it.
2. Report actionable findings first, with severity, location, and evidence.
   Verify factual claims about tests, coverage, or metrics before relying on
   them. Preserve security, correctness, and user-authorized stop rules.
3. Separate defects from optional improvements.

## Source-Code Boundaries

For source changes, review `modularity-and-encapsulation` against Architecture, Contracts, and the project checker evidence. Inspect relevant imports, exports, mutable state/invariants, vendor-type leakage, integration translation and construction ownership. Respect the chosen style and authorized exceptions. Report missing adoption or new violations; do not infer semantics from a populated table.

Procedure: `workflows/actions/fresh-eyes-review.md` supplies additional detail.

## Fan-out

Apply `workflows/references/work-item-first.md` spending and review rules. One
pass is the default; additional reviewers must answer distinct risk questions
within the shared ceiling, not duplicate a full review for consensus.

Use parallel reviewers only when available and useful. Give each a distinct
question within the same scope. Resolve duplicate or conflicting findings
before reporting; no reviewer may widen the scope or make edits without
authorization.

## OpenTelemetry Diagnostics

Apply selected `o11y-otel` practice sections, including agent run diagnostics
where commands/tests need persistent evidence. Preserve applicability without
silently re-selecting concerns. Require safe run/attempt evidence references,
verification outcome and capture limits at execution closeout; a quiet console
is not a pass. Shared schemas stay in Contracts, with actual OTel receiver proof
for claimed integrations. See `workflows/references/agent-diagnostics.md`.

## UX coverage

For affected interactive UI work, apply ux-interaction-patterns and the selected
component owner. Use workflows/references/ux-evidence.md: a missing STP UX
Coverage map is an adoption/readiness gap, not retroactive invalidity. Require
populated AC mappings and review exclusion reasons. For planning/readiness,
check named planned tests, commands, component gaps and evidence capture; do
not demand future passing results. For implementation/completion claims,
check actual test source and observed runtime results; SDK audit evidence
cannot prove interaction flows.
