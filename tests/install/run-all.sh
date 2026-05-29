#!/usr/bin/env bash
# Run every per-runtime install scenario.
#
# - Loads .env if present.
# - Builds each Docker image (or runs Python for Genie).
# - Runs install.sh then verify.sh in each container.
# - When `vhs` is on PATH, also captures terminal screencasts.
#
# Exit code is the number of failed scenarios (0 = all pass).

set -uo pipefail

cd "$(dirname "$0")"
TESTS_DIR="$PWD"

if [[ -f ".env" ]]; then
  set -a; source .env; set +a
fi

VHS=""
if command -v vhs >/dev/null 2>&1; then VHS=1; fi

DOCKER=""
if command -v docker >/dev/null 2>&1; then DOCKER=1; fi

# Terminal scenarios (Docker-based)
TERMINAL_SCENARIOS=(ddx claude-code codex-cli copilot-cli)

failed=0

run_terminal_scenario() {
  local name="$1"
  local dir="$TESTS_DIR/$name"
  echo
  echo "============================================================"
  echo "scenario: $name"
  echo "============================================================"
  if [[ -z "$DOCKER" ]]; then
    echo "SKIP: docker not on PATH"
    failed=$((failed + 1))
    return
  fi
  if [[ ! -f "$dir/Dockerfile" ]]; then
    echo "SKIP: $dir/Dockerfile not found"
    failed=$((failed + 1))
    return
  fi

  local image="helix-install-test:$name"
  if ! docker build -t "$image" "$dir"; then
    echo "FAIL: docker build for $name"
    failed=$((failed + 1))
    return
  fi

  # Pass auth env into container so functional checks can run when gated.
  # TEST_PUBLISHED switches a scenario to the real published-marketplace install.
  local env_args=()
  for v in ANTHROPIC_API_KEY OPENAI_API_KEY GH_TOKEN DATABRICKS_HOST DATABRICKS_TOKEN DATABRICKS_PROFILE TEST_FUNCTIONAL TEST_PUBLISHED; do
    if [[ -n "${!v:-}" ]]; then env_args+=(-e "$v=${!v}"); fi
  done

  # Mount the repo root so install.sh can use the local source.
  if ! docker run --rm "${env_args[@]}" \
      -v "$TESTS_DIR/../..:/workspace/helix:ro" \
      "$image"; then
    echo "FAIL: scenario $name (install or verify exit non-zero)"
    failed=$((failed + 1))
    return
  fi

  if [[ -n "$VHS" && -f "$dir/record.tape" ]]; then
    echo "recording $name screencast..."
    (cd "$dir" && vhs record.tape) || echo "WARN: vhs recording failed for $name"
  fi

  echo "PASS: $name"
}

for scenario in "${TERMINAL_SCENARIOS[@]}"; do
  run_terminal_scenario "$scenario"
done

# Genie scenario: not Docker. Calls scripts directly.
echo
echo "============================================================"
echo "scenario: genie"
echo "============================================================"
if [[ -z "${DATABRICKS_HOST:-}" || -z "${DATABRICKS_TOKEN:-}" ]] && [[ -z "${DATABRICKS_PROFILE:-}" ]]; then
  if [[ "${TEST_GENIE:-}" == "1" ]]; then
    echo "FAIL: TEST_GENIE=1 but Databricks credentials not set"
    failed=$((failed + 1))
  else
    echo "SKIP: Databricks credentials not set (set TEST_GENIE=1 to require)"
  fi
else
  if python3 "$TESTS_DIR/genie/install.py" && python3 "$TESTS_DIR/genie/verify.py"; then
    echo "PASS: genie install + verify"
  else
    echo "FAIL: genie scenario"
    failed=$((failed + 1))
  fi
fi

echo
echo "============================================================"
echo "summary: $failed scenario(s) failed"
echo "============================================================"
exit "$failed"
