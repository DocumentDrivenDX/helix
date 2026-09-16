# Converge

Use to drive a plan or completed work to convergence: review adversarially, resolve every blocking finding, and re-review until the review comes back clean.

1. Wrap the existing `review` contract; do not invent a new review.
2. Intrinsic gates (build, test, template conformance, `summary.phantom_claims`) block; external adversarial review is advisory.
3. Fold each finding-class into a gate so it cannot recur; stop when a review pass returns no `severity: blocking` finding and `phantom_claims: 0`, or the stop rule fires.
4. Never loop without a recorded stop rule (max rounds, or a named unresolvable decision).
5. Each round's review may fan out per `modes/review.md`; the intrinsic gates run once per round after fan-in, and the stop rule counts rounds, never agents.
6. End with the `modes/_report.md` block, `mode: converge`, carrying the final round's findings.

Procedure: `workflows/actions/converge.md` (the full action prompt; this file is the contract).
