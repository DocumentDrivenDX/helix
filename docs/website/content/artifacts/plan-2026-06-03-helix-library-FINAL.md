---
title: "FINAL Plan: helix-library Split — REVISED POST-MONOREPO 2026-06-04"
slug: plan-2026-06-03-helix-library-FINAL
weight: 740
activity: "Design"
source: "02-design/plan-2026-06-03-helix-library-FINAL.md"
generated: true
---
# FINAL Plan: helix-library Split — REVISED POST-MONOREPO 2026-06-04

- **Date:** 2026-06-04 (synthesized post-review, revised post-monorepo decision)
- **Status:** Ready to execute (test-first; bench fixtures gate implementation)
- **Companion docs:**
  - Design (full): [design-2026-06-03-helix-library-split.md](/artifacts/design-2026-06-03-helix-library-split/)
  - Migration plan (full): [plan-2026-06-03-helix-library-migration.md](/artifacts/plan-2026-06-03-helix-library-migration/)
- **Review:** adversarial review folded in (issues 1, 2, 3, 4 high-severity
  addressed in-design; issues 5–9 medium-severity addressed; issues 10–12
  low-severity surfaced and absorbed).
- **2026-06-04 amendment:** monorepo topology + test-first principle adopted.
  Family lives in a single repo with `library/`, `product/`, `infra/`
  subdirectories. See §0 below.

This is the file to read first. It answers:

1. Do we go ahead with this architecture?
2. What is the next concrete action?
3. What risks am I signing up for, plainly?

---

## 0. Monorepo Topology + Test-First (2026-06-04 revision)

The family lives in the existing `helix/` repo as a monorepo. Top-level
layout after the reorganization (which is a SEPARATE, user-approved
workflow — NOT part of this planning workflow):

```
helix/                          # the monorepo
├── .claude-plugin/
│   └── marketplace.json        # ONE marketplace lists 3 plugins
├── library/                    # data plugin (no SKILL.md)
│   ├── .claude-plugin/plugin.json
│   ├── types/                  # 30 promoted artifact types
│   ├── concerns/               # shared concerns
│   └── scripts/                # validator + renderer
├── product/                    # current helix methodology, renamed
│   ├── .claude-plugin/plugin.json
│   ├── skills/helix/
│   └── workflows/
├── infra/                      # absorbed from helix-infra repo
│   ├── .claude-plugin/plugin.json
│   ├── skills/helix-infra/
│   └── workflows/
├── tests/                      # bench fixtures (test-first)
│   └── fixtures/
└── docs/                       # docs/helix, docs/website, etc.
```

**Users install whichever plugins they want via the single `helix-family`
marketplace.** `helix-infra` as a standalone GitHub repo is absorbed (or
deprecated with a README redirect pointing at the monorepo).

### What simplifies under monorepo

- **Per-type semver (design §4.5):** no longer required. Everything ships
  from a single commit; library and methodologies cannot drift in flight.
  Semver stays OPTIONAL as a documents-on-disk compatibility hint
  (`library_type_version` in frontmatter still records the version a doc
  was authored against), but the library MINOR/MAJOR gates on methodology
  releases are dropped. Family ships in lockstep at every commit.
- **`validator_contract_version` handshake (design §6.2):** removed. One
  tree, one validator, one CI. The handshake existed to catch cross-repo
  drift that can no longer happen.
- **Three-step resolution chain (design §7.3):** collapses. The library is
  always at a well-known relative path (`../library/` from any methodology
  root, or `<repo-root>/library/`). Resolver tries that path first; only
  falls back to `~/.claude/plugins/helix-library/` for installs where the
  user took a single methodology plugin without the library co-resident.
- **DDx bead schema migration (Phase D0):** still real (DDx is a separate
  surface), but lands in the same monorepo PR cadence as the methodologies.
- **Per-repo plugin.json/marketplace.json (design §7.2):** one
  `marketplace.json` at the monorepo root co-lists three plugin entries;
  per-plugin `plugin.json` files stay under each subdirectory.

### What stays the same

- Library/methodology architectural split (data plugin vs methodology overlay).
- Two-namespace scheme (`library:` / `local:`).
- `graph.yml` per methodology.
- Edge model (`requires` / `informs` / `may_surface`).
- Co-activation precedence rules + bench fixtures (now MORE important
  because the family is test-first — see below).
- Additive-only overrides; multi-line overrides via `_overlays/<binding-id>/`.
- Generated activity READMEs.
- ADR as a single library type with section_aliases.
- 30 types promoted in v1; `architecture` and `contract` stay product-local.

### Test-first principle

Bench fixtures are written FIRST, in a separate workflow phase, BEFORE any
reorganization or migration. The fixtures double as the executable spec
for the family architecture:

- Co-activation precedence fixtures (T1–T4 from the test matrix).
- Resolver fallback fixtures (T5–T7).
- Override merge fixtures (T8–T9).
- Single-plugin install fixtures (T10–T11).
- Negative-control fixtures (T12–T13).

The migration is "done" when all 13 fixtures pass. Phase 5 of THIS
workflow run authors the fixture suite; Phase 6 writes the runner. No
reorganization happens in this workflow.

### Revised migration shape (replaces §3 below)

The 14-PR / 55h plan in §3 was sized for three separate repos with
per-repo CI, per-type semver bookkeeping, and a multi-step resolution
chain to debug across repos. Monorepo collapses most of that. New shape:
**~6 PRs / ~25–30h**:

1. **Reorganize.** Move existing helix tree to `product/`. Scaffold empty
   `library/` and `infra/`. One CI pipeline at the monorepo root. One
   marketplace.json at the monorepo root. (~4h)
2. **Promote 30 artifact types to `library/`.** Copy/strip per design §3
   and §4.1; add section_aliases for ADR. (~5h)
3. **Absorb helix-infra into `infra/`.** Move tree from the `helix-infra`
   repo; add `methodology.yml` + `graph.yml`; deprecate the old repo with
   a README redirect. (~4h)
4. **DDx bead schema (`graph_node:` field).** Same as old Phase D0, but
   the methodologies are in the same repo so the field can be wired up
   end-to-end in one PR. (~2h)
5. **Verification.** Run the bench fixture suite from this workflow. All
   13 fixtures green. (~6h)
6. **Tag family release.** One tag, one marketplace publish. (~2h)

Total: ~23h baseline; with normal slippage budget ~25–30h. Roughly half
the previous estimate, mostly from collapsing the three-repo CI/release
overhead and dropping the validator handshake.

The §3 table below is preserved as a historical record but the §0
shape is the active plan.

---

## TL;DR

**Go.** Build `helix-library` as a data-only Claude Code plugin that holds
30 universal artifact types. Reshape `helix` and `helix-infra` as thin
methodology overlays that own activities, concerns, principles, and the
document graph (`graph.yml`). The two-namespace scheme (`library:` /
`local:`) keeps resolution unambiguous; the validator lives in the library
and is invoked by methodologies through a resolution chain, eliminating
by-copy drift. Per-type semver with a one-minor deprecation window prevents
"library 1.0.5 bricks every in-flight ADR overnight."

**Effort:** ~55 agent-hours (~7 days), gated per-phase. The review surfaced
real footguns; the design now addresses them. No remaining HIGH blockers.

---

## 1. Decision

**Proceed with the split,** with the following review-folded amendments
relative to the original design:

| Amendment | Source review issue | Where it lives now |
| --- | --- | --- |
| Per-type semver + deprecation-window protocol | Issue 1 | Design §4.5 |
| Co-activation precedence rules + bench fixture | Issues 2, 7 | Design §7.5; Plan D2 |
| Full edge model (`requires` / `informs` / `may_surface`) + worked `allowed_cycles` | Issue 3 | Design §6.1.1, §6.1.2 |
| Validator OWNED BY library, methodologies invoke via resolution chain; `validator_contract_version` handshake | Issue 4 | Design §6.2; Plan A1, B1, C1 |
| Consumer repo migration (path shim, migration script, deprecation window) | Issue 5 | Design §12 |
| Forking a library type (shadowing rules, reverse migration) | Issue 6 | Design §4.6 |
| New-type promotion workflow (local first, library MINOR additive) | Issue 8 | Design §3.1; §9 tradeoff 9 clarified |
| Section_aliases semantics tightened (validator accepts canonical OR alias) | Issue 9 | Design §10 resolved Q2 |
| Setup-gap behaviour for existing docs (read-only-OK, new authoring blocked) | Issue 10 | Design §7.2 already covers; doc on first invocation |
| Phase C effort buffer (+50%) and pre-split graph.yml | Issue 11 | Plan Phase C heading; §10 resolved |
| DDx bead schema (`graph_node:` field) lands BEFORE D2 | Issue 12 | Plan Phase D0 |

**What did NOT change.** The core architecture from the original design holds:

- helix-library is a DATA plugin with no SKILL.md.
- Two namespaces (`library:` / `local:`) with bare-slug rejection.
- Additive-only overrides on graph nodes; multi-line overrides via
  `_overlays/<binding-id>/`.
- Activity READMEs generated from `graph.yml` + `narrative.md`.
- ADR is ONE library type with a superset of sections + `section_aliases`.
- 30 types promoted in v1; `architecture` and `contract` stay HELIX-local
  until a second consumer emerges.

---

## 2. Next Concrete Action

> NOTE: superseded by monorepo decision 2026-06-04. The next concrete
> action is no longer "create a separate helix-library repo." It is:
> finish authoring the bench fixture suite (Phase 5 of the current
> planning workflow), then run the reorganization PR (revised migration
> step 1 in §0). The original action is preserved below for audit.

**Create the `helix-library` repository skeleton (Plan §A1) and land the
validator + `validator_contract_version` handshake in that same first PR.**

Concretely, in a fresh `helix-library/` git repo at the same level as
`helix/` and `helix-infra/`:

```
helix-library/
├── .claude-plugin/plugin.json          # name=helix-library, NO skills field
├── .claude-plugin/marketplace.json     # mirrors family marketplace
├── README.md                            # "data tree, no skill"
├── CHANGELOG.md                         # 0.1.0 entry
├── types/                               # (empty; A2 populates 30 types)
├── concerns/                            # (empty; A3 populates)
└── scripts/
    ├── CONTRACT_VERSION                 # contains "1"
    ├── validate_meta.py                 # py3-stdlib meta.yml validator
    ├── helix_graph_check.py             # graph validator (consumed by methodologies)
    └── helix_graph_render.py            # activity README renderer
```

Verification gate before moving on:

- `python3 scripts/validate_meta.py types/` exits 0 on empty tree.
- `python3 scripts/helix_graph_check.py --self-test` exits 0.
- `plugin.json` parses; `marketplace.json` parses.
- Repo can be added as a Claude Code marketplace and `helix-library` plugin
  installs into `~/.claude/plugins/helix-library/`.

This is one PR. Subsequent PRs execute Plan §A2 (promote 30 types),
§A3 (promote shared concerns), §A4 (tag v0.1.0). Only after Phase A green
does helix-infra (Phase B) begin.

---

## 3. Phases at a Glance

> NOTE: superseded by monorepo decision 2026-06-04. The 14-PR / 55h
> sibling-repo plan below is preserved as audit. The active plan is the
> ~6-PR / ~25-30h shape in §0. The phase letters (A/B/C/D) and the
> verification gates still describe the WORK in each shape; only the PR
> count and per-repo ceremony change.

| Phase | Goal | PRs | Hours | Gate |
| --- | --- | --- | --- | --- |
| A | Stand up helix-library + validator | 1 (skeleton+validator) → 1 (types) → 1 (concerns) → 1 (publish v0.1.0) | ~10 | A4 verification: marketplace install works on clean workspace |
| B | Migrate helix-infra (the small one, proves the contract) | 1 (graph+methodology) → 1 (artifact moves+SKILL.md update) → 1 (publish v0.2.0) | ~10 | B5 verification: full intent→plan→apply walk on a fresh IaC repo |
| C | Migrate helix per-activity (pre-split graph.yml from day one) | 1 (graph+methodology) → 6 (one per activity) → 1 (skill update) | ~27 | Each activity PR: `just check-graph` + bench dispatch passes; at least one existing doc per migrated type validates |
| D | DDx schema, family verification, docs | 1 (DDx `graph_node:` field) → 1 (verification+docs) | ~8 | D2 negative test: uninstall library, setup-gap fires; co-activation fixtures pass |
| **Total** | | **~14 PRs** | **~55h** | |

Each Phase B/C PR is independently revertable. The methodology stays
working between PRs because graph.yml and library coexist with unmigrated
activity directories during the transition.

---

## 4. Risks I'm Signing Up For (plainly)

These are the risks that survived the review. Listed in plain language, with
how the design handles each.

1. **The Claude Code plugin loader might not mount sibling plugins under
   `~/.claude/plugins/<name>/` predictably.** If hashed paths are used, the
   sibling-dev fallback breaks and we fall to the vendored-release fallback.
   **Mitigation:** verify on a real install during Phase A1; the resolution
   chain has three steps for exactly this reason; vendored fallback always
   works.

2. **`plugin.json` with no `skills:` field may be rejected by Claude Code.**
   The library is data-only by design. **Mitigation:** preflight check at
   A1. If rejected, ship a `skills/_data/SKILL.md` whose frontmatter
   describes a deliberate no-route (negative trigger) but still mounts the
   tree. Tradeoff: a tiny "skill" that exists only to mount data.

3. **Library MINOR adds a required section and someone forgets the
   deprecation-window protocol.** **Mitigation:** the library repo's CI
   enforces the protocol: any PR that introduces a new `required_section`
   without `severity: warning` AND a CHANGELOG note flagging the warning
   cycle fails the lint. Per-type semver bumps are mechanical.

4. **Two methodology skills active simultaneously route incorrectly for
   generic verbs.** This is the normal install state. **Mitigation:** §7.5
   precedence rules + `tests/fixtures/co-activation/` bench. The
   disambiguation banner is informative, not silent. `HELIX_METHODOLOGY`
   override always wins. Fixture failures block release.

5. **DDx beads created today reference on-disk artifact paths; after
   migration those paths change.** **Mitigation:** Phase D0 lands the
   `graph_node:` field in DDx bead frontmatter BEFORE bench dispatch.
   Resolver translates legacy on-disk paths to graph nodes for existing
   beads. Path shim (§12) handles tooling reads for one minor cycle.

6. **Phase C is large.** 47 types, 7 activities, ~49 concerns. Even with
   the 50% buffer, this can blow up. **Mitigation:** per-activity PRs;
   each PR independently mergeable. Pre-split `graph/<activity>.yml` from
   day one. Bench dispatch is the per-PR gate, not just lint.

7. **Vendored consumer forks of HELIX continue to use the old
   `workflows/activities/<NN>/artifacts/` layout indefinitely.**
   **Mitigation:** accepted. Vendored snapshots are by definition pinned;
   the migration only affects upstream. Documented in §12.3 and risk register.

8. **graph.yml grows large and unreviewable in HELIX.** **Mitigation:**
   pre-split per-activity from day one (`graph/00-discover.yml`,
   `graph/01-frame.yml`, etc.). Validator reads the directory.

9. **Library version pinning is "advisory" — a user can install helix
   without helix-library.** **Mitigation:** setup-gap message on first
   invocation; documents on disk continue to validate against locally cached
   schemas; new authoring is blocked until the library is installed.

10. **Section aliases or override semantics could subtly break corpus
    validation.** **Mitigation:** A2 verification runs the new resolved
    `adr` spec against the entire existing HELIX `docs/adr/` corpus AND
    helix-infra's ADR corpus before A4 publishes the library. Any failure
    blocks publication.

11. **Validator-by-copy drift was a real footgun in the v1 plan. We
    eliminated it by moving the validator to the library, but the resolution
    chain now has a tighter dependency on the chain finding the library at
    `just check-graph` time.** **Mitigation:** `resolve-library-root.sh`
    has the same three fallbacks as the skill prose. A graph check that
    cannot find a library fails loudly, with the install command in the
    error.

12. **Phase C estimates may still be optimistic despite the 50% buffer.**
    **Mitigation:** the verification gate per-activity is "bench dispatch
    succeeds in this activity," not "diff applied cleanly." If an activity
    takes longer, the next activity PR doesn't start. The migration is
    pull-driven; the family is in a usable half-state at every boundary.

What I am NOT signing up for:

- A general-purpose templating engine. The library is a catalog.
- Auto-resolving cross-major version drift. Family advances at major
  boundaries together.
- A replacement for DDx as the runtime. DDx still owns beads/queue/dispatch.

---

## 5. Out of Scope for v1 (deferred follow-ups)

- Cross-methodology shared overlay tree (`helix-family-overlays`).
- Resolver as a stand-alone CLI binary.
- Performance work on graphs above ~100 nodes.
- Auto-migration of forked-then-re-promoted documents.
- `principles` and `concerns` content authoring guidance (shape-only types
  ship in v1; content lives in methodologies).

---

## 6. Acceptance (when the migration is "done")

1. `helix-library` v1.0.0 published with 30 types + shared concerns;
   installable via the family marketplace.
2. `helix-infra` v0.2.0 and `helix` v?.?.0 published with
   `requires: [helix-library]`; their `workflows/` trees match the design
   §5.1 skeleton.
3. `just check-graph && just render-readmes && git diff --exit-code`
   passes in both methodology repos.
4. Bench dispatch succeeds in all activities of both methodologies; ADR
   overlays apply correctly.
5. Negative test (uninstall library) produces the documented setup-gap
   message; no template improvisation.
6. Co-activation bench fixtures pass for all four `tests/fixtures/co-activation/`
   scenarios.
7. DDx beads accept `graph_node: <methodology-id>:<node-id>` frontmatter.
8. `docs/install/helix-library.md` exists; methodology READMEs link to it.
9. All existing HELIX and helix-infra documents validate unchanged against
   the resolved specs.

---

## 7. Where to read next

- For full architectural reasoning + worked examples: read the design doc
  (`design-2026-06-03-helix-library-split.md`).
- For per-step file lists, verification commands, rollbacks, and the full
  risk register: read the migration plan
  (`plan-2026-06-03-helix-library-migration.md`).
- For review history: the adversarial review object is embedded in the
  Phase 5 workflow output that produced this file; key issues are
  cross-referenced in §1 of this doc.
