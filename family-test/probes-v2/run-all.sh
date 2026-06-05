#!/usr/bin/env bash
# Bucket A v2 — functional probes. Each asks the agent to DO something whose
# correctness requires the skill's contract to hold.
#
# Auth: ANTHROPIC_API_KEY must be exported, OR ~/.claude/.credentials.json
# must be present. Without either, this exits 2 with a clear message —
# the harness is honest about what it can't verify.
#
# Usage:
#   bash run-all.sh                 # run all probes once
#   bash run-all.sh --determinism N # each probe runs N times (default 1)
#
# Output:
#   family-test/probe-evidence/bucket-a-v2/<probe>.{stream.jsonl,summary.txt}
#
set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HARNESS="$ROOT/docker/run-probe.sh"
EVIDENCE_DIR="$ROOT/probe-evidence/bucket-a-v2"
ASSERTIONS="$ROOT/docker/assertions.py"

DETERMINISM_RUNS=1
if [[ "${1:-}" == "--determinism" ]]; then
    DETERMINISM_RUNS="${2:-1}"
fi

mkdir -p "$EVIDENCE_DIR"

if [[ -z "${ANTHROPIC_API_KEY:-}" \
      && ! -f "${HELIX_PROBE_TOKEN_FILE:-/Users/erik/.cache/family-test-auth/token}" \
      && ! -f ~/.claude/.credentials.json ]]; then
    echo "FAIL: no auth source (ANTHROPIC_API_KEY, token file, or credentials.json)"
    exit 2
fi

PASS=0
FAIL=0
SKIP=0
FAILED_PROBES=()

# probe <id> <fixture-relpath> <plugins> <prompt> <cwd-relpath-in-workspace> <assertion-script>
probe() {
    local id="$1"
    local fixture="$2"
    local plugins="$3"
    local prompt_file="$4"
    local cwd_rel="$5"
    local assertion_fn="$6"

    local fixture_dir="$ROOT/$fixture"
    local evidence="$EVIDENCE_DIR/$id.stream.jsonl"
    local summary="$EVIDENCE_DIR/$id.summary.txt"

    if [[ ! -d "$fixture_dir" ]]; then
        echo "SKIP $id (fixture missing: $fixture_dir)"
        SKIP=$((SKIP + 1)); return
    fi

    echo "=== probe $id ==="
    if ! bash "$HARNESS" "$fixture_dir" "$plugins" "$ROOT/probes-v2/$prompt_file" "$evidence" "$cwd_rel" 2>&1; then
        echo "  (harness exited non-zero — evidence still inspected)"
    fi

    if "$assertion_fn" "$evidence" "$fixture_dir" "$summary"; then
        echo "PASS $id"
        PASS=$((PASS + 1))
    else
        echo "FAIL $id"
        FAIL=$((FAIL + 1))
        FAILED_PROBES+=("$id")
    fi
}

# Assertion helpers — each reads the stream-json evidence and writes a summary.
# Return 0 = pass, 1 = fail.

assert_write_under_root() {
    local evidence="$1"; local fixture="$2"; local summary="$3"
    local expected_root="$4"
    python3 - "$evidence" "$fixture" "$summary" "$expected_root" <<'PY'
import json, sys, re
evid, fix, summary, root = sys.argv[1:5]
writes = []
try:
    for line in open(evid):
        if not line.strip(): continue
        ev = json.loads(line)
        # claude stream-json: {type:"assistant", message:{content:[{type:"tool_use", name:"Write", input:{file_path:...}}]}}
        msg = ev.get("message") or {}
        for blk in msg.get("content") or []:
            if blk.get("type") == "tool_use" and blk.get("name") in ("Write", "Edit"):
                fp = (blk.get("input") or {}).get("file_path") or ""
                writes.append(fp)
except FileNotFoundError:
    open(summary, "w").write(f"FAIL: no evidence file at {evid}\n"); sys.exit(1)

ok = bool(writes) and all(root in w for w in writes)
with open(summary, "w") as f:
    f.write(f"writes: {writes}\nexpected_root: {root}\nok: {ok}\n")
sys.exit(0 if ok else 1)
PY
}

assert_a1() { assert_write_under_root "$1" "$2" "$3" "/docs/helix/"; }
assert_a2() {
    # A2 — scoped to services/api/docs/helix/. Pass if no Write outside scope.
    python3 - "$1" "$3" <<'PY'
import json, sys
evid, summary = sys.argv[1:3]
writes = []
for line in open(evid):
    if not line.strip(): continue
    ev = json.loads(line)
    msg = ev.get("message") or {}
    for blk in msg.get("content") or []:
        if blk.get("type") == "tool_use" and blk.get("name") in ("Write", "Edit"):
            writes.append((blk.get("input") or {}).get("file_path") or "")
required = "services/api/docs/helix/"
ok = all(required in w for w in writes) if writes else True  # no write = also acceptable (clarification)
with open(summary, "w") as f:
    f.write(f"writes: {writes}\nrequired_substring: {required}\nok: {ok}\n")
sys.exit(0 if ok else 1)
PY
}
assert_a3() {
    # A3 — marker is at workspace root, cwd is docs/helix/. Pass if any tool
    # reads either the parent .helix.yml OR runs `git rev-parse`.
    python3 - "$1" "$3" <<'PY'
import json, sys
evid, summary = sys.argv[1:3]
saw_upward_search = False
saw_git_rev_parse = False
saw_marker_read = False
all_reads = []
for line in open(evid):
    if not line.strip(): continue
    ev = json.loads(line)
    msg = ev.get("message") or {}
    for blk in msg.get("content") or []:
        if blk.get("type") != "tool_use": continue
        name = blk.get("name") or ""
        inp = blk.get("input") or {}
        if name == "Bash":
            cmd = inp.get("command") or ""
            if "rev-parse" in cmd:
                saw_git_rev_parse = True
            if ".helix.yml" in cmd:
                saw_marker_read = True
        if name == "Read":
            fp = inp.get("file_path") or ""
            all_reads.append(fp)
            # Did the agent read a parent-relative .helix.yml?
            if ".helix.yml" in fp and (".." in fp or fp.startswith("/workspace/.helix.yml") or fp == ".helix.yml"):
                saw_marker_read = True
ok = saw_marker_read or saw_git_rev_parse
with open(summary, "w") as f:
    f.write(f"git_rev_parse={saw_git_rev_parse}\nmarker_read={saw_marker_read}\nall_reads={all_reads}\nok: {ok}\n")
sys.exit(0 if ok else 1)
PY
}
assert_a4() {
    # A4 — agent must REJECT, not write any helix-infra artifact.
    python3 - "$1" "$3" <<'PY'
import json, sys, re
evid, summary = sys.argv[1:3]
writes = []
last_text = ""
for line in open(evid):
    if not line.strip(): continue
    ev = json.loads(line)
    msg = ev.get("message") or {}
    for blk in msg.get("content") or []:
        if blk.get("type") == "tool_use" and blk.get("name") in ("Write", "Edit"):
            writes.append((blk.get("input") or {}).get("file_path") or "")
        if blk.get("type") == "text":
            last_text = blk.get("text") or last_text
mentions_authz = bool(re.search(r"(authoriz|\.helix\.yml|marker|not in marker|not list)", last_text, re.I))
ok = not writes and mentions_authz
with open(summary, "w") as f:
    f.write(f"writes: {writes}\nmentions_authz: {mentions_authz}\nlast_text_snippet: {last_text[:200]!r}\nok: {ok}\n")
sys.exit(0 if ok else 1)
PY
}
assert_a5() {
    # A5 — agent stops on malformed marker, no fallback. No writes.
    python3 - "$1" "$3" <<'PY'
import json, sys, re
evid, summary = sys.argv[1:3]
writes = []
last_text = ""
for line in open(evid):
    if not line.strip(): continue
    ev = json.loads(line)
    msg = ev.get("message") or {}
    for blk in msg.get("content") or []:
        if blk.get("type") == "tool_use" and blk.get("name") in ("Write", "Edit"):
            writes.append((blk.get("input") or {}).get("file_path") or "")
        if blk.get("type") == "text":
            last_text = blk.get("text") or last_text
mentions_error = bool(re.search(r"(YAML.*error|parse.*error|malformed|invalid|cannot parse|broken)", last_text, re.I))
ok = not writes and mentions_error
with open(summary, "w") as f:
    f.write(f"writes: {writes}\nmentions_error: {mentions_error}\nlast_text_snippet: {last_text[:200]!r}\nok: {ok}\n")
sys.exit(0 if ok else 1)
PY
}
assert_a6() {
    # A6 — literal banner from design §1.3 verbatim
    python3 - "$1" "$3" <<'PY'
import json, sys, re
evid, summary = sys.argv[1:3]
text = ""
for line in open(evid):
    if not line.strip(): continue
    ev = json.loads(line)
    msg = ev.get("message") or {}
    for blk in msg.get("content") or []:
        if blk.get("type") == "text":
            text += "\n" + (blk.get("text") or "")
banner_re = re.compile(
    r"No \.helix\.yml found\. Activating helix by heuristic.*\n.*Run /helix init-marker to make this explicit\.",
    re.MULTILINE
)
ok = bool(banner_re.search(text))
with open(summary, "w") as f:
    f.write(f"banner_found: {ok}\ntext_snippet: {text[:300]!r}\n")
sys.exit(0 if ok else 1)
PY
}
assert_a7_helix() { assert_write_under_root "$1" "$2" "$3" "/docs/helix/"; }
assert_a7_infra() { assert_write_under_root "$1" "$2" "$3" "/infra/"; }

# Run probes
probe "a1" "consumer/clean" "library,methodology-product" \
      "a1-write-under-scope.prompt" "" assert_a1

probe "a2" "consumer/scoped-subtree" "library,methodology-product" \
      "a2-refuse-outside-scope.prompt" "" assert_a2

probe "a3" "consumer/clean" "library,methodology-product" \
      "a3-upward-walk.prompt" "docs/helix" assert_a3

probe "a4" "consumer/clean" "library,methodology-product,methodology-infra" \
      "a4-marker-authz.prompt" "" assert_a4

probe "a5" "consumer/malformed-with-heuristic" "library,methodology-product" \
      "a5-stop-malformed.prompt" "" assert_a5

probe "a6" "consumer/heuristic-fallback" "library,methodology-product" \
      "a6-literal-banner.prompt" "" assert_a6

probe "a7-helix" "consumer/multi-scope" "library,methodology-product,methodology-infra" \
      "a7-cwd-routing-helix.prompt" "docs/helix" assert_a7_helix

probe "a7-infra" "consumer/multi-scope" "library,methodology-product,methodology-infra" \
      "a7-cwd-routing-infra.prompt" "infra" assert_a7_infra

echo ""
echo "=== summary ==="
echo "PASS=$PASS  FAIL=$FAIL  SKIP=$SKIP"
if [[ $FAIL -gt 0 ]]; then
    echo "failed: ${FAILED_PROBES[*]}"
    exit 1
fi
