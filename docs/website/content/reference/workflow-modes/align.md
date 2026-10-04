---
title: "Align"
slug: align
weight: 10
generated: true
---

Generated from [`workflows/modes/align.md`](https://github.com/DocumentDrivenDX/helix/blob/main/workflows/modes/align.md), the mode contract the HELIX skill loads. Edit that file, not this page.

Use `align` to reconcile related HELIX documents, check traceability, or place
content in the right artifact. The default scope is the requested document and
the authorities that can affect it. Follow a graph relationship only when its
content could change the result.

1. Read the target, its relevant governing artifacts, and the applicable
   template or metadata. Preserve the authority order: vision, requirements,
   features and stories, architecture and ADRs, designs, tests, plans, then
   implementation.
2. Compare the affected documents. Classify a material gap as `ALIGNED`,
   `INCOMPLETE`, `DIVERGENT`, `UNDERSPECIFIED`, `STALE_PLAN`, or `BLOCKED`.
   Keep requirements at their intended strength; code alone does not authorize
   changing them.
3. For misplaced content, state its source, destination, and the proposed
   change. Omit a migration ledger unless the user requests one.
4. Give findings concrete evidence and a useful next step.

An implementation audit is a separate, explicit request. When asked, keep it
within the named scope and inspect the relevant code, tests, and governing
decisions. Use the audit checks in `actions/reconcile-alignment.md` as needed;
do not infer that every accepted decision has already been implemented.

Procedure: `workflows/actions/reconcile-alignment.md` supplies additional detail.

## Fan-out

Use parallel reviewers only when the host supports them and the scope warrants
it. Give each reviewer a distinct question and the same scope. Reconcile
conflicts and duplicates in the final answer. No reviewer may widen scope or
write artifacts unless the user authorized those changes.
