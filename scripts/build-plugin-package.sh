#!/usr/bin/env bash
# Build the Claude/Codex plugin package from HELIX source.
#
# Source of truth stays in:
#   workflows/                 methodology catalog and concern library
#   skills/helix/SKILL.md      routing skill
#
# Package output materializes the skill-local references floor required by
# installed skill runtimes:
#   dist/plugin-package/helix/skills/helix/references/...
#
# Usage:
#   bash scripts/build-plugin-package.sh [--out DIR]
#
# When --out is supplied, the package is written to DIR/helix.

set -euo pipefail

OUT_PARENT="dist/plugin-package"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --out)
      OUT_PARENT="$2"
      shift 2
      ;;
    *)
      echo "unknown arg: $1" >&2
      exit 2
      ;;
  esac
done

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

OUT_DIR="$OUT_PARENT/helix"
SRC_SKILL="skills/helix/SKILL.md"
SRC_LIBRARY="library"

required_paths=(
  ".claude-plugin/plugin.json"
  ".claude-plugin/marketplace.json"
  ".codex-plugin/plugin.json"
  "hooks/hooks.json"
  "$SRC_SKILL"
  "$SRC_LIBRARY/skill-prompts/stop-at-triggers.yml"
  "workflows/activities"
  "workflows/concerns"
  "workflows/graph.yml"
  "workflows/voice.yml"
)

for path in "${required_paths[@]}"; do
  if [[ ! -e "$path" ]]; then
    echo "error: required package input missing: $path" >&2
    exit 3
  fi
done

python3 - "$SRC_SKILL" <<'PY'
import re
import sys

path = sys.argv[1]
content = open(path, encoding="utf-8").read()
if not content.startswith("---\n"):
    print(f"error: {path} missing YAML frontmatter", file=sys.stderr)
    sys.exit(4)
end = content.find("\n---\n", 4)
if end == -1:
    print(f"error: {path} frontmatter unterminated", file=sys.stderr)
    sys.exit(4)
fm = content[4:end]
name_match = re.search(r"^name:\s*(.+?)\s*$", fm, re.M)
if not name_match or name_match.group(1).strip() != "helix":
    print("error: SKILL.md frontmatter `name` must be exactly 'helix'", file=sys.stderr)
    sys.exit(5)
PY

rm -rf "$OUT_DIR"
mkdir -p "$OUT_DIR/.claude-plugin" "$OUT_DIR/.codex-plugin" "$OUT_DIR/hooks" "$OUT_DIR/skills/helix"

cp -f .claude-plugin/plugin.json "$OUT_DIR/.claude-plugin/plugin.json"
cp -f .claude-plugin/marketplace.json "$OUT_DIR/.claude-plugin/marketplace.json"
cp -f .codex-plugin/plugin.json "$OUT_DIR/.codex-plugin/plugin.json"
cp -f hooks/hooks.json "$OUT_DIR/hooks/hooks.json"
cp -f "$SRC_SKILL" "$OUT_DIR/skills/helix/SKILL.md"
cp -Rf "$SRC_LIBRARY" "$OUT_DIR/library"

python3 scripts/sync_references.py "$OUT_DIR/skills/helix/references" >/dev/null

python3 - "$OUT_DIR/PACKAGE-SOURCE.json" <<'PY'
import json
import subprocess
import sys
from pathlib import Path

out = Path(sys.argv[1])
commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
version = json.load(open(".claude-plugin/plugin.json", encoding="utf-8"))["version"]
data = {
    "package": "helix-plugin",
    "source_commit": commit,
    "version": version,
    "builder": "scripts/build-plugin-package.sh",
    "builder_contract": 1,
}
out.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY

skill_files=$(find "$OUT_DIR/skills/helix" -type f | wc -l | tr -d ' ')
total_files=$(find "$OUT_DIR" -type f | wc -l | tr -d ' ')

echo "Plugin package built:"
echo "  path:        $OUT_DIR"
echo "  skill files: $skill_files"
echo "  total files: $total_files"
