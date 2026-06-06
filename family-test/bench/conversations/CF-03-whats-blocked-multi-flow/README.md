# CF-03 — "What's blocked across the project?" (multi-flow status query)

**Category:** conversation-library (cross-flow discriminators) (plan §1.5b + §14.1)
**Phase:** P5
**Tier:** must_pass_core

## What this asserts

Marker activates ALL THREE flows: `helix` (at `docs/helix/`),
`helix-data` (at `pipelines/orders/`), and `helix-infra` (at
`infra/`). Each flow has at least one in-progress artifact:

- helix: `docs/helix/01-frame/prd-002.md` (status: in-progress)
- helix-data: `pipelines/orders/data-product-brief.md` (status: in-progress)
- helix-infra: `infra/network-plan.md` (status: in-progress)

Plugins: library + methodology-product + methodology-data +
methodology-infra.

Operator says "What's blocked across the project?" The cross-flow
contract per plan §14.1: a project-wide status query MUST engage
all flows whose markers are active, so each flow can report its own
in-progress work. Per-flow skills MUST engage; the agent MUST NOT
answer from prose/training alone.

The structural floor at P5 lists all three `Skill(*)` tool_uses.
The typed discriminator (`skill_tool_use`) pins `Skill(helix-data)` because:

- helix-data is the most plugin-discriminating flow (its skill is
  registered ONLY when methodology-data is installed; library alone
  gives no helix-data skill).
- The negative control (`plugins_remove: methodology-data,
  methodology-product, methodology-infra` — i.e. keep only library)
  unregisters all three flow skills; `Skill(helix-data)` cannot fire,
  the agent answers from prose/general-knowledge with no per-flow
  status query.

The fact that ALL three flows must engage is graded at Layer 2/3
when the judge is wired (P7+); the typed Layer-1 floor uses one
flow's tool_use as the binary discriminator.

This is a standalone cross-flow discriminator row (isolates the
multi-flow status-query pattern from C021/C022/C025 which carry
single-flow floors).

## Negative control

`plugins_remove: [methodology-product, methodology-data,
methodology-infra]` — only `library` remains. No per-flow skill is
registered; the agent can only answer from prose/training/general
knowledge and cannot query any flow's status. `Skill(helix-data)`
tool_use cannot fire. Verdict flips present → absent.
