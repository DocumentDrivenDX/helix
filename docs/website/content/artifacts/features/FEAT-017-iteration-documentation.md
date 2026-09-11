---
title: "Feature Specification: FEAT-017 — Iteration Documentation"
slug: FEAT-017-iteration-documentation
weight: 150
activity: "Frame"
source: "01-frame/features/FEAT-017-iteration-documentation.md"
generated: true
collection: features
---

> **Example from HELIX's own docs.** This generated page comes from `docs/helix/`. Use it to see the method in practice; start with the [artifact-type catalog](/artifact-types/) for reusable templates. Historical plans and reports may describe retired architecture.

> **Source identity** (from `01-frame/features/FEAT-017-iteration-documentation.md`):

```yaml
ddx:
  id: FEAT-017
  authoring:
    home: repo
  depends_on:
    - helix.prd
  status: draft
```

# Feature Specification: FEAT-017 — Iteration Documentation

**Feature ID**: FEAT-017
**Status**: Draft
**Priority**: P1
**Owner**: HELIX maintainers

## Overview

The HELIX catalog covers the artifact-authority axis (vision → PRD →
features → designs → tests → implementation plans) thoroughly, but has no
artifact types on the time/commitment axis: how a human team sequences
outcomes across iterations, commits one iteration's worth with owners and
trade rules, and records how the iteration went. FEAT-017 adds the three
missing types — `roadmap` (01-frame), `iteration-plan` (06-iterate), and
`status-report` (06-iterate) — plus one `iterate` workflow route in the
routing skill that ties them into a loop with the existing
`improvement-backlog`.

## Ideal Future State

A team running HELIX on a human cadence (sprints, program increments,
consulting engagements) documents each iteration with governed artifacts:
the roadmap sequences framed outcomes across iterations; the iteration
plan commits one time-box with a falsifiable goal, tiered outcomes,
owners, and stable-ID task tables; the status report records outcome
status against the plan with evidence per claim. Runtime work-item
surfaces (DDx beads, markdown boards, GitHub issues) derive from the
iteration plan's task tables and own live status — the plan decides what
work exists, the tracker decides where each item stands. Review learnings
land in the improvement backlog, whose next-iteration selection feeds the
next plan, closing the 06-iterate loop.

## Problem Statement

- **Current situation**: `improvement-backlog` walks up to the commitment
  boundary and stops — it has a required `selection_for_next_iteration`
  section and describes itself as "ordered candidates for future execution
  without becoming the live tracker"
  (`workflows/activities/06-iterate/artifacts/improvement-backlog/meta.yml`).
  No type holds the commitment itself. `implementation-plan` (04-build)
  decomposes an *approved design* into build slices; it cannot hold a
  cross-workstream, time-boxed team commitment. The routing skill's
  engage list names "roadmap brief" as a HELIX artifact
  (`skills/helix/SKILL.md`), but no roadmap type exists in the catalog.
- **Evidence**: a consulting engagement running HELIX on a sprint cadence
  had to invent all three documents outside HELIX governance — a sprint
  plan (goal, Must/Like/Nice-tiered outcomes, owners, dates, task tables),
  a client-facing deliverables cut of the same commitment, and a
  sprint-review record — while its product documents mapped cleanly to
  existing types.
- **Pain points**:
  1. Teams on a human cadence author iteration documents ungoverned — no
     template, no quality checks, no graph edges, no drift detection.
  2. The skill/catalog inconsistency ("roadmap brief" named but untyped)
     means a roadmap request cannot bind a template and fails §Catalog
     Resolution's authoring contract.
  3. Without a governed plan, runtime work items and human boards have no
     single membership source, so scope drifts silently between surfaces.

## Requirements

### Functional Requirements by Area

**Catalog types**

- **FR-1**: A `roadmap` type in `01-frame` that sequences framed outcomes
  across iterations/horizons with dependencies, confidence, and ordering
  rationale. It commits sequence, not owners or dates.
- **FR-2**: An `iteration-plan` type in `06-iterate` that commits one
  time-box: falsifiable goal, exactly one Good, one Better, and one Best
  outcome per participating workstream — Good is the protected floor
  (never traded; at-risk means escalation, and once committed its ID,
  text, and acceptance evidence are immutable for the iteration), Best
  drops first under pressure, then Better. More outcomes per workstream is
  confusing; fewer breaks the flex model, so a workstream that cannot fill
  all three tiers is not participating this iteration, never partially
  committed (participation is per-iteration; registry active/closed status
  lives in the roadmap). Each outcome carries an owner, acceptance
  evidence, and at least one task. Outcome and task IDs are unique within
  the plan and fully qualified as `<iteration-id>.<id>` when cited
  elsewhere.
- **FR-2a (membership direction)**: the plan owns commitment membership —
  task rows select existing work items by ID (Work Item column), and rows
  without one are the source from which the runtime creates items,
  back-referencing each new ID in the plan. The tracker owns live state;
  the plan's Status column is planning-time state only.
  `workflows/conventions.md` §HELIX Integration states the same contract.
- **FR-3**: A `status-report` type in `06-iterate` that records outcome
  status against the plan's IDs with evidence per claim, trades against
  the plan's trade rules, blockers, and decisions needed.

**Graph edges**

- **FR-4**: Edges close the loop: `prd` → `roadmap` → `iteration-plan` →
  `status-report` → `improvement-backlog` → `roadmap` (revision), plus
  `improvement-backlog` → `iteration-plan` and `metrics-dashboard` →
  `status-report`. The graph generator projects only
  `relationships.informs:` into edges, so the loop is declared via the new
  types' `informs` blocks plus additive `informs` entries in the `prd`,
  `improvement-backlog`, and `metrics-dashboard` metas, then regenerated
  into `workflows/graph.yml`.

**Routing**

- **FR-5**: The routing skill gains an `iterate` route ("plan or report a
  human iteration") and a workflow contract that enforces the
  plan-owns-membership invariant: the plan decides which outcomes and
  tasks exist; the runtime tracker owns live status. The skill's activity
  table lists the three new types.

**Workstreams**

- **FR-6**: Iterations carry a workstream concept. The roadmap is the
  registry of record: each workstream gets a stable shorthand alias
  `WS-<n>` (assigned sequentially, never reused or renumbered — a closed
  workstream keeps its alias), a name, a scope line, and an owner.
  Iteration plans and status reports reference workstreams by alias and
  never mint new ones; a roadmap-less plan (single-workstream skip case)
  has one implicit workstream and uses no aliases — a second workstream
  requires the registry first. Aliases are unique within one flow
  instance. Runtime work items preserve the alias — as a label where the
  runtime supports labels (e.g. `ws:WS-1`, prefixed with the flow instance
  when several flows share one store), otherwise in the item's title or
  reference field — which is how workstreams are represented in the
  runtime's work-item store (the beads database on DDx) without HELIX
  shipping tracker schema.

### Acceptance Criteria

- **AC-1**: Given a request "cut the sprint plan" or "write the sprint
  status report", the skill routes to `iterate` and binds the matching
  template from the catalog.
- **AC-2**: `scripts/generate_graph.py` regenerates `workflows/graph.yml`
  with the three nodes and loop edges; `tests/validate-skills.sh` passes.
- **AC-3**: Each new type's `template.md` headings satisfy its own
  `meta.yml` `required_sections`.
- **AC-4**: The `iteration-plan` template states, in the Tasks section,
  that task IDs are stable and that the runtime tracker owns live status.
- **AC-5**: The roadmap template carries a Workstreams registry section
  with the `WS-<n>` alias rules; the iteration-plan template references
  aliases in outcomes and task groups and names the `ws:WS-<n>` work-item
  label convention; a blocking quality check on each side enforces
  registry-only aliases.
- **AC-6**: A blocking iteration-plan quality check rejects a plan where
  an active workstream has missing or surplus Good/Better/Best tiers;
  the template shows the inactive-workstream escape hatch.

### Non-Functional Requirements

- **NFR-1**: All three types stay runtime-neutral — no tracker commands,
  no board-tool references in template or prompt bodies (PRD R-4).
- **NFR-2**: HELIX still ships no tracker: the types govern documents;
  work-item surfaces remain runtime property (PRD out-of-scope list).

## Edge Cases and Error Handling

- **Iteration plan requested with no roadmap or backlog**: the graph
  consultation surfaces them as non-required prerequisites ("consider also
  drafting"); authoring proceeds — small teams may start at the plan. A
  roadmap-less plan has one implicit workstream and uses no aliases.
- **Status report claims Done without evidence**: blocking quality check
  (claims-vs-reality); the claim is a phantom until evidence is cited.
- **Scope added directly to a runtime board/tracker**: the contract routes
  it back through the iteration plan; hand-added tracker items never
  silently widen the plan.
- **Mid-iteration re-tiering**: an `evolve` pass against the iteration
  plan, recorded in the next status report's Changes and Trades — Better
  and Best only. A committed Good is immutable; a Good that becomes
  impossible is an escalation recorded in the status report with its
  decider named, never an edit or re-tier.

## Success Metrics

- A pilot engagement's next sprint documents author from these templates
  with no structural sections invented outside them.
- Zero skill/catalog naming inconsistencies: every artifact named in the
  skill's engage list binds a catalog type.

## Constraints and Assumptions

- **Anti-ceremony guard**: each type's prompt and the skill's `iterate`
  contract carry an explicit skip test — these artifacts are authored only
  when there is coordination or an audience (multiple workstreams, multiple
  owners, a review). Authoring them because the types exist is process as
  deliverable, and the contract says so.
- `implementation-plan` keeps its lane: design-derived build slices for a
  feature. The iteration plan may reference implementation plans but never
  replaces them.
- **Lifecycle**: the 06-iterate entry gate (deployed, monitored system)
  gates the metric-loop artifacts only; the human cadence pair is exempt —
  a project's first iteration plan precedes any deployment. Recorded in
  the activity's GATE.yaml scope note and README "Human cadence pair".
- **Ownership boundary**: `metrics-dashboard` keeps measurement
  interpretation; `status-report` owns commitment accounting against the
  plan and cites dashboard readings rather than re-deriving them
  (06-iterate README "Human cadence pair").
- Examples use the DepositMatch universe for consistency with existing
  catalog examples.

## Out of Scope

- Any board/tracker tooling, generators, or sync code (runtime property).
- First-class workstream objects in a runtime's work-item schema (e.g. a
  DDx beads-database entity with `ws` commands) — runtime-repo work; HELIX
  specifies only the `WS-<n>` alias standard and the `ws:WS-<n>` label
  convention.
- A retro/postmortem type — revisit when evidence shows the status
  report's review-kind section is insufficient.
- Per-runtime board conventions (markdown kanban, GitHub Projects) —
  install-guide material for runtimes that want it, not catalog content.

## Dependencies

- `helix.prd` — R-1 (artifact catalog), R-4 (runtime-neutral), out-of-scope
  list (no tracker).

## Relationships

- Extends activity `06-iterate` (types) and `01-frame` (roadmap).
- Closes the loop with `improvement-backlog` (existing).
