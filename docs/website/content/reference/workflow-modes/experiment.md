---
title: "Experiment"
slug: experiment
weight: 150
generated: true
---

Generated from [`skills/helix/SKILL.md`](https://github.com/DocumentDrivenDX/helix/blob/main/skills/helix/SKILL.md), the HELIX skill. Edit the skill, not this page.

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
