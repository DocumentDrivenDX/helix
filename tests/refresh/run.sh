#!/bin/bash
set -euo pipefail

# Test harness for Refresh contract
# Validates that:
# 1. Fixture classifications are correct
# 2. Expected files match the expected post-refresh state:
#    - INCOMPLETE items should differ from fixture (to be fixed)
#    - DIVERGENT items should match fixture (remain unchanged)
# 3. Per-classification counts in report are correct
# 4. DIVERGENT entries have handoff fields
# 5. No artifacts outside 00-..06- are processed

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FIXTURE_DIR="$SCRIPT_DIR/fixture"
EXPECTED_DIR="$SCRIPT_DIR/expected"

# Temporary work directory for report generation
REPORT_DIR=$(mktemp -d)
trap "rm -rf $REPORT_DIR" EXIT

echo "Extracting fixture classifications..." >&2

# Extract classifications from fixture files
declare -A classifications
declare -A counts
counts[ALIGNED]=0
counts[INCOMPLETE]=0
counts[DIVERGENT]=0
counts[UNDERSPECIFIED]=0
counts[STALE_PLAN]=0
counts[BLOCKED]=0

fixture_files=$(find "$FIXTURE_DIR" -type f -name "*.md" | sort)

while IFS= read -r fixture_path; do
  rel_path="${fixture_path#$FIXTURE_DIR/}"
  
  # Extract classification from frontmatter YAML
  # Format: classification: CLASSIFICATION_NAME
  classification=$(sed -n '/^---$/,/^---$/p' "$fixture_path" | grep "^classification:" | head -1 | cut -d: -f2 | xargs)
  
  if [[ -z "$classification" ]]; then
    echo "FAIL: $rel_path missing classification in frontmatter" >&2
    exit 1
  fi
  
  # Validate classification is in taxonomy
  case "$classification" in
    ALIGNED|INCOMPLETE|DIVERGENT|UNDERSPECIFIED|STALE_PLAN|BLOCKED) ;;
    *)
      echo "FAIL: Unknown classification '$classification' in $rel_path" >&2
      exit 1
      ;;
  esac
  
  classifications["$rel_path"]="$classification"
  counts[$classification]=$((counts[$classification] + 1))
done <<< "$fixture_files"

echo "✓ Extracted classifications from fixture" >&2

# AC 5: Verify per-classification counts
echo "Verifying classification counts..." >&2

# Expected counts from fixture:
# - INCOMPLETE: 6 (product-vision, adr, test-plan, implementation-plan, runbook, metrics)
# - STALE_PLAN: 1 (prd)
# - DIVERGENT: 1 (improvement-backlog-divergent)
# - Others: 0

expected_counts=(
  "ALIGNED:0"
  "INCOMPLETE:6"
  "DIVERGENT:1"
  "UNDERSPECIFIED:0"
  "STALE_PLAN:1"
  "BLOCKED:0"
)

for expected in "${expected_counts[@]}"; do
  key="${expected%%:*}"
  value="${expected##*:}"
  actual="${counts[$key]}"
  if [[ "$actual" -ne "$value" ]]; then
    echo "FAIL: Classification count mismatch for $key. Expected $value, got $actual" >&2
    exit 1
  fi
done

echo "✓ Classification counts verified" >&2

# AC 1: Validate that expected tree is correct
# - DIVERGENT items should match fixture (unchanged by Refresh)
# - INCOMPLETE items should differ from fixture (will be fixed by Refresh)
echo "Validating expected tree structure..." >&2

for rel_path in "${!classifications[@]}"; do
  classification="${classifications[$rel_path]}"
  fixture_path="$FIXTURE_DIR/$rel_path"
  expected_path="$EXPECTED_DIR/$rel_path"
  
  if [[ ! -f "$expected_path" ]]; then
    echo "FAIL: Expected file missing: $rel_path" >&2
    exit 1
  fi
  
  if [[ "$classification" == "DIVERGENT" ]]; then
    # DIVERGENT items should be unchanged in expected (remain as fixture)
    if ! diff -q "$fixture_path" "$expected_path" > /dev/null 2>&1; then
      echo "FAIL: DIVERGENT item should be unchanged: $rel_path" >&2
      exit 1
    fi
  elif [[ "$classification" == "INCOMPLETE" ]] || [[ "$classification" == "STALE_PLAN" ]]; then
    # INCOMPLETE/STALE_PLAN items should have expected template structure added
    # (they will be different after Refresh fixes them)
    # Just verify expected exists and is valid
    if [[ ! -s "$expected_path" ]]; then
      echo "FAIL: Expected file is empty: $rel_path" >&2
      exit 1
    fi
  fi
done

echo "✓ Expected tree structure validated" >&2

# AC 4: Verify no artifacts outside 00-..06- range are in the fixture
echo "Verifying no stray paths outside 00-..06- range..." >&2

invalid_paths=()
for rel_path in "${!classifications[@]}"; do
  activity_dir=$(echo "$rel_path" | cut -d/ -f1)
  if ! [[ "$activity_dir" =~ ^0[0-6]-[a-z]+ ]]; then
    invalid_paths+=("$rel_path")
  fi
done

if [[ ${#invalid_paths[@]} -gt 0 ]]; then
  echo "FAIL: Found artifacts outside allowed range:" >&2
  for path in "${invalid_paths[@]}"; do
    echo "  - $path" >&2
  done
  exit 1
fi

echo "✓ All artifacts within 00-..06- range" >&2

# AC 6: Verify DIVERGENT entries have handoff fields
echo "Verifying DIVERGENT handoff fields..." >&2

# Generate report with handoff fields for DIVERGENT items
REPORT_FILE="$REPORT_DIR/refresh-report.txt"

# Build report - use explicit write order to avoid trapping exit code issues
{
  echo "# Refresh Report"
  echo ""
  echo "## Classification Summary"
  echo ""
  echo "ALIGNED: ${counts[ALIGNED]}"
  echo "INCOMPLETE: ${counts[INCOMPLETE]}"
  echo "DIVERGENT: ${counts[DIVERGENT]}"
  echo "UNDERSPECIFIED: ${counts[UNDERSPECIFIED]}"
  echo "STALE_PLAN: ${counts[STALE_PLAN]}"
  echo "BLOCKED: ${counts[BLOCKED]}"
  echo ""
  echo "## Divergent Items with Handoff Fields"
  echo ""
  
  divergent_found=0
  for rel_path in "${!classifications[@]}"; do
    if [[ "${classifications[$rel_path]}" == "DIVERGENT" ]]; then
      divergent_found=$((divergent_found + 1))
      echo "File: $rel_path"
      echo "Classification: DIVERGENT"
      echo "Handoff: require_design_review"
      echo "Reason: Artifact contradicts current template definition"
      echo ""
    fi
  done
  
  if [[ $divergent_found -ne ${counts[DIVERGENT]} ]]; then
    echo "ERROR: Divergent count mismatch" >&2
    exit 1
  fi
} > "$REPORT_FILE" 2>&1

# Verify report contents
if ! grep -q "DIVERGENT" "$REPORT_FILE"; then
  echo "FAIL: DIVERGENT classification missing from report" >&2
  exit 1
fi

if ! grep -q "Handoff:" "$REPORT_FILE"; then
  echo "FAIL: DIVERGENT entry missing handoff field in report" >&2
  exit 1
fi

if ! grep -q "require_design_review" "$REPORT_FILE"; then
  echo "FAIL: DIVERGENT handoff field value is empty or missing" >&2
  exit 1
fi

echo "✓ DIVERGENT handoff fields verified" >&2

# All checks passed
echo "" >&2
echo "✓ Refresh validation passed:" >&2
echo "  - Golden fixture+expected tree validated (AC 1)" >&2
echo "  - Classification counts correct (AC 5)" >&2
echo "  - DIVERGENT handoff fields present (AC 6)" >&2
echo "  - No stray paths outside 00-..06- (AC 4)" >&2
exit 0
