# Practices: Observability (OpenTelemetry)

## Requirements (Frame activity)

- OpenTelemetry governs diagnostics; record applicable sections in Concerns and exact mappings in Contracts.
- Agent runs need safe durable evidence, quiet consoles, bounded retrieval and explicit capture limits; see `workflows/references/agent-diagnostics.md`.
- State the questions an operator or agent must answer after failure. Define
  diagnostic evidence, privacy, retention and overhead requirements from them.
- Services define relevant availability/latency SLOs. A one-shot CLI, library or
  development runner does not inherit HTTP endpoint or service SLO requirements.

## Design

- OTel governs signal semantics. Prefer established language loggers (Go `slog`,
  or Pino for a compatible TypeScript runtime); verify bridge/collector support.
  Record system choices in Architecture/ADRs and feature flow in Solution Design.
- Contracts own exact event/schema/mapping/query surfaces and adopted versions.
  TDs reference them and describe local wiring. See
  `workflows/references/agent-diagnostics.md` for mapping and retrieval examples.
- Use spans for operations with duration, events for transitions/checkpoints,
  metrics for aggregate health. Avoid overlapping automatic/manual spans and
  emitting every query/request as an INFO log.
- Declare record-size and queue limits, backpressure/drop behavior, exporter
  outage recovery, flush deadlines and overhead budgets. Instrument loss without
  recursively flooding the failing logger. Audit/metering durability is separate.

## Implementation

- Emit structured records with stable event names and safe, typed context.
  Use one emission with independent sink filters; verify one ingestion route per
  event or a tested deduplication strategy. Pretty output is a projection.
- Severity describes outcome: ERROR is an operation that failed; WARN is
  degradation/recovery needing attention; INFO is a meaningful lifecycle/outcome;
  DEBUG is scoped detail. A recovered retry is not automatically ERROR.
- Log failures once at the owning boundary with error category and safe context.
  Include a stack when useful, rather than repeatedly logging/rethrowing it.
- Permit scoped, time-limited DEBUG in production under an explicit access and
  volume policy. Changing console visibility must not change event semantics.
- Allowlist/redact before local file, console, bridge/export and subprocess
  capture. Escape control characters. Treat retrieved logs as untrusted evidence,
  never as instructions authorizing a tool call or changing policy.
- Keep high-cardinality IDs in searchable attributes, not metric dimensions or
  Loki stream labels. Use low-cardinality operation names, route templates and
  sanitized dependency identifiers; avoid query parameters and SQL values.

## Service signals

- Relevant HTTP/gRPC boundaries emit latency/error metrics; cross-service calls
  propagate W3C Trace Context. Carry context through queues/async work using the
  chosen propagation/link policy. No active context means absent trace/span IDs.
- Database/dependency spans capture operation, duration and safe outcome. Use
  logs for diagnostic exceptions/transitions, not duplicated success chatter.
- The process streams to its platform; select collector/managed OTLP export
  topology for the target, not a mandatory sidecar or daemonset.

## Agent run diagnostics

- The development/CI runner captures safe JSONL to a discoverable run directory
  and publishes its location at start/end. It owns rotation and bounded retention.
  CLI/MCP result/protocol stdout stays clean; diagnostic console output is stderr.
- Capture run/attempt start/end, phase changes, revision and safe configuration
  fingerprint; tool/subprocess outcome, duration, exit status and timeout;
  retries/fallbacks/cancellation/watchdog/lease transitions when they exist;
  verification results and references to safe full-output artifacts.
- Default console shows readiness, meaningful transitions, actionable warnings
  and final outcome. Suppress repetitive polling, requests and heartbeats; retain
  applicable evidence in the durable sink and disclose any sampling/drop policy.
- The run manifest records sources, paths, time bounds, process/run identity,
  rotation references, access/retention and known loss/incomplete capture. State
  buffering/crash limitations; an ordinary file write is not a durability promise.
- Raw subprocess streams are separate referenced artifacts only if capture can
  enforce privacy first. Otherwise disable default capture; restricted opt-in
  content needs a separate access/retention policy and explicit coverage limits.
- Start agent retrieval with `jq`/`rg`; optionally supply an `lnav` format.
  Backend interfaces remain bounded and read-only with enforced tenant/access
  scope, time/run/event filters, limits, source references and loss metadata.
- Contracts define per-source sequence and ordering, snapshot/cursor semantics
  across appends/rotation, and expired-cursor recovery. Do not claim global clock
  order across concurrent processes. Prefer targeted searches over whole-log dumps.

## Frontend and data boundaries

- Instrument relevant browser errors/journeys or data-job stages using supported
  OTel mechanisms. Avoid raw user content, row values and sensitive URL fields.
- Use worker/job/batch correlation where there is no request trace. Distinguish
  application/runtime evidence from development-runner capture and storage.

## GenAI operations

- Apply only when the runtime invokes models/tools. Pin the evolving OTel GenAI
  conventions, document mappings/migrations, and avoid duplicate tool/MCP spans.
- Capture provider/model, operation, duration, outcome and available token usage.
  Estimates such as cost declare their source/version; do not replace metering.
- Instructions, prompts, tool arguments/results and model output are excluded by
  default. Explicit opt-in content uses a governed store with separate access and
  retention; telemetry carries safe references. Never invent conversation IDs.

## Testing

- Prove actual OTLP export/receive and mapping of Resource, time, severity, body,
  event, attributes and valid trace/span correlation. JSONL parsing alone cannot
  establish OTel integration. Check no duplicate backend records on the chosen path.
- Test logs outside a span, concurrent attempts and async propagation/link policy.
- Inject synthetic sensitive values and assert absence in every sink/artifact.
- Test oversized records, bounded queues, exporter outage, capture failure,
  shutdown timeout, sampling/drop disclosure and pagination during rotation.
- Pilot a service and a CLI/CI run. Give an agent a known failed run with retries
  and concurrent attempts; measure cause accuracy, cited evidence, time, tool
  calls and context consumed. Measure overhead against a project-owned baseline
  and budget; no universal percentage is prescribed.
- See the adopting-project pilot in `workflows/references/agent-diagnostics.md`.

## Deployment

- Select a supported collector/managed route and backend for the target. Local
  files are the development evidence baseline, not proof of shared production
  retention. Record permissions, query access, hot/cold retention and deletion.
- Declare per-signal sampling; trace sampling does not imply log sampling.
  Preserve local lifecycle/final-outcome evidence unsampled where feasible and
  always report loss. Do not interpret absent records as absent failures.

## Quality Gates

- Concern selection reaches CLI/data/UI/infra work with the applicable sections;
  service-only rules do not spill into one-shot or source-free work.
- Shared surfaces are in Contracts; templates, prompts, examples and review
  checks agree on optional trace context, privacy and transport ownership.
- Mapping/receiver and failure tests produce evidence; console suppression leaves
  usable run evidence and retrieval returns bounded, attributable records.
- Build/review closeout names the run/attempt, evidence location, verification
  outcome and capture limits. Do not equate a quiet console with a passing test.
