---
title: "Polish"
slug: polish
weight: 150
generated: true
---

Generated from [`workflows/modes/polish.md`](https://github.com/DocumentDrivenDX/helix/blob/main/workflows/modes/polish.md), the mode contract the HELIX skill loads. Edit that file, not this page.

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

Procedure: `workflows/actions/polish.md` (deeper step detail; this file is the contract).
