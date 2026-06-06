Draft a backfill-plan artifact during helix-data phase 03-validate.
Use it before replaying historical partitions, dead letters, or corrected transformations.
Gather trigger, incident ID, affected date range, partition selector, row counts, dependencies, and consumers.
Confirm whether the execution environment allows autonomous changes.
Describe pre-run checks before any mutation.
Good output has bounded scope, a dry-run path, rollback mechanics, and clear consumer messaging.
Include expected runtime and resource limits so operators can schedule safely.
Reference fixtures for late events, replay, erasure, or reconciliation mismatches when relevant.
Name the exact tables, jobs, and partitions that will change.
Separate dry-run validation from the production swap.
Refuse to execute or imply execution when autonomy is manual.
Escalate if the backfill touches finance close, privacy deletion, or downstream SLAs.
Do not broaden scope to "all history" without an approval record.
Call out consumer-visible metric changes.
Prefer partition swaps or shadow tables when rollback risk is high.
End with the communication plan, not operational optimism.
