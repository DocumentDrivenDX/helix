# HELIX Prompt Engineering Harness (DDx-Backed Workflow)

This harness retargets prompt experiments from raw `ddx agent run` artifact generation to the HELIX→DDx execution flow.

The experiment unit is a **preserved bead attempt** produced by:

```bash
ddx agent execute-bead <bead-id> --from <rev> --no-merge
```

That keeps prompt iteration grounded in the real workflow surface:
- HELIX chooses the bead, autonomy behavior, and evaluation rubric
- DDx executes the bead from a fixed git revision
- DDx returns preserved-attempt evidence, required execution outcomes, ratchet results, and runtime metrics
- HELIX compares those outcomes and revises prompt or workflow wording

## Purpose

Use this harness to answer questions like:
- Does a prompt change improve bead execution quality?
- Does a prompt change improve low / medium / high autonomy behavior?
- Does a model or harness change improve outcomes for the same bead?
- Does a prompt change increase merge-eligible outcomes instead of preserve-only outcomes?

This harness is for **real runs with real models and real outputs**. Virtual replay is useful elsewhere, but not for prompt-engineering decisions.

## Assumptions

This harness assumes the DDx execution substrate exists with the following visible surface:
- `ddx agent execute-bead <bead-id> [--from <rev>] [--no-merge]`
- graph-discovered execution docs
- required execution semantics
- runtime evidence emitted for each attempt
- preserved non-merged attempts that remain inspectable
- merge-or-preserve outcomes returned to HELIX

Where DDx output formatting is still under development, the harness specifies **what must be observed**, not a final wire format.

---

## Core Principles

- Test the **real HELIX workflow**, not a simplified artifact-spam path.
- Keep **git history canonical**: prompt variants are compared from the same base revision.
- Treat **preserved attempts** as the primary comparison unit.
- Compare prompt variants using **measurable evidence**, not preference.
- Keep the DDx / HELIX boundary explicit:
  - **HELIX owns** bead choice, autonomy semantics, escalation behavior, and scoring rubric.
  - **DDx owns** execution, evidence capture, runtime metrics, required-execution evaluation, and preserve / merge mechanics.

---

## Architecture

```text
┌──────────────────────────────────────────────────────────────┐
│ Scenario Fixture or Real Bead                               │
│ • governing artifacts                                        │
│ • acceptance criteria                                        │
│ • expected artifacts                                         │
│ • linked execution docs                                      │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│ Fixed Base Revision                                          │
│ git rev-parse HEAD                                           │
│ same starting point for every prompt variant                 │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│ Prompt / Workflow Variant Worktree                           │
│ • prompt wording changes                                      │
│ • autonomy setting under test                                 │
│ • model / harness selection via DDx config or preset          │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│ DDx Execution                                                 │
│ ddx agent execute-bead <bead-id> --from <rev> --no-merge     │
│ • isolated attempt                                            │
│ • preserved commit/ref if not landed                          │
│ • required execution results                                  │
│ • ratchet outcomes                                            │
│ • runtime metrics                                              │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│ HELIX Evaluation                                              │
│ • completeness / quality / correctness                        │
│ • graph coherence                                              │
│ • required execution pass/fail                                 │
│ • ratchet pass/fail                                             │
│ • merge-vs-preserve interpretation                              │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│ Prompt Iteration Decision                                     │
│ • adopt                                                        │
│ • revise and rerun                                             │
│ • reject                                                       │
│ • file follow-up bead                                          │
└──────────────────────────────────────────────────────────────┘
```

---

## Test Inputs

Each experiment run should start from either:

1. a **scenario fixture** under `tests/scenarios/`, or
2. a **real HELIX bead** with bounded acceptance criteria.

### Preferred fixture shape

A scenario fixture should provide at least:
- `vision.md`
- `constraints.txt`
- `expected-artifacts.txt`
- `workflow.md` describing starting input/bead form, autonomy expectations, validations, and merge-vs-preserve interpretation
- one or more candidate beads representing the bounded work to execute
- linked execution docs that define required vs observational validations
- expected ratchet interpretation where relevant

### Scenario roles

| Scenario | Role | Typical use |
|---|---|---|
| A | baseline / simple | prompt regressions, low-noise comparisons |
| B | medium complexity | auth, constraints, operational tradeoffs |
| C | high complexity | ambiguity handling, escalation, autonomy behavior |

### Bead selection rules

Choose beads that are:
- bounded enough for one DDx attempt
- linked to governing artifacts
- backed by explicit acceptance criteria
- linked to execution docs if required validations are expected
- stable enough to compare across prompt variants

Avoid beads that are really undecomposed epics.

---

## What Changes Between Variants

A prompt-engineering experiment may vary one or more of:
- HELIX prompt wording
- HELIX workflow wording or decomposition guidance
- autonomy setting (`low`, `medium`, `high`)
- model / harness selection

Only change the variable being tested.

### Recommended comparison discipline

- Hold the **bead** constant.
- Hold the **base revision** constant.
- Hold the **scenario fixture** constant.
- Hold the **governing docs** constant unless the experiment is specifically about changed authority.
- If testing prompt wording, do **not** also change model or autonomy in the same comparison set.

---

## Measurement Dimensions

Use these dimensions for every run.

### 1. Artifact Completeness

Did the attempt produce the artifacts the bead and governing docs imply should exist?

Primary evidence:
- `tests/scenarios/<scenario>/expected-artifacts.txt`
- resulting changed files
- linked artifact IDs and expected downstream docs

Existing helper:
- `tests/measures/completeness.sh`

### 2. Artifact Quality

Are the produced artifacts structurally and semantically usable?

Examples:
- required sections exist
- acceptance criteria are explicit
- decisions are traceable to governing docs
- downstream docs are not empty shells

Existing helper:
- `tests/measures/quality.sh`

### 3. Decision Correctness

Did the attempt respect scenario constraints and governing requirements?

Examples:
- PostgreSQL is chosen when required
- OAuth2 / OIDC is respected where required
- constraints are not silently dropped
- assumptions are documented when autonomy permits assumptions

Existing helper:
- `tests/measures/correctness.sh`

### 4. Graph Coherence

Did the attempt preserve a coherent artifact graph?

Check for:
- correct `[[ID]]` references
- meaningful dependency links
- execution docs linked to governing artifacts
- no obvious orphan downstream docs
- no contradictory authority ordering

Graph coherence matters because prompt changes that create superficially plausible docs can still damage the artifact stack.

### 5. Required Execution Outcomes

Did all **required** execution docs for the bead succeed?

This is a merge-critical dimension.

Interpretation:
- required execution failure => the attempt should remain preserved, not land
- required execution success => the attempt may still be blocked by ratchets or workflow-level concerns, but it remains merge-eligible on this dimension

### 6. Ratchet Outcomes

Did the attempt meet ratchet expectations?

Examples:
- no regression below the floor
- observational metrics recorded even when non-blocking
- threshold breaches interpreted consistently

Use `workflows/ratchets.md` and linked metric definitions under:

```text
docs/helix/06-iterate/metrics/
```

### 7. Runtime Metrics

Record DDx-emitted runtime evidence for every run:
- tokens
- cost
- elapsed time / duration
- harness
- model
- attempt identifier / preserved ref

These metrics are part of the comparison surface, not incidental logs.

### 8. Merge-vs-Preserve Interpretation

Every run should end with an explicit interpretation:
- **merge-eligible**
- **preserve-only**
- **escalate / ask**

This interpretation is the key workflow-level output from the DDx-backed harness.

---

## Expected Outcome Matrix

Use this table when interpreting results.

| Evidence pattern | Expected interpretation |
|---|---|
| Required executions fail | Preserve-only |
| Required executions pass, ratchets pass, artifacts coherent | Merge-eligible |
| Required executions pass, observational checks fail only | Usually merge-eligible, but record follow-up if needed |
| Artifacts incomplete or constraint-incorrect | Preserve-only |
| Low autonomy asks instead of proceeding | Valid low-autonomy behavior, not a failure by itself |
| Medium autonomy escalates ambiguity appropriately | Valid medium-autonomy behavior |
| High autonomy completes work but DDx preserves due to failed validations | Preserve-only; return control to HELIX |

Important: a DDx preserve outcome is an execution result, not automatically a physics-level conflict.

---

## Test Execution Workflow

### Phase 1: Prepare the experiment

1. Choose the scenario or real bead.
2. Identify the exact bead ID to execute.
3. Freeze the base revision.
4. Confirm the bead is bounded and linked to governing artifacts.
5. Confirm the linked execution docs and expected ratchets are known.

Example:

```bash
BEAD_ID="hx-abc123"
BASE_REV="$(git rev-parse HEAD)"
```

Record both values in the experiment log.

### Phase 2: Create prompt variants

Use separate branches or worktrees so each variant is isolated in git.

Recommended naming:
- `prompt-baseline`
- `prompt-reworded`
- `prompt-high-autonomy-tuned`

Because git is canonical, prompt variants should be represented as actual file changes, not hidden out-of-band state.

### Phase 3: Run preserved attempts

For each prompt variant, execute the same bead from the same base revision:

```bash
ddx agent execute-bead "$BEAD_ID" --from "$BASE_REV" --no-merge
```

Required properties of the run:
- the attempt is bounded to the chosen bead
- the run starts from the same base revision for all compared variants
- the attempt is preserved for inspection
- DDx returns runtime and validation evidence

Repeat runs when measuring variance across models or prompt variants.

### Phase 4: Collect evidence

For each preserved attempt, collect:
- attempt identifier / preserved ref
- summary diff or changed files
- required execution results
- observational execution results
- ratchet outcomes
- runtime metrics
- merge-or-preserve outcome

Then evaluate artifact outputs using the HELIX-side measurements:
- completeness
- quality
- correctness
- graph coherence

### Phase 5: Score and compare

Use a per-attempt result table like this:

| Variant | Scenario | Bead | Autonomy | Harness | Model | Complete | Quality | Correct | Graph | Required execs | Ratchets | Outcome |
|---|---|---|---|---|---|---:|---:|---:|---|---|---|---|
| baseline | A | hx-abc123 | medium | agent | qwen3.5-27b | 82 | 78 | 95 | pass | pass | pass | merge-eligible |
| reworded | A | hx-abc123 | medium | agent | qwen3.5-27b | 91 | 85 | 95 | pass | pass | pass | merge-eligible |
| alt | A | hx-abc123 | medium | agent | qwen3.5-27b | 74 | 70 | 90 | weak links | fail | pass | preserve-only |

### Phase 6: Decide

Use these rules:
- **Adopt** the variant if it improves or maintains correctness, required execution success, and graph coherence while improving at least one major dimension.
- **Revise and rerun** if the results are mixed but promising.
- **Reject** if correctness, required execution outcomes, or graph coherence regress.
- **File a follow-up bead** if the run reveals missing execution docs, unclear ratchet policy, or ambiguous workflow contracts.

---

## Statistical Aggregation

When running multiple attempts for the same scenario:
- aggregate completeness / quality / correctness scores
- count required execution pass rate
- count ratchet pass rate
- count preserve-only vs merge-eligible outcomes
- compare runtime metrics by median and range, not only a single run

At minimum, summarize:
- runs
- mean completeness
- mean quality
- mean correctness
- required execution pass percentage
- ratchet pass percentage
- preserve percentage
- merge-eligible percentage
- median tokens
- median duration

---

## Suggested Test Matrix

Use this matrix to build confidence incrementally.

| Scenario | Autonomy | Comparison type |
|---|---|---|
| A | low | question quality and restraint |
| A | medium | baseline prompt vs revised prompt |
| A | high | completion quality vs preserve rate |
| B | medium | auth / constraints handling |
| B | high | execution-doc and ratchet interpretation |
| C | medium | escalation quality under ambiguity |
| C | high | bounded autonomy under complex design pressure |

Add model comparisons only after prompt comparisons are stable.

---

## Pass Criteria for Prompt Changes

A prompt change is acceptable only if it does **not** regress the hard dimensions:
- decision correctness
- graph coherence
- required execution outcomes

Preferred improvements are:
- higher completeness
- higher quality
- fewer preserve-only outcomes caused by avoidable prompt mistakes
- clearer low / medium / high autonomy behavior
- lower token or duration cost at equal quality

### Minimum bar

A candidate prompt should usually show:
- correctness at or above current baseline
- no drop in required execution pass rate
- no new graph-coherence failures
- a neutral or positive merge-eligibility trend

---

## Failure Analysis Checklist

When a run underperforms, classify the failure before editing prompts.

### Prompt failure
- omitted required artifact step
- weak instruction ordering
- ambiguity not handled as intended for the autonomy level
- insufficient traceability to governing docs

### Workflow-contract failure
- bead too large or under-specified
- missing or under-linked execution docs
- ratchet expectation unclear
- missing acceptance criteria

### Substrate failure
- DDx did not surface enough evidence
- preserve / merge result was not inspectable enough
- runtime metrics were missing or inconsistent

Only prompt failures should directly drive prompt edits. Other failure classes should file follow-up beads.

---

## Experiment Log Template

Use a log entry per comparison set:

```markdown
## Experiment: <name>

- Scenario: <A|B|C or real-work scope>
- Bead: <id>
- Base revision: <sha>
- Autonomy: <low|medium|high>
- Harness: <name>
- Model: <name>
- Compared variants:
  - baseline: <branch or commit>
  - candidate: <branch or commit>

### Outcomes
| Variant | Completeness | Quality | Correctness | Graph | Required execs | Ratchets | Runtime | Outcome |
|---|---:|---:|---:|---|---|---|---|---|
| baseline |  |  |  |  |  |  |  |  |
| candidate |  |  |  |  |  |  |  |  |

### Decision
- Adopt / Revise / Reject

### Notes
- What changed?
- What improved?
- What regressed?
- Is a follow-up bead required?
```

---

## Relationship to the Other Harnesses

This harness is specifically for **prompt and workflow wording iteration**.

Related surfaces:
- `tests/slider-autonomy-test-harness.md` focuses on autonomy behavior across low / medium / high.
- Scenario fixtures under `tests/scenarios/` define the reusable comparison inputs.
- `docs/helix/06-iterate/prompt-iteration-protocol.md` defines the repeatable decision loop and scoring rubric for these experiments.
- Execution-doc conventions live in `docs/helix/02-design/contracts/CONTRACT-002-helix-execution-doc-conventions.md`.

This harness should stay focused on answering:
**Does a prompt or workflow wording change improve real HELIX execution outcomes on top of DDx?**

---

## Success Condition

This harness is successful when HELIX maintainers can:
- run the same bead from the same base revision across prompt variants
- inspect preserved attempts instead of relying on ephemeral chat impressions
- compare artifact quality and workflow outcomes together
- determine whether a prompt change improves merge-eligible execution behavior
- file precise follow-up beads when failures come from workflow contracts or DDx substrate gaps instead of prompt wording
