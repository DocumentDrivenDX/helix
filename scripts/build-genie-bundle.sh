#!/usr/bin/env bash
# Build a Databricks Genie Code-compliant skill bundle from HELIX source.
#
# Outputs:
#   dist/genie-bundle/helix/SKILL.md
#   dist/genie-bundle/helix/references/activities/<NN>-<activity>/...
#
# The parent directory name `helix` must match the `name:` field in
# SKILL.md frontmatter (agentskills.io spec invariant).
#
# Usage: bash scripts/build-genie-bundle.sh [--out DIR]

set -euo pipefail

OUT_DIR="dist/genie-bundle/helix"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --out) OUT_DIR="$2/helix"; shift 2 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

SRC_SKILL="skills/helix/SKILL.md"
SRC_CATALOG="workflows/activities"
SRC_VOICE="workflows/voice.yml"
SRC_LIBRARY="library"

if [[ ! -f "$SRC_SKILL" ]]; then
  echo "error: $SRC_SKILL not found" >&2
  exit 3
fi
if [[ ! -d "$SRC_CATALOG" ]]; then
  echo "error: $SRC_CATALOG not found" >&2
  exit 3
fi
if [[ ! -f "$SRC_VOICE" ]]; then
  echo "error: $SRC_VOICE not found" >&2
  exit 3
fi
if [[ ! -d "$SRC_LIBRARY" ]]; then
  echo "error: $SRC_LIBRARY not found (SKILL.md references library/skill-prompts/...)" >&2
  exit 3
fi

# Validate SKILL.md frontmatter: name must equal 'helix'.
python3 - "$SRC_SKILL" <<'PY'
import sys
import re

path = sys.argv[1]
with open(path) as f:
    content = f.read()

if not content.startswith("---\n"):
    print(f"error: {path} missing YAML frontmatter", file=sys.stderr)
    sys.exit(4)

end = content.find("\n---\n", 4)
if end == -1:
    print(f"error: {path} frontmatter unterminated", file=sys.stderr)
    sys.exit(4)

fm = content[4:end]
name_match = re.search(r"^name:\s*(.+?)\s*$", fm, re.M)
desc_match = re.search(r"^description:\s*(.+?)\s*$", fm, re.M)

if not name_match or name_match.group(1).strip() != "helix":
    print(f"error: SKILL.md frontmatter `name` must be exactly 'helix'", file=sys.stderr)
    sys.exit(5)
if not desc_match or not desc_match.group(1).strip():
    print(f"error: SKILL.md frontmatter `description` must be non-empty", file=sys.stderr)
    sys.exit(5)

desc = desc_match.group(1).strip()
if len(desc) > 1024:
    print(f"warning: description is {len(desc)} chars (spec recommends <=1024)", file=sys.stderr)
PY

echo "✓ SKILL.md frontmatter OK (name=helix)"

# Assemble the bundle.
rm -rf "$OUT_DIR"
mkdir -p "$OUT_DIR/references"

cp "$SRC_SKILL" "$OUT_DIR/SKILL.md"
echo "✓ copied SKILL.md → $OUT_DIR/SKILL.md"

cp -r "$SRC_CATALOG" "$OUT_DIR/references/activities"
echo "✓ copied $SRC_CATALOG → $OUT_DIR/references/activities/"

cp "$SRC_VOICE" "$OUT_DIR/references/voice.yml"
echo "✓ copied $SRC_VOICE → $OUT_DIR/references/voice.yml"

cp -r "$SRC_LIBRARY" "$OUT_DIR/library"
echo "✓ copied $SRC_LIBRARY → $OUT_DIR/library/"

# Also vendor workflows/concerns so slots.yml + per-concern practices.md resolve,
# and workflows/graph.yml so §"Consult The Graph Before Authoring" resolves.
mkdir -p "$OUT_DIR/workflows"
if [[ -d workflows/concerns ]]; then
  cp -r workflows/concerns "$OUT_DIR/workflows/concerns"
  echo "✓ copied workflows/concerns → $OUT_DIR/workflows/concerns/"
fi
if [[ -f workflows/graph.yml ]]; then
  cp workflows/graph.yml "$OUT_DIR/workflows/graph.yml"
  echo "✓ copied workflows/graph.yml → $OUT_DIR/workflows/graph.yml"
fi
if [[ -f "$SRC_VOICE" ]]; then
  cp "$SRC_VOICE" "$OUT_DIR/workflows/voice.yml"
  echo "✓ copied $SRC_VOICE → $OUT_DIR/workflows/voice.yml"
fi

# Report what we built.
SKILL_BYTES=$(stat -c%s "$OUT_DIR/SKILL.md")
ACTIVITY_COUNT=$(find "$OUT_DIR/references/activities" -mindepth 1 -maxdepth 1 -type d | wc -l)
LIBRARY_FILES=$(find "$OUT_DIR/library" -type f | wc -l)
FILE_COUNT=$(find "$OUT_DIR" -type f | wc -l)

echo
echo "Genie bundle built:"
echo "  path:        $OUT_DIR"
echo "  SKILL.md:    $SKILL_BYTES bytes"
echo "  activities:  $ACTIVITY_COUNT"
echo "  library:     $LIBRARY_FILES files"
echo "  total files: $FILE_COUNT"
echo
echo "Next: python scripts/install-genie.py --bundle $OUT_DIR"
