---
title: "Converge"
slug: converge
weight: 40
generated: true
---

Generated from [`workflows/modes/converge.md`](https://github.com/DocumentDrivenDX/helix/blob/main/workflows/modes/converge.md), the mode contract the HELIX skill loads. Edit that file, not this page.

Use to drive a plan or completed work to convergence: review adversarially, resolve every blocking finding, and re-review until the review comes back clean.

1. Wrap the existing `review` contract; do not invent a new review.
2. Intrinsic gates (build, test, template conformance, phantom-claim count) block; external adversarial review is advisory.
3. Fold each finding-class into a gate so it cannot recur; stop when a review pass returns no blocking findings or the stop rule fires.
4. Never loop without a recorded stop rule (max rounds, or a named unresolvable decision).
5. Each round's review may fan out per `review.md`; the intrinsic gates run once per round after fan-in, and the stop rule counts rounds, never agents.

Procedure: `workflows/actions/converge.md` (the full action prompt; this file is the contract).
