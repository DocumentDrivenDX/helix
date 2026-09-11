---
title: "Project Audit"
slug: project-audit
weight: 160
generated: true
---

Generated from [`workflows/modes/project-audit.md`](https://github.com/DocumentDrivenDX/helix/blob/main/workflows/modes/project-audit.md), the mode contract the HELIX skill loads. Edit that file, not this page.

Use on entry to a project with stale context to answer one question: where does this project stand? Are specs, implementation, tests, and acceptance criteria aligned, is the work complete, and what is the next safe action?

1. Compose `check` with `align`: read governing artifacts, implementation evidence, and tests before reporting.
2. Report per-layer alignment (specs↔implementation↔tests↔ACs) using the Align taxonomy.
3. End with one recommended next mode and its evidence, in the `_report.md` shape.
4. Read-only: audit never edits artifacts or code.

Procedure: `workflows/actions/project-audit.md` (the full action prompt; this file is the contract).
