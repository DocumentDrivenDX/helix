# T6 — marker declares helix-infra only [HIGH RISK]

**Flow classification:** legacy marker-routing fixture. Retained as a frozen
compatibility probe for the old `methodologies:` marker and public
`helix-infra` sibling-skill design.

## Scenario

`helix-library`, `helix`, and `helix-infra` are all installed. The
workspace `.helix.yml` declares ONLY `helix-infra`:

```yaml
helix_version: 1
methodologies:
  - id: helix-infra
    root: infra/terraform/
```

The workspace contains BOTH `docs/helix/01-frame/prd.md` AND
`infra/terraform/main.tf`. The product methodology shape is in the
tree but NOT declared in the marker.

## Why it matters

Mirror of T5. The marker's job is to silence the product methodology
even when its shape exists on disk. Per design §1.3 and §1.5, an
explicit marker overrides ANY heuristic; a product-shape directory
that the marker did not declare must NOT activate the product
methodology. The user prompt asks for an ADR; the only declared
methodology is helix-infra, so it wins.

## What passes

- `Write` `tool_use` against `docs/adr/<NNNN>-<slug>.md` (helix-infra
  routes ADRs there).
- NO `Write` against `docs/helix/02-design/`.
- Prose MUST NOT surface a disambiguation banner — marker resolves
  unambiguously to helix-infra.

## What fails

- ADR written to `docs/helix/02-design/` (product methodology
  activated despite marker silence).
- Disambiguation banner (marker resolved; no ambiguity to surface).
- Setup-gap (marker not read).

## Risk

HIGH. Symmetric counterpart to T5; both must pass for "explicit
marker silences undeclared methodologies, even when their shape is
present on disk" — the central guarantee of the marker contract.
