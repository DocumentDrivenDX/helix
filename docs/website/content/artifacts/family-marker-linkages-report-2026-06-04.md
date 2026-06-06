---
title: "Family Marker + Linkage Relaxation — Entry-Point Report"
slug: family-marker-linkages-report-2026-06-04
weight: 430
activity: "Design"
source: "02-design/family-marker-linkages-report-2026-06-04.md"
generated: true
---
# Family Marker + Linkage Relaxation — Entry-Point Report

- **Date:** 2026-06-04
- **Status:** Phase 6 of 6 (entry-point report). Design + plan locked.
- **Companions (read in this order):**
  - [design-2026-06-04-helix-family-marker-and-linkages.md](/artifacts/design-2026-06-04-helix-family-marker-and-linkages/) — design of record.
  - [implementation-plan-2026-06-04-helix-library-family.md](/artifacts/implementation-plan-2026-06-04-helix-library-family/) — 6→9 PR plan with effort + gates.
  - [test-plan-2026-06-04-helix-library-family.md](/artifacts/test-plan-2026-06-04-helix-library-family/) — fixture-suite executable spec.
  - [family-readiness-report-2026-06-04.md](/artifacts/family-readiness-report-2026-06-04/) — preceding monorepo-only entry doc (now superseded for the marker/linkage layer).
  - [design-2026-06-03-helix-library-split.md](/artifacts/design-2026-06-03-helix-library-split/) — base library/methodology split (still in force for §0–§5).

---

## §1 Decision summary

**Adopt both.** The marker file `.helix.yml` and the three-layer
linkage relaxation (library shape / methodology graph / instance
edges) land together as PR7 and PR8 on top of the monorepo baseline
(PR1–PR6). The two changes ship paired because they are coupled by the
validator: the marker names the active methodology graph(s); the
graph defines allowed type-pair edges; instance frontmatter
(`ddx.links:`) declares actual edges and is resolved against the
marker-selected graph.

### What got folded from the Phase 4 adversarial review

| Review item | Severity | Disposition |
| --- | --- | --- |
| S1 — stray nested `.helix.yml` silently ignored | HIGH | M010 warning + `helix_check.py marker --discover` mode |
| S2 — `external_edges[].required: true` retroactively invalidates | HIGH | G104 graph-load hard-fail; cross-methodology edges restricted to `informs` (G105) |
| S3 — library major bump breaks pre-existing instances | HIGH | I010 deprecation warning for one major cycle when instance pins prior major |
| S4 — forward references to unauthored docs error noisily | HIGH | `status: planned` edge attr → downgrade I101 to I103; re-upgrades at exit-gate |
| S5 — self-loop semantics on `allowed_cycles` | MEDIUM | G103 (walked kinds require entry) + G133 (non-walked self-loops noted once per graph) |
| S6 — uninstalled vs inactive cross-methodology targets indistinguishable | MEDIUM | Split I120 (inactive but installed) / I121 (uninstalled); G140 at graph-load |
| S7 — library-strip cutover with stale consumer instances | MEDIUM | Transition phase matrix (A/B/C) with named library versions; `helix_version: 2` opts repo into strict-from-day-one |
| S8 — skill incidentally rewrites unknown frontmatter keys | HIGH | §2.5 round-trip contract: insertion-ordered dict, `sort_keys=False`, never translate legacy→new in-place |
| S9 — marker `root:` typo silently treated as zero-instance scope | HIGH | M006 hard stop + `--allow-empty-scope` escape hatch for fresh repos |
| S10 — naive per-invocation walk slow on 1k+ corpora | MEDIUM | Perf budget table (§4.7); `.helix/index.json` opt-in cache; `--changed-only <ref>` git-diff mode |

No Phase 4 HIGH issues remain open. MEDIUM/LOW residue lives in §6 of
the design (open questions) and §3 of the implementation plan (risk
register).

---

## §2 What the new architecture looks like in one paragraph

A consuming repo declares which HELIX methodology flavors are active
and where they live in a root-level `.helix.yml` marker
(`methodologies:` list of `{id, root}` plus optional `defaults`,
`cross_methodology_edges`, `concerns`). Library type `meta.yml` files
hold SHAPE ONLY — required sections, prompts, template, quality
checks — with no relationship info. Each methodology owns a
`graph.yml` that declares which TYPE-PAIR edges are allowed
(`requires`, `informs`, `contains`, `supersedes`, `may_surface`,
plus vendor-namespaced `x-` kinds) and authorises any cross-methodology
edges from itself outward in an `external_edges:` block (advisory
`informs` only). Each instance document declares its actual edges in
frontmatter under `ddx.links:` as a list of `{kind, to, ...}` records
keyed by stable id, with `status: planned` as the typed forward-
reference escape. A single py3-stdlib validator (`helix_check.py`)
with four subcommands (`marker`, `graph`, `instance`, `type`) runs at
three points — pre-commit hook, skill runtime, repo CI — using the
marker to dispatch graph and instance checks; exit codes are
classed M / T / G / I / R / W with exhaustive collection (no
short-circuit) and JSON output for tool integration.

---

## §3 Implementation plan delta (relative to prior plan)

### Prior plan baseline (FINAL §0 + readiness 2026-06-04)

PR1–PR6, monorepo only, ~30h:

- PR1 reorganize tree (product/, library/, infra/)
- PR2 promote 30 artifact types to library/
- PR3 absorb helix-infra into infra/
- PR4 DDx bead `graph_node:` + rename guard
- PR5 fixture runner + bench CI gate
- PR6 tag family v1.0.0

### Three PRs added

| PR | Title | Added effort | New on-disk surface |
| -- | ----- | ------------ | ------------------- |
| PR7 | Marker file + validator subcommands | ~9h | `library/schemas/marker.schema.json`, `library/schemas/graph.schema.json`, `library/scripts/helix_check.py` (4 subcommands), `library/scripts/migrate_relationships_to_links.py` skeleton, root `.helix.yml`, SKILL.md marker activation banner + frozen heuristic helper |
| PR8 | Linkage relaxation (graph.yml + ddx.links) | ~10h | `product/workflows/graph.yml`, `infra/workflows/graph.yml`, library `meta.yml` strip of `relationships:`, PRD/FEAT/ADR template `ddx.links: []` placeholders, validator semantics for I/G/T/W codes, frontmatter round-trip emitter in skill |
| PR9 | `.helix/index.json` cache + `--changed-only <ref>` | ~4h | Cache subsystem in `helix_check.py`, hook installer writes `.gitignore` entry, pre-commit defaults to cache mode, CI defaults to no-cache |

### PRs changed vs prior plan

- **PR1 — unchanged scope**, but adds `library/schemas/` empty
  placeholder for PR7 land. The probe finding that Claude Code accepts
  `plugin.json` with no `skills:` field removes the PR1.1 contingency:
  T13 stays as the on-path install test; T20/T21 (skills/_data
  workaround) are DEFERRED to v1.1 unless T13 regresses in
  upstream Claude Code.
- **PR2 — unchanged scope**, but the `library/types/*/meta.yml`
  emitted here is the SHAPE-ONLY shape (no `relationships:`). PR2's
  type validator runs in Phase A mode (W003 warning, not T003 error)
  so legacy relationship blocks demoted at this PR still warn rather
  than break CI; PR8 flips library/ to Phase B.
- **PR5 fixture set grows from 13 → 22 → 31**: T01b adversarial
  control (Phase 3), T14/T15/T16/T17/T18/T18b/T19/T22/T23 (Phase 3),
  then T05/T06/T07 RESHAPED + T05a/T06a/T07a heuristic-fallback
  regression guards + T24/T25/T26/T27/T28/T29/T30/T31/T32/T33
  (Phase 4 marker + linkage). T08 deferred via `status: deferred`.
- **PR6 — unchanged scope**, but its acceptance gate now runs PR8
  validators (T003 on every library `meta.yml`, G201 over every
  graph.yml, I101/W004 over every instance) before tagging.

### Total envelope

~53h vs ~30h baseline. Delta: +23h to land the marker + linkage
architecture. The probe (no skills/_data workaround needed) saved
~2h of T20/T21 work in PR1.1 that would otherwise have been
in-scope.

### Out-of-scope items unchanged

T8 helix-web fixture, slash-namespace policy, multi-workspace cwd
switches, synthetic-corpus perf fixture, DDx `graph_node:` rename
fixture, semantic-quality judgments, cross-major library/methodology
drift — all remain v1.1+.

---

## §4 Fixture inventory delta

Phase 5 (commit `b7487c0a`) added 13 new fixtures and reshaped 3.
Counts below relative to the PR5 13-fixture baseline from the
2026-06-04 readiness report.

### Added (10 new linkage + marker fixtures)

| Fixture | Asserts | Class |
| ------- | ------- | ----- |
| T24-instance-edge-respects-graph | Positive baseline: instance edge resolves; validator exits 0 | I (clean) |
| T25-instance-edge-violates-graph | Disallowed type-pair edge → G201 + allowed-kinds hint | G |
| T26-instance-edge-target-missing | Unresolved id → I101 + nearest-ids + `status: planned` hint | I |
| T27-cross-methodology-edge | `helix:prd informs helix-infra:change-intent` resolves clean | I (clean) |
| T28-nested-marker-warning | Stray nested `.helix.yml` under `services/api/` → M010 once | M (warn) |
| T29-external-edge-required-rejected | `external_edges[].required: true` → G104 at graph-load | G |
| T30-library-major-bump-deprecation | Instance pinned at v1, library now v2, new required section → I010 warning (not error) | I (warn) |
| T31-status-planned-forward-edge | `status: planned` to unauthored target → I103 (warn), not I101 | I (warn) |
| T32-frontmatter-write-contract | Skill edit preserves `depends_on:` + `x-team-owner:` byte-equivalent | structural |
| T33-marker-root-missing | `root: docs/helix/` directory absent → M006 hard stop + `--allow-empty-scope` hint | M |

### Added (3 fallback regression guards)

| Fixture | Asserts | Class |
| ------- | ------- | ----- |
| T05a-marker-absent-product-heuristic | `.helix.yml` absent + product tree → heuristic activates helix + banner | banner |
| T06a-marker-absent-tf-heuristic | `.helix.yml` absent + TF file → heuristic activates helix-infra | banner |
| T07a-marker-absent-mixed-banner | `.helix.yml` absent + mixed tree → disambiguation banner (frozen §7.5 behavior) | banner |

These three lock the frozen-heuristic fallback so a future refactor
of activation cannot regress existing HELIX installs that have no
marker.

### Reshaped (3 — previously precedence-only)

| Fixture | Was | Now |
| ------- | --- | --- |
| T05-product-shaped-precedence | Heuristic precedence: product wins under mixed tree | Marker declares both; `defaults.methodology` resolves; `--scope` flag silences the other |
| T06-tf-file-precedence | Heuristic: TF file wins | Marker declares helix-infra ONLY at `infra/terraform/`; product tree present but uncovered → helix-infra activates without ambiguity |
| T07-mixed-repo-disambiguation | Banner under mixed tree | Marker declares both at scoped roots (`services/web/docs/helix/`, `services/web/infra/terraform/`); cwd-under-scope picks per §1.5 resolution chain |

### Deprecated / removed

None outright. T08 (helix + helix-web cross-methodology routing)
remains `status: deferred`. T20 / T21 (skills/_data workaround)
remain in the fixture set but are not gating PR1 anymore (probe
result: T13 is on-path).

### Net fixture inventory

- **Active gating:** T01–T07, T09–T19, T22–T33 (31 fixtures including
  T05a/T06a/T07a and T12b/T18b).
- **Deferred:** T08 (helix-web), T20/T21 (skills workaround unless
  T13 regresses).
- **PR5 runner contract:** `<results>/<id>/*.stream.jsonl` +
  `*.prose.txt` artifacts on failure; 10s/100MB defensive ceiling per
  validator invocation.

---

## §5 Next concrete action

Land PR1 (monorepo reorganization) per the implementation plan and run
T01 / T13 against the resulting tree to confirm the no-skills
`plugin.json` probe holds end-to-end on a fresh user environment.

---

## §6 Open questions for the user

1. **Land PR7+PR8 together or sequentially?**
   - (a) Sequential: PR7 (marker only) → soak in CI → PR8 (linkage).
     Pro: smaller blast radius per merge; con: PR7 ships a validator
     that has no graph to validate against the new shape, so its
     instance-mode exit-code contract is half-tested in isolation.
   - (b) Together: ship as a stacked pair, both green together. Pro:
     the validator's instance-mode exits I/G/T are exercised against
     real fixtures from day one. Con: larger review surface.
   - Current plan assumes (b). Confirm.

2. **Transition matrix cadence (§5.4 of design) — 30/60 days or
   tie to releases?**
   - (a) Calendar-pinned: Phase A → Phase B at +30 days, Phase B →
     Phase C at +60 days (current text).
   - (b) Release-pinned: Phase A in library 1.0.0, Phase B in library
     1.1.0 whenever it ships, Phase C in 1.2.0 whenever that ships.
   - (c) Operator-pinned: `helix_version:` in marker is the only
     opt-in; library never auto-upgrades severity.
   - Calendar pinning matches the FINAL plan's "deprecation window
     protocol" intent but couples library shipping to clock time.

3. **Default for instance-mode `--cross-methodology-edges` (§4.2)?**
   - (a) `warn` (current default): unknown / inactive target methodology
     emits I120 / I121 but exits 0.
   - (b) `deny`: any cross-methodology edge to an inactive or
     uninstalled methodology is an error.
   - (c) `allow`: silent. Drops S6 entirely.
   - (a) preserves operator agency; (b) is the strict reading of the
     verification-exit-gate memory.

4. **Migration script auto-PR or dry-run only?**
   - (a) Migration script ships `--dry-run` only; humans hand-apply
     the suggested edits and open the PR.
   - (b) Migration script ships `--dry-run` (default) AND `--apply`
     that writes edits in place; CI in consumer repos runs
     `--dry-run --require-clean` to surface drift.
   - (b) is what the plan currently assumes; (a) is the conservative
     fallback if `--apply` risk is too high for first cut.

5. **Should PR4 (DDx bead schema bump) land before or after the
   marker work?**
   - (a) Keep PR4 between PR3 and PR5 as the plan currently has it,
     so bead corpus is clean before the bench gate goes live.
   - (b) Move PR4 to AFTER PR8, so beads can carry `graph_node:`
     references that are validated against the new graph.yml shape
     from the start.
   - (c) Move PR4 INTO PR1 (alongside reorganization) per the readiness
     report's question #3.
   - Current plan: (a). The graph_node guard works fine without the
     new graph.yml shape; tightening it onto graph.yml comes free in
     PR8 if (a) is chosen.

---
