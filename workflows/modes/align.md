# Align

Use `align` to reconcile related HELIX documents and assess whether a named
system or component coherently realizes its intent. A document target defaults
to that document and relevant authorities. A system/component target includes
its relevant implementation and tests; it does not authorize a whole-project
audit. Follow relationships only where they can affect the result.

1. Read the target, its relevant governing artifacts, and the applicable
   template or metadata. Preserve the authority order: vision, requirements,
   features and stories, architecture and ADRs, designs, tests, plans, then
   implementation.
2. Compare the affected documents for gaps affecting user outcomes,
   requirements, scope, design choices, safety, or completion evidence. Lifecycle
   labels, stale review stamps, and missing graph edges alone are not findings.
   Resolve ordinary drift from clear higher authority when edits are authorized;
   ask only for material choices that existing intent cannot resolve.
   Classify a material gap as `ALIGNED`,
   `INCOMPLETE`, `DIVERGENT`, `UNDERSPECIFIED`, `STALE_PLAN`, or `BLOCKED`.
   Keep requirements at their intended strength; code alone does not authorize
   changing them.
3. For misplaced content, state its source, destination, and the proposed
   change. Omit a migration ledger unless the user requests one.
4. Assess simplification within the selected scope under execution feedback.
   Inspect overlapping interfaces, redundant operations or state, duplicated
   verification and excessive source commentary where relevant. Use the
   comparison in `actions/reconcile-alignment.md`; volume alone is not a defect.
   Give findings concrete evidence, the proposed consolidation/removal and the
   behavior or proof that must remain. Separate advisory improvements from
   violations that block readiness; do not create gates or work items by default.

For system/component alignment, inspect relevant code and tests without requiring
another audit invocation. Keep document-only alignment bounded to its artifacts.
A comprehensive implementation inventory still requires explicit selection.
Do not infer that every accepted decision has already been implemented.

## Source-Code Boundaries

Check `modularity-and-encapsulation` selection and realization across relevant Architecture, Contracts, TD, test/build plans and scoped work. Separate legacy structural validity from current source-work readiness. When implementation is in scope, compare relevant imports/public surfaces to the map and check for new violations, redundant surfaces or unsupported claims.

Procedure: `workflows/actions/reconcile-alignment.md` supplies additional detail.

## Fan-out

Use parallel reviewers only when the host supports them and the scope warrants
it. Give each reviewer a distinct question and the same scope. Reconcile
conflicts and duplicates in the final answer. No reviewer may widen scope or
write artifacts unless the user authorized those changes.
