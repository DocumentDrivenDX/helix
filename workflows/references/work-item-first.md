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

## Token Spending and Administrative Restraint

When an agent estimate is needed, give a token range grounded in comparable
completed runs: cite the existing usage evidence, model, scope, and assumptions,
including verification and likely retries. Distinguish input, cached input, and
output when metered; compare like usage categories. Without comparable evidence,
say unknown; a small bounded probe may establish a baseline when useful. Do not
invent a calendar date from human sprint conventions. Forecast elapsed time only
from observed throughput, concurrency, and actual waits or dependencies; keep
human effort separate. Monetary estimates require known model rates.

Use an existing plan's execution contract or the runtime's current controls for
a total token ceiling, including planning, implementation, verification, review,
and administrative work. Honor the user's ceiling; when none exists, choose and
state a provisional ceiling from the evidence rather than ask routinely. With no
baseline, bound the probe first, then revise the estimate from measured usage.
The runtime owns metering and enforcement: use available limits, and check usage
at existing checkpoints before another costly phase or review. If usage or hard
limits are unavailable, disclose that once; never claim an enforced cap. At the
ceiling, preserve recovery evidence and report unfinished work; do not silently
raise the limit or declare completion. Required verification remains required.

Update administration on a meaningful change in scope, decision, blocker,
verified result, or handoff. Coalesce updates at existing checkpoints; do not
rewrite unchanged status, duplicate live runtime records, or create a report or
item merely to record spending. Preserve required leases, heartbeats, and audit
events; let the runtime maintain them without repeated agent narration. At
closeout, add measured usage and material estimate variance to the existing
completion evidence when available, so the next estimate can reuse it.

Review once by default. Re-review only changed material and affected dependencies
after a blocking fix or new evidence; unchanged content and advisory preferences
do not justify another pass. Reuse verified findings and test results while their
inputs remain valid. Any repeated or parallel review shares the total ceiling
and needs a distinct risk or question. Stop when blockers are resolved, no new
actionable evidence appears, or the round or spending limit is reached; report
remaining blockers without weakening acceptance.
