# Test Plan: helix Family Bench Fixtures

- **Date:** 2026-06-04
- **Status:** Authoring (Phase 2 of the helix-library planning workflow)
- **Companion docs:**
  - [plan-2026-06-03-helix-library-FINAL.md](./plan-2026-06-03-helix-library-FINAL.md)
  - [design-2026-06-03-helix-library-split.md](./design-2026-06-03-helix-library-split.md)
  - [plan-2026-06-03-helix-library-migration.md](./plan-2026-06-03-helix-library-migration.md)

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
| T13 | **HIGH**| helix-library only (plugin.json no skills:)| n/a                                 | Claude Code accepts a plugin.json with no skills field (data-only mount succeeds)      |

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

## Runner mechanics

The fixture runner (authored in Phase 6 of this workflow) does the
following for each fixture directory:

1. Materialize a clean temp dir, copy `workspace/` into it.
2. Parse `plugins-installed.txt`; for each plugin name, mount the
   monorepo subdirectory as a Claude Code plugin via
   `claude --plugin-dir <repo>/<subdir>`. (The monorepo layout means
   library/, product/, infra/ are sibling subdirs.)
3. For each `prompts/NN-name.txt` in lexicographic order:
   - Pipe the prompt to `claude -p --output-format stream-json` in
     the temp dir cwd.
   - Capture the full stream-json transcript.
4. Compare each transcript against the corresponding
   `expected/NN-name.json` using the assertion type declared in the
   `assert` field.
5. Report PASS / FAIL with the failing event/string surfaced.

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

The family migration is acceptance-complete when T1–T7 and T9–T13
are all green simultaneously on the monorepo HEAD. T8 stays
deferred.

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
