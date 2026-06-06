#!/usr/bin/env bash
# Vertical-slice test driver. Runs every scenario, compares actual to expected exit code.
set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIBRARY="$ROOT/library"
LIBRARY_V2="$ROOT/library-v2"
LIBRARY_ALIASES_POS="$ROOT/library-aliases-pos"
LIBRARY_BROKEN_ALIASES="$ROOT/library-broken-aliases"
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

# Match an exit code AND require certain codes are ABSENT from the output.
run_without_codes() {
  local name="$1"
  local expected="$2"
  local forbidden_codes="$3"  # space-separated
  shift 3
  local out
  out=$(python3 "$VALIDATOR" "$@" 2>&1)
  local actual=$?
  local present=""
  for code in $forbidden_codes; do
    if grep -q "$code" <<<"$out"; then
      present="$present $code"
    fi
  done
  if [ "$actual" -eq "$expected" ] && [ -z "$present" ]; then
    echo "PASS  $name  (exit $actual, no forbidden codes)"
    PASS=$((PASS + 1))
  else
    echo "FAIL  $name  (expected exit $expected got $actual; forbidden codes present:$present)"
    echo "----- output -----"
    echo "$out" | sed 's/^/    /'
    echo "------------------"
    FAIL=$((FAIL + 1))
    FAILURES+=("$name")
  fi
}

# Match an exit code AND require certain codes appear in the output.
run_with_codes() {
  local name="$1"
  local expected="$2"
  local required_codes="$3"  # space-separated
  shift 3
  local out
  out=$(python3 "$VALIDATOR" "$@" 2>&1)
  local actual=$?
  local missing=""
  for code in $required_codes; do
    if ! grep -q "$code" <<<"$out"; then
      missing="$missing $code"
    fi
  done
  if [ "$actual" -eq "$expected" ] && [ -z "$missing" ]; then
    echo "PASS  $name  (exit $actual, codes ok)"
    PASS=$((PASS + 1))
  else
    echo "FAIL  $name  (expected exit $expected got $actual; missing codes:$missing)"
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
echo "=== Bucket B fixtures ==="

# B1: I010 library major-bump deprecation
run_with_codes "B1a lib-bump-deprecated pinned v1 → I010 warn, exit 0" 0 "I010" \
  marker "$ROOT/consumer/lib-bump-deprecated/.helix.yml" \
  --methodology "helix=$METHODOLOGY" \
  --library-types "$LIBRARY_V2/types"
run_with_codes "B1b lib-bump-unpinned → T004 error, exit 3" 3 "T004" \
  marker "$ROOT/consumer/lib-bump-unpinned/.helix.yml" \
  --methodology "helix=$METHODOLOGY" \
  --library-types "$LIBRARY_V2/types"

# B2: I104 status:planned with resolved target
run_with_codes "B2 planned-but-resolved → I104 error, exit 1" 1 "I104" \
  marker "$ROOT/consumer/planned-but-resolved/.helix.yml" \
  --methodology "helix=$METHODOLOGY" \
  --library-types "$LIBRARY/types"

# B3: W005 legacy + new coexistence
run_with_codes "B3a legacy-and-new → W005 warn, exit 0" 0 "W005" \
  marker "$ROOT/consumer/legacy-and-new/.helix.yml" \
  --methodology "helix=$METHODOLOGY" \
  --library-types "$LIBRARY/types"
run_with_codes "B3b legacy-and-new --strict → W005 error, exit 1" 1 "W005" \
  marker "$ROOT/consumer/legacy-and-new/.helix.yml" \
  --methodology "helix=$METHODOLOGY" \
  --library-types "$LIBRARY/types" \
  --strict

# B4: M005 unknown methodology ignored, others proceed
run_with_codes "B4 unknown-methodology → M005 warn, helix validates, exit 0" 0 "M005" \
  marker "$ROOT/consumer/unknown-methodology/.helix.yml" \
  --methodology "helix=$METHODOLOGY" \
  --library-types "$LIBRARY/types"

# B5: intra-document edges (with paired negative)
run "B5a intra-doc-edges (scope: intra-document) → clean, exit 0" 0 \
  marker "$ROOT/consumer/intra-doc-edges/.helix.yml" \
  --methodology "helix=$METHODOLOGY" \
  --library-types "$LIBRARY/types"
run_with_codes "B5b intra-doc-edges-negative (scope: cross-document) → I101, exit 1" 1 "I101" \
  marker "$ROOT/consumer/intra-doc-edges-negative/.helix.yml" \
  --methodology "helix=$METHODOLOGY" \
  --library-types "$LIBRARY/types"

# B6: section_aliases (positive + paired negative)
run "B6a library-aliases-pos type-mode → clean, exit 0" 0 \
  type "$LIBRARY_ALIASES_POS/types"
run_with_codes "B6b library-broken-aliases (no aliases, ## FR) → T004, exit 3" 3 "T004" \
  type "$LIBRARY_BROKEN_ALIASES/types"

# B7: exhaustive collection — three independent errors in one run
run_with_codes "B7 three-errors → I101 (bad kind) + I101 (missing) + M005, exit 1" 1 "I101 M005" \
  marker "$ROOT/consumer/three-errors/.helix.yml" \
  --methodology "helix=$METHODOLOGY" \
  --library-types "$LIBRARY/types"

# B8: P12 terminology rename gate — M020 fires on v1 (legacy `methodologies:`), silent on v2 (`flows:`).
run_with_codes "B8a clean v1 marker → M020 fires, exit 0" 0 "M020" \
  marker "$ROOT/consumer/clean/.helix.yml" \
  --methodology "helix=$METHODOLOGY" \
  --library-types "$LIBRARY/types"
run_without_codes "B8b clean v2 marker (flows:) → M020 silent, exit 0" 0 "M020" \
  marker "$ROOT/consumer/clean-v2/.helix.yml" \
  --flow "helix=$METHODOLOGY" \
  --library-types "$LIBRARY/types"
# B8c: v2 marker still works under legacy --methodology flag alias (one-cycle compat).
run_without_codes "B8c v2 marker with legacy --methodology flag alias → M020 silent, exit 0" 0 "M020" \
  marker "$ROOT/consumer/clean-v2/.helix.yml" \
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
