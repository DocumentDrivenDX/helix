Draft an evolution-plan artifact during helix-data phase 06-evolve.
Use it for schema changes, semantic changes, pipeline version upgrades, or consumer contract shifts.
Gather current and target contracts, affected fields, consumers, migration dates, and validation evidence.
Identify breaking changes plainly.
Good output provides a bounded migration window, notification plan, rollback path, and measurable criteria.
Call out dual-write or dual-read periods.
Reference fixture IDs for schema drift and consumer-side mismatch.
Name compatibility tests that prove old and new contracts can coexist.
State the rollback decision point before removing legacy fields.
Escalate when a consumer cannot test before the migration window closes.
Refuse to treat breaking changes as non-breaking because a default value exists.
Do not remove old fields before sign-off from affected consumers.
Include rollback for both data and orchestration.
Keep success criteria observable in tests, monitors, or consumer acknowledgments.
Prefer compatibility shims over synchronized big-bang changes.
