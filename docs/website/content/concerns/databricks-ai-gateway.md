---
title: "Databricks AI Gateway (model access)"
slug: databricks-ai-gateway
generated: true
aliases:
  - /reference/glossary/concerns/databricks-ai-gateway
---

**Category:** Data-Governance · **Areas:** api, infra

## Description

## Category
data-governance

## Areas
api, infra

## Platform

**Platform-specific (Databricks).** The AI Gateway fronts model endpoints with
governed access, usage limits, and tracing. This concern is how a product
*calls models through it*, not how it governs the data the models read.

## Boundary

Owns: what the product names when it needs a model, who provisions and grants
the gateway services behind those names, how the names reach the deployed app,
and how the product proves each model it depends on is callable the way it will
actually call it.

Does not own: the identity model (service principal vs on-behalf-of) — see
`databricks-apps`; catalog grants as a general discipline — see `unity-catalog`
(a gateway service is a securable object there; grants: see `unity-catalog`); trace
and log conventions — see `o11y-otel`.

## Components

- **Tier**: a name for the job a call needs done (for example `quick`,
  `balanced`, `deep`), declared by the product. Tiers are not model names and
  not reasoning-effort levels.
- **Gateway service**: the governed endpoint a tier resolves to, with its
  fallback chain, usage limits, and grants. Owned by the infrastructure module,
  per environment.
- **Adapter**: the one place the product speaks to the gateway, on one API
  route.
- **Readiness gate**: a deploy-time call to every tier the app needs.

## Constraints

- **Name the need, not the model.** Product code and plug-ins declare a tier.
  The mapping from tier to model lives in per-environment infrastructure
  configuration, so a model change needs no product release.
- **One owner for services and grants.** The module that creates a gateway
  service also grants access to it. A grant made anywhere else is undone on the
  owner's next apply.
- **Names arrive through the app's per-target configuration, and every
  required one is non-empty after render.** Where the platform offers no app
  resource binding for a gateway service, the infrastructure module publishes
  one value per tier and the deploy renders them into the app's configuration. A missing service name must fail the deploy, not a
  user's first prompt.
- **The readiness gate exercises the call as the product makes it**: the same
  route and the same features (tools, streaming, structured output), once per
  tier, as the caller. A plain-prompt probe passes while tool calls fail.
- **A tier's model must support what the adapter uses on the route it speaks.**
  Capability differs by model family and route; verify by calling, not by
  documentation.
- **Retargeting a tier is a model substitution** and passes the evals of every
  workflow that declares the tier.
- **Model calls join one trace.** Send a W3C `traceparent` so product and
  gateway spans share a trace id. Span attributes carry ids and sizes, never
  prompts, answers, or tool arguments.
- **Identity is `databricks-apps`'s call**; the gateway's usage record names the
  caller.

## Drift Signals (anti-patterns to reject in review)

- A concrete model or service name hardcoded in product code or a plug-in
  manifest → declare a tier
- A gateway grant applied by hand or from the product's repository rather than
  by the module that owns the service
- Deploy passes while the first real prompt returns 404 → readiness gate does
  not call every tier
- Readiness probe sends a plain prompt but production sends tools → probe the
  features actually used
- A tier remapped without re-running the evals that depend on it
- A service-name variable that renders empty without failing the deploy
- Spans or logs carrying prompt or answer text

## When to use

Any product that calls models through the Databricks AI Gateway. Composable (no
slot). Select it with `databricks-apps` and `unity-catalog`; pair with
`o11y-otel` when model calls must be traced end to end.

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- ADR: the tier set, who provisions each service and its grants, how names reach the app
- TD: adapter route and features used; readiness gate coverage
- TEST_PLAN: gate that calls each tier with the features in use; evals gating tier remaps
- deployment-checklist: required service names non-empty after render; grants verified by a real call

## ADR References

Record an ADR for the tier set and its owner, and another when the adapter's
route or required features change. An unverified capability (does this model
accept tools on this route?) is a probe or `tech-spike`, not an assumption.

## Practices by activity

Agents working in any of these activities inherit the practices below through runtime work context, such as a DDx bead context digest.

How a product calls models through the gateway without discovering its gaps in
production. Boundaries and composition: see `concern.md`.

## Requirements (Frame activity)

- Name the jobs the product needs models for, and which workflows depend on
  which. Each becomes a tier.
- State who may choose or change a tier (the user, a router, an operator).

## Design

- Define the tier set and the owner of the tier-to-service mapping. Keep the
  mapping out of product code.
- List the features each tier must support (tools, streaming, structured
  output) and the single route the adapter speaks.
- Identity per call path is `databricks-apps`'s; the gateway's usage record
  names the caller.
- Design the readiness gate: one call per tier, with the features in use, as
  the caller.

## Implementation

- Resolve tiers to service names from per-target configuration; fail the deploy
  when any required name renders empty.
- Send `traceparent` on every model call; keep prompts and answers out of spans.
- Surface the gateway's status in the failure a user or operator sees.

## Testing

- The readiness gate runs in the deploy and fails it.
- Evals for each workflow run on any tier remap.
- Identity-dependent paths are verified on a deployed app, not locally.

## Deploy

- Confirm the owner module applied the services and grants before the app that
  depends on them. The app's service principal exists only after its first
  deploy, so a first deploy is two steps: deploy, then apply the grants to it.
- Verify by a real call, not by a merged grant.
