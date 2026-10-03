---
title: "Evolve"
slug: evolve
weight: 80
generated: true
---

Generated from [`workflows/modes/evolve.md`](https://github.com/DocumentDrivenDX/helix/blob/main/workflows/modes/evolve.md), the mode contract the HELIX skill loads. Edit that file, not this page.

Use when the user asks to add, amend, remove, or thread a requirement through
existing artifacts.

1. Start with the named entry artifact and the relevant authority. Follow
   `ddx.links` only where a relationship can affect this change; use the
   activity hierarchy when links are absent. Do not traverse the whole project
   by default.
2. Identify affected downstream artifacts from relevant links, direct
   references, and the requested behavior. Preserve legacy relationship fields
   as written; do not migrate them incidentally.
3. Surface conflicts instead of silently overwriting lower-authority content.
   An accepted ADR establishes the chosen direction; it does not establish that
   implementation is complete.
4. Update the affected artifacts from highest authority to lowest. Preserve the
   user's intended requirement strength and edit only within the authorized
   scope.
5. Summarize changed, unchanged, and unresolved artifacts with evidence. Create
   tracker work or add gates only when requested or required by a runtime
   consumer. Keep the output conversational unless a structured report is
   requested.

Procedure: `workflows/actions/evolve.md` supplies additional detail.
