---
title: "Experiment"
slug: experiment
weight: 90
generated: true
---

Generated from [`workflows/modes/experiment.md`](https://github.com/DocumentDrivenDX/helix/blob/main/workflows/modes/experiment.md), the mode contract the HELIX skill loads. Edit that file, not this page.

Use for metric-driven optimization loops.

1. Define the goal, metric, baseline, intervention, and stop condition.
2. Run bounded iterations.
3. Measure after each iteration.
4. Keep changes or revert/adjust based on metric evidence.
5. To validate a **methodology or skill change** (a workflow prompt, template,
   or this routing skill), use a **regression evaluation**: record a committed
   baseline, run a fixed brief from the bare prompt with the improved skill
   *installed* (never by redirecting reads), score intrinsic metrics against the
   baseline, and **keep what moved, cut what didn't**. That evaluation is the
   standing answer to "how do we know this change is impactful."

Procedure: `workflows/actions/experiment.md` (deeper step detail; this file is the contract).
