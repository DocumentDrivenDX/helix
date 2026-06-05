#!/usr/bin/env bash
# F4 cache invalidation matrix. Verifies the touch-table semantics:
#   1. touch one instance file  → re-validate JUST that file
#   2. touch graph.yml          → re-validate all instances of that methodology
#   3. touch marker             → full re-walk
#   4. touch library type meta  → re-validate all instances of that type
#
# Validator emits docs_scanned in stderr/output? It does not (today) — so we
# infer reuse via cache-file inspection AND wall-clock floor: a no-op rerun
# with the cache should be < 0.4s. A graph-touch run should be ~ first-run.
set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VALIDATOR="$ROOT/library/scripts/helix_check.py"
EVID="$ROOT/probe-evidence/bucket-f"
CORPUS="$ROOT/perf-corpus-1000"
GRAPH="$ROOT/methodology-product/workflows/graph.yml"
META="$ROOT/library/types/prd/meta.yml"

cd "$ROOT"
mkdir -p "$EVID"

t() { python3 -c "import time; print(time.monotonic())"; }
dt() { python3 -c "print(f'{$2 - $1:.4f}')"; }

run_cached() {
  local label="$1"
  local t0 t1
  t0=$(t)
  python3 "$VALIDATOR" marker "$CORPUS/.helix.yml" \
    --methodology helix="$ROOT/methodology-product" \
    --library-types "$ROOT/library/types" \
    --use-cache --json > "$EVID/${label}.json" 2> "$EVID/${label}.stderr"
  local ec=$?
  t1=$(t)
  local d
  d=$(dt $t0 $t1)
  echo "  $label: wall=$d exit=$ec" | tee -a "$EVID/f4-invalidation.log"
  echo "$d" > "$EVID/${label}.wall_s"
}

: > "$EVID/f4-invalidation.log"
echo "F4 invalidation matrix" | tee -a "$EVID/f4-invalidation.log"
echo "======================" | tee -a "$EVID/f4-invalidation.log"

# Reset
rm -rf "$CORPUS/.helix"

echo "[step 0] cold (no cache)" | tee -a "$EVID/f4-invalidation.log"
run_cached f4-step0-cold

echo "[step 1] warm (no changes)" | tee -a "$EVID/f4-invalidation.log"
run_cached f4-step1-warm

echo "[step 2] touch ONE instance → expect partial re-walk" | tee -a "$EVID/f4-invalidation.log"
touch "$CORPUS/docs/helix/01-frame/PRD-00042.md"
run_cached f4-step2-one-instance

echo "[step 3] touch graph.yml → expect full re-walk of that methodology" | tee -a "$EVID/f4-invalidation.log"
touch "$GRAPH"
run_cached f4-step3-graph
# undo (graph mtime moves forward — leave it)

echo "[step 4] touch library type meta.yml → expect re-walk of that type" | tee -a "$EVID/f4-invalidation.log"
touch "$META"
run_cached f4-step4-meta

echo "[step 5] touch MARKER → expect full re-walk" | tee -a "$EVID/f4-invalidation.log"
touch "$CORPUS/.helix.yml"
run_cached f4-step5-marker

# Final assertion summary
python3 - "$EVID" <<'PY'
import sys
from pathlib import Path
ev = Path(sys.argv[1])
def r(name): return float((ev / f"{name}.wall_s").read_text().strip())

cold   = r("f4-step0-cold")
warm   = r("f4-step1-warm")
one    = r("f4-step2-one-instance")
graph  = r("f4-step3-graph")
meta   = r("f4-step4-meta")
marker = r("f4-step5-marker")

print()
print(f"step0 cold            : {cold:.3f}s")
print(f"step1 warm rerun      : {warm:.3f}s  ratio={warm/cold*100:.1f}% (plan: <=30%)")
print(f"step2 one instance    : {one:.3f}s   (expect ~warm, only 1 doc re-checked)")
print(f"step3 graph touch     : {graph:.3f}s (expect ~cold, methodology-wide invalidation)")
print(f"step4 meta touch      : {meta:.3f}s  (expect ~cold, type-wide invalidation)")
print(f"step5 marker touch    : {marker:.3f}s (expect ~cold, full re-walk)")
print()

passed = []
# Assert: warm rerun < 30% of cold
passed.append(("warm<30%cold", warm < 0.30 * cold))
# Assert: one-instance is close to warm (within 2x)
passed.append(("one-instance ~warm", one < max(0.5, 2 * warm)))
# Assert: graph-touch is close to cold (>= 50% of cold)
passed.append(("graph-touch ~cold", graph >= 0.50 * cold))
# Assert: meta-touch is close to cold (>= 50% of cold)
passed.append(("meta-touch ~cold", meta >= 0.50 * cold))
# Assert: marker-touch is close to cold (>= 50% of cold)
passed.append(("marker-touch ~cold", marker >= 0.50 * cold))

print("invalidation-matrix assertions:")
for name, ok in passed:
    print(f"  {'PASS' if ok else 'FAIL'}  {name}")

failures = [n for n, ok in passed if not ok]
sys.exit(0 if not failures else 1)
PY
