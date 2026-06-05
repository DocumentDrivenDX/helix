# Validation Plan — Vertical Slice Completion

- **Date:** 2026-06-05
- **Status:** plan (refined post-codex-review + Docker constraint)
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

## How to run — Docker harness (REQUIRED for A and C)

All Bucket A and Bucket C probes MUST run inside Docker. Rationale:

- **Reproducibility.** Pin the `claude` CLI version (build arg
  `CLAUDE_INSTALL_URL` or vendored tarball). The user's local install is
  not part of the test surface.
- **Clean plugin install state per run.** `~/.claude/plugins/` is empty
  at container start; no leakage from the host's installed plugins
  (which include `helix` itself today).
- **No mutation of the user's environment.** Probes that install/uninstall
  plugins or seed `.helix.yml` files do so inside a throwaway container.

**Harness layout (reuse `tests/install/claude-code/` patterns):**

- Base image: `tests/install/claude-code/Dockerfile` already installs
  ubuntu:24.04 + claude CLI + python3 + python3-yaml. Extend with a
  `validation-probes` stage that adds `jq` (for stream-json parsing) and
  copies the family-test/ tree to `/opt/family-test`.
- Mount fixtures read-only: `-v <fixture>:/workspace:ro` per probe.
- Mount creds: `-e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY` (same pattern as
  `tests/install/claude-code/install.sh`).
- Plugins loaded via symlink from mounted dirs (PR-safe pattern from
  `install.sh`):
  - `ln -sf /opt/family-test/library ~/.claude/plugins/helix-library`
  - `ln -sf /opt/family-test/methodology-product ~/.claude/plugins/helix`
- Each probe is a shell script under
  `family-test/probes/<probe-id>/run.sh` that: (1) prepares the workspace,
  (2) runs `claude -p --output-format stream-json --bare < prompt.txt`,
  (3) writes stdout to `evidence/<probe-id>.jsonl`, (4) runs
  `assert.sh` (parses stream-json with `jq`) that exits 0 on pass.

**Bucket B, D, F:** Docker is recommended for reproducibility but not
strictly required — the validator is stdlib-portable. These can run on
the host with `python3 family-test/library/scripts/helix_check.py`.

---

### Bucket A — Skill activation (Docker-required)

**Question:** does Claude Code actually let a methodology skill drive
activation off `.helix.yml`? The design assumes the SKILL.md prose can
instruct the agent to read the marker and respect it — but no harness today
proves this. If activation can't be marker-driven, the design needs
fallback to slash-command-only and we lose the per-repo declaration win.

**Probe split below isolates "agent claims helix is active" from "agent
actually reads the marker and acts on it". Functional prompts MUST NOT
mention the marker, methodology, or activation by name — otherwise A1
can pass for the wrong reason (LLM pattern-matching the prompt).**

| Probe | What to set up | Pass criteria |
|---|---|---|
| **A1a — happy path (declarative)** | Plugins installed; workspace `/workspace/` with `.helix.yml` listing `helix` and `root: docs/helix/`. Prompt: *"Show me what methodologies are active in this repo."* | Stream-json shows `Read` tool_use against `.helix.yml` BEFORE the assistant message. Final message names `helix` and only `helix`. |
| **A1b — happy path (control: plugin NOT installed)** | Same `.helix.yml`, but ONLY `helix-library` plugin loaded — no `helix` methodology plugin. Same prompt. | Agent does NOT claim helix is active. Either reads `.helix.yml` and reports it lists helix but no resolver is available (M005 banner), OR says nothing is active. Critically: must not improvise. |
| **A1c — happy path (functional, marker not mentioned)** | Same as A1a. Prompt: *"Create a PRD for a coffee-ordering service."* (Prompt contains no methodology / active / marker / config wording.) | First relevant tool_use is `Read` on `.helix.yml` (or `Glob` for `.helix.yml`). Final write lands under the marker's `root:` path (`docs/helix/`). If the agent writes outside that root, fail. |
| **A2 — no marker, no heuristic (machine-checkable)** | Workspace with NO `.helix.yml` and NO `workflows/` or methodology heuristic files. Prompt verbatim: *"Using repository configuration only, report active methodology IDs as JSON: { active: [] }"* | Stdout JSON parses; `active == []`; no `Write`/`Edit` tool_use in stream-json; no prose claiming helix is active. |
| **A2b — no marker, heuristic present (fallback banner)** | Workspace with NO `.helix.yml` but a `workflows/methodology.yml` fixture present (heuristic trigger). Same prompt as A1a. | Agent emits the exact fallback banner from design §1.3. Does NOT proceed with helix-specific edits. |
| **A3 — scope respect** | Workspace with `.helix.yml` listing helix scoped to `services/api/docs/helix/`. cwd outside that path. Prompt: *"Create a PRD."* (no path hint) | Agent declines or asks for scope clarification. Does NOT write into the wrong directory. Stream-json shows no `Write` outside `services/api/docs/helix/`. |
| **A4 — multi-methodology** | `.helix.yml` listing helix + helix-infra at different scopes; prompt *"What's the active methodology here?"* (run twice — once with cwd under helix scope, once under helix-infra scope). | First invocation picks helix, second picks helix-infra. Per design §1.5 resolution chain. |
| **A5 — explicit prefix wins (PINNED)** | `.helix.yml` listing helix only; prompt prefixed `/helix intent`. Then second run with `/helix-infra intent` (helix-infra NOT in marker). | **Pin per design §1.5 rule 1:** explicit prefix wins IF the methodology is a marker member. Run 1: honors `/helix` (it is in marker). Run 2: rejects `/helix-infra` with diagnostic "helix-infra not authorized by .helix.yml" — marker membership IS the authorization boundary. |
| **A6 — malformed marker + heuristics (NEW)** | `.helix.yml` exists but is malformed (e.g. invalid YAML, or missing `version:`, or `root:` outside repo). `workflows/methodology.yml` heuristic file ALSO present. Prompt: *"Create a PRD."* | Agent STOPS with the marker parse error from design §1.4. Does NOT fall back to heuristics. Asserts design §1.4 "asymmetry is intentional" rule: heuristics fire only when marker is ABSENT, not when marker is BROKEN. |

**Effort:** ~3 hours including Docker harness.
**Blocking:** none — runnable today.
**Failure modes that matter:**
- A1c writes a PRD without reading `.helix.yml` → marker is theatre, agent uses its prior. Design needs slash-command-required, not marker-authoritative.
- A2 emits prose claiming helix active despite no marker/heuristics → hallucinated activation; SKILL.md prose is insufficient.
- A6 falls back to heuristics on malformed marker → silent degradation, contradicts design §1.4.
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
| **B5a — intra-document edges (positive)** | PRD with `{kind: contains, to: FR-1, scope: intra-document}` where FR-1 is an H2 section in the same doc. | Validator does NOT resolve `FR-1` against the cross-document index; resolves it against intra-doc sections. Clean exit 0. |
| **B5b — intra-document edges (paired negative)** | Same PRD but `scope: cross-document` (or scope omitted) for the same `to: FR-1`. | Validator MUST fail — `FR-1` is not a cross-document target. This catches the "all scope-tagged links silently dropped" failure mode where B5a passes for the wrong reason. Exit 1, finding code names FR-1 as unresolved. |
| **B6a — section_aliases (positive)** | Library type meta declares `section_aliases: {functional_requirements: [fr]}`. Instance template uses `## FR`. | Type-mode validation passes; the alias works. |
| **B6b — section_aliases (paired negative)** | Same template (`## FR`) but `section_aliases` REMOVED from library meta. | Type-mode validation FAILS T004 (required section `functional_requirements` not found). Confirms the alias is what carried B6a, not a permissive matcher. |
| **B7 — exhaustive collection (exact counts)** | One PRD with **exactly three** independent errors: (1) bad edge kind `{kind: bogus}`, (2) missing target `{kind: informs, to: NOPE-999}`, (3) `.helix.yml` references unknown methodology `helix-mobile`. | Validator surfaces EXACTLY 3 findings in one run. Finding codes: `[I101, I102, M005]` (or whatever the spec pins — must be deterministic). Exit code = highest class per design §4.3 (I101 is I-class error = exit 1). |

**How to run:** add scenarios to `family-test/consumer/` + extend `run-tests.sh`. Each follows the existing fixture pattern.
**Effort:** ~4 hours total (paired negatives added).
**Blocking:** none.

---

### Bucket C — Frontmatter round-trip (Docker-required, scripted)

Design §2.5 says the skill must preserve unknown frontmatter keys
byte-equivalent on edit. The validator can't prove this — it's skill
behavior. Test by scripted edit-rewrite inside the Docker harness.

| Probe | Fixture | Pass criteria |
|---|---|---|
| **C1 — unknown keys survive** | PRD with `x-team-owner: alice`, `depends_on: [LEGACY-001]`, `ddx.id: PRD-001`. Prompt the agent to add a sentence to the Summary body. | After edit, frontmatter byte-equivalent for `x-team-owner` and `depends_on`. Key order preserved. |
| **C2 — no implicit translation** | PRD with legacy `relationships: {informs: [FEAT-001]}` and NO `ddx.links:`. Prompt the agent to update the Problem section. | After edit, no `ddx.links:` was added. W005 still fires on validation. Translation requires explicit migration script invocation. |
| **C3 — determinism** | Same PRD. Two independent agent runs against the same input (separate containers). | Both runs produce byte-equivalent frontmatter. |

**How to run:** scripted `claude -p` calls inside the Docker harness with the helix skill installed, comparing files before/after with `diff` on the frontmatter span.
**Effort:** ~1.5 hours.
**Blocking:** depends on Bucket A confirming the skill activates at all.

---

### Bucket D — Migration script (one-shot)

Design §5 (referenced in the report) mentions a
`migrate_relationships_to_links.py` script that translates legacy
`relationships:` blocks into `ddx.links:` entries.

| Probe | Fixture | Pass criteria |
|---|---|---|
| **D1 — dry-run (family-test only)** | Synthetic corpus under `family-test/consumer/migration-corpus/` (3-5 docs with legacy frontmatter). Run `--dry-run`. | Script prints proposed edits without writing. Output identifies the source key (legacy `informs:`) and the proposed `ddx.links:` entry. |
| **D2 — apply against real helix corpus (integration)** | Real `/Users/erik/Projects/helix/docs/helix/` (or a copy thereof). Run `--apply` on a branch. | Files now have `ddx.links:` populated, legacy keys removed. Diff is mechanical. Round-trip preserves other unknown keys. Validator (W005) clean after migration. |
| **D3 — idempotent** | Run `--apply` a second time against the D2 output. | No changes; exit 0. |

**Effort:** ~3 hours including writing the script.
**Blocking:** Bucket B (validator must catch W005 first so the migration script has a target to clean).

---

### Bucket E — Pre-commit hook + CI integration

| Probe | Setup | Pass criteria |
|---|---|---|
| **E1 — lefthook integration** | Add `.lefthook.yml` step running `helix_check.py instance --staged-only --marker .helix.yml`. Stage a broken instance (bad edge kind). | `git commit` aborts with the I101 message. |
| **E2 — CI integration** | GitHub Actions workflow running `helix_check.py marker .helix.yml --strict`. PR with introduced violation. | CI fails red with the violation; PR can't merge. |
| **E3 — `--changed-only` mode (correctness)** | Repo with 100 instance docs. Modify one file that has dependents. | Validator runs against only the modified file PLUS any docs that link TO it (transitive closure of inbound edges). Findings are identical to a full-tree run for the affected subgraph; full-tree-only findings unrelated to the change must NOT appear. Timed: changed-only ≤ 20% of full run. |

**Effort:** ~2 hours.
**Blocking:** Bucket B passing. E does NOT strictly depend on Bucket A — hook/CI integration is validator-only and can proceed even if skill activation is being reworked.

---

### Bucket F — Performance + scale

Design §1.6 promises sub-10s validation for 1000-doc corpora and a defensive 10s/100MB ceiling per invocation.

| Probe | Setup | Pass criteria |
|---|---|---|
| **F0 — PyYAML baseline** | Run F1/F2 against the current PyYAML-based `helix_check.py`. | Captured numbers; report notes "PyYAML baseline, stdlib port deferred". Establishes the gap before the stdlib port follow-up. |
| **F1 — 100 docs** | Synthetic corpus generator writes 100 instances + a graph + a marker. Expected: 100 docs scanned, N edges resolved, 0 findings (clean fixture). | Validator full run under 1s wall-clock. Output reports exactly 100 docs scanned, exactly N edges resolved (N = generator-known), 0 findings. |
| **F2 — 1000 docs** | Same generator scaled up. Expected: 1000 docs, M edges, 0 findings. | Validator full run under 10s wall-clock. Exact counts match generator-known values. |
| **F3 — 5000 docs (ceiling)** | Same generator scaled up further. | Defensive ceiling triggers with **exit code 5** and stderr message naming the specific limit hit (e.g. "doc count exceeds 4096 limit" or "elapsed exceeds 10s limit"). Does NOT silently truncate. Does NOT just "complete" — must trigger the ceiling and say so. |
| **F4a — cache hit (correctness + perf)** | Run F2 twice in the same container; second run hits `.helix/index.json` cache. | Second run ≤ 30% wall-clock of first. **Output is byte-identical to the cold run** (same docs scanned count, same edges resolved count, same findings). |
| **F4b — cache invalidation matrix** | After warm F4a, mutate ONE input at a time and re-run. Inputs: (1) touch one instance doc, (2) touch graph file, (3) touch marker, (4) touch library type meta. | For each mutation: cache invalidates exactly the affected subset, not everything. (1) only the touched doc + its dependents re-validate. (2) all docs re-resolve edges. (3) marker + scope checks re-run; doc parsing cache survives. (4) only docs of that type re-validate against new meta. Output remains correct for each case (matches cold-run baseline). |

**Effort:** ~4 hours (generator + measurement + invalidation matrix).
**Blocking:** F0 (PyYAML baseline) runs NOW; stdlib-only port is a follow-up that will replay F1-F4. The performance gap is noted in the F report rather than blocking the bucket.

---

## Recommended sequence

Per codex point 7: Bucket E depends on B passing, not on A. A is the
load-bearing architecture question but doesn't gate the validator path.

```
1. A1a/A1b/A1c, A2, A2b  (~2h)   skill activation: happy path + controls + machine-checkable negative
2. A3, A4, A5, A6  (~1.5h)       scope + multi-methodology + pinned override + malformed-marker stop
3. B1–B7 (with paired negatives) (~4h)   mechanical validator extensions
4. C1–C3 (Docker)  (~1.5h)               frontmatter round-trip (depends on A passing)
5. D1 (family-test) + D2 (real corpus) + D3 idempotent  (~3h)   migration script
6. E3 (changed-only correctness) + F4 (cache correctness)  (~3h)   correctness-of-modes
7. E1, E2  (~1h)                  hook + CI integration (depends on B only)
8. F0 (baseline), F1–F3  (~2h)    perf + scale (PyYAML baseline; stdlib port is follow-up)
```

Total: ~18 hours. Bucket A is the architecture gate — if A1c or A6 fails,
stop and rework the design before doing C/D (B/E/F can still proceed,
since they're validator-only).

## What this plan does NOT cover

- **DDx bead schema `graph_node:` field** — covered in the prior implementation plan, separate work.
- **Stdlib-only validator port** — measured as F0 baseline here; the port itself is a follow-up that will replay F1-F4.
- **Concerns layer testing** — concerns are out of scope for the marker/linkage validation; tested separately by the existing helix corpus.
- **Multi-workspace cwd switches in one Claude session** — deferred to v1.1 per the prior implementation plan.
- **DDx bead with `graph_node:` pointing at a renamed library node** — deferred.

## Definition of done

The vertical slice is "validation complete" when:

1. All Bucket A probes have written evidence (stream-json captures committed under `family-test/probes/<probe-id>/evidence/`) showing the agent reads `.helix.yml` and respects it. A1a, A1c, A2, A2b, A6 are the load-bearing ones — all must pass.
2. All Bucket B/C/D fixtures pass in the family-test runner, including the paired negatives (B5b, B6b) that prove the positives didn't pass for the wrong reason.
3. Bucket E shows a hook actually aborting a bad commit; CI actually failing red; E3 changed-only is correctness-equivalent to full run.
4. Bucket F shows the perf budget is met (or PyYAML baseline + gap noted) and the ceiling triggers cleanly with exit code 5; F4 cache invalidation matrix passes.

At that point we have a validator and a methodology architecture proven across static checks, agent behavior, and hooks/CI. Then the monorepo reorganization (PR1 of the implementation plan) is just file moves with confidence.

## Open questions for the user — RESOLVED

1. **Want me to start with Bucket A1+A2 now?** **DECIDED: YES.** Bucket A (now A1a/b/c, A2, A2b, A3-A6) runs first, gated on Docker harness landing.
2. **Bucket C requires `claude -p` with a specific skill active. Probes install/uninstall plugins — OK or keep off your installed list?** **DECIDED: Docker.** All Bucket A and C probes run in containers; the user's installed plugins are not touched. Per-run clean state via fresh container.
3. **Bucket F's stdlib-only port is a prerequisite for honest perf numbers. Port BEFORE F, or measure PyYAML as baseline and note the gap?** **DECIDED: measure PyYAML as F0 baseline now**, port stdlib in follow-up, gap noted explicitly in the F report.
4. **Migration script (Bucket D) targets: family-test only, or real helix corpus?** **DECIDED: both.** D1 (dry-run) runs against family-test synthetic corpus. D2 (apply) runs against real `/Users/erik/Projects/helix/docs/helix/` as the integration test. D3 (idempotent) replays against D2 output.
