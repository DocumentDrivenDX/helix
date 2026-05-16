#!/usr/bin/env bash
# Verify the static invariants of an installed HELIX skill directory.
#
# Usage: bash verify-skill-layout.sh <skill-root>
#
# Asserts:
#   - <skill-root>/SKILL.md exists and is readable
#   - SKILL.md frontmatter parses as YAML
#   - frontmatter `name` equals basename(<skill-root>)  (agentskills.io invariant)
#   - frontmatter `description` is 1..1024 chars
#   - no sibling helix-* directories (legacy pre-collapse layout)
#   - no .git directory inside <skill-root> (not a working tree)
#
# Exit codes:
#   0  all assertions pass
#   1  some assertion failed (prints which)
#   2  argument error

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "usage: $0 <skill-root>" >&2
  exit 2
fi

SKILL_ROOT="$1"

if [[ ! -d "$SKILL_ROOT" ]]; then
  echo "FAIL: skill root not a directory: $SKILL_ROOT" >&2
  exit 1
fi

SKILL_MD="$SKILL_ROOT/SKILL.md"
if [[ ! -f "$SKILL_MD" ]]; then
  echo "FAIL: SKILL.md not found at $SKILL_MD" >&2
  exit 1
fi

EXPECTED_NAME="$(basename "$SKILL_ROOT")"

# Parse frontmatter with python (POSIX-compatible enough).
python3 - "$SKILL_MD" "$EXPECTED_NAME" <<'PY'
import sys
import re

path, expected_name = sys.argv[1], sys.argv[2]
with open(path) as f:
    content = f.read()

if not content.startswith("---\n"):
    print(f"FAIL: {path} missing YAML frontmatter (no leading ---)", file=sys.stderr)
    sys.exit(1)

end = content.find("\n---\n", 4)
if end == -1:
    print(f"FAIL: {path} frontmatter unterminated (no closing ---)", file=sys.stderr)
    sys.exit(1)

fm = content[4:end]
name_match = re.search(r"^name:\s*(.+?)\s*$", fm, re.M)
desc_match = re.search(r"^description:\s*(.+?)\s*$", fm, re.M)

if not name_match:
    print(f"FAIL: {path} frontmatter missing `name`", file=sys.stderr)
    sys.exit(1)
if name_match.group(1).strip() != expected_name:
    print(f"FAIL: name `{name_match.group(1).strip()}` != dir basename `{expected_name}` (agentskills.io invariant)", file=sys.stderr)
    sys.exit(1)

if not desc_match or not desc_match.group(1).strip():
    print(f"FAIL: {path} frontmatter missing/empty `description`", file=sys.stderr)
    sys.exit(1)
desc_len = len(desc_match.group(1).strip())
if desc_len < 1 or desc_len > 1024:
    print(f"FAIL: description {desc_len} chars (1..1024 expected per agentskills.io spec)", file=sys.stderr)
    sys.exit(1)

print(f"ok: SKILL.md frontmatter (name={expected_name}, description={desc_len} chars)")
PY

# Check parent dir for legacy helix-* siblings.
PARENT="$(dirname "$SKILL_ROOT")"
if find "$PARENT" -maxdepth 1 -type d -name 'helix-*' -not -path "$SKILL_ROOT" 2>/dev/null | grep -q .; then
  echo "FAIL: legacy helix-* sibling directories found in $PARENT" >&2
  find "$PARENT" -maxdepth 1 -type d -name 'helix-*' -not -path "$SKILL_ROOT" >&2
  exit 1
fi
echo "ok: no legacy helix-* sibling directories"

# Check that skill root is not itself a git working tree.
if [[ -e "$SKILL_ROOT/.git" ]]; then
  echo "FAIL: $SKILL_ROOT/.git exists (skill root should not be a working tree)" >&2
  exit 1
fi
echo "ok: not a git working tree"

echo
echo "verify-skill-layout: PASS ($SKILL_ROOT)"
