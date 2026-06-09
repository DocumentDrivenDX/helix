---
ddx:
  id: DN-001
  type: deprecation-notice
  methodology: helix-data
  library_type_version: 1.0.0
  links:
    - {kind: informs, to: EP-001}
---

# Deprecation Notice: Finance Reconciliation Consumer

## Artifact being deprecated
- **Consumer**: Finance reconciliation pipeline.
- **Contract version frozen at**: v0.9 (predates the current v1.0
  curated schema).
- **Specific surfaces**: the legacy view `customer_events.charge_v09`
  and the `legacy_amount_cents_int` column in `charge_fact`.

## Successor
The Finance team is moving to Stripe's own monthly reconciliation
reports. There is no in-platform successor — Finance is exiting our
pipeline entirely, not switching to a new view.

For other use cases that previously leaned on the v0.9 view, the
successor is the v1.0 charge_fact (or v2.0 once EP-001 ships).

## Consumers Affected

| Consumer | Touchpoint | Migration target |
|---|---|---|
| Finance reconciliation pipeline | `customer_events.charge_v09` view | Stripe monthly reports (out-of-platform) |
| (Implicit) Any analyst with a saved query against `legacy_amount_cents_int` | Redshift saved queries | Use `charge_fact.amount_cents` instead |

Sweep of saved queries on 2026-04-22 identified 7 analyst saved queries
using the deprecated column; all 7 owners were notified individually.

## Timeline

| Date | Milestone |
|---|---|
| 2026-04-01 | Deprecation announced in `#data-platform-changelog` |
| 2026-04-15 | Finance team begins migration to Stripe-side reports |
| 2026-05-15 | Read-only freeze on v0.9 view (no schema changes) |
| 2026-06-15 | Sev3 banner on dashboards using `legacy_amount_cents_int` |
| 2026-07-01 | **Final decommission** |

## Final Decommission Date
**2026-07-01.**

On this date:
- The `customer_events.charge_v09` Redshift view is dropped.
- The `legacy_amount_cents_int` column in `charge_fact` is dropped.
- The Finance consumer's IAM read access is revoked.
- The CONS-001 entry for Finance moves from "DEPRECATED" to
  "decommissioned".
- An entry is added to `audit_contract_breaks` noting the planned
  decommission for the historical record.

## Risk and mitigation

The primary risk is the **F11** failure mode: Finance is hard-coded to
v0.9 with no version check. The EP-001 evolution plan carves out a
v1-frozen path for them through this date specifically to prevent
silent corruption.

Mitigation steps already in place:
- The v0.9 view's schema is frozen (no DDL changes since 2026-03-12).
- Daily R-04 reconciliation sample includes a v0.9-shape query.
- A weekly Finance-team check-in confirms their migration is on track.

If Finance has NOT completed their migration by 2026-06-15, the
deprecation date is extended by 30 days AND a Sev2 incident is opened
to escalate. Decommission is non-negotiable past one such extension
because the cost of maintaining the v0.9 path grows non-linearly with
each v1/v2 evolution cycle.
