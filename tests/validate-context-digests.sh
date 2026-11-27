#!/usr/bin/env bash
set -euo pipefail

. "$(dirname "${BASH_SOURCE[0]}")/../scripts/lib/uvpy.sh"

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

PYTHONPATH="$repo_root" uvpy "$repo_root/tests/test_refresh_context_digests.py" >/dev/null

cat >"$tmpdir/valid.jsonl" <<'EOF'
{"id":"hx-digest-ok","title":"digest present","status":"open","labels":["helix","activity:build"],"description":"<context-digest>\n<principles>Validate Your Work</principles>\n</context-digest>\n\nBody"}
{"id":"hx-rationale-ok","title":"authorized omission rationale with provenance","status":"open","labels":["helix","activity:build","digest:omission-authorized","kind:legacy-migrated"],"digest-omission-path":"helix-input:legacy-migration","description":"Explicit omission rationale: Legacy migrated planning bead intentionally omits a digest until the upstream concern mapping lands."}
{"id":"hx-review-finding-ok","title":"review finding has area label","status":"open","labels":["helix","activity:build","review-finding","area:workflow"],"description":"<context-digest>\n<principles>Validate Your Work</principles>\n</context-digest>\n\nBody"}
{"id":"hx-closed-legacy","title":"closed legacy bead","status":"closed","labels":["helix","activity:build"],"description":"Legacy body"}
EOF

uvpy "$repo_root/scripts/validate_context_digests.py" --tracker "$tmpdir/valid.jsonl" >/dev/null

cat >"$tmpdir/invalid.jsonl" <<'EOF'
{"id":"hx-digest-missing","title":"missing digest","status":"open","labels":["helix","activity:build"],"description":"Legacy body"}
{"id":"hx-rationale-unauthorized","title":"unauthorized omission rationale","status":"open","labels":["helix","activity:build"],"description":"Explicit omission rationale: skipped for convenience"}
{"id":"hx-rationale-label-only","title":"label-only omission rationale","status":"open","labels":["helix","activity:build","digest:omission-authorized"],"description":"Explicit omission rationale: skipped for convenience"}
{"id":"hx-rationale-empty","title":"empty omission rationale","status":"open","labels":["helix","activity:build","digest:omission-authorized"],"digest-omission-path":"helix-input:legacy-migration","description":"Explicit omission rationale:   "}
{"id":"hx-forged-provenance","title":"forged authorized path without provenance label","status":"open","labels":["helix","activity:build","digest:omission-authorized"],"digest-omission-path":"helix-input:legacy-migration","description":"Explicit omission rationale: forged authorized omission path"}
{"id":"hx-review-finding-missing-area","title":"review finding missing area","status":"open","labels":["helix","activity:build","review-finding"],"description":"<context-digest>\n<principles>Validate Your Work</principles>\n</context-digest>\n\nBody"}
EOF

if uvpy "$repo_root/scripts/validate_context_digests.py" --tracker "$tmpdir/invalid.jsonl" >"$tmpdir/invalid.out" 2>"$tmpdir/invalid.err"; then
  echo "FAIL: validator should reject open HELIX beads without a digest or workflow-authorized valid omission rationale" >&2
  exit 1
fi

grep -Fq "hx-digest-missing" "$tmpdir/invalid.err" || {
  echo "FAIL: validator should identify the offending bead" >&2
  exit 1
}

grep -Fq "hx-rationale-unauthorized" "$tmpdir/invalid.err" || {
  echo "FAIL: validator should reject omission rationales without explicit authorization" >&2
  exit 1
}

grep -Fq "hx-rationale-label-only" "$tmpdir/invalid.err" || {
  echo "FAIL: validator should reject omission rationales that only self-apply the label" >&2
  exit 1
}

grep -Fq "hx-rationale-empty" "$tmpdir/invalid.err" || {
  echo "FAIL: validator should reject empty omission rationales" >&2
  exit 1
}

grep -Fq "hx-forged-provenance" "$tmpdir/invalid.err" || {
  echo "FAIL: validator should reject forged authorized omission path without provenance label" >&2
  exit 1
}

grep -Fq "hx-review-finding-missing-area" "$tmpdir/invalid.err" || {
  echo "FAIL: validator should identify review findings missing area labels" >&2
  exit 1
}

uvpy "$repo_root/scripts/validate_context_digests.py" --tracker "$repo_root/.ddx/beads.jsonl"
