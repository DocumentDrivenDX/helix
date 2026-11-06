# Practices: Model Gateway (model access)

How a product calls models through a gateway without discovering its gaps in
production. Boundaries and composition: see `concern.md`.

## Requirements (Frame activity)

- Name the jobs the product needs models for, and which workflows depend on
  which. Each becomes an alias.
- State who may choose or change an alias (the user, a router, an operator).

## Design

- Define the alias set and the owner of the alias-to-route binding. Keep the
  binding out of product code.
- List the features each alias must support (tools, streaming, structured
  output) and the single route the adapter speaks.
- Design the deploy gate: one call per alias, with the features and credential
  in use.
- Decide how a model call is matched to the gateway's request log.

## Implementation

- Resolve aliases to routes from per-environment settings; fail the deploy when
  a required one is missing or empty.
- Surface the gateway's status in the failure a user or operator sees.
- Keep retry ownership in one layer.

## Testing

- The deploy gate runs in the deploy and fails it.
- Evals for each workflow run on any alias rebind.
- Identity-dependent paths are verified on a deployed system, not locally.

## Deploy

- Confirm the route owner applied routes and access before the app that depends
  on them.
- Verify by a real call, not by a merged change.
