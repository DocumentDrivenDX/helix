---
title: "Technical Design: TD-013 — Multi-Runtime Install"
slug: TD-013-multi-runtime-install
weight: 820
activity: "Design"
source: "02-design/technical-designs/TD-013-multi-runtime-install.md"
generated: true
collection: technical-designs
---

> **Source identity** (from `02-design/technical-designs/TD-013-multi-runtime-install.md`):

```yaml
ddx:
  id: TD-013
  depends_on:
    - FEAT-013
    - helix.prd
```

# Technical Design: TD-013 — Multi-Runtime Install

**Feature**: [[FEAT-013-runtime-install-coverage]]
**Related**: [[helix.prd]] (R-4 runtime-neutral content, R-7 per-runtime
packages), [[CONTRACT-003-ddx-adapter-boundary]]

## Scope

- Story-level design covering: the per-runtime adapter files committed
  in the HELIX repo, the Genie packaging scripts, the install
  documentation updates, and the Docker-plus-screencast test harness.
- Inherits the no-fork policy from [`docs/install/README.md`](https://github.com/DocumentDrivenDX/helix/blob/main/docs/install/README.md)
  and the runtime-neutrality constraint from PRD R-4.
- Out of scope: changes to the routing skill body, changes to the
  artifact catalog, marketplace listing on third-party registries
  beyond what the agentskills.io spec enables.
- Governing artifacts: FEAT-013, PRD, agentskills.io spec, per-runtime
  research notes under `docs/resources/agents/`.

## Acceptance Criteria

1. **Given** a clean HELIX checkout, **when** `just install-test` runs,
   **then** each of five runtime scenarios executes its install,
   produces a passing static verification, and captures a screencast
   artifact in its scenario directory.
2. **Given** a workspace administrator with a Databricks PAT, **when**
   `python scripts/install-genie.py` runs with required env vars,
   **then** the bundle is uploaded to
   `/Workspace/.assistant/skills/helix/` and `python scripts/verify-genie.py`
   reports success without invoking any chat API.
3. **Given** a Claude Code user with API key, **when** they run
   `claude plugin marketplace add easel/helix && claude plugin install
   helix@helix --scope user -y`, **then** the plugin loads and
   `claude -p "list HELIX routing modes"` returns a response naming
   `align`, `frame`, `evolve`, `review`, `polish`.
4. **Given** the HELIX repo, **when** `grep -rn '"supervisory autopilot"'
   .claude-plugin/`, **then** zero matches.

## Technical Approach

**Strategy**: ship five thin adapter surfaces in the repo, plus an
isolated Python package for Genie workspace uploads. The HELIX content
(`skills/helix/`, `workflows/`) stays exactly where it is; everything
new is either an adapter file, a build/install script, or a test
scenario. Adopt the [agentskills.io specification](https://github.com/DocumentDrivenDX/helix/blob/main/docs/resources/agents/agentskills-spec.md)
as the canonical skill format so the routing skill is portable as-is
across DDx, Claude Code, Codex CLI, and Genie Code; Copilot consumes
the same content via `.github/copilot-instructions.md`.

**Key Decisions**:

- **Single plugin manifest for DDx + Claude Code.** DDx already reads
  the Claude Code plugin layout. One `.claude-plugin/plugin.json` serves
  both runtimes. Confirmed against observed DDx behavior at
  `~/.ddx/plugins/helix/.claude-plugin/`.
- **Marketplace lives in the same repo as the plugin.** The
  `.claude-plugin/marketplace.json` file sits alongside `plugin.json`
  in the HELIX repo. Users add `easel/helix` as a marketplace and
  install the `helix` plugin from it. This avoids a second repo for
  distribution.
- **Codex CLI has no native install command.** Two paths are documented:
  `npx skills add easel/helix -a codex` (cross-runtime CLI from Vercel
  Labs, requires Node) and a manual `mkdir + cp` Dockerfile recipe. No
  Codex-specific adapter file is added to the repo since Codex
  discovers skills from `~/.codex/skills/` or `~/.agents/skills/` and
  consumes the existing `skills/helix/SKILL.md` directly.
- **Copilot uses `.github/copilot-instructions.md` only.** GitHub App
  extensions were deprecated November 2025; MCP is the alternative for
  tool-using extensions but methodology-only HELIX does not need tools.
- **Genie packaging materializes a bundle in `dist/genie-bundle/`.**
  Genie expects a self-contained skill directory at
  `/Workspace/.assistant/skills/helix/`. The build script assembles
  this from `skills/helix/SKILL.md` and `workflows/activities/`,
  placing the catalog under `helix/references/activities/` inside the
  bundle. This is repackaging, not forking — the source content is
  unchanged, and the assembly is reproducible.
- **End-to-end Genie verification requires a browser.** Genie Code has
  no public chat API. The test harness combines headless install
  verification (`scripts/verify-genie.py`) with a manual browser
  procedure plus screencast capture.
- **vhs (not asciinema) for terminal screencasts.** vhs's `.tape`
  files are scriptable and reproducible; asciinema requires interactive
  capture. Existing `.cast` files under `website/static/demos/` stay
  for the marketing site; install tests use vhs.

**Trade-offs**:

- Marketplace-in-same-repo simplifies distribution but couples plugin
  versioning to marketplace listing — if HELIX ever wants to publish a
  multi-plugin marketplace, this needs revisiting.
- Putting Genie packaging scripts under `scripts/` blurs the line
  between "methodology content" and "tooling". Mitigated by keeping
  them isolated to install/test work — they do not implement any
  HELIX methodology behavior.
- Static-only CI checks miss real install regressions (e.g. Claude
  Code marketplace flow that breaks under a new CLI version).
  Functional checks gated by `TEST_FUNCTIONAL=1` fill the gap when
  someone wants to pay the token cost.

## Component Changes

### New: `.claude-plugin/marketplace.json`

- **Purpose**: enable Claude Code marketplace install of HELIX.
- **Interfaces**: read by Claude Code when a user runs
  `/plugin marketplace add easel/helix`.
- **Schema** (per [claude-code-plugins.md](https://github.com/DocumentDrivenDX/helix/blob/main/docs/resources/agents/claude-code-plugins.md)):
  ```json
  {
    "name": "helix",
    "description": "HELIX methodology marketplace",
    "plugins": [
      {
        "name": "helix",
        "source": ".",
        "description": "HELIX methodology, artifact catalog, and routing skill"
      }
    ]
  }
  ```
- **Files**: `.claude-plugin/marketplace.json`

### Modified: `.claude-plugin/plugin.json`

- **Current State**: `description` says "supervisory autopilot for
  AI-assisted software delivery".
- **Changes**: `description` becomes "HELIX methodology, artifact
  catalog, and routing skill for AI-assisted development." Verify
  `version` is current; bump on tag.
- **Files**: `.claude-plugin/plugin.json`

### New: `.github/copilot-instructions.md`

- **Purpose**: enable GitHub Copilot auto-discovery of HELIX as
  repo-scoped instruction content. Adopter repos can copy this file
  verbatim or include it via a symlink/include.
- **Interfaces**: read automatically by Copilot CLI, IDE Copilot Chat,
  github.com Copilot Chat, code review, cloud agent.
- **Files**: `.github/copilot-instructions.md`

### New: `scripts/build-genie-bundle.sh`

- **Purpose**: assemble a Genie-compliant bundle from HELIX source.
- **Interfaces**: input — repo at HEAD; output —
  `dist/genie-bundle/helix/SKILL.md` and
  `dist/genie-bundle/helix/references/activities/<NN>-<activity>/...`
- **Implementation**: shell script (~30 lines) using `cp -r` and
  optionally `yq` or `python` to validate the SKILL.md frontmatter
  matches the agentskills.io spec.
- **Files**: `scripts/build-genie-bundle.sh`,
  `dist/genie-bundle/` (gitignored; built on demand)

### New: `scripts/install-genie.py`

- **Purpose**: upload the assembled bundle to a Databricks workspace
  using the Databricks Python SDK.
- **Interfaces**:
  - Inputs: env vars `DATABRICKS_HOST`, `DATABRICKS_TOKEN`; optional
    flag `--target` (default `/Workspace/.assistant/skills/helix`);
    optional flag `--bundle` (default `dist/genie-bundle/helix`).
  - Outputs: progress lines to stderr; exit code 0 on success.
- **Implementation**: Python using `databricks.sdk.WorkspaceClient`.
  Walk the bundle directory and call `w.workspace.upload(path=...,
  content=..., overwrite=True)` per file. Create parent directories
  with `w.workspace.mkdirs(...)`. Fail fast if env vars missing.
- **Files**: `scripts/install-genie.py`

### New: `scripts/verify-genie.py`

- **Purpose**: verify the installed bundle without invoking a chat API.
- **Interfaces**:
  - Inputs: env vars + `--target` (same as install).
  - Outputs: pass/fail summary; exit 0 if all checks pass.
- **Implementation**: Python using `databricks.sdk` to `list` and
  `export` files under the target. Validate that `SKILL.md` exists,
  parses as YAML frontmatter + Markdown body, contains required
  `name` and `description` fields, and that `references/activities/`
  is populated.
- **Files**: `scripts/verify-genie.py`

### Modified: `docs/install/README.md`

- **Current State**: lists DDx, Claude Code, and Codex (lumped CLI +
  Copilot). Three runtime cards.
- **Changes**: lists five runtimes (DDx, Claude Code, OpenAI Codex CLI,
  GitHub Copilot, Databricks Genie Code). Each card names the
  canonical one-step install command.
- **Files**: `docs/install/README.md`

### Modified: `docs/install/claude-code.md`

- **Current State**: recommends user-global symlink as the primary
  path.
- **Changes**: marketplace flow becomes primary
  (`/plugin marketplace add easel/helix` + `/plugin install
  helix@helix`); `--plugin-dir` documented as the dev/CI fallback;
  user-global symlink described as a development-only convenience.
- **Files**: `docs/install/claude-code.md`

### Modified: `docs/install/codex.md`

- **Current State**: covers both Codex CLI and Copilot/Copilot
  extensions in one doc with "git clone" as the install method.
- **Changes**: scope narrows to OpenAI Codex CLI only. "git clone"
  replaced with `npx skills add easel/helix -a codex` (primary) and a
  manual `mkdir + cp` Docker recipe (fallback). Renamed to retain the
  same filename for backward link compatibility.
- **Files**: `docs/install/codex.md`

### New: `docs/install/copilot.md`

- **Purpose**: GitHub Copilot-specific install guide split off from
  the former combined doc.
- **Content**: `.github/copilot-instructions.md` as canonical install,
  `.github/instructions/*.instructions.md` with `applyTo:` as
  per-path scoping, Copilot CLI (`gh copilot`) as headless test
  surface, GitHub App extensions deprecated note.
- **Files**: `docs/install/copilot.md`

### Modified: `docs/install/databricks-genie.md`

- **Current State**: recommends `helix-genie-bundle/skill/SKILL.md`
  wrapper layout (incorrect per agentskills.io spec); carries
  "format still moving" hedge.
- **Changes**: documents the correct `helix/SKILL.md` layout (parent
  dir name = `name:` per spec). Drops the moving-format hedge. Adds
  `scripts/install-genie.py` and `scripts/verify-genie.py` as the
  canonical install path. Replaces "use the HELIX skill" invocation
  phrasing with the `@helix` mention syntax.
- **Files**: `docs/install/databricks-genie.md`

### Modified: `justfile`

- **Current State**: `install` recipe calls `bash the HELIX skill doctor
  --fix` which fails because `the HELIX skill` is gone.
- **Changes**: `install` recipe reduced to `ddx install helix --force`
  followed by `bash tests/install/ddx/verify.sh`. New `install-test`
  recipe builds and runs the full Docker scenario set.
- **Files**: `justfile`

### New: `tests/install/`

Test scaffolding plus one subdirectory per runtime.

- **`tests/install/README.md`** — how to run the harness, required
  env vars, expected outputs.
- **`tests/install/shared/expected-modes.txt`** — canonical list of
  HELIX routing modes used by functional verification.
- **`tests/install/shared/verify-skill-layout.sh`** — common static
  invariants asserted by every runtime's `verify.sh`.
- **`tests/install/ddx/`** — `Dockerfile`, `install.sh`, `verify.sh`,
  `record.tape`. Uses `ddx install helix --local /workspace/helix --force`
  against a mounted source.
- **`tests/install/claude-code/`** — `Dockerfile`, `install.sh`,
  `verify.sh`, `record.tape`. Uses `claude plugin marketplace add` +
  `claude plugin install`.
- **`tests/install/codex-cli/`** — `Dockerfile`, `install.sh`,
  `verify.sh`, `record.tape`. Uses `npx skills add` (Node-based base
  image) or manual filesystem copy.
- **`tests/install/copilot-cli/`** — `Dockerfile`, `install.sh`,
  `verify.sh`, `record.tape`. Uses the `gh` CLI with Copilot
  extension; verifies via `.github/copilot-instructions.md`
  discovery.
- **`tests/install/genie/`** — `install.py` (calls
  `scripts/install-genie.py`), `verify.py` (calls
  `scripts/verify-genie.py`), `test-procedure.md` (manual browser
  steps), `screencast-template.md` (capture spec), `recordings/`
  (output directory for captured screencasts).
- **Files**: as above.

## API/Interface Design

### `scripts/install-genie.py`

```text
Usage: scripts/install-genie.py [--bundle PATH] [--target WORKSPACE_PATH]

Required env: DATABRICKS_HOST, DATABRICKS_TOKEN
Optional env: DATABRICKS_PROFILE (overrides host/token)

Behavior:
  1. Validate env and inputs; fail with one-line error if invalid.
  2. Connect via databricks.sdk.WorkspaceClient.
  3. mkdirs <target>; mkdirs <target>/references/activities.
  4. For each file in <bundle> (recursive), upload with overwrite=True.
  5. Print summary: N files uploaded, M dirs created.

Exit codes:
  0  success
  2  missing or invalid env
  3  bundle not present (run scripts/build-genie-bundle.sh first)
  4  upload error
```

### `scripts/verify-genie.py`

```text
Usage: scripts/verify-genie.py [--target WORKSPACE_PATH]

Required env: DATABRICKS_HOST, DATABRICKS_TOKEN

Behavior:
  1. databricks workspace list <target>; assert SKILL.md present.
  2. Export SKILL.md; parse YAML frontmatter.
  3. Assert frontmatter has `name: helix` and `description` of 1..1024 chars.
  4. databricks workspace list <target>/references/activities;
     assert 00-discover through 06-iterate are present.
  5. Print pass/fail per check; exit 0 only if all pass.

Exit codes:
  0  all checks pass
  2  missing or invalid env
  5  install incomplete or malformed
```

### `tests/install/shared/verify-skill-layout.sh`

```text
Usage: verify-skill-layout.sh <skill-root>

Asserts:
  - <skill-root>/SKILL.md exists
  - SKILL.md frontmatter has name == basename(<skill-root>)
  - SKILL.md frontmatter has description of 1..1024 chars
  - No sibling helix-* directories exist (legacy detection)
  - <skill-root> contains no .git directory (not a working tree)

Exit codes:
  0  pass
  1  fail (prints which assertion failed)
```

## Data Model Changes

None.

## Integration Points

| From | To | Method | Data |
|---|---|---|---|
| HELIX repo | DDx registry | `ddx install` (registry-pull) | plugin archive |
| HELIX repo | Claude Code | marketplace add + install | `marketplace.json` + `plugin.json` |
| HELIX repo | Codex CLI | `npx skills add` or filesystem copy | `skills/helix/` directory |
| HELIX repo | GitHub Copilot | `.github/copilot-instructions.md` auto-discovery | markdown context |
| HELIX repo → bundle | Databricks workspace | Databricks Python SDK upload | `dist/genie-bundle/helix/` |
| Test harness | each runtime CLI | non-interactive prompt + stdout assertion | `expected-modes.txt` |

### External Dependencies

- **Databricks Python SDK** (`databricks-sdk` PyPI) for Genie install.
  Fallback: use `databricks workspace import` CLI per file.
- **vhs** for terminal screencast capture. Fallback: `asciinema rec`.
- **Docker** for runtime sandboxes. Fallback: run the install scripts
  locally and capture manually.
- **DDx CLI** (already present in dev env) for the DDx scenario.

## Security

- Per-runtime API keys / PATs (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`,
  `GH_TOKEN`, `DATABRICKS_TOKEN`) are read from env vars only; never
  written to disk in the repo or in test artifacts.
- `tests/install/.env.example` lists required variables with empty
  values; never commit `.env`.
- Screencast captures must be reviewed before sharing — they may
  contain transient session output that reveals env state. The
  per-runtime `record.tape` scripts redact env display by default.

## Testing

The feature IS the test harness. Test coverage strategy:

- **Static checks** (no LLM cost): file presence, YAML parse, layout
  invariants. Run on every PR.
- **Functional checks** (LLM cost): one-shot prompt per runtime,
  assert response names expected modes. Gated by `TEST_FUNCTIONAL=1`;
  run on release tags only.
- **Genie manual verification**: captured per release; reviewable
  artifact under `tests/install/genie/recordings/`.
- **Smoke test for stale DDx snapshot**: a scenario that pre-stages a
  v0.3.2 install, runs `ddx install helix --force`, then asserts the
  layout matches the current release.

## Sequencing

The work decomposes into seven phases, captured as beads under
FEAT-013. Phase 0–1 are blocking for the tomorrow Genie milestone.

| Phase | Beads | Description |
|---|---|---|
| 0 | description fix | one-line edit to `plugin.json` |
| 1 | adapter files | `marketplace.json`, `copilot-instructions.md`, Genie scripts |
| 2 | Genie e2e | tomorrow's run: bundle, upload, verify, browser screencast |
| 3 | install doc updates | reflect verified install commands per runtime |
| 4 | test harness scaffolding | `tests/install/` framework |
| 5 | per-runtime Docker scenarios | one per runtime |
| 6 | release | tag v0.3.4 once all above stabilizes |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Claude Code marketplace flow needs a separate marketplace repo, not in-tree | Medium | Medium | Test with `claude --plugin-dir` first; only commit `marketplace.json` after confirming in-repo flow works |
| `npx skills add` does not accept HELIX's directory structure | Low | Medium | Test the command against current `easel/helix` before promoting it to canonical install path; fall back to manual recipe in docs |
| Genie SDK upload corrupts Markdown trees | Medium | High | Dry-run against a user-scoped workspace path first; never run against `/Workspace/.assistant/skills/` on first attempt |
| Functional checks burn budget in CI | Low | Medium | Gate behind `TEST_FUNCTIONAL=1`; default to static-only |
| Screencasts go stale and mislead users | Medium | Medium | Embed HELIX version in each recording; lint as part of release ratchet |
| Marketplace name collision with a hypothetical third-party `helix` | Low | Medium | Document the canonical `easel/helix` reference; refuse install if `.claude-plugin/marketplace.json` points elsewhere |

## Open Questions

1. Does Claude Code's `--plugin-dir` flag treat the directory as
   ephemeral session-only, or as a full install for the session?
   Confirm against current CLI before relying on it in CI.
2. Genie's `references/` subdirectory naming — does Genie load all
   `.md` files under `references/` lazily, or does the skill body need
   to reference each path explicitly? If the latter, `SKILL.md` may
   need updates to enumerate catalog paths under
   `references/activities/`.
3. For the Genie test scenario, do we want CI to fail on missing
   `DATABRICKS_TOKEN`, or skip the scenario? Default: skip with a
   warning; require explicit opt-in via `TEST_GENIE=1` to enforce
   presence.

## Observability

- Each `verify.sh` and `verify.py` prints a single-line summary on
  success and a multi-line diagnostic on failure.
- Screencast captures include the verification output as the final
  on-screen content so reviewers can read pass/fail without watching
  the full recording.
- Release notes for v0.3.4 list which runtimes were verified and
  link to the captured screencasts.
