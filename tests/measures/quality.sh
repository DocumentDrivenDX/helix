#!/bin/bash
# Measure quality score for HELIX artifacts
# Checks for required sections, cross-references, and acceptance criteria

set -euo pipefail

score=0
max_score=100

echo "=== Quality Assessment ==="

# PRD quality checks (if exists)
if [ -f "docs/helix/01-frame/prd.md" ]; then
    echo ""
    echo "Checking PRD..."
    
    if grep -q "## Requirements" docs/helix/01-frame/prd.md; then
        echo "  ✓ Has Requirements section"
        ((score+=25))
    else
        echo "  ✗ Missing Requirements section"
    fi
    
    if grep -q "## Constraints" docs/helix/01-frame/prd.md; then
        echo "  ✓ Has Constraints section"
        ((score+=25))
    else
        echo "  ✗ Missing Constraints section"
    fi
else
    echo "No PRD found (may be expected for low autonomy)"
fi

# Cross-reference traceability (minimum 5 refs across all artifacts)
echo ""
echo "Checking cross-references..."
ref_count=$(grep -r '\[\[.*\]\]' docs/helix/ 2>/dev/null | wc -l || echo "0")

if [ "$ref_count" -ge 5 ]; then
    echo "  ✓ Found $ref_count cross-references (≥5 required)"
    ((score+=25))
else
    echo "  ✗ Only $ref_count cross-references found (<5)"
fi

# Acceptance criteria in user stories
echo ""
echo "Checking user story acceptance criteria..."
if grep -rq "## Acceptance Criteria" docs/helix/01-frame/user-stories/ 2>/dev/null; then
    ac_count=$(grep -r "## Acceptance Criteria" docs/helix/01-frame/user-stories/ | wc -l)
    echo "  ✓ Found acceptance criteria in $ac_count user stories"
    ((score+=25))
else
    echo "  ✗ No acceptance criteria found in user stories"
fi

# Cap at max score
[ $score -gt $max_score ] && score=$max_score

echo ""
echo "Quality Score: $score/$max_score"
echo "$score"
