# helix-family Readiness Report

- **Date:** 2026-06-04
- **Phase:** 6 of 6 (smoke + report)
- **Companion docs:**
  - [design-2026-06-03-helix-library-split.md](./design-2026-06-03-helix-library-split.md)
  - [plan-2026-06-03-helix-library-FINAL.md](./plan-2026-06-03-helix-library-FINAL.md) (§0 monorepo amendment)
  - [implementation-plan-2026-06-04-helix-library-family.md](./implementation-plan-2026-06-04-helix-library-family.md)
  - [test-plan-2026-06-04-helix-library-family.md](./test-plan-2026-06-04-helix-library-family.md)

This report closes the planning workflow that produced specs, fixtures, a
plan, and a runner for the helix-family architecture. No HELIX tree
reorganisation happened in this workflow. The actual monorepo move is the
next user-approved workflow run.

---

## 1. State summary — what got built

The workflow folded two new architectural decisions into the prior split
design:

1. **Monorepo topology.** `helix-library`, `helix` (product), and
   `helix-infra` ship as three plugins from the existing `helix/`
   repo, listed in a single `marketplace.json`. The per-plugin semver
   and validator-by-copy ceremony in the original sibling-repo plan
   collapses because everything ships from one commit.
2. **Test-first.** Executable bench fixtures double as the spec. The
   migration is "done" when every active fixture under
   `tests/fixtures/family/` is green.

Phase-by-phase output:

| Phase | Output | Commit |
| --- | --- | --- |
| 1 — fold decisions | design + FINAL plan annotated with monorepo amendment | `025b67aa` |
| 2 — fixture authoring | 23 active + 1 deferred fixture (T01–T23, T8 deferred, T12b parallel) | `d2775d66` |
| 3 — adversarial review | 7 high-severity gaps folded as T14–T21 (+T18b) | (in d2775d66 / 26fd2459) |
| 4 — implementation plan | 6-PR monorepo plan replacing 14-PR sibling plan | `26fd2459` |
| 5 — runner | `tests/family/validate_fixture_structure.py` + `tests/family/run_fixture.py` and two `just` recipes | `c0154782` |
| 6 — smoke + report | this document | (pending) |

---

## 2. Fixture inventory

25 fixture directories under `tests/fixtures/family/`. One is deferred
(T08). The high-risk subset (eight active fixtures) carries the
architectural questions.

### High risk — load-bearing for the architecture (8)

| Fixture | What it pins |
| --- | --- |
| T02-helix-missing-library | helix plugin behaviour when library is absent |
| T05-product-shaped-precedence | product overrides library when slugs collide |
| T06-tf-file-precedence | terraform-file shape resolution across infra+library |
| T07-mixed-repo-disambiguation | which plugin's view wins when both define the same type |
| T13-no-skills-field | does Claude Code accept a data-only plugin (skills-less)? |
| T14-library-upgrade-stale-doc | library upgrade adds a required_section against a pre-existing doc |
| T15-corrupt-library-mount | diagnostic surfaces when the mount is half-present |
| T16-graph-cycle-detected | graph.yml cycle is named at both nodes |
| T17-graph-dangling-requires | graph.yml dangling `requires:` is named |
| T18-local-override-weakens | local override that strips a canonical section is rejected |
| T19-edit-existing-without-library | edit-existing path triggers the library setup-gap |
| T20-skills-data-workaround | positive workaround if T13 fails (skills/_data/SKILL.md) |

(That's the eight from the matrix plus the four folded from the Phase 3
review; the report lists all twelve so the high-risk surface is visible
in one place.)

### Standard risk (12)

T01, T03, T04, T09, T10, T11, T12, T12b, T18b, T21, T22, T23.

### Deferred (1)

T08-helix-web-deferred — needs the helix-web plugin to exist; deferred
to v1.1 per the implementation plan.

Total: **25 fixture directories, 24 active, 1 deferred.**

---

## 3. Smoke result

### Structure validator

Initial run:

```
$ just test-family-fixtures-structure
FAIL: 1 fixture issue(s):
  - T13-no-skills-field: prompts/ has no prompt files
```

T13 is the install-only fixture (it drives `claude plugins install …`
through `expected/01-install.json` rather than a model prompt). The
runner contract still requires a `prompts/<stem>` per
`expected/<stem>`. Per the workflow instruction ("fix the fixture in
place rather than the validator"), a stub
`prompts/01-install.txt` was added that documents the install-only
nature of the case. Re-run:

```
$ just test-family-fixtures-structure
OK: 25 fixture(s) validated under .../tests/fixtures/family
```

### Dry-runs (3 representative fixtures)

All three exit 0 with the runner reporting the fixture is well-formed
for a future real run.

**T01-library-only** (lowest risk; happy path):

```
plugins: ['helix-library']
prompts: 2
## prompt: 01-list-types.txt
  expectation: assert=prose_match
## prompt: 02-adversarial-discover.txt
  expectation: assert=stream_json_tool_use
DRY-RUN: fixture is well-formed for future real run
```

**T05-product-shaped-precedence** (high risk; co-activation):

```
plugins: ['helix-library', 'helix', 'helix-infra']
prompts: 1
## prompt: 01-author-adr.txt
  expectation: assert=stream_json_tool_use
DRY-RUN: fixture is well-formed for future real run
```

**T13-no-skills-field** (load-bearing architectural question):

```
plugins: ['helix-library']
prompts: 1
## prompt: 01-install.txt
  expectation: assert=install_result
DRY-RUN: fixture is well-formed for future real run
```

### Runner UX defect noticed

The `just test-family-fixture-dry-run FIXTURE=…` recipe takes the
fixture as a positional argument, not `FIXTURE=…` style. The workflow
instruction used `FIXTURE=…` and the recipe interpreted that literally:

```
$ just test-family-fixture-dry-run FIXTURE=T01-library-only
FAIL: fixture not found: .../family/FIXTURE=T01-library-only
$ just test-family-fixture-dry-run T01-library-only
# Fixture dry-run: T01-library-only … (works)
```

Two ways to resolve in the implementation workflow: (a) rename the
recipe argument and document the call form, or (b) accept either form
in the runner. Filed as an open question (Q5).

---

## 4. What's still MISSING for implementation to start

1. **Claude Code cross-skill resource resolution semantics — unverified.**
   The architecture assumes a methodology skill (e.g. `helix-product`)
   can read structured data shipped by a different plugin
   (`helix-library`) at a deterministic mount path. The docs do not
   confirm this. A `claude-code-guide` query (or a one-off probe in a
   throwaway plugin) is required before any code is written against
   the library mount. T13 + T20 turn the question into a test, but
   they cannot answer it on their own.

2. **Monorepo reorganisation has not happened.** No files have moved.
   `library/`, `product/`, `infra/` do not exist. `marketplace.json`
   has not been written. This is the next user-approved workflow run.

3. **Type promotion to library has not happened.** No artifact-type
   spec has been moved from `workflows/` into the eventual
   `library/types/`. The fixtures reference a future shape; nothing
   under `workflows/` matches it yet. This is a separate workflow
   from the monorepo move.

4. **Runner does not invoke Claude yet.** `tests/family/run_fixture.py`
   is dry-run-only — it prints the command it *would* run. Wiring it
   to actually launch `claude --plugin-dir …` and capture
   stream-json is part of the implementation workflow.

---

## 5. Next concrete action

Run a one-off probe against the live `claude` binary to confirm
whether a plugin with `plugin.json` containing no `skills:` field
installs and mounts cleanly (T13), then approve the monorepo
reorganisation workflow — the entire architecture's shape branches on
that probe.

---

## 6. Open questions for the user

1. **Probe-first vs test-first on T13.** Do you want to answer the
   no-skills-field question with a throwaway probe before starting
   the monorepo reorganisation, or accept the worst case (T20
   workaround) and start the move immediately? The workaround
   means every methodology plugin in the family carries a stub
   `skills/_data/SKILL.md`; reversible later but visible in
   `skills list`.

2. **Type promotion scope.** When the type-promotion workflow runs,
   do all 30+ artifact types move at once, or do we start with a
   minimum library (e.g. ADR + PRD + technical-design) and grow it
   plugin-by-plugin? The fixtures don't pin this — they exercise
   shape resolution given *some* library, not a specific catalogue.

3. **`helix-infra` scope.** The infra plan
   ([plan-2026-06-03-helix-infra-sibling.md](./plan-2026-06-03-helix-infra-sibling.md))
   predates the monorepo decision and is the only design doc that
   hasn't been touched in this workflow. Should Phase 1 of the
   implementation workflow refold it the way the library plan was
   refolded, or do you want a separate alignment pass first?

4. **Runner harness choice.** The dry-run prints a single
   `claude --plugin-dir …` command shape. The actual implementation
   has to pick between (a) shelling out to the user's installed
   `claude` binary, (b) the `ddx agent run --harness claude` path,
   or (c) the Docker-based test harness in `tests/install/`. Which
   one is canonical for the family bench?

5. **Just recipe argument form.** Rename
   `test-family-fixture-dry-run FIXTURE` to a positional
   `test-family-fixture-dry-run F` and update the workflow docs, or
   accept `FIXTURE=…` syntax in the Python runner? Cosmetic, but
   the wrong call form currently produces a confusing
   "fixture not found" error.

---

## 7. Sign-off

Everything this planning workflow promised to produce is on disk and
the runner smokes green. The next workflow run is the monorepo
reorganisation, gated on resolving Q1.
