# HELIX Action: Plan

You are creating a design plan for a HELIX project scope.

Your goal is the **minimal design that governs implementation without inventing
scope**: architecture, interfaces, errors, security, testing strategy, and
implementation ordering needed to build — not a completeness exercise.

Prefer short, implementable plans. Process redesign mid-delivery is not a plan
outcome; ship the product unit (or methodology content that changes behavior).

## Action Input

You may receive:

- a scope named in the request, such as `auth`, `FEAT-003`, or `payments`
- `--rounds N` as an optional upper bound on refinement passes

Infer scope from the named task when possible. Ask when no clear scope can be
inferred; do not expand to the whole repository by default.

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

0. Read the marker and bind the graph before editing. Load active principles
   and concerns when they affect the design.
1. Read the target and governing artifacts needed to resolve the requested
   scope. Follow linked artifacts only when their content could change the
   design.
2. Read implementation, tests, and tracked work only when they bear on the
   design question or the user requests them.
3. Identify the decisions the existing authority leaves open.
4. **Spiking is a first-class path to good design — de-risk before you commit.**
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
   "spike/unknown" is authoritative. When the unknown is a third-party
   candidate not yet chosen (a technology, product, or managed provider), write
   a **`component-profile`** (00-discover) per candidate first — the public
   record, cited, with a fit verdict — so the spike is spent only on what the
   record cannot settle. Define a **`tech-spike`** (or
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
5. **Load design artifact numbering rules** before creating an SD or TD:
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

## STEP 1 - First Draft

Produce a design document covering the sections that are **load-bearing for this
scope**. Omit optional sections that do not apply; do not invent content to fill
shells or add `N/A` entries.

When vision/PRD exist, each major implementation slice must name the **product
outcome** it advances. Reject slices that only deepen process machinery
(schema/digest/audit redesigns with no product outcome).

Candidate sections (use what this scope needs):

1. **Problem Statement and User Impact**
2. **Requirements Analysis** (functional, non-functional, constraints)
3. **Architecture Decisions** (question, alternatives, choice, why)
4. **Interface Contracts**
5. **Data Model**
6. **Error Handling Strategy**
7. **Security Considerations**
8. **Test Strategy**
9. **Implementation Plan with Dependency Ordering** — each slice needs an
   observable validation command or evidence path (not a milestone name)
10. **Risk Register** (record material risks and their mitigations)
11. **Observability**

### Concern-Mandated Sections

If active concerns require specific design coverage, those sections are
mandatory for this scope:

- `security-owasp` active → include an applicable threat model
- `o11y-otel` active → include an applicable observability plan
- `a11y-wcag-aa` active → Accessibility (WCAG AA) for user-facing surfaces
- Other active concerns → Check each concern's `practices.md` for design-activity
  requirements

## Refinement

Challenge only assumptions, interfaces, failure paths, security concerns, and
other material gaps in scope. Add detail when it resolves a real uncertainty or
lets an implementation slice be verified. Stop when the design is implementable
and no material ambiguity remains. Treat `--rounds N` only as an upper bound;
stop earlier when ready.

## ACTIVITY N+1 - Finalize

1. Write the final plan to:
   `docs/helix/02-design/plan-YYYY-MM-DD[-scope].md`
   where YYYY-MM-DD is today's date and scope is the input scope (omit if repo-wide).
2. Ensure the plan is self-contained: a reader should understand the full design
   without reading other documents, though it should cross-reference governing
   artifacts by path.

## ACTIVITY N+2 - Measure

Check the design against the request and relevant governing criteria. If a
runtime work item governs it, use that item's acceptance criteria.

1. **Acceptance criteria**: Design document exists at the canonical path;
   load-bearing and applicable concern-mandated sections are present;
   each major slice names an outcome (when vision/PRD exist) and a
   command/evidence validation path.
2. **Readiness**: implementation slices are verifiable and no material
   ambiguity remains, or identify what blocks readiness.
3. **Concern coverage**: Address applicable design requirements from active
   concerns; omit requirements that do not apply.
4. Record results on the governing work item when one applies.

## ACTIVITY N+3 - Report

Summarize the design, evidence, and any unresolved guidance.

1. If a runtime work item governs this design, record the evidence summary and
   follow that runtime's closure rules.
2. Create follow-on work only when requested or required by the runtime, for:
   - Missing concern-mandated sections
   - Sections that need further refinement
   - Guidance-dependent items
3. Before runtime dispatch, use polish when implementation slices still need
   decomposition into work items.

## Output

When the user or runtime requests structured output, these fields are
available:

```
PLAN_STATUS: CONVERGED|IN_PROGRESS|GUIDANCE_NEEDED
PLAN_DOCUMENT: docs/helix/02-design/plan-YYYY-MM-DD[-scope].md
PLAN_ROUNDS: N
MEASURE_STATUS: PASS|FAIL|PARTIAL
ITEM_ID: <governing-item-id>
FOLLOW_ON_CREATED: N
```

- `CONVERGED`: the design is implementable and no material ambiguity remains
- `IN_PROGRESS`: the requested round limit was reached before readiness
- `GUIDANCE_NEEDED`: a consequential ambiguity needs user input
