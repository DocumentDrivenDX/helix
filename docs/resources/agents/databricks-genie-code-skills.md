---
ddx:
  id: resource.agents.databricks-genie-code-skills
---

# Databricks Genie Code Skill Mechanism

## Source

- Genie Code skills: https://docs.databricks.com/aws/en/genie-code/skills
- Agent skills (general): https://docs.databricks.com/aws/en/agent-skills/
- Genie Code overview: https://docs.databricks.com/aws/en/genie-code/
- Databricks agent skills repo: https://github.com/databricks/databricks-agent-skills
- Skills CLI: https://github.com/vercel-labs/skills
- Spec: https://agentskills.io/specification
- Spec repo: https://github.com/agentskills/agentskills
- Genie Spaces Conversation API (distinct product): https://docs.databricks.com/aws/en/genie/conversation-api
- Workspace CLI: https://docs.databricks.com/aws/en/dev-tools/cli/reference/workspace-commands
- Genie Code launch blog: https://www.databricks.com/blog/introducing-genie-code
- ai-dev-kit: https://github.com/databricks-solutions/ai-dev-kit
- Accessed: 2026-05-15

## Summary

**Genie Code** is Databricks' agentic coding assistant inside the
workspace. GA as of 2026-03-11; documentation last updated 2026-05-12.
It is **distinct** from "Genie" (BI end-user data assistant) and "Genie
Spaces" (curated data domains). HELIX targets Genie Code.

Genie Code adopts the **agentskills.io specification**: skills are
directories containing a `SKILL.md` with YAML frontmatter, placed at a
known workspace filesystem path, auto-discovered on directory scan.

There is **no public REST or SDK API for Genie Code chat**. Skill
installation can be automated end-to-end via Databricks CLI/SDK; skill
*invocation and end-to-end verification* requires the workspace UI.

## Product identity

| Product | Status | What it does | API surface |
|---|---|---|---|
| Genie (BI) | GA | NL → SQL for business users | Conversation API exists for the Spaces variant |
| Genie Spaces | GA | Curated data domains, NL Q&A | `/api/2.0/genie/spaces/...` |
| **Genie Code** | **GA (2026-03-11)** | **Agentic coding assistant** | **No public chat API** |

HELIX targets Genie Code only.

## Skill format

agentskills.io spec compliant. See
[agentskills-spec.md](agentskills-spec.md) for the full schema.

```
helix/
  SKILL.md             # required: name + description frontmatter, Markdown body
  references/          # optional: heavier content (the artifact catalog)
  scripts/             # optional
  assets/              # optional
```

Parent directory name MUST match `name:` frontmatter exactly.

Required frontmatter:
- `name` (1–64 chars, lowercase a-z0-9-)
- `description` (1–1024 chars)

Optional: `license`, `compatibility`, `metadata`, `allowed-tools`.

## Workspace install paths

| Scope | Path |
|---|---|
| Workspace-wide (admin) | `/Workspace/.assistant/skills/<name>/SKILL.md` |
| User-scoped | `/Users/<username>/.assistant/skills/<name>/SKILL.md` |

Auto-discovered by directory scan. No registration command needed. Start
a new Agent-mode chat for changes to take effect. Users can `@<name>`
to force activation.

## Install procedures

### A. Manual via UI

Genie Code panel → Settings → "Open skills folder" → create
`<skill>/SKILL.md` and any supporting files via the workspace file
browser.

### B. Vercel Labs Skills CLI (local-agent only, NOT for workspace)

```bash
npx skills add owner/repo --list
npx skills add owner/repo --skill helix
npx skills add owner/repo -a claude-code
```

The CLI writes to local agent paths (`.agents/skills/`,
`.claude/skills/`, `~/.codex/skills/`). It does NOT write to
`/Workspace/.assistant/skills/`. Use this CLI for local-agent installs,
not for Genie Code workspace installs.

### C. Databricks CLI / SDK (canonical for workspace installs)

```bash
# Create the target directory
databricks workspace mkdirs /Workspace/.assistant/skills/helix

# Upload SKILL.md
databricks workspace import \
  --format AUTO \
  --language MARKDOWN \
  --file ./helix/SKILL.md \
  /Workspace/.assistant/skills/helix/SKILL.md

# For arbitrary files (catalog content), use the Python SDK which handles
# binary content cleanly:
python -c "
from databricks.sdk import WorkspaceClient
w = WorkspaceClient()
with open('./helix/references/catalog.md', 'rb') as f:
    w.workspace.upload(
        path='/Workspace/.assistant/skills/helix/references/catalog.md',
        content=f,
        overwrite=True,
    )
"
```

Note: `databricks workspace import-dir` historically filtered to
`.py`/`.scala`/`.sql`/`.r` extensions. For Markdown trees, use the
Python SDK `w.workspace.upload()` in a loop, or use `import` per file
with `--format AUTO`.

Verify:

```bash
databricks workspace list /Workspace/.assistant/skills/helix
databricks workspace export /Workspace/.assistant/skills/helix/SKILL.md
```

## Auth

Minimum: workspace **PAT** or OAuth token + **workspace-admin** role
for installing under `/Workspace/.assistant/skills/`. User-scoped
install only needs the user's own PAT.

```bash
databricks configure                  # interactive
# or
export DATABRICKS_HOST=https://...
export DATABRICKS_TOKEN=dapi...
```

## Headless / end-to-end testing limits

**Hard constraint: no public Genie Code chat API.** Every documented
Databricks API for "chat with an agent" targets Genie Spaces, not
Genie Code. The Genie Spaces Conversation API
(`/api/2.0/genie/spaces/{space_id}/start-conversation`,
`.../create-message`, Python SDK `w.genie.start_conversation_and_wait()`)
will NOT exercise skills under `/Workspace/.assistant/skills/`.

What CAN be tested headlessly:

1. **Install verification**: confirm files exist at the right paths via
   `databricks workspace list` and `databricks workspace export`, then
   YAML-parse the frontmatter locally.
2. **Frontmatter validity**: `npx skills-ref validate ./helix` (offline)
3. **File integrity**: SHA-compare uploaded files against source.

What CANNOT be tested headlessly today:

- Genie Code's actual decision to route a prompt to the skill
- Skill body interpretation
- Tool execution within a skill

Browser-based end-to-end test is the only documented path:

1. Open Genie Code in workspace browser
2. Start a new Agent-mode chat
3. Run the verification prompts from `docs/install/databricks-genie.md`
4. Capture results (screencast)

Playwright against the workspace UI is technically feasible but
undocumented and likely fragile. The `ai-dev-kit` repo at
`databricks-solutions/ai-dev-kit` provides patterns for bridging
external coding agents to Databricks but does NOT expose Genie Code
chat as an automatable endpoint.

## HELIX implications

- Adapter file in repo: NONE in-tree — Genie expects content at a
  workspace path, not a repo path. The "adapter" is the upload script
  that places HELIX content into `/Workspace/.assistant/skills/helix/`.
- Required restructuring: HELIX's catalog under `workflows/activities/`
  needs to be uploaded into `helix/references/activities/` (or similar
  subdirectory) inside the Genie skill bundle — Genie expects the skill
  to be self-contained, not to reach outside its directory.
- Test plan (see `tests/install/genie/`):
  1. Build bundle from source: copy `skills/helix/SKILL.md` and
     `workflows/activities/` into a `dist/genie-bundle/helix/` tree
  2. Upload via Databricks SDK Python script
  3. Verify file presence via Databricks CLI
  4. Manual browser verification via workspace UI with screencast
     capture

## Caveats

- "Bundle wrapper" advice (placing `SKILL.md` under a `skill/`
  subdirectory) is incorrect per current spec; the parent dir must
  match `name:` exactly. HELIX's existing
  `docs/install/databricks-genie.md` recommends a
  `helix-genie-bundle/skill/SKILL.md` layout that needs to be revised
  to `helix/SKILL.md` directly.
- Skill format maturity caveat in the install doc is now stale; the
  agentskills.io spec is GA and Databricks has shipped Genie Code as GA.
- The `databricks-agent-skills` repo at github.com/databricks/databricks-agent-skills
  provides Databricks-published example skills.
- Skills are heavier-weight than custom-instructions; a Genie Code
  skill body is referenced when the description matches user intent,
  not unconditionally injected like Copilot custom instructions.
