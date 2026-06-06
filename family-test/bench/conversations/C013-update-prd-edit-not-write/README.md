# C013 — "Update the PRD to add a new requirement" (guided, exploratory)

**Category:** conversation library (plan §1.5 row C013)
**Phase:** P5b
**Tier:** exploratory

## Scenario

Workspace state:
- `.helix.yml` marker has helix active.
- `docs/helix/01-frame/PRD-001-coffee-ordering.md` exists with
  approved frontmatter (id, type, status, ddx.spec_id, ddx.links).

Operator says: "Update PRD-001 to add a new requirement: support
gift-card payments at checkout."

## Expected behaviour

Per plan §1.5 row C013: the skill MUST modify the existing PRD via
Edit (not Write — Write would replace the whole file and risk
frontmatter loss). The Read-then-Edit ordering is the structural
contract; it also surfaces the frontmatter the agent must preserve
byte-equivalent (ddx.links, status, id).

Discriminator: `read_before_write` asserts a Read targeting
`PRD-001-coffee-ordering.md` appears at an earlier stream index than
the first Edit (or Write) targeting the same file.

## Why exploratory

The read-before-write contract for updates is a strong heuristic, but
agents under autonomy=guided can legitimately ask first (delaying
Read), then Read+Edit, OR can re-author the file as Write+content
that happens to preserve frontmatter. The "Edit not Write" wording is
correct in the canonical case but soft when measured strictly.
Marked exploratory per plan §5.

## Negative control

Plugin removed (`plugins_remove: [methodology-product]`). Without the
helix methodology plugin, the skill cannot engage; the agent may
update the PRD from training but is significantly less likely to Read
the file first (the marker-aware "preserve frontmatter, edit don't
overwrite" rule is helix-specific). The matcher's strict ordering
verdict flips from present to absent.
