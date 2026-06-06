# C010 — Deploy the site (multi-flow, cwd disambiguates)

**Category:** conversation-library (happy paths) (plan §1.5b)
**Phase:** P5
**Tier:** must_pass_core

## What this asserts

Marker activates BOTH `helix-web` and `helix-infra`. The site lives at
`services/web/`. Operator says "Let's deploy the site" with cwd set to
`services/web/`. Per the §1.5 / §13.6b resolution chain, cwd-under-scope
wins: the skill MUST route to `helix-web`'s deploy flow, not
`helix-infra`'s.

The discriminator is `route_decision` with
`routing_signal: prose_attribution` — the agent's prose must attribute
the routing decision to `helix-web` (not `helix-infra`).

## Negative control

Remove the `helix-web` instance from the marker. With only `helix-infra`
active, the agent cannot route to a `helix-web` flow that no longer
exists; routing attribution to `helix-web` cannot fire.
