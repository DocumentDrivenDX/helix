---
title: "Refresh"
slug: refresh
weight: 180
generated: true
---

Generated from [`workflows/modes/refresh.md`](https://github.com/DocumentDrivenDX/helix/blob/main/workflows/modes/refresh.md), the mode contract the HELIX skill loads. Edit that file, not this page.

Use to bring every artifact instance under a project HELIX tree up to
date with the current canonical templates and prompts. Refresh is
`modes/validate.md` (fix-mode) applied across a whole project in one pass.

1. Resolve the project HELIX root per §Project Root Resolution.
   Enumerate every artifact instance under it. Group instances by
   activity directory (00-discover, 01-frame, …, 06-iterate). Skip
   anything that isn't an artifact instance (READMEs, plan
   sub-directories, generated files).
2. For each instance, run `modes/validate.md` in fix-mode. When the runtime
   supports sub-agent dispatch, parallelise across the activity groups
   (one agent per activity); otherwise execute the groups in activity
   order.
3. Aggregate the per-instance validate outputs into a single report:
   per-classification counts using the unified taxonomy (`ALIGNED` /
   `INCOMPLETE` / `DIVERGENT` / `UNDERSPECIFIED` / `STALE_PLAN` /
   `BLOCKED`) plus the union of every handoff validate produced.
4. Refresh surfaces handoffs in the report. It does **not** itself file
   work items; the runtime decides whether to file work from the block or
   display it unchanged. This keeps refresh runtime-neutral while
   preserving `modes/align.md`'s tracker-mutation rules for runtimes that
   have a tracker.
5. Refresh is read-only against templates and prompts in the skill
   catalog. If refresh reveals that a template itself needs to change,
   route through `evolve` against the catalog separately.

End with the `modes/_report.md` block, `mode: refresh`.
