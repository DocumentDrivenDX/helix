---
title: "Review"
slug: review
weight: 190
generated: true
---

Generated from [`workflows/modes/review.md`](https://github.com/DocumentDrivenDX/helix/blob/main/workflows/modes/review.md), the mode contract the HELIX skill loads. Edit that file, not this page.

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

Use parallel reviewers only when available and useful. Give each a distinct
question within the same scope. Resolve duplicate or conflicting findings
before reporting; no reviewer may widen the scope or make edits without
authorization.
