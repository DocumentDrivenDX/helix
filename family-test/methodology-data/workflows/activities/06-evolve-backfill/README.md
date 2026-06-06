# 06-evolve-backfill

Purpose: schema evolution, reprocessing strategy, deprecation of
consumers, breaking-change communication. This is the long-tail
concern data engineers actually have — the bulk of pipeline-team work
after launch is here.

Inputs: `data-contract` (requires), `consumer-inventory` (informs,
required and freshness-checked), `metrics-dashboard` (informs for
improvement-backlog).

Outputs:
- `evolution-plan` (exit-gate): breaking_changes, migration_window,
  consumer_notification_plan, rollback_plan, success_criteria.
- `deprecation-notice`: artifact_being_deprecated, successor,
  consumers_affected, timeline, final_decommission_date.
- `improvement-backlog`: prioritized list of pipeline improvements,
  fed by metrics-dashboard signal and incidents from runbook history.

Exit gate: `evolve-validation` — every evolution-plan names a
rollback_plan and a non-trivial success_criteria (NOT "tests pass" —
must reference contract invariants); every deprecation-notice names
every consumer in the inventory tagged `dependency_strength: hard`,
with explicit per-consumer migration status.

Authority boundary: evolution-plan and deprecation-notice drafting is
allowed at all autonomy levels; ANY execution of breaking changes or
consumer cutoffs is `stop_at` regardless of autonomy. helix-data
drafts them and surfaces them for approval; it does not run them.

Stale-inventory check: if `consumer-inventory` is older than the
contract being evolved, refuse to author the notice until the
inventory is refreshed. Surface the freshness gap.
