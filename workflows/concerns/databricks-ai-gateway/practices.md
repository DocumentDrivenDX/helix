# Practices: Databricks AI Gateway (model access)

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
