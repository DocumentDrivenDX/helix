# VS-02 — Read marker AND graph before authoring a new PRD (guided)

**Category:** verbose-but-stuck (plan §1.5b)
**Phase:** P13
**Tier:** must_pass_core
**Invariant under test:** SKILL.md §1.5 ordering rule (Read `.helix.yml`
AND Read `graph.yml` BEFORE any Write/Edit).

## Scenario

Workspace:

- `.helix.yml` marker active with `helix` flow, root `docs/helix/`.
- `docs/helix/00-discover/product-vision.md` (VIS-001, approved).
- No PRD yet.

Operator: "The product vision is approved. Draft the PRD for the
coffee-ordering app."

## Expected behaviour (positive)

The skill engages and, BEFORE the first Write tool_use creating the
PRD, emits:

1. A `Read` on `.helix.yml` (binds scope + flows authorization).
2. A `Read` on `workflows/graph.yml` (binds the PRD's library type +
   the `prd informs product-vision` upstream edge that anchors
   `ddx.links`).

Then writes the new PRD under `docs/helix/01-frame/`.

This is the canonical "new artifact" verbose-but-stuck shape: an agent
that knows HELIX from training can produce a PRD-shaped file without
ever reading the workspace's marker or graph. The §1.5 rule says: not
allowed. The matcher catches the failure by asserting a Read of either
file precedes the first Write.

## Discriminator

`read_before_write` with `target_pattern: (\.helix\.yml|graph\.yml)$`.
Positive run: ordered. Negative-control run (plugin removed): the agent
may still emit a PRD from training, but the marker/graph Reads are no
longer reliably in the lead position.

## Why must_pass_core

New-artifact authoring is the highest-frequency PRD path. If the
ordering invariant doesn't hold here, the skill's contribution beyond
training is unverifiable on creation flows.
