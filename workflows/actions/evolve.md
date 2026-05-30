# HELIX Action: Evolve

You are threading a new requirement through the project's artifact stack.

Your goal is to take a requirement — a feature request, constraint change,
spec amendment, incident learning, or customer feedback — and propagate it
through the governing documents, detect conflicts with existing work, create
properly triaged tracker issues for implementation, and produce a structured
evolution report.

This action modifies governing artifacts. Treat every write with the same
care as a production code change.

## Action Input

You receive:

- A requirement description (natural language or structured)
- Optional: `--scope` to limit blast radius (e.g., `area:wal`, `SD-017`)
- Optional: `--artifact` to target a specific governing artifact
- Optional: `--from` to indicate the requirement source (incident, feedback, etc.)

## Authority Hierarchy

When artifacts disagree, use this precedence:

1. Product Vision
2. Product Requirements
3. Feature Specs / User Stories
4. Architecture / ADRs
5. Solution Designs / Technical Designs
6. Test Plans / Tests
7. Implementation Plans
8. Source Code / Build Artifacts

Update higher-authority documents FIRST, then propagate downward. Never
update a lower-authority artifact in a way that contradicts a higher one.

## Evolve Default and Convergence

**Evolve is the default for threading change.** When a new, changed, removed, or
incident-driven requirement lands, prefer **progressive evolution** — amend the
specific artifacts the requirement touches — over re-generating ("re-splatting")
the artifact stack. Re-splat discards prior review investment and reintroduces
finding-classes that were already resolved. Touch only what the requirement
affects.

**Convergence is not "the reviewer said SHIP."** An evolution converges when:

1. the updated artifacts are **verified** — consistent with higher authority, no
   unresolved conflicts, downstream work items created, and the
   claims-vs-reality check clean (zero `ASSERTED_UNBACKED`; see
   `workflows/ratchets.md` and FEAT-016); **and**
2. each **finding-class** surfaced during the pass is **folded back into a gate**
   (a template check, an acceptance criterion, a concern propagation check, or a
   ratchet) so the same class cannot silently recur.

A reviewer verdict is evidence toward (1), never a substitute for (2). If a
finding-class cannot be folded into a gate this pass, file it as explicit
follow-on work rather than declaring convergence.

**Intrinsic gates are blocking; external adversarial review is advisory.** The
intrinsic gates — build, test, template conformance, the phantom-claim count —
block convergence. An external adversarial reviewer (a separate tool or model)
is advisory input only and must never be a hard gate: when it hangs, errors, or
is unavailable, convergence is decided by the intrinsic gates, not stalled
waiting on it.

## STEP 0 — Bootstrap

0. **Load active design principles** following the principles-resolution
   reference for this runtime. Use these as scoping guidance when evaluating
   which artifacts need updates and how to resolve judgment calls. Note: the
   evolve action reads principles but never modifies the principles file —
   only the frame action may write it.
0a. **Load active concerns and practices** following the concern-resolution
   reference for this runtime. Concern context affects the scope of downstream
   changes:
   - A requirement that implies a technology change (new language, new framework,
     new runtime, new dependency) must be checked against declared concerns.
   - If the change conflicts with an active concern (e.g., adding a Node.js
     dependency in a `typescript-bun` project, or introducing `println!` logging
     in an `o11y-otel` project), flag it as a conflict requiring an ADR.
   - If the requirement implies adopting a technology that has a library concern
     but the project doesn't yet declare it, include concern selection as part of
     the evolution — create or update `docs/helix/01-frame/concerns.md` alongside
     the other artifact updates.
   - If the requirement removes or replaces a technology covered by an active
     concern, the concern declaration and project overrides must be updated as
     part of Step 4 artifact evolution.
0b. **Context digest**: When this action creates or modifies work items, it
   must assemble a context digest per the runtime's context-digest reference
   and prepend it to the item description. If a repo helper exists for digest
   assembly, use it instead of hand-writing the XML. The concerns element must
   contain matched concern names, never area labels.

## STEP 0.5 — Work Item Acquisition

Before modifying any artifacts, acquire a governing work item for this
evolution pass. See the runtime's work-item acquisition reference for the full
pattern.

## STEP 1 — Requirement Analysis

Parse the input requirement:

1. Identify the core change — what capability, constraint, or behavior is
   being added, changed, or removed.
2. Classify the type: new feature, amendment, constraint, policy change,
   incident remediation.
3. Assess scope: which subsystems, interfaces, and data models are affected.
4. If the requirement is ambiguous, state your interpretation explicitly
   and proceed. Do not halt for clarification on things you can reasonably
   infer.

## STEP 2 — Artifact Discovery

Search the project's doc tree for governing artifacts in scope:

1. Read `AGENTS.md` for the project's artifact structure.
2. Search for artifacts that reference the affected subsystems, interfaces,
   or capabilities.
3. Build an ordered list of artifacts to review, highest authority first.
4. For each artifact, note its current state and the section(s) that will
   need updating.
5. **If the evolution will create new numbered artifacts**, load the relevant
   meta.yml files and determine the next available IDs now — before writing
   anything:
   - **New feature spec (FEAT-NNN)**: read the feature-specification meta.yml,
     scan `docs/helix/01-frame/features/FEAT-*.md`, set next FEAT ID = max + 1
     (use `001` if none exist).
   - **New solution design (SD-NNN)**: read the solution-design meta.yml,
     scan `docs/helix/02-design/solution-designs/SD-*.md`, set next SD ID =
     max + 1.
   - **New technical design (TD-NNN)**: read the technical-design meta.yml,
     scan `docs/helix/02-design/technical-designs/TD-*.md`, set next TD ID =
     max + 1.
   - Record these values. Use them exclusively when assigning IDs; never guess
     or reuse an existing number.

Use commands like:
- `find docs/ -name "*.md" | xargs grep -l "keyword"`
- List open work items from the runtime-provided work-item source to find related open items

## STEP 3 — Conflict Detection

For each affected artifact:

1. Read the relevant sections.
2. Check whether the new requirement contradicts existing content.
3. Check whether the new requirement conflicts with open tracker issues.
4. Check whether the new requirement conflicts with active concerns:
   - Does it introduce a tool, framework, or convention that contradicts a
     declared concern's constraints or practices?
   - Does it require a technology not covered by any active concern? **If so,
     decide by RISK** (same rule as `concern-resolution.md`): clear/low-risk,
     well-understood (known provider, standard integration) → add a concern
     (provider-behind-abstraction) or capture it in an ADR; **material
     uncertainty** — unknown/changing API, cost, permissions/credentials,
     correctness, or operational risk (true even for a known vendor: billing,
     marketplaces, send-time optimization, queue design) → define a **`tech-spike`**
     and de-risk it before committing the design. Prefer a **bounded runnable**
     spike when feasible; when running is infeasible/unsafe (external/paid APIs,
     missing creds, long benchmarks) record a **blocked spike** (why it could not
     run, what was read/simulated, which decisions stay provisional).
     **Anti-reframe (this is where evolve commonly fails):** "low-risk" means the
     capability's design-defining facts are **evidenced** (operator statement,
     governing artifact, existing implementation, docs/API proof, completed spike) —
     not model familiarity, and not because you picked a mechanism or named a
     provider. Name the **top 1-3 design-defining decisions** (API shape, data
     model, pricing/cost, security/permissions, operational guarantees, or
     decomposition); if any is **assumed**, spike it — **even with a provider
     chosen and its live integration deferred** (deferral de-risks timing, not the
     decision). Deferring the vendor call does not defer the **app-side data the
     current slice's integration contract requires** — the events/records the app
     must emit (e.g. usage-metering events) are build-work for the slice; sequencing
     the outbound call later is legitimate only after spike/blocked-spike/guidance-needed
     is recorded. An operator-marked "spike/unknown" is authoritative; don't demote it. The only alternative to a spike is a **recorded assumption + residual-risk
     note**, and only when reversible/non-blocking/provisional or the spike is
     blocked. A **business** unknown a technical spike can't answer (e.g. pricing) →
     record guidance-needed or a blocked spike. Never fabricate a concern for the
     not-yet-understood, and never silently drop the requirement.
   - Would it change the project's area taxonomy or concern applicability?
5. For each conflict found, record:
   - Artifact and section (or concern name, for concern conflicts)
   - What the artifact or concern currently says
   - What the requirement asks for
   - Whether the conflict is resolvable by reasonable interpretation or
     requires human decision
   - For concern conflicts: whether an ADR is needed to justify the departure

Conflicts that require human decision are flagged but do NOT halt the
entire evolution. Proceed with non-conflicting artifacts.

When a concern conflict is identified, the resolution options are:

- **ADR + concern update**: Create an ADR justifying the technology change,
  then update `concerns.md` to reflect the new selection.
- **Project override**: Add or modify a project override in `concerns.md`
  that documents the exception and its rationale.
- **Reject**: The requirement is incompatible with the project's technology
  commitments and should be reconsidered.

## STEP 4 — Artifact Evolution

For each non-conflicting artifact, from the highest-authority artifact down:

1. Read the current document.
2. Draft the amendment — add, modify, or extend the relevant sections.
3. Validate the amendment does not contradict any higher-authority artifact
   that was already updated in this session.
4. For any **new** artifact being written (not an update to an existing file):
   - Confirm the ID was assigned from the scanned-next-ID computed in Step 2,
     not guessed.
   - Inspect the artifact frontmatter `depends_on` list. For each referenced
     ID, verify the target artifact exists on disk before writing. If a target
     is missing, either remove the dependency or stop and request guidance.
     Never write an artifact with a broken `depends_on` reference.
5. Write the update.
6. If the project uses acceptance manifests (`.acceptance.toml`), update
   those too with new or modified acceptance criteria.
7. If the update touches acceptance artifacts, set
   `NIFLHEIM_ACCEPTANCE_CHANGE=1` before committing.

Keep amendments minimal and scoped. Do not rewrite sections that aren't
affected by the requirement.

## STEP 5 — Work Item Decomposition

Create work items for the implementation work implied by the updated artifacts:

1. For each updated artifact, determine what code changes are needed.
2. Create work items that are individually implementable in one build cycle.
3. Each work item must:
   - carry labels `helix,activity:build,...`
   - set `spec-id` to the updated artifact
   - have deterministic acceptance criteria
4. Set parent if the items belong to an existing epic.
5. Group related items under a new epic if the requirement implies
   multiple implementation slices.

## STEP 6 — Dependency Wiring

Search existing open work items for overlap with the new items:

1. Retrieve the current open item queue from the runtime-provided work-item source.
2. For each new item, check if existing items touch the same files,
   subsystems, or acceptance criteria.
3. Add dependency links where ordering matters.
4. If the new requirement supersedes an existing item, record the supersession.

## STEP 7 — Evolution Report and Commit

1. Commit all artifact changes with a message referencing the requirement
   and the governing work item ID.
2. Push to the remote.

## STEP 8 — Measure

Verify the evolution against the governing work item's acceptance criteria.
See the measure action for the full pattern.

1. **Artifact consistency**: All updated artifacts are consistent with each
   other and with higher-authority artifacts.
2. **Conflict resolution**: All resolvable conflicts were resolved; remaining
   conflicts are documented with clear resolution options.
3. **Work item completeness**: Downstream implementation work items were created
   for all code changes implied by the updated artifacts.
4. **Concern threading**: If the requirement introduced or changed a concern,
   verify the concern is properly declared and its practices are referenced
   in new work items.
5. **Self-validation mode-gate (must fail on findings)**: the verify activity
   over the updated artifacts must yield no blocking finding. This is a
   workflow-mode gate, not a literal "run validate+align+check" command list —
   confirm the artifacts are internally consistent and the claims-vs-reality
   check is clean (`ASSERTED_UNBACKED` count is zero). A blocking finding here
   means convergence is not reached; fold the finding-class into a gate or file
   it as follow-on work.
6. **Record results** on the governing work item via the runtime-provided work-item source.

## STEP 9 — Report

Close the evolution cycle and feed back into the planning cycle. See the
report action for the full pattern.

1. If measurement passed, close the governing work item with evidence summary.
2. If conflicts remain, create follow-on work items for each unresolved
   conflict requiring human decision.
3. Output a structured report:

```
## Evolution Report

### Requirement
[summary of the requirement]

### Artifacts Updated
- [artifact]: [what changed]

### Artifacts Skipped (Conflicts)
- [artifact]: [conflict description — what needs human resolution]

### Work Items Created
- [id]: [title] (spec-id: [ref], deps: [ids])

### Dependencies Wired
- [new-id] depends on [existing-id]: [reason]

### Open Conflicts Requiring Human Resolution
- [description with specific artifact references]
```

4. Output the required trailer:

```
EVOLUTION_STATUS: COMPLETE|CONFLICTS|BLOCKED
ARTIFACTS_UPDATED: [count]
ITEMS_CREATED: [count]
CONFLICTS: [count]
MEASURE_STATUS: PASS|FAIL|PARTIAL
ITEM_ID: <governing-item-id>
FOLLOW_ON_CREATED: N
```

`COMPLETE` means all artifacts updated and work items created with no conflicts.
`CONFLICTS` means some artifacts were skipped due to conflicts that need
human resolution, but non-conflicting work was completed.
`BLOCKED` means the requirement fundamentally contradicts the project's
governing artifacts and cannot proceed without human decision.

## Runtime Integration Appendix

This appendix covers how a runtime realizes the evolve action. The reference
paths and work-item acquisition below are runtime-neutral; for the concrete
commands of a specific runtime, see its install guide (DDx:
[docs/install/ddx.md](../../docs/install/ddx.md)).

### STEP 0 — Reference resolution

- Principles: `workflows/references/principles-resolution.md`
- Concerns: `workflows/references/concern-resolution.md`
- Context-digest: `workflows/references/context-digest.md`
- Feature-specification meta: `workflows/activities/01-frame/artifacts/feature-specification/meta.yml`
- Solution-design meta: `workflows/activities/02-design/artifacts/solution-design/meta.yml`
- Technical-design meta: `workflows/activities/02-design/artifacts/technical-design/meta.yml`

The `<concerns>` element in a context digest must contain matched concern
names, never `area:*` labels.

### STEP 0.5 — Work-item acquisition

Acquire the governing work item before modifying files, per
`workflows/references/bead-first.md`: find an open planning item labelled
`kind:planning,action:evolve` (claim it if found) or create one with labels
`helix,activity:design,kind:planning,action:evolve`, a `<context-digest>`
description naming the requirement being threaded through the artifact stack
and its source (the `--from` value if provided), and acceptance "Requirement
threaded through all affected artifacts; no unresolved conflicts; downstream
work items created with context digests". Record the item ID; all subsequent
artifact modifications are governed by it. The runtime supplies the work-item
store; for the concrete commands see its install guide
([docs/install/ddx.md](../../docs/install/ddx.md) for DDx).

### STEP 2 — Find related items

List open work items from the runtime-provided work-item source to find items
related to the affected subsystems.

### STEP 6 — Dependency wiring

List open work items from the runtime-provided work-item source. Where ordering
matters, declare a dependency from the blocked item to the blocking item. If the
new requirement supersedes an existing item, mark the old item superseded by the
new one.

### STEP 7 — Commit

Commit with a message referencing the requirement and the governing item ID.

### Output trailer

```
EVOLUTION_STATUS: COMPLETE|CONFLICTS|BLOCKED
ARTIFACTS_UPDATED: [count]
ISSUES_CREATED: [count]
CONFLICTS: [count]
MEASURE_STATUS: PASS|FAIL|PARTIAL
ITEM_ID: <governing-item-id>
FOLLOW_ON_CREATED: N
```
