# Work-Item Acquisition

Use a runtime work-item store when the user requests tracker-backed execution
or the active runtime requires it. Routine authoring, alignment, and review do
not create tracker items by default.

## Acquisition

When tracker-backed execution applies:

1. Search for an open item that covers the requested scope and action.
2. Reuse it if it remains relevant; otherwise create an item only when the
   user authorized durable work or the runtime requires one.
3. Give the item a clear goal, scope, governing artifact, and verifiable
   outcome. Include a context digest when the runtime's contract requires one.
4. Follow the runtime's rules for claiming, measuring, and closing the item.

Do not create a tracker item solely to record an alignment or review finding.
Create follow-up work when requested or required by a runtime consumer. Report
the evidence and suggested next step even when no tracker is available.

The DDx runtime may impose additional acquisition rules in its own install
guidance. Those rules belong to that runtime and do not change HELIX's
conversational default.
