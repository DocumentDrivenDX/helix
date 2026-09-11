---
title: "Runtime Handoff"
slug: runtime-handoff
weight: 200
generated: true
---

Generated from [`workflows/modes/runtime-handoff.md`](https://github.com/DocumentDrivenDX/helix/blob/main/workflows/modes/runtime-handoff.md), the mode contract the HELIX skill loads. Edit that file, not this page.

Use when a workflow mode concludes that the next step is execution, source
control, packaging, or a long-lived operator loop. HELIX does not own those
surfaces; the runtime does.

1. Name the governed work item or artifact gap that is ready for runtime
   action.
2. Name the domain lane and scope instance the runtime should preserve.
3. Name the verification evidence the runtime must record before reporting
   completion. For buildable products, this includes observable end-to-end
   evidence against the running system when feasible, plus a claims-vs-reality
   check with zero phantom claims. See the in-tree
   `workflows/concerns/verification/practices.md`, or the
   `references/concerns/verification/practices.md` floor — resolved via
   §Catalog Resolution (the floor always resolves).
4. For data-backed products, require governed sample or seed data with
   synthetic non-PII values and enough variation to exercise schema-relevant
   states. See the in-tree `workflows/concerns/sample-data/practices.md`, or the
   `references/concerns/sample-data/practices.md` floor — resolved via §Catalog
   Resolution (the floor always resolves).
5. Do not prescribe runtime commands from the skill body. Point to the
   runtime's install or operator guide for concrete execution, source control,
   packaging, or loop commands.
