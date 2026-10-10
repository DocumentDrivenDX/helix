# Execution Authority and Optional Tracking

An implementation-ready plan is sufficient governing scope when the user
explicitly authorizes implementation. Planning alone does not authorize build.
The runtime owns execution, source control, and release operations.

## Plan-Driven Default

Execute the ordered steps through verified completion. A step boundary or
context-window boundary is not a stopping condition. Continue ordinary debugging
and implementation decisions within scope. Stop for missing authorization, a
material authority conflict, a decision requiring the user, or a concrete blocker.
Do not widen acceptance criteria to make verification pass.

Use a compact continuation record alongside the plan: governing plan path and
revision, completed steps with evidence, remaining steps, decisions, blockers,
and the next action. Reconcile it against the actual diff and tests on resume.
This record is evidence for recovery, not a second issue queue. When a tracker
is explicitly selected, it owns claims, live status, and execution history.

## Optional Work-Item Acquisition

Use a work-item store only when the user requests tracking or the active
execution contract explicitly requires it. Installed binaries, metadata,
frontmatter namespaces, and an available adapter are not such a contract.
Do not search for or invoke a tracker binary to run ordinary HELIX workflows.
Do not load an adapter install guide unless that adapter is explicitly selected.

When tracking applies:

1. Reuse a relevant existing item before creating another.
2. Prefer one item governing a coherent plan. Split only for independent
   scheduling, ownership, parallel execution, or deferred work.
3. Keep scope, acceptance evidence, governing artifacts, and dependencies
   explicit; follow the selected runtime's claim, audit, and closure rules.
4. Do not turn every step or finding into an item. Report review findings and
   suggested corrections; create follow-up items only when requested or required.

Complexity calls for stronger plans and checkpoints, not automatic ticket
proliferation. Preserve required safety stops and verification at every size.
