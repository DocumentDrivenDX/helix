---
ddx:
  id: FEAT-013
  depends_on:
    - helix.prd
---

# Feature Specification: FEAT-013 — Runtime Install Coverage

**Feature ID**: FEAT-013
**Status**: Draft
**Priority**: P0
**Owner**: HELIX maintainers

## Overview

HELIX must be installable as a real plugin or skill across five target
runtimes — DDx, Claude Code, OpenAI Codex CLI, GitHub Copilot, and
Databricks Genie Code — using each runtime's canonical install
mechanism, not `git clone`. This feature delivers the adapter files,
build scripts, and a Docker-plus-screencast test harness that verify
the install works on each runtime. It satisfies PRD R-7
(distribution packages for each target runtime) and is the operational
expression of PRD R-4 (runtime-neutral content packaged identically
across runtimes).

## Ideal Future State

A user lands on the HELIX repo. The README points to five per-runtime
install guides. Each guide names a single supported install command
that works without manual file editing. After running that command,
the user runs a verification step that confirms the routing skill is
discoverable and the catalog is reachable. The repo's CI runs the same
install + verification path in Docker on every release, producing
screencast evidence that each runtime's install path still works.
Genie Code is included in this coverage even though its skill-format
research only recently stabilized.

## Problem Statement

- **Current situation**: Only DDx has a working one-step install
  (`ddx install helix`). The other four runtimes are documented in
  `docs/install/` but lack the adapter files needed for their canonical
  install paths to work. The DDx install itself pulls a stale snapshot
  (observed 0.3.2 vs. repo 0.3.3) and the `.claude-plugin/plugin.json`
  description still says "supervisory autopilot" — wording from before
  the scope collapse. No automated install test exists; the previous
  `tests/test-install.sh` was removed in the cleanup.
- **Pain points**:
  1. Users on Claude Code, Codex CLI, Copilot, or Genie Code cannot
     install HELIX with one supported command.
  2. The DDx install pulls a stale snapshot until a release tag triggers
     a refresh, and the only known refresh command (`bash the HELIX skill
     doctor --fix`) was removed without a replacement.
  3. The current install documentation contains layout errors (e.g.
     Genie bundle wrapper structure) and stale hedges ("Genie format is
     still moving") that no longer match reality.
  4. No screencast or CI evidence demonstrates that any install path
     currently works end-to-end.
- **Desired outcome**: Each of five runtimes has a verified one-command
  install plus an automated test that runs in Docker (or, for Genie,
  via Databricks SDK upload + manual browser verification) and produces
  a captured screencast.

## Functional Areas

| Area | User question or job | Feature responsibility |
|---|---|---|
| Repo adapters | "What files in the repo make HELIX installable on my runtime?" | Commit the adapter files each runtime expects |
| Install docs | "Which command do I run for my runtime?" | Document one canonical install command per runtime |
| Genie packaging | "How do I get HELIX into a Databricks workspace?" | Provide bundle assembly + upload scripts |
| Install verification | "Did the install work?" | Per-runtime verification scripts (static + functional) |
| Test harness | "Does the install path still work on this release?" | Docker-based scenarios + screencast captures |

## Requirements

### Functional Requirements by Area

#### Repo adapters

[ADAPT-01]. The repo MUST contain `.claude-plugin/plugin.json` with an
up-to-date `description` aligned with the PRD ("methodology + artifact
catalog + alignment skill", not "supervisory autopilot").

[ADAPT-02]. The repo MUST contain `.claude-plugin/marketplace.json`
listing the HELIX plugin so Claude Code users can run
`/plugin marketplace add easel/helix` followed by `/plugin install
helix@helix`.

[ADAPT-03]. The repo MUST contain `.github/copilot-instructions.md`
pointing GitHub Copilot at the routing skill (`skills/helix/SKILL.md`)
and the artifact catalog (`workflows/activities/`).

[ADAPT-04]. The `skills/helix/SKILL.md` frontmatter MUST conform to the
[agentskills.io specification](../../resources/agents/agentskills-spec.md)
(parent directory name equals `name:`, required `name` and
`description` fields, sized to fit a progressive-disclosure model).

#### Genie packaging

[GENIE-01]. The repo MUST contain a build script that assembles a
Genie-compliant bundle at `dist/genie-bundle/helix/` from
`skills/helix/SKILL.md` and `workflows/activities/`, with the
agentskills.io directory-name invariant respected.

[GENIE-02]. The repo MUST contain an install script that uploads the
bundle to a Databricks workspace path
(`/Workspace/.assistant/skills/helix/`) using the Databricks Python SDK.

[GENIE-03]. The repo MUST contain a verification script that confirms
the uploaded files are present and the SKILL.md frontmatter parses
without making any chat calls.

#### Install docs

[DOC-01]. `docs/install/README.md` MUST list the five runtimes and
their canonical install commands.

[DOC-02]. Each per-runtime doc under `docs/install/` MUST name a
single canonical install command (not "git clone") plus a verification
prompt taken from the routing skill's expected response.

[DOC-03]. `docs/install/copilot.md` MUST exist as a runtime-specific
guide separate from the Codex CLI guide, covering
`.github/copilot-instructions.md`, optional `.github/instructions/`
path-scoping, and Copilot CLI headless verification.

[DOC-04]. `docs/install/databricks-genie.md` MUST reflect the
agentskills.io-correct layout (`helix/SKILL.md` directly under the
skills path, no `helix-genie-bundle/skill/` wrapper) and drop the
"format still moving" hedge.

#### Test harness

[TEST-01]. The repo MUST contain `tests/install/` with one
subdirectory per runtime (`ddx/`, `claude-code/`, `codex-cli/`,
`copilot-cli/`, `genie/`).

[TEST-02]. Each terminal-based runtime (DDx, Claude Code, Codex CLI,
Copilot CLI) MUST provide a Dockerfile, an install script, a
verification script, and a `vhs` `.tape` file for screencast capture.

[TEST-03]. The Genie test scenario MUST provide the SDK install
script, the offline verification script, a manual browser verification
procedure, and a captured screencast of the manual verification.

[TEST-04]. Each `verify.sh` MUST run a static check (file layout,
frontmatter parses, no legacy `helix-*` directories) that requires no
LLM call.

[TEST-05]. Each `verify.sh` MUST also be capable of running a
functional check that invokes the runtime non-interactively and asserts
that the response names a known set of HELIX routing modes drawn from
`tests/install/shared/expected-modes.txt`. Functional checks SHOULD be
gated behind an environment variable to control token cost.

[TEST-06]. The repo MUST provide a top-level entry point (justfile
recipe or single script) that builds all images, runs all install +
verify steps, and captures all screencasts in one invocation.

### Acceptance Criteria

| Requirement | Scenario | Given | When | Then |
|---|---|---|---|---|
| ADAPT-01 | description string is current | repo at HEAD | `jq -r .description .claude-plugin/plugin.json` | output does not contain "supervisory autopilot" |
| ADAPT-02 | Claude Code marketplace flow works | a clean Claude Code env | `claude plugin marketplace add easel/helix && claude plugin install helix@helix --scope user -y` | plugin appears in `claude plugin list` |
| ADAPT-03 | Copilot instructions auto-discovered | a clean repo checkout | `gh copilot suggest "what HELIX modes exist?"` | response names align/frame/evolve/review modes |
| GENIE-01,02,03 | Genie bundle installs and verifies | a clean Databricks workspace + admin PAT | `python scripts/install-genie.py && python scripts/verify-genie.py` | verification reports success without browser interaction |
| DOC-01..04 | docs reflect verified reality | `docs/install/` contents | `grep -rn "git clone" docs/install/ \| grep -v "no-fork policy"` | zero matches in install procedure sections |
| TEST-01..06 | Docker harness passes | `tests/install/` | `just install-test` | every runtime scenario produces a captured screencast in its directory |

### Non-Functional Requirements

- **Performance**: full `just install-test` run including all Docker
  builds completes in under 30 minutes on developer hardware.
- **Cost**: functional LLM-based verification checks must be opt-in
  via `TEST_FUNCTIONAL=1` to avoid burning tokens on every CI run.
- **Reliability**: static checks (file presence, frontmatter parse)
  must not depend on network access beyond the initial Docker base
  pull and the install command itself.
- **Auditability**: every screencast must carry a timestamp and a
  recorded HELIX version so old recordings are visibly stale.

## User Stories

Single-feature scope without breakdown into separate stories. Beads
under FEAT-013 act as the implementation work items.

## Edge Cases and Error Handling

- **Stale DDx snapshot**: After tagging a new release, users running
  `ddx install helix --force` should refresh past the prior version.
  The test harness explicitly seeds a stale-version state and verifies
  that `--force` clears it.
- **Missing Databricks credentials**: `scripts/install-genie.py` MUST
  fail with a clear, single-line error referencing the required env
  vars (`DATABRICKS_HOST`, `DATABRICKS_TOKEN`) when either is unset.
- **Marketplace name collision**: If a user has previously added a
  different `helix` marketplace, the Claude Code install path should
  surface the conflict, not silently install from the older source.

## Success Metrics

| Metric | Target | Measurement |
|---|---|---|
| Verified runtime coverage | 5 of 5 runtimes | `just install-test` exit 0; screencast captured per runtime |
| Install-doc accuracy | 0 stale "git clone" recipes in install procedure sections | `grep` lint, see ADAPT-01 acceptance test |
| Genie manual e2e | One captured screencast against a real workspace per release | Reviewable artifact in `tests/install/genie/recordings/` |
| Stale-snapshot drift | DDx user-scoped install at `~/.ddx/plugins/helix/` reports the latest tagged version | Manual or scripted version inspection after `--force` |

## Constraints and Assumptions

- HELIX content stays runtime-neutral. Per-runtime adapter files and
  scripts are thin shims; they do not fork the methodology or the
  catalog (PRD R-4, install README no-fork policy).
- Genie Code's chat API is not public. End-to-end skill activation can
  only be verified through the workspace UI; the test harness accepts
  this constraint and combines headless install verification with
  manual browser-screencast verification.
- The cross-runtime `npx skills add` CLI is real but only installs to
  local agent paths. It is the recommended install path for Codex CLI
  (and a viable alternative for Claude Code in `--plugin-dir` mode) but
  not for Genie or Copilot.

## Dependencies

- **PRD R-4 and R-7**: feature operationalizes both requirements.
- **agentskills.io spec**: HELIX's skill must remain compliant.
- **`scripts/install-genie.py`** needs the Databricks Python SDK on the
  developer/CI machine.
- **DDx registry publishing** controls when a tagged HELIX release
  becomes visible to `ddx install helix`.

## Relationships

- **Supersedes**: nothing. Extends FEAT-004 (plugin packaging) which is
  partially superseded; FEAT-013 carries forward the surviving "runtime
  distribution packaging" scope of FEAT-004 and operationalizes it
  across five runtimes.
- **Informs**: [TD-013](../../02-design/technical-designs/TD-013-multi-runtime-install.md)
  technical design.
- **Referenced by**: `docs/install/*` runtime guides and
  `docs/resources/agents/*` mechanism notes.
