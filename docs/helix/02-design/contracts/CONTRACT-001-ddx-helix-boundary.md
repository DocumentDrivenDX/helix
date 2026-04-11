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
  canonical git-aware single-bead execution primitive
- `ddx agent execute-loop [--once] [--poll-interval <duration>]` as the
  canonical single-project queue-drain primitive that claims ready beads,
  runs `execute-bead`, and closes merged work with evidence
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
For every managed execute-bead attempt, including attempts launched by
`ddx agent execute-loop`, DDx should capture runtime facts such as:
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
- when to delegate a current project queue to `ddx agent execute-loop`
- bead authoring rules for deterministic acceptance and success-measurement
  criteria so DDx-managed execution can close merged work without manual
  interpretation
- bead topology policy for parent-child relationships and dependencies when
  queue order matters (curation — ensures DDX's deterministic ordering is correct;
  HELIX does not predict which bead DDX will select)

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
- stage-authored behavior stance for planning, execution, review, alignment,
  and related workflow stages
- bead prompt structure
- workflow wording and intervention policy
- execution-document authoring conventions for HELIX artifacts (see [CONTRACT-002](CONTRACT-002-helix-execution-doc-conventions.md))

HELIX does **not** expose stage personalities as a separate first-class
workflow configuration surface. The simpler contract is:

- HELIX bakes stage stance into the governing action prompt, skill wording, or
  execution-doc convention for that stage
- DDx still owns harness/model execution and any concrete model resolution
- if a stage needs a smarter, cheaper, slower, or faster lane, HELIX may ask
  for tier or harness constraints, but it must not turn stage stance into
  concrete model policy

The default HELIX stage stances are:

| Stage family | Stance owned by HELIX | Notes |
|---|---|---|
| Planning (`input`, `frame`, `design`, `evolve`, `triage`, `polish`) | exploratory, assumption-surfacing, artifact-authoring | widen context, expose ambiguity, prefer reversible shaping |
| Managed execution (`build`, `measure`, execution-ready bead work) | contract-following, bounded, anti-feature-creep | implement only the governed slice and prove it deterministically |
| Review (`review`, fresh-eyes passes) | adversarial, defect-seeking, risk-first | findings first; preserve merge/preserve evidence boundary |
| Alignment (`align`) | top-down, conservative, drift-seeking | compare lower layers against higher-authority artifacts |
| Supervisory/mechanical (`check`, `report`, queue steering) | concise, state-oriented, policy-applying | route work without inventing new product behavior |

These stances apply whether HELIX launches work through DDx-managed execution
or through a direct non-managed prompt such as `ddx agent run` for planning,
review, or alignment. The stage selects the stance; DDx resolves the execution
vehicle and concrete model policy.

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
- what autonomy behavior should apply
- what workflow prompt/context to use
- what stage-authored stance should apply for the selected workflow step
- when implementation/verification should be dispatched
- whether to dispatch one bounded attempt with `ddx agent execute-bead` or
  hand a single-project ready queue to `ddx agent execute-loop`

HELIX then hands execution to DDx through managed agent/execution surfaces.

### DDx -> HELIX
DDx returns evidence, not workflow policy:
- execution outcome
- queue-drain result summaries when `execute-loop` is used
- required execution results
- ratchet results
- runtime metrics
- landed vs preserved outcome
- transcript/session/exec evidence locations

Minimum workflow-visible outcome surface from `ddx agent execute-loop --once --json`:

```json
{
  "project_root": "/path",
  "attempts": 1,
  "successes": 1,
  "failures": 0,
  "results": [
    {
      "bead_id": "hx-abc123",       "attempt_id": "...",
      "harness": "codex",           "status": "success",
      "detail": "...",              "session_id": "...",
      "base_rev": "sha",             "result_rev": "sha",
      "retry_after": "..."
    }
  ]
}
```

`results[].status` values:

| Status | Meaning |
|--------|---------|
| `success` | Bead merged or preserved with success |
| `no_changes` | Agent produced no tracked changes; worktree clean |
| `execution_failed` | Agent or harness exit non-zero |
| `land_conflict` | Attempt preserved: rebase failed or fast-forward not possible |
| `post_run_check_failed` | Attempt preserved: post-run checks failed |
| `structural_validation_failed` | Bead malformed or missing required fields |

Outcome-to-status mapping (internal to DDx):
- `outcome=merged` → `status=success`
- `outcome=no-changes` → `status=no_changes`
- `outcome=preserved`, reason in (rebase failed, ff-merge failed, ff-merge not possible) → `status=land_conflict`
- `outcome=preserved`, reason=post-run checks failed → `status=post_run_check_failed`
- `outcome=preserved`, other reason → `status=success`

HELIX uses `results[].bead_id` for all post-cycle bookkeeping (not a pre-selected bead).
HELIX uses `results[].result_rev` as the closing SHA candidate.
HELIX uses `results[].retry_after` for blocked/suspended bead surfaced via `ddx bead blocked`.

HELIX-authored execution beads must make success machine-auditable. In
practice this means deterministic acceptance and success-measurement criteria:
exact commands, named checks, concrete files or fields to inspect, and
observable end states. Vague success text such as "works correctly" is not a
sufficient contract for `ddx agent execute-bead` or `ddx agent execute-loop`.

When HELIX delegates queue draining to `ddx agent execute-loop`, DDx owns the
claim/execute/close mechanics for merged work in that loop. HELIX remains
responsible for deciding when loop delegation is appropriate and for
interpreting preserved, failed, or blocked outcomes.

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
- a second single-project queue-drain loop once `ddx agent execute-loop`
  satisfies the required HELIX supervision contract

## Queue Curation Policy

HELIX owns queue curation. DDx owns bead selection and execution.

HELIX does not predict which bead DDx will select. Instead, HELIX ensures the
queue is in the correct state so DDx's deterministic `ReadyExecution()` ordering
produces the intended sequence.

| Queue mechanism | DDx behavior | HELIX responsibility |
|---|---|---|
| `dep-ids` | `ReadyExecution` waits for all deps to be `closed` | Set correctly on all beads; update when deps are added |
| `parent` hierarchy | DDx respects parent/child but does not enforce child execution order | Epic execution is separate from child execution; children enter ready queue independently |
| `execution-eligible` | `ReadyExecution` filters out `false`; defaults `true` if absent | Set `false` to temporarily suppress a bead without closing it |
| `superseded-by` | `ReadyExecution` filters out superseded beads | Set when a bead is superseded; do not leave superseded beads open |
| `execute-loop-retry-after` | `ReadyExecution` filters out beads on cooldown | DDx sets this on failed attempts; HELIX should not set it |

### Epic-focus queue curation

When HELIX enters epic-focus mode (stay on an epic until all children are done):

1. HELIX sets `execution-eligible: false` on all non-child open beads via `ddx bead update --set execution-eligible=false`.
2. DDx's `ReadyExecution` naturally picks only eligible children.
3. When the epic closes or switches, HELIX removes the `execution-eligible` suppression from remaining beads.
4. No DDX flag or special selection logic is required.

### Queue-drift ownership

Drift (superseded-by, parent change, spec-id change) is a **pre-execution** concern.
HELIX detects drift at `helix check` time and prevents stale beads from entering
the ready queue. DDx executes what it is given; it does not reopen beads after
close-with-evidence.

HELIX does not implement post-close reopen logic. If a bead was ready when DDx
picked it, the execution result stands.

## Queue-Injected Supervisory Beads

Review and alignment are **regular beads**, not post-cycle hooks. HELIX injects them
into the queue and lets DDx execute them through execute-loop:

| Bead type | Trigger | Acceptance |
|---|---|---|
| `review-finding` | Post-build or periodic | Agent finds 0 new drift violations |
| `alignment-review` | Every N completed passes | No governance drift detected |

When HELIX injects a review or alignment bead into the queue, DDx picks it up
like any other ready bead. The execution produces the same evidence bundle as
implementation beads, enabling performance analysis.

`--no-auto-review` and `--no-auto-align` control whether HELIX injects these beads
— they do not disable post-cycle hooks.

## Performance Metadata and Optimization

Every execute-bead attempt produces:

```
bead_id → { new_state, performance_metadata }
```

Performance metadata captured by DDx per attempt:
- model, harness, provider
- elapsed time
- token usage (input, output, total)
- cost
- base revision, result revision
- session ID, attempt ID

HELIX uses this for:
- **Prompt optimization**: did a simpler prompt produce the same result faster?
- **Model routing**: would a faster/cheaper model have sufficed? Would a smarter model have avoided the failure?
- **Process improvement**: why did this experiment fail? What assumption was wrong?

HELIX experiments use this infrastructure:
- Queue a batch of experiment beads with specific acceptance criteria
- DDx runs them all in order via execute-loop
- Each produces: new state + performance metadata
- Keep the ones that improve state; failed experiments leave a detailed record
  of what didn't work and why, enabling targeted improvement

This turns every bead execution into a measurable data point for continuous
process optimization.

## Post-Cycle HELIX Behavior

After `ddx agent execute-loop --once` returns, HELIX applies post-cycle
supervisory policy to the bead(s) in `results[].bead_id`.

| Behavior | Owner | Notes |
|---|---|---|
| Queue injection (review, alignment) | **HELIX** | Creates beads, DDx executes them |
| Epic promotion (task → epic when children appear) | **HELIX** | Post-cycle tracker mutation |
| Acceptance-failure filing | **HELIX** | Creates follow-on beads |
| Cycle counting | **HELIX** | Increments on `status=success` |
| Context refresh | **HELIX** | Every 5 cycles or on epic switch |
| Closing SHA sync | **DDx** | Uses `results[].result_rev` |
| Build gate (pre-merge check) | **DDx** | Runs before merge; reverts on failure |
| Retry suppression | **DDx** | Sets `execute-loop-retry-after` on cooldown |
| Orphan worktree recovery | **DDx** | Automatic after crashed runs |

Behaviors **deleted** from HELIX wrapper:
- HELIX retry/backoff logic (superseded by DDx `retry-after`)
- HELIX blocker tracking and reporting (superseded by `ddx bead blocked`)
- HELIX orphan tracker recovery (redundant with DDx worktree recovery)
- `git checkout -- .` cleanup (DDx worktrees are isolated)
- `safe_unclaim` after failed attempt (DDx handles claim lifecycle)
- `HELIX_SELECTED_ISSUE` env var (DDx never consumed it)

## Validation Checklist

The boundary is healthy when all of the following are true:

- [ ] HELIX uses DDx graph primitives instead of a parallel graph implementation for document indexing/traversal
- [ ] HELIX uses DDx-managed bead execution instead of directly inventing its own execution/provenance substrate
- [ ] HELIX parses `execute-loop --json` to find executed bead(s), applies post-cycle
  bookkeeping to those bead IDs rather than to a pre-selected bead
- [ ] HELIX does not pass `HELIX_SELECTED_ISSUE` or any bead selector to DDx execute-loop
- [ ] HELIX uses `execution-eligible` for epic-focus queue curation, not DDX flags
- [ ] HELIX injects review and alignment as regular beads into the queue, not as post-cycle hooks
- [ ] HELIX uses performance metadata from execute-bead results for prompt and model routing optimization
- [ ] HELIX experiments use execute-loop to run batched experiment beads with performance tracking
- [ ] HELIX does not implement retry/backoff or blocker tracking (DDx handles via `retry_after`)
- [ ] HELIX does not implement post-close reopen logic (drift is pre-execution)
- [ ] HELIX execution beads carry deterministic success criteria and
  measurement hooks precise enough for DDx-managed close-with-evidence
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
