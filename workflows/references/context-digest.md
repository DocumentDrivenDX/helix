---
dun:
  id: helix.workflow.context-digest
  depends_on:
    - helix.workflow.principles-resolution
    - helix.workflow.concern-resolution
    - FEAT-006
---
# Context Digest Assembly

This reference defines how HELIX assembles a compact context digest into
beads at creation time, making them self-contained execution units.

## Purpose

Implementing agents should be able to work from a bead's description alone
without reading upstream files in the common case. The context digest
summarizes all cross-cutting concerns and governing context into
~1000-1500 tokens prepended to the bead description.

## When to Assemble

| Action | Behavior |
|--------|----------|
| `helix triage` | Assemble digest for every new bead |
| `helix evolve` | Assemble digest for beads it creates or modifies |
| `helix polish` | Refresh digest against current upstream state |
| `helix build` | Read digest from bead (do not reassemble) |
| `helix review` | Read digest to verify consistency |

## Assembly Algorithm

1. **Principles**: Load active principles per
   `workflows/references/principles-resolution.md`. Include the full list
   as a compact single line (separator: ` · `).

2. **Stack**: Load active concerns per
   `workflows/references/concern-resolution.md`. Summarize selected
   components as `name | name | name`.

3. **Practices**: Load merged practices (library + project overrides).
   Summarize as key conventions (separator: ` · `). Prioritize:
   linter, formatter, testing, and language-config practices.

4. **ADRs**: Find ADRs relevant to the bead's scope:
   - Match ADR `Related` field against the bead's `spec-id` chain
   - Match ADR topic against the bead's `area:*` labels
   - For each relevant ADR: extract the decision statement and one-line
     rationale. Do not include alternatives or exploration.

5. **Governing spec**: Load the artifact referenced by `spec-id`.
   Extract:
   - The specific requirement or acceptance criterion this bead addresses
   - Key constraints relevant to implementation
   - Do not include the full spec — just the governing clause.

6. **Format**: Assemble into XML-tagged block (see format below).

7. **Write**: Prepend the `<context-digest>` block to the bead's
   `description` field. If a digest already exists, replace it.

## Digest Format

```xml
<context-digest>
<principles>Principle 1 · Principle 2 · Principle 3</principles>
<concerns>Component 1 | Component 2 | Component 3</concerns>
<practices>Practice 1 · Practice 2 · Practice 3</practices>
<adrs>ADR-NNN decision summary · ADR-NNN decision summary</adrs>
<governing>FEAT-NNN §X.Y — key requirement or constraint</governing>
</context-digest>
```

Each XML element is optional — omit it if there is no relevant content
(e.g., omit `<adrs>` if no ADRs are relevant, omit `<concerns>` if no
stack is declared).

## Token Budget

| Section | Target | Notes |
|---------|--------|-------|
| Principles | ~100 tokens | Full list, compact format |
| Stack | ~50 tokens | Component names only |
| Practices | ~200 tokens | Key conventions, not exhaustive |
| ADRs | ~200 tokens per ADR | Decision + rationale only |
| Governing | ~300 tokens | Specific clause, not full spec |
| **Total** | **~1000-1500 tokens** | Less than one upstream file read |

If the total exceeds 2000 tokens (many ADRs, many stacks), prioritize:
principles first, then stack/practices, then governing, then ADRs by
relevance. Truncate ADR summaries before dropping them entirely.

## Refresh at Polish Time

When `helix polish` encounters a bead with an existing
`<context-digest>`:

1. Re-run the assembly algorithm against current upstream state.
2. Compare each section against the existing digest.
3. If material changes exist:
   - Replace the `<context-digest>` block with the updated version.
   - Add a note to the bead: "Context digest refreshed: [what changed]".
4. If no changes: leave the digest untouched.

Material changes include: principle added/removed, concern changed,
practice overridden, ADR superseded, governing spec amended.

## Reading the Digest at Build Time

When `helix build` or `helix review` processes a bead with a
`<context-digest>`:

1. Parse the XML tags from the description.
2. Use the digest contents as authoritative context for this bead.
3. Do not redundantly read the upstream files that the digest summarizes.
4. If the digest is missing (legacy bead), fall back to reading upstream
   files directly.

Trust the digest — rely on `helix polish` to keep it current.
