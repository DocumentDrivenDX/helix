#!/usr/bin/env bash
# check-cc-revalidation.sh — warn if the CC version pin is overdue.
#
# Reads family-test/bench/cc-version.lock, parses re_validation_required_after,
# and prints a WARN line to stderr if the date is in the past.
#
# Exit code: 0 always (this is advisory). Callers that want to gate on it
# should grep the output for "WARN: CC version re-validation overdue".
#
# Used by:
#   - lefthook.yml pre-commit (warns on every commit, never blocks)
#   - .github/workflows/family-bench.yml self-test job (surfaces in CI)
set -euo pipefail

# Resolve repo root so the script works from any cwd (pre-commit, CI, manual).
here="$(cd "$(dirname "$0")" && pwd)"
lock="$here/../cc-version.lock"

if [[ ! -f "$lock" ]]; then
    echo "WARN: cc-version.lock not found at $lock" >&2
    exit 0
fi

python3 - "$lock" <<'PY'
import sys
from datetime import date

lock_path = sys.argv[1]
deadline = None
version = None
for raw in open(lock_path):
    line = raw.split("#", 1)[0].strip()
    if not line or ":" not in line:
        continue
    key, _, val = line.partition(":")
    key = key.strip()
    val = val.strip()
    if key == "re_validation_required_after":
        deadline = val
    elif key == "claude_code_version":
        version = val

if not deadline:
    print("WARN: cc-version.lock missing re_validation_required_after", file=sys.stderr)
    sys.exit(0)

try:
    y, m, d = (int(x) for x in deadline.split("-"))
    deadline_date = date(y, m, d)
except Exception:
    print(f"WARN: cc-version.lock has unparseable re_validation_required_after: {deadline}", file=sys.stderr)
    sys.exit(0)

today = date.today()
if today > deadline_date:
    overdue_days = (today - deadline_date).days
    print(
        f"WARN: CC version re-validation overdue "
        f"(pin={version}, deadline={deadline_date}, {overdue_days} days past). "
        f"See family-test/bench/docs/cc-version-revalidation.md.",
        file=sys.stderr,
    )
PY
