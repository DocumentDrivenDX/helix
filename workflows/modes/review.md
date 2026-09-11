# Review

Use for fresh-eyes review of plans, PRs, implementation, or recent work.

1. Scope the review narrowly.
2. Inspect governing artifacts, changed implementation, tests, and public
   projection relevant to the scope.
3. Report findings first, ordered by severity, with concrete evidence.
4. Run the **claims-vs-reality** check: any artifact assertion of a test,
   coverage figure, or emitted metric that does not exist is a blocking
   phantom-claim finding (zero-floor), not a stylistic note.
5. File durable follow-up work for actionable medium-or-higher findings in
   the project's work tracker.
6. A clean verdict is necessary but not sufficient: the loop converges only
   when the work is verified **and** each finding-class is folded back into a
   gate so it cannot silently recur. Drive fixes by progressive evolve against
   the specific finding, not by re-generating the artifact or implementation.
7. **Intrinsic gates block; external adversarial review is advisory.** The
   intrinsic gates — build, test, template conformance, the phantom-claim count
   — block convergence. An external adversarial reviewer (a separate tool or
   model) is advisory input only and must never be a hard gate: when it hangs,
   errors, or is unavailable, convergence is decided by the intrinsic gates.

Procedure: `workflows/actions/fresh-eyes-review.md` (deeper step detail; this file is the contract).
