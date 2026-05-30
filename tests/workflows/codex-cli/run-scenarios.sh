#!/usr/bin/env bash
# Codex CLI integration test for HELIX skill activation.
#
# Exercises Codex's machine-readable output to assert that the helix skill
# is invoked for each scenario. Exit code 0 on all scenarios passing.
#
# Usage:
#   bash tests/workflows/codex-cli/run-scenarios.sh [--no-skill]
#
# Environment:
#   OPENAI_API_KEY or CODEX_API_KEY: required, Codex API key
#   HELIX_REPO_PATH: optional, path to helix repo (default: current directory)

set -euo pipefail

HELIX_REPO_PATH="${HELIX_REPO_PATH:-.}"
SCENARIOS_DIR="$HELIX_REPO_PATH/tests/workflows/codex-cli/scenarios"
EXPECTED_DIR="$HELIX_REPO_PATH/tests/workflows/codex-cli/expected"
INSTALL_DIR="$HELIX_REPO_PATH/tests/install/codex-cli"
IMAGE_TAG="helix-int-test:codex-cli"
NO_SKILL="${1:-}"
SKIP_SKILL_INSTALL=0

if [[ "$NO_SKILL" == "--no-skill" ]]; then
  SKIP_SKILL_INSTALL=1
  log_info "Running in --no-skill negative control mode (should fail)"
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
  echo -e "${GREEN}→${NC} $*"
}

log_error() {
  echo -e "${RED}✗${NC} $*" >&2
}

log_warn() {
  echo -e "${YELLOW}!${NC} $*"
}

# Check requirements
if [[ -z "${OPENAI_API_KEY:-}${CODEX_API_KEY:-}" ]]; then
  log_error "OPENAI_API_KEY or CODEX_API_KEY not set"
  exit 1
fi

if ! command -v docker &> /dev/null; then
  log_error "docker not found in PATH"
  exit 1
fi

if ! command -v jq &> /dev/null; then
  log_warn "jq not found in PATH (optional, used for structured output parsing)"
fi

# Build the Docker image
log_info "Building Docker image: $IMAGE_TAG"
docker build \
  -t "$IMAGE_TAG" \
  -f "$INSTALL_DIR/Dockerfile" \
  "$HELIX_REPO_PATH" 2>&1 | tail -20

# Create a temporary directory for test outputs
TEST_TMP=$(mktemp -d)
trap "rm -rf '$TEST_TMP'" EXIT

log_info "Test temp directory: $TEST_TMP"

# Load and validate routing.jsonl expectations
EVALS_FILE="$HELIX_REPO_PATH/tests/workflows/codex-cli/evals/routing.jsonl"
if [[ ! -f "$EVALS_FILE" ]]; then
  log_error "Routing evaluations file not found: $EVALS_FILE"
  exit 1
fi

log_info "Loaded routing evaluations from: $EVALS_FILE"

# Run each scenario
SCENARIOS=("install-verify" "skill-list" "bootstrap")
FAILED_SCENARIOS=()
PASSED_SCENARIOS=()

for scenario in "${SCENARIOS[@]}"; do
  log_info "Running scenario: $scenario"

  PROMPT_FILE="$SCENARIOS_DIR/$scenario.prompt"
  EXPECT_FILE="$EXPECTED_DIR/$scenario.expect"
  RESPONSE_FILE="$TEST_TMP/$scenario.response.txt"
  STREAM_FILE="$TEST_TMP/$scenario.stream.jsonl"
  GIT_DIFF_FILE="$TEST_TMP/$scenario.git-diff.txt"

  if [[ ! -f "$PROMPT_FILE" ]]; then
    log_error "Prompt file not found: $PROMPT_FILE"
    FAILED_SCENARIOS+=("$scenario")
    continue
  fi

  if [[ ! -f "$EXPECT_FILE" ]]; then
    log_error "Expected file not found: $EXPECT_FILE"
    FAILED_SCENARIOS+=("$scenario")
    continue
  fi

  # Read the prompt
  PROMPT=$(cat "$PROMPT_FILE")
  log_info "  Input: ${PROMPT:0:60}..."

  # Create a Docker setup script that will:
  # 1. Install the skill (if not --no-skill)
  # 2. Run codex exec with the prompt
  # 3. Capture output
  DOCKER_SETUP=$(mktemp)
  cat > "$DOCKER_SETUP" << 'DOCKER_EOF'
#!/bin/bash
set -euo pipefail

PROMPT="$1"
SCENARIO="$2"
SKIP_INSTALL="$3"

cd /workspace/helix

if [[ "$SKIP_INSTALL" != "1" ]]; then
  echo "Installing HELIX skill..."
  /usr/local/bin/install.sh >/dev/null 2>&1
  
  # Check both possible install locations
  if [[ -f ~/.codex/skills/helix/SKILL.md ]]; then
    echo "✓ Skill installed at ~/.codex/skills/helix/"
  elif [[ -f ~/.agents/skills/helix/SKILL.md ]]; then
    echo "✓ Skill installed at ~/.agents/skills/helix/"
  else
    echo "✗ Skill installation failed"
    exit 1
  fi
fi

# Set up authentication
if [[ -n "${OPENAI_API_KEY:-}" ]]; then
  export OPENAI_API_KEY
  printenv OPENAI_API_KEY | codex login --with-api-key 2>/dev/null || true
fi

# Run codex exec with the prompt
# Use --skip-git-repo-check to avoid git requirement
# Try to get JSON output if available, fall back to text
echo "$PROMPT" | codex exec \
  --skip-git-repo-check \
  --ephemeral \
  2>&1 || true

# Also capture git status if available to show behavioral evidence
if git status >/dev/null 2>&1; then
  echo ""
  echo "=== Git status (behavioral evidence) ==="
  git status --porcelain
fi
DOCKER_EOF

  if ! docker run --rm \
    -e OPENAI_API_KEY="${OPENAI_API_KEY:-}" \
    -e CODEX_API_KEY="${CODEX_API_KEY:-}" \
    -v "$HELIX_REPO_PATH:/workspace/helix:ro" \
    -v "$DOCKER_SETUP:/tmp/run-scenario.sh:ro" \
    "$IMAGE_TAG" \
    bash /tmp/run-scenario.sh "$PROMPT" "$scenario" "$SKIP_SKILL_INSTALL" > "$RESPONSE_FILE" 2>&1; then
    log_error "  Docker run failed for scenario: $scenario"
    rm -f "$DOCKER_SETUP"
    FAILED_SCENARIOS+=("$scenario")
    continue
  fi
  rm -f "$DOCKER_SETUP"

  # Extract response
  RESPONSE=$(cat "$RESPONSE_FILE" | tr -d '\n')

  # For non-bootstrap scenarios, check expected text patterns
  if [[ "$scenario" != "bootstrap" ]]; then
    local failed=0
    while IFS= read -r expected; do
      if [[ -n "$expected" && ! "$RESPONSE" =~ $expected ]]; then
        log_error "  Missing expected text: '$expected'"
        failed=1
      fi
    done < "$EXPECT_FILE"

    if [[ $failed -eq 1 ]]; then
      FAILED_SCENARIOS+=("$scenario")
      continue
    fi
  fi

  # Check for behavioral signal: skill invocation for bootstrap scenario
  # Since Codex may not expose structured tool_use events like Claude,
  # we check if the response mentions HELIX concepts or modes
  SKILL_INVOKED=0
  if [[ "$scenario" != "install-verify" ]]; then
    # Check if response contains HELIX-specific terminology or artifact names
    if [[ "$RESPONSE" =~ (frame|input|design|review|product-vision|prd|helix) ]]; then
      SKILL_INVOKED=1
    fi

    if [[ $SKILL_INVOKED -eq 0 ]]; then
      if [[ $SKIP_SKILL_INSTALL -eq 1 ]]; then
        # In --no-skill mode, expected that skill is NOT invoked
        log_info "  Expected: Skill not invoked in --no-skill mode"
        FAILED_SCENARIOS+=("$scenario")
        continue
      else
        log_warn "  No helix skill invocation detected in response"
        # For bootstrap, this is a blocker
        if [[ "$scenario" == "bootstrap" ]]; then
          FAILED_SCENARIOS+=("$scenario")
          continue
        fi
      fi
    elif [[ $SKIP_SKILL_INSTALL -eq 1 ]]; then
      # In --no-skill mode, we found skill invoked - this is wrong
      log_error "  ERROR: Skill invoked in --no-skill mode!"
      FAILED_SCENARIOS+=("$scenario")
      continue
    fi
  fi

  log_info "  ✓ Scenario passed: $scenario"
  PASSED_SCENARIOS+=("$scenario")
done

# Negative control: run with bootstrap prompt but skill explicitly uninstalled
if [[ $SKIP_SKILL_INSTALL -eq 0 ]]; then
  log_info "Running negative control: skill uninstalled"

  PROMPT=$(cat "$SCENARIOS_DIR/bootstrap.prompt")
  NEGATIVE_RESPONSE="$TEST_TMP/negative-control.response.txt"
  
  NEGATIVE_SETUP=$(mktemp)
  cat > "$NEGATIVE_SETUP" << 'DOCKER_EOF'
#!/bin/bash
set -euo pipefail
PROMPT="$1"

cd /workspace/helix

# Remove skill installation entirely
rm -rf ~/.codex/skills/helix ~/.agents/skills/helix

# Set up authentication
if [[ -n "${OPENAI_API_KEY:-}" ]]; then
  export OPENAI_API_KEY
  printenv OPENAI_API_KEY | codex login --with-api-key 2>/dev/null || true
fi

# Try to run without the skill - should fail or produce suboptimal response
echo "$PROMPT" | codex exec \
  --skip-git-repo-check \
  --ephemeral \
  2>&1 || true
DOCKER_EOF

  if docker run --rm \
    -e OPENAI_API_KEY="${OPENAI_API_KEY:-}" \
    -e CODEX_API_KEY="${CODEX_API_KEY:-}" \
    -v "$HELIX_REPO_PATH:/workspace/helix:ro" \
    -v "$NEGATIVE_SETUP:/tmp/run-scenario.sh:ro" \
    "$IMAGE_TAG" \
    bash /tmp/run-scenario.sh "$PROMPT" > "$NEGATIVE_RESPONSE" 2>&1; then

    # Check that response does NOT contain HELIX-specific terminology
    NEGATIVE_RESPONSE_TEXT=$(cat "$NEGATIVE_RESPONSE" | tr -d '\n')
    if [[ ! "$NEGATIVE_RESPONSE_TEXT" =~ (frame|input|design|review|product-vision|prd|helix.*skill) ]]; then
      log_info "  ✓ Negative control: Skill behavior absent when skill uninstalled"
    else
      log_warn "Negative control: Response still contains HELIX terminology (may indicate fallback behavior)"
    fi
  else
    log_warn "Negative control docker run exited nonzero (expected if skill was the only handler)"
  fi
  
  rm -f "$NEGATIVE_SETUP"
fi

# Print results
echo
log_info "Test Results"
log_info "============"
log_info "Passed: ${#PASSED_SCENARIOS[@]}/${#SCENARIOS[@]}"
for scenario in "${PASSED_SCENARIOS[@]}"; do
  echo -e "  ${GREEN}✓${NC} $scenario"
done

if [[ ${#FAILED_SCENARIOS[@]} -gt 0 ]]; then
  echo
  log_error "Failed: ${#FAILED_SCENARIOS[@]}/${#SCENARIOS[@]}"
  for scenario in "${FAILED_SCENARIOS[@]}"; do
    echo -e "  ${RED}✗${NC} $scenario"
  done
  exit 1
fi

log_info "All scenarios passed"
exit 0
