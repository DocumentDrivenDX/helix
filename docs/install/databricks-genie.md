# HELIX on Databricks Genie Code: deploy runbook

This runbook deploys HELIX as a Databricks Genie Code skill. What HELIX
is, how the skill finds its catalog, how to invoke it, and the Genie
host limits are in the [install guide](README.md#databricks-genie-code);
this page holds only the deploy procedure.

## TL;DR

### From inside a Databricks notebook (recommended, no setup)

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

> Do not use `%sh` for the install. A `%sh` subprocess loses the
> notebook's kernel context: the SDK partially detects "looks like a
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

The Databricks CLI is not required. The installer talks directly to the
workspace REST API via the Databricks Python SDK. The `just genie-build`,
`just genie-install`, and `just genie-verify` recipes wrap the underlying
scripts for a source checkout.

## Bundle layout

The installer uploads a skill directory in the agentskills.io shape:

```
helix/
  SKILL.md             # required: YAML frontmatter + Markdown body
  references/          # generated catalog floor (graph.yml, modes/, activities/, ...)
```

The agentskills invariant, parent directory name (`helix`) equal to the
`name:` frontmatter field, is enforced by the installer.

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
from their parent. Where the root grants only `admins` (the default in
security-tightened workspaces), an admin-run `--shared` install would be
admin-readable only, so the installer idempotently grants
`users → CAN_READ` on both the skill dir and its parent
`/Workspace/.assistant/skills` (Genie lists the parent to discover
skills). If the grant call fails (SDK too old, or a non-admin ran
`--shared` where no admin perms were needed) it logs a
`databricks workspace update-permissions ...` suggestion instead. If
other users still cannot see HELIX, verify:

```bash
# 1. Get the directory object IDs.
databricks workspace get-status /Workspace/.assistant/skills
databricks workspace get-status /Workspace/.assistant/skills/helix

# 2. Inspect ACLs: the `users` group should appear with CAN_READ.
databricks workspace get-permissions directories <object_id>
```

The parent `/Workspace/.assistant` stays admin-only (it may hold a
workspace-level `.mcp_servers.json` with MCP credentials); Genie reads
the skill by direct path, so the `skills` subtree grant is sufficient.

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

The installer prefers a pre-built release bundle and falls back to
downloading the source archive and running `scripts/build-genie-bundle.sh`
locally when none is published for the requested ref.

## Auth options

The installer accepts credentials in this order (first match wins):

1. Inside a Databricks notebook: implicit. The notebook runtime
   supplies workspace identity automatically. Nothing to set.
2. `DATABRICKS_HOST` + `DATABRICKS_TOKEN` env vars: workspace URL plus
   a PAT.
3. `DATABRICKS_PROFILE` env var: names a section in `~/.databrickscfg`.
4. Default profile in `~/.databrickscfg`: if present, used as the final
   fallback.

Workspace admin role is required for `--shared` installs. A user PAT (or
notebook identity with appropriate workspace permissions) is sufficient
for default user-scoped installs.

## Distributing HELIX to other users

There is no marketplace for Genie Code skills today. Distribution is
per-workspace, per-install: an admin runs `genie-install --shared` once
per workspace (every Genie Code user there sees HELIX), other workspaces
or organizations run the same installer against their own
`DATABRICKS_HOST`, and any user with a PAT can run `genie-install`
without `--shared` for a private, opt-in install that affects nobody else.

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
frontmatter parse, generated-reference floor presence). For an
end-to-end check, open Genie Code in Agent mode and run:

**Step 1.** "List the HELIX workflow modes you can route to, and cite
the SKILL.md section that defines each one." Expected: Genie names the
modes (input, frame, align, evolve, design, backfill, review, polish,
check, build, run, commit, release, experiment, worker) and cites the
routing table and the mode contracts.

**Step 2.** "Using HELIX, list the artifact types defined under activity
01-frame." Expected: the 01-frame types (compliance-requirements through
validation-checklist), which are inlined in the skill's Catalog
Resolution table and need no filesystem traversal.

**Step 3.** Smoke-test a routing decision against a real project:

```
I have docs/helix/00-discover/product-vision.md and
docs/helix/01-frame/prd.md in this repo. Use HELIX to check whether
they are aligned. Do not write any files yet.
```

Expected: Genie selects align mode and returns an alignment-shaped
report with classifications (`ALIGNED`, `INCOMPLETE`, `DIVERGENT`,
`UNDERSPECIFIED`, `STALE_PLAN`, `BLOCKED`) without modifying files.

If Genie does not pick HELIX automatically on a relevant prompt, prefix
with `@helix` to force activation.

## Integration test

The Playwright-based integration test at `tests/workflows/genie/` (see
its `README.md`) drives headless Chromium against your workspace across
three scenarios (install-verify, skill-list, bootstrap), asserts on DOM
signals of skill activation, and records `recordings/INT-GN.webm` plus an
events log as evidence. Run it after install:

```bash
export DATABRICKS_HOST=https://<workspace>.azuredatabricks.net
export DATABRICKS_WORKSPACE_URL=https://<workspace>.azuredatabricks.net/?o=<org-id>
export DBAUTH_COOKIE_PATH=/path/to/dbauth.txt
bash tests/workflows/genie/run-scenarios.sh
```

## Known limitations

- Bead `helix-96f7dd34` (open): Genie's filesystem tool does not
  auto-resolve bundle-relative paths outside the inline Catalog
  Resolution table, so reads of a template body at
  `references/activities/.../template.md` may fail until the bead
  resolves; the inline index covers the common queries.
- User-level custom instructions can shadow HELIX behavior. If Genie
  reasons about a `datahelix/`-like local path, your workspace has a
  user custom instruction biasing path lookups. Clear or scope those
  instructions if you see unexpected workspace-filesystem search.
- Multi-user state. Genie is a shared workspace agent: multiple users
  may invoke HELIX against the same artifact tree. HELIX is stateless
  between invocations, so this is safe, but concurrent edits flow
  through the workspace's git/Repos surface, not through HELIX. Confirm
  commit-attribution behavior with your workspace admin before relying
  on audit trails.

## Manual install (no installer)

If you cannot run the `genie-install` shebang (for example no `uv` on
the machine), the underlying steps are:

```bash
git clone https://github.com/DocumentDrivenDX/helix /tmp/helix
cd /tmp/helix
bash scripts/build-genie-bundle.sh                  # → dist/genie-bundle/helix/
python scripts/install-genie.py --target /Users/<you>/.assistant/skills/helix
python scripts/verify-genie.py --target /Users/<you>/.assistant/skills/helix
```

These are the steps `genie-install` automates. Same result.

## See also

- [`scripts/genie-install`](../../scripts/genie-install): single-file installer
- [`scripts/build-genie-bundle.sh`](../../scripts/build-genie-bundle.sh): bundle assembler
- [`scripts/install-genie.py`](../../scripts/install-genie.py): direct uploader
- [`scripts/verify-genie.py`](../../scripts/verify-genie.py): offline verifier
- [docs/resources/agents/databricks-genie-code-skills.md](../resources/agents/databricks-genie-code-skills.md):
  Genie Code mechanism research notes
- [Genie Code skill authoring documentation](https://docs.databricks.com/aws/en/genie-code/skills)
- [Install guide](README.md)
