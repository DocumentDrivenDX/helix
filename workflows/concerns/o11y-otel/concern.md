# Concern: Observability (OpenTelemetry)

## Category

observability

## Areas

all

## Boundary

This concern owns operational signal semantics, instrumentation, correlation,
and diagnostic evidence for people and agents. **OpenTelemetry (OTel) is the
governing telemetry model**; local JSON Lines (JSONL) is a serialization that
maps to it, not a second telemetry standard or the OpenTelemetry Protocol (OTLP)
wire format. It is composable and fills no exclusive slot.

- **Language/runtime concerns** choose an established structured logger and
  supported OTel integration. A logger bridge or collector mapping is valid;
  every application need not emit through an OTel logging SDK.
- **`twelve-factor` and deploy targets** own process transport and platform
  capture. The development/CI runner owns local file capture and rotation;
  deployed applications do not manage their own log files.
- **`security-owasp`** owns sensitivity, access, redaction and security audit
  policy. Operational telemetry is best-effort; audit records and
  **`usage-metering`** records need their own governed durability guarantees.
- **`resilience` and `concurrency-model`** decide retries, fallbacks, deadlines,
  cancellation and lease/lock behavior. This concern carries their evidence.

## Components

- **Logs/events**: structured diagnostic messages and named state transitions.
- **Traces**: duration-bound operations with context propagated across boundaries.
- **Metrics**: aggregate rates, errors and duration distributions where relevant.
- **Agent diagnostics**: durable run evidence, a quiet console and bounded,
  authorized retrieval of relevant records with source references.

## Constraints

- Map logs explicitly to the OTel Logs Data Model; pin adopted specification,
  semantic-convention and instrumentation versions in the project Contract.
- Use stable event names and typed attributes with explicit units. Carry service,
  version and environment identity as Resource attributes. Do not parse messages
  to recover fields already known to the emitter.
- Carry trace/span IDs only from valid context. Use separately namespaced
  run/attempt/work-item IDs; never fabricate trace or GenAI conversation IDs.
- Emit an event once and configure independent storage/console projections.
  Verify the ingestion route does not duplicate it in the backend.
- Preserve useful local/CI evidence while keeping default console output to
  readiness, meaningful transitions, actionable warnings and final outcomes.
  Reserve CLI/MCP stdout for results/protocol; diagnostics use stderr.
- Apply allowlists/redaction before **every** sink, including captured subprocess
  output. No secrets, raw prompts, tool payloads or transcripts by default.
- Bound records, queues, retention, query output and shutdown flushing. Disclose
  sampling, suppression and capture/export loss; silence is not proof of success.
- Keep correlation IDs out of metric dimensions and Loki stream labels.

## When to use

Select for backend services/APIs needing operational diagnosis, or a project
developed or operated with agents that execute commands, builds, tests or tools
and need persistent diagnostic evidence. The product need not call a model.
CLI, CI, frontend and data work are eligible; `areas: all` permits propagation
but does not make every practice applicable to every surface.

Record the applicable sections from `practices.md` in the existing Concerns
**Why Active / Key Practices** fields: service signals, agent run diagnostics,
frontend/data boundaries, and/or GenAI operations. These are prose applicability
sections, not a new resolver schema. Endpoint/SLO rules apply only to services;
GenAI rules apply only to actual model/tool invocation. A library can accept
caller-owned instrumentation without owning a backend or collector.

Skip for source-free prose work with no runtime diagnostic surface. Do not add
an SDK or shared logging backend to a static site or library solely because an
agent edits it; the development runner may supply the required evidence.

## Artifact Impact

Selecting this concern requires applicable artifacts to change; an obligation
missing from its owning artifact is drift:

- CONCERNS: applicability evidence and selected practice sections, overrides.
- ARCHITECTURE / ADR: signal ownership, logger/OTel integration and transport
  choices; collector/backend rationale and operational tradeoffs when needed.
- SOLUTION_DESIGN: cross-component signal flow and applicable diagnostics.
- CONTRACT: exact schema/event catalog, OTel mapping and version compatibility;
  capture and query surfaces, correlation, ordering and failure/loss semantics.
- TD: local instrumentation, context propagation and sink wiring referencing
  Contracts; never redefine shared telemetry fields inline.
- TEST_PLAN / STORY_TEST_PLAN: allocate test layers; prove mapping through a real
  OTel receiver, redaction, correlation, bounded retrieval and failure behavior.
- IMPLEMENTATION_PLAN: sequence contract, capture/instrumentation, conformance
  and diagnostic pilot; record evidence before claiming the integration works.
- MONITORING_SETUP: actual collection route, retention/access, sampling/loss,
  query entrypoints and alerts for relevant pipeline failures.
- RUNBOOK: exact bounded retrieval recipes, evidence locations and diagnostic
  escalation with prerequisites and stop conditions.
