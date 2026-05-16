# HELIX install test harness

Per-runtime install scenarios verifying that HELIX installs cleanly on
each supported runtime and that the routing skill is discoverable.

Each scenario consists of:

- `Dockerfile` — minimal base image with the runtime CLI installed
- `install.sh` — runs the canonical install command for that runtime
- `verify.sh` — runs the shared layout invariants + optional functional check
- `record.tape` — vhs script for terminal screencast capture (`.gif` output)

Genie Code is the exception: it has no public chat API, so its scenario
provides offline upload + verification scripts plus a manual browser
procedure for end-to-end screencast capture.

## Run the full matrix

```bash
just install-test
# or
bash tests/install/run-all.sh
```

The runner builds each image, runs install + verify, and (optionally)
captures screencasts via `vhs`. Required env vars (per
`.env.example`):

| Var | Required by | Notes |
|---|---|---|
| `ANTHROPIC_API_KEY` | claude-code | needed when `TEST_FUNCTIONAL=1` |
| `OPENAI_API_KEY` | codex-cli | needed when `TEST_FUNCTIONAL=1` |
| `GH_TOKEN` | copilot-cli | must have Copilot license attached |
| `DATABRICKS_HOST` | genie | workspace URL |
| `DATABRICKS_TOKEN` | genie | PAT or OAuth |
| `TEST_FUNCTIONAL` | all (gated) | set to `1` to enable LLM-based checks |
| `TEST_GENIE` | genie | set to `1` to require Genie scenario to run |

DDx requires no credentials and is the smoke-test default.

## What each check asserts

**Static (free, deterministic):**
- Skill `SKILL.md` exists at the expected runtime location
- Frontmatter parses as valid YAML
- `name:` matches parent directory name (agentskills.io invariant)
- No legacy `helix-*` skill directories (pre-collapse cruft)
- No `.git` directory inside the installed skill dir (not a working tree)

**Functional (gated by `TEST_FUNCTIONAL=1`):**
- Runtime non-interactive prompt asking for HELIX modes
- Response contains a known subset of mode names from
  `tests/install/shared/expected-modes.txt`

## Per-runtime scenarios

| Scenario | Auth | Headless? |
|---|---|---|
| `ddx/` | none | yes |
| `claude-code/` | ANTHROPIC_API_KEY | yes (claude -p) |
| `codex-cli/` | OPENAI_API_KEY | yes (codex exec --ephemeral) |
| `copilot-cli/` | GH_TOKEN + Copilot license | yes (gh copilot suggest) |
| `genie/` | DATABRICKS_HOST + DATABRICKS_TOKEN | partial (install yes, chat no) |

## Screencast capture

Terminal scenarios use [vhs](https://github.com/charmbracelet/vhs)
which reads `.tape` files and produces `.gif` (or `.mp4`) recordings.

```bash
vhs tests/install/<runtime>/record.tape
# → tests/install/<runtime>/recording.gif
```

Genie's manual browser verification is captured per the procedure in
`tests/install/genie/test-procedure.md`; recordings go in
`tests/install/genie/recordings/`.

## CI integration

Static checks should run on every PR. Functional checks should be
gated by `TEST_FUNCTIONAL=1` and run on release tags only to avoid
burning tokens on every commit.

## See also

- [FEAT-013](../../docs/helix/01-frame/features/FEAT-013-runtime-install-coverage.md)
- [TD-013](../../docs/helix/02-design/technical-designs/TD-013-multi-runtime-install.md)
- [Install index](../../docs/install/README.md)
