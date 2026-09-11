---
title: "E2E Ladder"
slug: e2e-ladder
weight: 70
generated: true
---

Generated from [`workflows/modes/e2e-ladder.md`](https://github.com/DocumentDrivenDX/helix/blob/main/workflows/modes/e2e-ladder.md), the mode contract the HELIX skill loads. Edit that file, not this page.

Use to build end-to-end coverage as a ladder of scenarios of increasing complexity, each rung a durable automated test that drives the real runtime boundary and stays in CI.

1. Start from the simplest real-client scenario that proves the boundary works; add one rung at a time.
2. Each rung exercises the running system through the interface-appropriate harness (browser, HTTP client, CLI, MCP client).
3. Cite the acceptance criteria each rung covers with `@covers`.
4. A rung is done only when it runs green in CI, not on a developer machine alone.

Procedure: `workflows/actions/e2e-ladder.md` (the full action prompt; this file is the contract).
