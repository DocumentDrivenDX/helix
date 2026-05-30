# HELIX on Databricks Genie Code

This guide installs HELIX as a Databricks Genie Code skill so Genie can
route requests to the HELIX methodology — alignment, framing, evolution,
design, review — over a project's governing artifacts.

## TL;DR

### From inside a Databricks notebook (recommended — no setup)

Paste this into a Python notebook cell. The kernel has implicit
workspace credentials; no PAT, env vars, or CLI required.

```python
%pip install --quiet databricks-sdk PyYAML

import urllib.request, runpy
urllib.request.urlretrieve(
    "https://github.com/DocumentDrivenDX/helix/releases/latest/download/genie-install",
    "/tmp/genie_install.py",
)
g = runpy.run_path("/tmp/genie_install.py")

g["install"]()                # user-scoped (current notebook user)
# g["install"](shared=True)   # workspace-wide (admin)
# g["install"](main=True)     # track main branch
```

The `install()` function runs in the notebook's Python kernel where
the Databricks SDK can use implicit notebook-runtime auth. Re-run any
time to refresh.

> **Don't use `%sh`** for the install. A `%sh` subprocess loses the
> notebook's kernel context — the SDK partially detects "looks like a
> notebook" (Spark Py4J connects) but then fails the IPython context
> lookup with `'NoneType' object has no attribute 'parent_header'`.
> Run the installer in a Python cell instead.

### From a dev box or CI

```bash
# One-time auth setup (whichever you prefer):
export DATABRICKS_HOST=https://<workspace>.azuredatabricks.net
export DATABRICKS_TOKEN=<personal access token>
#   ... OR add a section to ~/.databrickscfg and:
# export DATABRICKS_PROFILE=<section-name>

# Install
curl -fsSL https://github.com/DocumentDrivenDX/helix/releases/latest/download/genie-install -o /tmp/genie-install
chmod +x /tmp/genie-install
/tmp/genie-install                          # user-scoped
# /tmp/genie-install --shared               # workspace-wide
```

The Databricks CLI is **not** required — the installer talks directly
to the workspace REST API via the Databricks Python SDK.

## What you are installing

Genie Code adopts the [agentskills.io specification](https://agentskills.io/specification),
the open standard also used by Claude Code, OpenAI Codex CLI, Cursor,
VS Code/Copilot, and Gemini CLI. A skill is a directory:

```
helix/
  SKILL.md             # required: YAML frontmatter + Markdown body
  references/
    activities/        # HELIX artifact catalog under here
```

Required frontmatter:

```yaml
---
name: helix
description: Route HELIX methodology work to the right planning, alignment, design, review, execution, or release workflow. ...
---
```

The agentskills invariant: parent directory name (`helix`) must equal
the `name:` field. The installer enforces this.

## Workspace install paths

| Scope | Path | Who can install |
|---|---|---|
| Workspace-wide | `/Workspace/.assistant/skills/helix/SKILL.md` | workspace admin |
| User-scoped | `/Users/<your-email>/.assistant/skills/helix/SKILL.md` | the user themselves (own PAT enough) |

Skills are auto-discovered by directory scan. No registration command
needed. Start a new Agent-mode chat after changes for them to take
effect. User-scoped installs override workspace-wide ones for that
user, useful for testing pre-release content without affecting
teammates.

### ACLs on `--shared` installs

Workspace objects under `/Workspace/.assistant/skills/` inherit ACLs
from their parent. On tenants whose root `/directories/` only grants
`admins` (the default in security-tightened workspaces), an admin-run
`--shared` install creates the skill dir as admin-readable only —
non-admin users won't see HELIX even though it's "installed."

The installer detects `--shared` (or any non-`/Users/...` target) and
idempotently grants `users → CAN_READ` on both the skill dir
(`/Workspace/.assistant/skills/helix`) and its parent
(`/Workspace/.assistant/skills`). Genie lists the parent to discover
skills, so both grants matter. The installer logs the action and
falls back to a `databricks workspace update-permissions ...` command
suggestion if the grant call fails (e.g. SDK too old, or non-admin
runs `--shared` against a workspace that didn't actually need admin
perms there).

If other users still can't see HELIX after a `--shared` install,
verify:

```bash
# 1. Get the directory object IDs.
databricks workspace get-status /Workspace/.assistant/skills
databricks workspace get-status /Workspace/.assistant/skills/helix

# 2. Inspect ACLs — `users` group should appear with CAN_READ.
databricks workspace get-permissions directories <object_id>
```

The parent `/Workspace/.assistant` itself is left admin-only; it may
hold a workspace-level `.mcp_servers.json` containing MCP credentials.
Genie reads `/Workspace/.assistant/skills/helix/SKILL.md` by direct
path, not by traversing `.assistant` — so granting on the `skills`
subtree is sufficient.

## Installer flags

```text
genie-install                            # latest release, current user
genie-install --shared                   # latest release, workspace-wide
genie-install --main                     # main branch HEAD, current user
genie-install --main --shared            # main branch, workspace-wide
genie-install --version v0.5.0           # specific release tag
genie-install --bundle /path/to/helix    # skip download; install local bundle
genie-install --target /Workspace/...    # explicit workspace path
genie-install --repo <owner>/<repo>      # install from a fork
```

`--main`, `--version`, and `--bundle` are mutually exclusive (only one
source). `--shared` and `--target` are mutually exclusive (only one
destination).

The installer prefers a pre-built release bundle when one exists
(faster, no local build step). If no pre-built bundle is published for
the requested ref, it falls back to downloading the source archive and
running `scripts/build-genie-bundle.sh` locally — same result, slightly
slower.

## Auth options

The installer accepts credentials in this order (first match wins):

1. **Inside a Databricks notebook**: implicit. The notebook runtime
   supplies workspace identity automatically. Nothing to set.
2. **`DATABRICKS_HOST` + `DATABRICKS_TOKEN` env vars**: workspace URL
   plus a PAT.
3. **`DATABRICKS_PROFILE` env var**: names a section in
   `~/.databrickscfg`.
4. **Default profile in `~/.databrickscfg`**: if present, used as the
   final fallback.

The Databricks CLI is **not** required at any layer — the Databricks
Python SDK reads `~/.databrickscfg` and auto-detects notebook auth
directly.

Workspace admin role is required for `--shared` installs. User PAT (or
notebook identity with appropriate workspace permissions) is
sufficient for default user-scoped installs.

## Distributing HELIX to other users

There is no "marketplace" for Genie Code skills today. Distribution is
per-workspace, per-install:

- **Same workspace**: install once at the workspace-wide path with
  `--shared` (admin). Every user with Genie Code enabled in that
  workspace sees HELIX automatically.
- **Different workspace, same org**: that workspace's admin runs
  `genie-install --shared` against their own `DATABRICKS_HOST`.
- **Different organization**: they grab the installer with the same
  `curl` line, point it at their workspace, run as admin or user.
- **Per-user, opt-in**: anyone with their own PAT can run
  `genie-install` (no `--shared`) — installs to their own
  `/Users/<them>/.assistant/skills/helix/`. Doesn't affect anyone else.

## Update / uninstall

Update:

```bash
/tmp/genie-install                  # re-run; overwrites existing install
```

Uninstall:

```bash
databricks workspace delete --recursive /Workspace/.assistant/skills/helix
# or for user-scoped:
databricks workspace delete --recursive /Users/<you>/.assistant/skills/helix
```

## Verifying the install

The installer runs offline verification automatically (file presence,
frontmatter parse, activity-dir presence). For an additional
end-to-end check, open Genie Code in Agent mode and run:

**Step 1.** Confirm the skill loaded and routes:

```
List the HELIX workflow modes you can route to, and cite the SKILL.md
section that defines each one.
```

Expected: Genie names input, frame, align, evolve, design, backfill,
review, polish, check, build, run, commit, release, experiment,
worker, and cites the routing table and §-prefixed contract sections.

**Step 2.** Confirm the catalog index is reachable from SKILL.md:

```
Using HELIX, list the artifact types defined under activity 01-frame.
```

Expected: Genie returns the 16 artifact types under 01-frame
(compliance-requirements, concerns, feasibility-study, ... ,
validation-checklist) — these are inlined in SKILL.md §Catalog
Resolution and don't require filesystem traversal.

**Step 3.** Smoke-test a routing decision against a real project:

```
I have docs/helix/00-discover/product-vision.md and
docs/helix/01-frame/prd.md in this repo. Use HELIX to check whether
they are aligned. Do not write any files yet.
```

Expected: Genie selects align mode, returns an alignment-shaped report
with classifications (`ALIGNED`, `INCOMPLETE`, `DIVERGENT`,
`UNDERSPECIFIED`, `STALE_PLAN`, `BLOCKED`) — without modifying files.

If Genie doesn't pick HELIX automatically on a relevant prompt,
prefix with `@helix` to force activation.

## Integration test

For automated end-to-end verification across three scenarios (install-verify,
skill-list, bootstrap), see the Playwright-based integration test at
`tests/workflows/genie/`. The test drives headless Chromium against your
workspace, asserts on structural DOM signals of skill activation, and
captures a webm screencast as evidence:

- **Screencast**: `tests/workflows/genie/recordings/INT-GN.webm`
- **Events log**: `tests/workflows/genie/recordings/INT-GN-events.json`
- **Documentation**: `tests/workflows/genie/README.md`

Run the test locally after install to verify the full workflow:

```bash
export DATABRICKS_HOST=https://<workspace>.azuredatabricks.net
export DATABRICKS_WORKSPACE_URL=https://<workspace>.azuredatabricks.net/?o=<org-id>
export DBAUTH_COOKIE_PATH=/path/to/dbauth.txt
bash tests/workflows/genie/run-scenarios.sh
```

## Known limitations

- **Bead `helix-96f7dd34` (open)**: Genie's filesystem tool does not
  auto-resolve paths relative to the skill bundle for files outside
  the inline §Catalog Resolution table. Queries that need to read a
  template's body (not just list types) may fail to find the file at
  `references/activities/.../template.md`. The 0.5.0+ SKILL.md
  mitigates the most common queries via the inline index, but heavier
  reads are blocked until the bead resolves.
- **User-level custom instructions can shadow HELIX behavior.** If
  Genie reasons about a `datahelix/`-like local path, your workspace
  has a user custom instruction biasing path lookups. Clear or scope
  those instructions if you see unexpected workspace-filesystem
  search.
- **Build / Run modes on Genie**: Genie's shell-execution surface is
  more constrained than Claude Code or Codex CLI. HELIX `build` and
  `run` modes that depend on running a project gate typically need
  to be paired with a Databricks job, notebook, or CI pipeline rather
  than executed inline.

## Refresh: keeping your HELIX tree current

Refresh is a first-class HELIX mode that brings every artifact instance
under a project HELIX tree up to date with the current canonical
templates and prompts. Databricks Genie Code does not have a sub-agent
dispatch mechanism, so Refresh runs sequentially: each activity directory
is processed in order (00-discover, then 01-frame, …, through 06-iterate).
For large artifact trees where parallel processing would be beneficial,
consider using DDx or another execution runtime alongside Genie for
faster turnaround.

## Caveats vs. other runtimes

- **File-write surface.** Claude Code and Codex run with the user's
  local filesystem permissions. Genie writes through the Databricks
  workspace; write access to a Git-backed repo folder may go through
  a Databricks Repos integration rather than direct filesystem writes.
  Confirm commit-attribution behavior with your workspace admin before
  relying on audit trails.
- **Multi-user state.** Genie is a shared workspace agent: multiple
  users may invoke HELIX against the same artifact tree. HELIX itself
  is stateless between invocations, so this is safe, but concurrent
  edits flow through the workspace's git/Repos surface, not through
  HELIX.
- **DDx is not present.** The DDx reference runtime — beads queue,
  execution loop, evidence capture — is not part of this install.
  HELIX-on-Genie is HELIX-as-methodology only. Projects that want the
  full HELIX-plus-runtime experience can use DDx in a connected dev
  environment and have Genie operate over the same artifact tree.

## Manual install (no installer)

If you can't run the `genie-install` shebang (e.g. no `uv` on the
machine), the underlying steps are:

```bash
git clone https://github.com/DocumentDrivenDX/helix /tmp/helix
cd /tmp/helix
bash scripts/build-genie-bundle.sh                  # → dist/genie-bundle/helix/
python scripts/install-genie.py --target /Users/<you>/.assistant/skills/helix
python scripts/verify-genie.py --target /Users/<you>/.assistant/skills/helix
```

These are the steps `genie-install` automates. Same result.

## See also

- [`scripts/genie-install`](../../scripts/genie-install) — single-file installer
- [`scripts/build-genie-bundle.sh`](../../scripts/build-genie-bundle.sh) — bundle assembler
- [`scripts/install-genie.py`](../../scripts/install-genie.py) — direct uploader
- [`scripts/verify-genie.py`](../../scripts/verify-genie.py) — offline verifier
- [docs/resources/agents/databricks-genie-code-skills.md](../resources/agents/databricks-genie-code-skills.md)
  — Genie Code mechanism research notes
- [Genie Code skill authoring documentation](https://docs.databricks.com/aws/en/genie-code/skills)
- [Install README index](README.md)
- Companion install guides: [Claude Code](claude-code.md),
  [OpenAI Codex CLI](codex.md), [GitHub Copilot](copilot.md)
