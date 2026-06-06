---
ddx:
  id: GC-001
  type: governance-classification
  methodology: helix-data
  library_type_version: 1.0.0
  links:
    - {kind: informs, to: DD-001}
    - {kind: informs, to: RB-001}
    - {kind: informs, to: EP-001}
    - {kind: informs, to: DN-001}
---

# Governance Classification: Customer Events

## PII Fields
| Field (silver/gold name) | Source | Classification | Treatment |
|---|---|---|---|
| `customer_token` | sha256(`data.object.customer.id` + salt) | internal | passthrough |
| `data.object.customer.email` (bronze only) | source | **restricted** | tokenize at bronze→silver; never persisted past silver (**F4** seam) |
| `data.object.customer.name` (bronze only) | source | **restricted** | drop at bronze→silver |
| `data.object.billing_details.address.*` | source | **restricted** | drop at bronze→silver |
| `data.object.metadata.*` | source | **restricted by default** | quarantine + manual review (**F4** mitigation: customer-supplied PII trap) |
| `event_type`, `event_ts_utc`, `payload_silver` (non-PII fields) | derived | internal | normal access |

## Access Tier
- **Bronze (raw S3 landing)**: tier=**restricted**. KMS-encrypted, accessible
  only to `data-platform-pipeline` IAM role. No human read access.
- **Silver (Glue tables)**: tier=**internal**. Accessible to data-eng + the
  3 hard-consumer service roles.
- **Gold (Redshift marts)**: tier=**internal**. Accessible to analytics +
  product. NO email/PII columns present.
- **DLQ (S3 path `s3://.../dlq/...`)**: tier=**restricted**. May contain raw
  PII from rejected events. Same posture as bronze.

## Retention Policy
- Bronze: 90 days, then GDPR-style hard delete.
- Silver: 13 months (one full fiscal year + buffer).
- Gold: 7 years (analytics + audit).
- DLQ: 30 days, then hard delete (forced retention cap because contents are
  PII-bearing by definition).
- **F5 — right-to-be-forgotten**: customer-deletion events trigger a
  scheduled redaction job that propagates deletes through bronze, silver,
  and gold within 24h (G-02 expectation in DQE-001). The job is documented
  in RB-001 §"customer-deletion propagation".

## Residency Constraints
- All bronze/silver/gold storage in `us-east-1`. No cross-region replication.
- DLQ same region.
- EU customer data: scoped out at the source — EU webhooks route through a
  separate Stripe account (`account_eu`) that lands in a parallel pipeline
  in `eu-central-1`. That pipeline is its own helix-data instance, out of
  scope for this example but referenced for completeness.

## Audit Log Requirements
- All access to bronze + DLQ logged to CloudTrail with 1-year retention.
- All Redshift query logs to the `audit_redshift` schema, 7-year retention.
- **F4 enforcement audit**: weekly job scans silver/gold for `@` substrings
  in any text column and emits a Sev1 alert if any row matches. Result
  logged to `audit_pii_canary` with 7-year retention.
- **F5 enforcement audit**: deletion-propagation job logs every redacted
  customer_token + the affected table list. Logged to `audit_redaction`
  with 7-year retention (this is the GDPR audit trail).
- **F11 enforcement audit**: contract-version mismatch incidents logged to
  `audit_contract_breaks` (rare but high-impact; surfaced in monthly
  governance review).
