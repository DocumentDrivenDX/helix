# Slider Autonomy Test Harness

This harness defines **observable workflow tests** for HELIX autonomy behavior on top of the DDx execution substrate.

It replaces the earlier implementation-sketch tests for regex parsing and homemade graph traversal internals. Those substrate concerns belong in DDx. This harness tests the HELIX-owned behavior contract:
- when HELIX asks
- when HELIX proceeds
- when HELIX escalates
- when HELIX dispatches bounded work to DDx
- how HELIX interprets DDx merge vs preserve outcomes

## Scope

This harness covers the **autonomy and handoff slice** of the behavior described by:
- `FEAT-011`
- `TD-011`
- `CONTRACT-001`
- `CONTRACT-002`

It does **not** attempt to cover every acceptance area in those documents. In particular, graph primitives, full impact-detection coverage, authority ordering, verification traceback, and execution-doc authoring conventions are covered elsewhere and should have their own focused tests.

This harness specifically tests:
- `low` / `medium` / `high` as **HELIX semantics**, not DDx permissions
- explicit HELIX→DDx handoff through `ddx agent execute-bead`
- resolvable vs physics-level conflict handling
- gap/speculative bead creation when the graph cannot support safe continuation
- preserve-vs-merge interpretation after bounded DDx attempts
- graph-aware planning behavior as seen through beads, questions, and dispatches

---

## Philosophy

- No invisible reasoning claims; only observable workflow outputs count.
- The test surface is the **real HELIX workflow**, not a mocked internal algorithm.
- DDx is treated as the execution substrate; HELIX is treated as the workflow supervisor.
- Every assertion must be checkable from a transcript, bead state, or DDx outcome summary.
- Preserve outcomes are not failures by default; they are workflow-relevant results.

---

## Required Observable Surfaces

Each autonomy run must emit enough evidence to judge behavior from the outside.

### HELIX-side evidence
- input request or bead selector
- selected autonomy level
- questions asked to the user, if any
- beads created or updated
- escalation beads created, if any
- summary of intended graph impact / downstream work
- supervisory decision: ask, dispatch, continue, escalate, or block

### DDx-side evidence
- explicit dispatch event to `ddx agent execute-bead <bead-id> [--from <rev>] [--no-merge]`
- attempt outcome: merged or preserved
- required execution summary
- ratchet summary
- runtime evidence with at least:
  - harness
  - model
  - session ID
  - elapsed duration
  - token usage
  - cost
  - base revision
  - result revision

### Tracker evidence
- created follow-up beads
- escalation beads (`kind:escalation`) when applicable
- speculative or gap beads if policy creates them

If these surfaces are missing, the harness cannot pass because the workflow is not observable enough.

---

## Common Test Inputs

Use scenario fixtures under `tests/scenarios/` once they are updated for the DDx-backed workflow.

Each scenario should provide:
- vision / intent
- constraints
- expected artifacts
- `workflow.md` describing starting input/bead form, autonomy-specific behavior, validations, and merge-vs-preserve interpretation
- expected execution-doc / ratchet interpretation where relevant

### Scenario roles

| Scenario | Primary use |
|---|---|
| A | low-noise baseline for ask-first vs autonomous behavior |
| B | resolvable ambiguity and operational constraints |
| C | complex planning, escalation quality, bounded autonomy under pressure |
| Contradiction fixture | true physics-level blocking behavior |

The contradiction fixture may be a dedicated small test input rather than a full scenario.

---

## Evidence Record Per Run

For each test run, capture a record with at least these fields:

```yaml
run:
  scenario: A
  autonomy: low
  input: "build a REST API for managing user profiles"
  base_revision: <sha>
  bead_ids_created:
    - hx-...
  questions_asked:
    - "Which OAuth provider should we start with?"
  dispatches:
    - bead: hx-...
      command: ddx agent execute-bead <bead-id> --from <rev> --no-merge
  ddx_outcomes:
    - bead: hx-...
      result: preserved
      required_executions: fail
      ratchets: pass
      runtime:
        harness: agent  # DDx harness backed by the ddx-agent binary
        model: qwen3.5-27b
        session_id: s-...
        elapsed_ms: 12345
        tokens: 9876
        cost_usd: 0.42
        base_revision: abc1234
        result_revision: def5678
  supervisory_outcome: ask
```

The exact serialization can vary. The fields themselves are the contract.

---

## Expected Behavior Summary by Autonomy Level

| Autonomy | Expected HELIX behavior |
|---|---|
| `low` | Ask before each graph step and before each downstream artifact creation; do not dispatch DDx work without approval |
| `medium` | Traverse and plan autonomously; ask when ambiguity or conflict blocks deterministic progress |
| `high` | Continue end-to-end unless a physics-level contradiction blocks the workflow; create escalation beads for resolvable conflicts; dispatch DDx work when a bounded bead is ready |

Important:
- a DDx **preserve** outcome ends the current bounded attempt and returns control to HELIX
- a DDx preserve outcome is **not** automatically a physics-level conflict
- physics-level conflicts block the supervisory workflow before or during planning because the governing intent is contradictory

---

## Test Matrix

| Test | Scenario / fixture | Autonomy | Main assertion |
|---|---|---|---|
| 1 | A | low | ask before first graph step |
| 2 | A | low | ask before downstream artifact creation |
| 3 | B | medium | autonomous traversal, ask on ambiguity |
| 4 | B | high | resolvable conflict creates escalation bead and still dispatches |
| 5 | contradiction fixture | high | physics-level conflict blocks before DDx dispatch |
| 6 | missing-link fixture | medium/high | gap/speculative bead is created when required upstream support is missing |
| 7 | B or C | high | DDx preserve returns to HELIX as preserve-only result, not physics-level |
| 8 | A or B | medium/high | DDx merge outcome allows HELIX to continue/report |

---

## Test 1: Low Autonomy Asks Before First Graph Step

**Goal:** verify `low` autonomy is truly ask-first.

### Setup
- Use Scenario A or another simple fixture with a clear path.
- Start from sparse user intent through `helix input "..." --autonomy low` once that surface exists.
- Equivalent pre-command test setup is acceptable if it preserves the same workflow semantics.

### Input
```text
"Build a CLI tool that converts temperatures between Celsius, Fahrenheit, and Kelvin."
```

### Expected observable behavior
- HELIX does **not** immediately create downstream artifacts.
- HELIX asks at least one explicit approval question before the first graph/planning step.
- HELIX does **not** dispatch `ddx agent execute-bead` yet.

### Pass criteria
- `questions_asked >= 1` before any downstream artifact creation
- `dispatches = 0`
- no implementation bead is executed yet

### Fail examples
- HELIX immediately creates PRD / FEAT / TD artifacts without asking
- HELIX dispatches DDx work before user approval

---

## Test 2: Low Autonomy Asks Before Each Downstream Artifact Creation

**Goal:** verify low autonomy asks repeatedly, not just once.

### Setup
- Continue from Test 1 after the user approves the first step.
- Use a fixture where at least two downstream artifacts would normally be created.

### Expected observable behavior
Before each new downstream artifact or major graph step, HELIX asks again.

Examples:
- ask before creating the PRD
- ask before decomposing into features
- ask before creating a technical-design bead

### Pass criteria
- for a run that reaches `n` downstream artifact-creation steps, HELIX records `n` corresponding approvals or questions
- no silent batch creation of multiple downstream artifacts under low autonomy
- no DDx dispatch occurs until the relevant implementation bead is explicitly approved

### Fail examples
- HELIX asks once, then bulk-creates the rest
- HELIX silently transitions from planning to execution

---

## Test 3: Medium Autonomy Traverses Autonomously but Asks on Ambiguity

**Goal:** verify `medium` is guided autonomy, not ask-first and not full-autonomy.

### Setup
Use Scenario B or similar input with a real ambiguity such as auth-provider choice.

### Input
```text
"Build a REST API for managing user profiles with OAuth authentication. Needs to scale to 10k users initially."
```

### Expected observable behavior
- HELIX traverses the graph and creates or proposes the deterministic planning work without asking at every step.
- HELIX asks when an ambiguity blocks deterministic progress.
- HELIX does not classify ordinary design choices as physics-level contradictions.

### Observable ambiguity examples
- which OAuth provider to start with
- default rate-limit values
- framework choice when several options satisfy constraints equally

### Pass criteria
- some planning beads or artifact intentions are produced without a per-step approval loop
- at least one question or escalation appears for the true ambiguity
- if execution is not yet blocked, HELIX may still prepare bounded beads for later DDx dispatch

### Fail examples
- medium behaves like low and asks before every step
- medium behaves like high and silently assumes all ambiguous details without surfacing them

---

## Test 4: High Autonomy Escalates Resolvable Conflicts but Still Dispatches

**Goal:** verify `high` autonomy continues through resolvable conflicts.

### Setup
Use Scenario B or C with a resolvable conflict, such as an implementation choice where multiple valid options exist.

### Example resolvable conflict
- PostgreSQL is required, but partitioning / hosting / OAuth-provider choice is still open
- a design tradeoff exists without contradiction in the governing intent

### Expected observable behavior
- HELIX creates an escalation bead for the unresolved choice if traceability requires it
- HELIX continues creating bounded work instead of blocking the whole workflow
- once a bead is ready, HELIX dispatches DDx execution

### Pass criteria
- at least one `kind:escalation` bead is created for the resolvable issue
- supervisory outcome is **continue** or **dispatch**, not **block**
- at least one DDx dispatch occurs:

```bash
ddx agent execute-bead <bead-id> --from <rev> --no-merge
```

### Fail examples
- resolvable conflict is treated as physics-level and blocks everything
- no escalation bead is recorded despite ambiguity requiring traceability
- high autonomy still asks the user before every move

---

## Test 5: Physics-Level Conflict Blocks Before DDx Dispatch

**Goal:** verify true contradictions stop the supervisory workflow.

### Setup
Use a dedicated contradiction fixture.

### Input
```text
Requirements:
- System must process requests in real time (<100ms)
- All processing must be batch-only
```

### Expected observable behavior
- HELIX classifies this as physics-level
- HELIX blocks supervisory progress
- HELIX does not dispatch bounded implementation work to DDx for the contradictory path
- HELIX asks for human resolution or creates a blocking escalation record

### Pass criteria
- conflict class is recorded as physics-level
- supervisory outcome is **block** or **ask for resolution**
- `dispatches = 0` for the blocked path

### Fail examples
- HELIX creates implementation beads and dispatches anyway
- HELIX downgrades the contradiction to an ordinary escalation bead and continues silently

---

## Test 6: Missing Graph Support Creates a Gap / Speculative Bead

**Goal:** verify HELIX records missing-support cases explicitly instead of silently continuing.

### Setup
Use a fixture where the requested downstream work depends on an upstream artifact, execution doc, or graph link that does not yet exist or is clearly incomplete.

Examples:
- a requested change implies a TD or TP that has no governing upstream artifact yet
- a bounded bead is ready in principle, but required supporting graph context is absent

### Expected observable behavior
- HELIX does not silently invent hidden context and proceed as if the graph were complete
- HELIX creates a follow-up bead to represent the gap
- the bead is marked as speculative / gap work according to the workflow policy in force
- HELIX may continue other safe work, but the missing-support path stays explicit

### Pass criteria
- at least one bead is created for the missing-support condition
- the bead is labeled or classified as `kind:speculative`, gap work, or equivalent explicit missing-context state
- the transcript or summary explains what governing support is missing

### Fail examples
- HELIX silently proceeds as though the missing upstream artifact existed
- HELIX drops the missing-support path without a bead

---

## Test 7: DDx Preserve Outcome Returns Control to HELIX Without Reclassifying the Conflict

**Goal:** verify preserve handling matches the boundary contract.

### Setup
Use a bead whose linked required executions can fail in a controlled way.
Examples:
- required execution doc fails
- ratchet floor regresses

### Expected DDx outcome
- DDx returns `preserved`
- required execution summary and/or ratchet summary explains why the attempt did not land

### Expected HELIX behavior
- HELIX interprets the attempt as preserve-only
- HELIX does **not** label the result itself as a physics-level conflict
- HELIX chooses a supervisory next step such as:
  - ask for input
  - create a follow-up bead
  - escalate
  - revise prompt/workflow wording

### Pass criteria
- DDx outcome recorded as `preserved`
- HELIX outcome recorded as one of: `ask`, `escalate`, `follow-up`, `revise`
- no false `physics-level` classification unless the governing intent is separately contradictory

### Fail examples
- every preserve is treated as a workflow-halting contradiction
- HELIX loses the DDx evidence and cannot explain why the attempt was preserved

---

## Test 8: DDx Merge Outcome Allows Workflow Continuation

**Goal:** verify successful bounded execution feeds the next HELIX step.

### Setup
Use a simple merge-eligible bead from Scenario A or B.

### Expected DDx outcome
- `merged`
- required executions pass
- ratchets pass

### Expected HELIX behavior
After a merged outcome, HELIX continues to the next supervisory step, such as:
- measure
- report
- next bead selection
- additional bounded dispatch if the workflow requires it

### Pass criteria
- DDx outcome recorded as `merged`
- HELIX records a continuation step rather than asking for conflict resolution
- no preserve-only or contradiction language is attached to the merged attempt

---

## Comparison Rules Across Autonomy Levels

Use these cross-checks to avoid false positives.

### Low vs Medium
- If both behave the same, the test fails.
- Low must ask earlier and more often.
- Medium must proceed further before asking.

### Medium vs High
- If both stop on resolvable ambiguity, the test fails.
- High must continue via escalation beads where medium may ask.

### High vs Physics-Level Fixture
- High must continue through resolvable conflicts.
- High must still stop on true contradictions.

---

## Minimal Result Table

Use a table like this for each test set:

| Test | Scenario | Autonomy | Questions | Escalation beads | Gap/spec beads | DDx dispatches | DDx outcome | Supervisory outcome | Pass? |
|---|---|---|---:|---:|---:|---:|---|---|---|
| 1 | A | low | 2 | 0 | 0 | 0 | none | ask | pass |
| 3 | B | medium | 1 | 0 | 0 | 0 or 1 | none/preserved | ask | pass |
| 4 | B | high | 0 | 1 | 0 | 1 | preserved | continue then escalate | pass |
| 5 | contradiction | high | 1 | 0 or 1 | 0 | 0 | none | block | pass |
| 6 | missing-link | medium/high | 0 or 1 | 0 | 1 | 0 or 1 | none/preserved | follow-up | pass |
| 7 | B | high | 0 | 1 | 0 | 1 | preserved | follow-up | pass |
| 8 | A | high | 0 | 0 | 0 | 1 | merged | continue | pass |

---

## Merge Gate for FEAT-011

Before slider autonomy can move beyond planning, this harness should demonstrate:

- [ ] low autonomy asks before graph progression and downstream artifact creation
- [ ] medium autonomy proceeds deterministically and asks on ambiguity/conflict
- [ ] high autonomy escalates resolvable conflicts without blocking the whole workflow
- [ ] physics-level contradictions block supervisory progress
- [ ] missing-support conditions create explicit gap/speculative beads instead of silent continuation
- [ ] HELIX dispatches bounded work through `ddx agent execute-bead`
- [ ] DDx preserve outcomes are visible and interpreted correctly by HELIX
- [ ] DDx merge outcomes allow workflow continuation
- [ ] results are observable from transcript, tracker, and DDx outcome evidence, including minimum runtime fields from `CONTRACT-001`

---

## Failure Classification

When a test fails, classify the failure.

### HELIX semantic failure
Examples:
- low autonomy failed to ask
- medium autonomy asked too early or too often
- high autonomy blocked on a resolvable conflict
- preserve outcome was misclassified as physics-level

### Fixture failure
Examples:
- scenario did not contain a real ambiguity
- contradiction fixture was not actually contradictory
- expected behavior was underspecified

### DDx substrate failure
Examples:
- no visible execute-bead dispatch evidence
- preserved attempt evidence missing
- required execution or ratchet summaries not surfaced

Only semantic failures should directly drive changes to FEAT-011 / TD-011 behavior. Fixture and substrate failures should create follow-up beads.

---

## Relationship to Other Test Docs

- `tests/prompt-engineering-harness.md` compares prompt variants using preserved bead attempts.
- `docs/helix/06-iterate/prompt-iteration-protocol.md` defines the repeatable scoring rubric and decision loop for those experiments.
- `tests/scenarios/` provides reusable scenario fixtures.
- `CONTRACT-001` defines the DDx / HELIX ownership split.
- `CONTRACT-002` defines the execution-doc conventions that make required-execution and ratchet behavior discoverable.

This harness focuses on one question:

**Does HELIX exhibit the intended low / medium / high workflow behavior on top of DDx-managed execution?**
