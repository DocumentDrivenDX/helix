---
title: "Rename \"authority order\" to \"authority hierarchy\""
slug: plan-2026-05-29-rename-authority-order
weight: 710
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
revisions:
  - codex-review-2026-05-29
```

# Rename "authority order" to "authority hierarchy"

## Why

A survey found 109 occurrences of "authority order" across 56 files. The
phrase wraps two ideas:

1. A series of governing artifacts: Vision → PRD → Feature Specs →
   Architecture/ADRs → Designs → Tests → Implementation Plans → Source Code.
2. A precedence rule: when two governing artifacts disagree, the higher one
   wins ("higher artifacts govern lower").

"Authority order" carries the precedence rule via "authority", but "order"
reads as a sequence rather than a structure of governance, and the phrase is
mechanical.

"Authority hierarchy" keeps the governance semantics, drops the awkward
"order", and aligns with project usage of "hierarchy" (101 occurrences in the
codebase, three of them as "authority hierarchy" already). The long form on
first use in any document is "artifact authority hierarchy"; subsequent uses
are "authority hierarchy".

Two alternatives were considered and rejected:

- **"Abstraction hierarchy"** describes the *shape* but not the *rule*. The
  load-bearing point of the concept is what wins under conflict, not what
  level of abstraction a document occupies. Under "abstraction hierarchy",
  "up" reads as more abstract rather than more authoritative, so the
  precedence rule weakens. Codex review surfaced this and several specific
  sentences where "abstraction hierarchy" reads worse than "authority order".
- **"Specification hierarchy"** is too narrow. Vision is intent more than
  specification; Source Code is output, not specification. Neither end of
  the list reads as "spec".

"Levels of abstraction" is useful as descriptive prose ("each level is a
greater abstraction than the one below"), not as the noun phrase for the
concept.

## What changes

- The noun phrase: `authority order` → `authority hierarchy`.
  Hyphenated variant: `authority-order` → `authority-hierarchy`.
- First use in any document: `artifact authority hierarchy`.
- The section heading: `## Authority Order` → `## Authority Hierarchy`.
- The anchor: `#authority-order` → `#authority-hierarchy`.
- Several sentences need a small rewrite, not a literal token swap. Examples
  flagged by codex review:
  - `Changes can enter at any activity. The same authority order resolves
    them` → `… The same authority hierarchy determines which artifact
    governs.`
  - `Apply updates in authority order` in `skills/helix/SKILL.md` → `Apply
    updates from the highest-authority artifact down.` (Do not say "in
    authority hierarchy".)
  - `When artifacts disagree, HELIX resolves conflicts up the order` →
    `When artifacts disagree, HELIX escalates to the higher-authority
    artifact.`
  - `workflows/artifact-hierarchy.md` opening "explains authority order,
    artifact relationships…" → `explains the authority hierarchy, artifact
    relationships…`.
- Compatibility for old fragment links: add an explicit HTML anchor next to
  the new heading so deep links to `#authority-order` keep working. Hugo
  `aliases:` only redirects page-level URLs; fragments are browser-side and
  unaffected. Two approaches, in increasing sturdiness:

  ```markdown
  <a id="authority-order"></a>
  ## Authority Hierarchy
  ```

  The raw anchor renders because `markup.goldmark.renderer.unsafe: true` is
  set in `website/hugo.yaml`. Both `#authority-order` and
  `#authority-hierarchy` will navigate to the heading. **Caveat surfaced by
  codex review**: Hextra applies a sticky-header offset to its generated
  heading anchors via a CSS scroll-margin / offset span; the bare `<a id>`
  does not get that offset, so the scroll position lands a few pixels
  differently for the legacy fragment than for the canonical one. Sturdier
  approach: add a small `legacy-anchor` shortcode (or a raw `<span>` matching
  Hextra's offset pattern) and browser-test both fragments in a deployed
  page before declaring the migration done.

## What does NOT change

- "Authority" used in other contexts (e.g., "authority is missing",
  "stakeholder authority", "the operator authorizes the edit") stays.
- "Governance", "governing", "governs" stay.
- "Artifact hierarchy" used in `workflows/artifact-hierarchy.md` as the file
  name and a related concept stays — the file describes the same hierarchy.
- The 8-level list itself (Vision through Source Code) stays unchanged.
- The semantics of higher governing lower stay unchanged.

## Scope (expanded after codex review)

109 lines across 56 files in the original grep, plus additional trees codex
flagged that need an explicit pass before the rename can be called complete:

| Tree | Files | Notes |
|---|---|---|
| `docs/helix/` (source artifacts) | ~14 | mirrored to `docs/website/content/artifacts/` by `publish-artifacts.py` |
| `docs/website/content/` (curated) | ~13 | `why/`, `use/`, `reference/`, `skills/` |
| `workflows/` | ~6 | including `artifact-hierarchy.md`, `EXECUTION.md`, `QUICKSTART.md`, `REFERENCE.md`, `actions/*` |
| `skills/helix/SKILL.md` | 1 | the routing skill body |
| Top-level | 3 | `README.md`, `AGENTS.md`, `CLAUDE.md` |
| `docs/demos/` | TBD per audit | demo session JSON + assertions; many are golden fixtures |
| `docs/resources/` | TBD per audit | research notes; expect 1–2 hits |
| `tests/refresh/`, `tests/install/` | TBD per audit | fixture expectations |
| `.github/copilot-instructions.md` | 1 | agent-facing instructions |
| `scripts/generate-reference.py` | 1 | generator may emit the phrase into rendered pages |
| Generated mirrors | ~25 | `docs/website/content/artifacts/`, `docs/website/content/concerns/`, regenerated automatically |
| Historical plan docs | ~3 | including the two plans created today |

### Demo fixture audit (gated before the rename touches them)

`docs/demos/*/session.jsonl` and `tests/install/shared/expected-modes.txt`
and similar fixtures are golden transcripts. Renaming inside them can break
the validate-demos drift gate or invalidate recorded evidence. The audit
step:

1. `grep -ln 'authority order\|authority-order' docs/demos tests/install
   tests/refresh` returns the affected fixtures.
2. For each one, classify:
   - **Replayable** (no historical claim): rename inline + regenerate cast.
   - **Golden / historical**: leave the fixture as recorded; record the
     decision in the rename commit message.

## Execution order (revised per codex)

The previous plan put curated pages in the same commit as the canonical page,
and left the skill + top-level READMEs for last. Codex flagged that
agent-facing semantics should change atomically: split between commits 1, 2,
and 3 risks the skill routing the agent to one term while the workflow page
defines another.

Revised order:

1. **Commit 1 — canonical page + compatibility anchor**:
   `docs/website/content/use/workflow/_index.md`. Rename section heading,
   anchor, and sentence-level mentions. Add the `<a id="authority-order"></a>`
   line directly above the new heading.
2. **Commit 2 — agent-facing atomically**:
   `workflows/artifact-hierarchy.md`, `workflows/EXECUTION.md`,
   `workflows/QUICKSTART.md`, `workflows/REFERENCE.md`, `workflows/DDX.md`,
   `workflows/actions/*.md`,
   `workflows/activities/00-discover/artifacts/product-vision/prompt.md`,
   `workflows/concerns/hugo-hextra/practices.md`, `skills/helix/SKILL.md`,
   `README.md`, `AGENTS.md`, `CLAUDE.md`,
   `.github/copilot-instructions.md`. Same commit so agent-side semantics
   move together.
3. **Commit 3 — source artifacts + generated mirrors**:
   `docs/helix/` PRD, principles, FEATs, ADRs, contracts, technical designs,
   test plans, the worked-example homepage graph. Run regenerators
   (`uv run scripts/generate-reference.py && uv run scripts/publish-artifacts.py
   && uv run scripts/publish-resources.py`) in the same commit so the
   `docs/website/content/artifacts/` mirrors update together.
4. **Commit 4 — curated pages**: `why/the-thesis.md`, `why/principles.md`,
   `skills/_index.md`, `reference/skills/_index.md`, `use/getting-started.md`,
   the recipes, `use/_index.md`, `why/_index.md`, `why/who-its-for.md`,
   `reference/glossary/_index.md`. (May be folded into Commit 1 if size is
   small; review before splitting.)
5. **Run gates** in the same push: `just lint-prose`,
   `python3 scripts/check-prose-redundancy.py`, `just check-website-links`,
   `bash tests/validate-website-generated.sh`,
   `bash tests/validate-deploy-artifacts.sh`,
   `bash tests/validate-demos.sh` (if any session fixtures were touched).

## Verification (expanded per codex)

After all commits land:

- The grep target must include every tree the rename touches **and every
  variant of the phrase**. Codex flagged that the prior plan's grep was
  case-sensitive and only matched `authority order|authority-order`,
  missing `Authority Order`, `authority-ordered`, and `authority ordering`.
  It also missed the committed `.cast` files under `website/static/demos/`.
  Full final-check command:

  ```sh
  grep -RnliE 'authority[- ]order(ed|ing)?' \
    docs/website/content docs/helix workflows skills \
    docs/demos docs/resources tests/refresh tests/install \
    .github .vale README.md AGENTS.md CLAUDE.md \
    scripts/generate-reference.py website/static/demos \
    | grep -v plan-2026-05-29-rename-authority-order.md \
    | grep -v plan-2026-05-29-prose-quality-pass.md \
    | grep -v plan-2026-05-29-curated-page-scopes.md
  ```

  Returns nothing if the rename is complete (the three historical plans are
  exempt; see the open question).

- The internal anchor `#authority-hierarchy` resolves on the canonical page.
- The `<a id="authority-order"></a>` compatibility anchor resolves the same
  scroll position. Spot-check in a real browser since this is the part Hugo
  `aliases:` does not handle.
- `validate-website-generated.sh` reports 0 drift after the regenerator pass.
- `validate-demos.sh` returns OK if any demo fixture was renamed.
- The CI Website workflow stays green.

## Rollback

`git revert` the four commits in reverse order. Aliases, the compatibility
anchor, and the renamed mirrors revert together. No external redirect or DNS
change is involved.

## Risks

1. **Bulk replace catches unintended matches**. Mitigation: word-boundary
   replacement; manual review of each diff; the final grep above.
2. **Generated mirrors drift if the regenerator misses a path**. Mitigation:
   the drift gate (`validate-website-generated.sh`) is the safety net; the
   regenerators wipe-and-rebuild their destination dirs.
3. **Hugo `aliases:` does not preserve fragment anchors** — the page alias
   redirects `/foo/` but `#authority-order` is browser-side. Mitigation: use
   an explicit `<a id="authority-order"></a>` adjacent to the new heading.
   Verify in a deployed page, not just via curl, because some link checkers
   only see the heading-generated `id` attribute.
4. **Linguistic awkwardness in prose around the rename**. Codex flagged the
   sentences listed in "What changes". Mitigation: rewrite the listed
   sentences explicitly; read each touched paragraph after the swap.
5. **Skill / agent-facing terminology split across commits**. Mitigation:
   Commit 2 puts the skill, workflows, agent-facing READMEs, and copilot
   instructions in one commit so an agent reading mid-transition never sees
   one term in the skill and another in the workflow doc.
6. **Demo fixtures and test expectations are golden transcripts**. Mitigation:
   the demo audit step above. Decisions recorded in the relevant commit
   message.
7. **Generators emit the phrase**. `scripts/generate-reference.py` may
   produce the phrase into rendered concern or artifact-type pages.
   Mitigation: grep the generator scripts before Commit 3 and fix at source.

## Open question (unchanged)

Do we update the **three planning artifacts** created today
(`plan-2026-05-29-prose-quality-pass.md`,
`plan-2026-05-29-curated-page-scopes.md`, and this plan)? My instinct is to
update them, since they are still active plans rather than completed
history. Either way, declare the decision in the rename commit messages.

## Out of scope

- Other naming cleanups ("concerns", "beads", "context digests"). Each is a
  separate plan.
- A general anti-jargon pass on the catalog. Different work.
- Promotion of any Vale rule to error level. Owned by the prose-quality plan.

## Review log

- 2026-05-29: codex advisory review. Recommended `authority hierarchy` over
  `abstraction hierarchy` and flagged the Hugo-aliases / fragment issue, the
  missed verification scope, demo fixture risk, and a sounder commit
  sequence. Incorporated into this revision.
