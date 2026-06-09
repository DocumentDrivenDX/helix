# T9 — local:my-adr override (shadowing)

## Scenario

`helix-library` and `helix` are installed. The workspace has an
overlay at `docs/helix/02-design/_overlays/my-adr/spec.yml` that
declares a `local:my-adr` type. The methodology's `graph.yml` binds
the design-phase ADR node to `local:my-adr` instead of `library:adr`.

The `local:my-adr` spec adds a "Customer Impact" section beyond the
canonical ADR sections.

## Why it matters

Per design §4.6, **local overrides shadow library types** for a
single binding. This is the escape valve for teams that need a
customized ADR shape without forking the whole library type.

The test verifies the shadowing actually wins: when authoring an ADR
in the design phase, the local spec's extra section appears, not the
canonical library:adr shape.

## What passes

- `Write` `tool_use` against `docs/helix/02-design/<NNNN>-<slug>.md`.
- The written content includes a `## Customer Impact` heading (from
  the local override).
- The written frontmatter references `local:my-adr` (not
  `library:adr`).

## What fails

- The written content lacks the override section (library:adr won
  silently).
- Frontmatter says `library_type: library:adr` (override ignored).

## Risk

Medium. The override mechanism is documented but has subtle merge
semantics. A miss here doesn't break the family architecture, but
breaks the override contract.
