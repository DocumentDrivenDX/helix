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
defines the intended build shape so the runtime can execute the plan directly
without inventing scope, ordering, or validation rules. Work items are optional;
follow `workflows/references/work-item-first.md`. Readiness alone does not
authorize implementation.

## Example

<details open>
<summary>Show a worked example of this artifact</summary>

``````markdown
---
ddx:
  id: example.implementation-plan.depositmatch
  authoring:
    home: repo
  depends_on:
    - example.technical-design.depositmatch.upload-csv
    - example.story-test-plan.depositmatch.upload-csv
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

## Execution Contract

The user authorizes implementation separately from plan readiness. Execute the
ordered slices through their verification gates and the goal's exit criteria.
A slice is a reviewable change, not necessarily a separately scheduled issue.
Stay within Scope; stop for authority conflicts, missing authorization, or
concrete blockers requiring a decision. Ordinary debugging remains in scope.

## Continuation Evidence

On interruption, record plan revision, completed slice IDs with evidence,
remaining slices, decisions, blockers, and the next action alongside this plan.
On resume, reconcile the record with the diff and tests before continuing.
When tracking is explicitly selected, its store owns claims and live status.

## Optional Tracking

Use work items only when requested or required by the active execution contract.
Prefer one item for this goal; split for independent scheduling, ownership,
parallel execution, or deferred work. Follow the selected runtime's acceptance,
dependency, audit, and closure requirements. Do not discover tracker binaries.

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

Plan readiness requires defined scope, ordered slices, shared constraints, and
explicit verification gates. These planning checks do not establish completion.
Execution is complete only when:

- [ ] US-001 upload succeeds end to end; governed rejection and storage-failure paths pass STP-001 tests.
- [ ] Every required slice validation gate and the final integration gate pass.
- [ ] Acceptance evidence is recorded; no required step or material blocker remains.
- [ ] Required canonical documentation and review are complete.
- [ ] Any explicitly selected runtime's audit and closure requirements are met.

## Diagnostic Evidence Sequencing

A diagnostic adoption slice requires its own story, Contract and Story Test Plan
before implementation. Sequence logger/capture wiring, actual OTel receiver and
privacy/failure proof, then service/CLI agent diagnosis. Runtime closeout records
run/attempt, safe manifest/receiver evidence, verification outcome and capture
limits. This example defines sequencing and does not report pilot completion.
``````

</details>

## Reference

<table class="helix-reference-table">
<tbody>
<tr><th>Activity</th><td><a href="../../../reference/glossary/activities/"><strong>Build</strong></a> — Implement against the specs and tests. Capture the implementation plan that scopes the work.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/04-build/implementation-plan.md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Informs</th><td><a href="../../../artifact-types/deploy/release-notes/">Release Notes</a><br><a href="../../../artifact-types/deploy/deployment-checklist/">Deployment Checklist</a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Build Plan Generation Prompt&#10;&#10;Create the canonical build plan for the Build activity. Keep it short, but preserve the sequencing, issue boundaries, and verification rules needed to execute implementation against the test plan and technical designs.&#10;&#10;## Purpose&#10;&#10;The Implementation Plan is the **build sequencing and execution-readiness&#10;artifact**. Its unique job is to translate approved story, technical design, and&#10;test-plan context into bounded implementation slices with dependencies,&#10;validation gates, and closeout evidence.&#10;&#10;It is not the tracker. The runtime owns issue state and execution. This artifact&#10;defines the intended build shape so the runtime can execute the plan directly&#10;without inventing scope, ordering, or validation rules. Work items are optional;&#10;follow `workflows/references/work-item-first.md`. Readiness alone does not&#10;authorize implementation.&#10;&#10;## Reference Anchors&#10;&#10;Use this local resource summary as grounding:&#10;&#10;- `docs/resources/google-small-cls.md` grounds small, reviewable,&#10;  rollback-friendly implementation slices with related tests.&#10;&#10;## Active Concerns&#10;&#10;For each concern selected in `docs/helix/01-frame/concerns.md`, apply its declared&#10;`## Artifact Impact` (from `workflows/concerns/&lt;name&gt;/concern.md`) to THIS build plan — realize the&#10;IMPLEMENTATION_PLAN-level obligations it names (relational-data-modeling -&gt; migration steps; resilience -&gt; guard wiring; usage-metering -&gt; metering wired on the real path). A selected concern whose Artifact Impact names IMPLEMENTATION_PLAN&#10;but leaves no trace here is drift (reconcile-alignment Concern-&gt;Artifact Realization check).&#10;&#10;## Storage Location&#10;&#10;`docs/helix/04-build/implementation-plan.md`&#10;&#10;## Required Inputs&#10;&#10;- `docs/helix/03-test/test-plan.md` and `docs/helix/03-test/test-plans/TP-*.md`&#10;- `docs/helix/02-design/technical-designs/TD-*.md`&#10;- project-level design constraints&#10;&#10;## Include&#10;&#10;- scope and governing artifacts&#10;- build order and dependencies&#10;- execution authorization, completion conditions, and stop conditions&#10;- concise continuation evidence and optional tracking rules&#10;- quality gates and closeout criteria&#10;- risks that should refine upstream artifacts&#10;&#10;## Boundary Test&#10;&#10;| If you are writing... | Put it in... |&#10;|---|---|&#10;| Product or feature behavior changes | PRD / Feature Specification / User Story |&#10;| Design or interface decisions | Solution Design / Technical Design / Contract / ADR |&#10;| Exact story tests and fixtures | Story Test Plan |&#10;| Build slice order, dependencies, and validation gates | Implementation Plan |&#10;| Assignee, live status, claim, execution logs | runtime work item or issue |&#10;&#10;## Template&#10;&#10;`workflows/activities/04-build/artifacts/implementation-plan/template.md`&#10;For tracker conventions see the runtime&#x27;s install guide.&#10;&#10;## Boundary Gate Sequencing&#10;&#10;For source projects, apply `modularity-and-encapsulation`: sequence baseline&#10;adoption, boundary mapping and the actual project checker before dependent feature&#10;work. Name the single command used locally, in pre-commit, and CI, plus allowed&#10;and forbidden import negative controls. Include supported cycle/private-access&#10;checks and named semantic review obligations. Bounded adoption work may proceed&#10;before the gate exists; feature work may not. Inventory existing violations&#10;individually with owners and remediation; do not enlarge baselines to hide new debt.&#10;&#10;## Diagnostic Evidence Sequencing&#10;&#10;When `o11y-otel` applies, follow the template&#x27;s diagnostic sequencing and include&#10;its TEST_PLAN obligations in the project Test Plan and exact tests in Story Test&#10;Plans. Sequence Contract adoption, instrumentation/capture, actual OTel receiver&#10;proof and diagnostic pilot. Runtime work items carry safe evidence references,&#10;verification outcome and coverage/loss limits; do not dump whole logs into them.</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---&#10;ddx:&#10;  id: implementation-plan&#10;  authoring:&#10;    home: repo&#10;---&#10;&#10;# Build Plan&#10;&#10;## Scope&#10;&#10;**Governing Artifacts**:&#10;- [docs/helix/01-frame/...]&#10;- [docs/helix/02-design/...]&#10;- [docs/helix/03-test/...]&#10;&#10;## Shared Constraints&#10;&#10;- [Constraint from requirements, design, architecture, or security]&#10;&#10;## Implementation Slices&#10;&#10;For handwritten source, put boundary adoption/map and checker scaffolding before&#10;feature slices that depend on them. Name the project-local boundary command and&#10;its local/pre-commit/CI wiring; identify allowed/forbidden import controls.&#10;&#10;| Slice | Story / Area | Governing Artifacts | Depends On | Validation Gate | Notes |&#10;|-------|---------------|---------------------|------------|-----------------|-------|&#10;| [B-001] | [US-XXX or area] | [TP/TD refs] | None | [Command/evidence] | [Why first] |&#10;| [B-002] | [US-XXX or area] | [TP/TD refs] | [Dependency] | [Command/evidence] | [Why next] |&#10;&#10;## Execution Contract&#10;&#10;The user authorizes implementation separately from plan readiness. Execute the&#10;ordered slices through their verification gates and the goal&#x27;s exit criteria.&#10;A slice is a reviewable change, not necessarily a separately scheduled issue.&#10;Stay within Scope; stop for authority conflicts, missing authorization, or&#10;concrete blockers requiring a decision. Ordinary debugging remains in scope.&#10;&#10;## Continuation Evidence&#10;&#10;On interruption, record plan revision, completed slice IDs with evidence,&#10;remaining slices, decisions, blockers, and the next action alongside this plan.&#10;On resume, reconcile the record with the diff and tests before continuing.&#10;When tracking is explicitly selected, its store owns claims and live status.&#10;&#10;## Optional Tracking&#10;&#10;Use work items only when requested or required by the active execution contract.&#10;Prefer one item for this goal; split for independent scheduling, ownership,&#10;parallel execution, or deferred work. Follow the selected runtime&#x27;s acceptance,&#10;dependency, audit, and closure requirements. Do not discover tracker binaries.&#10;&#10;## Validation Plan&#10;&#10;- [ ] Failing tests exist before implementation starts&#10;- [ ] All required tests pass before reporting goal completion&#10;- [ ] Behavior changes update canonical documents&#10;- [ ] Code review is complete before activity exit&#10;&#10;## Risks and Rollbacks&#10;&#10;| Risk | Impact | Response | Rollback |&#10;|------|--------|----------|----------|&#10;| [Risk] | [H/M/L] | [Action] | [How to reverse or disable] |&#10;&#10;## Exit Criteria&#10;&#10;Plan readiness requires defined scope, ordered slices, shared constraints, and&#10;explicit verification gates. These planning checks do not establish completion.&#10;Execution is complete only when:&#10;&#10;- [ ] [Observable implemented goal and its acceptance evidence]&#10;- [ ] Every required slice validation gate and the final integration gate pass.&#10;- [ ] Acceptance evidence is recorded; no required step or material blocker remains.&#10;- [ ] Required canonical documentation and review are complete.&#10;- [ ] Any explicitly selected runtime&#x27;s audit and closure requirements are met.&#10;&#10;## Diagnostic Evidence Sequencing (when applicable)&#10;&#10;For selected `o11y-otel` practices, sequence Contracts before dependent wiring,&#10;then real receiver/conformance and failure proof before the service/CLI diagnostic&#10;pilot. Each closeout names run/attempt, safe evidence location, verification&#10;outcome and capture limits. A quiet console is not verification evidence.</code></pre></details></td></tr>
</tbody>
</table>
