# helix-data worked example: customer-events pipeline

A complete, marker-valid walkthrough of the **helix-data** flow against a real-shaped scenario: **Stripe webhook events → S3 → Glue → Redshift**, consumed by analytics and ops.

This example is the verification artifact for Phase 9 of the conversation-bench plan. It walks every helix-data lifecycle activity end-to-end against a single data product, with every artifact tied to one or more of the 11 adversarial fixtures (`fixtures/F1-F11`) so each lifecycle stage is provably catching real failure modes — not just rendering a sanitized happy path.

## Scope

- **Source**: Stripe webhook stream (`charge.*`, `customer.*`, `invoice.*` event types).
- **Sinks**: S3 raw landing (bronze), Glue-curated silver tables, Redshift gold marts.
- **Consumers**: analytics (Redshift dashboards), ops (Slack alerts), product (Looker).
- **Out of scope**: the apps that produce or consume the data (helix product flow), the AWS accounts and IAM that host them (helix-infra), the UI dashboards' design system (helix-web).

## Walkthrough by activity

| Activity | Artifacts | Adversarial fixtures exercised |
|---|---|---|
| `00-discover` | `data-product-brief.md`, `source-profile-stripe.md`, `consumer-inventory.md` | F1, F2, F3, F4, F8 |
| `01-contract` | `data-contract-stripe-events.md`, `data-quality-expectations.md`, `governance-classification.md` | F1, F3, F4, F5, F11 |
| `02-design` | `data-architecture.md`, `data-design.md`, `adr/ADR-001-glue-vs-spark.md` | F2, F4, F7, F8, F9, F10 |
| `03-validate` | `data-quality-tests.md`, `backfill-plan.md`, `reconciliation-suite.md` | F1, F2, F3, F6, F9, F10 |
| `04-build` | `implementation-plan.md`, `lineage-spec.md` | F7 |
| `05-operate` | `runbook.md`, `monitoring-setup.md`, `metrics-dashboard.md` | F1, F2, F4, F6, F7, F8, F9, F10 |
| `06-evolve` | `evolution-plan.md`, `deprecation-notice.md` | F3, F5, F11 |

## Validation

```bash
# Static marker check — required to pass.
helix_check.py marker examples/helix-data-customer-events/.helix.yml --strict

# Adversarial coverage — every F1-F11 fixture must be referenced by ≥1 artifact.
helix_check.py example --adversarial-coverage examples/helix-data-customer-events/
```

CI re-runs both checks on every helix-data PR. The example is the operator's reference for what a complete data-pipeline scope looks like.

## How to read this example

1. Start with `docs/helix/00-discover/data-product-brief.md` — it frames the problem.
2. Read `01-contract/data-contract-stripe-events.md` to see the producer/consumer surface.
3. `02-design/adr/ADR-001-glue-vs-spark.md` shows a real decision with consequences.
4. `03-validate/` shows tests-as-contracts, including the backfill rehearsal.
5. `05-operate/runbook.md` is the operator's playbook for the 11 adversarial scenarios.
6. `06-evolve/` shows how the flow handles breaking changes and deprecation.

The `fixtures/F<n>-*.yml` files are the adversarial scenarios each artifact must address. Search any artifact for `F1`, `F2`, ... `F11` to see which fixture it covers.
