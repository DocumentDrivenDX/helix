---
title: "Polish"
slug: polish
weight: 110
generated: true
---

Generated from [`skills/helix/SKILL.md`](https://github.com/DocumentDrivenDX/helix/blob/main/skills/helix/SKILL.md), the HELIX skill. Edit the skill, not this page.

Use to refine work items before execution.

1. Load open work for the scope and any governing plan.
2. Run multiple passes for deduplication, coverage, acceptance quality,
   dependency correctness, sizing, and label hygiene.
3. **Evidence gate for implement/build items:** verify residual against
   code/tests before keeping or filing build work. Prefer story/AC floor
   items when only docs lag. Close or re-scope items whose residual is
   already green (passing tests cite the AC, or documented exception).
4. Require execution-ready work items to name exact files, commands, checks, fields,
   or observable repository states.
5. If acceptance cannot be sharpened from governing artifacts, flag the work as
   not execution-ready and route it back through planning.
