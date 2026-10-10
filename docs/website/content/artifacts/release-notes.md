---
title: "Release Notes — HELIX v0.15.3"
slug: release-notes
weight: 540
activity: "Deploy"
source: "05-deploy/release-notes.md"
generated: true
---

> **Example from HELIX's own docs.** This generated page comes from `docs/helix/`. Use it to see the method in practice; start with the [artifact-type catalog](/artifact-types/) for reusable templates. Historical plans and reports may describe retired architecture.

> **Source identity** (from `05-deploy/release-notes.md`):

```yaml
ddx:
  id: release-notes
  authoring:
    home: repo
  depends_on:
    - deployment-checklist
  review:
    self_hash: fb47a9c6a156682c88a3f34e22cdb968b09f586f711e82b16ab068d2cb85f553
    deps:
      deployment-checklist: 00556985f9bfc7cabe6c1288473bb2935f3fe4a83fb5fcd53918e95bf29e5d21
    reviewed_at: "2026-10-04T03:52:23Z"
```

# Release Notes — HELIX v0.15.3

## v0.15.3 — Plan-Driven Execution

Implementation-ready plans now govern authorized execution through verified
completion. Tracker decomposition is optional; independent ownership, scheduling,
parallel work, and deferred follow-up may still use separate items. Portable
prompts no longer point agents toward the optional DDx adapter or infer tracking
from installed binaries or metadata. Existing artifact metadata remains compatible.

Plan and iteration contracts include continuation evidence for interruption
recovery. Explicit worker contracts retain their claims, audit, and closure rules.
Contract regression checks cover authorization, recovery, and tracker opt-in.

## Release Scope

- Release identifier: `v0.15.2`
- Release date: 2026-10-09
- Previous release: `v0.15.1`
- Scope: OpenTelemetry concern, agent diagnostics guidance, artifact catalog,
  routing mode contracts, generated plugin/Genie bundles and public references.
- Release owner: HELIX maintainer; the release pull request triggers the
  existing auto-tag and publication workflows.

## Audience and Channels

| Audience | Impact | Channel |
|----------|--------|---------|
| HELIX users | Safe persistent diagnostics and quieter consoles | Versioned concern catalog and plugin |
| Runtime integrators | Explicit capture, retrieval and evidence obligations | Mode contracts and diagnostic reference |
| Website readers | Aligned artifact guidance | Public reference website |

## Highlights

- OpenTelemetry governs the existing `o11y-otel` concern across applicable
  service, CLI, CI and agent workflows. Projects own exact schemas and mappings
  in Contracts; valid trace context remains optional and separate from run IDs.
- Agent diagnostics use runner-owned local evidence, quiet console projections,
  pre-sink privacy controls, bounded retrieval and explicit capture-loss state.
- Architecture, design, test, monitoring and runbook guidance assigns diagnostic
  responsibilities and requires real receiver evidence for claimed integrations.

## Required Actions Summary

- Users: update to `v0.15.2`; apply the relevant sections when `o11y-otel` is selected.
- Runtime integrators: preserve safe run/attempt evidence and capture limits in
  execution closeout; implement the project-owned Contract before claiming readiness.
- Operators: choose collection, access and retention policies for the deployment target.

## Changes and Fixes

| Area | Change | Effect |
|------|--------|--------|
| Observability | Expanded OTel concern and diagnostic reference | Local evidence and operational telemetry share explicit semantics |
| Artifact catalog | Conditional diagnostic sections and review criteria | Shared interfaces stay in Contracts; local wiring stays in technical designs |
| Monitoring action | Removed mandatory trace ID and competing field list | Untraced events remain valid and follow the governing mapping |
| Verification | Executable bounded-query examples and alignment regression | Query truncation, source references and malformed-input behavior are checked |
| Deck test runner | Explicit Node test file path | Supported Node runtimes execute the existing test suite |

## Breaking Changes and Required Actions

No installation or artifact-format breaking changes. Existing concern selections
are preserved. Selected practices add evidence obligations according to project
applicability; they do not mandate a new telemetry backend or collector sidecar.

## Migration or Rollback Guidance

1. Update the plugin or bundle to `v0.15.2`.
2. Record applicable diagnostic practices and adopt exact mappings, capture and
   query rules in the project Contract.
3. Run the adopting-project pilot with a real OTel receiver before claiming
   integration readiness; preserve receiver output and measured results.

To roll back the plugin, pin `v0.15.1`. Preserve project-owned diagnostic Contracts
and evidence; changing plugin versions does not remove those decisions.

## Known Issues and Support

- HELIX content tests do not execute an adopting project's OTel integration.
  The documented receiver and agent investigation pilot remains project-owned.
- Metadata quality checks are instructional review criteria, not automated
  semantic validation of a project's diagnostic system.
- GenAI conventions remain evolving and require a pinned revision and migration policy.

Support: open an issue in the HELIX repository.

## References

- Deployment checklist: [deployment-checklist.md](/artifacts/deployment-checklist/)
- Diagnostic design: [design-agent-diagnostics.md](/artifacts/design-agent-diagnostics/)
- Diagnostic reference: `workflows/references/agent-diagnostics.md`
- OTel concern: `workflows/concerns/o11y-otel/`
- Release automation: `.github/workflows/release-tag.yml`
- Version guard: `.github/workflows/release-version-guard.yml`
