#!/usr/bin/env bash
# Validate that the generated Claude/Codex plugin package is self-contained and
# reflects the canonical source catalog under workflows/.

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

fail() {
  printf 'plugin package validation failed: %s\n' "$*" >&2
  exit 1
}

[[ ! -e "$repo_root/skills/helix/references" ]] || \
  fail "skills/helix/references is generated package output and must not be committed on main"

pkg_parent="$(mktemp -d)"
expected_refs="$(mktemp -d)"
trap 'rm -rf "$pkg_parent" "$expected_refs"' EXIT

bash "$repo_root/scripts/build-plugin-package.sh" --out "$pkg_parent" >/dev/null
python3 "$repo_root/scripts/sync_references.py" "$expected_refs" >/dev/null

pkg_root="$pkg_parent/helix"
pkg_skill="$pkg_root/skills/helix"

[[ -f "$pkg_root/.claude-plugin/plugin.json" ]] || fail "missing Claude plugin manifest"
[[ -f "$pkg_root/.codex-plugin/plugin.json" ]] || fail "missing Codex plugin manifest"
[[ -f "$pkg_root/hooks/hooks.json" ]] || fail "missing auto-loaded hooks/hooks.json"
[[ -f "$pkg_skill/SKILL.md" ]] || fail "missing packaged SKILL.md"
[[ -f "$pkg_root/library/skill-prompts/stop-at-triggers.yml" ]] || fail "missing packaged library prompt"
[[ -f "$pkg_root/PACKAGE-SOURCE.json" ]] || fail "missing package provenance"

if ! diff -r "$expected_refs" "$pkg_skill/references" >/dev/null 2>&1; then
  diff -r "$expected_refs" "$pkg_skill/references" >&2 || true
  fail "packaged references differ from workflows/ source; run scripts/build-plugin-package.sh"
fi

python3 - "$pkg_skill/SKILL.md" <<'PY' || fail "packaged SKILL.md frontmatter invalid"
import sys
import yaml

path = sys.argv[1]
text = open(path, encoding="utf-8").read()
if not text.startswith("---\n"):
    raise SystemExit("missing frontmatter")
end = text.find("\n---\n", 4)
if end == -1:
    raise SystemExit("unterminated frontmatter")
fm = yaml.safe_load(text[4:end])
if fm.get("name") != "helix":
    raise SystemExit("name must be helix")
desc = fm.get("description") or ""
if len(desc) > 1024:
    raise SystemExit("description exceeds 1024 characters")
PY

echo "validated generated plugin package"
