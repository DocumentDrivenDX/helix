# HELIX Action: Reconcile Alignment

Compare the requested artifacts or named system/component with governing intent
and assess opportunities for simplification. A system/component alignment includes
its relevant implementation and tests without another audit invocation; a
request limited to documents does not authorize a code audit. Comprehensive
inventory requires explicit selection. Keep analysis read-only unless the user
also authorizes edits.

## Scope and authority

Use the scope named by the user. If it is unclear, ask before expanding the
review. Read the target and only the authorities that can affect it. Follow
relevant links as needed; do not traverse every upstream or downstream artifact
by default.

When documents disagree, use this order: vision, requirements, features and
stories, architecture and ADRs, designs, tests, implementation plans, then
code. A lower layer does not silently revise a higher one. An accepted ADR
records the chosen direction; implementation status requires separate evidence.

## Document alignment

1. Summarize the target's intent from its governing artifacts.
2. Compare affected documents for material contradictions, ambiguity, or stale
   content that changes user outcomes, requirements, scope, design choices,
   safety, or completion evidence. Missing links, lifecycle labels, and stale
   review stamps alone are not findings. Use content and authority when links
   are absent. Resolve ordinary lower-layer drift from clear higher authority
   when edits are authorized; surface only choices that existing intent cannot
   resolve. Do not create separate status or linkage housekeeping tasks.
3. Classify material gaps as `ALIGNED`, `INCOMPLETE`, `DIVERGENT`,
   `UNDERSPECIFIED`, `STALE_PLAN`, or `BLOCKED`.
4. For misplaced content, identify its source and proposed destination. Draft
   destination text only when the user asks for it or authorizes edits.
5. Report findings with evidence and a useful next step. A conversational
   answer is sufficient by default.
6. Separately, list simplification opportunities: overlapping types or
   operations, duplicated verification, or obsolete detail. Report one only when
   removing it would materially reduce what must be understood or maintained;
   length alone is not a defect. Name the redundancy, the proposed removal and
   the evidence that keeps the required outcome. These are advisory: they take
   no gap classification, do not block readiness and create no work items by
   default.

## Implementation comparison

For system/component alignment or an explicitly requested implementation audit,
inspect only code and tests relevant to the named scope. Compare the resulting
system's coherence as well as requirement coverage: overlapping methods or types,
duplicated state, unnecessary operations, tests that duplicate other evidence or
assert private steps, and comments that restate code or design documents. Judge
these under `workflows/principles.md` (Design for Simplicity, Make Intent
Explicit) and the testing practices, and report them as in step 6.

Select the existing checks below where they answer the alignment question; a full
inventory is not required unless the user asks for comprehensive coverage.

- **Bidirectional traceability:** for comprehensive audits, map material scoped
  code surfaces (such as routes, APIs, jobs, migrations, feature flags, and
  deployment behavior) to governing artifacts; map scoped requirements and
  acceptance criteria to implementation and exercising tests. Exclude generated
  output and framework plumbing unless they affect the audited behavior.
- **Acceptance evidence:** state whether each in-scope criterion is implemented,
  exercised by a relevant test, and passing. Report missing implementation,
  missing or failing tests, and unsupported claims separately. Follow the
  [verification completion contract](../concerns/verification/practices.md) for
  existing mappings, test-source citations, assertions and observed results.
- **Accepted ADRs:** compare the chosen mechanism or boundary with the scoped
  implementation. An unimplemented choice is a gap against desired state, not
  proof that the ADR is invalid.
- **Concerns and practices:** check active security, observability, technology,
  or operational practices when they apply to the scoped surface. Check both
  required behavior and relevant artifact obligations.
- **Measurable NFRs:** compare scoped measurements with stated targets when
  available. Distinguish missing measurement from a measured failure.
- **Claims and instruments:** verify claims about tests, coverage, metrics, or
  gates before treating them as evidence. Use an available deterministic
  checker when its result is relevant; inspect its rule only when needed to
  interpret the finding.

Record factual claims with evidence such as artifact sections, code locations,
tests, commands, or observed measurements. State what was not examined when
that limit changes the conclusion. Do not manufacture `N/A` rows for absent
dimensions, and do not turn each finding into a gate or tracker item.

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

## Formal Methods Alignment

For selected `formal-methods`, compare owning requirements, Contracts and designs
with the chosen scope/rigor and property authority. Inspect current analysis
results, bounds/assumptions, reachable witnesses, targeted negative controls and
model/code/test correspondence before accepting assurance claims. Safety analysis
does not prove liveness or production correctness. Missing/stale evidence blocks
the affected claim. Unaffected slices record reviewed non-applicability without
an analyzer/proof run. Preserve legacy structural validity and existing concern
selection; use `workflows/references/formal-methods.md` for adoption checks.
