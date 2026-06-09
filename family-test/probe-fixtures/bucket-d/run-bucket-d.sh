#!/usr/bin/env bash
# Reproduce Bucket D evidence end-to-end.
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/../../.." && pwd)"
cd "$repo_root"

# Probe-fixture for migrate_relationships_to_links.py (historical bucket-d
# evidence). The script was part of the family-test/library/ research fork
# which was removed during canonical promotion. If you need to reproduce
# bucket-d evidence, restore the script from git history at sha 0d1a858a^
# or earlier, place it under a path of your choice, and set `script=` below.
script=${HELIX_MIGRATE_SCRIPT:-library/scripts/migrate_relationships_to_links.py}
if [[ ! -f "$script" ]]; then
  echo "SKIP: migrate script not present at $script (family-test/library/ was removed)" >&2
  exit 0
fi
fixtures=family-test/probe-fixtures/bucket-d/migration-corpus
workdir=family-test/probe-fixtures/bucket-d/migration-corpus-applied
evidence=family-test/probe-evidence/bucket-d
mkdir -p "$evidence"

echo "=== D1 — dry-run vs synthetic corpus ==="
python3 "$script" "$fixtures" --dry-run | tee "$evidence/d1-dry-run.txt"

echo
echo "=== D2 — dry-run vs real corpus (docs/helix) ==="
python3 "$script" docs/helix --dry-run | tee "$evidence/d2-docs-helix.txt"
echo "  (also wider tree, see d2-real-corpus-dry-run.txt for the summary)"

echo
echo "=== D3 — idempotent --apply ==="
rm -rf "$workdir"
cp -r "$fixtures" "$workdir"
echo "--- first apply ---" | tee "$evidence/d3-idempotent.txt"
python3 "$script" "$workdir" --apply | tee -a "$evidence/d3-idempotent.txt"
echo "--- second apply (no-op expected) ---" | tee -a "$evidence/d3-idempotent.txt"
set +e
python3 "$script" "$workdir" --apply | tee -a "$evidence/d3-idempotent.txt"
ec=$?
set -e
echo "second-apply exit=$ec" | tee -a "$evidence/d3-idempotent.txt"
[[ "$ec" == "0" ]] || { echo "FAIL: second apply should exit 0"; exit 1; }

echo
echo "=== --require-clean gate ==="
set +e
python3 "$script" "$fixtures" --require-clean --quiet
dirty=$?
python3 "$script" "$workdir" --require-clean --quiet
clean=$?
set -e
echo "dirty exit=$dirty (want 1)   clean exit=$clean (want 0)"
[[ "$dirty" == "1" && "$clean" == "0" ]] || { echo "FAIL: --require-clean gate"; exit 1; }

echo
echo "Bucket D — all probes PASS"
