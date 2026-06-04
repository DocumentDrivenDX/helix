# T20 — skills/_data SKILL.md workaround (positive) [HIGH RISK]

- **Installed:** `helix-library` with `skills: ["skills/_data"]`
- **Risk:** high (untested-fallback-path)

## Scenario

T13 tests `plugin.json` with NO `skills` field. If Claude Code
rejects that, the documented fallback in FINAL plan risk #2 is to
ship a `skills/_data/SKILL.md` with a never-trigger frontmatter. T20
is the positive test for that fallback: install must succeed, the
SKILL.md must mount, and the skill must NEVER route on any prompt
(even an adversarially compound one).

## Why it matters

T13 alone tests only ONE of the two architecture-forking paths. If
T13 fails and the family pivots to the workaround, the workaround
itself is UNVERIFIED in the current matrix. T20 closes that gap.

## Pass signature

- Install exits 0.
- Filesystem: `~/.claude/plugins/helix-library/skills/_data/SKILL.md`
  exists.
- Compound prompt (list types + start discover + write ADR) produces
  NO Edit/Write/Bash tool_use and NO prose evidence of routing.

## Failure signatures

- Install fails → workaround not viable; library cannot ship.
- Skill routes on the prompt → workaround does not actually
  suppress routing; users get unexpected behavior.
