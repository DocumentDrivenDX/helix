#!/usr/bin/env bash
# SCN-01 assertion checks: verify routing decision and artifact production.
#
# Invoked by run-scenarios.sh after `ddx work --once --json`.
# Argument 1: result.json path
# Argument 2: workspace root (where artifacts should be)

set -euo pipefail

RESULT_FILE="${1:?result.json path required}"
WORKSPACE_ROOT="${2:?workspace root required}"

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

pass() {
  echo -e "${GREEN}✓${NC} $*"
}

fail() {
  echo -e "${RED}✗${NC} $*" >&2
  exit 1
}

# Assertion 1: Bead execution and routing decision
if ! jq -e '.results[0].bead_id' "$RESULT_FILE" > /dev/null 2>&1; then
  fail "No bead execution in result.json"
fi
BEAD_ID=$(jq -r '.results[0].bead_id' "$RESULT_FILE")

# Find execution directory and check manifest
EXECUTION_DIR=$(ls -td "$WORKSPACE_ROOT/.ddx/executions"/* 2>/dev/null | head -1)
if [[ -z "$EXECUTION_DIR" ]]; then
  fail "No execution directory found in .ddx/executions/"
fi

if [[ ! -f "$EXECUTION_DIR/manifest.json" ]]; then
  fail "Manifest not found in execution directory"
fi

HARNESS=$(jq -r '.harness' "$EXECUTION_DIR/manifest.json")
MODEL=$(jq -r '.model' "$EXECUTION_DIR/manifest.json")
ROUTE="$HARNESS/$MODEL"

pass "Routing decision recorded: $ROUTE"

# Assertion 2: Artifact paths exist
VISION_FILE="$WORKSPACE_ROOT/docs/helix/00-discover/product-vision.md"
PRD_FILE="$WORKSPACE_ROOT/docs/helix/01-frame/prd.md"

if [[ ! -f "$VISION_FILE" ]]; then
  fail "product-vision.md not found at $VISION_FILE"
fi
pass "product-vision.md exists"

if [[ ! -f "$PRD_FILE" ]]; then
  fail "prd.md not found at $PRD_FILE"
fi
pass "prd.md exists"

# Assertion 3: Frontmatter validation
if ! grep -q "^ddx:" "$VISION_FILE"; then
  fail "product-vision.md missing ddx: frontmatter"
fi
pass "product-vision.md has ddx: frontmatter"

if ! grep -q "^ddx:" "$PRD_FILE"; then
  fail "prd.md missing ddx: frontmatter"
fi
pass "prd.md has ddx: frontmatter"

# Assertion 4: Required sections
for section in "## Problem Space" "## Vision Statement"; do
  if ! grep -F "$section" "$VISION_FILE" > /dev/null; then
    fail "product-vision.md missing section: $section"
  fi
done
pass "product-vision.md contains required sections"

for section in "## Overview" "## User Personas" "## Features" "## Success Metrics"; do
  if ! grep -F "$section" "$PRD_FILE" > /dev/null; then
    fail "prd.md missing section: $section"
  fi
done
pass "prd.md contains required sections"

# Assertion 5: Dependency edge
if ! grep -q "depends_on.*helix.product-vision" "$PRD_FILE"; then
  fail "prd.md missing depends_on: [helix.product-vision]"
fi
pass "prd.md records dependency on product-vision"

echo
echo "All assertions passed."
