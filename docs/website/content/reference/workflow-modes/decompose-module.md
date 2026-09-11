---
title: "Decompose Module"
slug: decompose-module
weight: 50
generated: true
---

Generated from [`workflows/modes/decompose-module.md`](https://github.com/DocumentDrivenDX/helix/blob/main/workflows/modes/decompose-module.md), the mode contract the HELIX skill loads. Edit that file, not this page.

Use to decompose an oversized, poorly encapsulated code module into focused units, iteratively, behind a per-iteration verification gate. This is code-structure decomposition, distinct from decomposing requirements into work items (`frame` / `polish`).

1. Name the module, the target unit boundaries, and the verify command before the first extraction.
2. One extraction per iteration; run the verify gate after each; revert an iteration that fails it.
3. Preserve public behavior and tests; record any interface change as a design decision.
4. Stop when every unit is under the agreed size and the gate is green.

Procedure: `workflows/actions/decompose-module.md` (the full action prompt; this file is the contract).
