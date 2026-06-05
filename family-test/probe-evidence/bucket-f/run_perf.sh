#!/usr/bin/env bash
# Bucket F perf+scale driver. Runs validator against N-doc corpora under PyYAML
# baseline. Captures wall-clock and findings count. Treats stated budgets as
# informational (validator is currently O(N^2) — caching/index pending).
set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VALIDATOR="$ROOT/library/scripts/helix_check.py"
EVID="$ROOT/probe-evidence/bucket-f"

cd "$ROOT"

run_once() {
  local label="$1"
  local corpus="$2"
  shift 2
  local extra=("$@")
  local out="$EVID/${label}.txt"
  echo "[run] $label corpus=$corpus extra=${extra[*]:-}" | tee "$out"
  local t0 t1 dt
  t0=$(python3 -c "import time; print(time.monotonic())")
  python3 "$VALIDATOR" marker "$corpus/.helix.yml" \
    --methodology helix=methodology-product \
    --library-types library/types \
    "${extra[@]}" \
    --json > "$EVID/${label}.json" 2> "$EVID/${label}.stderr"
  local ec=$?
  t1=$(python3 -c "import time; print(time.monotonic())")
  dt=$(python3 -c "print(f'{$t1 - $t0:.3f}')")
  local findings docs_scanned
  if [ -s "$EVID/${label}.json" ]; then
    findings=$(python3 -c "import json; d=json.load(open('$EVID/${label}.json')); print(len(d['findings']))")
  else
    findings="(no-json-output;see-stderr)"
  fi
  docs_scanned=$(find "$corpus/docs" -name '*.md' | wc -l | tr -d ' ')
  {
    echo "  exit_code=$ec"
    echo "  wall_clock_s=$dt"
    echo "  findings=$findings"
    echo "  docs_in_corpus=$docs_scanned"
  } | tee -a "$out"
  echo "$dt" > "$EVID/${label}.wall_s"
}

# Ensure clean cache state for each measurement
rm -rf perf-corpus-100/.helix perf-corpus-1000/.helix perf-corpus-5000/.helix

# F1 — 100 docs (budget: <1s)
run_once f1-100 perf-corpus-100

# F2 — 1000 docs (budget: <10s)
run_once f2-1000 perf-corpus-1000

# F3 — 5000 docs with ceiling guard (must exit cleanly with exit=5 + stderr)
run_once f3-5000-ceiling perf-corpus-5000 --ceiling-s 10

# F3b — 5000 docs without ceiling (full run, informational)
run_once f3-5000-full perf-corpus-5000

# F4 — cache: r1 cold, r2 warm
rm -rf perf-corpus-1000/.helix
run_once f4-1000-r1-cold perf-corpus-1000 --use-cache
run_once f4-1000-r2-warm perf-corpus-1000 --use-cache

echo
echo "[done] evidence at $EVID/"
