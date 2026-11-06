# Polish

Use when the user asks to decompose or refine work items for a named scope.
Infer the scope from the task; ask when it is unclear. Do not select all open
work by default.

1. Prefer one item per coherent goal; split requested tracking only for
   independent scheduling, ownership, parallel execution, or deferred work, keeping
   dependencies in the order required by the governing plan.
2. Check scoped items for concrete acceptance criteria, evidence, dependencies,
   sizing, and applicable runtime labels. Preserve relevant area labels and
   concern-specific requirements.
3. Verify existing implementation work against code and tests. Close or re-scope
   work only when evidence shows the acceptance criteria are already met.
4. Stop when requested decomposition is complete, scoped items are ready, and
   no material ambiguity remains. A requested round limit is an upper bound.

Require execution-ready work items to name exact files, commands, checks, fields,
or observable outcomes that establish success. If those cannot be specified, mark the item
not execution-ready and route it back through planning.

## Source-Code Boundaries

Apply `modularity-and-encapsulation` and the source-code baseline in `workflows/references/concern-resolution.md`. Feature work is not execution-ready without baseline selection, populated boundary evidence, and sequenced project-local enforcement. Name destination modules and applicable check commands in scoped work items. Bounded adoption/checker work may establish those prerequisites; do not block it on the gate it creates.

Procedure: `workflows/actions/polish.md` supplies additional detail.

## UX coverage

For affected interactive UI work, apply ux-interaction-patterns and the selected
component owner. Use workflows/references/ux-evidence.md: a missing STP UX
Coverage map is an adoption/readiness gap, not retroactive invalidity. Require
populated AC mappings and review exclusion reasons. For planning/readiness,
check named planned tests, commands, component gaps and evidence capture; do
not demand future passing results. For implementation/completion claims,
check actual test source and observed runtime results; SDK audit evidence
cannot prove interaction flows.
