Draft a data-quality-tests artifact during helix-data phase 03-validate.
Use it when a dataset, pipeline, contract, or release needs explicit validation coverage.
Gather the dataset name, layers touched, existing expectations, schedules, fixtures, and known failing cases.
Ask for source and sink schemas when expectations depend on typed fields.
Capture tests as inventory entries with stable IDs and expectation IDs.
Name concrete fixture IDs, including adversarial fixtures when they reveal regressions.
Good output is executable by a validator or easy to translate into Great Expectations, dbt tests, or SQL checks.
Prefer high-signal tests over broad vague assertions.
Include duplicate, late-arrival, schema-drift, erasure, replay, and reconciliation cases when relevant.
Known failures must include an owner and expiry.
Tie each expectation to a release gate or monitoring job.
Call out tests that must run before backfills or schema evolution.
Refuse to mark validation complete when required fixtures or expectations are missing.
Escalate if a known failure affects regulated, financial, or consumer-facing reporting.
Do not invent passing results; label unrun tests as pending.
Keep the artifact short enough for release review.
