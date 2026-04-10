#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
skills_dir="$repo_root/skills"
agents_package_dir="$repo_root/.agents/skills"
claude_package_dir="$repo_root/.claude/skills"

declare -A skills_requiring_argument_hint=(
  [helix-align]=1
  [helix-backfill]=1
  [helix-check]=1
  [helix-experiment]=1
  [helix-build]=1
  [helix-design]=1
  [helix-evolve]=1
  [helix-implement]=1
  [helix-plan]=1
  [helix-polish]=1
  [helix-review]=1
  [helix-run]=1
  [helix-triage]=1
)

fail() {
  printf 'skill validation failed: %s\n' "$*" >&2
  exit 1
}

assert_file_contains() {
  local path="$1"
  local needle="$2"
  local message="$3"

  [[ -f "$path" ]] || fail "missing file for validation: $path"
  if ! grep -Fq "$needle" "$path"; then
    fail "$message"
  fi
}

assert_command_fails() {
  local output_file="$1"
  local message="$2"
  shift 2

  if "$@" >"$output_file" 2>&1; then
    fail "$message"
  fi
}

# ---------- Plugin layout checks ----------

plugin_manifest="$repo_root/.claude-plugin/plugin.json"
[[ -f "$plugin_manifest" ]] || fail "missing plugin manifest at .claude-plugin/plugin.json"
plugin_bin="$repo_root/bin/helix"
plugin_hooks="$repo_root/hooks/hooks.json"

# Validate plugin.json is parseable JSON with required fields
if command -v python3 &>/dev/null; then
  python3 - "$plugin_manifest" "$plugin_bin" "$plugin_hooks" <<'PYEOF'
import json, sys
path, plugin_bin, plugin_hooks = sys.argv[1:4]
try:
    manifest = json.load(open(path))
except json.JSONDecodeError as e:
    print(f"invalid JSON in {path}: {e}", file=sys.stderr)
    sys.exit(1)
required = ("name", "version", "description", "skills", "hooks")
missing = [k for k in required if not manifest.get(k)]
if missing:
    print(f"plugin.json missing required fields: {', '.join(missing)}", file=sys.stderr)
    sys.exit(1)
if manifest["skills"] != "./skills/":
    print(f"plugin.json skills must be ./skills/ (got {manifest['skills']!r})", file=sys.stderr)
    sys.exit(1)
if manifest["hooks"] != "./hooks/hooks.json":
    print(f"plugin.json hooks must be ./hooks/hooks.json (got {manifest['hooks']!r})", file=sys.stderr)
    sys.exit(1)
try:
    hooks = json.load(open(plugin_hooks))
except json.JSONDecodeError as e:
    print(f"invalid JSON in {plugin_hooks}: {e}", file=sys.stderr)
    sys.exit(1)
if not isinstance(hooks, dict):
    print(f"{plugin_hooks} must contain a JSON object", file=sys.stderr)
    sys.exit(1)
if "version" not in hooks or "hooks" not in hooks:
    print(f"{plugin_hooks} must define version and hooks keys", file=sys.stderr)
    sys.exit(1)
PYEOF
  [[ $? -eq 0 ]] || fail "plugin.json validation failed"
fi

[[ -f "$plugin_bin" ]] || fail "missing plugin wrapper at bin/helix"
[[ -x "$plugin_bin" ]] || fail "expected bin/helix to be executable"
[[ -f "$plugin_hooks" ]] || fail "missing plugin hooks at hooks/hooks.json"

# Verify that workflows/ references in SKILL.md files resolve from plugin root
while IFS= read -r wf_ref; do
  [[ -n "$wf_ref" ]] || continue
  wf_path="$repo_root/$wf_ref"
  [[ -f "$wf_path" ]] || fail "a SKILL.md references $wf_ref which does not exist at $wf_path"
done < <(grep -roh "workflows/[a-zA-Z0-9/_.-]*\.md" "$repo_root/skills"/*/SKILL.md 2>/dev/null | sort -u)

# ------------------------------------------

extract_frontmatter() {
  local skill_file="$1"

  awk '
    NR == 1 && $0 == "---" { in_frontmatter = 1; next }
    in_frontmatter && $0 == "---" { exit }
    in_frontmatter { print }
  ' "$skill_file"
}

extract_field() {
  local frontmatter="$1"
  local key="$2"

  printf '%s\n' "$frontmatter" | sed -n "s/^${key}:[[:space:]]*//p" | head -n1
}

[[ -d "$skills_dir" ]] || fail "missing skills directory at $skills_dir"
[[ -d "$agents_package_dir" ]] || fail "missing package directory at $agents_package_dir"
[[ -d "$claude_package_dir" ]] || fail "missing package directory at $claude_package_dir"

shopt -s nullglob
skill_dirs=("$skills_dir"/helix-*)
[[ "${#skill_dirs[@]}" -gt 0 ]] || fail "no published skills found under $skills_dir"

mapfile -t expected_skills < <(
  for path in "${skill_dirs[@]}"; do
    [[ -d "$path" ]] || continue
    printf '%s\n' "${path##*/}"
  done | sort
)

# Validate .agents/skills/ symlinks
mapfile -t agents_published_skills < <(
  for path in "$agents_package_dir"/*; do
    [[ -e "$path" || -L "$path" ]] || continue
    printf '%s\n' "${path##*/}"
  done | sort
)

# Validate .claude/skills/ symlinks
mapfile -t claude_published_skills < <(
  for path in "$claude_package_dir"/*; do
    [[ -e "$path" || -L "$path" ]] || continue
    printf '%s\n' "${path##*/}"
  done | sort
)

# Check .agents/skills/ matches skills/
expected_list="$(printf '%s\n' "${expected_skills[@]}")"
agents_published_list="$(printf '%s\n' "${agents_published_skills[@]}")"
[[ "$expected_list" == "$agents_published_list" ]] || fail "published skills in .agents/skills do not match skills/"

# Check .claude/skills/ matches skills/
claude_published_list="$(printf '%s\n' "${claude_published_skills[@]}")"
[[ "$expected_list" == "$claude_published_list" ]] || fail "published skills in .claude/skills do not match skills/"

for name in "${expected_skills[@]}"; do
  skill_file="$skills_dir/$name/SKILL.md"
  agents_package_link="$agents_package_dir/$name"
  claude_package_link="$claude_package_dir/$name"

  [[ -f "$skill_file" ]] || fail "missing SKILL.md for $name"

  # Validate .agents/skills/ symlinks
  [[ -L "$agents_package_link" ]] || fail "expected $agents_package_link to be a symlink"
  [[ "$(readlink "$agents_package_link")" == "../../skills/$name" ]] || fail "expected $agents_package_link to target ../../skills/$name"

  # Validate .claude/skills/ symlinks
  [[ -L "$claude_package_link" ]] || fail "expected $claude_package_link to be a symlink"
  [[ "$(readlink "$claude_package_link")" == "../../skills/$name" ]] || fail "expected $claude_package_link to target ../../skills/$name"

  frontmatter="$(extract_frontmatter "$skill_file")"
  [[ -n "$frontmatter" ]] || fail "missing frontmatter in $skill_file"

  skill_name="$(extract_field "$frontmatter" "name")"
  description="$(extract_field "$frontmatter" "description")"
  argument_hint="$(extract_field "$frontmatter" "argument-hint")"

  # YAML syntax check: detect unquoted colons in values that break parsers.
  # Codex's skill loader rejects these with "invalid YAML: mapping values
  # are not allowed in this context".
  while IFS= read -r line; do
    # Skip lines that are properly quoted (single or double quotes after key:)
    if [[ "$line" =~ ^[a-z-]+:\ *[\'\"] ]]; then
      continue
    fi
    # Check for a second colon-space in an unquoted value
    key_removed="${line#*: }"
    if [[ "$key_removed" == *": "* ]]; then
      fail "unquoted colon in $skill_file frontmatter: $line — wrap the value in quotes"
    fi
  done <<< "$frontmatter"

  [[ -n "$skill_name" ]] || fail "missing name field in $skill_file"
  # For symlinked skill directories, the SKILL.md name should match the
  # symlink target (not the link name), since the link is just an alias.
  if [[ -L "$skills_dir/$name" ]]; then
    target_name="$(basename "$(readlink "$skills_dir/$name")")"
    [[ "$skill_name" == "$target_name" ]] || fail "frontmatter name $skill_name does not match symlink target $target_name for alias $name"
  else
    [[ "$skill_name" == "$name" ]] || fail "frontmatter name $skill_name does not match directory $name"
  fi
  [[ -n "$description" ]] || fail "missing description field in $skill_file"

  if [[ -n "${skills_requiring_argument_hint[$name]:-}" && -z "$argument_hint" ]]; then
    fail "missing argument-hint field in $skill_file"
  fi
done

assert_file_contains \
  "$repo_root/skills/helix-triage/SKILL.md" \
  "deterministic acceptance and success-measurement criteria" \
  "helix-triage must require success-measurement criteria for execution-ready beads"
assert_file_contains \
  "$repo_root/skills/helix-triage/SKILL.md" \
  "DDx-managed execution to close merged work with evidence" \
  "helix-triage must explain DDx-managed close-with-evidence expectations"
assert_file_contains \
  "$repo_root/skills/helix-polish/SKILL.md" \
  "require execution-ready beads to name exact commands," \
  "helix-polish must require explicit measurable acceptance text for execution-ready beads"
assert_file_contains \
  "$repo_root/skills/helix-polish/SKILL.md" \
  "flag it as not execution-ready" \
  "helix-polish must define a flagging path for non-measurable acceptance text"
assert_file_contains \
  "$repo_root/workflows/actions/polish.md" \
  "Treat \"works\", \"correct\", \"complete\", \"aligned\", or similar adjectives" \
  "polish action must reject vague non-measurable acceptance wording"
assert_file_contains \
  "$repo_root/workflows/actions/polish.md" \
  "flag the bead as **not execution-ready**" \
  "polish action must define a not-execution-ready flagging path"
assert_file_contains \
  "$repo_root/docs/helix/01-frame/features/FEAT-011-slider-autonomy.md" \
  "### AC-09: Automation-Friendly Success Criteria" \
  "FEAT-011 must retain the automation-friendly success-criteria acceptance contract"
assert_file_contains \
  "$repo_root/docs/helix/02-design/contracts/CONTRACT-001-ddx-helix-boundary.md" \
  "HELIX-authored execution beads must make success machine-auditable." \
  "CONTRACT-001 must retain machine-auditable bead success criteria"
assert_file_contains \
  "$repo_root/docs/helix/02-design/technical-designs/TD-011-slider-autonomy-implementation.md" \
  "### Decision 5c: Bead Success-Measurement Contract" \
  "TD-011 must retain the bead success-measurement decision"

reject_output="$(mktemp)"
command -v python3 >/dev/null 2>&1 || fail "python3 is required for execution-ready bead validation"
assert_command_fails \
  "$reject_output" \
  "execution-ready validator should reject vague acceptance fixtures" \
  python3 \
  "$repo_root/scripts/validate_execution_ready_beads.py" \
  "$repo_root/tests/fixtures/execution-ready-beads/vague-acceptance.jsonl"
grep -Fq "hx-vague-ac" "$reject_output" || fail "execution-ready validator should identify the rejected fixture"
rm -f "$reject_output"

python3 "$repo_root/scripts/validate_execution_ready_beads.py" \
  "$repo_root/tests/fixtures/execution-ready-beads/flagged-acceptance.jsonl"

printf 'validated %d HELIX skills\n' "${#expected_skills[@]}"
