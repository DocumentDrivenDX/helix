---
title: "Rename \"authority order\" to \"abstraction hierarchy\""
slug: plan-2026-05-29-rename-authority-order
weight: 500
activity: "Design"
source: "02-design/plan-2026-05-29-rename-authority-order.md"
generated: true
---

> **Source identity** (from `02-design/plan-2026-05-29-rename-authority-order.md`):

```yaml
type: plan
status: proposed
created: 2026-05-29
owner: erik
```

# Rename "authority order" to "abstraction hierarchy"

## Why

A short survey found 109 occurrences of "authority order" across 56 files. The
phrase wraps two ideas:

1. A series of levels of abstraction: Vision → PRD → Feature Specs →
   Architecture/ADRs → Designs → Tests → Implementation Plans → Source Code.
   Each level captures the same product at a different granularity.
2. A precedence rule: when two levels disagree, the higher one wins
   ("higher layers govern lower layers").

"Authority order" carries the precedence rule via "authority" and the sequence
via "order", but it loses the underlying concept (the levels are *abstractions*
of each other, not commands of each other) and reads as command-and-control
governance.

"Abstraction hierarchy" captures both ideas in one phrase: "abstraction" names
the essence, "hierarchy" carries the precedence rule. It aligns with industry
vocabulary (Zachman rows, RUP abstraction levels, IEEE 1471 viewpoints) and
with existing project usage of "hierarchy" (101 occurrences in the codebase
already).

Alternative considered: "levels of abstraction" alone. Rejected because the
precedence rule needs separate wording every time the term is used; "hierarchy"
folds the rule into the noun.

## What changes

- The noun phrase: `authority order` → `abstraction hierarchy`.
  Hyphenated variant: `authority-order` → `abstraction-hierarchy`.
- The section heading: `## Authority Order` → `## Abstraction Hierarchy`.
- The anchor: `#authority-order` → `#abstraction-hierarchy`.
- The precedence sentence on the canonical page already reads "Higher layers
  govern lower layers"; no change needed.
- Cross-page links that use the old anchor: rewrite to the new anchor and add
  a Hugo `aliases` entry on the canonical page so external links to
  `#authority-order` keep working.

## What does NOT change

- "Authority" used in other contexts (e.g., "authority is missing",
  "stakeholder authority", "the operator authorizes the edit") stays.
- "Governance", "governing", "governs" stay.
- "Artifact hierarchy" and "the hierarchy" used loosely stay.
- File names: `workflows/artifact-hierarchy.md` keeps its name.
- The 8-level list itself (Vision through Source Code) stays unchanged.
- The semantics of higher governing lower stays unchanged.

## Scope

109 lines across 56 files. By tree:

| Tree | Files | Notes |
|---|---|---|
| `docs/helix/` (source artifacts) | ~14 | mirrored to `docs/website/content/artifacts/` by `publish-artifacts.py`; edit source, regenerate |
| `docs/website/content/` (curated) | ~13 | `why/`, `use/`, `reference/`, `skills/` |
| `workflows/` | ~6 | including `artifact-hierarchy.md`, `EXECUTION.md`, `QUICKSTART.md`, `REFERENCE.md`, `actions/*` |
| `skills/helix/SKILL.md` | 1 | the routing skill body |
| Top-level | 3 | `README.md`, `AGENTS.md`, `CLAUDE.md` |
| Generated mirrors | ~25 | `docs/website/content/artifacts/`, `docs/website/content/concerns/`, regenerated automatically |
| Historical plan docs | ~3 | including the two plans created today; either leave (history) or update (consistency) — see "Open question" |

## Execution order

Sequenced so the canonical home moves first, dependents follow, generators
re-run last.

1. **Canonical page first**:
   `docs/website/content/use/workflow/_index.md` — section heading, anchor, and
   sentence-level mentions. Add `aliases` entry so `#authority-order` deep
   links keep resolving.
2. **High-traffic curated pages**: `why/the-thesis.md`, `why/principles.md`,
   `skills/_index.md`, `reference/skills/_index.md`, `use/getting-started.md`,
   `use/claude-code-recipe.md`, `use/codex-recipe.md`, `use/databricks-recipe.md`,
   `use/manual-recipe.md`, `use/ddx-runtime.md`, `use/_index.md`,
   `why/_index.md`, `why/who-its-for.md`, `reference/glossary/_index.md`.
3. **Source artifacts** under `docs/helix/`: PRD, principles, FEATs, ADRs,
   contracts, technical designs, test plans, the worked-example homepage
   graph. (The mirrored pages under
   `docs/website/content/artifacts/` regenerate automatically.)
4. **Workflows**: `workflows/artifact-hierarchy.md` (heaviest concentration),
   `EXECUTION.md`, `QUICKSTART.md`, `REFERENCE.md`, `DDX.md`,
   `actions/*.md`, `activities/00-discover/artifacts/product-vision/prompt.md`,
   `concerns/hugo-hextra/practices.md`.
5. **Skill + top-level**: `skills/helix/SKILL.md`, `README.md`, `AGENTS.md`,
   `CLAUDE.md`.
6. **Regenerate**:
   `uv run scripts/generate-reference.py && uv run scripts/publish-artifacts.py && uv run scripts/publish-resources.py`.
7. **Run gates**: `just lint-prose`, `python3 scripts/check-prose-redundancy.py`,
   `just check-website-links`, `bash tests/validate-website-generated.sh`,
   `bash tests/validate-deploy-artifacts.sh`.

Logical commit groups:

- Commit 1: canonical page + curated content.
- Commit 2: source artifacts (regenerates the mirrors).
- Commit 3: workflows + skill + top-level + regenerator runs.

## Verification

After all commits land:

- `grep -rln 'authority order\|authority-order' docs/website/content docs/helix workflows skills .vale README.md AGENTS.md CLAUDE.md` returns nothing (or only the historical plan docs if we decided to leave them).
- The internal anchor `#abstraction-hierarchy` resolves on the canonical page.
- The `aliases` entry on the canonical page redirects `#authority-order` deep
  links to the new anchor.
- `validate-website-generated.sh` reports 0 drift after the regenerator pass.
- The CI Website workflow stays green.

## Rollback

`git revert` the three commits. The aliases revert with them; no external
redirect or DNS change is involved.

## Risks

1. **Bulk replace catches unintended matches**. Mitigation: word-boundary
   replacement, manual review of each diff, and a final grep for the old
   phrase before commit.
2. **Generated mirrors drift if the regenerator misses a path**. Mitigation:
   the drift gate (`validate-website-generated.sh`) is the safety net; the
   regenerators wipe-and-rebuild their destination dirs, so any source-side
   rename mirrors deterministically.
3. **External links to the old anchor break**. Mitigation: Hugo
   `aliases:` entry on the canonical page; `#authority-order` continues to
   resolve to the new heading.
4. **Linguistic awkwardness in prose around the rename**. Some sentences read
   naturally with "authority order" (`when artifacts disagree, the authority
   order resolves up`) but stilted with the literal swap (`the abstraction
   hierarchy resolves up` is fine; some other sentences will need a small
   reshuffle). Mitigation: read each touched paragraph aloud after the swap;
   tighten where it does not flow.
5. **Mixed terminology during the transition**. Mitigation: commit groups are
   each self-contained; do not push a half-done rename.
6. **Skill activation phrasing**. `skills/helix/SKILL.md` is what agents read
   to route. If "authority order" is part of an activation phrase or test
   fixture (`tests/install/shared/expected-modes.txt` and similar), the
   rename must not break activation. Mitigation: grep
   `tests/install/` and the skill fixture files before the skill commit.

## Open question

Do we update the **two planning artifacts** created today
(`plan-2026-05-29-prose-quality-pass.md` and
`plan-2026-05-29-curated-page-scopes.md`) that reference `authority order` in
their text, or leave them as historical record? My instinct is to update them,
since these are still active plans rather than completed history. If we treat
plans as immutable once filed, leave them; either way, declare it explicitly
so the decision is reproducible.

## Out of scope

- Other naming cleanups (e.g., re-naming "concerns", "beads", "context
  digests"). Each is a separate rename plan.
- A general anti-jargon pass on the catalog. Different work.
- Promotion of any Vale rule to error level. Owned by the prose-quality plan.
