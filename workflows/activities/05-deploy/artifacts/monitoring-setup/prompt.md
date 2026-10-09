# Monitoring Setup Generation Prompt

Create a concise, service-specific monitoring setup for this deployment.

## Reference Anchors

Use these local resources as grounding:

- `docs/resources/google-sre-monitoring-distributed-systems.md` grounds
  operational signals, dashboards, alerting, and the four golden signals.

## Focus
- Include only the metrics, logs, alerts, dashboards, and tracing needed to operate this service.
- Define measurable thresholds, routing, and escalation where they matter.
- Connect health checks and SLOs to rollout safety and rollback decisions.
- Avoid generic observability boilerplate that does not change operator behavior.
- Separate user-impacting alerts from dashboards that are only for diagnosis.

## Completion Criteria
- Core metrics and dashboards are defined.
- Alert thresholds and routing are explicit.
- Logging, tracing, and health-check expectations are clear.
- The setup is specific enough to support deployment and incident response.
- Every page-worthy alert has an operator action or runbook entrypoint.

## OpenTelemetry Diagnostics

For applicable `o11y-otel` practices, complete Logging from the governing
Contract; do not define a competing schema. Make trace context conditional and
run/attempt correlation independent. Record actual collection route, duplication
control, runner evidence/console policy, pre-sink privacy, retention/access and
sampling/loss/outage/flush behavior. Link bounded retrieval and receiver-proof
evidence. Collector topology follows the deploy target. Do not turn operational
logs into authoritative security audit or billing records.
