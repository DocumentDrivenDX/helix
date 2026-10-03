---
title: "Polish"
slug: polish
weight: 150
generated: true
---

Generated from [`workflows/modes/polish.md`](https://github.com/DocumentDrivenDX/helix/blob/main/workflows/modes/polish.md), the mode contract the HELIX skill loads. Edit that file, not this page.

Use when the user asks to decompose or refine work items for a named scope.
Infer the scope from the task; ask when it is unclear. Do not select all open
work by default.

1. Decompose requested implementation slices into bounded work items, keeping
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

Procedure: `workflows/actions/polish.md` supplies additional detail.
