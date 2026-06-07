---
name: helix-web
description: |
  HELIX web/frontend operator flow — owns the application surface a customer
  interacts with: site/app deploys, page perf, RUM/web monitoring (page
  errors, conversion funnel), and frontend release ops. Engage ONLY when the
  prompt names an explicit web/app-deploy verb (deploy/ship a feature to
  production, publish a build, add monitoring for a user-facing flow like
  checkout, optimize page performance). Do NOT engage on product-shaped asks
  ("plan the change", "the PRD says…") — DEFER to the `helix` product flow
  first; it frames the work and surfaces helix-web as a cross-flow
  prerequisite. Do NOT engage on infra-shaped verbs (terraform/tofu, CI
  runners, secrets, provider credentials) — DEFER to helix-infra. Do NOT
  engage on data-shaped verbs (backfill, ingest, schema migration) — DEFER
  to helix-data. Honor explicit operator prefix (/helix-web ...) and
  env override (HELIX_METHODOLOGY=helix-web) — stay silent otherwise.
version: 0.1.0
license: MIT
---

# HELIX web flow (slice)

Activates when `.helix.yml` lists `helix-web` as an active flow under a
scope containing the web/frontend application code (e.g. `services/web/`,
`apps/site/`) AND the operator prompt names an explicit web verb:

- `deploy`/`ship` the new feature to production
- `publish` a build / cut a frontend release
- add `monitoring` for a user-facing flow (checkout, signup, conversion
  funnel — the RUM/page-error/perf layer, not host/network/cost)
- `optimize` page performance / fix a Web Vitals regression
- frontend-only rollout decisions

If the prompt is product-shaped ("plan the change", "the PRD says we need
…", "what should we do about onboarding churn") DEFER to the `helix`
product flow. The product flow reads the PRD, frames the work, and
surfaces `helix-web` as a downstream cross-flow prerequisite. Engaging
helix-web first on a product-shaped ask short-circuits the PRD read and
plans a frontend deploy in a vacuum.

If the prompt names an explicit IaC verb (terraform/tofu/kubectl,
provision/destroy a resource, CI runner setup, credential rotation),
DEFER to `helix-infra`. helix-web consumes infra; helix-infra owns it.

If the prompt names a data-pipeline action (backfill/ingest a table,
profile a source, write a data contract, migrate a schema), DEFER to
`helix-data`. helix-web consumes data; helix-data owns the pipeline.
