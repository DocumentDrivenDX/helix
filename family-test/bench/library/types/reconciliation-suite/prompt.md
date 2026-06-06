Draft a reconciliation-suite artifact during helix-data phase 03-validate.
Use it when a pipeline has external truth, layered tables, or regulated reporting consumers.
Gather source system exports, sink tables, comparison windows, currencies, time zones, and owners.
Define invariants in terms of named source and sink fields.
Good output separates row-count, amount, freshness, and identity checks.
Set thresholds by business impact, not by convenience.
Reference runbooks that operators can actually execute.
Include fixture IDs for mismatch, late arrival, duplicate, and replay cases.
Include alert routing and severity for each threshold.
State how long evidence should be retained for audits.
Escalate when no source of truth is available for financial or compliance metrics.
Refuse reconciliation rules that compare incompatible windows or currencies.
Do not hide known drift in broad tolerances.
Mark thresholds that pause release or page on call.
Keep the suite focused on failures consumers would care about.
