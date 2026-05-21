#!/usr/bin/env bash
# Validate install surface consistency: manifests + docs agreement.
#
# Asserts:
#   - plugin.json repository URL matches marketplace.json plugins[0].source.url
#   - No easel/helix references in docs/install/ (should be DocumentDrivenDX/helix)
#   - Install docs reference the canonical repo (from marketplace.json)
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
MARKETPLACE_JSON="$REPO_ROOT/.claude-plugin/marketplace.json"
INSTALL_DOCS_DIR="$REPO_ROOT/docs/install"

if [[ ! -f "$PLUGIN_JSON" ]]; then
  echo "FAIL: plugin.json not found at $PLUGIN_JSON" >&2
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

# Extract and compare manifest repos with python
python3 - "$PLUGIN_JSON" "$MARKETPLACE_JSON" <<'PY'
import sys
import json
import re

plugin_path, marketplace_path = sys.argv[1], sys.argv[2]

with open(plugin_path) as f:
    plugin = json.load(f)

with open(marketplace_path) as f:
    marketplace = json.load(f)

# Extract repo paths from both manifests
plugin_repo = plugin.get("repository", "")
mp_source = marketplace.get("plugins", [{}])[0].get("source", {})
# Claude Code marketplace shape: {"source": "github", "repo": "owner/name"} or {"source": "url", "url": "..."}
marketplace_url = mp_source.get("url", "") or mp_source.get("repo", "")

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
if grep -rE 'easel/helix' "$INSTALL_DOCS_DIR" 2>/dev/null; then
  echo "FAIL: unwanted 'easel/helix' references found in $INSTALL_DOCS_DIR" >&2
  exit 1
fi
echo "ok: no unwanted 'easel/helix' references in install docs"

# Check that install docs reference the canonical repo
if ! grep -rE "DocumentDrivenDX/helix" "$INSTALL_DOCS_DIR" >/dev/null 2>&1; then
  echo "FAIL: canonical repo '$MARKER_REPO' not referenced in install docs" >&2
  exit 1
fi
echo "ok: install docs reference canonical repo ($MARKER_REPO)"

echo
echo "validate-install-consistency: PASS"
