---
name: helix-infra
description: HELIX IaC operator flow — authors and edits OpenTofu/Terraform modules, state operations, and IaC change instances. Engage ONLY when the prompt names an explicit IaC verb (tofu/terraform plan/apply/import/state, write/edit a module, provision/destroy a resource). Do NOT engage on mere mention of a cloud or provider (Cloudflare/AWS/GCP) when the prompt is a product-shaped ask like "plan the change" or "the PRD says…" — those route to the `helix` product flow first, which then surfaces helix-infra as a cross-flow prerequisite.
version: 0.1.1
license: MIT
---

# HELIX IaC flow (slice)

Activates when `.helix.yml` lists `helix-infra` as an active flow
(legacy marker key `methodologies:` accepted under M020 warn) under a
scope containing OpenTofu/Terraform work AND the operator prompt names
an explicit IaC verb (e.g. `tofu plan`, `terraform apply`, "write a
module", "import this resource", "provision the zone").

If the prompt is product-shaped — "plan the change", "the PRD says
we need…", "what should we do about…" — DEFER to the `helix` product
flow even when the PRD or marker mentions cloud providers like
Cloudflare, AWS, or GCP. The `helix` flow reads the PRD, frames the
work, and surfaces `helix-infra` as a downstream cross-flow
prerequisite. Engaging helix-infra first on a product-shaped ask
short-circuits the PRD read and plans infra in a vacuum.
