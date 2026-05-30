# HELIX Action: Reconcile Alignment

You are performing an iterative top-down reconciliation review of a HELIX
project.

Your goal is to re-align the implementation with the authoritative planning
stack, identify explicit divergence, determine whether additional execution
work remains for the reviewed scope, and produce deterministic next steps using
the runtime-provided work-item source.

This action is read-only with respect to product code unless explicitly told to
make fixes. It may create or update:

- review issues in the tracker
- execution issues in the tracker
- one durable alignment report in `docs/helix/06-iterate/alignment-reviews/`

## Action Input

You will receive a review scope as an argument. If no scope is given, default
to the repository.

## Authority Hierarchy

When artifacts disagree, use this authority hierarchy:

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

Use the runtime-provided work-item source only.

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
1. Verify the runtime-provided work-item source is available. If unavailable, run
   in **report-only mode** (see below) rather than stopping — the structural
   checks (Bidirectional Traceability, decomposition, AC validation) still run.
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

**Report-only mode (no work-item source).** When no runtime work-item source is
available, run the review read-only: emit all findings to the report / stdout with
**report finding IDs** (not owned issue IDs), and skip tracker acquisition,
tracker mutation, and Step 7 (execution work items). Every analysis step — the
Bidirectional Traceability surface map, decomposition granularity, concern/slot
integrity, and Acceptance Criteria Validation — runs unchanged; only the
tracker-write steps are skipped. This keeps the action runtime-vendor-neutral.

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

Unplanned code paths and dead/orphaned implementations are not a separate loose
check — they surface as findings in the structured inventory below.

### Review Dimensions (artifact-contract rubric)

Each governing artifact is a **contract with implementation implications**, and the
review's job is to verify *every* such contract against the code — not an ad-hoc
prose verdict that can silently omit a whole dimension (the failure mode: a review
that checks ACs and tooling but never asks whether the ADRs' decisions are honored
or the NFR targets are met). Review is therefore **artifact-driven**: walk each
artifact type, check its declared contract, and record the result so coverage is
auditable. Coverage is a **floor** (every dimension, and every in-scope item within
it, addressed) and never a **cap** (extra rigor is always welcome, never penalized).

| Dimension | Governing artifact | Contract the code must honor | Sub-check |
|---|---|---|---|
| Capability (FR) | PRD `FR-n`, `FEAT-NNN` | the requirement is implemented and traced | Bidirectional Traceability (code→spec) |
| Acceptance behavior | `US-NNN` ACs | each AC's behavior is exercised by a citing test that drives *that* AC | Acceptance Criteria Validation |
| Architecture decision | `ADR-NNN` | each accepted decision is reflected in code; no surface contradicts it | ADR Decision Honoring |
| Concern practice | `concerns.md` + practices | the concern's *behavioral* practices are realized in code (not only its tooling wired) | Concern Drift Detection |
| Concern→artifact realization | selected concern's `## Artifact Impact` | each selected concern's declared artifact obligations appear in the generated/evolved artifacts | Concern→Artifact Realization |
| Measurable NFR / budget | PRD/`FEAT` NFRs, design budgets | each measurable target is met or has observed evidence | NFR Target Verification |
| Decomposition | PRD subsystems → FEAT → story | structure is granular and reproducible | Acceptance Criteria Validation (decomposition) |
| Slot / instrument | `slots.yml`, templates/meta | the resolution + scoring instruments are intact | Slot Registry / Instrument-Integrity |

**Dimension Coverage Matrix (required output).** Emit one row per dimension above.
Each row carries the **denominators**, so a dimension cannot be counted "done"
while items inside it are silently skipped:

| Dimension | In-scope items found | Checked | Findings (non-ALIGNED) | Classification | Evidence |
|---|---|---|---|---|---|

- `In-scope items found` / `Checked` are counts (e.g. ADRs: 8 found / 8 checked;
  NFRs: 3 found / 3 checked). `Checked` < `found` is itself a completeness gap.
- `Classification` is the **worst** Step 4 value across the dimension's items
  (`ALIGNED` only when every item is).
- A dimension with no artifacts of that type is `N/A — <reason>` and must record
  the **search evidence** that establishes the absence (where you looked, what
  glob/grep returned nothing) — an unexamined `N/A` is not acceptable.
- A dimension row left **absent** is a **blocking review-completeness finding** —
  silent omission is the gap this rubric exists to close.

**Deterministic floor vs. model judgement.** Many checks here are *structural and
parseable* — they read the spec + code trees and need no judgement. Run the repo's
deterministic checker first to compute these reproducibly:
`scripts/helix_align_check.py` emits the coverage-matrix denominators and the
structural findings for decomposition (subsystem→FEAT→story, FR→FEAT, mega-FEAT,
naming), the `@covers` citation *inventory* (which ACs are cited, which citations
are dangling), and the ADR / NFR *inventories* (counts, status, naming). The
Slot-Registry Integrity check below is likewise fully deterministic (its six rules
read `slots.yml` + concern files). Spend model judgement on the **semantic**
verdicts the script deliberately defers and cannot decide: whether a cited test
*exercises that exact AC*, whether an ADR's *decision is honored* in code, whether
a concern's *behavioral practice is realized*, and whether an NFR *target is met*.
The deterministic pass makes the denominators identical across runtimes (the same
spec stack yields the same counts); the model pass supplies the behavioral truth
the counts cannot. If the repo does not ship the checker, perform the same
structural checks by hand. The checker is Python-3-standard-library-only and reads
files (no tracker, no harness dependency), so it runs identically under any
runtime (claude / codex / ddx).

### Bidirectional Traceability (spec ↔ code)

The spec is the contract; code is a projection of it (see the **Spec Is The
Contract** principle). Traceability runs **both ways** — neither direction is
primary, because a faithful evolve keeps both current and an unfaithful one can
break either. These checks are **structural and read the spec + code trees
directly** (no runtime tracker required — they run as report findings in a
no-tracker / report-only review).

**code → spec (no surface without a governing artifact).** Inventory the
**material surfaces** and map each to the artifact that governs it. A *material
surface* is externally-observable or lifecycle-significant: routes/endpoints,
screens/pages, CLI commands, **project-owned externally-consumed APIs / extension
points** (not incidental exported helpers or framework registrations), event
consumers/jobs, domain migrations, behavior-altering feature flags/config, and
deploy/runtime surfaces. **Exclude** generated/vendor/build output, framework
plumbing, passive wrappers, default config, and unexposed scaffolding. Product
capabilities map to a `FEAT`/`FR`/AC; technical/operational surfaces may map to an
`ADR`, technical-design, concern, deployment-checklist, runbook, or data-design.
Emit a **surface map** (one row per surface). `Kind` ∈ {capability, technical,
non-material}; `Classification` is one of the Step 4 values; `Mapping rationale`
states why that artifact governs the surface (or why the row is non-material/
excluded) — without it review-mapping is not reproducible:

| Surface | Evidence (file/path) | Kind | Governing artifact | Mapping rationale | Classification | Disposition |
|---|---|---|---|---|---|---|

- A material surface with **no** governing artifact is `UNDERSPECIFIED` (shipped
  but unspecced) or `DIVERGENT` (contradicts its spec) — **blocking once the
  stack is ready for handoff** (design/build/merge); during draft framing it is
  advisory. Allow a **temporary-scaffold** disposition only when the surface is
  unexposed/disabled and tied to a planned resolution.
- A dead/orphaned implementation (spec gone, code remains) is `STALE_PLAN` or
  `DIVERGENT`.
- Legitimate boilerplate/framework code is `Kind: non-material`, `Classification:
  ALIGNED` — recorded with evidence in `Disposition`, not forced to cite a feature.

**spec → code (no AC without an exercising, citing test).** The Acceptance
Criteria Validation below is the other half of this gate: every AC traces to an
exercising `@covers` test. An AC with no implementing+citing test takes its
existing AC-Validation status (`UNTESTED` / `ASSERTED_UNBACKED` / `UNCITED_COVERAGE`)
and is logged in the Gap Register; an AC whose **described behavior no longer
matches the code** (even if a test still passes) is `DIVERGENT`, not covered (the
exercise-not-just-cite rule guards this anti-rot case).

Both halves are coverage-floor checks: flag missing/ broken traceability, never
penalize extra rigor.

### ADR Decision Honoring

ADR naming/structure is checked under Acceptance Criteria Validation
(decomposition). This check is about the **decision itself**: an `accepted` ADR is
a binding architectural contract, so the code must reflect its decision — not
merely mention the ADR. For each ADR in scope:

1. **Decision realized (accepted ADRs).** For each `ADR-NNN` with status
   `accepted`, the *Decision* is observable in the implementation — the chosen
   mechanism, boundary, or pattern is the one in the code (e.g. ADR "single queue
   table with row-level locking" → the schema and dequeue path use it; ADR
   "per-tenant schema isolation" → queries are tenant-scoped). Cite the code
   evidence. An accepted ADR with no locatable implementation of its decision is
   `INCOMPLETE` (not yet built) or `UNDERSPECIFIED` (decision too vague to verify —
   an ADR-quality finding).
2. **Unaccepted ADR the code depends on.** If the implementation relies on a
   decision whose ADR is still `proposed` (not yet accepted), the decision is not a
   binding contract — classify `BLOCKED` or `UNDERSPECIFIED`, resolution
   `decision-needed` (accept the ADR, or stop depending on it). A `proposed` ADR
   does not silently become binding because its feature reached build.
3. **No contradicting surface.** No material surface implements the *rejected*
   alternative or otherwise contradicts an accepted decision (e.g. an ADR chose
   library X but a module imports Y for the same role). A contradiction is
   `DIVERGENT`, resolution `decision-needed` — either the code is wrong or the ADR
   is stale.
4. **Supersession / staleness.** An ADR superseded by a later ADR is checked
   against the **superseding** decision; the superseded one should carry
   `status: superseded`. When a newer higher-authority artifact (PRD/FEAT) has
   overtaken an ADR whose status was never updated, classify the ADR `STALE_PLAN`.
5. **Consequences present.** Where an accepted ADR records *Consequences* that
   imply code (a required migration, a compatibility shim, a monitoring hook),
   confirm they exist or are tracked. A missing implied consequence is `INCOMPLETE`.

Report each ADR with its decision, the code evidence (or its absence), and the
classification.

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

The checks above confirm each concern's **tooling** is wired and spot-check a few
security practices. Make this behavioral verification **explicit and systematic for
every active concern** — a wired tool does not guarantee the practice is followed
in the code:

5. **Behavioral practice realization.** Read the concern's practices and check the
   code embodies them, not just that the tool exists. Sample floor: in a small
   scope, check **all** material surfaces where the practice must hold; in a larger
   scope, a set of **named representative surfaces with the selection rationale
   recorded**, so the sample is reproducible.
   - **a11y-wcag-aa**: interactive elements have accessible names/roles; the active
     nav/location is marked (`aria-current`); forms have labels and error
     associations; keyboard focus is managed.
   - **security-owasp**: every state-changing or data-returning handler enforces
     authz and validates/parameterizes input; secrets are not hard-coded;
     authn/session/cookie handling matches the practice.
   - **o11y-otel**: the declared spans/metrics/logs are actually emitted on the real
     code paths, not merely importable.
   - **verification** concern: claims of behavior are backed by *observed
     running-system evidence*, not unit-green alone.
   A practice the tooling is wired for but the code does not follow is `DIVERGENT`
   (concern-behavior drift), distinct from a missing-tool finding; cite the specific
   unguarded handler / unlabeled control / unemitted span. This is a coverage floor
   — more practices verified, or a larger sample, is never a finding.

### Concern→Artifact Realization

Distinct from Concern Drift Detection above (which checks the concern's practices in the **code**),
this checks the concern's footprint in the **artifacts** — a concern is inert if it was selected but
left no trace in the documents it governs. For each concern selected in
`docs/helix/01-frame/concerns.md`, read its `## Artifact Impact` declaration (in
`workflows/concerns/<name>/concern.md` — the fixed vocabulary ADR / FEAT / TD / SD / DATA_DESIGN /
IMPLEMENTATION_PLAN / DESIGN_SYSTEM / TEST_PLAN) and verify each named artifact realizes it:

1. **Declared artifact present + realized.** For each artifact key a selected concern's
   `## Artifact Impact` names, the corresponding artifact exists AND carries the concern's decision —
   e.g. selected `domain-driven-design` → the technical-design models aggregates/value-objects/
   repositories and an ADR records the bounded-context/aggregate boundaries; `multi-tenancy` → the
   data-design has tenant scoping + an isolation ADR; `usage-metering` → the FEAT names billable
   actions and the implementation-plan wires metering. Cite the artifact evidence.
2. **Selected-but-inert is a finding.** A concern selected in `concerns.md` whose `## Artifact Impact`
   names artifact X, but X carries no trace of it, is `UNDERSPECIFIED` (the selection did not
   propagate) — **advisory during draft framing, blocking at design-exit and at evolve-handoff**.
   This is the gate that makes a concern *bite*: selecting it without realizing it is drift.
3. **Floor, not cap.** This is a floor on *selected* concerns only; an unselected concern's
   obligations need not appear, and extra concern coverage is never a finding.

One check, one output contract — the same `Concern→Artifact Realization` check runs at design-exit
and inside the evolve-until-converged loop. The model performs it by reading each selected concern's
`## Artifact Impact` and the artifacts it names. A deterministic floor (which selected concerns name
which artifacts, and whether those artifacts exist) is a planned `scripts/helix_align_check.py`
addition to pre-compute the structural part; until then the model performs the full check.

### NFR Target Verification

Non-functional requirements with a **stated, measurable** target (performance,
latency, throughput, availability, security posture, scalability,
accessibility-level) are contracts, so they are verified here against evidence.
This is distinct from the advisory Quality Evaluation in Step 4: **stated** NFR /
design-budget contracts are verified here; Step 4 Performance stays advisory for
*unstated* risks and general quality. **No-duplicate rule:** a stated-NFR failure
is reported here, not also as a generic Step 4 Performance finding. For each NFR
stated in the PRD, a `FEAT`, or a design budget, assign a Step 4 classification:

1. **Target is measurable.** The NFR names a target with a number/threshold and a
   condition (e.g. "p95 < 200ms at 100 rps", "supports 10k tenants", "WCAG 2.1
   AA"). An NFR stated only as an adjective ("fast", "scalable") is
   `UNDERSPECIFIED` — it cannot be verified.
2. **Evidence of meeting it.** Acceptable evidence is an observed measurement (a
   benchmark/load-test result at representative volume), an **executable guard** (a
   budget assertion in a test/CI that fails on regression), or an **explicitly
   reviewed analytical model** tied to a stated proof — not a bare index/query-plan
   asserted to be sufficient. Classification: target met = `ALIGNED`; target real
   but no measuring evidence = `INCOMPLETE`; evidence shows the target is *not* met
   = `DIVERGENT`; target overtaken/superseded by a higher-authority artifact but
   not updated = `STALE_PLAN`; measurement blocked by an external dependency =
   `BLOCKED`. (Per the honesty rule, an asserted-but-unmeasured NFR *figure* is also
   flagged `ASSERTED_UNBACKED` — a phantom claim, zero-tolerance — independent of
   the Step 4 classification above.)
3. **Ongoing guard where the target can regress.** A regression-prone budget should
   have an executable guard, not a one-off measurement; a regression-prone NFR with
   no guard is `INCOMPLETE`.

Record each NFR, its target, the evidence, and the classification in the Gap
Register and the Dimension Coverage Matrix. Extra NFRs verified beyond those stated
are welcome, never a finding.

### Slot Registry Integrity

A drifted slot registry corrupts high-autonomy concern resolution (FEAT-006
slots; the filler a slot resolves to comes straight from this registry), so the
instrument must be checked before its readings are trusted. Reconcile
`workflows/concerns/slots.yml` against the concern library
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

**Decomposition granularity (PRD subsystem → FEAT → story).** These checks are
**structural and parseable** — they read the spec files alone
(`docs/helix/01-frame/`, `02-design/adr/`), not a runtime tracker, so they run as
report findings even when no work-item source exists. They make decomposition
*reproducible* across runtimes (the same brief should yield comparable spec
stacks). All are coverage-floor checks (minimum rigor, never penalize more
features/stories). Apply once the frame stack is **ready for downstream handoff**
(design/build); during early draft framing a not-yet-decomposed stack is allowed.

Parsing anchors (exact, so the checks are reproducible): PRD subsystems are the
`### Subsystem: <name>` headings in `prd.md`; a feature's owned subsystems/FRs are
the `**Covered PRD Subsystem(s)**` and `**Covered PRD Requirements**` header fields
in each `FEAT-NNN-*.md`; its split-exemption is the `**Cross-Subsystem Rationale**`
field; a story's parent feature is the `**Feature**:` header field in each
`US-NNN-*.md`. Match subsystem names case-insensitively after trimming.

1. **Subsystem → FEAT coverage (blocking @ ready).** For each `### Subsystem:
   <name>` in `prd.md`, confirm **≥1 feature spec names it** in its
   `**Covered PRD Subsystem(s)**` field. A subsystem with no feature, **or a frame
   that has PRD subsystems but zero `FEAT-NNN` specs** (PRD → stories directly,
   skipping the feature tier), is a **blocking gap**.
2. **Mega-FEAT (advisory).** A feature whose `**Covered PRD Subsystem(s)**` lists
   **>1 subsystem** is an advisory finding — likely should split — **unless** its
   `**Cross-Subsystem Rationale**` field is non-empty (states that the
   cross-subsystem workflow *is* the feature). Do not block: legitimately
   cross-cutting features exist.
3. **FEAT → story (blocking @ ready).** Every `FEAT-NNN` is named by the
   `**Feature**:` field of **≥1 user story** (mirrors FR→story). A feature no story
   references is a coverage gap once ready for handoff.
4. **Artifact naming/structure (advisory).** Flag deviations from canonical,
   parseable forms: feature specs `FEAT-NNN-<name>.md`; user stories as
   **one file per story** `US-NNN-<slug>.md` (a single monolithic
   `user-stories.md` is a finding); ADRs `ADR-NNN-<name>.md` (uppercase, 3-digit;
   lowercase `adr-` or 4-digit is a finding); one decision per ADR (a lumped ADR
   is a finding). Non-canonical names break the structural checks above.

For each user story and feature spec in the reviewed scope:

1. Extract acceptance criteria from the governing artifact.
2. For each criterion, determine whether:
   - a test exists that **exercises** the criterion — via the
     **interface-appropriate harness** for the criterion's surface (web→Playwright,
     HTTP API→request client, CLI→shell/`expect`, TUI→tmux, backend/worker→integration;
     see the `testing` concern's *surface → real-path harness* mapping) it drives the
     criterion's action **and its guard/negative branch** (the rejection / failure /
     edge path) against the **running system** where the criterion is observable, and
     asserts the observed outcome of each. A test that merely names the criterion,
     runs adjacent code, asserts nothing relevant, **or drives only the happy path and
     never the guard branch** does **not** exercise it: classify that criterion
     `UNTESTED` — a guard branch left untested is **not `SATISFIED`** even when the
     happy-path unit test is green — and if an artifact *claims* the named test covers
     it, `ASSERTED_UNBACKED` — never "covered". A guard branch genuinely not
     applicable or not automatable is resolved only by the **recorded reviewed
     exception** of the AC coverage floor below (step 7: "manual verification
     accepted" / "non-automatable AC" with evidence — who verified, what was
     observed); an un-waived untested guard branch leaves the criterion `UNTESTED`.
   - the test passes
   - the implementation satisfies the criterion based on code inspection
   - the exercising test **cites the AC ID** in the canonical, parseable
     citation syntax — a structured tag `@covers <AC-ID>` (e.g.
     `@covers US-001-AC3`) in the test body, name, or a doc comment, using the
     story's stable `US-<n>-AC<m>` ID. This makes AC→test traceability
     machine-checkable rather than guessed. The citation is an **additional**
     gate on top of exercise+pass+satisfy — never a replacement for it; a
     citation alone, with no exercise, does not cover the criterion.
2a. **Cited-test ↔ AC behavioral match (operationalizes the `ASSERTED_UNBACKED`
    rule below).** A `@covers <AC-ID>` citation only holds when the cited test
    **drives the scenario of that exact AC** — the same precondition, action, and
    asserted outcome the AC describes. Do not accept a citation on name-match
    alone; read the cited test and confirm it exercises *this* AC, not a sibling
    AC's or adjacent code. Precedence when a citation is wrong (e.g. a test cites
    `US-005-AC1` "opt-out suppression created" but actually asserts send-exclusion):
    the **mis-cited AC** is `ASSERTED_UNBACKED` (a phantom traceability claim); the
    AC the test *actually* exercises, if real and uncited, is `UNCITED_COVERAGE`. Do
    not double-classify one AC as both `UNTESTED` and `ASSERTED_UNBACKED` — a wrong
    citation is `ASSERTED_UNBACKED`, honest silence (no citation) is `UNTESTED` or
    `UNCITED_COVERAGE`. This catches *wrong-AC* citations, not only *no* citation.
3. Classify each criterion as:
   - **SATISFIED** — test exists, passes, **cites the AC ID** in the canonical
     `@covers <AC-ID>` syntax, and implementation matches. (Exercise + pass +
     satisfy + citation.)
   - **TESTED_NOT_PASSING** — test exists but fails
   - **UNCITED_COVERAGE** — the **implementation satisfies** the criterion and a
     **passing test exercises it**, but no test cites the AC ID in the canonical
     syntax. The behavior is covered; the criterion is **not covered for AC
     *traceability***. This is
     **distinct from `UNTESTED`** (there *is* an exercising test) and from
     `ASSERTED_UNBACKED` (nothing untrue is asserted). The fix is to **add the
     `@covers <AC-ID>` citation to the existing test — NOT to write a new
     test.** Reported as an untraceable-coverage finding, not a missing-test
     finding.
   - **UNTESTED** — no test covers this criterion
   - **UNIMPLEMENTED** — no implementation addresses this criterion
   - **ASSERTED_UNBACKED** — an artifact *claims* this criterion is satisfied, names a test
     that covers it, **cites an AC ID via `@covers` from a test that does not actually exercise
     the criterion**, or states a coverage figure or emitted metric, but verification against the
     implementation finds no backing reality (the named test does not exist or does not exercise
     the AC it cites, the metric is never emitted, the figure is invented). This is a **phantom
     claim** — distinct from UNTESTED, which is honest about the gap, and from UNCITED_COVERAGE,
     which is honest behavioral coverage merely lacking a citation; ASSERTED_UNBACKED asserts
     something untrue. It is a traceability-honesty defect.
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
8. **AC-citation traceability gate (additional, not a replacement).** On top of the coverage floor,
   every covering test must **cite the AC ID it exercises** in the canonical `@covers <AC-ID>`
   syntax (per step 2), so AC→test traceability is machine-checkable. A criterion classified
   `UNCITED_COVERAGE` (exercises + passes, but no citation) is an **untraceable-coverage finding** —
   resolve it by **adding the `@covers <AC-ID>` citation to the existing test, NOT by writing a new
   test**. This gate is **distinct from the coverage floor**: `UNCITED_COVERAGE` ≠ `UNTESTED`
   (there is an exercising test; only the citation is missing) and ≠ `ASSERTED_UNBACKED` (nothing
   untrue is asserted). It makes coverage *traceable*, not *more numerous*; it is a floor on
   traceability, never a cap on tests.

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
- **Performance (unstated risks only)** — are there obvious scalability or
  latency risks **not already captured as a stated NFR**? *Stated*
  performance/scalability targets from requirements or design are verified in
  STEP 3 NFR Target Verification, not here (see its no-duplicate rule); this
  bullet covers only general, unstated quality risks the planning stack missed.

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

The report must consolidate all review items into one coherent repo artifact,
including the Dimension Coverage Matrix from Step 3 so the report shows every
review dimension was addressed. It is the durable output of the review run.

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
   confirm at least one execution issue exists that would resolve it. For every
   criterion classified `UNCITED_COVERAGE`, confirm an item exists to add the
   `@covers <AC-ID>` citation to the existing exercising test (not to write a
   new test).
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
5. **Dimension coverage**: Every review dimension appears in the Dimension
   Coverage Matrix with a classification or a recorded, evidenced `N/A`.
6. **Record results** on the governing work item via the runtime-provided work-item source.

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
6. Dimension Coverage Matrix
7. Acceptance Criteria Status
8. Gap Register (with Quality Findings)
9. Traceability Matrix
10. Review Item Summary
11. Execution Items Generated
12. Item Coverage Verification
13. Execution Order
14. Open Decisions
15. Queue Health and Exhaustion Assessment
16. Measurement Results
17. Follow-On Items Created

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

## Runtime Integration Appendix

This appendix covers how a runtime realizes the align action. The reference
paths and work-item acquisition below are runtime-neutral; for the concrete
commands of a specific runtime, see its install guide (DDx:
[docs/install/ddx.md](../../docs/install/ddx.md)).

### STEP 0 — Reference resolution

Verify the runtime-provided work-item source is reachable; if it is not, run in
report-only mode (see STEP 0.5) rather than stopping.

- Principles: `workflows/references/principles-resolution.md`
- Concerns: `workflows/references/concern-resolution.md`
- Context-digest: `workflows/references/context-digest.md`
- Ratchets: `workflows/ratchets.md`
- Alignment-review template: `workflows/templates/alignment-review.md`

For work items in scope, check whether `<context-digest>` blocks reflect current
upstream state. Stale digests are an alignment finding.

### STEP 0.5 — Work-item acquisition

Acquire the governing work item before modifying files, per
`workflows/references/bead-first.md`: find an open planning item labelled
`kind:planning,action:align` (claim it if found) or create one with labels
`helix,kind:review,kind:planning,action:align`, `spec-id` set to the governing
artifact if known, a `<context-digest>` description naming the scope of the
top-down reconciliation review and its functional areas, and acceptance
"Alignment review complete; all gaps classified; execution items created for
real gaps; traceability matrix produced". The runtime supplies the work-item
store; for the concrete commands see its install guide
([docs/install/ddx.md](../../docs/install/ddx.md) for DDx).

Whenever this action creates a new work item or materially updates an existing
item description, assemble or refresh its context digest per
`workflows/references/context-digest.md`. If the repo ships
`scripts/refresh_context_digests.py`, use it so digests and `area:*` labels
stay deterministic.

### STEP 3 — Deterministic structural checks

If the repo ships `scripts/helix_align_check.py`, run it first to compute the
deterministic coverage-matrix denominators and structural findings (decomposition
coverage, `@covers` citation inventory, ADR / NFR inventory) before the model's
semantic pass:

```
python3 scripts/helix_align_check.py --docs-root docs/helix --code-root . --format json
```

It is Python-3-standard-library-only and reads files only (no tracker / harness
dependency), so it runs identically across runtimes. Treat its output as the
reproducible floor and layer the STEP 3 semantic verdicts (AC-exercise,
ADR-decision-honoring, concern-behavior, NFR-target) on top. `--strict` exits
non-zero on a blocking structural finding for use as a gate.

### STEP 3 — Acceptance criteria ratchet

Check ratchet floor fixtures from `workflows/ratchets.md`.

### STEP 7 — Execution work items

Where ordering matters, declare a dependency from the blocked item to the
blocking item.

After creating or materially updating an execution item, assemble or refresh
its context digest; if the repo ships `scripts/refresh_context_digests.py`,
use it instead of hand-editing digest XML.

Do not close the governing alignment item while actionable findings still
exist only as prose in the report.

### Action input examples

```
/helix align repo
/helix align auth
/helix align FEAT-003
/helix align US-042
```

### Output trailer

```
ALIGN_STATUS: COMPLETE|INCOMPLETE|BLOCKED
GAPS_FOUND: N
EXECUTION_ISSUES_CREATED: N
MEASURE_STATUS: PASS|FAIL|PARTIAL
ITEM_ID: <governing-item-id>
FOLLOW_ON_CREATED: N
```
