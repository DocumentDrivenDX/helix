#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
skills_dir="$repo_root/skills"
package_dir="$repo_root/.agents/skills"

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
[[ -d "$package_dir" ]] || fail "missing package directory at $package_dir"

shopt -s nullglob
skill_dirs=("$skills_dir"/helix-*)
[[ "${#skill_dirs[@]}" -gt 0 ]] || fail "no published skills found under $skills_dir"

mapfile -t expected_skills < <(
  for path in "${skill_dirs[@]}"; do
    [[ -d "$path" ]] || continue
    printf '%s\n' "${path##*/}"
  done | sort
)

mapfile -t published_skills < <(
  for path in "$package_dir"/*; do
    [[ -e "$path" || -L "$path" ]] || continue
    printf '%s\n' "${path##*/}"
  done | sort
)

expected_list="$(printf '%s\n' "${expected_skills[@]}")"
published_list="$(printf '%s\n' "${published_skills[@]}")"
[[ "$expected_list" == "$published_list" ]] || fail "published skills in .agents/skills do not match skills/"

for name in "${expected_skills[@]}"; do
  skill_file="$skills_dir/$name/SKILL.md"
  package_link="$package_dir/$name"

  [[ -f "$skill_file" ]] || fail "missing SKILL.md for $name"
  [[ -L "$package_link" ]] || fail "expected $package_link to be a symlink"
  [[ "$(readlink "$package_link")" == "../../skills/$name" ]] || fail "expected $package_link to target ../../skills/$name"

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

printf 'validated %d HELIX skills\n' "${#expected_skills[@]}"
