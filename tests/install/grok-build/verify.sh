#!/usr/bin/env bash
# Static verify for Grok HELIX plugin install.
#
# Exit:
#   0  pass
#   77 grok not available (skip — not a failure for CI without grok)
#   1  fail

set -euo pipefail

if ! command -v grok >/dev/null 2>&1; then
  echo "SKIP: grok not on PATH"
  exit 77
fi

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd -P)"
SHARED_VERIFY="$REPO_ROOT/tests/install/shared/verify-skill-layout.sh"

echo "→ grok plugin list"
grok plugin list

echo "→ resolve skill root (prefer installed-plugins helix, else checkout)"
SKILL_ROOT=""
# Prefer registry-installed full plugin tree
if [[ -d "$HOME/.grok/installed-plugins" ]]; then
  cand="$(find "$HOME/.grok/installed-plugins" -path '*/skills/helix/SKILL.md' 2>/dev/null | head -1 || true)"
  if [[ -n "$cand" ]]; then
    SKILL_ROOT="$(dirname "$cand")"
  fi
fi
if [[ -z "$SKILL_ROOT" && -f "$REPO_ROOT/skills/helix/SKILL.md" ]]; then
  SKILL_ROOT="$REPO_ROOT/skills/helix"
fi
if [[ -z "$SKILL_ROOT" ]]; then
  echo "FAIL: could not resolve skills/helix root"
  exit 1
fi
echo "→ SKILL_ROOT=$SKILL_ROOT"

# Canonical source: path must contain 'helix' and end with skills/helix
case "$SKILL_ROOT" in
  */skills/helix) ;;
  *)
    echo "FAIL: skill root is not …/skills/helix: $SKILL_ROOT"
    exit 1
    ;;
esac

# Prefer non-legacy sources: reject known DDx legacy skill names when inspecting
if command -v python3 >/dev/null 2>&1; then
  python3 - <<'PY' || exit 1
import json, subprocess, sys
try:
    raw = subprocess.check_output(["grok", "inspect", "--json"], text=True)
    data = json.loads(raw)
except Exception as e:
    print(f"WARN: grok inspect --json failed: {e}", file=sys.stderr)
    sys.exit(0)

def walk(o, out):
    if isinstance(o, dict):
        if o.get("name") == "helix" or (
            isinstance(o.get("source"), dict)
            and "helix" in str(o.get("source")).lower()
            and o.get("name")
        ):
            out.append(o)
        for v in o.values():
            walk(v, out)
    elif isinstance(o, list):
        for v in o:
            walk(v, out)

found = []
walk(data, found)
helix = [s for s in found if s.get("name") == "helix"]
if not helix:
    print("FAIL: grok inspect has no skill name=helix", file=sys.stderr)
    sys.exit(1)
# At least one helix skill should not be the renamed helix-workflow path only
paths = []
for s in helix:
    src = s.get("source") or {}
    if isinstance(src, dict):
        paths.append(str(src.get("path") or src))
    else:
        paths.append(str(src))
print("→ helix skill sources:")
for p in paths:
    print("  ", p)
if any("helix-workflow" in p for p in paths) and not any(
    "/skills/helix/" in p or p.endswith("skills/helix/SKILL.md") for p in paths
):
    print("FAIL: only legacy helix-workflow found", file=sys.stderr)
    sys.exit(1)
print("ok: canonical helix skill present in inspect")
PY
fi

echo "→ verify-skill-layout"
bash "$SHARED_VERIFY" "$SKILL_ROOT"

# Adopter no-local-workflows path probe against this skill root
if [[ -f "$SKILL_ROOT/../../workflows/graph.yml" ]]; then
  echo "ok: full-plugin catalog via ../../workflows/graph.yml"
elif [[ -f "$SKILL_ROOT/references/graph.yml" ]]; then
  echo "ok: package floor catalog via references/graph.yml"
else
  echo "FAIL: neither ../../workflows/graph.yml nor references/graph.yml from skill root"
  exit 1
fi

echo "verify: PASS"
