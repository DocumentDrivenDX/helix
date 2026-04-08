#!/bin/bash
# Measure completeness score for HELIX artifact generation
# Usage: bash tests/measures/completeness.sh <scenario>

set -euo pipefail

SCENARIO="${1:-A}"
EXPECTED_FILE="/Users/erik/Projects/helix/tests/scenarios/$SCENARIO/expected-artifacts.txt"

if [ ! -f "$EXPECTED_FILE" ]; then
    echo "ERROR: Expected artifacts file not found: $EXPECTED_FILE" >&2
    exit 1
fi

# Read expected artifacts
mapfile -t expected < "$EXPECTED_FILE"
total=${#expected[@]}
found=0

echo "Checking for ${total} expected artifacts..."

for artifact in "${expected[@]}"; do
    # Check if file exists anywhere under docs/helix/
    if find docs/helix/ -name "*$(basename "$artifact")*" -type f >/dev/null 2>&1; then
        echo "✓ Found: $artifact"
        ((found++))
    else
        echo "✗ Missing: $artifact"
    fi
done

# Calculate percentage
if [ $total -eq 0 ]; then
    echo "N/A (no expected artifacts)"
    exit 0
fi

score=$(( (found * 100) / total ))
echo ""
echo "Completeness Score: $score/100 ($found/$total artifacts found)"
echo "$score"
