---
title: "Experiment"
slug: experiment
weight: 90
generated: true
---

Generated from [`workflows/modes/experiment.md`](https://github.com/DocumentDrivenDX/helix/blob/main/workflows/modes/experiment.md), the mode contract the HELIX skill loads. Edit that file, not this page.

Use for metric-driven optimization loops.

1. Define the goal, metric, baseline, intervention, and decision that the
   measurement will change. State the stopping condition before running.
2. Bound the whole experiment, including retries and parallel runs: maximum
   runs, elapsed time, retained temporary storage and paid-service usage where
   applicable. Honor existing user/runtime limits. With no baseline, choose a
   small probe with explicit size and duration limits before expanding.
3. Before each launch, bound its workload, timeout and outstanding parallel
   jobs to the remaining cumulative allowance. Measure results and resource
   use after each iteration, before launching another. Expand only to resolve
   a named remaining uncertainty. Stop when the
   decision is supported or any limit is reached; preserve results and cancel
   outstanding work through the runtime. Resuming does not reset the allowance.
4. Keep changes or revert/adjust based on metric evidence.
5. To validate a **methodology or skill change** (a workflow prompt, template,
   or this routing skill), use a **regression evaluation**: record a committed
   baseline, run a fixed brief from the bare prompt with the improved skill
   *installed* (never by redirecting reads), score intrinsic metrics against the
   baseline, and **keep what moved, cut what didn't**. That evaluation is the
   standing answer to "how do we know this change is impactful."

Known prices and metered usage can support a monetary estimate; unknown rates
or delayed billing cannot support a claimed dollar cap. Use available workload,
time and storage bounds instead, disclose the uncertainty once, and do not
start unbounded paid runs. The runtime enforces available limits and captures
usage; HELIX defines the stopping decision. Record resource limits and measured
use in the existing experiment record, not a second budget document. Token
spending still follows `workflows/references/work-item-first.md`.

Procedure: `workflows/actions/experiment.md` (deeper step detail; this file is the contract).
