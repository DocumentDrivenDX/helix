Draft a lineage-spec artifact during helix-data phase 04-build.
Use it when a pipeline needs observable dataset movement, impact analysis, or auditability.
Gather orchestration tool, transforms, tables, jobs, validation steps, and lineage backend.
Choose OpenLineage, dbt-style, or custom based on existing runtime support.
Good output names every source, transform, validation, and published sink node.
Include node IDs that match job and table names.
Describe consumers of lineage, not just the storage system.
Reference lineage-gap fixtures when coverage is being tested.
Name where lineage is emitted in orchestration, transform, and validation steps.
State whether backfills emit historical run lineage or only current runs.
Escalate if regulated or finance-critical outputs lack lineage coverage.
Refuse custom emitters when a supported OpenLineage path already exists unless a constraint is documented.
Do not emit customer PII in lineage metadata.
Keep metadata fields minimal and stable.
Call out any intentionally omitted node.
