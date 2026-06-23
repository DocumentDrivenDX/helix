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
