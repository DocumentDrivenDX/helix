# Refresh

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
3. Summarize the material changes and unresolved findings.
4. Refresh is read-only against templates and prompts in the skill
   catalog. If refresh reveals that a template itself needs to change,
   route through `evolve` against the catalog separately.
