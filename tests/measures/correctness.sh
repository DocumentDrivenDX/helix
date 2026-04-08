#!/bin/bash
# Measure decision correctness - checks that constraints were respected
# Usage: bash tests/measures/correctness.sh <scenario>

set -euo pipefail

SCENARIO="${1:-A}"
CONSTRAINTS_FILE="/Users/erik/Projects/helix/tests/scenarios/$SCENARIO/constraints.txt"

if [ ! -f "$CONSTRAINTS_FILE" ]; then
    echo "ERROR: Constraints file not found: $CONSTRAINTS_FILE" >&2
    exit 1
fi

score=100

echo "=== Decision Correctness Assessment ==="
echo ""

# Load constraints
mapfile -t constraints < "$CONSTRAINTS_FILE"

for constraint in "${constraints[@]}"; do
    echo "Checking: $constraint"
    
    case "$constraint" in
        *"PostgreSQL"*|*"postgres"*)
            if grep -rq "PostgreSQL\|postgres" docs/helix/02-design/ 2>/dev/null; then
                echo "  ✓ PostgreSQL constraint respected"
            else
                echo "  ✗ PostgreSQL not mentioned in design docs (-30)"
                ((score-=30))
            fi
            ;;
        
        *"TypeScript"*|*"Rust"*)
            if grep -rqE "(TypeScript|Rust)" docs/helix/02-design/ 2>/dev/null; then
                echo "  ✓ Language choice documented"
            else
                echo "  ⚠ Language not explicitly specified in design (-10)"
                ((score-=10))
            fi
            ;;
        
        *"OAuth"*|*"authentication"*)
            if grep -rqE "(OAuth|OIDC|authentication)" docs/helix/02-design/ 2>/dev/null; then
                echo "  ✓ Authentication approach documented"
            else
                echo "  ✗ No authentication design found (-25)"
                ((score-=25))
            fi
            ;;
        
        *"Docker"*|*"deployment"*)
            if grep -rqE "(Docker|dockerfile|deployment)" docs/helix/02-design/ 2>/dev/null; then
                echo "  ✓ Deployment approach documented"
            else
                echo "  ⚠ No deployment documentation (-10)"
                ((score-=10))
            fi
            ;;
        
        *"real-time"*|*"latency"*)
            if grep -rqE "(real.time|latency|websocket)" docs/helix/02-design/ 2>/dev/null; then
                echo "  ✓ Real-time requirements addressed"
            else
                echo "  ✗ Real-time constraints not addressed (-30)"
                ((score-=30))
            fi
            ;;
    esac
    
    echo ""
done

# Bonus for documented assumptions
echo "Checking for documented assumptions..."
assumption_count=$(grep -r "Assumption:" docs/helix/ 2>/dev/null | wc -l || echo "0")
if [ "$assumption_count" -gt 0 ]; then
    echo "✓ Found $assumption_count documented assumptions (+10 bonus)"
    ((score+=10))
fi

# Cap at 100
[ $score -gt 100 ] && score=100
[ $score -lt 0 ] && score=0

echo ""
echo "Correctness Score: $score/100"
echo "$score"
