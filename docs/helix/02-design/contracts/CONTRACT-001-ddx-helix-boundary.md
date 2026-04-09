# CONTRACT-001: DDx / HELIX Boundary Contract

**Status:** Draft  
**Owner:** HELIX maintainers  
**Related:** [Product Vision](../../00-discover/product-vision.md), [FEAT-011](../../01-frame/features/FEAT-011-slider-autonomy.md), [ADR-001](../adr/ADR-001-supervisory-control-model.md)

## Purpose

This contract defines the ownership boundary between **DDx** and **HELIX**.

- **DDx** is the platform substrate.
- **HELIX** is the workflow and methodology layer built on that substrate.

The goal is to keep execution/storage/platform concerns in DDx while keeping
workflow semantics, autonomy behavior, and prompt strategy in HELIX.

This contract exists to prevent two common failure modes:
1. HELIX re-implementing platform capabilities DDx already provides
2. DDx absorbing HELIX-specific workflow behavior and becoming methodology-bound

## DDx-Owned Substrate Responsibilities

HELIX expects DDx to provide these platform capabilities.

### 1. Graph primitives
- Document graph indexing
- `[[ID]]` body-link indexing in addition to frontmatter dependencies
- Upstream/downstream traversal primitives
- Reverse/dependent lookup primitives
- Discovery of graph-authored execution documents

### 2. Agent execution substrate
- `ddx agent run` as the general harness interface
- `ddx agent execute-bead <bead-id> [--from <rev>] [--no-merge]` as the
  canonical git-aware bead execution primitive HELIX expects to call
- Standard harness/model/effort/preset controls available through the DDx agent surface
- Session capture, transcript capture, and runtime evidence capture

### 3. Execution and metric substrate
- Graph-authored execution documents as authoritative definitions
- Immutable execution runs stored in the DDx execution substrate
- Metric projection over execution runs
- Required execution semantics sufficient to decide merge vs preserve
- Metric ratchet evaluation sufficient to decide merge vs preserve

### 4. Git-context execution mechanics
- Dirty-tree checkpointing before managed execution
- Isolated worktree execution
- Preserved hidden refs for non-landed attempts
- Rebase only to prepare fast-forward landing
- Fast-forward landing when merge-eligible
- Guaranteed worktree cleanup after landing or preservation

### 5. Always-on runtime metrics and provenance
For every managed execute-bead attempt, DDx should capture runtime facts such as:
- harness
- model
- session ID
- elapsed duration
- token usage
- cost
- base revision
- result revision

### 6. Repo-local DDx configuration surfaces
- `.ddx/config.yaml`
- installed DDx skills/bootstrap assets
- preset/model resolution surfaces used by HELIX

## HELIX-Owned Workflow / Methodology Responsibilities

HELIX owns workflow behavior on top of the DDx substrate.

### 1. Autonomy semantics
HELIX defines what `low`, `medium`, and `high` autonomy mean behaviorally.
DDx does not own these semantics.

### 2. Workflow routing and supervision
HELIX owns:
- `helix input`
- `helix run`
- planning vs execution routing
- supervisory stop/continue behavior
- when to ask for human input

### 3. Artifact-flow policy
HELIX owns:
- authority ordering across artifact layers
- change propagation policy through the artifact stack
- graph traversal policy beyond the primitive graph operations DDx exposes
- search fallback policy when declared links are incomplete

### 4. Conflict and escalation policy
HELIX owns:
- resolvable vs physics-level conflict classification
- the vocabulary and meaning of those conflict classes
- escalation behavior
- follow-on bead creation
- interpretation of preserved attempts for workflow continuation

The conflict taxonomy is HELIX-defined:
- **Resolvable**: workflow may continue with escalation, assumptions, or follow-on beads
- **Physics-level**: workflow must stop for human resolution because the governing intent is genuinely contradictory

DDx may return execution outcomes such as merged or preserved, but it does not define HELIX conflict classes.

HELIX interprets each bead as a governed workspace-state transformation:

- bead `B` defines the intended transition from workspace state `W` to
  successor workspace state `W'`
- the execution run is the attempt and evidence record for realizing `B : W -> W'`
- the execution outcome describes how that attempt landed
- the state delta is the realized material change between `W` and `W'`

### 5. Prompt and workflow strategy
HELIX owns:
- prompt design
- prompt engineering strategy
- bead prompt structure
- workflow wording and intervention policy
- execution-document authoring conventions for HELIX artifacts (see [CONTRACT-002](CONTRACT-002-helix-execution-doc-conventions.md))

## Shared Integration Objects

These objects are shared across the boundary and should keep stable meanings.

| Object | DDx role | HELIX role |
|---|---|---|
| **Bead** | tracker record + execution target | intended workspace-state transform (`B : W -> W'`) |
| **Workspace state** | execution substrate input/output surface | governed current/successor state under workflow interpretation |
| **State delta** | realized material diff between workspace states | workflow-visible change to inspect during measure/report |
| **Graph artifact** | indexed document node | governance/context layer |
| **Execution doc** | discovered executable validation definition | authored validation contract |
| **Execution run** | immutable evidence record | workflow input for measure/report/iteration |
| **Metric** | structured runtime observation | workflow signal |
| **Ratchet** | threshold/baseline evaluation | policy input for workflow decisions |
| **Preserved attempt** | non-landed managed execution result | experiment/review/iteration input |

## Workflow Handoff Points

### HELIX -> DDx
HELIX decides:
- what bead should be worked
- what autonomy behavior should apply
- what workflow prompt/context to use
- when implementation/verification should be dispatched

HELIX then hands execution to DDx through managed agent/execution surfaces.

### DDx -> HELIX
DDx returns evidence, not workflow policy:
- execution outcome
- required execution results
- ratchet results
- runtime metrics
- landed vs preserved outcome
- transcript/session/exec evidence locations

Minimum workflow-visible outcome surface expected by HELIX:
- merge vs preserve state
- required execution pass/fail summary
- ratchet pass/fail summary
- enough runtime evidence to inspect why the bounded attempt landed or was preserved

A preserved outcome is an execution result from a bounded DDx-managed attempt. It is not, by itself, a HELIX physics-level conflict; it hands control back to HELIX for workflow interpretation.

HELIX then decides what to do next:
- continue
- escalate
- ask for input
- create follow-on beads
- revise prompts/workflow wording

## Anti-Drift Rules

### DDx must not absorb
- HELIX autonomy semantics
- HELIX workflow routing logic
- HELIX escalation policy
- HELIX prompt engineering strategy
- HELIX artifact decomposition policy

### HELIX must not build in parallel
- a second graph engine if DDx provides graph indexing/traversal
- a second execution store
- a second metrics/provenance store
- a separate prompt-version registry
- custom git execution mechanics that bypass the DDx managed execution flow

## Validation Checklist

The boundary is healthy when all of the following are true:

- [ ] HELIX uses DDx graph primitives instead of a parallel graph implementation for document indexing/traversal
- [ ] HELIX uses DDx-managed bead execution instead of directly inventing its own execution/provenance substrate
- [ ] DDx provides enough runtime evidence for HELIX to evaluate preserved attempts and landed runs
- [ ] HELIX autonomy behavior is documented in HELIX, not DDx
- [ ] DDx execution/metric/git semantics are documented in DDx, not redefined in HELIX
- [ ] Preserved attempts, execution runs, and runtime metrics have one authoritative home in DDx
- [ ] HELIX workflow docs describe how they consume DDx results rather than duplicating DDx implementation details

## References

- [Product Vision](../../00-discover/product-vision.md)
- [FEAT-011: Slider Autonomy Control](../../01-frame/features/FEAT-011-slider-autonomy.md)
- [ADR-001: HELIX Supervisory Control Model](../adr/ADR-001-supervisory-control-model.md)
- [API-001: HELIX Tracker Mutation Surface](API-001-helix-tracker-mutation.md)
- [CONTRACT-002: HELIX Execution-Document Conventions](CONTRACT-002-helix-execution-doc-conventions.md)
