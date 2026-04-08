# FEAT-011: Slider Autonomy Control

**Status**: Planning  
**Priority**: P1  
**Created**: 2026-04-07  
**Related ADRs**: [ADR-001](../../02-design/adr/ADR-001-supervisory-control-model.md) (supervisory control model)

## Problem Statement

Current HELIX has 15+ skills that mirror CLI commands. This creates cognitive load and doesn't match the actual user workflow, which is:

1. **Two primary modes**: "take design input" vs "work the queue"
2. **Human input is sparse**: "design a CRM", "use postgres", "make logout blue", "here's a bug"
3. **Agent must maintain artifact stack coherence**: Vision → PRD → Specs → ADRs → Designs → Tests → Code

The current command-centric model doesn't support:
- Natural language input interpretation
- Cross-cutting concern enforcement (e.g., "use postgres" should check existing SQLite ADR)
- Human-agentic continuum (sometimes human does work, sometimes agent runs away)
- Non-blocking conflict escalation
- **Automated artifact graph traversal**

## Requirements

### FR-01: Artifact Graph Metadata (Based on Existing Hierarchy)
Each artifact shall declare its connections using the existing HELIX cross-reference pattern:

```markdown
# TD-036-list-mcp-servers.md
**User Story**: [[US-036-list-mcp-servers]]
**Parent Feature**: [[FEAT-001-mcp-server-management]]
**Solution Design**: [[SD-001-mcp-management]]
```

Graph metadata includes:
- **Upstream dependencies**: Higher-authority artifacts (PRD, FEAT, SD) that govern this one
- **Downstream dependents**: Lower-authority artifacts (TD → TP → tests → code) derived from this one
- **Peer relationships**: Same-level artifacts (US-036 ↔ US-037 in same feature)

**Storage**: Cross-references embedded in artifact frontmatter/body using `[[ID]]` notation. No separate registry needed initially.

### FR-02: Impact Detection via Search + Declared Links
The system shall identify impacted artifacts through two-phase detection:

1. **Declared links first**: Follow existing `[[ID]]` cross-references from changed artifact
2. **Search-based fallback**: Use `rg` to find term matches (e.g., "Postgres" → ADRs about database choice)

**Precedence**: Declared links take precedence over search results to avoid false positives. Search only supplements when declared links are incomplete.

### FR-03: Graph Traversal and Change Flow
Once impacted artifacts are identified, the system shall:

1. **Trace the graph**: Follow upstream/downstream connections from impact point
2. **Order by authority**: Process in canonical order (Vision → PRD → FEAT → US → SD → TD → TP → Tests → Code)
   - Note: ADRs can appear at multiple levels; they govern both specs AND designs
3. **Flow changes**: Propagate modifications through each layer as atomic diffs
4. **Create downstream work**: Generate beads for artifacts that need updating

**Cycle handling**: Traversal uses visited set to prevent infinite loops on peer relationships.

### FR-04: Physics-Level vs Resolvable Conflict Detection
The system shall distinguish between:

| Type | Definition | Example | Action |
|------|-----------|---------|--------|
| **Resolvable** | Different approaches to same goal | Postgres vs SQLite for database | Escalate via bead, continue with documented assumption |
| **Physics-level** | True contradictions that cannot coexist | "must be real-time" + "batch processing only" | Block execution, require human resolution |

High autonomy mode proceeds through resolvable conflicts; blocks only on physics-level.

DDx preserve outcomes from bounded execution attempts (for example failed required executions or ratchet regressions) are **not** physics-level conflicts. They terminate the current DDx-managed attempt and hand control back to HELIX for escalation, follow-on beads, or user input.

### FR-05: Autonomy Slider Controls Flow Behavior
The system shall support configurable autonomy level (per session or project):

| Level | Behavior | Use Case |
|-------|----------|----------|
| **Low** | Ask before each graph step and before creating each downstream artifact; do **not** make changes until the user approves | Learning mode, critical systems |
| **Medium** | Traverse graph autonomously, ask only on conflicts/ambiguity | Default for most work |
| **High** | Continue end-to-end autonomously; escalate resolvable conflicts as non-blocking beads; only physics-level conflicts stop the supervisory workflow, while DDx preserve outcomes end the current bounded attempt and hand control back to HELIX | Trusted contexts, rapid iteration |

### FR-06: Minimal CLI Surface (Backward Compatible)
CLI commands reduce to two core capabilities while maintaining backward compatibility:

1. **Input command**: `helix input "<natural language>"` - accepts sparse input, triggers graph traversal
2. **Execute command**: `helix run` - executes beads from queue (existing behavior preserved)

**Deprecation timeline**: Legacy commands (`design`, `build`, etc.) remain functional but route through new model. Deprecation warnings added in v0.4.x, removal in v1.0.

### FR-07: Bead-Centric Coordination
All work flows through beads (non-blocking for resolvable conflicts):

- User input → [Bead: Request]
- Agent refines → [Children: Questions/Decisions]
- Conflicts → [Bead: Escalation - non-blocking, label `kind:escalation`]
- Gaps → [Bead: Gap - speculative, label `kind:speculative`]

Workers execute from the bead queue without blocking on resolvable conflicts. Physics-level conflicts block only the affected worker path.

### FR-08: Verification Loop and Traceability
The system shall verify that artifact flow produces **functional, measurable results**:

#### Traceability Model (Based on Existing Pattern)
```
FEAT-001 → SD-001 → US-036 → TD-036 → TP-036 → tests → code
         ↓
         US-037 → TD-037 → TP-037 → tests → code
```

Each layer references upstream via `[[ID]]` notation. Tests reference spec IDs in comments or metadata.

#### Failure Triage Algorithm
When verification fails:
1. **Classify failure type**:
   - Test bug (test wrong) → create bead for test fix
   - Implementation bug (code wrong) → create bead for code fix  
   - Spec conflict (spec contradicts upstream) → trace back to spec, create escalation bead
2. **Trace back through graph** using `[[ID]]` references: failing test → TP → TD → US/FEAT → PRD
3. **Identify adjustment point**: nearest upstream artifact that directly specifies the failing behavior
4. **Create follow-on beads** for resolution

#### Metrics and Non-Functional Requirements
For non-testable constraints (latency, security, compliance):
- Define named metrics in artifacts (e.g., "P95 < 100ms" in PRD)
- Automated checks collect metrics continuously
- Threshold violations trigger reflow via beads

## DDx Substrate vs HELIX Workflow Ownership

This section summarizes the canonical boundary defined in [`CONTRACT-001`](../../02-design/contracts/CONTRACT-001-ddx-helix-boundary.md). If this feature text and the contract diverge, the contract is authoritative.

**DDx owns the substrate**:
- graph primitives (`[[ID]]` indexing, upstream/downstream traversal, reverse lookup)
- graph-discovered execution docs and required validation execution
- managed bead execution via `ddx agent execute-bead <bead-id> [--from <rev>] [--no-merge]`
- runtime evidence capture, execution runs, metric projection, ratchet evaluation, and merge/preserve mechanics

**HELIX owns the workflow semantics**:
- autonomy behavior (`low` / `medium` / `high`)
- authority ordering and artifact-flow policy
- conflict classification and escalation behavior
- workflow routing (`helix input`, `helix run`, follow-on bead creation)
- prompt design and prompt-engineering strategy

**Handoff contract**: HELIX decides scope, autonomy behavior, and workflow context; DDx executes the bounded bead and returns runtime evidence plus merge/preserve outcome; HELIX interprets that result to continue, escalate, or ask for input.

## Acceptance Criteria

### AC-01: Artifact Graph Metadata
- [ ] Existing `[[ID]]` cross-reference pattern works for graph traversal
- [ ] Traversal can follow declared connections automatically (tested with fixture artifacts)
- [ ] Search-based impact detection supplements declared relationships when links incomplete

### AC-02: Impact Detection and Traversal  
- [ ] Given sample artifact graph, change in PRD produces exactly expected downstream beads
- [ ] Graph traversal follows canonical authority order with ADR exceptions handled correctly
- [ ] Cycle detection prevents infinite loops on peer relationships

### AC-03: Conflict Classification
- [ ] System distinguishes resolvable vs physics-level conflicts (test cases defined)
- [ ] Resolvable conflicts create escalation beads and continue with documented assumptions
- [ ] Physics-level conflicts block execution and require human resolution

### AC-04: Autonomy Slider Behavior
- [ ] Low autonomy: asks before each graph step and before creating each downstream artifact, human approves flow (verified via test scenarios)
- [ ] Medium autonomy: autonomous traversal, asks on conflicts/ambiguity (default behavior)
- [ ] High autonomy: full autonomous flow ("until blocked"), escalates resolvable conflicts via beads and blocks only physics-level conflicts at the supervisory level

### AC-05: CLI Simplification (Backward Compatible)
- [ ] `helix input "<text>"` command accepts natural language and triggers graph traversal
- [ ] `helix run` continues to execute beads from queue without behavior change
- [ ] Legacy commands (`design`, `build`, etc.) route through new model with deprecation warnings

### AC-06: Verification Loop
- [ ] 100% of tests reference spec IDs (via comments or metadata)
- [ ] Failed verification traces back through graph to identify adjustment point (tested with fixtures)
- [ ] New constraints discovered during verification create follow-on beads for resolution
- [ ] Metrics thresholds defined and trigger reflow when violated

### AC-07: Backward Compatibility
- [ ] Existing CLI commands continue to work during transition period
- [ ] Existing skills remain functional (may be deprecated but not broken)
- [ ] `helix run` loop continues to function with new bead types (`kind:escalation`, `kind:speculative`)

### AC-08: DDx Handoff Is Observable
- [ ] HELIX dispatches bounded implementation/verification work through `ddx agent execute-bead` rather than an implicit internal execution path
- [ ] Preserve-vs-merge outcomes returned by DDx are observable inputs to HELIX workflow behavior (continue, escalate, or ask)
- [ ] A DDx preserve outcome ends the current bounded attempt and returns control to HELIX without being misclassified as a physics-level conflict
- [ ] Runtime evidence returned by DDx is sufficient for HELIX to interpret required execution outcomes and ratchet results without building a parallel execution store

## Non-Requirements

- This feature does NOT replace the existing CLI/skill contract immediately (deprecation timeline defined)
- This feature does NOT eliminate phase enforcers (they become parameterized by slider)
- This feature is NOT production-ready until fully tested in sandbox branch
- This feature does NOT require new artifact storage format (uses existing `[[ID]]` pattern)

## Dependencies

- DDx tracker must support custom labels for escalation/gap/speculative beads (`kind:escalation`, `kind:speculative`)
- Artifact stack must have complete `[[ID]]` cross-references for reliable traversal
- Slider config schema needs to be defined and validated (`.helix/slider-config.yaml`)
- DDx must provide the substrate defined in [`CONTRACT-001: DDx / HELIX Boundary Contract`](../../02-design/contracts/CONTRACT-001-ddx-helix-boundary.md), including graph primitives, managed bead execution, and runtime evidence capture

### Autonomy Scope Contract (Explicit)
- `low`: **ask-first** — do not proceed without explicit user confirmation per step and per downstream artifact creation
- `medium`: **guided-autonomy** — ask when ambiguity or conflict blocks deterministic progress
- `high`: **high-autonomy** — run to completion unless physics-level constraints stop progress; ordinary DDx preserve outcomes end the current bounded attempt and return control to HELIX, but are not themselves physics-level conflicts

`helix input` SHOULD expose this as `--autonomy`.

## Risks

1. **Breaking existing workflows**: If we replace skills too aggressively, automation breaks → Mitigation: deprecation timeline, backward compatibility
2. **Silent divergence**: Speculative work might drift from intent without proper reconciliation → Mitigation: escalation beads with documented assumptions
3. **Cognitive load shift**: Users need to understand slider settings and their implications → Mitigation: clear documentation, sensible defaults
4. **Graph traversal complexity**: Following artifact relationships correctly is non-trivial → Mitigation: start with declared links only, add search as supplement

## Success Metrics

- Reduced skill count (from 15+ to 2 core + optional specialized)
- Faster time from input to first artifact creation
- Higher quality conflict detection (fewer silent drifts)
- User satisfaction with autonomy level control
- **Automated change flow through artifact graph works reliably** (tested with fixtures)
- **Verification loop closes successfully**: tests pass, metrics met, failures trigger correct reflow
- **Functional artifacts produced**: each layer produces measurable, verifiable output

## References

- [Artifact Hierarchy](../../../workflows/artifact-hierarchy.md) - canonical authority order and naming
- [ADR-001: Supervisory Control Model](../../02-design/adr/ADR-001-supervisory-control-model.md) - helix-run as supervisor
- [CONTRACT-001: DDx / HELIX Boundary Contract](../../02-design/contracts/CONTRACT-001-ddx-helix-boundary.md) - platform/workflow ownership split
- [CONTRACT-002: HELIX Execution-Document Conventions](../../02-design/contracts/CONTRACT-002-helix-execution-doc-conventions.md) - how HELIX authors execution docs, metrics, and ratchet-backed validations for DDx discovery
- [DDx BEAD Tracker](../features/FEAT-004-ddx-bead-tracker.md) - execution tracking conventions

---

*This feature is in PLANNING mode. Do not implement until technical design document (TD-011) is approved and beads are created through proper HELIX workflow.*
