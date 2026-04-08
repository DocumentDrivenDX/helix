#!/usr/bin/env bash
# Integration test: ddx install helix produces a working plugin
#
# Verifies that after running `ddx install helix --local <repo>`:
#   - skills are symlinked into HOME/.agents/skills and HOME/.claude/skills
#   - scripts/helix is copied to HOME/.local/bin/helix
#   - helix help works
#   - helix doctor passes (with mock agent and --fix for project-level setup)
#
# The test uses a temporary HOME for isolation. Because `ddx install helix
# --local` also overwrites the project-level .agents/skills and .claude/skills
# symlinks with absolute paths, the cleanup handler restores them to the
# canonical relative form (../../skills/<name>) so validate-skills.sh is
# not broken by this test.

set -euo pipefail

export DDX_DISABLE_UPDATE_CHECK=1

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

fail() {
  printf 'FAIL: %s\n' "$*" >&2
  exit 1
}

pass() {
  printf 'PASS: %s\n' "$*"
}

assert_symlink() {
  local path="$1"
  local label="$2"
  [[ -L "$path" ]] || fail "$label: expected symlink at $path"
  pass "$label"
}

assert_executable() {
  local path="$1"
  local label="$2"
  [[ -f "$path" && -x "$path" ]] || fail "$label: expected executable file at $path"
  pass "$label"
}

assert_output_contains() {
  local haystack="$1"
  local needle="$2"
  local label="$3"
  [[ "$haystack" == *"$needle"* ]] || {
    printf 'expected substring: %s\nin:\n%s\n' "$needle" "$haystack" >&2
    fail "$label"
  }
  pass "$label"
}

assert_output_not_contains() {
  local haystack="$1"
  local needle="$2"
  local label="$3"
  [[ "$haystack" != *"$needle"* ]] || {
    printf 'unexpected substring: %s\nin:\n%s\n' "$needle" "$haystack" >&2
    fail "$label"
  }
  pass "$label"
}

# ── Setup ────────────────────────────────────────────────────────────────────

INSTALL_HOME="$(mktemp -d)"
PROJECT_DIR="$(mktemp -d)"
MOCK_BIN="$(mktemp -d)"

# Restore project-level .agents/skills and .claude/skills symlinks to the
# canonical relative form after ddx install overwrites them with absolute paths.
restore_skill_symlinks() {
  local skills_src="$repo_root/skills"
  local agents_dir="$repo_root/.agents/skills"
  local claude_dir="$repo_root/.claude/skills"
  for skill_src in "$skills_src"/helix-*/SKILL.md; do
    [[ -e "$skill_src" ]] || continue
    local name
    name="$(basename "$(dirname "$skill_src")")"
    local rel="../../skills/$name"
    ln -sfn "$rel" "$agents_dir/$name" 2>/dev/null || true
    ln -sfn "$rel" "$claude_dir/$name" 2>/dev/null || true
  done
}

cleanup() {
  restore_skill_symlinks
  rm -rf "$INSTALL_HOME" "$PROJECT_DIR" "$MOCK_BIN"
}
trap cleanup EXIT

# Create a minimal mock agent binary so helix doctor's agent-CLI check passes.
cat >"$MOCK_BIN/claude" <<'EOF'
#!/usr/bin/env bash
echo "claude mock 0.0.0 (test)"
EOF
chmod +x "$MOCK_BIN/claude"

# Initialise a bare git repository to serve as the target project directory.
git -C "$PROJECT_DIR" init -q
git -C "$PROJECT_DIR" config user.email "ci@helix.test"
git -C "$PROJECT_DIR" config user.name "HELIX CI"

# ── Step 1: run ddx install helix in isolated HOME ────────────────────────

install_output="$(HOME="$INSTALL_HOME" ddx install helix --local "$repo_root" --force 2>&1)"
printf '%s\n' "$install_output"

# ── Step 2: verify skill symlinks ─────────────────────────────────────────

skill_count=0
for skill_src in "$repo_root/skills"/helix-*/SKILL.md; do
  [[ -e "$skill_src" ]] || continue
  skill_name="$(basename "$(dirname "$skill_src")")"

  assert_symlink "$INSTALL_HOME/.agents/skills/$skill_name" \
    "skill symlink .agents/skills/$skill_name"
  assert_symlink "$INSTALL_HOME/.claude/skills/$skill_name" \
    "skill symlink .claude/skills/$skill_name"
  skill_count=$((skill_count + 1))
done

[[ "$skill_count" -gt 0 ]] || fail "no skills found in repo — expected at least one helix-* skill"
pass "all $skill_count skills symlinked in both .agents/skills and .claude/skills"

# ── Step 3: verify helix binary was copied to bin ────────────────────────

helix_bin="$INSTALL_HOME/.local/bin/helix"
assert_executable "$helix_bin" "helix binary at HOME/.local/bin/helix"

# Confirm the binary is not a symlink — ddx install copies it
[[ ! -L "$helix_bin" ]] || fail "helix binary should be a copy, not a symlink, at $helix_bin"
pass "helix binary is a real file (not a symlink)"

# ── Step 4: verify helix help works ──────────────────────────────────────

help_output="$(
  HOME="$INSTALL_HOME" \
  PATH="$MOCK_BIN:$PATH" \
  HELIX_ROOT="$repo_root" \
  DDX_DISABLE_UPDATE_CHECK=1 \
  "$helix_bin" help 2>&1
)"
assert_output_contains "$help_output" "helix run" "helix help lists 'run' command"
assert_output_contains "$help_output" "helix doctor" "helix help lists 'doctor' command"
assert_output_contains "$help_output" "Usage:" "helix help includes Usage header"

# ── Step 5: verify helix doctor passes ───────────────────────────────────
#
# Run `helix doctor --fix` first to create per-project symlinks, then
# run `helix doctor` (without --fix) and assert it exits 0 with no FAILURES.
#
# HELIX_ROOT points the installed binary to the workflows directory in
# the source checkout so workflows can be found.

doctor_fix_output="$(
  cd "$PROJECT_DIR"
  HOME="$INSTALL_HOME" \
  PATH="$MOCK_BIN:$PATH" \
  HELIX_ROOT="$repo_root" \
  DDX_DISABLE_UPDATE_CHECK=1 \
  "$helix_bin" doctor --fix 2>&1
)"
printf '%s\n' "$doctor_fix_output"

doctor_output="$(
  cd "$PROJECT_DIR"
  HOME="$INSTALL_HOME" \
  PATH="$MOCK_BIN:$PATH" \
  HELIX_ROOT="$repo_root" \
  DDX_DISABLE_UPDATE_CHECK=1 \
  "$helix_bin" doctor 2>&1
)" && doctor_rc=0 || doctor_rc=$?

printf '%s\n' "$doctor_output"

assert_output_contains "$doctor_output" "workflows" "helix doctor checks workflows"
assert_output_not_contains "$doctor_output" "FAILURES" "helix doctor reports no FAILURES"
[[ "$doctor_rc" -eq 0 ]] || fail "helix doctor exited with non-zero status $doctor_rc"
pass "helix doctor exits 0"

printf '\ninstall integration test: all checks passed\n'
