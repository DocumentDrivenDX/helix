---
ddx:
  id: GOV-EX-001
  type: governance-classification
  methodology: helix
  library_type_version: 1.0.0
  links: []
---

# Stripe Charge Events Governance Classification

## PII Fields
PII fields are `customer_email`, `billing_address`, and `last4`. `customer_id`
is pseudonymous personal data. Bronze also contains raw webhook metadata that
can include customer-facing receipt references.

## Access Tier
Tier 2 restricted business data for bronze and silver. Gold finance aggregates
without direct identifiers are Tier 1 internal analytics. Access requires SSO,
warehouse role approval from data-platform, and quarterly recertification.

## Retention Policy
Bronze webhook envelopes are retained for 400 days for replay and audit.
Silver charge facts are retained for 7 years for finance reconciliation. Gold
aggregates are retained for 7 years. PII masking applies after 18 months for
interactive customer success views unless an active support case requires it.

## Residency Constraints
Snowflake storage remains in the US production account. EU customer rows must
not be exported to non-approved regional workspaces. Fraud feature exports use
hashed `customer_email` and omit `billing_address` street lines.

## Audit Log Requirements
Log all grants, role changes, table reads from bronze and silver, PII export
queries, and manual backfills. Audit records must include user, role, query
identifier, object name, timestamp, and row count estimate.
