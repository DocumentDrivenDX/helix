# CF-02 — "The monitoring dashboard needs a DNS record. Set this up." (cross-flow helix-data → helix-infra)

**Category:** conversation-library (cross-flow discriminators) (plan §1.5b + §14.1)
**Phase:** P5
**Tier:** must_pass_core

## What this asserts

Marker activates BOTH `helix-data` (at `pipelines/customer-events/`)
and `helix-infra` (at `infra/`). The helix-data flow has a
`monitoring-setup.md` (in-progress) whose prose explicitly states
"dashboard URL needs DNS." Plugins: library + methodology-data +
methodology-infra.

Operator says "The monitoring dashboard needs a DNS record. Set this
up." The cross-flow contract per plan §14.1:

1. `helix-data` engages FIRST — the monitoring dashboard is a
   helix-data surface; the skill MUST read `monitoring-setup.md` to
   ground its plan (which dashboard, which URL).
2. The skill MUST surface `helix-infra` as a cross-flow prerequisite
   (DNS record), not "set up DNS in a vacuum".

The structural floor at P5 is the FIRST-engaged-flow signal:
the routing decision MUST land on `helix-data`. The cross-flow
handoff to `helix-infra` is graded by Layer 2/3 at P7+.

This is a standalone cross-flow discriminator row (isolates the
helix-data→helix-infra direction).

## Negative control

`plugins_remove: [methodology-data]`. Without the data plugin no
helix-data skill is registered. The agent — given only
`methodology-infra` — has no flow that owns "monitoring dashboard"
and never reads `monitoring-setup.md`; it sets up DNS in a vacuum.
The routing observable for `helix-data` cannot fire. Verdict flips
present → absent.
