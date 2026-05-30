# HELIX Action: Plan

You are creating a comprehensive design plan for a HELIX project scope.

Your goal is to produce a thorough markdown design document through iterative
self-critique and refinement, capturing architecture, interfaces, error
handling, security, testing strategy, and implementation ordering — all before
any code is written or issues are created.

This action is intentionally front-loaded. Invest deeply in planning quality
now to prevent expensive rework during implementation.

## Action Input

You may receive:

- no argument (default: repo-wide plan)
- a scope such as `auth`, `FEAT-003`, `payments`
- `--rounds N` controlling refinement iterations (default: 5)

## Authority Hierarchy

When artifacts disagree, use this hierarchy:

1. Product Vision
2. Product Requirements
3. Feature Specs / User Stories
4. Architecture / ADRs
5. Solution Designs / Technical Designs
6. Test Plans / Tests
7. Implementation Plans
8. Source Code / Build Artifacts

The plan you produce sits at levels 4-7 and must be consistent with levels 1-3
when they exist.

## STEP 0 - Context Load

0. **Context Recovery**: Re-read AGENTS.md so project instructions are fresh
   in your working memory. After long sessions, context compaction may have
   dropped critical project rules. This step is cheap insurance against drift.
0a. **Load active design principles** following the principles-resolution
   reference for this runtime. These principles guide architectural and design
   judgment throughout the plan.
0b. **Load active concerns and practices** following the concern-resolution
   reference for this runtime. The declared concerns constrain architecture
   decisions — design within the declared technology selections. Reference
   ADRs that justify concern choices when the design depends on them.
1. Read all existing planning artifacts for the scope:
   - product vision, PRD, feature specs, user stories
   - architecture docs, ADRs, technical designs
   - existing test plans and implementation plans
2. Read the current implementation state relevant to the scope.
3. Read the current work queue state if the tracker is initialized.
4. Identify gaps: what questions does the existing planning stack leave open?
4a. **Spiking is a first-class path to good design — de-risk before you commit.**
   For any hard or unknown choice (a capability with material uncertainty: unknown
   or changing API, cost, permissions/credentials, correctness, or operational
   risk — true even for a known vendor, e.g. billing, marketplaces, send-time
   optimization, queue design), do not let the ADR/technical-design commit on
   assumption. **Anti-reframe:** "known/low-risk" means design-defining facts are
   **evidenced** (operator statement, governing artifact, existing implementation,
   docs/API proof, completed spike) — not model familiarity, and not because you
   picked a mechanism or named a provider. Name the **top 1-3 design-defining
   decisions** (API shape, data model, pricing/cost, security/permissions,
   operational guarantees, decomposition); if any is **assumed**, spike it — even
   with a provider chosen and its live integration deferred. An operator-marked
   "spike/unknown" is authoritative. Define a **`tech-spike`** (or
   `proof-of-concept`) and de-risk it
   first: a **bounded runnable** spike when feasible, else a recorded **blocked
   spike** (why it could not run, what was read/simulated, which decisions stay
   provisional). The only alternative is a recorded **assumption + residual-risk**
   note, acceptable only when reversible/non-blocking/provisional or the spike is
   blocked; a **business** unknown a technical spike can't answer (e.g. pricing) →
   record guidance-needed or a blocked spike. Feed the spike's findings into the
   ADR/technical-design. (Same risk-based rule as `concern-resolution.md` and
   `evolve.md`; spike artifacts:
   `workflows/activities/02-design/artifacts/{tech-spike,proof-of-concept}/`.)
5. **Load design artifact numbering rules** (required before creating any SD or
   TD artifact):
   - Read the solution-design meta.yml to understand the SD-{number} format,
     naming pattern, and no-reuse policy.
   - Read the technical-design meta.yml to understand the TD-{number} format.
   - Scan `docs/helix/02-design/solution-designs/SD-*.md` to find the maximum
     existing SD number; **next SD ID = max + 1** (use `001` if none exist).
   - Scan `docs/helix/02-design/technical-designs/TD-*.md` to find the maximum
     existing TD number; **next TD ID = max + 1** (use `001` if none exist).
   - Record both values. Use them exclusively when assigning IDs to new SD or
     TD artifacts in this session; increment by one for each additional artifact
     created. Never guess or reuse an existing number.
   - Before writing any SD or TD artifact, validate each `depends_on` entry in
     its frontmatter: every referenced ID (e.g., `FEAT-XXX`) must resolve to an
     existing artifact on disk. If a target does not exist, stop and request
     guidance before writing the file.

## STEP 0.5 - Work Item Acquisition

Before writing any design content, acquire a governing work item for this
design pass to record progress, govern changes, and capture measurement
results. See the runtime's work-item acquisition reference for the full
pattern.

## STEP 1 - First Draft

Produce a comprehensive design document covering ALL of the following sections.
Do not skip sections; mark them "N/A" with rationale if genuinely inapplicable.

1. **Problem Statement and User Impact**
   - What problem does this solve? Who benefits? What happens if we don't solve it?
2. **Requirements Analysis**
   - Functional requirements (what the system must do)
   - Non-functional requirements (performance, scalability, reliability)
   - Constraints (technology, timeline, compliance)
3. **Architecture Decisions**
   - For each decision: state the question, list alternatives considered,
     explain the chosen approach and why alternatives were rejected
4. **Interface Contracts**
   - APIs, CLIs, configuration surfaces, file formats
   - Input validation rules and error response formats
5. **Data Model**
   - Entities, relationships, storage, migration strategy
6. **Error Handling Strategy**
   - Error categories, retry policies, fallback behavior, user-facing messages
7. **Security Considerations**
   - Attack surfaces, authentication, authorization, data protection
   - Threat model for new surfaces introduced
8. **Test Strategy**
   - What to test at each level (unit, integration, e2e)
   - Critical paths that must have coverage before shipping
9. **Implementation Plan with Dependency Ordering**
   - Work breakdown into issue-sized slices
   - Dependency graph showing what must be built first
   - Parallel tracks that can proceed independently
10. **Risk Register**
    - Known risks, likelihood, impact, mitigation strategy
11. **Observability**
    - Logging, metrics, alerting, dashboards

### Concern-Mandated Sections

If active concerns require specific design coverage, those sections are
mandatory (not just "recommended"):

- `security-owasp` active → Section 7 (Security Considerations) must include
  OWASP-aligned threat model, not just a placeholder.
- `o11y-otel` active → Section 11 (Observability) must include OpenTelemetry
  instrumentation plan with specific spans, metrics, and trace propagation.
- `a11y-wcag-aa` active → Add a **12. Accessibility** section covering WCAG AA
  compliance strategy for all user-facing surfaces.
- Other active concerns → Check each concern's `practices.md` for design-activity
  requirements and ensure the plan addresses them.

The governing work item's acceptance criteria include concern-mandated section
completeness.

## STEP 2 through N - Iterative Refinement

For each subsequent round:

1. Re-read AGENTS.md to refresh project context.
2. **Assume there are 80+ elements you have missed or underspecified.** This is
   not a suggestion — actively search for gaps in every section.
3. Challenge every assumption, interface, error path, and edge case.
4. For each section, ask:
   - What happens when this fails?
   - What happens at 10x scale?
   - What happens when the input is malformed?
   - What happens when a dependency is unavailable?
   - What would a security reviewer flag?
   - What would an oncall engineer need at 3am?
5. Add missing:
   - Error handling paths and recovery procedures
   - Concurrency considerations and race conditions
   - Migration strategies and backward compatibility
   - Rollback procedures
   - Monitoring and observability hooks
   - Performance constraints and benchmarks
   - Security attack surfaces
6. Track changes between rounds in a **Refinement Delta** section at the end:
   - Round number
   - Count of substantive changes
   - Summary of what changed and why

## Convergence Detection

Track a refinement velocity metric: count of substantive changes per round.
A substantive change is one that affects behavior, interfaces, error handling,
security, or architecture — not formatting or wording.

When velocity drops below 5 substantive changes for two consecutive rounds,
declare convergence and stop refinement.

## ACTIVITY N+1 - Finalize

1. Remove the Refinement Delta section (it served its purpose during iteration).
2. Write the final plan to:
   `docs/helix/02-design/plan-YYYY-MM-DD[-scope].md`
   where YYYY-MM-DD is today's date and scope is the input scope (omit if repo-wide).
3. Ensure the plan is self-contained: a reader should understand the full design
   without reading other documents, though it should cross-reference governing
   artifacts by path.

## ACTIVITY N+2 - Measure

Verify the design document against the governing work item's acceptance
criteria. See the measure action for the full pattern.

1. **Acceptance criteria**: Verify the design document exists at the canonical
   path and contains all required sections (including concern-mandated ones).
2. **Convergence**: Confirm refinement velocity dropped below threshold or
   explain why it did not.
3. **Concern coverage**: Verify each active concern's design-activity requirements
   are addressed in the plan.
4. **Record results** on the governing work item via the runtime-provided work-item source.

## ACTIVITY N+3 - Report

Close the design cycle and feed back into the planning cycle. See the report
action for the full pattern.

1. If measurement passed, close the governing work item with evidence summary.
2. If measurement identified gaps, create follow-on work items for:
   - Missing concern-mandated sections
   - Sections that need further refinement
   - Guidance-dependent items
3. Note: The design document itself is not an execution work item — it must go
   through the polish action to be decomposed into implementable items before
   the build action can execute against it.

## Output

Report these trailer lines at the end of your output:

```
PLAN_STATUS: CONVERGED|IN_PROGRESS|GUIDANCE_NEEDED
PLAN_DOCUMENT: docs/helix/02-design/plan-YYYY-MM-DD[-scope].md
PLAN_ROUNDS: N
MEASURE_STATUS: PASS|FAIL|PARTIAL
ITEM_ID: <governing-item-id>
FOLLOW_ON_CREATED: N
```

- `CONVERGED`: refinement velocity dropped below threshold
- `IN_PROGRESS`: max rounds reached but velocity still high
- `GUIDANCE_NEEDED`: ambiguity that requires user input before the plan can converge

## Runtime Integration Appendix

This appendix covers how a runtime realizes the design action. The reference
paths and work-item acquisition below are runtime-neutral; for the concrete
commands of a specific runtime, see its install guide (DDx:
[docs/install/ddx.md](../../docs/install/ddx.md)).

### STEP 0 — Reference resolution

- Principles: `workflows/references/principles-resolution.md`
- Concerns: `workflows/references/concern-resolution.md`
- Solution-design meta: `workflows/activities/02-design/artifacts/solution-design/meta.yml`
- Technical-design meta: `workflows/activities/02-design/artifacts/technical-design/meta.yml`

Validate `depends_on` entries in each artifact's `ddx:` frontmatter before writing.

### STEP 0.5 — Work-item acquisition

Acquire the governing work item before writing any design content, per
`workflows/references/bead-first.md`: find an open planning item labelled
`kind:planning,action:design` (claim it if found, filtering by scope or
`spec-id` when dispatched with a scope) or create one with labels
`helix,activity:design,kind:planning,action:design`, a `spec-id` pointing at the
governing artifact if known, a `<context-digest>` description that names the
scope to design for and the governing artifacts loaded in Step 0, and acceptance
"Design document converged with all required sections including concern-mandated
sections; written to canonical path". All subsequent file modifications are
governed by this work item. The runtime supplies the work-item store; for the
concrete commands see its install guide
([docs/install/ddx.md](../../docs/install/ddx.md) for DDx).

### Action input examples

```
/helix design
/helix design auth
/helix design --rounds 8 FEAT-003
```

### ACTIVITY N+2 — Record results

Record the measure results on the governing work item through the runtime
tracker.

### Output trailer

```
PLAN_STATUS: CONVERGED|IN_PROGRESS|GUIDANCE_NEEDED
PLAN_DOCUMENT: docs/helix/02-design/plan-YYYY-MM-DD[-scope].md
PLAN_ROUNDS: N
MEASURE_STATUS: PASS|FAIL|PARTIAL
ITEM_ID: <governing-item-id>
FOLLOW_ON_CREATED: N
```

Note: The design document must go through `/helix polish` to be decomposed
into implementable work items before the runtime executes ready work items
against it.
