# Scenario C Workflow Expectations

## Starting Input Form

### Sparse input
```text
Build a real-time collaborative document editor like Google Docs. Multiple users editing simultaneously with conflict resolution.
```

### Typical bounded beads
- sync algorithm evaluation or selection
- collaborative editing transport / websocket layer
- offline support strategy
- merge/conflict-resolution technical design

This scenario is the **complex-pressure** case. It should stress escalation quality, autonomy behavior, and preserve-vs-merge interpretation for harder design work.

## Expected Graph / Artifact Changes

Minimum planning artifacts are listed in `expected-artifacts.txt`.

Expected shape:
- PRD that captures latency, concurrency, offline, and timeline constraints
- feature split between real-time sync, conflict resolution, and offline support
- user stories for cursor tracking, change propagation, and merge behavior
- architecture decisions around sync algorithm and realtime transport
- technical designs for websocket/sync layers and reconciliation behavior
- bounded beads for experiments, design follow-up, and implementation slices

## Expected Required Validations

Required validations should confirm:
- the chosen approach addresses realtime and concurrency constraints explicitly
- conflict-resolution behavior is not hand-waved away
- offline support remains represented in the design
- artifact traceability across PRD/FEAT/ADR/TD layers is intact

## Expected Ratchets / Observations

Scenario C should emphasize observations and preserve-worthy evidence:
- runtime metrics for expensive prompt/model runs
- quality and completeness measurements across the artifact stack
- design-risk observations for latency, concurrency, and offline complexity

Possible ratchet use:
- minimum artifact-quality threshold
- minimum traceability/coherence threshold

## Autonomy-Level Expectations

### Low
- challenge risky assumptions early
- ask before each major graph step
- explicitly ask about algorithm choice and scope realism
- no DDx dispatch before approval

### Medium
- produce planning artifacts and identify major risks
- ask when sync algorithm, offline approach, or timeline assumptions become ambiguous
- escalation is appropriate for unresolved architecture choices

### High
- continue with bounded progress where possible
- create escalation beads for unresolved but non-contradictory architecture choices
- dispatch bounded DDx work only when the bead is truly narrow enough
- preserve-only outcomes are more likely here than in Scenario A because complexity is higher

## Mergeable vs Preserve-Only Expectations

### Mergeable path
A mergeable path is possible for a narrow, well-scoped bead where:
- required validations pass
- the chosen slice is bounded
- key design assumptions are documented and traceable

### Preserve-only path
Scenario C often legitimately ends as **preserve-only** when:
- the selected bead is still too exploratory
- required validations fail
- ratchet or quality thresholds are not yet met
- architecture ambiguity remains too high for safe landing

Preserve is therefore a normal outcome for some Scenario C runs, but it still must return enough DDx evidence for HELIX to decide whether to escalate, ask, or decompose further.
