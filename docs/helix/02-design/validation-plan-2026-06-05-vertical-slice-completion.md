# Validation Plan — Vertical Slice Completion

- **Date:** 2026-06-05
- **Status:** plan
- **Scope:** what's left to prove about the marker + linkage design after
  family-test/ commit `<this PR>` (13/13 static tests green)
- **Companions:**
  [design-2026-06-04-helix-family-marker-and-linkages.md](./design-2026-06-04-helix-family-marker-and-linkages.md),
  [family-marker-linkages-report-2026-06-04.md](./family-marker-linkages-report-2026-06-04.md).

## What's already proven

The 13/13 family-test suite locks: marker parsing + 4 hard-fail rules, graph parsing, type-mode `relationships:` forbidden, instance edge resolution against the graph, missing-target hint, `status: planned` forward refs, cross-methodology authorization via `external_edges`, `--cross-methodology-edges` warn vs deny.

## What's NOT yet proven — the gap list

The validation buckets below rank by load-bearing-ness. Bucket A is the
**load-bearing unknown that can invalidate the whole architecture.** B/C/D are
mechanical extensions that strengthen the slice. E and F are scale and
integration. Do A first.

---

### Bucket A — Skill activation (interactive, user-run)

**Question:** does Claude Code actually let a methodology skill drive
activation off `.helix.yml`? The design assumes the SKILL.md prose can
instruct the agent to read the marker and respect it — but no harness today
proves this. If activation can't be marker-driven, the design needs
fallback to slash-command-only and we lose the per-repo declaration win.

| Probe | What to set up | Pass criteria |
|---|---|---|
| **A1 — happy path** | Install `family-test/library/` + `family-test/methodology-product/` as plugins (`claude plugin marketplace add file:///.../family-test/library` etc.); workspace with `.helix.yml` listing `helix`; send prompt "Show me what methodologies are active in this repo." | Agent reads `.helix.yml`, responds naming `helix`. Stream-json shows `Read` tool_use against `.helix.yml`. |
| **A2 — negative control** | Same workspace, **remove** `.helix.yml`, same prompt. | Agent emits the fallback banner from design §1.3, OR clearly says no marker. Critically: does NOT improvise that helix is active. |
| **A3 — scope respect** | Workspace with `.helix.yml` listing helix scoped to `services/api/docs/helix/`. cwd outside that path; prompt "Create a PRD." | Agent declines or asks for scope clarification. Does NOT write into the wrong directory. |
| **A4 — multi-methodology** | `.helix.yml` listing helix + helix-infra at different scopes; prompt "What's the active methodology here?" (run twice — once with cwd under helix scope, once under helix-infra scope). | First invocation picks helix, second picks helix-infra. Per design §1.5 resolution chain. |
| **A5 — explicit override** | `.helix.yml` listing helix only; prompt prefixed `/helix-infra intent`. | Either rejects (helix-infra not in marker) OR honors the explicit `/` (design §1.5 rule 1). Either is defensible — the test pins which we chose. |

**How to run:** small interactive script you execute with `claude -p --output-format stream-json --bare`. One probe per scenario. Capture stdout. Parse for `Read .helix.yml` events and the agent's prose response.

**Effort:** ~2 hours including writing the harness.
**Blocking:** none — runnable today.
**Failure modes that matter:**
- Agent doesn't read `.helix.yml` at all → design needs marker as advisory + slash-command-required, not authoritative.
- Agent reads marker but ignores scope → scope is documentation, not enforcement; tighten validator-side scope checks.
- Multi-methodology routing is non-deterministic → freeze the §1.5 ordering and add a test fixture.

---

### Bucket B — Static validator extensions (mechanical, additive)

Adds to the family-test slice. Pure validator work.

| Probe | Fixture | Pass criteria |
|---|---|---|
| **B1 — I010 library major bump deprecation** | Two library versions: `library/types/prd/meta.yml` v1.0.0 with 7 required sections, archived `library-v2/types/prd/meta.yml` v2.0.0 with 8. Instance pins `library_type_version: 1.0.0` but missing the 8th section. | Validator emits I010 warning (deprecation), exit 0. Without the pin → T-class error, exit 3. |
| **B2 — I104 status:planned with resolved target** | PRD with `{kind: informs, to: FEAT-001, status: planned}` where FEAT-001 exists. | I104 error: "use status: present once the target exists". Exit 1. |
| **B3 — W005 legacy + new coexistence** | Instance with BOTH `relationships: {informs: [FEAT-001]}` and `ddx.links: [{kind: informs, to: FEAT-001}]`. | W005 warning pointing at the migration script. Exit 0 (or 1 under `--strict`). |
| **B4 — M005 unknown methodology** | `.helix.yml` lists `helix` (installed) + `helix-mobile` (no resolver). | M005 warning for helix-mobile, helix proceeds normally. Exit 0. |
| **B5 — intra-document edges** | PRD with `{kind: contains, to: FR-1, scope: intra-document}`. | Validator does NOT try to resolve `FR-1` against the cross-document index. Clean exit. |
| **B6 — section_aliases** | Library type meta declares `section_aliases: {functional_requirements: [fr]}`. Instance template uses `## FR` instead of `## Functional Requirements`. | Type-mode validation passes; the alias works. (Requires extending validator to honor aliases when checking H2 ↔ required_sections.) |
| **B7 — exhaustive collection** | One PRD with **three** independent errors (bad kind + missing target + unknown methodology). | Validator surfaces all three findings in one run. Single exit code reflects highest class. |

**How to run:** add seven scenarios to `family-test/consumer/` + extend `run-tests.sh`. Each follows the existing fixture pattern.
**Effort:** ~3 hours total.
**Blocking:** none.

---

### Bucket C — Frontmatter round-trip (skill behavior, scripted)

Design §2.5 says the skill must preserve unknown frontmatter keys
byte-equivalent on edit. The validator can't prove this — it's skill
behavior. Test by scripted edit-rewrite.

| Probe | Fixture | Pass criteria |
|---|---|---|
| **C1 — unknown keys survive** | PRD with `x-team-owner: alice`, `depends_on: [LEGACY-001]`, `ddx.id: PRD-001`. Prompt the agent to add a sentence to the Summary body. | After edit, frontmatter byte-equivalent for `x-team-owner` and `depends_on`. Key order preserved. |
| **C2 — no implicit translation** | PRD with legacy `relationships: {informs: [FEAT-001]}` and NO `ddx.links:`. Prompt the agent to update the Problem section. | After edit, no `ddx.links:` was added. W005 still fires on validation. Translation requires explicit migration script invocation. |
| **C3 — determinism** | Same PRD. Two independent agent runs against the same input. | Both runs produce byte-equivalent frontmatter. |

**How to run:** scripted `claude -p` calls with the helix skill installed, comparing files before/after with `diff` on the frontmatter span.
**Effort:** ~1.5 hours.
**Blocking:** depends on Bucket A confirming the skill activates at all.

---

### Bucket D — Migration script (one-shot)

Design §5 (referenced in the report) mentions a
`migrate_relationships_to_links.py` script that translates legacy
`relationships:` blocks into `ddx.links:` entries.

| Probe | Fixture | Pass criteria |
|---|---|---|
| **D1 — dry-run** | Existing HELIX corpus (3-5 docs with legacy frontmatter). Run `--dry-run`. | Script prints proposed edits without writing. Output identifies the source key (legacy `informs:`) and the proposed `ddx.links:` entry. |
| **D2 — apply** | Same corpus. Run `--apply`. | Files now have `ddx.links:` populated, legacy keys removed. Diff is mechanical. Round-trip preserves other unknown keys. |
| **D3 — idempotent** | Run `--apply` a second time. | No changes; exit 0. |

**Effort:** ~3 hours including writing the script.
**Blocking:** Bucket B (validator must catch W005 first so the migration script has a target to clean).

---

### Bucket E — Pre-commit hook + CI integration

| Probe | Setup | Pass criteria |
|---|---|---|
| **E1 — lefthook integration** | Add `.lefthook.yml` step running `helix_check.py instance --staged-only --marker .helix.yml`. Stage a broken instance (bad edge kind). | `git commit` aborts with the I101 message. |
| **E2 — CI integration** | GitHub Actions workflow running `helix_check.py marker .helix.yml --strict`. PR with introduced violation. | CI fails red with the violation; PR can't merge. |
| **E3 — `--changed-only` mode** | Repo with 100 instance docs. Modify one file. | Validator runs against only the modified file (timed), produces same outcome as full-tree run. |

**Effort:** ~2 hours.
**Blocking:** Buckets A and B should pass first; otherwise we're integrating a half-tested validator.

---

### Bucket F — Performance + scale

Design §1.6 promises sub-10s validation for 1000-doc corpora and a defensive 10s/100MB ceiling per invocation.

| Probe | Setup | Pass criteria |
|---|---|---|
| **F1 — 100 docs** | Synthetic corpus generator writes 100 instances + a graph + a marker. | Validator full run under 1s wall-clock. |
| **F2 — 1000 docs** | Same generator scaled up. | Validator full run under 10s wall-clock. |
| **F3 — 5000 docs (stress)** | Same generator scaled up further. | Defensive ceiling triggers OR run completes. Either is acceptable — the design budgets a ceiling. |
| **F4 — `.helix/index.json` cache** | Run F2 twice; second time should hit cache. | Second run ≤ 30% wall-clock of first. |

**Effort:** ~3 hours (generator + measurement).
**Blocking:** stdlib-only port (otherwise we're measuring PyYAML overhead, which production won't have).

---

## Recommended sequence

The bucket order also reflects the right execution order, except: do **A1+A2** before anything else, because they can invalidate the architecture.

```
1. A1, A2  (~1h)   skill activation happy path + negative — the load-bearing test
2. A3, A4, A5  (~1h)   multi-methodology + scope + explicit override
3. B1–B7  (~3h)    mechanical validator extensions
4. C1–C3  (~1.5h)  frontmatter round-trip (depends on A passing)
5. D1–D3  (~3h)    migration script (depends on B3 / W005)
6. E1–E3  (~2h)    hook + CI integration
7. F1–F4  (~3h)    perf + scale (after stdlib-only port)
```

Total: ~14.5 hours. Bucket A is the gate — if it fails (Claude Code can't drive activation from `.helix.yml`), stop and rework the design before doing B–F.

## What this plan does NOT cover

- **DDx bead schema `graph_node:` field** — covered in the prior implementation plan, separate work.
- **Stdlib-only validator port** — covered in the prior implementation plan, mechanical work.
- **Concerns layer testing** — concerns are out of scope for the marker/linkage validation; tested separately by the existing helix corpus.
- **Multi-workspace cwd switches in one Claude session** — deferred to v1.1 per the prior implementation plan.
- **DDx bead with `graph_node:` pointing at a renamed library node** — deferred.

## Definition of done

The vertical slice is "validation complete" when:

1. All Bucket A probes have written evidence (stream-json captures committed under `family-test/probe-evidence/`) showing the agent reads `.helix.yml` and respects it.
2. All Bucket B/C/D fixtures pass in the family-test runner.
3. Bucket E shows a hook actually aborting a bad commit; CI actually failing red.
4. Bucket F shows the perf budget is met or the ceiling triggers cleanly.

At that point we have a validator and a methodology architecture proven across static checks, agent behavior, and hooks/CI. Then the monorepo reorganization (PR1 of the implementation plan) is just file moves with confidence.

## Open questions for the user

1. **Want me to start with Bucket A1+A2 now?** Quick interactive probe — install plugins, send 2 prompts, parse stream-json. ~1h of work.
2. **Bucket C (round-trip) requires `claude -p` with a specific skill active.** I can drive that with `claude --plugin-dir` flags from this session. Are you OK with the probe creating + then uninstalling plugins as part of the test, or do you want it kept off your installed-plugins list?
3. **Bucket F's stdlib-only port is a prerequisite for honest perf numbers.** Do we do that port BEFORE F, or measure the PyYAML version as a baseline and note the gap?
4. **Migration script (Bucket D) targets:** the family-test slice has minimal fixtures. Do we exercise D against the real existing helix corpus (under `docs/helix/`) as the integration test, or keep D purely in family-test?

If you want me to just start running these in order, say so. Otherwise pick the open questions you want to answer first.
