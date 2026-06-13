---
title: "Curated page scopes — lock the document boundaries before the prose pass"
slug: plan-2026-05-29-curated-page-scopes
weight: 690
activity: "Design"
source: "02-design/plan-2026-05-29-curated-page-scopes.md"
generated: true
---

> **Example from HELIX's own docs.** This generated page comes from `docs/helix/`. Use it to see the method in practice; start with the [artifact-type catalog](/artifact-types/) for reusable templates. Historical plans and reports may describe retired architecture.

> **Source identity** (from `02-design/plan-2026-05-29-curated-page-scopes.md`):

```yaml
type: plan
status: proposed
created: 2026-05-29
owner: erik
supersedes: docs/helix/02-design/plan-2026-05-29-prose-quality-pass.md (Phase 1 redundancy work)
```

# Curated page scopes — lock the document boundaries before the prose pass

## Why this plan

The earlier prose-quality plan jumped to per-pair canonical assignment for the
seven redundant paragraph pairs. That had to invent ad-hoc rationale for each
pair. The structural problem is upstream: **most hand-authored pages do not
have a clear, necessary, non-overlapping scope today.** Until each page owns
exactly one job, every duplicate is a coin flip. This plan locks the scopes
first; the duplicate-resolution then falls out of the scopes.

## Dynamic content — single canonical location per tree

These trees are projections of upstream sources. Each has exactly one source
and one site location; canonicality is automatic. No hand-authored page may
restate their content — link instead.

| Site location | Source | Generator |
|---|---|---|
| `/artifacts/` | `docs/helix/` | `scripts/publish-artifacts.py` |
| `/artifact-types/` | `workflows/activities/<phase>/artifacts/<slug>/` | `scripts/generate-reference.py` |
| `/concerns/` | `workflows/concerns/` | `scripts/generate-reference.py` |
| `/research/` | `docs/resources/` | `scripts/publish-resources.py` |
| `/demos/*.cast` | `docs/demos/<slug>/session.jsonl` | `scripts/demos/render_session.py` (in CI) |

## Two cross-cutting canonical-home decisions

These two pieces of content recur across many pages and need a single home
before scopes can be assigned:

| Concept | Canonical home | Everyone else |
|---|---|---|
| **"What HELIX is"** (the methodology-layer + catalog + skill elevator pitch) | `why/the-thesis.md` | Page-specific framing only — no restatement; link to thesis if context is needed. |
| **The seven activities** (the names, what each does, what artifacts each owns) | `reference/glossary/activities.md` | One-sentence reference + link. |

If those two single-source rules hold, ~80% of the cross-page restatement
collapses.

## Scope inventory — 26 hand-authored pages

For each page: **Scope** (one sentence — what the page is for), **Owns**
(content that lives here exclusively), **Out of scope** (what to send
elsewhere).

### Top-level

#### `_index.md` (homepage)
- **Scope:** First-30-seconds orientation. Hero, sub-claim, four action cards.
- **Owns:** the hero, the loop figure, the action cards.
- **Out of scope:** any "what HELIX is" paragraphs beyond the hero subtitle; any feature lists; principles.

#### `install/_index.md`
- **Scope:** Pick the runtime and find its install guide.
- **Owns:** the cards for each runtime install path.
- **Out of scope:** "what HELIX is" (link to thesis); the runtime *comparison* (that's `platforms/`).

#### `platforms/_index.md`
- **Scope:** Compare the runtimes — which one to pick and why.
- **Owns:** the runtime comparison matrix; DDx-as-reference-runtime framing.
- **Out of scope:** "what HELIX is"; the install procedure (link to `install/`); the DDx full description (link to `use/ddx-runtime.md`).

#### `skills/_index.md`
- **Scope:** What HELIX skills are — the single alignment-and-planning skill, what artifacts it covers, what it does.
- **Owns:** the numbered artifact-coverage list; the "what is a skill" definition.
- **Out of scope:** invocation reference (that's `reference/skills/`); methodology.

### `why/` — the argument (4 content pages + section landing)

#### `why/_index.md`
- **Scope:** Section landing. Three-sentence framing + cards to the four pages.
- **Owns:** nothing canonical.
- **Out of scope:** the thesis itself; principles list; problem statement.

#### `why/the-thesis.md` — **CANONICAL HOME for "what HELIX is"**
- **Scope:** The central claim: HELIX is the methodology layer (catalog + alignment skill); runtime is separate; structural commitments (concerns propagate once; build-exit gate; converge loop).
- **Owns:** the methodology-layer claim; the artifact-impact contract claim; the verification-exit-gate claim; the convergence-loop claim.
- **Out of scope:** the harness list (link to methodology); the eight-principle catalog (link to principles); the problem statement (link to the-problem).

#### `why/principles.md`
- **Scope:** Catalog of the eight load-bearing principles, one per H2.
- **Owns:** each principle's name, statement, and one-line rationale.
- **Out of scope:** restating the thesis; procedural detail (each principle links to its `use/workflow/` page for the procedure).

#### `why/the-problem.md`
- **Scope:** What's broken with the current three approaches when AI agents are in the loop.
- **Owns:** the problem statement; the three-approaches breakdown.
- **Out of scope:** HELIX's solution (link to thesis).

#### `why/who-its-for.md`
- **Scope:** Audience filter — who benefits, who overpays.
- **Owns:** the team-shape rubric.
- **Out of scope:** what HELIX is; principles.

### `use/` — the how-to layer (5 recipes + workflow subsection + section landing)

#### `use/_index.md`
- **Scope:** Section landing. Cards to the recipes + workflow.
- **Owns:** nothing canonical.
- **Out of scope:** procedure; methodology restatement.

#### `use/getting-started.md`
- **Scope:** Minimum-viable-adoption walk-through.
- **Owns:** the numbered first-time-user steps.
- **Out of scope:** per-runtime specifics (link to recipes).

#### `use/claude-code-recipe.md`, `use/codex-recipe.md`, `use/databricks-recipe.md`, `use/manual-recipe.md`, `use/ddx-runtime.md`
- **Scope:** Runtime-specific procedure: install, invoke, use HELIX from that runtime.
- **Owns:** the install commands and recipes for that runtime.
- **Out of scope:** what HELIX is; methodology specifics; comparison to other runtimes (that's `platforms/`).

#### `use/workflow/_index.md` — **CANDIDATE FOR ABSORPTION**
- **Current state:** opens with the seven-activities enumeration and overlaps with methodology.md on the authority-hierarchy paragraph.
- **Proposal:** keep as a thin subsection landing (two sentences + cards to methodology and concerns) — OR absorb into methodology.md and drop the separate `_index.md`. I recommend the absorb-and-drop because the current page does not earn a distinct purpose.

#### `use/workflow/methodology.md` — **CANONICAL HOME for the HELIX procedure**
- **Scope:** How to run HELIX: the activities flow, the authority hierarchy, alignment review, build-exit gate (including the harness list), convergence loop.
- **Owns:** the procedural detail; the canonical harness list (Playwright / HTTP / CLI / terminal / integration).
- **Out of scope:** "what HELIX is"; principle statements (link to principles); the seven-activity names enumerated (link to glossary/activities).

#### `use/workflow/concerns.md` — **CANONICAL HOME for the Concerns concept (procedure)**
- **Scope:** How concerns work in practice — declaration, the Artifact Impact section, the knowledge chain.
- **Owns:** the Artifact Impact definition + example; the knowledge-chain diagram.
- **Out of scope:** the claim that concerns matter (that's the thesis); per-concern detail (that's `/concerns/`, generated).

### `reference/` — lookup (5 content pages + 2 section landings)

#### `reference/_index.md`
- **Scope:** Section landing. Cards to glossary, skills, demos.
- **Owns:** nothing canonical.

#### `reference/skills/_index.md` — **NEEDS A DISTINCT SCOPE OR SHOULD MERGE**
- **Current state:** near-duplicate of `/skills/` (1.00 paragraph similarity).
- **Proposal A (preferred):** Reference page for invocation — modes, the routing table, the activation phrasing, examples. Opens with one line linking back to `/skills/` for orientation.
- **Proposal B:** Merge into `/skills/` and drop the reference entry; the reference menu loses a card. Cleaner if there is not enough invocation-reference content to fill a page.
- **Decide based on:** the actual length of the technical invocation reference after we write it. If under ~30 lines, Proposal B is better.

#### `reference/glossary/_index.md`
- **Scope:** Glossary landing. Cards.
- **Owns:** nothing canonical.

#### `reference/glossary/activities.md` — **CANONICAL HOME for the seven activities**
- **Scope:** Catalog: each activity's name, purpose, key artifact types, location in the loop.
- **Owns:** the activity-by-activity catalog.
- **Out of scope:** "what HELIX is."

#### `reference/glossary/concepts.md`
- **Scope:** Definitions of HELIX concepts (artifact, bead, concern, authority hierarchy, context digest, etc.).
- **Owns:** the per-concept definitions.
- **Out of scope:** procedural use of the concepts (link to use/workflow).

#### `reference/glossary/tracker.md`
- **Scope:** Definitions of tracker primitives (bead, queue, label, etc.).
- **Owns:** the tracker-term definitions.

#### `reference/demos/_index.md`
- **Scope:** The demo reels page.
- **Owns:** the embedded reels + their short captions.

## How the 7 duplicate pairs resolve under these scopes

| Pair | Canonical (per scope) | Other page action |
|---|---|---|
| `skills/_index.md` ≡ `reference/skills/_index.md` (1.00) | `/skills/` owns orientation + the artifact list. | `/reference/skills/` becomes invocation reference (Proposal A) or is merged into `/skills/` (Proposal B). |
| `why/the-thesis.md` ↔ `why/principles.md` (0.70, gate paragraph) | `why/the-thesis.md` owns the **claim** that the gate matters. | `why/principles.md` keeps one principle sentence linking out. |
| `use/workflow/methodology.md` ↔ `why/the-thesis.md` (0.43, harness list) | `methodology.md` owns the **harness list and procedure**. | `the-thesis.md` keeps the claim only — no harness list. |
| `use/workflow/methodology.md` ↔ `why/principles.md` (0.39, harness list) | Same as above. | Same as above. |
| `use/workflow/concerns.md` ↔ `why/the-thesis.md` (0.31, artifact-impact contract) | `concerns.md` owns the **definition + example**. | `the-thesis.md` keeps the **claim** that concerns carry the contract. |
| `platforms/_index.md` ↔ `use/ddx-runtime.md` (0.28, DDx description) | `use/ddx-runtime.md` owns the **DDx description + procedure**. | `platforms/_index.md` keeps the **comparison context** only. |
| `use/workflow/_index.md` ↔ `use/workflow/methodology.md` (0.27, authority hierarchy) | `methodology.md` owns the **procedural rule**. | `_index.md` either keeps a one-line reference or is absorbed (see absorption candidate above). |

Hidden duplicates the redundancy scanner did not catch (because the
paragraphs were under the 15-word minimum or split across short paragraphs)
that the scopes resolve in the same direction:

- The "HELIX is the methodology layer..." elevator pitch on `_index.md`,
  `install/_index.md`, `why/_index.md`, `use/workflow/methodology.md`,
  `skills/_index.md`, `reference/skills/_index.md`, `platforms/_index.md` →
  trim everything to page-specific framing; the canonical pitch lives at
  `why/the-thesis.md`.
- The "seven activities" enumeration on `use/workflow/_index.md` and inside
  `methodology.md` → catalog lives at `reference/glossary/activities.md`;
  other pages link.

## Open decisions for you

These three need your call before I touch prose. Each one changes the page
count.

1. **`use/workflow/_index.md`**: keep as a thin landing, or absorb into
   `methodology.md` and drop. Recommend **absorb** because the page does not
   earn a distinct purpose under the scopes above.

2. **`reference/skills/_index.md`**: keep as invocation reference (Proposal A),
   or merge into `/skills/` (Proposal B). Recommend deciding after I draft the
   invocation reference content — if under ~30 lines, merge.

3. **Section-landing pages** (`why/_index.md`, `use/_index.md`,
   `reference/_index.md`, `reference/glossary/_index.md`): keep all four as
   thin card-hub landings. Recommend keep — hextra navigation expects them
   and the cost is small.

## Exit criteria

Phase 0 (this plan): you confirm or redirect the scopes; the table of "what
each page owns" is the contract.

Phase 1 (the rewrite): each page's content is reduced to its declared scope.
The cross-file redundancy script returns 0 at the 0.25 threshold. Pages that
were absorbed are deleted (with `aliases` frontmatter on the surviving page
so old links keep working).

Phase 2 onward: the existing prose-quality plan (Wordiness → Hedges →
Passive → SentenceLength) is unblocked because the document boundaries are
clear and each remaining hit is local to one canonical page.

## What this plan deliberately does not do

- It does not specify the *prose* of the rewritten paragraphs. Each page's
  scope is the contract; the wording is for the rewrite step.
- It does not promote any Vale rule to error. That still depends on Phase 2.
- It does not touch generated trees.
