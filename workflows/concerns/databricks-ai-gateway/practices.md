# Practices: Databricks AI Gateway (model access on Databricks)

The Databricks specifics only; the generic practices are in `model-gateway`.

## Design

- Name who creates each gateway service and issues its Unity Catalog grants.
- Decide the identity per call path in `databricks-apps`; the gateway's usage
  record should name the real caller.

## Implementation

- Send `traceparent` on every model call.

## Deploy

- Confirm the owning module applied the services and grants before the app that
  depends on them. The app's service principal exists only after its first
  deploy, so a first deploy is two steps: deploy, then grant it access.
- Verify by a real call, not by a merged grant.
