# Databricks Genie Code — manual test procedure

Genie Code has no public chat API. End-to-end skill activation can only
be verified through the workspace UI. This procedure pairs scripted
install/verify (headless) with a manual browser interaction (captured
as a screencast).

## Prerequisites

- Databricks workspace with Genie Code enabled
- Workspace admin role (for `/Workspace/.assistant/skills/` installs)
  OR user PAT (for `/Users/<you>/.assistant/skills/` installs)
- `DATABRICKS_HOST` and `DATABRICKS_TOKEN` env vars set, OR
  `DATABRICKS_PROFILE` pointing at a `~/.databrickscfg` section
- Local checkout of the HELIX repo
- `uv` installed (the Genie scripts use PEP 723 inline deps)
- Browser + screen-capture tool (OS screen recorder, ffmpeg, or Playwright)

## Step 1 — build the bundle

```bash
cd <helix-repo-root>
bash scripts/build-genie-bundle.sh
# → dist/genie-bundle/helix/SKILL.md
# → dist/genie-bundle/helix/references/activities/00-discover/...
# → ...
```

Confirm the bundle has the agentskills-compliant layout (`helix/SKILL.md`,
parent dir name equals `name:` in frontmatter).

## Step 2 — dry-run against a personal workspace path

Test the upload pipeline against your own user-scoped path before
targeting the workspace-wide path:

```bash
python tests/install/genie/install.py \
    --target /Users/$(whoami)/.assistant/skills/helix-test
python tests/install/genie/verify.py \
    --target /Users/$(whoami)/.assistant/skills/helix-test
```

Both should exit 0. If not, fix before proceeding.

Optional cleanup:

```bash
databricks workspace delete --recursive /Users/$(whoami)/.assistant/skills/helix-test
```

## Step 3 — install to workspace path

```bash
python tests/install/genie/install.py
# default target: /Workspace/.assistant/skills/helix
python tests/install/genie/verify.py
```

Both exit 0 on success.

## Step 4 — manual browser verification with screencast

**Start screen capture before opening Genie Code.** Capture should
include the install command outputs, the verify pass, and the three
Genie chat exchanges below. Save the recording to
`tests/install/genie/recordings/<YYYY-MM-DD>-verify.{mp4,gif}`.

Open Genie Code in the workspace browser and start a new Agent-mode
chat. Run each prompt in sequence.

### Prompt 1 — list modes

```
List the HELIX workflow modes you can route to, and cite the SKILL.md
section that defines each one.
```

**Expected response:** names input, frame, align, evolve, design,
backfill, review, polish, check, build, run, commit, release,
experiment, worker (or a faithful subset). References the routing
table or per-mode workflow contracts in `SKILL.md`.

**Pass criteria:** at least 5 of the expected modes named. Genie cites
`SKILL.md` (not generic external knowledge).

### Prompt 2 — catalog reachable

```
Using HELIX, list the artifact types defined under activity 01-frame,
and show the path of each artifact-type directory in the catalog.
```

**Expected response:** lists artifact-type directories under
`references/activities/01-frame/artifacts/` (e.g. `prd`,
`feature-specification`, `user-stories`, ...). Paths are anchored at
the skill root, not invented.

**Pass criteria:** at least 3 real artifact-type directory names with
paths referencing `references/activities/01-frame/`.

### Prompt 3 — smoke routing decision

```
I have docs/helix/00-discover/product-vision.md and
docs/helix/01-frame/prd.md in this repo. Use HELIX to check whether
they are aligned. Do not write any files yet.
```

**Expected response:** Genie selects align mode, reads both artifacts,
and returns an alignment-shaped report with gaps classified as
`ALIGNED`, `INCOMPLETE`, `DIVERGENT`, `UNDERSPECIFIED`, `STALE_PLAN`,
or `BLOCKED`. No file writes.

**Pass criteria:** response uses at least 2 of the classification
labels and does not modify files.

## Step 5 — capture metadata

After the three prompts succeed and the screencast is saved, write a
metadata sidecar at
`tests/install/genie/recordings/<YYYY-MM-DD>-verify.json`:

```json
{
  "date": "YYYY-MM-DD",
  "helix_version": "0.3.4",
  "workspace_host": "<masked>",
  "target_path": "/Workspace/.assistant/skills/helix",
  "operator": "<your-handle>",
  "prompt_1_pass": true,
  "prompt_2_pass": true,
  "prompt_3_pass": true,
  "notes": "..."
}
```

This sidecar gives future reviewers context without having to scrub
the video.

## Failure modes and remediation

| Symptom | Likely cause | Remediation |
|---|---|---|
| `install.py` exits 2 on missing env | DATABRICKS_HOST/TOKEN unset | export them or use DATABRICKS_PROFILE |
| `install.py` exits 4 on upload error | workspace path permissions | confirm admin role or use `/Users/<you>/.assistant/skills/...` |
| `verify.py` exits 5 with "frontmatter missing name" | bundle layout wrong | re-run `bash scripts/build-genie-bundle.sh`; ensure no `helix/skill/SKILL.md` wrapper |
| Genie does not surface HELIX in step 4 prompt 1 | skill not discovered | check `databricks workspace list /Workspace/.assistant/skills/helix`; start a fresh Agent-mode chat |
| Genie returns generic answer without citing SKILL.md | description not matching | re-check SKILL.md frontmatter `description` field has the routing-skill phrasing |

## See also

- [scripts/install-genie.py](../../../scripts/install-genie.py)
- [scripts/verify-genie.py](../../../scripts/verify-genie.py)
- [scripts/build-genie-bundle.sh](../../../scripts/build-genie-bundle.sh)
- [docs/install/databricks-genie.md](../../../docs/install/databricks-genie.md)
- [docs/resources/agents/databricks-genie-code-skills.md](../../../docs/resources/agents/databricks-genie-code-skills.md)
