---
title: "Observability (OpenTelemetry)"
slug: o11y-otel
generated: true
aliases:
  - /reference/glossary/concerns/o11y-otel
---

**Category:** Quality Attributes · **Areas:** api, backend, infra

## Description

## Category
observability

## Areas
api, backend, infra

## Components

- **Standard**: OpenTelemetry (traces, metrics, logs)
- **Traces**: Distributed tracing with correlation IDs
- **Metrics**: RED metrics (Rate, Errors, Duration) for all services
- **Logs**: Structured JSON logging with trace context

## Constraints

- All HTTP/gRPC endpoints must emit latency and error metrics
- All cross-service calls must propagate trace context
- Logs must be structured JSON with correlation IDs
- No `console.log` / `print` for operational logging

## When to use

Any project with backend services, APIs, or distributed systems. Essential
for production debugging, performance monitoring, and incident response.

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- ADR: OpenTelemetry (traces/metrics/logs) as the observability standard
- TD: RED metrics on endpoints, trace-context propagation, structured JSON logs with correlation IDs

## Practices by activity

Agents working in any of these activities inherit the practices below through runtime work context, such as a DDx bead context digest.

## Requirements (Frame activity)

- All services must define SLOs for availability and latency
- Incident response requires structured logs and traces

## Design

- Use OpenTelemetry SDK for instrumentation (not vendor-specific SDKs)
- All cross-service calls propagate W3C Trace Context headers
- Define span naming conventions per service type
- Metric names follow OpenTelemetry semantic conventions

## Implementation

- Structured JSON logging — no unstructured text logs in production
- Every HTTP handler: request ID, trace ID, duration, status code
- Every database query: duration, table, operation type
- Every external API call: duration, endpoint, status code
- Error logs include stack trace and request context
- Use log levels consistently: ERROR (actionable), WARN (degraded),
  INFO (business events), DEBUG (development only)

## Testing

- Verify trace propagation in integration tests
- Verify structured log format in unit tests
- Load test with tracing enabled to validate overhead < 5%
- Alert on missing trace context in production logs

## Deployment

- Configure OTEL collector as a sidecar or daemonset
- Export to the project's observability backend (Grafana, Datadog, etc.)
- Set sampling rate appropriate to traffic volume
