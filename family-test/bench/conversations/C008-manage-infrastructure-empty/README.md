# C008 — "Let's manage our infrastructure"; empty workspace (guided, exploratory)

**Category:** conversation library (plan §1.5 row C008)
**Phase:** P5b
**Tier:** exploratory
**Flow classification:** legacy sibling-flow research row. Retained as an
expected-failing router probe for the retired public `helix-infra` skill
design; not current HELIX user guidance.

## Scenario

Workspace state:
- Empty repository. No `.helix.yml`, no docs/, no prior artifacts.

Operator says: "Let's manage our infrastructure for the coffee-ordering
service."

## Expected behaviour

Per plan §1.5 and §5.1: helix-infra's SKILL.md description claims the
verbs "terraform, tofu, infrastructure, cloudflare, DNS." The verb
"manage our infrastructure" routes to helix-infra.

Under `autonomy=guided` the skill MUST:

1. Engage as helix-infra (description anchor on "infrastructure").
2. Surface the marker addition: "add helix-infra to .helix.yml".
3. Offer to draft the first helix-infra artifact (change-intent).
4. ASK before the first state-changing tool_use.

## Why exploratory

helix-infra is a P5b/P6 scaffold (per plan §6.x); its full description
and graph aren't authored to the discrimination-fidelity P5-core rows
require. The verb-routing surface ("infrastructure" → helix-infra) is
sound but downstream cascade (change-intent → plan → apply) is not
mechanised at v1. Marked exploratory per plan §5 row C008.

## Negative control

Plugin removed (`plugins_remove: [methodology-infra]`). Without
helix-infra's description loaded, the verb "infrastructure" does not
route to a HELIX-family flow; the agent will not propose helix-infra
by name or surface change-intent as the first artifact.
