# VS-01 — Read marker AND graph before updating an existing PRD (guided)

**Category:** verbose-but-stuck (plan §1.5b)
**Phase:** P13
**Tier:** must_pass_core
**Invariant under test:** SKILL.md §1.5 ordering rule (Read `.helix.yml`
AND Read `graph.yml` BEFORE any Write/Edit).

## Scenario

Workspace:

- `.helix.yml` marker active with `helix` flow, root `docs/helix/`.
- `docs/helix/01-frame/PRD-001-coffee-ordering.md` already exists with
  approved frontmatter (ddx.links: informs VIS-001).

Operator: "Update PRD-001 to add a new requirement: support gift-card
payments at checkout."

## Expected behaviour (positive)

The skill engages and, BEFORE the first Edit/Write tool_use targeting
the PRD, emits:

1. A `Read` on `.helix.yml` (binds scope + flows authorization).
2. A `Read` on the active flow's `workflows/graph.yml` (binds the type
   catalog + edge candidates for the PRD's frontmatter).

Then performs an Edit on `PRD-001-coffee-ordering.md`. The ordering
matters because:

- Without the marker Read, the skill cannot verify it is allowed to
  write under `docs/helix/` (scope contract).
- Without the graph Read, the skill cannot know which edge kinds are
  valid for `ddx.links` on a PRD (type contract) — it would fall back
  to training-encoded guesses.

The verbose-but-stuck failure mode catches the case where the skill
fires `Skill(helix)` and prose-narrates HELIX reasoning, then writes
without grounding either Read. The matcher fails such transcripts.

## Discriminator

`read_before_write` with `target_pattern: (\.helix\.yml|graph\.yml)$`.
Positive run: at least one Read of either file precedes the first
Edit/Write. Negative-control run (plugin removed): the skill cannot
engage, so the marker/graph Reads are not part of the skill's
discipline; the agent's edit ordering becomes training-driven and the
strict Read-before-Write contract no longer reliably holds.

## Why must_pass_core

The §1.5 ordering rule is the central anti-verbose-but-stuck guard.
If VS-01 fails on a representative update scenario, the rule itself is
not being enforced and downstream artifact contracts (frontmatter,
ddx.links, scope) cannot be trusted.
