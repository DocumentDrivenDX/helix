---
title: "Implementation Plan: helix-library Family (monorepo, test-first)"
slug: implementation-plan-2026-06-04-helix-library-family
weight: 470
activity: "Design"
source: "02-design/implementation-plan-2026-06-04-helix-library-family.md"
generated: true
---
# Implementation Plan: helix-library Family (monorepo, test-first)

- **Date:** 2026-06-04
- **Status:** Phase 5 of 6 — marker + linkage review folded; ready to execute
- **Companion docs:**
  - [design-2026-06-03-helix-library-split.md](/artifacts/design-2026-06-03-helix-library-split/)
  - [design-2026-06-04-helix-family-marker-and-linkages.md](/artifacts/design-2026-06-04-helix-family-marker-and-linkages/) (marker + linkage extension)
  - [plan-2026-06-03-helix-library-FINAL.md](/artifacts/plan-2026-06-03-helix-library-final/) §0 (monorepo amendment)
  - [plan-2026-06-03-helix-library-migration.md](/artifacts/plan-2026-06-03-helix-library-migration/) (preserved as historical)
  - [test-plan-2026-06-04-helix-library-family.md](/artifacts/test-plan-2026-06-04-helix-library-family/) (executable spec)

This is the implementation plan that replaces the 14-PR/55h sibling-
repo plan from the FINAL doc with a 6-PR monorepo shape and folds in
the Phase 3 adversarial review.

**Phase 5 update (2026-06-04):** the marker + linkage relaxation
design (design-2026-06-04-helix-family-marker-and-linkages.md) lands
as PR7 and PR8 after the monorepo base. Phase 4 review of the marker
design was folded into the design doc (M006, M010, I010, I101/I103/
I104, I120/I121, G103/G104/G105/G133/G140, W003/W004/W005, R020) and
into the fixture set: T5/T6/T7 reshaped to validate marker-resolves
behavior, T5a/T6a/T7a preserve the heuristic fallback under absent
marker, T24-T33 lock the new contracts. Effort updated below.

---

## 1. Decision

**GO.** Proceed with the monorepo helix-family architecture
(library/ + product/ + infra/) under a single marketplace, gated by
the test-first bench fixture suite. No HIGH-severity blockers remain
after the Phase 3 review was folded into the test plan and the
fixture set was expanded from 13 to 22 scenarios (23 if you count
T18b; T8 stays deferred).

### What was folded from the Phase 3 review

| Review item | Severity | Disposition |
| --- | --- | --- |
| T2.5 library upgrade adds required_section against stale doc | high | Added T14 (warn-on-stale, enforce-on-new contract) |
| Corrupt/half-mounted library | high | Added T15 (distinct diagnostic, no improvisation) |
| graph.yml cycle detection | high | Added T16 (cycle named with both nodes) |
| graph.yml dangling requires | high | Added T17 (dangling target named) |
| Local override weakens canonical | high | Added T18 (rejects + names stripped section) |
| Local override extends unknown type | high | Added T18b (parallel to T11) |
| T2-prime edit-existing without library | high | Added T19 (edit is authoring; setup-gap fires) |
| T13 forks architecture; workaround untested | high | Added T20 (positive workaround) + T21 (malformed) |
| Slash-command namespace collision | medium | Deferred to v1.1 — needs slash-namespace ADR first |
| Multi-workspace cwd switches | medium | Deferred to v1.1 — runner change required |
| DDx bead `graph_node:` pointing at renamed node | medium | Deferred to v1.1 — covered by Phase D0 guard in v1 |
| Empty docs/helix/ (gitkeep only) signal pin | medium | Added T22 (artifact, not directory) |
| HELIX_METHODOLOGY env override exercised | medium | Added T23 (first fixture to actually use env) |
| Negative control for T1 (adversarial prompt) | medium | Added T01 prompt 02 (routing barrier, not user-cooperation) |
| All weak_assertions on T01/T02/T03/T04/T05/T07/T09/T10/T11/T12/T13 | mixed | Tightened in place (see §5) |
| T8 runner skip rule ambiguity | medium | Pinned to `status: deferred` frontmatter only |
| Validator perf at scale | low | Surfaced in test plan §Open follow-ups; runner enforces 10s/100MB ceiling as defensive default |
| stream_json_tool_use lacks exactly_one cap | (across fixtures) | Added to assertion schema; applied to T3/T4/T5/T9/T14/T23 |
| Transcript artifacts on failure | (review recommendation) | Pinned runner mechanics: per-fixture `<results>/<id>/*.stream.jsonl` + `*.prose.txt` |

### What did NOT change

- The monorepo topology and the ~6-PR shape from FINAL §0.
- The methodology/library architectural split, two-namespace scheme,
  edge model, override semantics.
- 30 types promoted to library in v1; architecture + contract stay
  product-local.
- The methodology-level resolver chain (library/ co-resident →
  `~/.claude/plugins/helix-library/` → vendored fallback).

---

## 2. Phase-by-phase

The phase letters (A/B/C/D) from FINAL §3 are preserved here so
cross-references survive; the PR count collapses because monorepo
removes per-repo CI ceremony.

### PR1 — Reorganize: move helix tree to product/, scaffold library/ + infra/

- **Title:** `helix-family: monorepo reorganization (product/, library/, infra/)`
- **Files added:**
  - `.claude-plugin/marketplace.json` (root, lists 3 plugins)
  - `library/.claude-plugin/plugin.json` (no `skills:` field — T13 will tell us if the workaround is needed)
  - `library/{types,concerns,scripts}/` (empty placeholders)
  - `infra/.claude-plugin/plugin.json` (placeholder; PR3 populates)
- **Files moved:**
  - existing `skills/helix/` → `product/skills/helix/`
  - existing `workflows/` → `product/workflows/`
  - existing `.claude-plugin/plugin.json` → `product/.claude-plugin/plugin.json`
- **Files deleted:** none.
- **Verification gate:**
  - `tests/fixtures/family/T01-library-only/` passes (library installs, no routing — once PR2 lands an empty library is enough for this PR).
  - `tests/fixtures/family/T13-no-skills-field/` passes OR fails with documented signal (T13's `on_failure_followup` triggers PR1.1 to land the skills/_data workaround; T20 then becomes the on-path test).
- **Effort:** ~5h (4h move + 1h marketplace.json + plugin.json wiring).
- **Rollback:** `git revert`. The product/ subtree and original `skills/helix/` are mirror trees; rollback restores the old layout. Marketplace can be unpublished if it was pushed.

### PR2 — Promote 30 artifact types to library/

- **Title:** `helix-library: promote 30 artifact types + section_aliases for ADR`
- **Files added:**
  - `library/types/{prd,adr,runbook,...}.yml` (30 specs per design §3, §4.1)
  - `library/types/adr.yml` includes section_aliases mapping (design §10)
- **Files changed:**
  - `product/workflows/` references updated to use `library:` namespace.
- **Files deleted:** type definitions that moved to library/ (their old locations).
- **Verification gate:**
  - T03, T04, T09, T12, T12b pass.
  - T10, T11, T18 fail with the EXPECTED non-zero exit and correctly-named offending nodes/types/sections.
  - T16, T17 fail with cycle/dangling diagnostics naming the right nodes.
- **Effort:** ~7h (5h type promotion + 2h validator fixes uncovered by graph fixtures).
- **Rollback:** revert. Types specs are pure data; product/ workflows still reference legacy paths until PR2's second commit, so rollback is mechanical.

### PR3 — Absorb helix-infra into infra/

- **Title:** `helix-family: absorb helix-infra (skills + workflows + ADR location)`
- **Files added:**
  - `infra/skills/helix-infra/` (from the standalone helix-infra repo)
  - `infra/workflows/`
  - `infra/methodology.yml` + `infra/graph.yml`
- **Files changed:** `.claude-plugin/marketplace.json` (helix-infra metadata).
- **Files deleted:** `infra/.claude-plugin/plugin.json` placeholder from PR1 replaced with the real one.
- **External:** old `helix-infra` GitHub repo gets a README redirect pointing here (separate PR in that repo, not part of this monorepo PR).
- **Verification gate:**
  - T04, T06, T05, T07, T22, T23 all pass.
  - T19 still passes (helix-only setup-gap unchanged).
- **Effort:** ~5h (4h tree absorb + 1h marketplace wiring).
- **Rollback:** revert. The old helix-infra repo remains the canonical source until this PR's marketplace publish; revert and re-publish from there.

### PR4 — DDx bead `graph_node:` field + library-node-rename guard

- **Title:** `helix-family: DDx bead graph_node frontmatter + rename guard`
- **Files added:**
  - DDx bead schema bump (in DDx surface, but lands in this repo since the family ships the rename).
  - `scripts/family-bead-guard.py`: walks the existing bead corpus and asserts every `graph_node:` reference resolves to a node in the current library tree. Runs in CI.
- **Files changed:** bead frontmatter samples in `docs/`.
- **Verification gate:**
  - Bead guard exits 0 on the current corpus.
  - Manual: add a fake bead with a renamed node id; guard exits non-zero.
- **Effort:** ~3h (1h schema bump + 2h guard script + CI wire).
- **Rollback:** revert. The `graph_node:` field is additive; existing beads continue to work without it.

### PR5 — Fixture runner + bench gate in CI

- **Title:** `helix-family: bench fixture runner + CI gate`
- **Files added:**
  - `tests/fixtures/family/run.py` (the runner described in test plan §Runner mechanics).
  - `.github/workflows/family-bench.yml` (or `just bench-family`).
  - Per-fixture artifact archiving (transcripts on failure).
- **Verification gate:**
  - All non-deferred fixtures (T1–T7, T9–T23, T12b, T18b) green.
  - T8 SKIPPED (status: deferred).
  - Runner emits transcripts to `<results>/<id>/*.stream.jsonl` + `*.prose.txt` on every run.
- **Effort:** ~8h (5h runner + 2h CI wiring + 1h transcript ergonomics).
- **Rollback:** revert. CI remains green on the prior PR4 state without the bench gate.

### PR6 — Tag family release v1.0.0

- **Title:** `helix-family: release v1.0.0`
- **Files added:**
  - `CHANGELOG.md` (family-level + per-plugin entries).
  - `library/CHANGELOG.md`, `product/CHANGELOG.md`, `infra/CHANGELOG.md`.
- **Files changed:**
  - `.claude-plugin/marketplace.json` version bumps.
  - `library/.claude-plugin/plugin.json`, `product/.claude-plugin/plugin.json`, `infra/.claude-plugin/plugin.json` version bumps.
- **Verification gate:**
  - PR5's bench gate green on the tagged commit.
  - Manual install + smoke prompt against a fresh user environment.
- **Effort:** ~2h.
- **Rollback:** delete the tag, unpublish the marketplace (or publish a v1.0.1 with the rollback). v1.0.0 with a known regression should be yanked, not silently superseded.

### PR7 — Marker file (.helix.yml) + validator subcommands

- **Title:** `helix-family: marker file, validator marker/graph/instance/type subcommands`
- **Files added:**
  - `library/schemas/marker.schema.json` — JSON Schema for `.helix.yml`
    (helix_version, methodologies, defaults, cross_methodology_edges).
  - `library/schemas/graph.schema.json` — JSON Schema for `graph.yml`
    (nodes, edges, allowed_cycles, external_edges).
  - `library/scripts/helix_check.py` — single py3-stdlib script, four
    subcommands (`marker`, `graph`, `instance`, `type`) per
    design-2026-06-04 §4.
  - `library/scripts/migrate_relationships_to_links.py` — migration
    script per design-2026-06-04 §5.4. Default `--dry-run`.
  - Root `.helix.yml` for this monorepo (declares helix at
    `product/` and helix-infra at `infra/`).
- **Files changed:**
  - `product/skills/helix/SKILL.md` — read marker on activation, log
    one-line resolution banner (`marker → helix (scope: docs/helix/)`).
  - Heuristic-fallback path (frozen) retained behind a single
    `_resolve_methodology_from_heuristics()` helper.
- **Verification gate:**
  - T05 (marker resolves both methodologies, defaults wins).
  - T06 (marker silences undeclared product methodology).
  - T07 (cwd-under-scope wins).
  - T05a / T06a / T07a (frozen heuristic fallback under absent marker).
  - T28 (nested marker M010 warning).
  - T33 (root: path missing M006 hard stop).
  - T24 (validator marker mode exits clean on a happy-path corpus).
- **Effort:** ~9h (4h schemas + validator skeleton, 2h marker walk +
  M010 + M006, 1h migration script skeleton, 1h skill activation
  changes, 1h fixture wiring).
- **Rollback:** revert. Marker is opt-in; frozen heuristic fallback
  keeps existing repos working.

### PR8 — Linkage relaxation (library shape only, graph + instance edges)

- **Title:** `helix-family: linkage relaxation (drop type relationships, add graph.yml / ddx.links)`
- **Files added:**
  - `product/workflows/graph.yml` — extracted from prior `meta.yml
    relationships:` per design-2026-06-04 §2.2 + Phase B migration.
  - `infra/workflows/graph.yml` — same for helix-infra.
  - Validator semantics for I101/I103/I104/I120/I121, G103/G104/
    G105/G133/G140/G201, T003/T010, I010, W003/W004/W005, R020.
- **Files changed:**
  - `library/types/*/meta.yml` — strip `relationships:` from every
    promoted type (Phase B of §5.4 transition matrix).
  - PRD/FEAT/ADR templates — add `ddx.links: []` placeholder under
    frontmatter and document the new edge format.
  - `product/skills/helix/SKILL.md` — round-trip frontmatter per
    §2.5 write contract (key-preserving emitter, no incidental
    legacy → new translation).
- **Verification gate:**
  - T24 (instance edge respects graph).
  - T25 (instance edge violates graph — G201).
  - T26 (instance edge target missing — I101 + nearest + planned hint).
  - T27 (cross-methodology informs edge resolves).
  - T29 (external_edge required: true → G104).
  - T30 (library major bump → I010 deprecation warning).
  - T31 (status: planned downgrade to I103).
  - T32 (skill rewrite preserves unknown frontmatter keys).
  - Library-mode validator self-test: every shipped type meta.yml
    parses clean (no relationships:).
- **Effort:** ~10h (3h graph extraction, 3h instance validator + edge
  resolution + status:planned + cross-methodology routing, 1h
  library_type_version semver semantics, 1h frontmatter round-trip
  in skill, 2h fixture wiring + library type strip).
- **Rollback:** revert. The migration script is dry-run by default;
  Phase A library version (1.0.0) accepts both shapes so a rollback
  PR can ship the prior shape without breaking instances.

### PR9 — Performance cache + --changed-only incremental mode (split from PR7/PR8)

- **Title:** `helix-family: .helix/index.json cache + --changed-only mode`
- **Files added:**
  - `library/scripts/helix_check.py` cache subsystem (per
    design-2026-06-04 §4.7): `--cache .helix/index.json` with
    `{doc_path, mtime_ns, ddx.id, edges_hash}`.
  - `.gitignore` entry for `.helix/index.json` written by hook
    installer.
  - Pre-commit hook update: `helix_check.py instance --cache
    --changed-only HEAD` for fast-feedback.
- **Verification gate:**
  - Synthetic-corpus perf fixture (deferred to v1.1; defensive
    10s/100MB ceiling in PR5 runner protects against regression now).
  - Cache parity self-test: validator output is byte-equivalent with
    and without `--cache`.
- **Effort:** ~4h (2h cache logic, 1h --changed-only git plumbing,
  1h hook wiring + .gitignore).
- **Rollback:** revert. Cache is opt-in via flag; rolling back just
  takes the fast path away.

**Total estimate:** ~53h (PR1 5h + PR2 7h + PR3 5h + PR4 3h + PR5 8h
+ PR6 2h + PR7 9h + PR8 10h + PR9 4h). Original FINAL §0 envelope
was 25–30h; the marker + linkage relaxation adds ~23h of new work
covering scope explicitly declared in Phase 3 design and Phase 4
review. PR1–PR6 (the prior monorepo baseline) remain unchanged at
30h.

---

## 3. Risk register

Surviving risks after the review fold. Tracking only items not
already covered as Acceptance gates.

| Risk | Mitigation |
| --- | --- |
| T13 fails (Claude Code rejects no-skills plugin.json) | T20/T21 cover the documented workaround. PR1.1 lands the workaround if T13 fails on first run. |
| Validator cycle detection regresses to O(N^2) or hangs | Runner enforces 10s/100MB ceiling per validator invocation; perf fixture deferred to v1.1 but the defensive ceiling catches the regression at T16. |
| Override-weakens fixture (T18) requires validator surface that does not exist yet | PR2's verification gate explicitly lists T18; if the validator does not gate override weakening, PR2 grows by one commit to add it. |
| Section_order ordering not honored in renderer/agent (T9) | T9 fixture's `content_regex_forbid` catches a renderer that ignores order. PR2 gate. |
| HELIX_METHODOLOGY env not threaded through the skill (T23) | T23 fixture catches it; PR3 gate. |
| Two implementations of `helix_graph_check.py` (validator) diverge on diagnostic strings | All validator fixtures use `stderr_match_all` requiring both a category pattern AND the offending identifier — diagnostic strings are part of the contract surface. |
| Library upgrade fixture (T14) commits to contract A (warn-on-stale) but a user prefers contract B | Documented in T14 README: flipping `expect_exit_nonzero: true` is a 1-line change if the family elects contract B. PR2 reviewers should consciously confirm contract A. |
| Bench fixtures are non-deterministic on prose | Every fixture's load-bearing assertion is structural (tool_use, exit code, filesystem) — prose is corroborative. The runner is deterministic on structure (test plan §Runner mechanics). |
| PR7 marker walk slow on 1k+ doc corpora; users `--no-verify` the hook | PR9 ships the `.helix/index.json` cache + `--changed-only HEAD` mode (design §4.7). Until PR9 the runner's defensive 10s/100MB ceiling catches regressions; the perf budget table sets the contract. |
| PR8 frontmatter round-trip drops or reorders unknown keys (S8 regression) | T32 locks the round-trip contract: legacy `depends_on:` and vendor `x-team-owner:` must survive byte-equivalent. Skill must use insertion-ordered dict + `sort_keys=False`. |
| PR8 library type strip lands before consumer repos migrate (S7 cutover) | Phase A library 1.0.0 ships T003 as WARNING (W003); Phase B 1.1.0 flips to ERROR after ~30 days. `helix_version: 2` marker opts a repo into strict-from-day-one. Transition matrix lives in design §5.4. |
| Cross-methodology edge points at uninstalled methodology (S6) | I120 (inactive) vs I121 (uninstalled) split diagnostics direct the operator to the right next step. G140 fires once per graph load when active graph's external_edges reference inactive methodologies. |
| Library major bump breaks all in-flight instances (S3) | I010 deprecation warning fires for one major cycle when instance pins a prior major; design §2.1 codifies the semver semantics. T30 is the regression guard. |
| Stray nested `.helix.yml` files create silent ignore (S1) | M010 warning fires once per stray marker. `helix_check.py marker --discover` mode scans the whole tree for one-shot lint. T28 covers the warning; CI runs `--discover` to surface count. |

---

## 4. Out of scope for v1

- T8 (helix + helix-web) — deferred until helix-web exists.
- Slash-command namespace policy + collision fixture — needs an ADR
  before a fixture can be authored. v1.1.
- Multi-workspace cwd switches in one Claude session — runner change
  required. v1.1.
- Validator perf at scale (synthetic 500 / 5000 node graphs) —
  defensive 10s/100MB ceiling in v1; dedicated perf fixture in v1.1.
- DDx bead `graph_node:` referencing a renamed/removed library node
  as a first-class fixture — v1 covers via the PR4 rename guard,
  fixture deferred to v1.1.
- Semantic-quality judgments on generated artifacts (a stylistic
  "this PRD reads well" assertion is a different layer).
- Cross-major version drift between library and methodologies — the
  monorepo ships in lockstep; cross-major drift cannot occur.

---

## 5. Fixture refinements applied in Phase 4

Beyond new fixtures, every weak_assertion from the review was
tightened in place. Summary of in-place edits:

- **T01 / 01-list-types:** narrowed must_match_any (removed bare
  `(?i)library`); added negative on routing-into-authoring verbs;
  added `expect_tool_use` blocking Edit/Write/Bash (filesystem
  immobility for data-only plugin).
- **T01 / 02-adversarial-discover** (new): adversarial negative
  control. User demands methodology behavior; library-only refuses.
- **T02 / 01-read-prd:** added Read tool_use assertion (proof of
  read); added verbatim-token must_match_any ($40k / 2% / WMS) to
  defeat hallucination.
- **T02 / 02-author-prd:** tightened setup-gap pattern to require
  library name + non-installed verb within 80 chars; expanded
  improvisation-forbid to multi-anchor (Problem/Goals/Non-goals/
  Risks/Success Metrics/Out of scope, h1–h4).
- **T03 / 01-author-section:** added content_regex_all requiring
  `## Risks` heading AND 20 chars of body; added exactly_one cap.
- **T04 / 01-author-adr:** added content_regex_all for canonical
  ADR sections (Context/Decision/Consequences); added exactly_one cap.
- **T05 / 01-author-adr:** added second forbid_tool_use bounding
  the markdown Write universe to docs/helix/02-design/; added
  exactly_one cap.
- **T07 / 01-author-adr:** replaced loose `\bhelix\b` with
  negative-lookaround `(?<!-)\bhelix\b(?!-)` so helix-library /
  helix-infra alone do not satisfy must_match_all; bounded forbid_tool_use
  to all markdown writes (universe-wide).
- **T09 / 01-author-adr:** added section-order content_regex_all
  (Decision → Customer Impact → Consequences) and
  content_regex_forbid (canonical-only order).
- **T10 / 01-run-validator:** changed stderr_match_any to stderr_match_all,
  requiring the offending node id `02-design/adr` to appear.
- **T11 / 01-run-validator:** same change; require `not-a-real-type`
  to appear in the diagnostic.
- **T12 / 01-run-validator:** unchanged (already validator_exit
  exit-zero); T12b added as negative companion.
- **T13 / 01-install:** replaced `claude plugin install --from-dir`
  with command_resolver + command_candidates (probes
  `claude plugins --help`); added filesystem post_install_assert.
- **T08 / runner skip rule:** pinned to `status: deferred`
  frontmatter; absence of plugins-installed.txt is no longer a skip
  signal.

---

## 6. Acceptance

The family migration is "done" when:

A. **All non-deferred fixtures are green** on the monorepo HEAD —
   that is T1–T7, T9, T10, T11, T12, T12b, T13, T14, T15, T16, T17,
   T18, T18b, T19, T20, T21, T22, T23. T8 is SKIPPED via
   `status: deferred`.

B. **One `marketplace.json` at the monorepo root publishes three
   plugins** (helix-library, helix, helix-infra) and a fresh user
   environment can install each via the documented commands. T13
   (or, if T13 fails, T20/T21) is the install gate.

C. **The bench gate in CI** (PR5) runs the fixture suite on every
   commit to main, archives transcripts on failure, and a red bench
   blocks merge to a release branch.

The previous FINAL §6 acceptance list (9 items) is now subsumed by
A–C; the fixture suite is the executable spec for those nine items.

---

## 7. Open questions for the user

1. **Contract A vs contract B for stale-doc validation (T14).** Fixture
   commits to contract A: validator emits a non-fatal warning on
   stale docs, enforces new authoring against the upgraded shape.
   Is that the right call? Contract B (error on stale) is a one-line
   fixture flip and a sterner deprecation cycle. The FINAL plan §4
   risk #3 mentioned a "deprecation-window protocol" but did not pin
   warn-vs-error for pre-existing docs.

2. **Whether to land the skills/_data workaround pre-emptively in PR1.**
   Two paths:
   - (a) Land PR1 with `plugin.json` lacking `skills:`; if T13 fails,
     land PR1.1 to add the workaround.
   - (b) Land PR1 with the workaround already in place; T13 becomes
     a positive test of "Claude Code accepts plugin.json with no skills"
     only if we revert PR1.1 in a future PR.
   Recommendation: (a). Cheaper if T13 passes (likely); the fixture
   spec is unambiguous either way.

3. **PR4 ordering — DDx bead schema migration.** The FINAL plan had
   Phase D0 land BEFORE methodology migration. With the monorepo we
   can keep that order (PR4 → PR5 → PR6) or interleave (DDx bump in
   PR1 alongside the reorganization). Current plan keeps Phase D0
   in PR4 for clarity. Worth confirming if there's a preference for
   bead-schema-first.

4. **Should slash-namespace policy land as an ADR in v1?** The
   collision risk is real but the design today is silent. Authoring
   an ADR + fixture in v1 adds ~3h. Defer to v1.1 is the current
   plan; reverse if slash-command UX is a v1 acceptance item for
   the user.
