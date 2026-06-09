---
ddx:
  id: FEAT-X
  type: feature-specification
  status: drafted
  links: []
---

# Feature X — Receipt export

Operators export the day's receipts as a single CSV from the admin
panel. Triggered manually before close. No scheduling, no retention
policy — the file is downloaded once and discarded by the caller.

## Acceptance

- Export button on the admin receipts page.
- CSV columns: `receipt_id`, `placed_at`, `total_cents`, `floor`.
- Empty-day export returns an empty file with the header row only.
