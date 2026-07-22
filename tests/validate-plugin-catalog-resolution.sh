#!/usr/bin/env bash
# Filesystem-only checks for §Catalog Resolution path availability.
#
# Proves documented paths EXIST for:
#   - HELIX self-host / source-checkout (project + skill-relative workflows/)
#   - full plugin-root layout (skills/helix + ../../workflows)
#   - generated package floor (skills/helix/references/)
#   - adopter project with NO local workflows/ still has plugin/package paths
#
# Does NOT prove the model follows precedence (that needs a functional/LLM
# probe). Failures here mean packaging or layout broke fall-through.

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

fail() {
  printf 'catalog resolution validation failed: %s\n' "$*" >&2
  exit 1
}

pass() {
  printf 'ok: %s\n' "$*"
}

# --- Self-host / source checkout (this repo) ---
[[ -f "$repo_root/workflows/graph.yml" ]] || fail "self-host missing workflows/graph.yml"
[[ -f "$repo_root/workflows/activities/01-frame/artifacts/prd/template.md" ]] \
  || fail "self-host missing PRD template"
[[ -f "$repo_root/workflows/voice.yml" ]] || fail "self-host missing workflows/voice.yml"
[[ -f "$repo_root/skills/helix/SKILL.md" ]] || fail "missing skills/helix/SKILL.md"
skill_root="$repo_root/skills/helix"
[[ -f "$skill_root/../../workflows/graph.yml" ]] \
  || fail "skill-relative ../../workflows/graph.yml missing from source skill root"
pass "self-host / source-checkout catalog paths present"

# Project-local rank stays above plugin: SKILL.md must document in-tree project
# workflows before plugin env roots (ordering contract from plan A1).
if ! awk '
  /## Catalog Resolution/ { in_sec=1; next }
  in_sec && /^## / { exit }
  in_sec { print }
' "$skill_root/SKILL.md" | grep -n 'In-tree project catalog\|In-tree catalog\|In-tree project' >/dev/null; then
  # accept either heading phrasing
  if ! awk '
    /## Catalog Resolution/ { in_sec=1; next }
    in_sec && /^## / { exit }
    in_sec { print }
  ' "$skill_root/SKILL.md" | grep -E 'In-tree' >/dev/null; then
    fail "Catalog Resolution must still document in-tree project workflows rank"
  fi
fi
catalog_sec="$(awk '
  /## Catalog Resolution/ { in_sec=1; next }
  in_sec && /^## / { exit }
  in_sec { print }
' "$skill_root/SKILL.md")"
# Numbered step order (ignore prose summary that may mention env vars early):
# step 2 In-tree must appear before step 4 Plugin env root.
intree_line="$(printf '%s\n' "$catalog_sec" | grep -nE '^[0-9]+\. \*\*In-tree' | head -1 | cut -d: -f1)"
env_step_line="$(printf '%s\n' "$catalog_sec" | grep -nE '^[0-9]+\. \*\*Plugin env root' | head -1 | cut -d: -f1)"
source_line="$(printf '%s\n' "$catalog_sec" | grep -nE '^[0-9]+\. \*\*Source-checkout' | head -1 | cut -d: -f1)"
[[ -n "$intree_line" ]] || fail "Catalog Resolution missing numbered In-tree step"
[[ -n "$source_line" ]] || fail "Catalog Resolution missing numbered Source-checkout step"
[[ -n "$env_step_line" ]] || fail "Catalog Resolution missing numbered Plugin env root step"
printf '%s\n' "$catalog_sec" | grep -q 'GROK_PLUGIN_ROOT' \
  || fail "Catalog Resolution missing GROK_PLUGIN_ROOT"
printf '%s\n' "$catalog_sec" | grep -q 'CLAUDE_PLUGIN_ROOT' \
  || fail "Catalog Resolution missing CLAUDE_PLUGIN_ROOT"
(( intree_line < source_line )) || fail "In-tree step must precede Source-checkout step"
(( source_line < env_step_line )) || fail "Source-checkout step must precede Plugin env root (no demotion)"
pass "SKILL.md documents fall-through with project rank above plugin env"

# --- Full plugin-root fixture (skills/helix + workflows at plugin root) ---
full_plugin="$(mktemp -d)"
pkg_parent="$(mktemp -d)"
adopter="$(mktemp -d)"
env_root="$(mktemp -d)"
trap 'rm -rf "$full_plugin" "$pkg_parent" "$adopter" "$env_root"' EXIT
mkdir -p "$full_plugin/skills/helix" "$full_plugin/workflows/activities/01-frame/artifacts/prd"
cp -f "$repo_root/skills/helix/SKILL.md" "$full_plugin/skills/helix/SKILL.md"
cp -f "$repo_root/workflows/graph.yml" "$full_plugin/workflows/graph.yml"
cp -f "$repo_root/workflows/voice.yml" "$full_plugin/workflows/voice.yml"
cp -f "$repo_root/workflows/activities/01-frame/artifacts/prd/template.md" \
  "$full_plugin/workflows/activities/01-frame/artifacts/prd/template.md"
fp_skill="$full_plugin/skills/helix"
[[ -f "$fp_skill/../../workflows/graph.yml" ]] \
  || fail "full plugin-root relative graph missing"
[[ -f "$fp_skill/../../workflows/activities/01-frame/artifacts/prd/template.md" ]] \
  || fail "full plugin-root relative PRD template missing"
[[ ! -e "$fp_skill/references/graph.yml" ]] \
  || fail "full plugin-root fixture should not need references/ floor"
pass "full plugin-root layout binds via ../../workflows/"

# --- Generated package floor ---
bash "$repo_root/scripts/build-plugin-package.sh" --out "$pkg_parent" >/dev/null
pkg_skill="$pkg_parent/helix/skills/helix"
[[ -f "$pkg_skill/SKILL.md" ]] || fail "package missing SKILL.md"
[[ -f "$pkg_skill/references/graph.yml" ]] || fail "package missing references/graph.yml"
[[ -f "$pkg_skill/references/voice.yml" ]] || fail "package missing references/voice.yml"
[[ -f "$pkg_skill/references/activities/01-frame/artifacts/prd/template.md" ]] \
  || fail "package missing PRD template on references floor"
pass "generated package references/ floor present"

# --- Adopter with NO local workflows still has plugin/package paths ---
mkdir -p "$adopter/docs/helix/01-frame"
cat > "$adopter/.helix.yml" <<'YAML'
version: 1
flows:
  - id: helix
    root: docs/helix/
defaults:
  flow: helix
YAML
# no workflows/ under adopter
[[ ! -e "$adopter/workflows" ]] || fail "adopter fixture must not have workflows/"
# catalog still available from full plugin and package skill roots
[[ -f "$fp_skill/../../workflows/graph.yml" ]] \
  || fail "adopter+full-plugin: graph not available via plugin skill relative path"
[[ -f "$pkg_skill/references/graph.yml" ]] \
  || fail "adopter+package: graph not available via references floor"
[[ -f "$fp_skill/../../workflows/activities/01-frame/artifacts/prd/template.md" ]] \
  || fail "adopter+full-plugin: PRD template not available"
[[ -f "$pkg_skill/references/activities/01-frame/artifacts/prd/template.md" ]] \
  || fail "adopter+package: PRD template not available"
pass "no-local-workflows adopter still has plugin/package catalog paths"

# --- Env-root shape (path existence under a fake env root) ---
# Documents the layout A1 step 4 expects; does not set process env permanently.
mkdir -p "$env_root/workflows" "$env_root/skills/helix/references"
cp -f "$repo_root/workflows/graph.yml" "$env_root/workflows/graph.yml"
cp -f "$repo_root/workflows/graph.yml" "$env_root/skills/helix/references/graph.yml"
[[ -f "$env_root/workflows/graph.yml" ]] || fail "env-root workflows/graph.yml"
[[ -f "$env_root/skills/helix/references/graph.yml" ]] || fail "env-root references floor"
pass "plugin env-root layouts (workflows/ and skills/helix/references/) are well-formed"

echo
echo "validate-plugin-catalog-resolution: PASS"
