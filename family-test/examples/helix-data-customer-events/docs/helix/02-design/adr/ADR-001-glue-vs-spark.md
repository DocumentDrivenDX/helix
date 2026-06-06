---
ddx:
  id: ADR-001
  type: adr
  methodology: helix-data
  library_type_version: 1.0.0
  links:
    - {kind: informs, to: DA-001}
    - {kind: informs, to: DD-001}
---

# ADR-001: AWS Glue (managed Spark) over self-managed EMR Spark

## Context
We need a Spark-shaped compute engine to run the Bronze→Silver
transformations: dedup (F1), PII tokenize/drop (F4), schema fingerprint
(F3), late-arrival folding (F2), and skew detection (F9). The pipeline
processes ~2.4M events/day with bursts to 1.8M/hour. Operators are a
2-person data engineering team that already runs a Glue-based pipeline
for orders.

## Decision Drivers
- **Operational burden**: a 2-person team cannot keep an EMR cluster
  fleet healthy.
- **Cost predictability**: F8 cost-overrun monitoring needs a predictable
  cost model (Glue = DPU-seconds; EMR = instance-hours + EBS + autoscaling
  complexity).
- **Cold-start latency**: the 10-min silver SLA means a 5+ minute Spark
  warm-up is unacceptable.
- **Skill reuse**: the orders pipeline runs on Glue 4.0; same skill set,
  same monitoring, same IAM patterns.
- **Skew + salting (F9)**: must be implementable in PySpark; both engines
  support this.
- **Lineage emit (F7)**: OpenLineage Spark listener works on both engines.

## Considered Options

### Option 1 — AWS Glue 4.0 (managed Spark 3.3)
Pros:
- Job-bookmark mechanism handles incremental bronze→silver reads natively.
- 10x-DPU job warm-pool keeps cold-start ~30s in practice.
- Per-second billing, idle-cost zero — matches our bursty profile.
- IAM-native; no cluster security model to maintain.
- Native CloudWatch integration matches MS-001's monitoring story.

Cons:
- Spark version pinned to Glue's track (~6mo lag vs. upstream).
- Limited shuffle tuning vs. self-managed EMR.
- Glue's auto-scaling has a 10-DPU step floor — small jobs over-provision.

### Option 2 — Self-managed EMR Spark 3.5
Pros:
- Latest Spark; full tuning control (custom shuffle, spot fleet, etc.).
- Lower per-DPU price at sustained load.
- Custom container images.

Cons:
- Cluster lifecycle is the team's problem (24/7 health, autoscaler,
  spot interruption handling).
- Cold-start: 4-7min for a fresh cluster, prohibitive for our 10-min SLA
  unless we keep a warm pool — which inverts the cost advantage.
- Patching, security upgrades, K8s/YARN choices, log shipping — all on us.

### Option 3 — Databricks Jobs
Pros:
- Best-in-class Spark; Delta Lake bonuses.
- Photon engine could halve cost at sustained load.

Cons:
- Adds a vendor relationship the org doesn't have.
- Higher per-DBU price than Glue at our scale.
- Procurement timeline (~6 weeks) is incompatible with the project clock.

## Decision
**Option 1 — AWS Glue 4.0.**

The 2-person ops constraint dominates. Glue's job-bookmark + per-second
billing + zero-idle-cost matches the bursty 2.4M/day profile better than
EMR's tuning ceiling. The 6-month Spark lag is acceptable because we have
no features in the OSS 3.5 release that we currently need.

We reserve the option to revisit if monthly Glue spend exceeds 2x the F8
budget envelope ($800/mo) for two consecutive months — at which point the
EMR Pro/Con balance flips and a re-evaluation ADR is warranted.

## Consequences

### Positive
- Operational burden bounded — no cluster fleet to babysit.
- Cost ceiling well-defined; F8 monitoring (MS-001 alert) trips at $400/mo.
- Lineage instrumentation (F7) uses the same OpenLineage Glue connector
  the orders pipeline already runs.
- Schema-drift detection (F3) implementable in PySpark with no engine
  gymnastics.

### Negative
- Spark version lag means we cannot use AQE's latest skew-join hints.
  We work around this with manual salting (DD-001 §"Skew Detection
  Internals") — this is the F9 mitigation surface.
- Glue's per-DPU price is ~15% higher than EMR at sustained load. At
  our duty cycle (~25%) this still wins.
- Migration cost if we ever switch: the OpenLineage URNs would change
  namespaces, breaking F7 lineage history at the cut-over.

## Status
Accepted (2026-05-29). Next review: 2026-11-29 OR on the first month
where Glue spend > $800.
