# CRM Scope Decision

Bead: `helix-5129f35d`
Parent epic: `helix-db7d13a9`
Governing scope: `helix.prd` at `docs/helix/01-frame/prd.md`

## Decision

Keep the CRM artifact stack in this repository only as a HELIX worked example
and demo planning artifact rooted at `docs/examples/crm/`.

## Rationale

`docs/helix/01-frame/prd.md` defines HELIX as methodology content, an artifact
catalog, examples, and one portable alignment/routing skill. It also keeps
domain-specific product extensions out of scope. The CRM artifacts are
therefore acceptable here as illustrative HELIX material, but not as a HELIX
product surface or CRM product implementation.

## Parent-Epic Linkage

The parent epic `helix-db7d13a9` remains the umbrella for the CRM example
planning stack under provisional spec-id `CRM-001`. If work proceeds beyond
example/demo planning into actual CRM product implementation, migrate the
artifact stack to a dedicated HELIX-managed CRM project repository by seeding
that repo from `docs/examples/crm/`, then supersede or retire the `CRM-001`
beads that no longer belong in this repository.
