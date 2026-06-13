---
title: "Test Plan: helix Family Bench Fixtures"
slug: test-plan-2026-06-04-helix-library-family
weight: 830
activity: "Design"
source: "02-design/test-plan-2026-06-04-helix-library-family.md"
generated: true
---

> **Example from HELIX's own docs.** This generated page comes from `docs/helix/`. Use it to see the method in practice; start with the [artifact-type catalog](/artifact-types/) for reusable templates. Historical plans and reports may describe retired architecture.

# Test Plan: helix Family Bench Fixtures

- **Date:** 2026-06-04
- **Status:** Phase-3-reviewed, Phase-4-revised (adversarial review folded in)
- **Companion docs:**
  - [plan-2026-06-03-helix-library-FINAL.md](/artifacts/plan-2026-06-03-helix-library-final/)
  - [design-2026-06-03-helix-library-split.md](/artifacts/design-2026-06-03-helix-library-split/)
  - [plan-2026-06-03-helix-library-migration.md](/artifacts/plan-2026-06-03-helix-library-migration/)

## Purpose

The bench fixtures are the **executable spec** for the helix family
architecture (helix-library data plugin + helix / helix-infra methodology
plugins, all shipped from the same monorepo via a single marketplace).

The migration from "today's single helix repo" to "monorepo with
library/ + product/ + infra/" is **done when all fixtures in
`tests/fixtures/family/` pass**. No fixture passes today; each green
fixture is a load-bearing claim about the family.

The fixtures double as documentation: each `README.md` explains
**what** the scenario asserts, **why it matters**, and **what a failure
looks like**. A reviewer who reads the fixtures should be able to
reconstruct the precedence, resolution, and validation contracts
without reading the design doc.

## Fixture layout convention

Every fixture is a directory under `tests/fixtures/family/` named
`TNN-<descriptive-slug>/`. Inside:

```
TNN-<slug>/
├── README.md               # scenario, why it matters, pass/fail signature
├── workspace/              # minimal repo tree the agent sees as cwd
│   └── ...                 # files that drive co-activation/resolution
├── plugins-installed.txt   # one plugin name per line (helix-library, helix, helix-infra)
├── prompts/
│   ├── 01-<name>.txt       # one or more prompts piped in sequence
│   └── 02-<name>.txt
└── expected/
    ├── 01-<name>.json      # structured assertion for prompt 01
    └── 02-<name>.json      # structured assertion for prompt 02
```

Conventions:

- `plugins-installed.txt` is the **only** declaration of which family
  components are mounted. The runner reads this and constructs the
  Claude Code session accordingly. If the file is empty, no family
  plugin is mounted (still a valid scenario — see negative controls).
- `workspace/` may be empty (T1, T2) when the assertion is about plugin
  install behavior, not about repo-shape-driven precedence.
- `expected/NN.json` declares the **assertion type** in its top-level
  `assert` field. Supported assertion types:
  - `"stream_json_tool_use"` — checks that a specific `tool_use` event
    appears (or does not appear) in the stream-json transcript.
  - `"prose_match"` — checks the final assistant message text for
    presence/absence of substrings or regex matches.
  - `"validator_exit"` — runs `python3 library/scripts/helix_graph_check.py`
    (or the appropriate validator) and asserts an exit code +
    stderr/stdout pattern.
  - `"install_result"` — runs `claude plugin install` (or the harness
    equivalent) and asserts success/failure + stderr pattern.

## The 13 scenarios

The table below summarizes; each fixture's `README.md` carries the
full prose. **HIGH RISK** = scenarios where a failure means the
architecture is broken (not just a typo).

| ID  | Risk    | Components installed                       | Repo shape (workspace/)             | What we assert                                                                          |
| --- | ------- | ------------------------------------------ | ----------------------------------- | --------------------------------------------------------------------------------------- |
| T1  | low     | helix-library only                         | empty                               | library installs cleanly as a data-only plugin; no skill routes                         |
| T2  | **HIGH**| helix only (library NOT installed)         | docs/helix/01-frame/prd.md          | setup-gap message fires; existing docs still read-only-OK; new authoring blocked       |
| T3  | low     | helix-library + helix                      | docs/helix/01-frame/prd.md          | happy path: helix routes; library:prd resolves; validator finds library                |
| T4  | low     | helix-library + helix-infra                | main.tf, terraform/                 | happy path: helix-infra routes; library:adr resolves; validator finds library          |
| T5  | **HIGH**| library + helix + helix-infra              | docs/helix/01-frame/prd.md (no *.tf)| precedence: product-shaped repo → helix wins; helix-infra stays silent                 |
| T6  | **HIGH**| library + helix + helix-infra              | main.tf only                        | precedence: *.tf wins → helix-infra routes; helix stays silent                          |
| T7  | **HIGH**| library + helix + helix-infra              | docs/helix/ + main.tf (mixed)       | precedence: most-specific match wins (banner offers disambiguation)                    |
| T8  | DEFER   | library + helix + helix-web (future)       | n/a                                 | placeholder — helix-web does not exist yet                                              |
| T9  | medium  | library + helix + local:my-adr override    | docs/helix/02-design/_overlays/my-adr/| shadowing: local:my-adr wins over library:adr in this binding                          |
| T10 | medium  | library + helix (graph.yml uses bare slug) | broken graph.yml in workspace/      | validator rejects bare slug; exit non-zero; clear error                                |
| T11 | medium  | library + helix (graph.yml uses library:nonexistent) | broken graph.yml         | validator rejects unknown library type; exit non-zero                                  |
| T12 | medium  | library + helix (section_aliases on adr)   | docs/adr/0001-x.md w/ alias section | validator accepts canonical OR alias section name                                       |
| T12b| medium  | library + helix (section_aliases REMOVED)  | same doc as T12                   | validator REJECTS alias when methodology declares none (proves alias is load-bearing)  |
| T13 | **HIGH**| helix-library only (plugin.json no skills:)| n/a                                 | Claude Code accepts a plugin.json with no skills field (data-only mount succeeds)      |
| T14 | **HIGH**| library upgraded 1.0→1.1 + new required section | stale PRD on disk            | validator warns on stale doc, enforces on new authoring                                |
| T15 | **HIGH**| helix + corrupt library mount (truncated prd.yml) | empty workspace             | distinct diagnostic from setup-gap; no template improvisation                          |
| T16 | **HIGH**| library + helix (graph.yml has A↔B cycle) | broken graph.yml                  | validator detects cycle; names BOTH offending node ids                                 |
| T17 | **HIGH**| library + helix (requires: dangling node) | broken graph.yml                  | validator detects dangling edge; names missing node id                                 |
| T18 | **HIGH**| library + helix + override removing canonical section | weak-adr overlay        | validator rejects weakening override                                                   |
| T18b| medium  | library + helix + override extends unknown library type | orphan-adr overlay    | validator rejects dangling extends (parallel to T11)                                   |
| T19 | **HIGH**| helix only (library NOT installed)        | existing PRD on disk              | EDIT to existing doc blocked with setup-gap; no Risks improvisation                    |
| T20 | **HIGH**| helix-library with skills:_data workaround | empty                            | install succeeds, skill never routes on adversarial compound prompt                    |
| T21 | medium  | helix-library with malformed _data SKILL.md | empty                           | install fails with diagnostic naming SKILL.md/frontmatter                              |
| T22 | medium  | library + helix + helix-infra              | docs/helix/02-design/.gitkeep only| signal is artifact, not directory; no silent route on no-artifact repo                 |
| T23 | medium  | library + helix + helix-infra, HELIX_METHODOLOGY=helix-infra | T5 workspace    | env override wins over repo shape; ADR lands at docs/adr/                              |

### Scenario detail

#### T1 — library only

- **Installed:** `helix-library`
- **Workspace:** empty.
- **Prompts:** `01-list-types.txt` ("list the document types you know about").
- **Assertion (`expected/01-list-types.json`):** `assert: "prose_match"`,
  expect the response to either (a) name several library types
  (prd, adr, runbook, etc.) without committing to a methodology, or
  (b) state plainly that no methodology skill is active. The library is
  data; it routes nothing on its own.

#### T2 — helix only (library missing) [HIGH RISK]

- **Installed:** `helix` (NOT `helix-library`).
- **Workspace:** `docs/helix/01-frame/prd.md` with frontmatter
  `library_type: library:prd` and one body section.
- **Prompts:**
  - `01-read-prd.txt` ("what does this PRD say?") — must succeed; existing
    docs are read-only-OK without the library.
  - `02-author-prd.txt` ("create a new PRD for feature X") — must produce
    the setup-gap message documented in design §7.2, NOT improvised
    template output.
- **Assertions:**
  - `01`: `assert: "prose_match"`, must contain a summary of the PRD;
    must NOT contain the setup-gap phrase.
  - `02`: `assert: "prose_match"`, must contain the setup-gap phrase
    (regex on `helix-library.*not installed` or the design's exact
    string) AND must NOT contain a `# Problem` heading (i.e. the
    template was not improvised).

#### T3 — library + helix (happy path)

- **Installed:** `helix-library`, `helix`.
- **Workspace:** `docs/helix/01-frame/prd.md` with valid frontmatter.
- **Prompts:**
  - `01-author-section.txt` ("add a Risks section to the PRD").
- **Assertion (`expected/01-author-section.json`):** `assert:
  "stream_json_tool_use"`, expect a `tool_use` event for `Edit` or
  `Write` against the PRD file. Optional secondary `prose_match` for
  the assistant's confirmation message.

#### T4 — library + helix-infra (happy path)

- **Installed:** `helix-library`, `helix-infra`.
- **Workspace:** `main.tf`, `terraform/modules/network/main.tf`.
- **Prompts:**
  - `01-author-adr.txt` ("record an ADR for choosing VPC peering over
    transit gateway").
- **Assertion:** `assert: "stream_json_tool_use"`, expect a `Write`
  `tool_use` whose path matches `docs/adr/.*\.md` (the helix-infra
  default ADR location) and whose content includes
  `library_type: library:adr`.

#### T5 — product-shaped repo, both methodologies installed [HIGH RISK]

- **Installed:** `helix-library`, `helix`, `helix-infra`.
- **Workspace:** `docs/helix/01-frame/prd.md` and `docs/helix/02-design/`.
  NO `*.tf` files. NO `terraform/`.
- **Prompts:**
  - `01-author-adr.txt` ("record an ADR for our auth approach").
- **Assertion:** `assert: "stream_json_tool_use"` AND `prose_match`.
  - The `Write` `tool_use` path MUST match `docs/helix/02-design/.*\.md`
    (helix's ADR location), NOT `docs/adr/.*`.
  - The assistant prose MAY contain a disambiguation banner ("I'm
    treating this as helix because the repo is product-shaped — say
    `use helix-infra` to override") but MUST NOT silently pick
    helix-infra.

#### T6 — *.tf repo, both methodologies installed [HIGH RISK]

- **Installed:** `helix-library`, `helix`, `helix-infra`.
- **Workspace:** `main.tf` only. NO `docs/helix/`.
- **Prompts:**
  - `01-author-adr.txt` ("record an ADR for our subnet layout").
- **Assertion:** `assert: "stream_json_tool_use"`.
  - The `Write` `tool_use` path MUST match `docs/adr/.*\.md`
    (helix-infra's ADR location), NOT `docs/helix/02-design/.*`.
  - File-pattern detection of `*.tf` wins over the absence of helix
    repo shape.

#### T7 — mixed repo (both signals) [HIGH RISK]

- **Installed:** `helix-library`, `helix`, `helix-infra`.
- **Workspace:** `docs/helix/01-frame/prd.md` AND `main.tf`.
- **Prompts:**
  - `01-author-adr.txt` ("record an ADR").
- **Assertion:** `assert: "prose_match"` AND `stream_json_tool_use`.
  - Most-specific match: the assistant MUST surface a disambiguation
    banner offering both methodologies (regex on
    `helix-infra.*or.*helix|helix.*or.*helix-infra`).
  - No silent pick. If a `Write` `tool_use` fires before the user
    disambiguates, the fixture fails.

#### T8 — library + helix + helix-web (future) [DEFER]

- **Installed:** placeholder.
- **Workspace:** n/a.
- **Status:** deferred until `helix-web` exists as a methodology
  plugin. README.md in the fixture explains the deferral. No
  workspace/prompts/expected files.

#### T9 — local:my-adr override (shadowing)

- **Installed:** `helix-library`, `helix`.
- **Workspace:** `docs/helix/02-design/_overlays/my-adr/spec.yml`
  declaring a `local:my-adr` type that shadows `library:adr` for one
  binding in `graph.yml`.
- **Prompts:**
  - `01-author-adr.txt` ("record an ADR in the design phase").
- **Assertion:** `assert: "stream_json_tool_use"` against `Write`,
  AND `prose_match` for the local-override sections (the `local:my-adr`
  spec adds a non-default `Customer Impact` section).

#### T10 — bare slug rejected

- **Installed:** `helix-library`, `helix`.
- **Workspace:** invalid `graph.yml` with a node `binds: adr` (bare
  slug, not `library:adr`).
- **Prompts:**
  - `01-run-validator.txt` ("run the graph validator").
- **Assertion:** `assert: "validator_exit"`, expect non-zero exit and
  stderr matching `bare slug|must be namespaced`.

#### T11 — nonexistent library type rejected

- **Installed:** `helix-library`, `helix`.
- **Workspace:** invalid `graph.yml` with `binds: library:not-a-real-type`.
- **Prompts:**
  - `01-run-validator.txt`.
- **Assertion:** `assert: "validator_exit"`, expect non-zero exit and
  stderr matching `unknown library type|not found in library`.

#### T12 — section_aliases extends adr

- **Installed:** `helix-library`, `helix`.
- **Workspace:** `docs/adr/0001-pick-x.md` whose heading uses the
  alias `## Outcome` instead of the canonical `## Decision`.
  Methodology declares `section_aliases: {Decision: [Outcome]}` for
  `library:adr`.
- **Prompts:**
  - `01-run-validator.txt`.
- **Assertion:** `assert: "validator_exit"`, expect **exit 0**; the
  alias resolves to the canonical name and the doc validates.

#### T13 — plugin.json with no skills field [HIGH RISK]

- **Installed:** `helix-library` only.
- **Workspace:** empty.
- **Prompts:** none (this is a pure install test).
- **Assertion:** `assert: "install_result"`, expect success. The
  `plugin.json` in the library deliberately has NO `skills:` field
  (this is the core question from risk #2 in the FINAL plan: does
  Claude Code accept data-only plugins?). If install fails with
  "missing skills field," the architecture must fall back to the
  `skills/_data/SKILL.md` workaround documented in the plan.

#### T12b — section_aliases removed (negative companion to T12)

Same workspace as T12 but `methodology.yml` declares no aliases.
The doc (still using `## Outcome`) must FAIL with a "missing
Decision" diagnostic. Pair (T12 + T12b) pins the alias as the
load-bearing input; a validator that silently skips
`required_sections` checks for `library:adr` cannot pass both.

#### T14 — library upgrade adds required_section [HIGH RISK]

Library upgraded 1.0.0 → 1.1.0 between sessions (overlay mounted
via `workspace/library-overlay/`). The new spec requires a
`Success Metrics` section; a pre-existing PRD on disk lacks it.
Contract A: validator warns on stale docs (exit 0 + drift hint) but
enforces on new authoring (the second prompt's Write MUST include
`Success Metrics` + `library_type_version: 1.1.0`). If the family
elects contract B (error on stale), flip `expect_exit_nonzero` in
the fixture and document.

#### T15 — corrupt/half-mounted library [HIGH RISK]

`library-corrupt/types/prd.yml` is truncated mid-document; the
runner mounts it via `helix-library:corrupt`. Authoring prompt
must produce a diagnostic distinct from the setup-gap
(`corrupt|truncated|malformed|unreadable|invalid|parse error|broken`
in proximity to library/prd.yml/spec) and MUST NOT improvise the
template. The not-installed phrase is explicitly forbidden — the
two failure modes must be distinguishable to users.

#### T16 — graph.yml cycle [HIGH RISK]

`A requires B; B requires A`, no `allowed_cycles` annotation.
Validator must exit non-zero AND name both offending node ids. A
cycle-detection regression that hangs the validator is caught by
the 10s wall-clock ceiling in §Runner mechanics.

#### T17 — graph.yml dangling requires [HIGH RISK]

`requires: [01-frame/this-node-does-not-exist]`. Validator must
exit non-zero AND name the missing target. Silent skip at runtime
is the failure mode this fixture prevents.

#### T18 — local override weakens canonical [HIGH RISK]

`local:weak-adr extends library:adr` but its `required_sections`
list omits `Consequences`. Validator must reject AND name the
stripped section. T9 covers the additive happy path; T18 covers the
subtractive failure path.

#### T18b — local override extends unknown library type

`extends: library:not-a-real-base`. Parallel to T11 on the override
surface. Validator must reject AND name the missing base type.

#### T19 — edit-existing PRD with library missing [HIGH RISK]

T2 covers read (allowed) vs create-new (blocked). T19 covers the
boundary case: EDIT-EXISTING. The library is required for edits;
the setup-gap fires; no Write tool_use; no `## Risks` improvisation
in prose. Highest-traffic real-world authoring action.

#### T20 — skills/_data SKILL.md workaround (positive) [HIGH RISK]

`plugin.json` with `skills: ["skills/_data"]` and a SKILL.md whose
frontmatter says `trigger: never`. Install must succeed, mount must
leave the SKILL.md on disk, and the skill must NEVER route — even
on an adversarially compound prompt (`list types + start discover +
write an ADR`). This is the on-path test for the documented T13
fallback; the architecture forks on T13's outcome and T20 covers
the previously untested branch.

#### T21 — skills/_data SKILL.md malformed

Companion to T20. SKILL.md has unterminated frontmatter; install
must FAIL with a diagnostic naming the malformation. Prevents
silent mount of broken workarounds.

#### T22 — empty docs/helix/ (.gitkeep only)

Workspace has `docs/helix/02-design/.gitkeep` and nothing else. No
artifact, no `*.tf`. Pins the signal definition: the repo-shape
rule keys on ARTIFACT presence, not directory existence. NO silent
Write; prose must disambiguate or declare no-signal.

#### T23 — HELIX_METHODOLOGY env override exercised

Workspace identical to T5 (product-shaped), but `env.txt` sets
`HELIX_METHODOLOGY=helix-infra`. The env MUST win over repo shape:
exactly one Write at `docs/adr/`, no Write at `docs/helix/02-design/`.
First fixture that actually USES the env contract surface T7's
expected/ mentions.

## Runner mechanics

The fixture runner (authored in Phase 6 of this workflow) does the
following for each fixture directory:

0. **Skip rule (pinned).** If the fixture's `README.md` has top-level
   frontmatter `status: deferred`, the runner reports SKIPPED and
   moves on. This is the ONE skip signal — absence of
   `plugins-installed.txt` is treated as a fixture authoring error,
   not a skip. (Phase 4 review folded this in to resolve T8's
   ambiguous "absent file OR DEFERRED tag" runner rule.)
1. Materialize a clean temp dir, copy `workspace/` into it. If
   `env.txt` is present, parse it as `KEY=VALUE` lines and export each
   pair into the Claude Code subprocess environment.
2. Parse `plugins-installed.txt`; for each plugin name, mount the
   monorepo subdirectory as a Claude Code plugin via
   `claude --plugin-dir <repo>/<subdir>`. (The monorepo layout means
   library/, product/, infra/ are sibling subdirs.) Special tokens:
   `helix-library:corrupt` mounts the fixture's `workspace/library-corrupt/`
   tree as the library (T15); a fixture-local `workspace/library-overlay/`
   directory is mounted as a shadow library overlay when prompted by the
   validator command (T14).
3. For each `prompts/NN-name.txt` in lexicographic order:
   - Pipe the prompt to `claude -p --output-format stream-json` in
     the temp dir cwd.
   - Capture the full stream-json transcript to
     `<results-dir>/<fixture-id>/<NN-name>.stream.jsonl`.
   - Also persist the final assistant text to
     `<results-dir>/<fixture-id>/<NN-name>.prose.txt`.
4. Compare each transcript against the corresponding
   `expected/NN-name.json` using the assertion type declared in the
   `assert` field.
5. Report PASS / FAIL with the failing event/string surfaced AND a
   pointer to the per-fixture artifact dir so reviewers can tell
   "wrong tool path" from "tool didn't fire" from "prose pattern
   missed" without re-running.

### Assertion schema (extended in Phase 4)

Every `expected/NN.json` declares `assert` as one of
`prose_match | stream_json_tool_use | validator_exit | install_result`.
Phase 4 review folded in these schema extensions:

- **`expect_tool_use.exactly_one: true`** (alias: `max_count: 1`) —
  the named tool_use must fire exactly once. Used by T3, T4, T5, T9,
  T14, T23 to forbid double-write escapes.
- **`expect_tool_use.content_regex_all: [...]`** — all listed regex
  must match the tool_use's content. Used by T3 (heading + body),
  T4 (frontmatter + canonical sections), T9 (order pin), T14
  (frontmatter + new required section).
- **`expect_tool_use.content_regex_forbid: [...]`** — any match
  fails the assertion. Used by T9 to pin section order by forbidding
  the canonical-only order.
- **`expect_tool_use.name_regex: '^Read$'`** — Read tool_use
  assertions (not just Write/Edit). Used by T2's read-prd fixture to
  prove the agent opened the file.
- **`stderr_match_all: [...]`** — every pattern must match (vs.
  `stderr_match_any` which requires only one). Used by T10/T11/T16/T17/T18
  to require both a generic-error pattern AND the offending node id /
  type / section by name.
- **`prose_match.must_match_any_2: [...]`** — a second
  `must_match_any` block, ANDed with the first. Used by T7 to require
  both the structural banner shape AND a disambiguation verb.
- **`install_result.command_resolver`** + **`command_candidates`** —
  the runner probes `claude plugins --help` first and picks the first
  command from `command_candidates` whose verb appears in the help
  output. Used by T13 / T20 / T21 because the install CLI form
  (`plugin install` vs `plugins install`; `--from-dir` vs positional)
  is not pinned by Claude Code yet.
- **`install_result.post_install_assert.paths_must_exist`** /
  **`paths_must_be_readable`** — filesystem check after install. Used
  by T13 / T20 to prove the plugin is MOUNTED, not just that install
  exited 0.
- **`validator_exit`**: every validator invocation must complete
  within 10s wall-clock and 100MB RSS. Used to catch O(N^2) cycle
  detection regressions before they reach a real user (also see
  "Open follow-ups" perf entry).

### Validator CLI signature (pinned in Phase 4)

The library ships `library/scripts/helix_graph_check.py`. Its CLI:

```
python3 library/scripts/helix_graph_check.py [--methodology FILE]
    [--library-overlay DIR] [--override FILE] [--doc FILE]
    [GRAPH.yml ...]
```

- Positional arguments are graph YAML files (or document paths when
  `--doc` is used).
- `--methodology FILE` — points at a methodology.yml that supplies
  section_aliases and other resolver inputs (T12 / T12b).
- `--library-overlay DIR` — mounts a tree that shadows the installed
  library's type specs (T14).
- `--override FILE` — validates an override spec.yml in isolation
  (T18 / T18b).
- `--doc FILE` — validates a single document against the resolved
  schema (T12 / T14).
- Non-zero exit on any validation failure; stderr carries the
  diagnostic; stdout is reserved for the rendered graph or
  machine-readable summary.

T10/T11/T16/T17/T18/T18b all use this signature; T12 and T14 add the
`--methodology` and `--library-overlay` flags respectively.

The runner is **deterministic on structure** (stream-json events,
exit codes, regex matches on prose) and explicitly **avoids
semantic LLM-judged passes**. A flake in the prose generator that
still produces a valid `tool_use` event against the right path
passes; that is intentional — we are testing the family wiring, not
the model.

## Pass criteria per fixture

A fixture passes when:

- All prompts in `prompts/` were dispatched without runner error.
- Every `expected/NN.json` assertion evaluated to `true`.
- For `stream_json_tool_use` assertions: the named tool event
  appeared (or did not appear, for negative assertions) at least
  once in the transcript, and (if a `path_match` or `content_match`
  regex is declared) it matched.
- For `prose_match` assertions: every required substring/regex hit;
  every forbidden substring/regex missed.
- For `validator_exit` assertions: the validator process exited
  with the declared code; if `stderr_match` is declared, it matched.
- For `install_result` assertions: install exit code matched; if a
  `stderr_match` regex is declared, it matched.

The family migration is acceptance-complete when T1–T7, T9–T13,
T12b, and T14–T23 are all green simultaneously on the monorepo
HEAD. T8 stays deferred (status: deferred frontmatter).

## Out of scope

- **T8 (helix + helix-web).** `helix-web` does not exist yet. The
  fixture is scaffolded as a placeholder README so the slot is
  reserved and the numbering doesn't shift when web lands. No
  workspace, prompts, or expected files until then.
- **Semantic-quality judgments.** Fixtures do not assert "the PRD is
  well-written" or "the ADR captures the right decision." They
  assert family wiring (precedence, resolution, validation).
- **DDx bead schema (`graph_node:` field).** Tested separately in
  the existing DDx test suite; not part of the family fixtures.
- **Cross-major version drift.** The family ships in lockstep from a
  single monorepo commit; cross-major scenarios cannot occur.

### Deferred to v1.1 (medium-severity gaps from Phase 3 review)

- **Slash-command namespace collision.** Both methodologies (or a
  future third) registering the same `/review` or `/align` command.
  Design is silent on slash-namespace policy today; the contract
  surface (namespaced `/helix-x` vs last-installed-wins vs ambiguous-
  reject) needs an ADR before a fixture can be authored. Tracked as
  open question for v1.1.
- **Multi-workspace cwd switches in one session.** Two `cd`s within
  one Claude session, distinct workspaces, distinct expected
  activations. Real risk, but the runner currently models one cwd
  per fixture; multi-cwd support is a meaningful runner change.
  Tracked for v1.1.
- **DDx bead `graph_node:` pointing at a renamed/removed library
  node.** The family ships renames in its monorepo PR cadence; cross-
  boundary stale references are a real concern. v1 mitigation: DDx
  bead schema (Phase D0 in the FINAL plan) lands BEFORE the rename;
  a guard pass over the existing bead corpus runs in the migration
  PR. A first-class fixture for the renamed-node case is deferred
  to v1.1 (covered by the migration guard for v1).

## Open follow-ups (low-severity, deferred)

- **Validator perf at scale.** Synthetic `graph.yml` with N=500 /
  N=5000 nodes, assert <2s wall-clock and <100MB RSS for N=1000.
  Validator is py3-stdlib; O(N^2) cycle detection is easy to write
  accidentally. The §"Assertion schema" 10s / 100MB ceiling above is
  a defensive default; a dedicated perf fixture should land before
  any methodology grows past ~200 graph nodes. Tracked as `T-perf`
  for v1.1.
- **Slash-namespace policy ADR.** See deferred list above.
