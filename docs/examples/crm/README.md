---
ddx:
  id: crm.readme
---

# CRM Example - Worked Example Artifacts

This directory holds discover, frame, and design artifacts for a hypothetical
CRM product, authored from the sparse intake `"design a CRM"` via the HELIX
methodology.

It exists for two reasons:

1. **Dogfood.** Exercise HELIX templates on a greenfield product distinct from
   HELIX itself.
2. **Demo material.** Provide a self-contained example of how HELIX turns a
   one-line intake into vision/PRD artifacts with explicit assumptions.

## Artifacts

| ID | Path | Purpose |
|---|---|---|
| `crm.vision` | `00-discover/product-vision.md` | North-star CRM product vision |
| `crm.prd` | `01-frame/prd.md` | CRM product requirements (MVP scope) |
| `crm.solution-design` | `02-design/solution-design.md` | CRM worked-example solution design grounded in `crm.prd` |

## Scope and authority

These artifacts govern downstream CRM work referenced under the provisional
spec-id `CRM-001`. Beads filed against `CRM-001` should adopt `crm.prd` (or a
narrower canonical ID once feature specs land) as their governing reference.

The CRM artifact stack remains in this repository only as a HELIX worked
example and demo planning artifact. Bead `helix-5129f35d` records the scope
decision against the HELIX PRD: HELIX ships methodology content, artifact
templates, quality criteria, and examples; it does not add domain-specific
product extensions. CRM planning here is therefore illustrative material, not a
HELIX product surface.

If CRM work moves beyond example/demo planning into product implementation,
migrate it to a dedicated HELIX-managed CRM project repository. Seed that repo
from this directory, then replace provisional spec-id `CRM-001` with the new
project's canonical artifact IDs.

## Status

Discover, frame, and design artifacts exist. Downstream decomposition and
later-activity implementation planning are not authored here yet; those remain
tracked by sibling beads `helix-7e8a9c4b` (decomposition) and any follow-on
CRM example planning work.
