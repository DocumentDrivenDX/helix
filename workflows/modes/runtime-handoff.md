# Runtime Handoff

Use when a workflow mode concludes that the next step is execution, source
control, packaging, or a long-lived operator loop. HELIX does not own those
surfaces; the runtime does.

1. Name the implementation-ready plan, explicitly selected work item, or
   artifact gap that is ready for runtime action. Follow
   `workflows/references/work-item-first.md`: a plan can govern the whole goal
   without tracker acquisition. Planning readiness does not authorize execution.
   After implementation is authorized, continue through verified completion,
   preserving continuation evidence across interruptions.
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

## Source-Code Boundaries

For handwritten source, require `modularity-and-encapsulation` evidence: adopted module map, concrete boundary-check command and supported negative controls, semantic review of public APIs/type ownership/invariants, and existing-debt/exception dispositions. Do not hand dependent feature work off as ready without these prerequisites. Bounded adoption work may create them.

## OpenTelemetry Diagnostics

Apply selected `o11y-otel` practice sections, including agent run diagnostics
where commands/tests need persistent evidence. Preserve applicability without
silently re-selecting concerns. Require safe run/attempt evidence references,
verification outcome and capture limits at execution closeout; a quiet console
is not a pass. Shared schemas stay in Contracts, with actual OTel receiver proof
for claimed integrations. See `workflows/references/agent-diagnostics.md`.
