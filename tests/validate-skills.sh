#!/usr/bin/env bash
set -euo pipefail

repo_root="${HELIX_VALIDATE_SKILLS_REPO_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
skills_dir="$repo_root/skills"
agents_package_dir="$repo_root/.agents/skills"
claude_package_dir="$repo_root/.claude/skills"

declare -A skills_requiring_argument_hint=(
  [helix]=1
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

assert_file_not_contains() {
  local path="$1"
  local needle="$2"
  local message="$3"

  [[ -f "$path" ]] || fail "missing file for validation: $path"
  if grep -Fq "$needle" "$path"; then
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

assert_output_contains() {
  local haystack="$1"
  local needle="$2"
  local message="$3"

  if [[ "$haystack" != *"$needle"* ]]; then
    printf 'expected substring: %s\nin:\n%s\n' "$needle" "$haystack" >&2
    fail "$message"
  fi
}

validate_helix_triage_intro() {
  local path="$1"
  local intro normalized
  local blanket_execution_ready_pattern

  [[ -f "$path" ]] || fail "missing file for validation: $path"
  intro="$(
    awk '
      /^# Triage: Shape Execution-Ready And Planning Issues$/ { in_intro = 1; next }
      in_intro && /^## / { exit }
      in_intro { print }
    ' "$path"
  )"
  [[ -n "$intro" ]] || fail "helix-triage intro block is missing"

  normalized="$(
    printf '%s\n' "$intro" \
      | tr '[:upper:]' '[:lower:]' \
      | tr '\n' ' ' \
      | tr -s '[:space:]' ' '
  )"

  blanket_execution_ready_pattern='(every|all|each)([[:space:]]+[[:alpha:]][[:alpha:]-]*)*[[:space:]]+(issue|issues|bead|beads|task|tasks|work[[:space:]]+item|work[[:space:]]+items)[[:space:]]+should[[:space:]]+enter[[:space:]]+the[[:space:]]+tracker[[:space:]]+ready[[:space:]]+(to[[:space:]]+execute|for[[:space:]]+execution)'
  if [[ "$normalized" =~ $blanket_execution_ready_pattern ]]; then
    fail "helix-triage intro must not prime every issue as execution-ready"
  fi
}

assert_helix_triage_blanket_priming_regression() {
  local temp_root output_file regression_output
  local -a blanket_priming_sentences=(
    "All implementation issues should enter the tracker ready to execute when possible."
    "All execution-ready implementation planning and review issues should enter the tracker ready to execute when possible."
  )

  if [[ "${HELIX_VALIDATE_SKILLS_SKIP_REGRESSION:-0}" == "1" ]]; then
    return
  fi

  command -v python3 >/dev/null 2>&1 || fail "python3 is required for execution-ready bead validation"

  temp_root="$(mktemp -d)"
  output_file="$(mktemp)"

  cp -Rf \
    "$repo_root/.agents" \
    "$repo_root/.claude" \
    "$repo_root/.claude-plugin" \
    "$repo_root/.codex-plugin" \
    "$repo_root/docs" \
    "$repo_root/hooks" \
    "$repo_root/scripts" \
    "$repo_root/skills" \
    "$repo_root/workflows" \
    "$temp_root/"
  mkdir -p "$temp_root/tests"
  cp -f "$repo_root/tests/validate-skills.sh" "$temp_root/tests/validate-skills.sh"

  for blanket_priming_sentence in "${blanket_priming_sentences[@]}"; do
    python3 - "$temp_root/skills/helix-triage/SKILL.md" "$blanket_priming_sentence" <<'PYEOF'
from pathlib import Path
import sys

path = Path(sys.argv[1])
blanket_priming_sentence = sys.argv[2]
text = path.read_text(encoding="utf-8")
needle = "# Triage: Shape Execution-Ready And Planning Issues\n\n"
replacement = (
    "# Triage: Shape Execution-Ready And Planning Issues\n\n"
    f"{blanket_priming_sentence}\n\n"
)
if needle not in text:
    raise SystemExit("missing helix-triage heading in regression fixture")
path.write_text(text.replace(needle, replacement, 1), encoding="utf-8")
PYEOF

    assert_command_fails \
      "$output_file" \
      "validate-skills must fail when helix-triage regains blanket execution-ready priming" \
      env \
        HELIX_VALIDATE_SKILLS_REPO_ROOT="$temp_root" \
        HELIX_VALIDATE_SKILLS_SKIP_REGRESSION=1 \
        bash "$temp_root/tests/validate-skills.sh"

    regression_output="$(<"$output_file")"
    assert_output_contains \
      "$regression_output" \
      "helix-triage intro must not prime every issue as execution-ready" \
      "validate-skills must report the blanket execution-ready triage regression"

    cp -f "$repo_root/skills/helix-triage/SKILL.md" "$temp_root/skills/helix-triage/SKILL.md"
  done

  rm -rf "$temp_root"
  rm -f "$output_file"
}

# ---------- Plugin layout checks ----------

if command -v python3 >/dev/null 2>&1; then
  python3 "$repo_root/scripts/helix_validate_artifact_meta.py"
else
  fail "python3 is required for artifact metadata validation"
fi

plugin_manifest="$repo_root/.claude-plugin/plugin.json"
[[ -f "$plugin_manifest" ]] || fail "missing plugin manifest at .claude-plugin/plugin.json"
codex_plugin_manifest="$repo_root/.codex-plugin/plugin.json"
[[ -f "$codex_plugin_manifest" ]] || fail "missing Codex plugin manifest at .codex-plugin/plugin.json"
plugin_hooks="$repo_root/hooks/hooks.json"

# Validate plugin.json is parseable JSON with required fields
if command -v python3 &>/dev/null; then
  python3 - "$plugin_manifest" "$codex_plugin_manifest" "$plugin_hooks" <<'PYEOF'
import json, sys
path, codex_path, plugin_hooks = sys.argv[1:4]
try:
    manifest = json.load(open(path))
except json.JSONDecodeError as e:
    print(f"invalid JSON in {path}: {e}", file=sys.stderr)
    sys.exit(1)
required = ("name", "version", "description", "skills")
missing = [k for k in required if not manifest.get(k)]
if missing:
    print(f"plugin.json missing required fields: {', '.join(missing)}", file=sys.stderr)
    sys.exit(1)
if manifest["skills"] != "./skills/":
    print(f"plugin.json skills must be ./skills/ (got {manifest['skills']!r})", file=sys.stderr)
    sys.exit(1)
# Claude Code v2.1.x auto-loads hooks/hooks.json from the standard location.
# Declaring manifest.hooks pointing at that same path causes a duplicate-load
# error and the plugin refuses to install. Reject the field here to prevent
# regression: any future hooks declaration must use a non-standard path.
if "hooks" in manifest and manifest["hooks"] == "./hooks/hooks.json":
    print("plugin.json: manifest.hooks must not duplicate the auto-loaded "
          "./hooks/hooks.json — remove the field or point at an additional path",
          file=sys.stderr)
    sys.exit(1)

try:
    codex_manifest = json.load(open(codex_path))
except json.JSONDecodeError as e:
    print(f"invalid JSON in {codex_path}: {e}", file=sys.stderr)
    sys.exit(1)
allowed_codex_fields = {
    "id",
    "name",
    "version",
    "description",
    "skills",
    "apps",
    "mcpServers",
    "interface",
    "author",
    "homepage",
    "repository",
    "license",
    "keywords",
}
unknown = sorted(set(codex_manifest) - allowed_codex_fields)
if unknown:
    print(f"Codex plugin.json unsupported fields: {', '.join(unknown)}", file=sys.stderr)
    sys.exit(1)
required_codex = ("name", "version", "description", "skills", "author", "interface")
missing = [k for k in required_codex if not codex_manifest.get(k)]
if missing:
    print(f"Codex plugin.json missing required fields: {', '.join(missing)}", file=sys.stderr)
    sys.exit(1)
if codex_manifest["name"] != manifest["name"]:
    print("Codex plugin.json name must match Claude plugin.json name", file=sys.stderr)
    sys.exit(1)
if codex_manifest["version"] != manifest["version"]:
    print("Codex plugin.json version must match Claude plugin.json version", file=sys.stderr)
    sys.exit(1)
if codex_manifest["description"] != manifest["description"]:
    print("Codex plugin.json description must match Claude plugin.json description", file=sys.stderr)
    sys.exit(1)
if codex_manifest["skills"] != "./skills/":
    print(
        f"Codex plugin.json skills must be ./skills/ (got {codex_manifest['skills']!r})",
        file=sys.stderr,
    )
    sys.exit(1)
author = codex_manifest.get("author")
if not isinstance(author, dict) or not author.get("name"):
    print("Codex plugin.json author.name is required", file=sys.stderr)
    sys.exit(1)
interface = codex_manifest.get("interface")
if not isinstance(interface, dict):
    print("Codex plugin.json interface must be an object", file=sys.stderr)
    sys.exit(1)
required_interface = (
    "displayName",
    "shortDescription",
    "longDescription",
    "developerName",
    "category",
    "capabilities",
    "defaultPrompt",
)
missing_interface = [k for k in required_interface if not interface.get(k)]
if missing_interface:
    print(
        "Codex plugin.json interface missing required fields: "
        + ", ".join(missing_interface),
        file=sys.stderr,
    )
    sys.exit(1)
if not isinstance(interface["capabilities"], list) or not all(
    isinstance(value, str) and value.strip() for value in interface["capabilities"]
):
    print("Codex plugin.json interface.capabilities must be an array of strings", file=sys.stderr)
    sys.exit(1)
default_prompt = interface["defaultPrompt"]
if not isinstance(default_prompt, list) or not default_prompt:
    print("Codex plugin.json interface.defaultPrompt must be a non-empty array", file=sys.stderr)
    sys.exit(1)
if len(default_prompt) > 3 or any(
    not isinstance(prompt, str) or not prompt.strip() or len(prompt) > 128
    for prompt in default_prompt
):
    print(
        "Codex plugin.json interface.defaultPrompt entries must be 1-3 non-empty strings at most 128 characters",
        file=sys.stderr,
    )
    sys.exit(1)
# The standard hooks file is optional; when present, validate shape.
import os
if os.path.exists(plugin_hooks):
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

# hooks/hooks.json is optional — Claude Code auto-loads if present.

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
skill_dirs=("$skills_dir"/helix "$skills_dir"/helix-*)
[[ "${#skill_dirs[@]}" -gt 0 ]] || fail "no published skills found under $skills_dir"

mapfile -t expected_skills < <(
  for path in "${skill_dirs[@]}"; do
    [[ -d "$path" ]] || continue
    printf '%s\n' "${path##*/}"
  done | sort
)

# Validate .agents/skills/ symlinks — only HELIX-published skills (helix*).
# Other entries (e.g. ddx-* skills installed by the ddx runtime) are
# runtime artifacts and intentionally ignored here.
mapfile -t agents_published_skills < <(
  for path in "$agents_package_dir"/helix*; do
    [[ -e "$path" || -L "$path" ]] || continue
    printf '%s\n' "${path##*/}"
  done | sort
)

# Validate .claude/skills/ symlinks — only HELIX-published skills (helix*).
mapfile -t claude_published_skills < <(
  for path in "$claude_package_dir"/helix*; do
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
  "$repo_root/skills/helix/SKILL.md" \
  "Use this as the HELIX entrypoint." \
  "helix skill must be the single public HELIX entrypoint"
assert_file_contains \
  "$repo_root/skills/helix/SKILL.md" \
  'Rule: do not add separate public `helix-*` skills' \
  "helix skill must prohibit reintroducing public helix-* skill sprawl"
assert_file_contains \
  "$repo_root/skills/helix/SKILL.md" \
  "Require execution-ready work items to name exact files, commands, checks, fields," \
  "helix polish mode must require explicit measurable acceptance text for execution-ready work items"
assert_file_contains \
  "$repo_root/skills/helix/SKILL.md" \
  "not execution-ready and route it back through planning" \
  "helix polish mode must define a flagging path for non-measurable acceptance text"
assert_file_contains \
  "$repo_root/skills/helix/SKILL.md" \
  "content migration ledger" \
  "helix align mode must require content migration ledger behavior"
assert_file_contains \
  "$repo_root/skills/helix/SKILL.md" \
  "Destination-shaped draft content" \
  "helix content migration ledger must capture destination-shaped content"
assert_file_not_contains \
  "$repo_root/skills/helix/SKILL.md" \
  "compatibility" \
  "helix skill must not describe helix-* compatibility layers"
assert_file_contains \
  "$repo_root/skills/helix/SKILL.md" \
  "### Refresh" \
  "helix skill must have Refresh section under Workflow Contracts"
assert_file_contains \
  "$repo_root/skills/helix/SKILL.md" \
  "## Project Root Resolution" \
  "helix skill must have Project Root Resolution top-level section"
assert_file_contains \
  "$repo_root/skills/helix/SKILL.md" \
  "using the Align taxonomy: \`ALIGNED\`, \`INCOMPLETE\`, \`DIVERGENT\`," \
  "helix skill must list the unified taxonomy in Validate item 5"
assert_file_contains \
  "$repo_root/skills/helix/SKILL.md" \
  "\`UNDERSPECIFIED\`, \`STALE_PLAN\`, or \`BLOCKED\`" \
  "helix skill must list the unified taxonomy in Validate item 5"
assert_file_contains \
  "$repo_root/skills/helix/SKILL.md" \
  "Bring every artifact instance up to date with the current templates and prompts | refresh" \
  "helix skill must have routing row for refresh"
assert_file_contains \
  "$repo_root/workflows/actions/polish.md" \
  "Treat \"works\", \"correct\", \"complete\", \"aligned\", or similar adjectives" \
  "polish action must reject vague non-measurable acceptance wording"
assert_file_contains \
  "$repo_root/workflows/actions/polish.md" \
  "flag the work item as **not execution-ready**" \
  "polish action must define a not-execution-ready flagging path"
assert_file_contains \
  "$repo_root/docs/helix/02-design/contracts/CONTRACT-001-ddx-helix-boundary.md" \
  "HELIX-authored execution beads must make success machine-auditable." \
  "CONTRACT-001 must retain machine-auditable bead success criteria"
command -v python3 >/dev/null 2>&1 || fail "python3 is required for execution-ready bead validation"
mixed_fixture="$repo_root/tests/fixtures/execution-ready-beads/mixed-ready-semantics.jsonl"
mixed_tracker_dir="$(mktemp -d)"
mkdir -p "$mixed_tracker_dir/.ddx"
cp -f "$mixed_fixture" "$mixed_tracker_dir/.ddx/beads.jsonl"
mixed_expected_ids="$(mktemp)"
mixed_actual_ids="$(mktemp)"
DDX_BEAD_DIR="$mixed_tracker_dir/.ddx" ddx bead ready --execution --json >"$mixed_expected_ids"
python3 - "$repo_root/scripts/validate_execution_ready_beads.py" "$mixed_tracker_dir/.ddx/beads.jsonl" >"$mixed_actual_ids" <<'PYEOF'
import importlib.util
import json
import sys
from pathlib import Path

script_path, tracker_path = sys.argv[1:3]
spec = importlib.util.spec_from_file_location("validate_execution_ready_beads", script_path)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)
ready = module.execution_ready_beads(module.load_beads(Path(tracker_path)))
json.dump([bead["id"] for _, bead in ready], sys.stdout)
PYEOF
python3 - "$mixed_expected_ids" "$mixed_actual_ids" <<'PYEOF'
import json
import sys

expected_path, actual_path = sys.argv[1:3]
with open(expected_path, "r", encoding="utf-8") as handle:
    # `ddx bead ready --execution` includes ready epics (deps satisfied), but HELIX's
    # execution-ready contract excludes epics — an epic is a container, you execute its
    # children, not the epic itself (see validate_execution_ready_beads.py + the skip-list
    # below). Filter epics so the oracle matches that contract.
    expected = sorted(
        entry["id"] for entry in json.load(handle) if entry.get("issue_type") != "epic"
    )
with open(actual_path, "r", encoding="utf-8") as handle:
    actual = sorted(json.load(handle))
if expected != actual:
    print(f"expected ready ids {expected}, got {actual}", file=sys.stderr)
    sys.exit(1)
PYEOF
mixed_reject_output="$(mktemp)"
assert_command_fails \
  "$mixed_reject_output" \
  "execution-ready validator should reject only the vague bead from the mixed queue fixture" \
  python3 \
  "$repo_root/scripts/validate_execution_ready_beads.py" \
  "$mixed_fixture"
grep -Fq "hx-ready-vague" "$mixed_reject_output" || fail \
  "mixed execution-ready fixture should identify the ready vague bead"
for skipped_id in hx-deferred-build hx-closed-build hx-ready-epic hx-blocked-build hx-not-execution-eligible hx-superseded-build; do
  if grep -Fq "$skipped_id" "$mixed_reject_output"; then
    fail "mixed execution-ready fixture should skip non-ready bead $skipped_id"
  fi
done
rm -f "$mixed_expected_ids" "$mixed_actual_ids" "$mixed_reject_output"
rm -rf "$mixed_tracker_dir"

reject_output="$(mktemp)"
assert_command_fails \
  "$reject_output" \
  "execution-ready validator should reject vague acceptance fixtures" \
  python3 \
  "$repo_root/scripts/validate_execution_ready_beads.py" \
  "$repo_root/tests/fixtures/execution-ready-beads/vague-acceptance.jsonl"
grep -Fq "hx-vague-ac" "$reject_output" || fail "execution-ready validator should identify the rejected fixture"
rm -f "$reject_output"

flagged_fixture="$repo_root/tests/fixtures/execution-ready-beads/flagged-acceptance.jsonl"
assert_file_contains \
  "$flagged_fixture" \
  "\"execution-eligible\":false" \
  "flagged acceptance fixture must stay marked not execution-ready"
assert_file_contains \
  "$flagged_fixture" \
  "flagged by polish for non-measurable acceptance" \
  "flagged acceptance fixture must record non-measurable acceptance as the reason it is not execution-ready"
flagged_output="$(mktemp)"
python3 "$repo_root/scripts/validate_execution_ready_beads.py" \
  "$flagged_fixture" \
  >"$flagged_output" 2>&1
grep -Fq "validated measurable acceptance on 0 execution-ready bead(s)" "$flagged_output" || fail \
  "flagged acceptance fixture should be skipped once it is marked not execution-ready"
rm -f "$flagged_output"

# Assert every path SKILL.md instructs the runtime to load actually exists in
# the shipped tree. Catches drift like "SKILL.md references library/foo.yml
# but only family-test/library/foo.yml is shipped" — a defect that lets the
# plugin install while leaving the skill unable to load its resources at
# runtime.
python3 - "$repo_root/skills/helix/SKILL.md" "$repo_root" <<'PYEOF' || fail "SKILL.md references a path that does not exist in the shipped tree"
import re, sys
skill_path, repo_root = sys.argv[1], sys.argv[2]
text = open(skill_path).read()
# Patterns the skill instructs the runtime to load. Only check repo-relative
# paths the agent is told to Read; skip operator-only paths (docs/helix/...
# which lives in the user's project, not the plugin) and in-text examples.
# The `references/` floor ships beside SKILL.md so §Catalog Resolution always
# resolves a graph/template in plugin installs that package only ./skills/; it
# is a synced copy of the workflows/ catalog, kept in lockstep by the
# sync_references.py diff check below.
required = {
    "library/skill-prompts/stop-at-triggers.yml",
    "workflows/concerns/slots.yml",
    "workflows/concerns/verification/practices.md",
    "workflows/concerns/sample-data/practices.md",
    "workflows/graph.yml",
    "workflows/voice.yml",
}
import os
missing = [p for p in required if not os.path.exists(os.path.join(repo_root, p))]
# Also assert each path appears verbatim in SKILL.md — guards against the
# reverse drift (we ship a file, SKILL.md stops referencing it).
not_referenced = [p for p in required if p not in text]
if missing:
    print(f"SHIPPING DEFECT — SKILL.md references these paths but they do not exist in the shipped tree: {missing}", file=sys.stderr)
if not_referenced:
    print(f"DRIFT — these paths exist in the shipped tree but are no longer referenced by SKILL.md: {not_referenced}", file=sys.stderr)
sys.exit(1 if (missing or not_referenced) else 0)
PYEOF

# workflows/graph.yml drift: regenerate from meta.yml into a temp file and diff
# against the committed copy. Catches "meta.yml relationships.informs changed
# but graph.yml wasn't regenerated."
graph_tmp="$(mktemp)"
python3 - "$repo_root" "$graph_tmp" <<'PYEOF' || fail "workflows/graph.yml is stale — run scripts/generate_graph.py"
import subprocess, sys, shutil, os, filecmp
repo_root, tmp = sys.argv[1], sys.argv[2]
# Run generator with output redirected to tmp via env-side-channel: easiest is
# to invoke it normally then move the result.
backup = tmp + ".committed"
shutil.copy(os.path.join(repo_root, "workflows", "graph.yml"), backup)
subprocess.check_call([sys.executable, os.path.join(repo_root, "scripts", "generate_graph.py")],
                      stderr=subprocess.DEVNULL)
generated = os.path.join(repo_root, "workflows", "graph.yml")
if not filecmp.cmp(backup, generated, shallow=False):
    # Restore committed version so the working tree isn't dirtied by the check.
    shutil.copy(backup, generated)
    print("DRIFT: workflows/graph.yml does not match what scripts/generate_graph.py would emit from current meta.yml", file=sys.stderr)
    sys.exit(1)
PYEOF
rm -f "$graph_tmp" "$graph_tmp.committed"

# skills/helix/references/ floor sync: the committed floor MUST be an exact copy
# of the workflows/ catalog. Re-sync into a temp dir and diff bidirectionally
# (diff -r reports files present on only one side too), catching both drift and
# orphaned/missing floor files. Run the graph generator first so the floor's
# graph.yml is compared against the freshly-generated workflows/graph.yml.
ref_tmp="$(mktemp -d)"
if ! python3 "$repo_root/scripts/sync_references.py" "$ref_tmp" >/dev/null; then
  rm -rf "$ref_tmp"
  fail "sync_references.py failed"
fi
if ! diff -r "$ref_tmp" "$repo_root/skills/helix/references" >/dev/null 2>&1; then
  rm -rf "$ref_tmp"
  fail "skills/helix/references/ is out of sync with workflows/ — run: python3 scripts/sync_references.py"
fi
rm -rf "$ref_tmp"

# Canonical SKILL.md frontmatter check: enforce agentskills.io spec AND the
# runtime-specific limits we hit in benchmarking:
#   - codex: description max 1024 chars (HARD: codex refuses to load over)
#   - claude-code: 1024 recommended
# v0.2.2 of helix had a 1670-char description that broke every codex
# routing-eval call. This guard catches that class of regression.
#
# Targets the canonical install at skills/helix/SKILL.md (post canonical-
# promotion; the family-test/methodology-* research fork was removed).
python3 - "$repo_root" <<'PYEOF' || fail "canonical SKILL.md frontmatter check failed"
import sys, yaml, glob, os
repo_root = sys.argv[1]
patterns = [
    os.path.join(repo_root, "skills", "*", "SKILL.md"),
]
errors = []
checked = 0
for pat in patterns:
    for path in glob.glob(pat):
        checked += 1
        text = open(path).read()
        if not text.startswith("---\n"):
            errors.append(f"{path}: missing frontmatter")
            continue
        end = text.find("\n---\n", 4)
        if end == -1:
            errors.append(f"{path}: unterminated frontmatter")
            continue
        try:
            fm = yaml.safe_load(text[4:end])
        except yaml.YAMLError as e:
            errors.append(f"{path}: YAML parse error: {e}")
            continue
        if not isinstance(fm, dict):
            errors.append(f"{path}: frontmatter is not a mapping")
            continue
        name = fm.get("name", "")
        desc = fm.get("description", "")
        expected_name = os.path.basename(os.path.dirname(path))
        if name != expected_name:
            errors.append(f"{path}: name '{name}' != dir basename '{expected_name}'")
        if not desc:
            errors.append(f"{path}: description is empty")
            continue
        n = len(desc)
        if n > 1024:
            errors.append(f"{path}: description {n} chars exceeds 1024 (codex hard limit, claude-code recommended limit)")
        if n < 1:
            errors.append(f"{path}: description must be 1..1024 chars (got {n})")
print(f"checked {checked} canonical SKILL.md file(s)")
if errors:
    for e in errors:
        print(f"  FAIL: {e}", file=sys.stderr)
    sys.exit(1)
PYEOF

printf 'validated %d HELIX skills\n' "${#expected_skills[@]}"
