# 01-contract

Purpose: specify producer→consumer contracts as first-class artifacts
BEFORE design. Schemas, freshness SLAs, evolution policy, PII
classification all pin down here so design can satisfy a known shape.

Inputs: `consumer-inventory` (required), `data-product-brief` (informs),
`source-profile` (informs).

Outputs:
- `data-contract` (exit-gate): producer, consumer(s),
  schema_versioning_policy, semantic_field_definitions, freshness_sla,
  evolution_policy, termination_clauses.
- `data-quality-expectations`: bronze / silver / gold expectations,
  escalation_when_failed, override_policy.
- `governance-classification`: pii_fields, access_tier, retention_policy,
  residency_constraints, audit_log_requirements.

Exit gate: `contract-validation` — at least one contract exists per
named consumer in the inventory; expectations exist for every gold-tier
field referenced by a consumer; governance classification covers every
PII field surfaced in any source-profile.

Cascade: refuse to draft expectations or governance without a contract;
offer to draft the contract first.
