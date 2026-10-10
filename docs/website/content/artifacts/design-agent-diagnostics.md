---
title: "Design: Agent Diagnostics with OpenTelemetry"
slug: design-agent-diagnostics
weight: 390
activity: "Design"
source: "02-design/design-agent-diagnostics.md"
generated: true
---

> **Example from HELIX's own docs.** This generated page comes from `docs/helix/`. Use it to see the method in practice; start with the [artifact-type catalog](/artifact-types/) for reusable templates. Historical plans and reports may describe retired architecture.

> **Source identity** (from `02-design/design-agent-diagnostics.md`):

```yaml
ddx:
  id: helix.design.agent-diagnostics
  authoring:
    home: repo
```

# Design: Agent Diagnostics with OpenTelemetry

## Scope

Implement the operator-approved logging proposal in HELIX's existing
`o11y-otel` concern and catalog. Authority: the operator's implementation
request, project Architecture's portable-content/runtime boundary, and the
existing concern-selection and Contract/SD/TD ownership rules. Astra at ultra
reviewed the proposal in two passes; the revised proposal was approved.
This document records that proposal review, not a review of the implementation.

The product is methodology guidance. Runtime instrumentation, live model
benchmarks and shared production backends belong to adopting projects. HELIX
ships policies, examples and a pilot procedure; it does not claim those projects
have run the pilot or achieved its budgets.

## Requirements Mapping

| Requirement | Design | Proof |
|---|---|---|
| OpenTelemetry governs logs | Explicit mapping, adopted-version policy and OTLP receiver proof | Concern, Contract guidance and pilot |
| Durable files and quiet console | Runner-owned capture; independent filtered projection | Capture and transport guidance |
| Agent retrieval | Bounded filters, source references, loss disclosure and stable continuation | Query example and project Contract obligations |
| Coverage across work areas | `areas: all`, conditional practice sections | Real concern resolver injection tests |
| Safe evidence | Pre-sink privacy, conditional trace IDs, capture failure policy | Catalog alignment and adopting-project negative controls |
| Correct artifact placement | System choices in Architecture/ADR, feature flow in SD, surfaces in Contract, local wiring in TD | Catalog prompts/templates and surface gate |

## Selected Approach

Extend `o11y-otel`; do not introduce a competing telemetry concern, exclusive
slot or profile resolver. Applicability sections are recorded in existing
Concerns Why Active / Key Practices fields. A service applies service signals;
a local CLI applies run diagnostics without inheriting endpoint/SLO rules.
Agent development alone does not require an application SDK for a static site.

OTel's logical model governs local JSONL and export. Projects choose an
established logger with a supported bridge or collector mapping. Trace context
is optional; run/attempt identity is separate. The process emits once and the
chosen route avoids duplicate backend ingestion. Default service transport
remains a platform stream; CLI/MCP diagnostic output is stderr. Local capture
and rotation belong to the runner. A platform-native OTLP path is a documented
project choice subject to the deploy target's capabilities.

Exact schema/query/capture definitions belong in adopting-project Contracts.
The library's mapping is illustrative, not a new universal wire protocol. OTel
specification/semantic-convention/instrumentation versions are pinned by the
adopter, particularly evolving GenAI conventions.

## Component Changes

| Component | Responsibility |
|---|---|
| `workflows/concerns/o11y-otel/` | Semantics, applicability, capture, noise, retrieval, privacy, bounded failure policy |
| `workflows/references/agent-diagnostics.md` | Mapping/retrieval example, tool choices and service/CLI OTel pilot |
| Concerns / Contract / SD / TD catalog | Preserve decisions at the right authority and propagate applicable obligations |
| Story Test Plan / Implementation Plan catalog | Derive receiver/failure tests and sequence evidence before readiness claims |
| Monitoring Setup / Runbook catalog | Operational routes, access/retention, optional context, bounded investigation |
| Security / twelve-factor / Databricks concerns | Align privacy and transport without changing their ownership |
| Frame / handoff / review / alignment procedures | Selection and evidence requirements at their existing gates |
| `tests/test_agent_diagnostics.py` | Resolver, catalog coherence and documented query negative controls |

## Implementation Slices

This is the polished decomposition for direct implementation. Each slice has a
bounded outcome and depends on the preceding contract guidance; no tracker
mutation was requested.

| Slice | Depends On | Outcome | Validation |
|---|---|---|---|
| Concern and examples | None | Replace production-only logging rules; add mapping/query/pilot reference | Query examples execute; applicability reviewed |
| Catalog propagation | Concern | Contract/SD/TD/Test/Build/Deploy guidance, quality checks and examples agree | Artifact schema and surface-leakage gates |
| Transport/privacy alignment | Concern | Repeated stdout-only rules gain CLI/native-OTLP qualification; security details remain safe | Alignment tests and scoped review |
| Regression and package gates | All above | Real CLI/data/UI concern injection and canonical package propagation | `python3 tests/test_agent_diagnostics.py`, `just test`, `git diff --check` |

## Verification and Pilot

HELIX verification checks content, real concern injection, executable retrieval
examples and package/catalog consistency. Adopters separately prove JSONL/logger
mapping through an actual OTel receiver and matching trace, duplicates, outages,
redaction, concurrency and rotation. Run both a service and CLI/CI pilot; measure
agent cause accuracy, cited evidence, time, calls/context and runtime overhead
against agreed baselines. The pilot is defined in the shipped reference.

## Risks and Rollback

- Broad concern scope could over-apply service rules: explicit applicability
  sections and CLI injection coverage guard the boundary.
- File plus SDK ingestion could duplicate logs: declare one canonical route and
  compare emitted/received event identities in the pilot.
- Raw subprocess capture could bypass privacy: default capture requires pre-sink
  controls; unsupported content capture is disabled or restricted opt-in.
- Concurrent writes/rotation could destabilize queries: project Contracts define
  snapshot/cursor semantics and evidence coverage; never claim global ordering.
- Existing artifact instances remain legacy-valid; explicit adoption is required
  before claiming current diagnostic readiness. No auto-selection or migration.
- Roll back this additive methodology change with a normal revert; preserve
  unrelated working-tree changes and execution audit history.
