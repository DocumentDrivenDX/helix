# VS-04 — Read marker AND graph before authoring a cross-cutting ADR (guided)

**Category:** verbose-but-stuck (plan §1.5b)
**Phase:** P13
**Tier:** must_pass_core
**Invariant under test:** SKILL.md §1.5 ordering rule applies to
cross-cutting artifacts (ADRs) just as it applies to cascade-anchored
artifacts (PRDs).

## Scenario

Workspace:

- `.helix.yml` marker active with `helix` flow, root `docs/helix/`.
- `docs/helix/00-discover/product-vision.md` approved.
- No PRD or ADR yet.

Operator: "Record an ADR for choosing Postgres as the primary
datastore."

## Expected behaviour (positive)

ADRs are cross-cutting per `graph.yml` (the `adr` node has
`scope: cross-cutting` in the methodology-product graph) and may be
authored without upstream PRD/vision dependencies — see C012. That
relaxation is about EDGE prerequisites, NOT about §1.5 Reads. The
skill must STILL:

1. `Read` `.helix.yml` to verify scope + flow authorization.
2. `Read` `workflows/graph.yml` to confirm `adr` is a known node type
   AND to surface the `scope: cross-cutting` annotation that allows
   the empty `depends_on` chain.

Then write the ADR under `docs/helix/02-design/`.

The failure mode this row catches: an agent that has internalized
"ADRs are cross-cutting" from training writes the ADR straight from
prose, bypassing the §1.5 Reads on the grounds that "no upstream
artifacts are needed". The §1.5 rule is independent of edge
prerequisites — Reads precede every Write regardless of the artifact's
cascade position.

## Discriminator

`read_before_write` with `target_pattern: (\.helix\.yml|graph\.yml)$`.
Positive run: ordered. Negative-control (plugin removed): the agent
may emit an ADR from training, but the marker/graph Reads are not
reliably ordered before the Write.

## Why must_pass_core

Cross-cutting artifacts are the most likely place an agent rationalises
skipping §1.5 ("nothing upstream so nothing to read"). The rule's
generality is the contract; VS-04 keeps it honest.
