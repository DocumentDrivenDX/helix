# HELIX on Databricks Genie Code

This guide installs HELIX as a Databricks Genie Code skill so that
Genie can route requests to the HELIX methodology — alignment,
framing, evolution, design, review — over a project's governing
artifacts.

HELIX ships an automated build + upload + verify pipeline:

```bash
bash scripts/build-genie-bundle.sh           # assemble dist/genie-bundle/helix/
python scripts/install-genie.py              # upload to workspace
python scripts/verify-genie.py               # confirm install (offline checks)
```

The skill itself is content + frontmatter (no executable code). The
runtime — Genie Code — does the file I/O.

> **Genie Code** is Databricks' agentic coding assistant inside the
> workspace. GA as of 2026-03-11. It is distinct from "Genie" / "Genie
> Spaces" (BI Q&A over data). HELIX targets Genie Code.

## Skill format

Genie Code adopts the [agentskills.io specification](https://agentskills.io/specification),
the open standard also used by Claude Code, OpenAI Codex CLI, Cursor,
VS Code/Copilot, and Gemini CLI. A skill is a directory:

```
helix/
  SKILL.md             # required: YAML frontmatter + Markdown body
  references/          # optional: progressive-disclosure content
    activities/        # HELIX artifact catalog under here
  scripts/             # optional
  assets/              # optional
```

The agentskills invariant: parent directory name (`helix`) must equal
the `name:` field in SKILL.md frontmatter.

Required frontmatter:

```yaml
---
name: helix
description: Route HELIX methodology work to the right planning, alignment, design, review, execution, or release workflow. ...
---
```

`description` is 1–1024 chars. See
[docs/resources/agents/agentskills-spec.md](../resources/agents/agentskills-spec.md)
for the full schema (optional `license`, `compatibility`, `metadata`,
`allowed-tools`).

## Workspace install paths

| Scope | Path |
|---|---|
| Workspace-wide (admin) | `/Workspace/.assistant/skills/helix/SKILL.md` |
| User-scoped | `/Users/<username>/.assistant/skills/helix/SKILL.md` |

Skills are auto-discovered by directory scan. No registration command
is needed. Start a new Agent-mode chat after changes for them to take
effect.

## Install

### 1. Build the bundle locally

```bash
cd <helix-repo-root>
bash scripts/build-genie-bundle.sh
# → dist/genie-bundle/helix/SKILL.md
# → dist/genie-bundle/helix/references/activities/00-discover/...
# → ...
```

The script validates SKILL.md frontmatter (`name: helix` invariant)
and assembles the directory. `dist/` is gitignored.

### 2. Configure Databricks credentials

```bash
export DATABRICKS_HOST=https://<your-workspace>.databricks.com
export DATABRICKS_TOKEN=<PAT or OAuth token>
# OR
export DATABRICKS_PROFILE=<section name in ~/.databrickscfg>
```

Required role: workspace admin for `/Workspace/.assistant/skills/...`
installs; the user's own PAT is sufficient for user-scoped installs.

### 3. Dry-run against a personal-scope workspace path

Before targeting the workspace-wide path, dry-run against your own
`.assistant/skills/` directory:

```bash
python scripts/install-genie.py \
    --bundle dist/genie-bundle/helix \
    --target /Users/$(whoami)/.assistant/skills/helix-test
python scripts/verify-genie.py \
    --target /Users/$(whoami)/.assistant/skills/helix-test
```

Both should exit 0. Inspect the uploaded tree with the Databricks
workspace browser or `databricks workspace list /Users/.../helix-test`.

### 4. Install to workspace path

After dry-run passes, target the workspace-wide path:

```bash
python scripts/install-genie.py \
    --bundle dist/genie-bundle/helix \
    --target /Workspace/.assistant/skills/helix
python scripts/verify-genie.py \
    --target /Workspace/.assistant/skills/helix
```

The catalog lives in workspace storage; multiple users share one copy.

## Verify install (offline + manual)

### Offline static verification

```bash
python scripts/verify-genie.py --target /Workspace/.assistant/skills/helix
```

Asserts:
- Target directory exists and contains `SKILL.md`
- Frontmatter parses as valid YAML
- `name == "helix"`
- `description` is 1–1024 chars
- All seven `references/activities/<NN>-<activity>/` dirs are present

No chat API calls. Exit 0 on success; exit 5 on any failure.

### Manual browser verification

Genie Code has no public chat API. End-to-end skill activation must
be verified through the workspace UI. Open Genie Code and run three
prompts in a new Agent-mode chat:

**Step 1.** List modes:

```
List the HELIX workflow modes you can route to, and cite the SKILL.md
section that defines each one.
```

Expected: Genie names input, frame, align, evolve, design, backfill,
review, polish, check, build, run, commit, release, experiment,
worker. Genie cites the routing table and per-mode contracts in
`SKILL.md`.

**Step 2.** Catalog reachable:

```
Using HELIX, list the artifact types defined under activity 01-frame,
and show the path of each artifact-type directory in the catalog.
```

Expected: Genie returns the artifact-type directories under
`references/activities/01-frame/artifacts/` with paths anchored at
the skill root. If Genie returns generic descriptions without paths,
the catalog references are unreachable.

**Step 3.** Smoke-test routing:

```
I have docs/helix/00-discover/product-vision.md and
docs/helix/01-frame/prd.md in this repo. Use HELIX to check whether
they are aligned. Do not write any files yet.
```

Expected: Genie selects align mode, reads both artifacts, and returns
an alignment-shaped report (gaps classified as `ALIGNED`,
`INCOMPLETE`, `DIVERGENT`, `UNDERSPECIFIED`, `STALE_PLAN`, or
`BLOCKED`) without modifying files.

Capture a screencast of all three exchanges for release evidence.

## Invocation

Genie routes by natural language. HELIX is designed for that
interface; users describe what they want and the routing skill picks
the matching workflow.

If Genie does not select the HELIX skill automatically, mention it
explicitly:

```
@helix Use HELIX to align the artifacts under docs/helix/ for this repo.
```

The `@helix` mention forces activation. Healthy routing should not
need it.

Example prompts:

- "@helix Align the artifacts under `docs/helix/` for this repo."
- "Run a HELIX framing pass and produce a PRD for the new ingestion feature."
- "Evolve the HELIX artifacts to thread the new compliance requirement
  through vision, PRD, feature specs, and any affected designs."
- "Do a HELIX fresh-eyes review of the changes on this branch."

## Caveats vs. other runtimes

- **File-write surface.** Claude Code and Codex run with the user's
  local filesystem permissions. Genie writes through the Databricks
  workspace; write access to a Git-backed repo folder may go through
  a Databricks Repos integration rather than direct filesystem writes.
  HELIX alignment and evolve passes that propose artifact edits may
  need to be applied via the Repos commit flow rather than direct
  file write. Confirm commit-attribution behavior with your workspace
  administrator before relying on audit trails.
- **Execution surface.** Claude Code and Codex can run shell commands
  inline. Genie's shell-execution surface inside the workspace is
  more constrained. HELIX `build` and `run` modes that depend on
  running a project gate typically need to be paired with a Databricks
  job, notebook, or CI pipeline triggered outside the HELIX skill.
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
- **No CLI verbs.** This install does not introduce a `helix` CLI.
  All invocation is natural language through Genie, exactly as with
  the Claude Code and Codex installs.

## Update / uninstall

Update:

```bash
bash scripts/build-genie-bundle.sh           # rebuild bundle
python scripts/install-genie.py              # re-upload (overwrite=True)
python scripts/verify-genie.py               # confirm
```

Uninstall by deleting the workspace path:

```bash
databricks workspace delete --recursive /Workspace/.assistant/skills/helix
```

## See also

- [`scripts/build-genie-bundle.sh`](../../scripts/build-genie-bundle.sh) — bundle assembler
- [`scripts/install-genie.py`](../../scripts/install-genie.py) — uploader
- [`scripts/verify-genie.py`](../../scripts/verify-genie.py) — offline verifier
- [docs/resources/agents/databricks-genie-code-skills.md](../resources/agents/databricks-genie-code-skills.md)
  — Genie Code mechanism research notes
- [Genie Code skill authoring documentation](https://docs.databricks.com/aws/en/genie-code/skills)
- [Install README index](README.md)
- Companion install guides: [Claude Code](claude-code.md),
  [OpenAI Codex CLI](codex.md), [GitHub Copilot](copilot.md)
