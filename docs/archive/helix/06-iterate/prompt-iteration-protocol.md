# HELIX Prompt Iteration Protocol and Evaluation Rubric

## Purpose

This document defines the repeatable process HELIX uses to improve prompt and workflow wording once DDx-managed preserved-attempt execution is available.

It turns prompt work into a measurable iteration loop instead of an intuition-driven editing cycle.

Use this protocol when comparing:
- prompt wording revisions
- workflow wording revisions
- autonomy-behavior wording (`low` / `medium` / `high`)
- model / harness choices for the same bead and scenario

## Scope Boundary

This protocol assumes the DDx substrate provides:
- `ddx agent execute-bead <bead-id> [--from <rev>] [--no-merge]`
- preserved attempts for non-landed runs
- required execution summaries
- ratchet summaries
- runtime evidence

HELIX owns:
- experiment design
- scenario and bead selection
- autonomy semantics
- the scoring rubric
- the decision about whether to revise prompt wording, workflow wording, scenario expectations, or governing docs

DDx owns:
- execution mechanics
- preserved attempt storage and evidence
- merge / preserve outcome
- runtime metrics

## Core Rules

1. **Compare from the same base revision.**
2. **Change one variable at a time.**
3. **Use preserved attempts as the default experiment unit.**
4. **Do not adopt a prompt change that regresses correctness, graph coherence, or required execution outcomes.**
5. **File follow-up beads when the failure is in the fixture, workflow contract, or DDx substrate rather than the prompt.**

---

## Protocol

### Step 1: State the experiment hypothesis

Write one sentence describing the change and what improvement is expected.

Examples:
- "Tightening autonomy wording should reduce unnecessary questions in medium mode."
- "Explicit artifact-link instructions should improve graph coherence."
- "A clearer handoff instruction should reduce preserve-only outcomes caused by missing required validation context."

If the hypothesis changes more than one variable, split it into separate experiments.

### Step 2: Choose the scenario and bead

Select either:
- a fixture scenario under `tests/scenarios/`, or
- a real HELIX bead with clear acceptance criteria

Selection rules:
- the bead must be bounded
- the governing artifacts must be stable enough for comparison
- expected validations and outcomes must be knowable ahead of time
- if autonomy behavior is under test, the scenario must contain the relevant ambiguity or constraint pressure

Record:
- scenario name
- bead ID
- autonomy level
- harness/model being used

### Step 3: Freeze the base revision

All compared variants must run from the same base revision.

```bash
BASE_REV="$(git rev-parse HEAD)"
```

Record the base revision in the experiment log.

If the base revision changes, start a new comparison set.

### Step 4: Create isolated variants in git

Represent each prompt or workflow variant as real git changes in a branch or worktree.

Recommended naming:
- `prompt-baseline`
- `prompt-candidate-1`
- `prompt-candidate-2`

Because git is canonical, prompt revisions must be inspectable as normal repository changes.

### Step 5: Run preserved attempts

For each variant, execute the same bead from the same base revision:

```bash
ddx agent execute-bead <bead-id> --from <rev> --no-merge
```

Use preserved attempts for comparison by default. Do not merge candidate prompt runs directly into mainline while still comparing them.

Run additional attempts only when measuring variance across models or when the run is known to be noisy.

### Step 6: Collect evidence

For each run, collect the following:

#### DDx evidence
- preserved ref or merged result identifier
- required execution summary
- ratchet summary
- runtime evidence:
  - harness
  - model
  - session ID
  - elapsed duration
  - token usage
  - cost
  - base revision
  - result revision

#### HELIX workflow evidence
- transcript excerpts
- questions asked
- escalation beads created
- follow-up beads created
- supervisory interpretation after DDx returns

#### Output evidence
- changed files / diff summary
- artifact set produced
- graph links and traceability quality
- constraint handling quality

### Step 7: Score with the rubric

Score each run independently before comparing them.

### Step 8: Compare against baseline

A candidate is compared to the current accepted baseline, not just judged in isolation.

Ask:
- Did the candidate improve the intended dimension?
- Did it regress any hard gate?
- Did it reduce merge-eligible behavior?
- Did it make autonomy behavior less correct?

### Step 9: Choose the next action

After scoring, choose exactly one:
- **Adopt prompt change**
- **Revise prompt wording**
- **Revise workflow wording**
- **Revise scenario expectations**
- **File DDx follow-up bead**
- **Stop and ask for human guidance**

---

## Required Evidence Checklist

A run is not reviewable unless all of the following are available:

- [ ] base revision
- [ ] bead ID and scenario
- [ ] autonomy level
- [ ] changed prompt/workflow files
- [ ] DDx merge/preserve outcome
- [ ] required execution summary
- [ ] ratchet summary
- [ ] runtime evidence fields
- [ ] changed-file or diff summary
- [ ] enough transcript or summary evidence to judge ask/escalate/dispatch behavior

If any item is missing, the result should normally trigger a follow-up bead rather than a prompt conclusion.

---

## Evaluation Rubric

Score each category from **0 to 3**.

### 1. Scope Selection

How well did the prompt keep the attempt bounded to the intended bead and scope?

| Score | Meaning |
|---|---|
| 0 | Attempt ignored the bead boundary or sprawled into unrelated work |
| 1 | Attempt mostly respected scope but introduced substantial drift |
| 2 | Attempt stayed bounded with minor extras |
| 3 | Attempt was tightly scoped and appropriately decomposed |

### 2. Graph Coherence

How well did the run preserve artifact traceability and graph integrity?

| Score | Meaning |
|---|---|
| 0 | Broken or missing links; orphaned artifacts; incoherent authority flow |
| 1 | Partial traceability; some missing or weak links |
| 2 | Good traceability with minor gaps |
| 3 | Strong, explicit, coherent graph behavior throughout |

### 3. Constraint Handling

Did the run respect explicit scenario constraints and governing requirements?

| Score | Meaning |
|---|---|
| 0 | Major constraints violated or ignored |
| 1 | Constraints acknowledged but incompletely respected |
| 2 | Constraints respected with minor omissions |
| 3 | Constraints handled correctly and explicitly |

### 4. Autonomy Correctness

Did the run behave correctly for the selected autonomy level?

| Score | Meaning |
|---|---|
| 0 | Behavior contradicted the autonomy contract |
| 1 | Mixed behavior; some correct, some incorrect |
| 2 | Mostly correct autonomy behavior |
| 3 | Clean, clearly correct autonomy behavior |

Examples:
- low should ask before steps and artifact creation
- medium should proceed deterministically and ask on ambiguity
- high should continue through resolvable conflicts and stop only on physics-level contradictions

### 5. Verification Behavior

Did the run handle required executions, ratchets, and preserve/merge interpretation correctly?

| Score | Meaning |
|---|---|
| 0 | Required execution / preserve behavior was incorrect or uninterpretable |
| 1 | Some evidence existed but interpretation was weak or inconsistent |
| 2 | Verification behavior was mostly correct |
| 3 | Verification behavior was explicit, correct, and easy to interpret |

### 6. Output Quality

Are the produced artifacts and results structurally and semantically strong?

| Score | Meaning |
|---|---|
| 0 | Low-quality or unusable output |
| 1 | Partially useful output with major gaps |
| 2 | Solid output with minor issues |
| 3 | High-quality, ready-to-use output |

### 7. Efficiency

Did the run use an acceptable amount of time and tokens for the quality achieved?

| Score | Meaning |
|---|---|
| 0 | Wasteful or clearly inefficient for the result |
| 1 | Marginal efficiency; too much cost for limited gain |
| 2 | Reasonable efficiency |
| 3 | Strong efficiency for the achieved quality |

Efficiency is a **soft** category. It must not override correctness.

---

## Hard Gates vs Soft Dimensions

### Hard gates
A candidate must not regress these categories below the accepted baseline:
- Constraint Handling
- Graph Coherence
- Autonomy Correctness
- Verification Behavior

A score of **0 or 1** in any hard gate normally blocks adoption.

### Soft dimensions
These may guide iteration but do not override hard-gate failures:
- Scope Selection
- Output Quality
- Efficiency

---

## Decision Rules

### Adopt prompt change
Adopt when all of the following are true:
- no hard-gate regression
- intended target dimension improved
- merge-eligible behavior is neutral or better
- preserve-only outcomes are not increased by avoidable prompt mistakes

### Revise prompt wording
Choose this when:
- the workflow contract appears sound
- substrate evidence is sufficient
- the failure looks like unclear or weak instructions

Typical signals:
- missing artifact links
- under-specified required sections
- autonomy behavior drift caused by wording ambiguity

### Revise workflow wording
Choose this when:
- multiple prompt variants fail in the same workflow step
- routing, escalation, or handoff instructions appear ambiguous
- the issue is behavioral policy, not prompt phrasing alone

### Revise scenario expectations
Choose this when:
- the fixture does not cleanly exercise the intended behavior
- the scenario is too ambiguous or too easy for the experiment
- mergeable vs preserve-only expectations were unrealistic

### File DDx follow-up bead
Choose this when:
- preserved-attempt evidence is missing or incomplete
- required execution summaries are not inspectable enough
- runtime evidence fields are absent
- merge/preserve semantics are not surfaced cleanly

### Ask for human guidance
Choose this when:
- two competing prompt variants trade off hard-gate behavior in a way the rubric cannot cleanly resolve
- the governing docs themselves may need to change

---

## Experiment Log Template

```markdown
## Experiment: <name>

- Hypothesis: <one sentence>
- Scenario: <A|B|C or real-work scope>
- Bead: <id>
- Base revision: <sha>
- Autonomy: <low|medium|high>
- Harness: <name>
- Model: <name>
- Variants:
  - baseline: <branch or commit>
  - candidate: <branch or commit>

### Evidence
- DDx outcome: <merged|preserved>
- Required executions: <summary>
- Ratchets: <summary>
- Runtime: <tokens / cost / duration / session>
- Questions asked: <count or summary>
- Escalations created: <count or ids>
- Follow-up beads: <count or ids>

### Rubric
| Category | Baseline | Candidate | Notes |
|---|---:|---:|---|
| Scope Selection |  |  |  |
| Graph Coherence |  |  |  |
| Constraint Handling |  |  |  |
| Autonomy Correctness |  |  |  |
| Verification Behavior |  |  |  |
| Output Quality |  |  |  |
| Efficiency |  |  |  |

### Decision
- Adopt / Revise prompt / Revise workflow / Revise scenario / File DDx bead / Ask for guidance

### Rationale
- What improved?
- What regressed?
- What is the next concrete action?
```

---

## Relationship to the Harness Docs

- `tests/prompt-engineering-harness.md` defines the experimental harness shape.
- `tests/slider-autonomy-test-harness.md` defines autonomy-specific behavioral expectations.
- `tests/scenarios/*/workflow.md` defines scenario-level expected behavior, validations, and merge-vs-preserve interpretation.

This protocol tells maintainers **how to run and judge the experiments**.

## Success Condition

The protocol is working when HELIX maintainers can repeatedly:
- choose a scenario and bead
- freeze a base revision
- run preserved attempts across prompt variants
- inspect the same evidence fields every time
- score runs with the same rubric
- make a clear decision about whether to revise prompts, workflow wording, scenario expectations, or DDx substrate behavior
