---
ddx:
  id: current-state-inventory-analytics-estate
  type: current-state-inventory
  status: draft
  authoring:
    home: repo
---

# Current-State Inventory: Analytics Estate

Register of what Northwind Retail already runs for reporting and analytics,
each entry graded for evidence. **This is a survey, not a target.** The
warehouse consolidation decision lives in [[architecture]] and ADR-014.

## Scope and Boundary

- Estate: reporting, analytics and the pipelines feeding them
- Surveyed: 3–17 March 2026
- Excluded: transactional systems (covered by the order-platform inventory);
  marketing SaaS, which Marketing Ops owns and has not shared
- Owner: Priya Raman, Data Platform

## Evidence Grades

| Grade | Means |
|-------|-------|
| **Evidenced** | A named source attests it exists and works this way. Cited, with a date. |
| **Partial** | It exists, but a design-defining fact about it is unrecorded. |
| **Assumed** | Claimed, with no source. It may be real; we cannot say so. |
| **Aspirational** | Target state. It does not exist today. |
| **Spike-open** | A design-defining fact is assumed *and* blocks a decision. |

An entry graded Evidenced with no citation is Assumed.

## Inventory

### Ingestion

| Component | Supplier / incumbent | Grade | Evidence |
|-----------|----------------------|-------|----------|
| Nightly ETL | Airflow 2.6, self-hosted | Evidenced | Runbook walkthrough, Priya Raman, 5 Mar 2026. 41 DAGs, 02:00 UTC |
| CDC from orders DB | Debezium | Partial | Confirmed running (Priya, 5 Mar). Which tables it covers is unrecorded |
| Partner SFTP drops | — | Assumed | Named on the 2024 platform diagram; no owner found, no job scheduling it |

### Storage

| Component | Supplier / incumbent | Grade | Evidence |
|-----------|----------------------|-------|----------|
| Warehouse | Redshift, 4-node ra3.xlplus | Evidenced | Billing console, 6 Mar 2026 |
| Lake | S3, `nw-analytics-raw` | Partial | Exists (console). Retention policy and access model unrecorded |
| Lakehouse | Iceberg on S3 | Aspirational | On the FY27 plan. No table, no catalog, no owner |

### Consumption

| Component | Supplier / incumbent | Grade | Evidence |
|-----------|----------------------|-------|----------|
| Exec dashboards | Looker | Evidenced | Licence renewal, 12 Mar 2026. 9 of 340 dashboards viewed weekly |
| Ad-hoc SQL | Redshift Query Editor | Evidenced | Query logs, 11 Mar 2026 |
| Notebooks | — | Spike-open | Analysts describe "notebooks" without naming a platform. Blocks the compute-isolation decision in ADR-014 |
| Embedded reporting | — | Assumed | On the diagram. No consumer found |

## Totals

Tallied from the rows above, 17 March 2026.

| Grade | Count | Share |
|-------|-------|-------|
| Evidenced | 4 | 40% |
| Partial | 2 | 20% |
| Aspirational | 1 | 10% |
| Assumed | 2 | 20% |
| Spike-open | 1 | 10% |

**3 of 10 entries have no evidence they exist** — the Assumed and Aspirational
rows. Two of those three are on the 2024 platform diagram and nowhere else,
which is the strongest argument in this document for retiring that diagram.

## Open Questions

| # | Question | Blocks | Owner |
|---|----------|--------|-------|
| 1 | Which tables does CDC actually cover? | Warehouse consolidation scope | Priya Raman |
| 2 | What do analysts mean by "notebooks"? | ADR-014 compute isolation | Sam Okafor |
| 3 | Does anything consume the partner SFTP drops? | Whether ingestion can be retired | Priya Raman |

## Review Checklist

- [x] Every entry carries exactly one grade from the declared vocabulary
- [x] Every Evidenced entry names a source and a date
- [x] Totals are tallied from this revision, not carried forward
- [x] The unevidenced share is stated, not implied
- [x] Scope and exclusions are both stated
- [x] No target state, recommendation or decision has crept in
