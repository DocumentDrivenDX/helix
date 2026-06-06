---
ddx:
  id: RB-001
  type: runbook
  methodology: helix-data
  library_type_version: 1.0.0
  links:
    - {kind: informs, to: IB-001}
---

# Runbook: Customer Events Pipeline

On-call playbook. Every section corresponds to a documented alert + a
specific adversarial fixture in `fixtures/`.

## Duplicate-event surge (F1)

**Symptom**: T-B02 dedup window flagging > 1% duplicates.

**Diagnose**
1. Check Stripe status page (`status.stripe.com`) — they may be retrying.
2. Check the signature-verify Lambda error rate; if elevated, Stripe is
   retrying because we 5xx'd.

**Respond**
- If Stripe-side: monitor; dedup is doing its job, no action.
- If our-side (Lambda 5xx): page Lambda owner; the dedup is masking the
  real problem.

**Validate the fix**
- 24h trailing dedup rate returns to baseline (< 0.01%).

## Late-event arrival surge (F2)

**Symptom**: `dlq/late_event/` growing > 10k/hour.

**Diagnose**
1. Check Stripe events API for delivery lag.
2. Check the silver job's late-arrival rule (DD-001 step 5).

**Respond**
- Spike during Stripe-side incident: expected; trigger late-event replay
  (BP-001) after Stripe recovers.
- Sustained baseline shift: revisit the 24h watermark — may need widening.

## Schema drift detected (F3)

**Symptom**: T-B06 or T-S03 alerts.

**Diagnose**
1. Pull the offending event from `dlq/schema_drift/`.
2. Compare `payload_silver` shape to the contract fingerprint.
3. Determine: additive (new field) or breaking (narrowed/removed)?

**Respond**
- Additive: update `data-contract-stripe-events.md` (DC-001) to include the
  new field; bump `library_type_version`; deploy new schema fingerprint.
  Roll forward — no consumer impact.
- Breaking: HALT silver promotion; escalate to data-eng + Stripe vendor
  contact. Engage EP-001 (evolution-plan) workflow.

## PII canary fired (F4)

**Symptom**: T-S02 BLOCKING alert; silver→gold promotion halted.

**Diagnose**
1. Inspect the offending row in `dlq/pii_metadata/`.
2. Determine whether the leak is via `customer.email` (should have been
   tokenized — pipeline bug) OR `metadata.{}` (customer-supplied — data
   exposure).

**Respond**
- Pipeline bug: roll back the silver job to the prior version; fix the
  bug; redeploy; verify on golden corpus before resuming.
- Customer-supplied: confirm rows did NOT promote to gold; trigger the
  GDPR-style audit log entry (`audit_pii_canary`); contact the offending
  customer's account manager.

**Hard gate**: T-S02 must clear before silver→gold resumes. No override
exists for this.

## Customer-deletion propagation (F5)

**Symptom**: scheduled redaction job's daily report shows lag, OR R-05
reconciliation breach.

**Diagnose**
1. Pull the affected `customer_token` from the audit log.
2. Check whether the prune job ran successfully across all gold tables.

**Respond**
- Job failure: re-run for the missed `customer_token`; log to
  `audit_redaction`.
- Sustained: open IB-001 entry (improvement backlog) to harden the prune
  job; engage governance review.

**Hard gate**: GDPR exposure; Sev1; 24h to resolution.

## Reconciliation drift response (F6)

**Symptom**: R-01 or R-04 reconciliation alerts.

**Diagnose**
1. Drift direction: bronze-low (data loss?) or gold-low (load failure?).
2. Time-bound the gap window.
3. Check the F10 DLQ for the relevant reason codes.

**Respond**
- bronze-low: check API Gateway error rate; check Firehose error metrics;
  examine recent Stripe events API for the gap window.
- gold-low: check Redshift COPY logs; if fingerprint mismatch (G-06),
  this is actually an F11 — escalate that path instead.
- Both: trigger targeted backfill per BP-001 Scenario 2 for the affected
  window.

**Validate the fix**
- R-01 returns within tolerance for 24h.

## Lineage gap remediation (F7)

**Symptom**: R-06 or T-S04/T-G03 alert.

**Diagnose**
1. Identify the gold rows missing `lineage_ref`.
2. Check OpenLineage emit failures in the Glue job logs around the
   affected time window.

**Respond**
- Emit failure: the row(s) should be in `dlq/lineage_emit_failed/`. Fix
  the DataHub connectivity issue; replay the DLQ subpath.
- Silver-job bypass (someone wrote silver without emitting): treat as a
  pipeline defect; roll back, fix, redeploy.

**Hard gate**: lineage gap is a contract violation; cannot be silenced.

## Cost overrun (F8)

**Symptom**: F8 alert in MS-001 — Glue spend > $400/mo run-rate.

**Diagnose**
1. Pull the partition-explosion check from MD-001.
2. Check for unbounded scans in Glue (sub-partition not used).
3. Check for hot-key skew (F9 may be co-occurring).

**Respond**
- Partition explosion: identify which event_type is over-emitting; verify
  the sub-partition is being honored.
- Skew: enable salted-join mode for the affected batches.
- Sustained beyond mitigations: open IB-001 entry for re-evaluation of
  ADR-001's Glue choice.

## Hot-key / skew (F9)

**Symptom**: T-S06 hot-key alert.

**Diagnose**
1. Pull the offending `customer_token` from the skew log.
2. Hash back to the customer ID (with consent) and identify the upstream
   cause.

**Respond**
- Enable salted-join mode for the next N batches.
- Contact product to engage with the customer if the upstream cause is
  an integration bug.

**Validate the fix**
- T-S06 clears for 24h.

## DLQ replay after schema fix (F10)

**Procedure**: see BP-001 Scenario 2.

**Operator checklist**
- [ ] Root cause documented and fix shipped.
- [ ] DLQ writes for the affected reason code stopped ≥1h.
- [ ] Dry-run on first 1000 rows succeeds.
- [ ] Replay scoped to the single reason-code subpath.
- [ ] Replay tagged with `replay_run_id`.
- [ ] Reconciliation R-01..R-03 stays green during replay.
- [ ] Soft notification sent to `#data-platform-changelog`.

## Contract-version mismatch (F11)

**Symptom**: T-G06 fingerprint mismatch alert.

**Diagnose**
1. Identify which consumer is on the mismatched version.
2. Check whether they ACKed the most recent contract bump per CONS-001.

**Respond**
- If the consumer is deprecated (Finance, per DN-001): force-cutover to
  v0.9 frozen view if still pre-sunset; otherwise this is the sunset
  triggering moment.
- If the consumer is hard + active: HALT gold load to that consumer's
  scoped view; engage the consumer team; do not silently degrade.

**Hard gate**: F11 silent-tolerance was the original failure mode; the
contract enforces explicit acknowledgment.

## Capture as golden

When a new failure mode hits production:
1. Capture the offending event payload (sanitized).
2. Add it to `fixtures/golden-events/F<n>-<slug>.json`.
3. Add a new F-fixture YAML if it's a category not yet covered.
4. Add a corresponding test to DQT-001.
5. Update this runbook with the diagnose/respond sections.

This is the feedback loop that keeps F-fixtures comprehensive.
