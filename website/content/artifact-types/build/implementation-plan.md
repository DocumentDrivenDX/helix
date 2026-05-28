---
title: "Implementation Plan"
linkTitle: "Implementation Plan"
slug: implementation-plan
activity: "Build"
artifactRole: "core"
weight: 10
generated: true
---

## Purpose

The Implementation Plan is the **build sequencing and execution-readiness
artifact**. Its unique job is to translate approved story, technical design, and
test-plan context into bounded implementation slices with dependencies,
validation gates, and closeout evidence.

It is not the tracker. The runtime owns issue state and execution. This artifact
defines the intended build shape so the runtime's work items can execute
without inventing scope, ordering, or validation rules.

## Example

<details open>
<summary>Show a worked example of this artifact</summary>

``````markdown
---
ddx:
  id: example.implementation-plan.depositmatch
  depends_on:
    - example.technical-design.depositmatch.upload-csv
    - example.story-test-plan.depositmatch.upload-csv
  review:
    self_hash: c470ce1b656f474335d2b2ec376a3e41e3389d5b83c7fcc1b350890b50a42d7c
    deps:
      example.story-test-plan.depositmatch.upload-csv: 20aed2c4e248a67b448b0528b49ae9b2724d5045879ddcda655ad220d1c276ed
      example.technical-design.depositmatch.upload-csv: 064c51468da1d444da9c6f65d6c2502487724ac315fa3e6c50f9bbeffd3d69b9
    reviewed_at: "2026-05-26T02:56:15Z"
---

# Build Plan

## Scope

Build the US-001 upload slice for DepositMatch CSV import. This plan covers
database migration, upload service, API route, UI upload flow, and story test
handoff. It does not cover column mapping, row validation, import confirmation,
or match generation.

**Governing Artifacts**:

- `example.user-story.depositmatch.upload-csv`
- `example.technical-design.depositmatch.upload-csv`
- `example.story-test-plan.depositmatch.upload-csv`
- `example.contract.depositmatch.import-session-api`
- `example.solution-design.depositmatch.csv-import`

## Shared Constraints

- API-001 is normative.
- Failing tests from STP-001 must exist before behavior implementation.
- Raw CSV row values must not appear in logs.
- Storage failure must not leave partial session metadata.
- Build slices should stay small enough for review and rollback.

## Implementation Slices

| Slice | Story / Area | Governing Artifacts | Depends On | Validation Gate | Notes |
|-------|---------------|---------------------|------------|-----------------|-------|
| B-001 | Database migration and repository | TD-001, STP-001 | None | `pnpm test -- importSessionRepository` | Establish persistence contract first |
| B-002 | Source-file storage adapter and upload service tests | TD-001, STP-001 | B-001 | `pnpm test -- importUploadService` | Add red tests before service implementation |
| B-003 | API route and contract tests | API-001, TD-001, STP-001 | B-001, B-002 | `pnpm test -- importSessions` | Proves success and problem-details errors |
| B-004 | React upload UI and component tests | US-001, TD-001, STP-001 | B-003 | `pnpm test -- ImportSessionUpload` | Uses API response `next.href` directly |
| B-005 | P0 E2E smoke and closeout | US-001, STP-001 | B-004 | `pnpm test:e2e -- upload-csv` | Final story evidence |

## Issue Decomposition

Story-level work is tracked as work items in the runtime's work-item store.

**Per-issue requirements**:

- Labels: `helix`, `activity:build`, `kind:build`, `story:US-001`
- References: US-001, TD-001, STP-001, API-001, this build plan
- `spec-id` pointing at the nearest governing artifact
- Blockers as dependency links

| Story / Area | Goal | Dependencies |
|--------------|------|--------------|
| US-001 / persistence | Create draft session and file metadata persistence | None |
| US-001 / upload service | Store encrypted originals and persist metadata transactionally | persistence |
| US-001 / API | Expose API-001 success and error behavior | upload service |
| US-001 / UI | Let Maya upload files and route to mapping review | API |
| US-001 / E2E | Prove happy path and rejection path in browser | UI |

## Validation Plan

- [ ] Failing tests exist before implementation starts for each slice.
- [ ] B-001 passes repository tests.
- [ ] B-002 passes upload service tests and log-redaction assertions.
- [ ] B-003 passes API-001 contract tests.
- [ ] B-004 passes UI component tests.
- [ ] B-005 passes Playwright upload smoke test.
- [ ] `pnpm test`, `pnpm test:coverage`, and `pnpm test:e2e -- upload-csv`
  pass before closing the story.

## Risks and Rollbacks

| Risk | Impact | Response | Rollback |
|------|--------|----------|----------|
| Multipart upload implementation buffers files in memory | H | Add memory regression test and stream files to storage | Revert B-002/B-003 before UI slice lands |
| API/UI validation drift | M | API contract tests remain authoritative; UI validation stays advisory | Disable `csvImportV1` UI entry point |
| Storage failure leaves partial data | H | Wrap metadata commit after storage success; test failure injection | Revert service slice and drop draft sessions created in test only |

## Exit Criteria

- [ ] Build issue set is defined with sequence and dependencies.
- [ ] Shared constraints are documented.
- [ ] Verification expectations are explicit.
- [ ] Runtime issues can be created from this plan without inventing scope.

## Review Checklist

- [ ] Governing artifacts are listed and exist on disk
- [ ] Shared constraints trace back to requirements, design, or architecture
- [ ] Build sequence has a justified ordering
- [ ] Dependencies between build steps are explicit
- [ ] Each story/area references its governing artifacts
- [ ] Issue decomposition follows tracker conventions
- [ ] Quality gates are specific and enforceable
- [ ] Risks have concrete responses
- [ ] Plan is consistent with governing test plan and technical designs
``````

</details>

## Reference

<table class="helix-reference-table">
<tbody>
<tr><th>Activity</th><td><a href="/reference/glossary/activities/"><strong>Build</strong></a> — Implement against the specs and tests. Capture the implementation plan that scopes the work.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/04-build/implementation-plan.md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Informs</th><td><a href="/artifact-types/deploy/release-notes/">Release Notes</a><br><a href="/artifact-types/deploy/deployment-checklist/">Deployment Checklist</a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Build Plan Generation Prompt

Create the canonical build plan for the Build activity. Keep it short, but preserve the sequencing, issue boundaries, and verification rules needed to execute implementation against the test plan and technical designs.

## Purpose

The Implementation Plan is the **build sequencing and execution-readiness
artifact**. Its unique job is to translate approved story, technical design, and
test-plan context into bounded implementation slices with dependencies,
validation gates, and closeout evidence.

It is not the tracker. The runtime owns issue state and execution. This artifact
defines the intended build shape so the runtime&#x27;s work items can execute
without inventing scope, ordering, or validation rules.

## Reference Anchors

Use this local resource summary as grounding:

- `docs/resources/google-small-cls.md` grounds small, reviewable,
  rollback-friendly implementation slices with related tests.

## Active Concerns

For each concern selected in `docs/helix/01-frame/concerns.md`, apply its declared
`## Artifact Impact` (from `workflows/concerns/&lt;name&gt;/concern.md`) to THIS build plan — realize the
IMPLEMENTATION_PLAN-level obligations it names (relational-data-modeling -&gt; migration steps; resilience -&gt; guard wiring; usage-metering -&gt; metering wired on the real path). A selected concern whose Artifact Impact names IMPLEMENTATION_PLAN
but leaves no trace here is drift (reconcile-alignment Concern-&gt;Artifact Realization check).

## Storage Location

`docs/helix/04-build/implementation-plan.md`

## Required Inputs

- `docs/helix/03-test/test-plan.md` and `docs/helix/03-test/test-plans/TP-*.md`
- `docs/helix/02-design/technical-designs/TD-*.md`
- project-level design constraints

## Include

- scope and governing artifacts
- build order and dependencies
- issue decomposition rules
- quality gates and closeout criteria
- risks that should refine upstream artifacts

## Boundary Test

| If you are writing... | Put it in... |
|---|---|
| Product or feature behavior changes | PRD / Feature Specification / User Story |
| Design or interface decisions | Solution Design / Technical Design / Contract / ADR |
| Exact story tests and fixtures | Story Test Plan |
| Build slice order, dependencies, and validation gates | Implementation Plan |
| Assignee, live status, claim, execution logs | runtime work item or issue |

## Template

`workflows/activities/04-build/artifacts/implementation-plan/template.md`
For tracker conventions see the runtime&#x27;s install guide (DDx:
`docs/install/ddx.md`).</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---
ddx:
  id: implementation-plan
---

# Build Plan

## Scope

**Governing Artifacts**:
- [docs/helix/01-frame/...]
- [docs/helix/02-design/...]
- [docs/helix/03-test/...]

## Shared Constraints

- [Constraint from requirements, design, architecture, or security]

## Implementation Slices

| Slice | Story / Area | Governing Artifacts | Depends On | Validation Gate | Notes |
|-------|---------------|---------------------|------------|-----------------|-------|
| [B-001] | [US-XXX or area] | [TP/TD refs] | None | [Command/evidence] | [Why first] |
| [B-002] | [US-XXX or area] | [TP/TD refs] | [Dependency] | [Command/evidence] | [Why next] |

## Issue Decomposition

Story-level work is tracked as work items in the runtime&#x27;s work-item store.

**Per-issue requirements**:
- Labels: `helix`, `activity:build`, `kind:build`, `story:US-{story-id}`
- References: user story, technical design, story test plan, this build plan
- `spec-id` pointing at the nearest governing artifact
- Blockers as dependency links

| Story / Area | Goal | Dependencies |
|--------------|------|--------------|
| [US-XXX] | [Outcome] | [Deps] |

## Validation Plan

- [ ] Failing tests exist before implementation starts
- [ ] All required tests pass before closing a build issue
- [ ] Behavior changes update canonical documents
- [ ] Code review is complete before activity exit

## Risks and Rollbacks

| Risk | Impact | Response | Rollback |
|------|--------|----------|----------|
| [Risk] | [H/M/L] | [Action] | [How to reverse or disable] |

## Exit Criteria

- [ ] Build issue set is defined with sequence and dependencies
- [ ] Shared constraints are documented
- [ ] Verification expectations are explicit
- [ ] Runtime issues can be created from this plan without inventing scope

## Review Checklist

Use this checklist when reviewing an implementation plan:

- [ ] Governing artifacts are listed and exist on disk
- [ ] Shared constraints trace back to requirements, design, or architecture
- [ ] Build sequence has a justified ordering — not just arbitrary
- [ ] Dependencies between build steps are explicit
- [ ] Each story/area references its governing artifacts (TP, TD)
- [ ] Issue decomposition follows tracker conventions (labels, spec-id, deps)
- [ ] Quality gates are specific and enforceable, not aspirational
- [ ] Risks have concrete responses (&quot;we do X&quot;), not vague strategies
- [ ] Plan is consistent with governing test plan and technical designs</code></pre></details></td></tr>
</tbody>
</table>
