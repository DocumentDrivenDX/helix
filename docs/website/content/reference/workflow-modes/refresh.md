---
title: "Refresh"
slug: refresh
weight: 60
generated: true
---

Generated from [`skills/helix/SKILL.md`](https://github.com/DocumentDrivenDX/helix/blob/main/skills/helix/SKILL.md), the HELIX skill. Edit the skill, not this page.

Use to bring every artifact instance under a project HELIX tree up to
date with the current canonical templates and prompts. §Refresh is
§Validate (fix-mode) applied across a whole project in one pass.

1. Resolve the project HELIX root per §Project Root Resolution.
   Enumerate every artifact instance under it. Group instances by
   activity directory (00-discover, 01-frame, …, 06-iterate). Skip
   anything that isn't an artifact instance (READMEs, plan
   sub-directories, generated files).
2. For each instance, run §Validate in fix-mode. When the runtime
   supports sub-agent dispatch, parallelise across the activity groups
   (one agent per activity); otherwise execute the groups in activity
   order.
3. Aggregate the per-instance §Validate outputs into a single report:
   per-classification counts using the unified taxonomy (`ALIGNED` /
   `INCOMPLETE` / `DIVERGENT` / `UNDERSPECIFIED` / `STALE_PLAN` /
   `BLOCKED`) plus the union of every §Align gap-to-implementation
   handoff §Validate produced.
4. §Refresh surfaces handoffs in the report. It does **not** itself
   file work items — that responsibility stays with the runtime: DDx
   runtimes may file work items in response, Claude Code runtimes may emit
   tracker issues, chat-only runtimes may simply display the report.
   This keeps §Refresh runtime-neutral while preserving §Align's
   tracker-mutation rules for runtimes that have a tracker.
5. §Refresh is read-only against templates and prompts in the skill
   catalog. If §Refresh reveals that a template itself needs to change,
   route through `evolve` against the catalog separately.
