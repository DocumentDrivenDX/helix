---
title: "HELIX Family Vertical-Slice Validation Results — 2026-06-05"
slug: validation-results-2026-06-05
weight: 860
activity: "Design"
source: "02-design/validation-results-2026-06-05.md"
generated: true
---
# HELIX Family Vertical-Slice Validation Results — 2026-06-05

Validation of the design at
[design-2026-06-04-helix-family-marker-and-linkages.md](/artifacts/design-2026-06-04-helix-family-marker-and-linkages/)
following the plan at
[validation-plan-2026-06-05-vertical-slice-completion.md](/artifacts/validation-plan-2026-06-05-vertical-slice-completion/).

Codex-review constraints absorbed pre-execution:
A1 split (happy / negative-control / functional);
A2 made machine-checkable + A2b for heuristic banner;
A5 pinned to design §1.5 rule 1 (marker membership IS authorization);
A6 added (malformed marker → STOP not heuristic);
B5/B6/B7 paired negatives;
F-cache correctness + invalidation matrix;
E sequencing decoupled from A.

Docker harness required for Bucket A and C probes (clean plugin install state per run).

## §1 Overall verdict

**architecture-blocker** — for the activation discrimination question that Bucket A
was designed to answer. The methodology-skill activation path is NOT discriminative
on the surface-level "what methodology is active" prompt: when the methodology plugin
is uninstalled (A1b negative control), the agent still reads `.helix.yml` directly via
the `Read` tool and produces an indistinguishable answer. The marker file is plain
text and does not require the skill to be loaded.

Skill activation IS discriminative for functional probes that demand non-trivial
methodology behavior (A1c writes the correct PRD/FEAT pair; A5 cites marker
authorization and refuses an explicit-prefix override; A6 refuses heuristic
fallback when the marker is malformed) — but the *gate condition the plan asked
about* (activation path is provably necessary) is not met, so Bucket C
(frontmatter round-trip) was correctly skipped per the plan's gating rule.

Other buckets (B static validation, D migration, E hook/CI integration, F
performance + cache) all passed against their budgets. The architecture blocker is
specific to "how do we prove the skill is doing work that wouldn't happen otherwise."

## §2 Per-bucket result table

| Bucket | Scope | Result | One-line summary |
|---|---|---|---|
| Docker harness | Foundation | pass (soft) | Container builds, plugins mount via `--plugin-dir`, stream-json assertions self-test 8/8; live auth gated on `ANTHROPIC_API_KEY`. |
| A | Skill activation (Docker) | **architecture-blocker** | A1a/A1c/A2/A5/A6 pass; A1b negative control FAILS to discriminate (plain-text marker is readable without skill); A2b banner string not literal; A3 scope respect non-deterministic; A4 upward-marker-search missing from skill prompt. |
| B | Static validation + linkages | pass | 24/24 fixtures green (13 baseline + 11 new: B1a/b, B2, B3a/b, B4, B5a/b, B6a/b, B7); validator extensions for section_aliases, intra-doc scope, W→I strict promotion. |
| C | Frontmatter round-trip | skipped | Gated on Bucket A pass per plan; not run to avoid contaminating signal against an unproven activation path. |
| D | Legacy → ddx.links migration | pass-with-notes | D1/D3 exercise full migration logic on synthetic corpus; D2 confirms real corpus has zero legacy frontmatter (no-op path verified, not migration path); `--require-clean` CI gate works. |
| E | Hook + CI integration | pass-with-notes | E1 lefthook fires on staged `.helix.yml`/`docs/helix/**` and aborts commit with I101; E2 workflow YAML ships and steps simulated locally (root activation out of scope); E3 `--changed-only` deferred (flag not implemented). |
| F | Performance + cache | pass-with-notes | F0 baseline PyYAML O(N²) documented; F1 100 docs 0.37s; F2 1000 docs 1.57s; F3 ceiling fires exit=5 with stderr at >10s; F4 warm rerun 9% of cold; invalidation matrix 5/5 (instance/graph/meta/marker touches behave correctly). |

## §3 What worked, what didn't, what's deferred

### What worked

- **Docker harness as a reusable probe surface.** Adapted from
  `tests/install/claude-code/` with non-root probe user, zero preinstalled
  plugins, stream-json-aware probe runner, stdlib assertion parser.
  Mid-execution defect found and fixed: symlinking under
  `~/.claude/plugins/<name>/` does NOT register plugins (registry is
  `installed_plugins.json`); fix is `claude --plugin-dir <path>` for inline
  install. This is a reusable finding for any future hermetic skill bench.
- **Static validation surface (Bucket B).** All 11 paired-negative fixtures
  passed including B5/B5b (intra-doc scope), B6/B6b (alias-removed), B7
  (exact finding count, exact codes, exit class = highest). Validator
  extensions (T002/T004 → exit 3, W→I strict promotion, section_aliases in
  `cmd_type`, library-pin-aware T004 demotion to I010) are clean and were
  needed by the design.
- **Migration script + dry-run discipline (Bucket D).** Real-corpus run is a
  pure no-op today (no legacy frontmatter exists yet) so risk is bounded.
  D1 + D3 cover the actual migration path against a synthetic corpus
  including unknown-key survival, key-order preservation, idempotence on
  second --apply, and `--require-clean` CI gate.
- **Hook integration (Bucket E1).** Lefthook + `helix_check.py marker
  --strict` aborts a git commit that introduces an I101 edge-kind mismatch.
  End-to-end probe (build isolated repo, install lefthook, stage broken
  fixture, commit fails, restore) is reproducible.
- **Cache scaffolding + ceiling (Bucket F).** Per-process caches (instance
  index, meta.yml, graph.yml) eliminate the O(N²) re-walk; warm rerun is
  9% of cold against a 1000-doc corpus and meets the <30% budget. Ceiling
  flag fires `exit=5` + stderr naming the limit hit. Invalidation matrix
  covers all four touch dimensions called out in design F4.
- **Marker-as-authorization semantics (A5).** The skill correctly refused
  to apply `helix-infra` when the marker did not include it, citing the
  marker as the authorization boundary. Design §1.5 rule 1 is implemented
  in the prompt.
- **Stop-on-malformed (A6).** Skill refused to fall back to a heuristic
  when `.helix.yml` had a YAML parse error. Design §1.4 asymmetry holds.

### What didn't

- **Bucket A negative control (A1b).** The discriminator the plan was built
  around does not discriminate. With the helix methodology plugin
  uninstalled (`plugins=[helix-library]`, `skills` no `helix:helix`), the
  agent still reads `.helix.yml` directly and reports helix active with
  near-identical prose to A1a. The marker is plain text. The skill is
  necessary for *functional* methodology behavior but not for *naming what
  is active*. This is the architecture blocker.
- **A2b literal banner.** Heuristic-fallback activation conveys the spirit
  of the design §1.3 banner but does not emit the literal string. A
  contract this specific needs either a deterministic emitter (validator
  inserts the banner) or a sharper prompt.
- **A3 scope respect.** Non-deterministic. One run wrote `PRD.md` to the
  repo root (out of scope); another wrote it under
  `services/api/docs/helix/` (correct). Scope is not reliably enforced by
  the agent on its own.
- **A4 upward marker search.** From `cwd=docs/helix` or `cwd=infra`, the
  agent searched only within `cwd` and reported "no active methodology"
  rather than walking up to the parent's `.helix.yml`. The skill prompt
  lacks an explicit upward-search instruction.
- **Bucket E2 activation.** GitHub Actions only reads workflows from the
  repo root; the file currently lives under `family-test/.github/`. Plan
  accepts as out-of-scope; activation requires a copy/symlink.

### Deferred

- **Bucket C (frontmatter round-trip).** Gated on Bucket A; not run.
- **Bucket E3 (`--changed-only`).** Validator does not expose the flag.
- **stdlib-only port of `helix_check.py`.** Current implementation is
  PyYAML-based; the production target is stdlib-only.
- **Real-corpus `--apply` of migration script.** Real corpus has no legacy
  frontmatter so there is nothing to migrate today; the script is ready
  when the day comes.
- **Long-form content-hash cache matrix.** F4 covers mtime-based
  invalidation; design's content-hash variant is a future iteration.

## §4 Architecture blocker — what specifically blocks, design change required

**Block.** The plan treated "skill activation via `Skill(helix:helix)` is
present in the stream-json transcript" as the gate for trusting that the
methodology is doing work. A1b shows that's not enough: a *non-activation*
path (`Read` tool against the plain-text `.helix.yml`) produces an
indistinguishable surface answer. The plan's discriminator is not a
discriminator.

**Required design change.** One of:

1. **Make the methodology answer require methodology behavior.** Bucket A
   probes should ask the agent to *do something that requires the
   methodology skill to produce a correct answer*, not "what methodology is
   active." A1c, A5, A6 are examples that already work. Retire A1a/A1b/A2/A2b
   as activation gates — they test surface naming, which the marker handles
   on its own.
2. **OR change the activation contract.** If the design wants the *naming*
   to require the skill (so plain `Read` against the marker is
   insufficient), the marker file should not be self-describing in plain
   text — e.g. a non-obvious filename, or a binary index that the skill
   alone knows how to read. This contradicts the design's "marker is human-
   readable YAML at the workspace root" principle and is not recommended.
3. **AND fix the in-skill defects exposed during A** regardless of which
   path is taken: (a) emit the literal §1.3 banner deterministically (or
   relax the contract); (b) add upward marker-search to the skill prompt
   so cwd-rooted invocations resolve correctly (fixes A4); (c) make scope
   respect deterministic by surfacing the marker's `scope:` paths to the
   agent at the top of every methodology-touching prompt (fixes A3).

Recommendation: take path (1) — the design's value comes from methodology
*behavior*, not from gating who can read a YAML file. Update the
validation plan and the skill prompt; do not change the marker contract.

## §5 Open follow-ups

- [ ] **Redesign Bucket A activation probes** to require methodology
  behavior, not surface naming. Re-gate Bucket C against the new probes.
- [ ] **Fix skill prompt defects** surfaced by A: emit literal §1.3 banner;
  add upward marker-search; thread scope into every prompt.
- [ ] **stdlib-only port of `helix_check.py`** (validator, migration,
  baseline). Currently PyYAML.
- [ ] **Bucket E3** — implement `--changed-only <ref>` on
  `helix_check.py` and run the deferred probe.
- [ ] **Bucket E2 activation** — copy/symlink the workflow to repo-root
  `.github/workflows/` once the slice graduates from `family-test/`.
- [ ] **Real-corpus `--apply` rehearsal** — re-run when any legacy
  frontmatter (relationships:, ddx.links:, referenced_by:) appears in the
  real `docs/helix/` tree.
- [ ] **Content-hash cache matrix** (F4 extension) — design's longer-form
  invalidation strategy beyond mtime.
- [ ] **A1b/A2/A2b retirement decision** — fold into bucket-A redesign or
  rewrite as functional probes.

## §6 Next concrete action

Redesign Bucket A to probe methodology *behavior* (functional outputs
that require the skill, like A1c/A5/A6) instead of surface naming
(A1a/A1b/A2/A2b), re-run the gate, and then execute the previously-gated
Bucket C frontmatter round-trip probes against the corrected activation
path.
