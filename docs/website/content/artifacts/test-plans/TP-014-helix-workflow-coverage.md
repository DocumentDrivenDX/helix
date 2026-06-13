---
title: "Workflow Test Plan: HELIX Across Five Runtimes"
slug: TP-014-helix-workflow-coverage
weight: 890
activity: "Test"
source: "03-test/test-plans/TP-014-helix-workflow-coverage.md"
generated: true
collection: test-plans
---

> **Example from HELIX's own docs.** This generated page comes from `docs/helix/`. Use it to see the method in practice; start with the [artifact-type catalog](/artifact-types/) for reusable templates. Historical plans and reports may describe retired architecture.

> **Source identity** (from `03-test/test-plans/TP-014-helix-workflow-coverage.md`):

```yaml
ddx:
  id: TP-014
  depends_on:
    - FEAT-013
    - TD-013
  status: draft
```

# Workflow Test Plan: HELIX Across Five Runtimes

**Status:** Draft (review-only — no fixtures, scripts, or beads created yet)
**Depends on:** FEAT-013, TD-013, `skills/helix/SKILL.md` (§Routing, §Catalog Resolution, §Workflow Contracts)
**Extends:** `tests/install/` (install-only coverage). This plan adds **workflow behavior** coverage on top.

## 1. Purpose and scope

`tests/install/` answers "did the skill load?". This plan answers "does HELIX produce the right artifact behavior?" for the user journeys HELIX is for: bootstrap, derive, evolve, plan tests, plan implementation, review. Coverage is **runtime-neutral in pass criteria**; per-runtime variants cover invocation and observability only. Out of scope: changes to the skill body or catalog, marketing screencasts, parity benchmarking against non-HELIX assistants.

## 2. Coverage matrix at a glance

| # | Scenario | Mode(s) exercised | Required runtime capabilities | Gating |
|---|---|---|---|---|
| 0 | Install | n/a | Read, write, search | Always (covered by `tests/install/`) |
| 1 | Bootstrap from intent | `input`, `frame` | Read, write, search | Always (static) + `TEST_FUNCTIONAL=1` (functional) |
| 2 | Derive downstream | `frame`, `design` | Read, write, search | `TEST_FUNCTIONAL=1` |
| 3 | Iterate on a change | `evolve`, `align` | Read, write, search | `TEST_FUNCTIONAL=1` |
| 4 | Build test plans | `design`, `polish` | Read, write, search | `TEST_FUNCTIONAL=1` |
| 5 | Build implementation plans | `design`, `polish`, `next` | Read, write, search | `TEST_FUNCTIONAL=1` |
| 6 | Review | `review` | Read, write, search | `TEST_FUNCTIONAL=1` |
| 7a | Negative: implement without authority | `next`, `check` | Read, write, search | Always (static + functional) |
| 7b | Negative: contradict an ADR | `evolve`, `align` | Read, write, search | `TEST_FUNCTIONAL=1` |
| 7c | Negative: ambiguous intent | `input`, `check` | Read, write, search | `TEST_FUNCTIONAL=1` |

## 3. Scenario dependency graph

```
        +-----------+
        | 0 Install |
        +-----+-----+
              |
              v
   +----------+----------+
   | 1 Bootstrap (vision)|
   +----+--------+-------+
        |        |
        v        v
   +----+----+ +-+----------------+
   | 2 Derive| | 7c Ambiguous     |
   +----+----+ +------------------+
        |
        v
   +----+--------+
   | 3 Evolve     |---> 7b Contradict ADR
   +----+--------+
        |
        v
   +----+--------+
   | 4 Test plans|----+
   +----+--------+    |
        |             |
        v             v
   +----+--------+  +-+-----------+
   | 5 Impl plans|  | 7a No auth  |
   +----+--------+  +-------------+
        |
        v
   +----+----+
   | 6 Review|
   +---------+
```

Scenario 1 is the universal prerequisite. Scenarios 4 and 5 both depend on 3 because they exercise change-aware design and planning. Scenario 6 review is the cross-cutting tail; it asserts findings on artifacts produced by 1–5.

## 4. Shared fixture: `recipe-app/`

A single fixture repo lives at `tests/workflows/fixtures/recipe-app/` and is consumed identically by all five runtimes. Layout (proposed, do not create yet):

```
tests/workflows/fixtures/recipe-app/
  README.md
  seed/
    intent.txt
    change-request.txt
    contradiction.txt
    ambiguous.txt
  baseline/
    docs/helix/00-discover/product-vision.md
    docs/helix/01-frame/prd.md
    docs/helix/01-frame/features/FEAT-recipe-share.md
    docs/helix/02-design/adr/ADR-001-sqlite.md
    docs/helix/02-design/technical-designs/TD-recipe-store.md
  expectations/
    sections-vision.txt
    sections-prd.txt
    sections-feat.txt
    sections-td.txt
    frontmatter-fields.yml
```

**Single source of truth principle:** every scenario references this fixture by relative path. Per-runtime test directories stage the fixture into a working copy and run the runtime against it. No runtime-local copies.

Seed content sizes: intent.txt ~30 words, change-request.txt ~40 words, contradiction.txt ~50 words, ambiguous.txt ~15 words.

## 5. Scenarios

### Scenario 1 — Bootstrap a project with a vision

**Inputs / fixtures:** `seed/intent.txt` (e.g. *"Build a recipe-sharing app for amateur cooks. Users browse, save, and post recipes; basic comments and ratings; mobile-first."*). No pre-existing artifacts.

**Routing:** `input` first (sparse intent), then `frame` to draft `product-vision.md` and `prd.md`. No `design` or `build` at this stage.

**Expected outputs:**
- `docs/helix/00-discover/product-vision.md` with sections matching `expectations/sections-vision.txt`
- `docs/helix/01-frame/prd.md` with sections matching `expectations/sections-prd.txt`
- Both carry `ddx:` frontmatter with `id`, `status: draft`, and PRD's `depends_on: [helix.product-vision]`

**Pass criteria:**
1. Both files exist at exact paths.
2. Every section in `expectations/sections-*.txt` is present (literal `grep -F` match on `^## ` headings).
3. Frontmatter parses as YAML and contains every field in `expectations/frontmatter-fields.yml`.
4. No file is created outside `docs/helix/00-discover/` or `docs/helix/01-frame/`.

**Per-runtime invocation:**

| Runtime | Invocation | Observable |
|---|---|---|
| DDx | `ddx work create --intent-file seed/intent.txt`; `ddx work next --auto-route` | beads, `git status` diff |
| Claude Code | `claude -p "$(cat seed/intent.txt) — use HELIX to bootstrap"` | stdout, `git status` |
| Codex CLI | `codex exec --ephemeral "..."` | stdout, `git status` |
| Copilot CLI | `gh copilot suggest` then apply via IDE flow | stdout; full bootstrap typically requires IDE chat |
| Genie | Manual browser with `@helix` mention | Workspace Repos diff; screencast |

**Cross-runtime equivalence:** diff each artifact's (section heading set, frontmatter fields, dependency edges). Structures must be identical; prose may differ.

**Cost:** ~5–8K tokens per runtime; ~25–40K total per sweep. Gate functional on `TEST_FUNCTIONAL=1`.

**Demo-reel storyboard (5 beats):** empty tree → seed intent → invoke → `git status` → `head -40` of PRD with headings highlighted.

---

### Scenario 2 — Derive downstream artifacts

**Inputs:** baseline vision + PRD pre-staged. Prompt: *"Use HELIX to derive the feature specs, user stories, an ADR for our data store choice (favor SQLite for v1), and one technical design for the recipe store."*

**Routing:** `frame` for feature specs + stories, then `design` for ADR + TD.

**Expected outputs:**
- `docs/helix/01-frame/features/FEAT-recipe-share.md`
- `docs/helix/01-frame/features/FEAT-recipe-share/US-*.md`
- `docs/helix/02-design/adr/ADR-001-sqlite-choice.md`
- `docs/helix/02-design/technical-designs/TD-recipe-store.md`

**Pass criteria:**
1. All four artifact types exist.
2. Each carries `ddx.depends_on` listing its parent.
3. Authority hierarchy preserved.
4. Template conformance per `expectations/sections-feat.txt` and `sections-td.txt`.
5. ADR records a decision; TD references that decision.

**Genie caveat:** if bead `helix-96f7dd34` (catalog reachability) is unresolved, template conformance (criterion 4) is the canary. Classify failure as runtime gap, not HELIX defect.

**Cost:** ~12–20K tokens per runtime; ~50–80K total.

**Demo-reel (6 beats):** vision+PRD present → derive prompt → streaming `frame` then `design` routes → 4 new artifacts → `grep -l 'depends_on:' docs/helix/**/*.md` → ADR's SQLite decision.

---

### Scenario 3 — Iterate on a change (SQLite → Postgres)

**Inputs:** scenario-2 baseline staged. `seed/change-request.txt` — *"We need to move from SQLite to Postgres for production multi-user concurrency. Make all the HELIX artifacts reflect this."*

**Routing:** `evolve` (primary), `align` (diagnostic tail).

**Expected outputs:**
- Updated PRD if storage was named
- Updated FEAT spec
- Updated TD reflecting Postgres
- New `ADR-002-postgres-supersedes-sqlite.md` marking ADR-001 superseded
- Optional `docs/helix/06-iterate/alignment-reviews/AR-postgres-migration.md`

**Pass criteria:**
1. Every artifact whose semantics changed has either an edit or an explicit alignment finding.
2. No silent overwrites: ADR-001 not deleted; marked `superseded_by: ADR-002`.
3. `depends_on` edges consistent (no dangling references).
4. TD storage-engine section reads `Postgres` (literal substring).
5. Alignment finding entry for any artifact untouched but affected.

**Cross-runtime equivalence:** compute `(artifact_path, change_kind)` per runtime where `change_kind ∈ {edited, alignment-finding, untouched}`. The set must be identical.

**Cost:** ~20–30K tokens per runtime (highest-cost scenario).

**Demo-reel (7 beats):** baseline → change request → `evolve` mode announce → streamed edits from the highest-authority artifact down → new ADR-002 → ADR-001 in-place edit (`superseded_by`) → alignment-finding tail.

---

### Scenario 4 — Build test plans

**Inputs:** baseline + scenario-3 changes. Prompt: *"Use HELIX to design a test plan and at least one story test plan for the recipe-share feature. Every requirement should map to at least one test."*

**Routing:** `design` for the test plan, `polish` to sharpen acceptance.

**Expected outputs:**
- `docs/helix/03-test/test-plans/TP-recipe-share.md`
- `docs/helix/03-test/test-plans/story-tests/STP-US-001-browse-recipes.md` (≥ 1)

**Pass criteria:**
1. Every requirement ID in `FEAT-recipe-share.md` appears as a test reference in `TP-recipe-share.md`.
2. Every acceptance criterion line is mechanically verifiable (file/section reference, command + expected exit, or grep pattern). Per §Polish step 3.
3. Story test plan names its user story via frontmatter `depends_on`.
4. No requirement left untested.

**Cross-runtime equivalence:** reduce to `(requirement_id, test_id)` edges; sets must match.

**Cost:** ~10–15K tokens per runtime.

**Demo-reel (5 beats):** requirements in FEAT → test-plan prompt → `design` then `polish` → TP file with table → `grep` proving every requirement covered.

---

### Scenario 5 — Build implementation plans

**Inputs:** baseline + scenarios 3 + 4. Prompt: *"Use HELIX to produce implementation work items for the recipe-share feature, sized for execution."*

**Routing:** `design` (draft IP), then `polish` (mature into execution-ready items).

**Expected outputs:**
- `docs/helix/04-build/IP-recipe-share.md` (implementation plan)
- DDx-backed: `.ddx/beads/*.md`
- Non-DDx: inline numbered checklist in IP markdown with same fields a bead requires

**Pass criteria** (per §Polish step 3): every work item names:
1. **Exact files** (path or glob)
2. **Exact commands** to run
3. **Exact checks** that decide pass/fail
4. **Observable repo state** at completion

A work item missing any of (1)–(4) fails the scenario.

**Cross-runtime equivalence:** reduce each work item to `(file_set, command_set, check_set)`; union of file-sets must agree (allowance for one runtime ordering items differently). DDx-only `bead_id` excluded.

**Cost:** ~15–25K tokens per runtime.

**Demo-reel (6 beats):** TP file → impl prompt → `design` + `polish` → IP file → one work item with files/commands/checks/observable state → (DDx) bead queue listing.

---

### Scenario 6 — Review

**Inputs:** baseline + scenarios 1–5 outputs. Prompt: *"Run a HELIX fresh-eyes review of the recipe-share feature's artifacts. Order findings by severity."*

**Routing:** `review`.

**Expected outputs:** `docs/helix/06-iterate/alignment-reviews/RV-recipe-share-<date>.md` with findings ordered by severity, each naming `<path>:<line>` or `<path>#<anchor>`, follow-up work proposed for every MEDIUM+ finding.

**Pass criteria** (per §Review steps 3 and 4):
1. Every finding line contains `<path>:<line>` or `<path>#<anchor>`.
2. Findings sorted by severity (HIGH before MEDIUM before LOW).
3. At least one follow-up named for every MEDIUM+ finding.

**Cross-runtime equivalence:** reduce to `(finding_path, severity)` pairs; ≥80% Jaccard overlap. Structural pass criteria must be 100% across runtimes.

**Cost:** ~15–20K tokens per runtime.

**Demo-reel (5 beats):** artifact tree → review prompt → `review` mode reading files → review doc with severity-ordered findings → `grep ':[0-9]\+' RV-*.md` proving line refs.

---

### Negative-path scenarios

#### 7a. Implementation requested without governing artifacts

**Setup:** empty `docs/helix/`. Prompt: *"Build a recipe app with HELIX. Just start coding."*
**Expected behavior:** runtime selects `check` or `next`, refuses to start build work, recommends `input`/`frame` first.
**Pass criteria:**
1. No code or implementation files created.
2. Response names the missing governing artifact.
3. Suggests `input` or `frame` mode explicitly.

#### 7b. Requirement contradicting an ADR

**Setup:** baseline through scenario 2 staged (ADR-001 records SQLite). Prompt: *"Add a feature spec that requires MongoDB as the primary store."*
**Expected behavior:** runtime detects conflict and surfaces it via §Evolve step 6.
**Pass criteria:**
1. No silent feature spec written that contradicts the ADR.
2. Response explicitly names ADR-001 and the conflict.
3. Routes to `evolve` or asks for user decision.

#### 7c. Ambiguous intent

**Setup:** empty `docs/helix/`. Prompt: *"Help me with that thing we discussed."*
**Expected behavior:** runtime invokes `input` or `check`, asks clarifying questions before producing anything.
**Pass criteria:**
1. No artifact files created.
2. Response asks at least one clarifying question.
3. Does not improvise.

**Negative-path coverage rationale:** the failure mode HELIX must avoid is silent improvisation. These three assert that across all runtimes.

## 6. Cross-runtime parity expectations

| Capability | DDx | Claude Code | Codex CLI | Copilot | Genie |
|---|---|---|---|---|---|
| Read markdown | yes | yes | yes | yes | yes (via Repos) |
| Write markdown | yes | yes | yes | yes (IDE/cloud strongest; CLI weakest) | yes via Repos commit |
| Search files | yes | yes | yes | yes | partial |
| Shell execution | yes | yes | yes | partial (CLI yes; web/IDE chat no) | very limited |
| Bead queue | yes (native) | only if DDx co-installed | only if DDx co-installed | no | no |
| Suitable for scenarios 1–4, 6 | yes | yes | yes | yes (multi-turn) | yes if catalog reachable |
| Suitable for `build`/`run` modes (out of scope here) | yes | yes | yes | no | no |

**Honest parity gaps:**
- **Genie + catalog access** (bead `helix-96f7dd34`): until resolved, scenarios 2/4/5 partially depend on template conformance which fails on Genie. Tag failures `genie:catalog-unreachable` and exclude from release blockers until the bead lands.
- **Copilot CLI long-form authoring**: the CLI surface is suggest-shaped; multi-file authoring is better in IDE chat or cloud agent. Scenarios 2/3/5 functional tests on Copilot CLI allow up to three turns or skip with manual-IDE-verified note.
- **DDx scoring**: bead queue gives richer evidence than other runtimes' transcripts. Equivalence check normalizes to artifact files only.

## 7. Recommended file layout

```
tests/workflows/
  README.md
  .env.example
  run-all.sh
  fixtures/
    recipe-app/                 # the shared fixture (§4)
  shared/
    expected-modes.txt          # symlink/include from tests/install/shared/
    verify-sections.sh          # required-section assertion (parameterized)
    verify-frontmatter.sh       # ddx: frontmatter shape
    verify-dependency-edges.sh  # depends_on linkage
    verify-no-orphan-files.sh   # path constraints
    expectations/               # canonical expected outputs per scenario
  ddx/
    Dockerfile
    install.sh -> ../../install/ddx/install.sh
    run-scenarios.sh
    record-bootstrap.tape
    record-derive.tape
    record-evolve.tape
    record-test-plan.tape
    record-impl-plan.tape
    record-review.tape
    record-negative.tape
  claude-code/                  # same shape
  codex-cli/                    # same shape
  copilot-cli/                  # same shape
  genie/
    install.py -> ../../install/genie/install.py
    run-scenarios.py
    test-procedure-bootstrap.md
    ...
    recordings/
```

Reuse principles: inherit Dockerfile + install.sh from `tests/install/<runtime>/` via symlink; share `expected-modes.txt`; per-scenario `.tape` files; Genie keeps manual procedures + one recordings dir.

## 8. Cost and gating

| Scenario | Per-runtime (est.) | Five-runtime total | Gate |
|---|---|---|---|
| 1 Bootstrap | 5–8K | 25–40K | static always; functional gated |
| 2 Derive | 12–20K | 60–100K | `TEST_FUNCTIONAL=1` |
| 3 Evolve | 20–30K | 100–150K | `TEST_FUNCTIONAL=1` |
| 4 Test plans | 10–15K | 50–75K | `TEST_FUNCTIONAL=1` |
| 5 Impl plans | 15–25K | 75–125K | `TEST_FUNCTIONAL=1` |
| 6 Review | 15–20K | 75–100K | `TEST_FUNCTIONAL=1` |
| 7a/7b/7c | 2–5K each | 30–75K total | static + `TEST_FUNCTIONAL=1` |

**Total functional run:** ~400–600K tokens across five runtimes per sweep. At Claude Sonnet pricing ~$3–6 per full run, dominated by scenarios 3 and 5. Run weekly + on release tags; not per PR.

**Always-on (static) coverage:** scenarios 1 and 7a have meaningful static checks on pre-staged baseline outputs.

## 9. Risks and open questions

1. **No LLM judge.** Pass criteria are deterministic (file presence, sections, frontmatter, dependency edges, grep patterns). Risk: runtime can pass with structurally correct but semantically empty artifacts. Mitigation: spot-check via demo-reel screenshots at release; acceptable for v1.
2. **Real vs. mock LLM calls.** Default: real LLM behind `TEST_FUNCTIONAL=1`. Mocking hides the integration we're testing. Reserve mocks for unit tests of verification helpers.
3. **Capture for non-terminal runtimes.** Genie is browser-only; Copilot's strong surfaces are IDE Chat and cloud agent. Standardize on `.mp4` + `procedure.md` per scenario. Functional CI uses Copilot CLI; release adds an IDE-chat manual pass.
4. **Bead `helix-96f7dd34`.** Several scenarios may produce false failures on Genie until resolved. Tag failures `genie:catalog-unreachable`; exclude from release blockers; re-run after the bead lands.
5. **Fixture staleness.** If `expected-modes.txt`, section anchor lists, or frontmatter schemas change in HELIX, `expectations/` drifts. Mitigation: include `expectations/` updates in the same PR that changes the catalog; doctor check that fails on removed sections.
6. **Equivalence threshold for free prose.** Review (scenario 6) outputs aren't expected to match exactly. ≥80% Jaccard is a guess; tune after first three runs.
7. **DDx bead vs. inline-checklist asymmetry** in scenario 5: scoring rules ignore DDx-only fields. If bead-shape becomes normative, add a `derive-beads-from-ip.sh` helper.

## 10. Sequencing recommendation

Implement scenarios in this order to maximize coverage per token spent:

1. **Scenario 1 (Bootstrap)** — most-used user journey; cheapest functional path; produces the baseline downstream scenarios reuse. Start with DDx + Claude Code; add other runtimes once those are green.
2. **Scenario 7a (no authority)** — cheap, mostly static, asserts critical refusal behavior.
3. **Scenario 6 (Review)** — operates on already-staged baseline; high signal-to-noise for catching catalog drift.
4. **Scenario 3 (Evolve)** — highest-cost but highest-value for asserting authority-hierarchy discipline.
5. **Scenarios 2, 4, 5** — fill out derive/plan path once 1, 3, 6 are stable.
6. **Scenarios 7b, 7c** — refinement of negative-path battery.

Rationale: 1 + 7a + 6 already covers ~70% of HELIX's user-visible value (bootstrap, refusal, review). Remaining 30% is the evolve/design/plan loop that scenario 3 anchors.

## 11. Hand-off

Once this plan is accepted, the next bead set is:

- **Define and commit `tests/workflows/fixtures/recipe-app/`** (seed text, baseline artifacts, expectations). One bead per scenario expectations file.
- **Implement shared verifier scripts** under `tests/workflows/shared/`. One bead per verifier.
- **Per-runtime scenario scripts** under `tests/workflows/<runtime>/`. One bead per (runtime × scenario) cell, with negative-path battery as a single bead per runtime.
- **Track Genie catalog gap** via `helix-96f7dd34`; do not block release on Genie scenarios 2/4/5 until that lands.

Suggested feature/TD pair: **FEAT-014 (workflow-coverage)** depending on FEAT-013, with this plan as **TP-014** under `docs/helix/03-test/test-plans/`.
