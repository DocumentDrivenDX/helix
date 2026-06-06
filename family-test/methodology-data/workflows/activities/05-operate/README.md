# 05-operate

Purpose: production rollout + ongoing operation. Deploy folds in here
because data pipelines run continuously — there is no ship-and-forget
moment. Monitoring, incident response, freshness/cost tuning.

Inputs: `implementation-plan` (informs, required), `lineage-spec`
(informs), `data-quality-tests` (informs), `data-architecture`
(informs for metrics-dashboard).

Outputs:
- `runbook` (exit-gate): named failure modes (freshness violation,
  schema drift, dead-letter overflow, cost spike), per-mode response,
  on-call escalation.
- `monitoring-setup`: freshness alarms, quality-test alerting,
  lineage-emitter health, cost dashboards.
- `metrics-dashboard`: gold-tier metrics surfaced to consumers; layout,
  refresh cadence, audience.

Exit gate: `operate-validation` — runbook covers every
`escalation_when_failed` trigger named in expectations; monitoring
alarms exist for every freshness_sla declared in contracts;
metrics-dashboard exists for every consumer with read_pattern
`interactive`.

Cross-flow: monitoring-setup may need `helix-infra:change-intent` (new
alerts, new DNS for dashboards); metrics-dashboard may inherit visual
language from `helix-web:design-system`. Surface both per §8 cross-flow
awareness.
