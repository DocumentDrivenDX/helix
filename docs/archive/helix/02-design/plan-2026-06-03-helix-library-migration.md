# Plan: helix-library Migration

- **Date:** 2026-06-03 (drafted), 2026-06-04 (synthesized), 2026-06-04 (monorepo amendment)
- **Status:** Proposed (superseded by monorepo plan — see §0)
- **Design doc:** [design-2026-06-03-helix-library-split.md](./design-2026-06-03-helix-library-split.md)
- **Entry-point doc:** [plan-2026-06-03-helix-library-FINAL.md](./plan-2026-06-03-helix-library-FINAL.md) §0 carries the active monorepo plan.
- **Scope:** Execute the architectural refactor: stand up `helix-library`,
  migrate `helix` and `helix-infra` onto it, verify family-wide.

This plan assumes the design doc has been reviewed and accepted (or the
review pass surfaced no blocking changes). Each step lists the files
touched, verification command, rollback, and estimated effort in
agent-hours.

---

## 0. 2026-06-04 Amendment: Monorepo Plan (replaces phases A–D below)

The family is reorganizing as a monorepo (one repo, three subdirs:
`library/`, `product/`, `infra/`). The 14-PR / 55h sibling-repo plan
below is preserved as audit; the active plan is below, and is also
the §0 plan in
`plan-2026-06-03-helix-library-FINAL.md`. Test-first: bench fixtures
land BEFORE reorganization.

### Test-first prerequisite (separate workflow)

Bench fixture suite (T1–T13 from the test matrix) is authored in a
dedicated planning workflow, with a runner. The suite defines the
"done" gate for the migration. Implementation cannot start until the
fixtures are red against the current tree (and pass once the migration
lands).

### Phase 1: Reorganize (~4h, 1 PR)

- Move existing helix tree to `product/`.
- Scaffold empty `library/` and `infra/` directories with placeholder
  `.claude-plugin/plugin.json`.
- One CI pipeline at the monorepo root.
- One `.claude-plugin/marketplace.json` at the monorepo root listing
  three plugins (subdirectories of the same repo URL).
- Verification: existing CI still green; `product/` skill still
  activates against the existing test fixtures.

### Phase 2: Promote 30 artifact types to `library/` (~5h, 1 PR)

- Copy types from `product/workflows/artifacts/` (and a few from
  `infra/` once Phase 3 lands — order may swap if helpful) into
  `library/types/`.
- Strip `activity:`, `output.location`, `workflow.approvers`,
  `relationships.informed_by`, `relationships.informs` per design §4.1.
- For ADR specifically: union the section lists; add `section_aliases`.
- Verification: meta validator green on `library/types/`; existing
  HELIX ADRs still validate under the resolved spec.

### Phase 3: Absorb helix-infra into `infra/` (~4h, 1 PR)

- Move the helix-infra repo tree into `infra/`.
- Add `methodology.yml` + `graph.yml` per design §5.2 and §6.1.
- Add the ADR overlay at `infra/workflows/artifacts/_overlays/adr@02-plan/`.
- Deprecate the standalone `helix-infra` GitHub repo with a README
  redirect at the repo root.
- Verification: `just check-graph` green for infra; bench co-activation
  fixtures still red until Phase 5.

### Phase 4: DDx bead schema `graph_node:` field (~2h, 1 PR)

- Same as old Phase D0. Add `graph_node: <methodology-id>:<node-id>`
  to DDx bead frontmatter schema; CLI accepts `--graph-node`.
- Verification: bead created with `--graph-node infra:change-plan`
  round-trips through the queue.

### Phase 5: Verification (~6h, 1 PR)

- Run the full bench fixture suite (T1–T13).
- All fixtures green is the gate. Any red fixture blocks the family
  release.

### Phase 6: Tag family release (~2h, 1 PR)

- Tag the monorepo at `helix-family/v1.0.0` (or whatever the chosen
  scheme is — see FINAL plan §0 versioning note).
- Publish marketplace.json.
- Update install docs.

**Total: ~23h baseline, ~25-30h with slippage.** Replaces the ~55h
sibling-repo plan below.

---

## Phase A — Stand up `helix-library` (4 steps, ~10h)

> NOTE: Phases A–D below superseded by monorepo plan §0. Preserved as
> audit and because the per-step file lists, verification commands, and
> rollback notes remain useful when executing the equivalent monorepo
> steps (Phase 1 reorganize ≈ A1 scaffolding; Phase 2 promote types
> ≈ A2; Phase 3 absorb infra ≈ B1+B2+B3+B4; Phase 4 DDx ≈ D0;
> Phase 5 verify ≈ D1+D2+D3).

> Review-fold: validator now ships IN the library (not by-copy per methodology).
> Phase A grows by ~2h to land the validator + `validator_contract_version`
> handshake before any methodology depends on it.


### A1. Create the `helix-library` repository skeleton

**Files added:**

```
helix-library/
├── .claude-plugin/plugin.json          # name=helix-library, no skills field
├── .claude-plugin/marketplace.json     # mirrors family marketplace, optional
├── README.md                            # "data tree, no skill"
├── CHANGELOG.md                         # version 0.1.0 — initial scaffold
├── types/                               # empty for now; A2 populates
├── concerns/                            # empty for now; A2 populates
└── scripts/
    ├── CONTRACT_VERSION                 # "1" — validator contract handshake
    ├── validate_meta.py                 # py3-stdlib meta.yml validator
    ├── helix_graph_check.py             # graph validator (consumed by methodologies)
    └── helix_graph_render.py            # activity README renderer (consumed by methodologies)
```

**Verification:**

- `python3 scripts/validate_meta.py types/` exits 0 on empty tree.
- `cat .claude-plugin/plugin.json | python3 -c 'import json, sys; json.load(sys.stdin)'` parses cleanly.

**Rollback:** Delete the repo. Nothing else depends on it yet.

**Effort:** ~1h.

---

### A2. Promote 30 universal artifact types into the library

**For each promoted type** (per design §3):

1. Copy `meta.yml`, `template.md`, `prompt.md`, `example.md` from the source
   location (HELIX or helix-infra) into `helix-library/types/<slug>/`.
2. Strip from `meta.yml`: `activity:`, `output.location` (move to
   `default_output.location`), `workflow.approvers`, `relationships.informed_by`,
   `relationships.informs`.
3. For ADR specifically: union HELIX's 4-section list with helix-infra's
   6-section list; add `section_aliases` per design §4.1.
4. Bump `schema_version: 1`, `version: 1.0.0`.

**Source-of-truth choices** (where the same type exists in both repos):

- `adr`: helix-infra superset for required_sections; HELIX template body as
  baseline (more thorough); aliases let HELIX corpus validate unchanged.
- `principles`: HELIX shape (helix-infra adapted from it).
- `concerns`: HELIX shape (singleton pattern shared).
- `runbook`: HELIX shape (module-guide is NOT a library type).
- All others: only one source exists, use it.

**Files added:** ~30 × 4 = ~120 files under `helix-library/types/`.

**Verification:**

- `python3 scripts/validate_meta.py types/` exits 0.
- For each promoted type, diff its old location vs new: only the stripped
  fields should be missing.
- Spot-check: load `types/adr/meta.yml`, confirm it validates the existing
  helix `ADR-001.md` and helix-infra `ADR-001.md` (if one exists) under the
  resolved spec (aliases applied).

**Rollback:** Delete `types/<slug>/`. Methodologies still have their copies.

**Effort:** ~3h.

---

### A3. Promote shared concern definitions into the library

For the security/compliance concern bundle (where shape and content overlap
across methodologies), copy `concern.md` + `practices.md` to
`helix-library/concerns/<slug>/`. Conservative choice for v1: promote ONLY
concerns whose content is methodology-agnostic. Methodology-shaped concerns
(the six IaC concerns; HELIX's product concerns) stay local.

**Verification:** load each promoted concern's `concern.md` — it should not
reference methodology-specific surfaces (no PRD, no change-plan, etc.).

**Rollback:** Delete `concerns/<slug>/`.

**Effort:** ~1.5h.

---

### A4. Publish `helix-library` v0.1.0

**Files added:**

```
helix-library/CHANGELOG.md                # 0.1.0 entry
helix-library/.claude-plugin/plugin.json   # version 0.1.0
```

**Verification:**

- Tag `v0.1.0` and push.
- Install in a clean Claude Code workspace via marketplace:
  `/plugin marketplace add DocumentDrivenDX/helix-marketplace` then
  `/plugin install helix-library`. Confirm the tree mounts at
  `~/.claude/plugins/helix-library/`.

**Rollback:** Untag and delete the GitHub release. Library is unused by any
methodology yet.

**Effort:** ~2.5h (includes marketplace.json updates and CI for the lib repo).

---

## Phase B — Migrate `helix-infra` (5 steps, ~10h)

Migrating helix-infra first because it is smaller (5 artifact types, 3
activities) and the family's newer member with cleaner shape.

### B1. Add `methodology.yml` and `graph.yml`

**Files added:**

```
helix-infra/workflows/methodology.yml         # per design §5.2
helix-infra/workflows/graph.yml               # full worked example, design §6.1
helix-infra/scripts/resolve-library-root.sh   # walks the §7.3 chain
# NOTE: validator + renderer live in helix-library, NOT here (review-fold issue 4)
```

**Files changed:** `justfile` gains `check-graph` and `render-readmes`
recipes.

**Verification:**

- `just check-graph` exits 0 (all nodes resolve, no cycles).
- `just render-readmes` produces no diff against current
  `activities/*/README.md` after manually folding `narrative.md` content
  out of the current README (see B3).

**Rollback:** Delete the three new files and revert justfile.

**Effort:** ~2h.

---

### B2. Add inline ADR overlay

**Files added:**

```
helix-infra/workflows/artifacts/_overlays/adr@02-plan/prompt-append.md
helix-infra/workflows/artifacts/_overlays/adr@02-plan/template-append.md
```

Content: the concern-traceability prompt fragment and template section, lifted
from the current `workflows/activities/02-plan/artifacts/adr/{prompt.md,template.md}`
diff vs HELIX's ADR (the additive content only).

**Verification:** `python3 scripts/helix_graph_check.py` resolves `library:adr`
with overrides; the merged template includes the concern_traceability section
heading.

**Rollback:** Delete the `_overlays/adr@02-plan/` directory.

**Effort:** ~1h.

---

### B3. Migrate methodology-local artifact types to `workflows/artifacts/`

**Files moved:**

```
workflows/activities/01-intent/artifacts/change-intent/
  → workflows/artifacts/change-intent/

workflows/activities/02-plan/artifacts/change-plan/
  → workflows/artifacts/change-plan/

workflows/activities/03-apply-verify/artifacts/apply-evidence/
  → workflows/artifacts/apply-evidence/

workflows/activities/03-apply-verify/artifacts/module-guide/
  → workflows/artifacts/module-guide/
```

For each: strip `activity:` from `meta.yml` (activity placement now in
`graph.yml`); strip `relationships.informed_by` / `relationships.informs`
(now in graph edges); keep everything else.

**Files deleted:**

```
workflows/activities/01-intent/artifacts/    # entire subtree
workflows/activities/02-plan/artifacts/      # entire subtree (incl. adr/)
workflows/activities/03-apply-verify/artifacts/   # entire subtree
```

**Files added:**

```
workflows/activities/01-intent/activity.yml
workflows/activities/02-plan/activity.yml
workflows/activities/03-apply-verify/activity.yml
workflows/activities/01-intent/narrative.md   # prose split from old README
workflows/activities/02-plan/narrative.md
workflows/activities/03-apply-verify/narrative.md
```

`README.md` files in each activity are regenerated from `graph.yml` +
`narrative.md` by `helix_graph_render.py`.

**Verification:**

- `git diff --stat workflows/` shows the rename of 4 directories + deletion
  of activity-level `artifacts/` subtrees + addition of `activity.yml` and
  `narrative.md` per activity.
- `just check-graph` still passes.
- `just render-readmes && git diff --exit-code workflows/activities/*/README.md`
  passes (generated READMEs match committed).
- Open one current `change-intent` document; load via the resolver and
  confirm validation passes against the new `meta.yml`.

**Rollback:** `git revert` the migration commit. The old directory layout
returns; graph.yml becomes stale but does not break anything because the
skill prose hasn't been updated yet.

**Effort:** ~3h.

---

### B4. Update `skills/helix-infra/SKILL.md`

**Files changed:** `skills/helix-infra/SKILL.md`.

- Add frontmatter `library_root: ./vendor/helix-library/` (vendored release
  fallback) or rely on resolution chain.
- Replace §"Where the methodology lives" with design §7.3 prose (catalog
  resolution chain, setup-gap behavior).
- Update §Catalog Resolution if present, or add it.
- Bump version to 0.2.0.

**Verification:**

- Bench dispatch: install helix-infra alone (no library), invoke the skill,
  confirm setup-gap message names `helix-library`.
- Bench dispatch: install both, invoke `/helix-infra plan`, confirm ADR
  template resolves through `library:adr` with concern overlay applied.

**Rollback:** Revert the SKILL.md change. Tests pinned to old prose still
pass.

**Effort:** ~2h.

---

### B5. Tag `helix-infra` v0.2.0 and publish

**Files changed:** `.claude-plugin/plugin.json` (version 0.2.0, `requires:
[helix-library]`), `CHANGELOG.md`.

**Verification:** marketplace install in a clean workspace; cold-start an
IaC repo and run the full intent → plan → apply path. All artifacts
produced, all validations pass.

**Rollback:** Untag v0.2.0; users continue on v0.1.x.

**Effort:** ~1h.

---

## Phase C — Migrate `helix` (7 steps, ~27h)

HELIX is the heavyweight: ~47 artifact types, 7 activities, ~49 concerns. The
migration is sequenced per-activity to keep PR sizes reviewable.

> Review-fold (issue 11): Phase C now carries a 50% buffer (~18h → ~27h)
> because per-activity bench dispatch + full-corpus validation are heavier
> than originally scoped. graph.yml is pre-split per-activity from day one
> to keep PRs reviewable.

### C1. Land `methodology.yml`, per-activity `graph/*.yml`

Same as B1 but for helix. The graph is pre-split into per-activity files
because a single file would exceed 500 lines once all 7 activities,
cross-cutting nodes, and overlays are declared.

**Files added:**

```
helix/workflows/methodology.yml
helix/workflows/graph/00-discover.yml
helix/workflows/graph/01-frame.yml
helix/workflows/graph/02-design.yml
helix/workflows/graph/03-test.yml
helix/workflows/graph/04-build.yml
helix/workflows/graph/05-deploy.yml
helix/workflows/graph/06-iterate.yml
helix/workflows/graph/_cross-cutting.yml   # concerns, principles, adr
helix/workflows/graph/_methodology.yml     # methodology header + allowed_cycles
helix/scripts/resolve-library-root.sh      # validator+renderer live in helix-library
```

**Verification:** `just check-graph` resolves all 30 library types and all
17 methodology-local types declared across the split graph files. Validator
loads the `graph/` directory and concatenates.

**Rollback:** Delete the four new files.

**Effort:** ~3h.

---

### C2. Per-activity migration: 01-frame

Pilot activity for the HELIX migration. Smallest in terms of library-type
density (12 library types, 5 local types).

**Files moved:** `workflows/activities/01-frame/artifacts/{local-type}/` →
`workflows/artifacts/{local-type}/` for the 5 HELIX-local types
(`prd`, `pr-faq`, `feature-registry`, `feature-specification`, `user-stories`).

**Files deleted:** `workflows/activities/01-frame/artifacts/{library-type}/`
for the 12 library-resolved types.

**Files added:** `workflows/activities/01-frame/activity.yml`, `narrative.md`.

**Verification:**

- `just check-graph` passes.
- One existing PRD document validates against the new local type.
- One existing risk-register document validates against `library:risk-register`
  (resolved through the vendored library).

**Rollback:** Revert the commit; previous directory tree returns.

**Effort:** ~2h.

---

### C3–C7. Per-activity migration: 00-discover, 02-design, 03-test, 04-build, 05-deploy, 06-iterate

Same pattern as C2, one PR per activity. Skipping detailed file lists — they
follow the design §3 split (which types are library, which are local) and the
inventory's `methodology_specific.helix` list.

Notable specifics:

- **02-design:** `adr` migrates to `library:adr` with a HELIX-side overlay
  for `ac_traceability_impact` (additive section + quality_check).
  `architecture`, `contract`, `data-design` stay local.
- **05-deploy:** `runbook` migrates to `library:runbook`.

**Verification per PR:**

- `just check-graph` passes.
- `just render-readmes` produces no diff (after migrating prose to
  `narrative.md`).
- At least one existing document of each type validates.
- A bench dispatch to the helix skill (frame mode or design mode depending
  on activity) produces the expected artifact via the new resolver.

**Rollback per PR:** `git revert` that activity's PR; downstream activities
remain unaffected because the graph still validates (just with the prior
activity's old paths).

**Effort:** ~3h per activity × 6 activities ≈ ~18h (review-fold: bumped 50%
to account for bench-dispatch overhead and corpus validation per activity).

---

### C8. Update `skills/helix/SKILL.md`

Same as B4 but for helix. Replace §Catalog Resolution prose with the design
§7.3 chain, bump version, add `requires: [helix-library]`.

**Verification:** bench dispatch to helix skill in all 7 modes, confirm
all artifacts resolve.

**Rollback:** Revert SKILL.md change.

**Effort:** ~1h.

---

## Phase D — Verification (4 steps, ~8h)

### D0. DDx bead schema addition (PRE-REQUISITE for D2)

Review-fold (issue 12, open question 7): before bench dispatch can produce
graph-node-referencing beads, the DDx bead frontmatter must accept a
`graph_node: <methodology-id>:<node-id>` field.

**Files changed:** `ddx/skills/ddx/SKILL.md` (bead schema doc); DDx CLI
bead-create path accepts `--graph-node`. Optional during migration;
required once both methodologies are on the new shape.

**Verification:** create a bead with `--graph-node helix-infra:change-plan`;
confirm frontmatter persists and queries by graph node return the bead.

**Effort:** ~2h.

---

### D1. Family-wide validator pass

**Verification:**

- In `helix-library`: every type's `meta.yml` validates against the
  `schema_version: 1` JSON schema.
- In `helix`: `just check-graph && just render-readmes && git diff --exit-code`
  passes.
- In `helix-infra`: same.
- Cross-check: for every `library:<slug>` in either methodology's graph.yml,
  the library publishes that slug at the pinned major.

**Effort:** ~1h.

---

### D2. Bench: dispatch each methodology, observe library resolution

For each methodology, run a full activity walk via `ddx agent run` against a
sample project. Specifically:

- helix-infra: change-intent → change-plan (with one ADR) → apply-evidence →
  module-guide. Confirm the ADR's concern-traceability section appears
  (overlay applied).
- helix: frame → design (with one ADR) → test → build. Confirm ADR's
  `ac_traceability_impact` section appears (HELIX overlay applied).
- Negative test: uninstall helix-library, re-dispatch, confirm setup-gap
  message names the missing plugin.
- **Co-activation fixture (review-fold issue 2):** install BOTH skills,
  run against `tests/fixtures/co-activation/{infra-only, product-only, mixed,
  dual-methodology}/` and assert the correct methodology wins per §7.5
  precedence rules. "Create an ADR" in `mixed/` fires the disambiguation
  banner.

**Effort:** ~4h.

---

### D3. Migration snapshot and documentation

**Files added:**

```
docs/helix/02-design/decisions/ADR-XXX-helix-library-split.md
helix-library/README.md                # final pass with marketplace screenshot
docs/install/helix-library.md          # how to install the family
```

**Verification:** documentation review; cross-link from helix and helix-infra
READMEs to the install doc.

**Effort:** ~2h.

---

## Total Estimated Effort

| Phase | Description                    | Hours |
| ----- | ------------------------------ | ----- |
| A     | Stand up helix-library         | ~10   |
| B     | Migrate helix-infra            | ~10   |
| C     | Migrate helix (with 50% buffer)| ~27   |
| D     | Verification + DDx + docs      | ~8    |
| **Total** |                            | **~55** |

Roughly 7 agent-days. Recommend Phase A in one PR, B as 2 PRs (graph + skill;
artifact moves), C as 8 PRs (one per activity, plus skill update; graph is
pre-split per-activity from day one), D as DDx-schema PR + verification PR.

---

## Risk Register

| Risk                                              | Likelihood | Impact | Mitigation                                                                                                                          |
| ------------------------------------------------- | ---------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------- |
| Claude Code plugin loader does not mount plugins as siblings under `~/.claude/plugins/`. | Med | High | Verify on a real install before Phase A4. If hashed paths, fall back to vendored-library distribution and drop chain steps 2a/2b. |
| `plugin.json` with `"skills": null` is rejected by CC. | Low | High | Pre-flight check during A1. If rejected, ship a minimal `skills/_data/SKILL.md` whose description routes nothing (negative trigger) but mounts the data tree. |
| ADR section_aliases don't apply in resolver, breaking existing HELIX ADR corpus. | Med | High | Implement and test aliases as part of A2; run validator against the full HELIX `docs/adr/` corpus before A4. |
| Methodology-local artifact moves break tooling that hardcodes `workflows/activities/<NN>/artifacts/<slug>/`. | Med | Med | Audit `scripts/` and `justfile` in both methodologies before B3/C2. Ship a one-shot symlink farm if needed; remove at v1.0. |
| Generated READMEs lose content that was previously hand-edited. | Med | Med | Before B3/C2, manually fold any non-redundant prose from each README into `narrative.md`. Validate first render is content-preserving. |
| Library version pinning is advisory, methodology installs against wrong major. | Low | High | Resolver checks `library/VERSION` (or `plugin.json.version`) against `methodology.yml.library.version_range` at activation, surfaces a clear error on mismatch. |
| graph.yml grows large and unreviewable. | Low | Med | helix graph.yml is ~250 lines; split per-activity files (`graph/<activity>.yml`) if a single file exceeds 500 lines. Defer to v1.1. |
| Bench passes but real users hit edge cases (sibling-checkout dev workflow, monorepo, vendored release). | Med | Med | The three-step resolution chain is explicitly designed for each mode; document each in `docs/install/helix-library.md`. |
| DDx workflows that assume the old artifact paths break. | Med | High | Audit DDx skill prose for `workflows/activities/.+/artifacts/` patterns before publishing; update DDx in parallel to methodologies. |
| HELIX migration is too large for a single iteration; partial migration leaves the family in a half-resolved state. | High | Med | Phase C is explicitly per-activity. Each PR is independently mergeable; the methodology continues to work between PRs because `graph.yml` and library coexist with unmigrated activity directories during the transition. |
| Cross-cutting ADR placement confuses users (where do I write a new one?). | Med | Low | SKILL.md prose names the nominal home (`02-plan` for helix-infra, `02-design` for helix) while clarifying ADRs may surface from any activity. |
| Vendored release builds drift from the upstream library between releases. | Low | Low | Vendoring is via `git subtree pull` automated in the methodology's release script; CI fails if `vendor/helix-library/VERSION` ≠ pinned major. |
| Orphaned consumer forks vendor old `workflows/activities/<NN>/artifacts/<slug>/` template paths. | Med | Low | Documented in design §12.3 as accepted: vendored snapshots continue to work; upstream cannot keep them in sync. `scripts/migrate_consumer_repo.py` (shipped in HELIX) reports hardcoded paths. |
| Library MINOR adds a required section that bricks in-flight documents in consumer repos. | Low | High | §4.5 deprecation-window protocol: new required sections enter as `severity: warning` for one minor cycle, promote to `blocking` only at next major. CI for library blocks any PR that ships a new blocking section without the warning cycle. |
| Both skills active in a mixed repo route the wrong methodology for a generic verb. | Med | Med | §7.5 precedence rules + `tests/fixtures/co-activation/` bench. Disambiguation banner on tie. `HELIX_METHODOLOGY` env override documented. |
| Validator drift between library and methodology (validator-by-copy footgun). | Eliminated | — | Validator lives in helix-library; methodologies invoke via resolution chain. `validator_contract_version` handshake hard-fails on mismatch. |

---

## Rollback Strategy

Each phase is independently revertable; the migration is sequenced so that
each Phase B/C PR leaves the family in a working state.

- **Phase A rollback:** delete the library repo. Methodologies are untouched.
- **Phase B rollback:** revert helix-infra to pre-migration; library remains
  but is unreferenced by helix-infra. Library still works for helix once
  Phase C completes (if it does).
- **Phase C rollback (per activity):** revert that activity's PR. The activity
  returns to its pre-migration directory layout; graph.yml entries for that
  activity are kept in sync with the revert via the PR.
- **Full rollback:** revert all helix-library install references in both
  methodology marketplaces. Methodologies return to standalone operation. The
  library repo can stay published as a no-op for future re-attempt.

---

## Acceptance Criteria

The migration is complete when:

1. `helix-library` v1.0.0 is published with 30 types and is installable via
   the family marketplace.
2. `helix-infra` v0.2.0 and `helix` v?.?.0 are published with
   `requires: [helix-library]` and their `workflows/` trees match the
   skeleton in design §5.1.
3. `just check-graph && just render-readmes && git diff --exit-code` passes
   in both methodology repos.
4. Bench dispatches succeed in all activities of both methodologies, with the
   correct overlays applied to ADRs and other contested types.
5. The negative test (uninstall library) produces the documented setup-gap
   message; no template improvisation occurs.
6. `docs/install/helix-library.md` exists and the methodology READMEs link
   to it.
7. All existing helix and helix-infra documents (ADRs, PRDs, change-plans,
   etc.) validate against the resolved specs without modification.
