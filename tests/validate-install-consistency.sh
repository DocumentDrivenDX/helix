#!/usr/bin/env bash
# Validate install surface consistency: manifests + docs agreement.
#
# Asserts:
#   - Claude and Codex plugin manifests agree on repo/version/skill path
#   - plugin.json repository URL matches marketplace.json plugins[0].source.url
#   - No easel/helix references in install docs or release installer
#   - Install docs reference the canonical repo (from marketplace.json)
#   - docs/install/README.md is the one guide with a section per host
#   - .github/copilot-instructions.md points at the skill and copies none of it
#
# Exit codes:
#   0  all assertions pass
#   1  some assertion failed (prints which)
#   2  argument error

set -euo pipefail

REPO_ROOT="${1:-.}"

if [[ ! -d "$REPO_ROOT" ]]; then
  echo "FAIL: repo root not a directory: $REPO_ROOT" >&2
  exit 2
fi

PLUGIN_JSON="$REPO_ROOT/.claude-plugin/plugin.json"
CODEX_PLUGIN_JSON="$REPO_ROOT/.codex-plugin/plugin.json"
MARKETPLACE_JSON="$REPO_ROOT/.claude-plugin/marketplace.json"
INSTALL_DOCS_DIR="$REPO_ROOT/docs/install"
GENIE_INSTALL="$REPO_ROOT/scripts/genie-install"

if [[ ! -f "$PLUGIN_JSON" ]]; then
  echo "FAIL: plugin.json not found at $PLUGIN_JSON" >&2
  exit 1
fi

if [[ ! -f "$CODEX_PLUGIN_JSON" ]]; then
  echo "FAIL: Codex plugin.json not found at $CODEX_PLUGIN_JSON" >&2
  exit 1
fi

if [[ ! -f "$MARKETPLACE_JSON" ]]; then
  echo "FAIL: marketplace.json not found at $MARKETPLACE_JSON" >&2
  exit 1
fi

if [[ ! -d "$INSTALL_DOCS_DIR" ]]; then
  echo "FAIL: install docs dir not found at $INSTALL_DOCS_DIR" >&2
  exit 1
fi

if [[ ! -f "$GENIE_INSTALL" ]]; then
  echo "FAIL: genie-install not found at $GENIE_INSTALL" >&2
  exit 1
fi

# Extract and compare manifest repos with python
python3 - "$PLUGIN_JSON" "$CODEX_PLUGIN_JSON" "$MARKETPLACE_JSON" <<'PY'
import sys
import json
import re

plugin_path, codex_plugin_path, marketplace_path = sys.argv[1:4]

with open(plugin_path) as f:
    plugin = json.load(f)

with open(codex_plugin_path) as f:
    codex_plugin = json.load(f)

with open(marketplace_path) as f:
    marketplace = json.load(f)

# Extract repo paths from both manifests
plugin_repo = plugin.get("repository", "")
mp_source = marketplace.get("plugins", [{}])[0].get("source", {})
# Claude Code marketplace shape: {"source": "github", "repo": "owner/name"} or {"source": "url", "url": "..."}
marketplace_url = mp_source.get("url", "") or mp_source.get("repo", "")
marketplace_version = marketplace.get("plugins", [{}])[0].get("version", "")

# Normalize URLs: extract owner/repo pattern from GitHub URLs
def extract_repo_path(url):
    # Handle https://github.com/X/Y(.git), git@github.com:X/Y(.git), and bare owner/repo
    match = re.search(r'github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?$', url)
    if match:
        return f"{match.group(1)}/{match.group(2)}"
    return url.strip('/').removesuffix('.git')

plugin_path_norm = extract_repo_path(plugin_repo)
marketplace_path_norm = extract_repo_path(marketplace_url)

if plugin_path_norm != marketplace_path_norm:
    print(f"FAIL: repo mismatch", file=sys.stderr)
    print(f"  plugin.json repository: {plugin_repo} → {plugin_path_norm}", file=sys.stderr)
    print(f"  marketplace.json source.url/.repo: {marketplace_url} → {marketplace_path_norm}", file=sys.stderr)
    sys.exit(1)

codex_path_norm = extract_repo_path(codex_plugin.get("repository", ""))
if codex_path_norm != plugin_path_norm:
    print("FAIL: Codex plugin repo mismatch", file=sys.stderr)
    print(f"  .codex-plugin/plugin.json repository: {codex_plugin.get('repository', '')} → {codex_path_norm}", file=sys.stderr)
    print(f"  .claude-plugin/plugin.json repository: {plugin_repo} → {plugin_path_norm}", file=sys.stderr)
    sys.exit(1)

for field in ("name", "version", "description", "skills"):
    if codex_plugin.get(field) != plugin.get(field):
        print(f"FAIL: Codex plugin field {field!r} does not match Claude plugin manifest", file=sys.stderr)
        print(f"  Codex: {codex_plugin.get(field)!r}", file=sys.stderr)
        print(f"  Claude: {plugin.get(field)!r}", file=sys.stderr)
        sys.exit(1)

if marketplace_version and marketplace_version != plugin.get("version"):
    print("FAIL: marketplace version does not match plugin manifest version", file=sys.stderr)
    print(f"  marketplace: {marketplace_version}", file=sys.stderr)
    print(f"  plugin: {plugin.get('version')}", file=sys.stderr)
    sys.exit(1)

print(f"ok: plugin.json and marketplace.json repos match: {plugin_path_norm}")
PY

MARKER_REPO=$(python3 - "$MARKETPLACE_JSON" <<'PY'
import sys
import json
import re

marketplace_path = sys.argv[1]
with open(marketplace_path) as f:
    marketplace = json.load(f)

mp_source = marketplace.get("plugins", [{}])[0].get("source", {})
marketplace_url = mp_source.get("url", "") or mp_source.get("repo", "")

def extract_repo_path(url):
    match = re.search(r'github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?$', url)
    if match:
        return f"{match.group(1)}/{match.group(2)}"
    return url.strip('/').removesuffix('.git')

print(extract_repo_path(marketplace_url))
PY
)

# Check for unwanted easel/helix references
if grep -rE 'easel/helix' "$INSTALL_DOCS_DIR" "$GENIE_INSTALL" 2>/dev/null; then
  echo "FAIL: unwanted 'easel/helix' references found in install docs or genie-install" >&2
  exit 1
fi
echo "ok: no unwanted 'easel/helix' references in install docs or genie-install"

# Check that install docs reference the canonical repo
if ! grep -rE "DocumentDrivenDX/helix" "$INSTALL_DOCS_DIR" >/dev/null 2>&1; then
  echo "FAIL: canonical repo '$MARKER_REPO' not referenced in install docs" >&2
  exit 1
fi
echo "ok: install docs reference canonical repo ($MARKER_REPO)"

# One install guide: README.md carries every host, including Grok Build
README_MD="$INSTALL_DOCS_DIR/README.md"
if [[ ! -f "$README_MD" ]]; then
  echo "FAIL: missing docs/install/README.md" >&2
  exit 1
fi
echo "ok: docs/install/README.md exists"

for host in 'Claude Code' 'OpenAI Codex CLI' 'GitHub Copilot' 'Grok Build' 'Databricks Genie Code' 'DDx'; do
  if ! grep -qE "^### ${host}\$" "$README_MD"; then
    echo "FAIL: docs/install/README.md must have a per-host section '### ${host}'" >&2
    exit 1
  fi
done
echo "ok: README has a per-host section for all six hosts"

if ! grep -q 'grok plugin install' "$README_MD"; then
  echo "FAIL: docs/install/README.md must document grok plugin install" >&2
  exit 1
fi
echo "ok: README documents grok plugin install"

if ! grep -qE -- '--trust' "$README_MD"; then
  echo "FAIL: docs/install/README.md must mention --trust (or trust flow)" >&2
  exit 1
fi
echo "ok: README documents Grok trust"

if ! grep -qE 'fall.?through|need not vendor|do not copy|do not vendor|need not copy' "$README_MD"; then
  echo "FAIL: README must state no-local-template / fall-through doctrine" >&2
  exit 1
fi
echo "ok: no-local-template / fall-through doctrine present"

# Retired per-host guides must not be referenced from the install docs
if grep -rnE 'install/(claude-code|codex|copilot|grok)\.md' "$INSTALL_DOCS_DIR"; then
  echo "FAIL: install docs reference a retired per-host guide (claude-code/codex/copilot/grok.md)" >&2
  exit 1
fi
echo "ok: no references to retired per-host guides"

# .github/copilot-instructions.md is a pointer at the skill, not a fork of it
COPILOT_MD="$REPO_ROOT/.github/copilot-instructions.md"
if [[ ! -f "$COPILOT_MD" ]]; then
  echo "FAIL: missing .github/copilot-instructions.md" >&2
  exit 1
fi

if ! grep -q 'skills/helix/SKILL.md' "$COPILOT_MD"; then
  echo "FAIL: copilot-instructions.md must point at skills/helix/SKILL.md" >&2
  exit 1
fi
if ! grep -q 'workflows/modes/' "$COPILOT_MD"; then
  echo "FAIL: copilot-instructions.md must point at the mode files under workflows/modes/" >&2
  exit 1
fi
echo "ok: copilot-instructions.md points at the skill and mode files"

# Any of the skill's normative section headings or a mode-level ### heading
# means contract text was copied in.
for heading in '## Routing Rules' '## Mode Contracts' '## Catalog Resolution' '## Activation Discipline' '## Routing Axes' '## Autonomy' '## Voice Resolution' '## Operating Discipline'; do
  if grep -qF "$heading" "$COPILOT_MD"; then
    echo "FAIL: copilot-instructions.md contains skill section '$heading'; it must point at the skill, not copy it" >&2
    exit 1
  fi
done
if grep -qE '^### ' "$COPILOT_MD"; then
  echo "FAIL: copilot-instructions.md contains a '### ' heading (mode contract text copied from the skill)" >&2
  grep -nE '^### ' "$COPILOT_MD" >&2
  exit 1
fi
if grep -qE '^\| `[a-z-]+`(/`[a-z-]+`)? \|' "$COPILOT_MD"; then
  echo "FAIL: copilot-instructions.md contains a routing-table row copied from the skill" >&2
  exit 1
fi
COPILOT_LINES=$(wc -l < "$COPILOT_MD" | tr -d " ")
if (( COPILOT_LINES > 60 )); then
  echo "FAIL: copilot-instructions.md is $COPILOT_LINES lines; a pointer stays under 60" >&2
  exit 1
fi
echo "ok: copilot-instructions.md carries no mode contract text ($COPILOT_LINES lines)"

echo
echo "validate-install-consistency: PASS"
