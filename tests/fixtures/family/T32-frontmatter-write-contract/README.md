# T32 — skill rewrite preserves unknown frontmatter keys [HIGH RISK]

## Scenario

An existing PRD-001 has legacy frontmatter mixing the prior schema
keys (`depends_on:` at top level) with vendor-namespaced keys
(`x-team-owner:`). User asks the skill to "add a one-line summary
to the body" — a body-only edit. Per §2.5 the skill must
round-trip the frontmatter byte-equivalent: every unknown key
survives in the same position, no key gets translated incidentally.

## Why it matters

S8 review item. Without this, two agent runs on the same legacy PRD
produce different frontmatter shapes (some drop `depends_on:`, some
keep, some translate). The whole determinism guarantee of the design
breaks at the write boundary.

## What passes

- The PRD-001 file is rewritten (Write tool fires).
- After the rewrite, the frontmatter still contains:
  - `depends_on:` top-level key (legacy, untranslated).
  - `x-team-owner:` (vendor key, preserved).
  - `ddx.id:` and `ddx.type:` (runtime-managed, unchanged).
- The frontmatter must NOT contain a new `ddx.links:` key (the skill
  must not translate legacy keys on incidental edits per §2.5
  rule 2).
- The body MUST contain the requested one-line summary.

## What fails

- `depends_on:` stripped or moved.
- `x-team-owner:` dropped (unknown-key dropper).
- `ddx.links:` auto-generated from `depends_on:` (incidental
  translation forbidden).
- Body edit missing (skill misread the task).

## Risk

HIGH. Determinism at the write boundary is the foundation of the
whole linkage-relaxation contract.
