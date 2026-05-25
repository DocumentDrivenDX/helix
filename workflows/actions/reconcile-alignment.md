# HELIX Action: Reconcile Alignment

You are performing an iterative top-down reconciliation review of a HELIX
project.

Your goal is to re-align the implementation with the authoritative planning
stack, identify explicit divergence, determine whether additional execution
work remains for the reviewed scope, and produce deterministic next steps using
the runtime tracker.

This action is read-only with respect to product code unless explicitly told to
make fixes. It may create or update:

- review issues in the tracker
- execution issues in the tracker
- one durable alignment report in `docs/helix/06-iterate/alignment-reviews/`

## Action Input

You will receive a review scope as an argument. If no scope is given, default
to the repository.

## Authority Order

When artifacts disagree, use this authority order:

1. Product Vision
2. Product Requirements
3. Feature Specs / User Stories
4. Architecture / ADRs
5. Solution Designs / Technical Designs
6. Test Plans / Tests
7. Implementation Plans
8. Source Code / Build Artifacts

Rules:

- Higher layers govern lower layers.
- Tests govern build execution but do not override requirements or design.
- Source code reflects current state but does not redefine the plan.
- If a higher layer is missing or contradictory, do not infer intent from lower layers.
- Prefer aligning code to plan. Propose plan changes only when strongly justified.

## Tracker Rules

Use the runtime tracker only.

### Review Structure

Use two issue categories:

1. Review epic
   - `type: epic`
   - labels: `helix`, `kind:review`, `kind:review`
   - title pattern: `HELIX alignment review: <scope>`

2. Review issues
   - `type: task`
   - parented to the review epic
   - labels: `helix`, `kind:review`, `kind:review`, plus area labels

Only after consolidation, create execution issues for approved follow-up work.
Execution issues must use tracker IDs, `parent`, `deps`, `spec-id`, and
HELIX labels appropriate to the work activity.

## STEP 0 - Review Bootstrap

0. **Context Recovery**: Re-read AGENTS.md so project instructions are fresh
   in your working memory. After long sessions, context compaction may have
   dropped critical project rules. This step is cheap insurance against drift.
0a. **Load active design principles** following the principles-resolution
   reference for this runtime. Use them as alignment criteria — flag artifacts
   whose design choices deviate from the active principles.
0b. **Load active concerns and practices** following the concern-resolution
   reference for this runtime. Concern drift is an alignment finding at every
   layer, not just implementation:
   - Flag **implementation** that uses tools or conventions inconsistent with the
     declared concerns (e.g., using `vitest` when `bun:test` is declared).
   - Flag **planning artifacts** (PRD technical context, design docs, test plans)
     that reference tools, frameworks, or conventions contradicted by the active
     concerns (e.g., a design doc specifying ESLint when the concern declares
     Biome, or a test plan referencing Jest when the concern declares `bun:test`).
   - Flag **ADRs** that contradict current concern selections.
   - Flag **missing concern coverage**: if the project uses a technology that has
     a library concern but that concern is not declared in `concerns.md`, note it.
   - For each concern, load its practices and check that the project's actual
     tooling matches each practice category (linter, formatter, test framework,
     build tool, dependency audit). Report specific mismatches.
0c. **Verify context digest freshness**: For work items in scope, check whether
   context digest blocks reflect current upstream state. Stale digests are an
   alignment finding.
1. Verify the runtime tracker is available. Stop immediately if unavailable.
2. Determine the review scope.
3. Break the scope into functional areas.
4. Reconcile any existing review epic and review issues for the same scope.
   - Reuse and update existing review work where possible.
   - Mark stale review work as closed, superseded, or split as appropriate.
5. Create or update:
   - one review epic for the run
   - one review issue per functional area
6. Record the epic ID and review issue IDs in the alignment report.
7. **Note deduplication rule**: Before appending notes to any review issue
   (existing or new), read the issue's current `notes` field. If the new
   note is substantively identical to an existing note (same proof lane,
   same scope, same verification outcome), **do not append** — the existing
   note already records the evidence. Only append when the verification
   state has materially changed (new test results, different artifact state,
   changed finding). This prevents repeated alignment reruns from bloating
   tracker records with duplicate evidence paragraphs.

## STEP 0.5 - Work Item Acquisition

Before modifying any tracker work items or writing reports, acquire a governing
work item for this alignment pass. See the runtime's work-item acquisition
reference for the full pattern.

If this action was reached through a skill or CLI entrypoint, treat that
entrypoint as a thin launcher only. The governing work item and stored prompt
are the durable contract.

Whenever this action creates or materially updates a work item's description,
assemble or refresh its context digest. If the runtime provides a digest-refresh
helper, use it so digests and area labels stay deterministic.

## STEP 1 - Reconstruct Intent

Using planning artifacts only, summarize:

- product vision
- product requirements
- feature specs
- user stories
- architecture decisions / ADRs
- solution designs
- technical designs
- test plans
- implementation plans

Do not use source code to fill planning gaps in this activity.

## STEP 2 - Planning Stack Consistency

Validate traceability as a dependency graph, not a forced linear chain.

Check for:

- Vision -> Requirements
- Requirements -> Feature Specs / User Stories
- Requirements / Feature Specs -> Architecture
- Architecture / User Stories / Feature Specs -> Solution or Technical Designs
- Technical Designs / Test Plans -> Implementation Plans
- Specs / Stories / Designs -> Tests

Identify:

- contradictions
- missing links
- underspecified areas
- stale artifacts
- same-layer conflicts
- downstream artifacts that no longer match upstream authority
- concern-artifact inconsistencies: planning artifacts that specify tools,
  frameworks, quality gates, or conventions that conflict with the active
  concerns and their merged practices

## STEP 3 - Implementation Review

Inspect implementation and map it to the planning stack.

Identify:

- workspace/package/module topology
- runtime entry points
- public interfaces
- tests
- feature flags and config switches
- build and deploy surfaces
- major unplanned code paths
- dead or orphaned implementations

### Concern Drift Detection

For each active concern, verify the implementation matches its declared
practices:

1. **Tech-stack concerns** (rust-cargo, typescript-bun, python-uv, go-std,
   scala-sbt): Check that the actual linter, formatter, test runner, build
   tool, and dependency manager match what the concern and project overrides
   declare. Check for drift signals listed in the concern's Drift Signals
   section (if present). Report each mismatch with the specific file evidence.
2. **Infrastructure concerns** (k8s-kind): Check that deployment manifests,
   local dev setup, and service discovery patterns match the declared approach.
3. **Quality concerns** (security-owasp, o11y-otel, a11y-wcag-aa): Check that
   the concern's quality gates are present in CI or pre-commit configuration.
   Verify dependency audit commands are wired. Check that practices like
   parameterized queries, input validation, and secret management are followed.
4. **Concern-specific quality gates**: For each concern that declares quality
   gate commands (e.g., `cargo deny check advisories`, `govulncheck`,
   `bun audit`), verify those commands are present in CI configuration or
   pre-commit hooks. Missing gates are alignment findings.

### Slot Registry Integrity

A drifted slot registry corrupts high-autonomy concern resolution (FEAT-006
slots; the filler a slot resolves to comes straight from this registry), so the
instrument must be checked before its readings are trusted. Reconcile
`.ddx/plugins/helix/workflows/concerns/slots.yml` against the concern library
and the operator override; each failure below is a **blocking
instrument-integrity finding**:

1. **Every `## Slot` names a known slot.** For each concern whose `concern.md`
   has a `## Slot` section, the named slot must exist as a key under `slots:` in
   `slots.yml`. A `## Slot` naming an undeclared slot is drift.
2. **Every default names a matching member.** For each `key: value` under
   `defaults:`, the concern `value` must exist and its `concern.md` `## Slot`
   must name that same `key`. A typo default, or a default whose `## Slot`
   disagrees with the key, is drift.
3. **Defaults only for exclusive slots.** Every key under `defaults:` must be a
   slot declared `exclusive: true`. A default on a non-exclusive (or undeclared)
   slot is drift.
4. **Overrides name a real slot + concern.** If `docs/helix/01-frame/concerns.local.yml`
   exists, each `key: value` under its `defaults:` must name a slot present in
   `slots.yml` and a concern whose `## Slot` matches that key. An override naming
   an unknown slot or a non-member concern is drift.
5. **No duplicate default keys.** YAML keeps the *last* of duplicate keys
   silently rather than erroring, so the keyed-map shape does not by itself
   guarantee one default per slot. Scan the raw text of each `defaults:` block
   (`slots.yml` and `concerns.local.yml`) for a slot key appearing more than
   once; a repeated key is drift — it is the literal "two defaults for one slot"
   the registry exists to forbid.
6. **One `## Slot` per concern.** A concern fills exactly one functional
   position, so its `concern.md` must have at most one `## Slot` section naming a
   single scalar slot. Multiple `## Slot` sections, or a list value, is drift.

Report each finding with the specific file and key. Resolve by reconciling the
registry, the concern's `## Slot`, or the override — never by weakening the
check.

### Acceptance Criteria Validation

This check enforces a **coverage floor (minimum rigor), not equal depth** — more
stories or tests are always welcome. Flag only **missing required coverage**;
never penalize a story or suite for having *more* rigor than another.

**Decomposition coverage (FR → story).** Before validating criteria, check that
every PRD functional requirement maps to a story: for each stable `FR-n` in
`docs/helix/01-frame/prd.md`, confirm **≥1 user story covers it** (a story names
the `FR-n` it covers in its header / Dependencies). An `FR-n` with no covering
story is a **blocking coverage gap**. One story may cover several `FR-n`s, but a
story bundling **unrelated** `FR-n`s without recorded justification is a finding
(split it). This requires stable `FR-n` IDs in the PRD; if they are absent, that
template gap is itself a finding (the mapping is not reproducible without them).

For each user story and feature spec in the reviewed scope:

1. Extract acceptance criteria from the governing artifact.
2. For each criterion, determine whether:
   - a test exists that **exercises** the criterion — it drives the criterion's
     action and asserts the criterion's observable outcome. A test that merely
     names the criterion, runs adjacent code, or asserts nothing relevant does
     **not** exercise it: classify that criterion `UNTESTED`, and if an artifact
     *claims* the named test covers it, `ASSERTED_UNBACKED` — never "covered".
   - the test passes
   - the implementation satisfies the criterion based on code inspection
3. Classify each criterion as:
   - **SATISFIED** — test exists, passes, and implementation matches
   - **TESTED_NOT_PASSING** — test exists but fails
   - **UNTESTED** — no test covers this criterion
   - **UNIMPLEMENTED** — no implementation addresses this criterion
   - **ASSERTED_UNBACKED** — an artifact *claims* this criterion is satisfied, or names a test
     that covers it, or states a coverage figure or emitted metric, but verification against the
     implementation finds no backing reality (the named test does not exist, the metric is never
     emitted, the figure is invented). This is a **phantom claim** — distinct from UNTESTED, which
     is honest about the gap; ASSERTED_UNBACKED asserts something untrue. It is a
     traceability-honesty defect.
3a. **Claims-vs-reality check (honesty rule).** Every artifact assertion about a test, a coverage
    figure, or an emitted metric/signal must resolve to something that actually exists in the
    implementation, test suite, or emitted telemetry. Verify each such claim against reality. A
    claim with no backing is classified ASSERTED_UNBACKED.
4. Record results in the Gap Register with the governing artifact as planning
   evidence and the test or code file as implementation evidence.
5. If the project has adopted an acceptance criteria ratchet, compare the
   current satisfaction count against the committed floor. Flag any regression
   — a decrease in SATISFIED criteria that was not accompanied by a floor
   override.
6. **Phantom-claim floor is zero.** The ASSERTED_UNBACKED count must be 0; any phantom claim is a
   blocking regression regardless of the satisfaction floor. Resolve each by either making the
   claim true (add the test / emit the metric) or deleting the claim from the artifact — never by
   weakening or removing the check.
7. **AC coverage floor (blocking, with one escape hatch).** Every acceptance criterion must have
   ≥1 test that *exercises* it (per step 2). A criterion classified `UNTESTED` is a **blocking
   coverage gap** by default — resolve it by adding an exercising test. The **only** non-blocking
   resolution is a **recorded reviewed exception**: the criterion is documented as
   "manual verification accepted" or "non-automatable AC" with the evidence of the manual
   verification (who verified, what was observed). A criterion is never silently passed as covered
   when no test exercises it — it is either tested, or carries a recorded reviewed exception. This
   is a floor: extra tests beyond one-per-AC are always fine and never a finding.

### Instrument-Integrity Check

A gate can lie exactly as an artifact can; fix the instrument before trusting
its reading. Before reporting any conformance or metric score, verify the
instrument that produced it (FEAT-016 FR-6):

1. **Template↔meta agreement.** For each artifact scored against its
   `template.md` and `meta.yml`, confirm the two **agree**: every section the
   template marks required appears in the meta's `required_sections`, and the
   meta requires no section the template omits. When they **drift**, the
   conformance score they jointly produce is untrustworthy — a misleadingly low
   score reflects a broken instrument, not a bad artifact (this is the "prd
   scored 1/8" failure mode). Flag template↔meta drift as a **blocking
   instrument-integrity finding** and resolve it by reconciling the two; do not
   report the misleading score as the artifact's grade.
2. **Verified measurement.** A metric definition cited as evidence must name a
   measurement command that was actually run, with the run recorded in
   `last_verified`. An asserted-but-unmeasured metric is `ASSERTED_UNBACKED` per
   the honesty rule above — a number with no run behind it is a phantom claim.

## STEP 4 - Gap Classification

For each relevant area, assign exactly one classification:

- ALIGNED
- INCOMPLETE
- DIVERGENT
- UNDERSPECIFIED
- STALE_PLAN
- BLOCKED

Each classification must include:

- planning evidence
- implementation evidence
- explanation
- default resolution direction: `code-to-plan`, `plan-to-code`, or `decision-needed`
- owning review issue ID

### Quality Evaluation

For each area classified as ALIGNED or INCOMPLETE, evaluate:

- **Robustness** — does the implementation handle edge cases, errors, and
  degraded inputs as specified? Are failure modes defined in the design and
  tested?
- **Maintainability** — is the implementation structured for change? Are
  boundaries clean, dependencies explicit, and coupling proportional to
  cohesion?
- **Performance** — are performance constraints from requirements or design
  met or testable? Are there obvious scalability risks unaddressed by the
  planning stack?

Quality concerns do not change the gap classification. Instead, record them as
supplementary findings in the Gap Register with resolution direction
`quality-improvement` and create backlog-type execution issues in Step 7 when
warranted.

## STEP 5 - Traceability Matrix

Produce a matrix with:

- Vision item
- Requirement
- Feature Spec / User Story
- Architecture / ADR reference
- Solution / Technical Design reference
- Test reference
- Implementation Plan reference
- Code status
- Classification

## STEP 6 - Consolidated Report

Create or update the durable report at:

- `docs/helix/06-iterate/alignment-reviews/AR-YYYY-MM-DD[-scope].md`

Use the template at:

the alignment-review template in the runtime's templates directory.

The report must consolidate all review items into one coherent repo artifact.
It is the durable output of the review run.

## STEP 7 - Execution Work Items

After consolidation, create or update deterministic execution work items only
for real gaps that require follow-up work.

Execution work item rules:

- one coherent gap per work item
- use native upstream types such as `task`, `chore`, or `decision`
- assign HELIX activity/kind labels that match the actual work
- set `spec-id` to the nearest governing canonical artifact
- link to the source review item using description, parenting, or
  `discovered-from` dependencies
- when several execution items belong to one larger fix, create or reuse an
  epic parent instead of leaving them as flat siblings
- when one item must land before another can run safely, encode that as a
  dependency rather than prose in the description
- if a gap first requires design/doc/policy work and only then code changes,
  create the upstream planning item first and block the downstream
  implementation item on it
- do not close the governing alignment work item while actionable findings
  still exist only as prose in the report
- if canonical docs must change before implementation, create the doc/design
  item before the code item
- do not create duplicate items for the same gap
- after creating or materially updating an execution item, assemble or refresh
  its context digest using the runtime's context-digest reference or helper

### Work Item Coverage Verification

After creating execution work items, verify completeness:

1. For every gap in the Gap Register that is not ALIGNED, confirm at least one
   execution item exists that addresses it.
2. For every acceptance criterion classified as UNTESTED or UNIMPLEMENTED,
   confirm at least one execution issue exists that would resolve it.
3. For every quality concern recorded, confirm either an execution issue exists
   or the concern is explicitly deferred with rationale.

If coverage gaps remain, create the missing execution items before proceeding.
The item set must fully represent the work required to move from current state
to the end state defined by the planning stack.

If a ratchet regression was detected in Step 3, create a regression item that
references the specific criteria or metrics that dropped below the floor. The
item must include the previous floor value, the current measured value, and the
governing artifact where the regression is visible.

## STEP 8 - Execution Order

Output:

- dependency chain
- critical path
- parallelizable execution items
- blockers
- first recommended execution set
- queue health and exhaustion assessment for the reviewed scope

## Evidence Requirements

Every non-trivial claim must cite:

- planning evidence with file path and line reference where practical
- implementation evidence with file path and line reference where practical

Be explicit about inference when a conclusion is not directly stated by the
artifacts.

## STEP 9 - Measure

Verify the alignment review against the governing work item's acceptance
criteria. See the measure action for the full pattern.

1. **Completeness**: All functional areas in scope have a gap classification.
2. **Traceability**: The traceability matrix covers all in-scope artifacts.
3. **Work item coverage**: Every non-ALIGNED gap has at least one execution
   work item.
4. **Concern drift**: All concern drift findings are recorded and have
   corresponding execution items.
5. **Record results** on the governing work item via the runtime tracker.

## STEP 10 - Report

Close the alignment cycle and feed back into the planning cycle. See the
report action for the full pattern.

1. If measurement passed, close the governing work item with evidence summary.
2. If measurement identified gaps in the review itself (incomplete areas,
   missing traceability), create follow-on work items.
3. The execution items created in Step 7 are the primary output — they
   re-enter the planning cycle for polish and then build.

**Convergence criterion.** Alignment converges when the scope is **verified**
(every gap classified, traceability complete, zero `ASSERTED_UNBACKED` per Step
3) **and** each finding-class is **folded back into a gate** so it cannot
silently recur — not when a review simply reports "aligned." Resolve findings by
**progressive evolve** against the specific gap rather than re-splatting the
artifact stack; wholesale regeneration discards prior alignment work and
reintroduces resolved finding-classes.

## Output Format

Produce these sections in order:

1. Review Metadata
2. Scope and Governing Artifacts
3. Intent Summary
4. Planning Stack Findings
5. Implementation Map
6. Acceptance Criteria Status
7. Gap Register (with Quality Findings)
8. Traceability Matrix
9. Review Item Summary
10. Execution Items Generated
11. Item Coverage Verification
12. Execution Order
13. Open Decisions
14. Queue Health and Exhaustion Assessment
15. Measurement Results
16. Follow-On Items Created

Then emit the machine-readable trailer:

```
ALIGN_STATUS: COMPLETE|INCOMPLETE|BLOCKED
GAPS_FOUND: N
EXECUTION_ITEMS_CREATED: N
MEASURE_STATUS: PASS|FAIL|PARTIAL
ITEM_ID: <governing-item-id>
FOLLOW_ON_CREATED: N
```

Be precise, deterministic, and evidence-driven.

## DDx Integration Appendix

This appendix applies when DDx is the active HELIX runtime.

### STEP 0 — DDx bootstrap

```bash
ddx bead status  # stop immediately if this fails
```

- Principles: `.ddx/plugins/helix/workflows/references/principles-resolution.md`
- Concerns: `.ddx/plugins/helix/workflows/references/concern-resolution.md`
- Context-digest: `.ddx/plugins/helix/workflows/references/context-digest.md`
- Ratchets: `.ddx/plugins/helix/workflows/ratchets.md`
- Alignment-review template: `.ddx/plugins/helix/workflows/templates/alignment-review.md`

For beads in scope, check whether `<context-digest>` blocks reflect current
upstream state. Stale digests are an alignment finding.

### STEP 0.5 — DDx bead acquisition

```bash
ddx bead list --status open --label kind:planning,action:align --json

ddx bead update <id> --claim   # if found

# if not found:
ddx bead create "align: <scope description>" \
  --type task \
  --labels helix,kind:review,kind:planning,action:align \
  --set spec-id=<governing-artifact-if-known> \
  --description "<context-digest>...</context-digest>
Top-down reconciliation review for <scope>.
Scope areas: <list functional areas>" \
  --acceptance "Alignment review complete; all gaps classified; execution issues created for real gaps; traceability matrix produced"
```

Whenever this action creates a new bead or materially updates an existing bead
description, assemble or refresh its context digest per
`.ddx/plugins/helix/workflows/references/context-digest.md`. If the repo ships
`scripts/refresh_context_digests.py`, use it so digests and `area:*` labels
stay deterministic.

### STEP 3 — DDx acceptance criteria ratchet

```bash
# check ratchet floor fixtures from .ddx/plugins/helix/workflows/ratchets.md
```

### STEP 7 — DDx execution work items

```bash
ddx bead dep add <blocked-id> <blocking-id>
```

After creating or materially updating an execution bead, assemble or refresh
its context digest; if the repo ships `scripts/refresh_context_digests.py`,
use it instead of hand-editing digest XML.

Do not close the governing alignment bead while actionable findings still
exist only as prose in the report.

### DDx action input examples

```
/helix align repo
/helix align auth
/helix align FEAT-003
/helix align US-042
```

### DDx output trailer

```
ALIGN_STATUS: COMPLETE|INCOMPLETE|BLOCKED
GAPS_FOUND: N
EXECUTION_ISSUES_CREATED: N
MEASURE_STATUS: PASS|FAIL|PARTIAL
BEAD_ID: <governing-bead-id>
FOLLOW_ON_CREATED: N
```
