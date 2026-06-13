---
title: "Prose-quality pass — evaluate and implement the expanded Vale findings"
slug: plan-2026-05-29-prose-quality-pass
weight: 700
activity: "Design"
source: "02-design/plan-2026-05-29-prose-quality-pass.md"
generated: true
---

> **Example from HELIX's own docs.** This generated page comes from `docs/helix/`. Use it to see the method in practice; start with the [artifact-type catalog](/artifact-types/) for reusable templates. Historical plans and reports may describe retired architecture.

> **Source identity** (from `02-design/plan-2026-05-29-prose-quality-pass.md`):

```yaml
type: plan
status: proposed
created: 2026-05-29
owner: erik
```

# Prose-quality pass — evaluate and implement the expanded Vale findings

## Context

The Helix Vale style covered 6 tokens (delve/leverage/seamless + em-dash +
honest/interesting). `just lint-prose` stayed green while the hand-authored
narrative carried throat-clearing, weak hedges, passive voice, and
cross-file paragraph duplication. Commit `b24cb3aa` added four warning-level
rules — `Wordiness`, `Hedges`, `PassiveVoice`, `SentenceLength` — plus a
cross-file redundancy detector (`scripts/check-prose-redundancy.py`) wired
as `just check-prose-redundancy`. The findings below are from the first
clean run; the plan turns them into bounded fix work.

## Baseline findings (first run)

### Vale — 95 warnings across 21 files

| Rule | Count |
|---|---|
| `Helix.PassiveVoice` | 75 |
| `Helix.Hedges` | 19 |
| `Helix.Wordiness` | 1 |
| `Helix.SentenceLength` | 0 |

Top files by warning count:

| File | Warnings |
|---|---|
| `why/principles.md` | 13 |
| `why/the-thesis.md` | 9 |
| `why/who-its-for.md` | 9 |
| `reference/glossary/concepts.md` | 7 |
| `use/workflow/concerns.md` | 7 |
| `why/_index.md` | 7 |
| `use/workflow/_index.md` | 6 |
| `platforms/_index.md` | 5 |
| `use/workflow/methodology.md` | 5 |
| `reference/glossary/tracker.md` | 4 |

The `why/` argument cluster is the heaviest — expected, because those pages
carry the most explanatory prose.

### Redundancy — 7 cross-file pairs ≥ 0.25 Jaccard similarity

| Score | Pair |
|---|---|
| 1.00 | `skills/_index.md` ↔ `reference/skills/_index.md` (identical paragraph) |
| 0.70 | `why/principles.md` ↔ `why/the-thesis.md` (verification-exit-gate explanation) |
| 0.43 | `use/workflow/methodology.md` ↔ `why/the-thesis.md` (build-side guards) |
| 0.39 | `use/workflow/methodology.md` ↔ `why/principles.md` (build-side guards) |
| < 0.39 | three more pairs (run the script to see) |

The verification-gate / build-side-guards idea is restated three ways across
`why/the-thesis`, `why/principles`, and `use/workflow/methodology`. Pick one
canonical location and link to it from the other two.

## Evaluation criteria

Before rewriting, classify each finding so we do not over-edit prose that
already earns its words.

For every `Hedges` and `Wordiness` hit:
- **Drop** if the word adds no information (`just`, `actually`, `very`,
  `simply` are usually filler).
- **Keep** if the word carries a real contrast or limit (`just one ask`
  contrasting against a multi-step flow; `actually` after a misconception).
- **Replace** if Wordiness suggests a tighter form (`in order to → to`).

For every `PassiveVoice` hit:
- **Rewrite to active** when the actor matters and is known
  (`the gate is enforced` → `the build exit gate enforces`).
- **Keep passive** when the actor is unknown, irrelevant, or the object is
  genuinely the subject of interest (`the artifact is regenerated on every
  push` is fine — the regeneration is the point).

For every `SentenceLength` hit:
- **Split** when the sentence carries more than one claim.
- **Keep** when the length is structural (a single complex claim with
  parallel clauses earns its length).

For every redundancy pair:
- Pick the page where the explanation belongs by topic
  (`why/the-thesis.md` owns the thesis, `why/principles.md` owns the
  principle catalog, `use/workflow/methodology.md` owns the procedure).
- Trim the other pages to a one-sentence reference + relative link.
- Re-run the redundancy script to confirm the pair drops below threshold.

## Phased implementation

### Phase 1 — redundancy consolidation (highest leverage, smallest LOC)

Seven pairs, mostly the verification-gate explanation and the skills-list
duplicate. Fixing these collapses ~30 sentences of restated content and
incidentally reduces some of the passive-voice and hedge counts (fewer
words → fewer flagged words).

Exit: `just check-prose-redundancy` returns 0 pairs at default 0.25 threshold.

### Phase 2 — Wordiness to zero, promote to error

Only 1 finding. Fix it, then bump `.vale/styles/Helix/Wordiness.yml` from
`warning` to `error`. Wordiness substitutions are deterministic, so the
forward gate prevents regression.

Exit: 0 `Helix.Wordiness` warnings; level set to `error`.

### Phase 3 — hedges, file by file (top offenders first)

19 hits, mostly clustered. Walk the top files (`why/principles.md`,
`why/the-thesis.md`, `why/who-its-for.md`) and apply the
keep/drop/replace rubric per occurrence. Hedges are judgment calls per
sentence; do not blanket-strip.

Exit: each hand-authored file under 3 `Helix.Hedges` warnings; remaining
hits documented inline (the place names a real contrast).

### Phase 4 — passive voice, top files first

75 hits is the largest bucket and the most prose-shaping work. Sequence by
file weight (heaviest first). For each hit, rewrite to active only when the
actor matters; otherwise mark accepted.

Exit: 50% reduction (≤ 38 warnings) after the first pass; 80% reduction (≤
15) after the second. Reaching 0 is not realistic — some passive
constructions earn their place.

### Phase 5 — sentence length

0 hits in the first run, but the regex is approximate (`[A-Z][^.!?\n]*?
(?:\s+\S+){30,}[^.!?\n]*[.!?]`). Tighten the regex once we have a real
positive case; promote to error only after the regex is calibrated.

Exit: no change to the file count unless the tightened regex surfaces real
positives.

## Promotion criteria (warning → error)

Each rule promotes to `level: error` only when:
1. Its count is at zero across the hand-authored tree.
2. The CI Website workflow has run green for at least one push at zero.

This prevents promoting a rule the moment it hits zero locally and then
breaking CI on a separate writer's branch.

## Tooling follow-ups (not blocking the prose work)

- The `Helix.SentenceLength` regex is approximate. Once a real long-sentence
  hit appears, refine to a Vale 3 `metric` rule (`extends: metric`) so word
  count is exact instead of regex-counted.
- `PassiveVoice` token list catches `be + -ed/-en` plus a curated irregular
  list. Audit a couple of false positives ("are needed") and add a small
  excludes list if they recur.
- The redundancy script uses paragraph trigram shingles + Jaccard. If pairs
  surface inside a single file (intra-file redundancy), extend it to also
  compare paragraphs within the same file behind a flag.

## Verification

- `just lint-prose` — should report monotonically decreasing warnings after
  each phase commit.
- `just check-prose-redundancy` — should reach 0 cross-file pairs after
  Phase 1.
- The Website CI workflow tracks `just lint-prose`; promoting a rule to
  error guards against regression in subsequent pushes.

## Out of scope

- The generated trees (`artifacts/`, `concerns/`, `artifact-types/`,
  `research/`) are projections of upstream sources and are excluded by
  `.vale.ini`. Their prose quality is governed at source (`workflows/`,
  `docs/helix/`, `docs/resources/`), and extending these checks there is a
  follow-up plan.
- LLM-assisted semantic audit via the `avoid-ai-writing` skill. The
  mechanized rules above are deterministic and fast; the skill audit is
  slower and non-deterministic, and is better as a periodic review than a
  per-commit gate.
