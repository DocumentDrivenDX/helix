#!/usr/bin/env bash
# Vertical-slice test driver. Runs every scenario, compares actual to expected exit code.
set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIBRARY="$ROOT/library"
METHODOLOGY="$ROOT/methodology-product"
VALIDATOR="$LIBRARY/scripts/helix_check.py"

PASS=0
FAIL=0
FAILURES=()

run() {
  local name="$1"
  local expected="$2"
  shift 2
  local out
  out=$(python3 "$VALIDATOR" "$@" 2>&1)
  local actual=$?
  if [ "$actual" -eq "$expected" ]; then
    echo "PASS  $name  (exit $actual)"
    PASS=$((PASS + 1))
  else
    echo "FAIL  $name  (expected $expected, got $actual)"
    echo "----- output -----"
    echo "$out" | sed 's/^/    /'
    echo "------------------"
    FAIL=$((FAIL + 1))
    FAILURES+=("$name")
  fi
}

echo "=== type-mode tests ==="
run "T01 library clean (no relationships)" 0 \
  type "$LIBRARY/types"
run "T02 library broken (relationships present)" 3 \
  type "$ROOT/library-broken/types"

echo ""
echo "=== graph-mode tests ==="
run "G01 graph clean" 0 \
  graph "$METHODOLOGY" --library-types "$LIBRARY/types"

echo ""
echo "=== marker-mode tests (clean) ==="
run "M01 marker clean — all instances valid" 0 \
  marker "$ROOT/consumer/clean/.helix.yml" \
  --methodology "helix=$METHODOLOGY" \
  --library-types "$LIBRARY/types"

echo ""
echo "=== marker-mode tests (instance violations) ==="
run "I01 bad edge kind (contains where graph declares informs) → I101" 1 \
  marker "$ROOT/consumer/bad-edge-kind/.helix.yml" \
  --methodology "helix=$METHODOLOGY" \
  --library-types "$LIBRARY/types"
run "I02 missing target → I101 with hint" 1 \
  marker "$ROOT/consumer/missing-target/.helix.yml" \
  --methodology "helix=$METHODOLOGY" \
  --library-types "$LIBRARY/types"
run "I03 planned-forward → I103 warning, no error" 0 \
  marker "$ROOT/consumer/planned-forward/.helix.yml" \
  --methodology "helix=$METHODOLOGY" \
  --library-types "$LIBRARY/types"

echo ""
echo "=== marker-mode tests (cross-methodology) ==="
run "X01 cross-methodology edge authorized + both active" 0 \
  marker "$ROOT/consumer/cross-method/.helix.yml" \
  --methodology "helix=$METHODOLOGY" \
  --methodology "helix-infra=$ROOT/methodology-infra" \
  --library-types "$LIBRARY/types"
run "X02 cross-methodology edge with target methodology inactive (warn mode) → exit 0 with I120/I121" 0 \
  marker "$ROOT/consumer/cross-method-target-inactive/.helix.yml" \
  --methodology "helix=$METHODOLOGY" \
  --library-types "$LIBRARY/types"
run "X03 same scenario under --cross-methodology-edges deny → I101 error" 1 \
  marker "$ROOT/consumer/cross-method-target-inactive/.helix.yml" \
  --methodology "helix=$METHODOLOGY" \
  --library-types "$LIBRARY/types" \
  --cross-methodology-edges deny

echo ""
echo "=== marker-mode tests (marker hard-fail) ==="
run "M02 root escapes repo → M002" 4 \
  marker "$ROOT/consumer/malformed-marker-escape/.helix.yml" \
  --methodology "helix=$METHODOLOGY" \
  --library-types "$LIBRARY/types"
run "M03 duplicate id → M003" 4 \
  marker "$ROOT/consumer/malformed-marker-dup-id/.helix.yml" \
  --methodology "helix=$METHODOLOGY" \
  --library-types "$LIBRARY/types"
run "M04 missing scope → M006 (without --allow-empty-scope)" 4 \
  marker "$ROOT/consumer/malformed-marker-missing-scope/.helix.yml" \
  --methodology "helix=$METHODOLOGY" \
  --library-types "$LIBRARY/types"

echo ""
echo "=== summary ==="
echo "PASS: $PASS"
echo "FAIL: $FAIL"
if [ "$FAIL" -gt 0 ]; then
  echo "failures: ${FAILURES[*]}"
  exit 1
fi
