---
ddx:
  id: helix.workflow.reference
  depends_on:
    - helix.workflow
  review:
    self_hash: f3d64df6fcff492e40828af0363a9db3efaddb5b499ba8373df8b67435b933f7
    deps:
      helix.workflow: 1b6caaf3ebc6950bc4fff314e09bc0ee1b71deaa9223a4a70a13f399291ad98c
    reviewed_at: "2026-05-26T03:19:52Z"
---
# HELIX Quick Reference Card

This reference summarizes the runtime-neutral HELIX methodology. Runtime
commands and runtime-specific queue guidance live in each runtime's install
guide; for DDx-specific commands, see [docs/install/ddx.md](../docs/install/ddx.md).

## Canonical Methodology Docs

- [README.md](README.md): high-level model, artifact authority hierarchy,
  runtime boundary, and alignment methodology
- `activities/*/artifacts/`: canonical artifact-type catalog, prompts, templates,
  metadata, and examples
- [reconcile-alignment.md](actions/reconcile-alignment.md): top-down review
- [backfill-helix-docs.md](actions/backfill-helix-docs.md): conservative
  reconstruction
- [plan.md](actions/plan.md): iterative design document creation
- [polish.md](actions/polish.md): issue or work-item refinement before
  implementation
- [fresh-eyes-review.md](actions/fresh-eyes-review.md): post-implementation
  review
- [experiment.md](actions/experiment.md): metric-driven optimization iteration
- [metric-definition.yaml](templates/metric-definition.yaml): shared metric
  definitions

## Activity Summary

| Activity | Primary Output | Main Location |
|---|---|---|
| Optional `00-discover` | vision and opportunity framing | `docs/helix/00-discover/` |
| `01-frame` | requirements and stories | `docs/helix/01-frame/` |
| `02-design` | architecture and design contracts | `docs/helix/02-design/` |
| `03-test` | test plans and failing tests | `docs/helix/03-test/`, `tests/` |
| `04-build` | implementation guidance and evidence | `docs/helix/04-build/` |
| `05-deploy` | rollout, monitoring, and recovery evidence | `docs/helix/05-deploy/` |
| `06-iterate` | backlog, reports, metrics, and follow-up planning | `docs/helix/06-iterate/` |

## Authority Hierarchy

1. Product Vision
2. Product Requirements
3. Feature Specs / User Stories
4. Architecture / ADRs
5. Solution / Technical Designs
6. Test Plans / Tests
7. Implementation Plans
8. Source Code / Build Artifacts

## Methodology Actions

Use these as capability names regardless of runtime:

- **Intake**: turn sparse user intent into governed artifact updates or bounded
  work items.
- **Frame**: establish product direction, requirements, principles, and stories.
- **Design**: create architecture, decisions, solution designs, and technical
  designs.
- **Test**: define executable acceptance before implementation is considered
  safe.
- **Build**: perform one bounded implementation slice against governing tests and
  designs.
- **Deploy**: release with rollout, monitoring, and recovery evidence.
- **Review**: inspect completed work for correctness, regressions, and missing
  evidence.
- **Align**: reconcile artifacts top-down when direction or evidence diverges.
- **Backfill**: conservatively reconstruct missing documentation from current
  evidence.
- **Iterate**: record measurements, learning, and follow-up planning.

## Decision Guide

- Starting new work or a large scope: frame the intent, design the governing
  artifacts, refine bounded work items, then execute one slice at a time.
- Starting from sparse user intent: use intake to identify affected artifacts and
  create enough context for safe planning or execution.
- Ready execution work exists: execute the next bounded item in the runtime and
  record evidence against its acceptance criteria.
- Work lacks design authority: return to Frame or Design before implementation.
- Specs changed and open work may be stale: refine the affected work items before
  implementation resumes.
- The next safe work item is unclear: run alignment and record a durable
  alignment review.
- Canonical docs are missing or too incomplete to execute safely: run backfill
  and clearly label reconstructed authority.
- Work is blocked or already in progress: stop, report the blocker, and avoid
  creating duplicate execution tracks.
- After implementing an issue: run fresh-eyes review before continuing broad
  execution.

## Artifact Inputs

Use the prompts and templates under the package's shared workflow root:

- `activities/00-discover/artifacts/`
- `activities/01-frame/artifacts/`
- `activities/02-design/artifacts/`
- `activities/03-test/artifacts/`
- `activities/04-build/artifacts/`
- `activities/05-deploy/artifacts/`
- `activities/06-iterate/artifacts/`

These artifact directories support canonical project docs under `docs/helix/`.
They are the portable HELIX shape; runtime queue mechanics are integration
specific. Concrete install paths for a given runtime are listed in its
integration appendix.

## Skill Package Guidance

Portable HELIX skills should use stable capability names and runtime-neutral
arguments where practical. They do not need to mirror any CLI command unless a
specific runtime integration requires that compatibility surface.

Canonical project package path: `./.agents/skills`
Canonical user install path: `~/.agents/skills`
Claude compatibility path: `~/.claude/skills`

Published `SKILL.md` files must include `name` and `description`; include
`argument-hint` when the skill accepts a trailing scope, selector, issue ID, or
goal. A package must include the shared workflow resources its skills reference.

## Output Reports

- Alignment reviews:
  `docs/helix/06-iterate/alignment-reviews/AR-YYYY-MM-DD[-scope].md`
- Backfill reports:
  `docs/helix/06-iterate/backfill-reports/BF-YYYY-MM-DD[-scope].md`

## Validation

When changing methodology docs, validate the affected artifact and projection
paths required by the repository's contribution rules. Runtime-specific tests
belong to the integration that owns the changed behavior.

## Runtime Integration

The methodology actions above are runtime-neutral capability names. Concrete
commands for executing them — bootstrap, queue control, tracker labeling, and
validation — belong to each runtime's install guide. For DDx-specific commands,
see [docs/install/ddx.md](../docs/install/ddx.md).
