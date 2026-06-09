#!/usr/bin/env bash
# ablate-descriptions.sh — P1 description-shape ablation runner.
#
# Activates a given SKILL.<variant>.md as the live SKILL.md, then iterates
# every row in family-test/bench/routing-evals/{positive,negative,ambiguous}
# running each prompt through the Docker probe harness with the helix
# methodology-product plugin (+ helix-library) installed.
#
# Per-row result written to:
#   family-test/bench/runner/ablation-results/<variant>.jsonl
#
# Each line:
#   {"id": ..., "kind": "positive|negative|ambiguous", "prompt": ...,
#    "expected": ..., "skill_engaged": bool, "skills_called": [...],
#    "evidence": "<path>", "probe_rc": N}
#
# Usage:
#   ablate-descriptions.sh <variant>           # one variant
#   ablate-descriptions.sh --all               # baseline, verb-list, when-to-use, minimal
#   ablate-descriptions.sh --restore           # restore SKILL.md to baseline
#
# Env:
#   PARALLEL   max concurrent probes (default 6)
#   ROWS       optional space-separated list of row-ids to run (else all 75)
#   SKIP_BUILT_IMAGE  if "1", trust an existing image instead of rebuilding

set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
BENCH_ROOT="$(cd "$HERE/.." && pwd)"
FAMILY_TEST_DIR="$(cd "$BENCH_ROOT/.." && pwd)"
REPO_ROOT="$(cd "$FAMILY_TEST_DIR/.." && pwd)"

SKILL_DIR="$FAMILY_TEST_DIR/methodology-product/skills/helix"
EVAL_DIR="$BENCH_ROOT/routing-evals"
RESULTS_DIR="$HERE/ablation-results"
TMP_ROOT="$FAMILY_TEST_DIR/.tmp"
mkdir -p "$RESULTS_DIR" "$TMP_ROOT"

PARALLEL="${PARALLEL:-6}"

VARIANTS_ALL=(baseline verb-list when-to-use minimal)

PROBE_IMAGE="${PROBE_IMAGE:-family-test-claude:latest}"
export PROBE_IMAGE

if ! docker image inspect "$PROBE_IMAGE" >/dev/null 2>&1; then
    echo "[ablate] building $PROBE_IMAGE" >&2
    docker build \
        --build-arg "HOST_UID=$(id -u)" \
        --build-arg "HOST_GID=$(id -g)" \
        -t "$PROBE_IMAGE" \
        -f "$FAMILY_TEST_DIR/docker/Dockerfile.claude" \
        "$FAMILY_TEST_DIR/docker"
fi

# ---------------------------------------------------------------------------
# Variant install
# ---------------------------------------------------------------------------
install_variant() {
    local variant="$1"
    local src="$SKILL_DIR/SKILL.${variant}.md"
    if [[ ! -f "$src" ]]; then
        echo "[ablate] ERROR: no such variant file: $src" >&2
        exit 1
    fi
    cp "$src" "$SKILL_DIR/SKILL.md"
    echo "[ablate] installed variant=$variant (cp SKILL.${variant}.md SKILL.md)"
}

# ---------------------------------------------------------------------------
# Row execution
# ---------------------------------------------------------------------------
run_row() {
    local kind="$1"      # positive|negative|ambiguous
    local row_json="$2"  # raw jsonl line
    local variant="$3"
    local rundir="$4"    # per-row tmp dir
    local resultfile="$5"

    local id prompt expected
    id=$(printf '%s' "$row_json" | python3 -c 'import json,sys; print(json.loads(sys.stdin.read())["id"])')
    prompt=$(printf '%s' "$row_json" | python3 -c 'import json,sys; print(json.loads(sys.stdin.read())["prompt"])')

    if [[ "$kind" == "positive" || "$kind" == "negative" ]]; then
        expected=$(printf '%s' "$row_json" | python3 -c 'import json,sys; v=json.loads(sys.stdin.read()).get("expected_skill"); print("" if v is None else v)')
    else
        expected=$(printf '%s' "$row_json" | python3 -c 'import json,sys; print(json.loads(sys.stdin.read()).get("correct_route",""))')
    fi

    mkdir -p "$rundir"
    local prompt_file="$rundir/prompt.txt"
    local evidence_file="$rundir/evidence.jsonl"
    printf '%s\n' "$prompt" > "$prompt_file"

    local fixture="$FAMILY_TEST_DIR/consumer/clean"
    local plugins="$FAMILY_TEST_DIR/library,$FAMILY_TEST_DIR/methodology-product"

    set +e
    bash "$FAMILY_TEST_DIR/docker/run-probe.sh" \
        "$fixture" "$plugins" "$prompt_file" "$evidence_file" \
        >"$rundir/probe.stdout" 2>"$rundir/probe.stderr"
    local rc=$?
    set -e

    # Parse evidence for Skill tool_use
    python3 - "$id" "$kind" "$expected" "$variant" "$evidence_file" "$rc" \
            "$resultfile" "$prompt" <<'PY'
import json, sys, os
id_, kind, expected, variant, evidence, rc, resultfile, prompt = sys.argv[1:9]
rc = int(rc)
sys.path.insert(0, os.environ.get("DOCKER_DIR", ""))
# Inline minimal parser so we don't depend on path tricks
def load_events(p):
    out=[]
    if not os.path.exists(p): return out
    with open(p, "r", encoding="utf-8") as f:
        for line in f:
            line=line.strip()
            if not line: continue
            try: out.append(json.loads(line))
            except Exception: continue
    return out

events = load_events(evidence)
skills_called = []
all_tools = []
for ev in events:
    msg = ev.get("message")
    if not isinstance(msg, dict): continue
    content = msg.get("content")
    if not isinstance(content, list): continue
    for block in content:
        if not isinstance(block, dict): continue
        if block.get("type") == "tool_use":
            name = block.get("name") or ""
            inp = block.get("input") or {}
            if not isinstance(inp, dict): inp = {}
            all_tools.append(name)
            if name == "Skill":
                called = inp.get("skill") or inp.get("name") or ""
                skills_called.append(called)

# also pick up final result prose
final_text = ""
for ev in events:
    if ev.get("type") == "result":
        final_text = (ev.get("result") or "")[:500]

skill_engaged = any(s in ("helix", "helix:helix") for s in skills_called)

rec = {
    "id": id_,
    "kind": kind,
    "prompt": prompt,
    "expected": expected,
    "variant": variant,
    "skill_engaged": skill_engaged,
    "skills_called": skills_called,
    "tools_used": all_tools,
    "result_prose_head": final_text,
    "evidence": evidence,
    "probe_rc": rc,
}
with open(resultfile, "a", encoding="utf-8") as f:
    f.write(json.dumps(rec) + "\n")
PY
}

# ---------------------------------------------------------------------------
# Parallel scheduler
# ---------------------------------------------------------------------------
process_variant() {
    local variant="$1"
    install_variant "$variant"

    local resultfile="$RESULTS_DIR/${variant}.jsonl"
    : > "$resultfile"

    local runroot
    runroot="$(mktemp -d -p "$TMP_ROOT" "ablate-${variant}.XXXXXX")"
    echo "[ablate] variant=$variant runroot=$runroot"

    local pids=()
    local i=0
    for kind in positive negative ambiguous; do
        local evalfile
        case "$kind" in
            positive) evalfile="$EVAL_DIR/helix-positive.jsonl" ;;
            negative) evalfile="$EVAL_DIR/helix-negative.jsonl" ;;
            ambiguous) evalfile="$EVAL_DIR/helix-ambiguous.jsonl" ;;
        esac
        while IFS= read -r line; do
            [[ -z "$line" ]] && continue
            # row filter
            if [[ -n "${ROWS:-}" ]]; then
                local rid
                rid=$(printf '%s' "$line" | python3 -c 'import json,sys;print(json.loads(sys.stdin.read())["id"])')
                if ! grep -qw "$rid" <<<"$ROWS"; then
                    continue
                fi
            fi
            i=$((i+1))
            local rid_short=$(printf '%s' "$line" | python3 -c 'import json,sys;print(json.loads(sys.stdin.read())["id"])')
            local rundir="$runroot/$rid_short"
            run_row "$kind" "$line" "$variant" "$rundir" "$resultfile" &
            pids+=($!)
            # throttle
            if (( ${#pids[@]} >= PARALLEL )); then
                wait -n
                # rebuild pids array — drop any that have finished
                local newpids=()
                for p in "${pids[@]}"; do
                    if kill -0 "$p" 2>/dev/null; then newpids+=("$p"); fi
                done
                pids=("${newpids[@]}")
            fi
        done < "$evalfile"
    done

    # final drain
    for p in "${pids[@]}"; do
        wait "$p" 2>/dev/null || true
    done

    echo "[ablate] variant=$variant complete: $(wc -l < "$resultfile") rows in $resultfile"
}

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
if [[ $# -eq 0 ]]; then
    echo "usage: $0 <variant> | --all | --restore" >&2
    exit 1
fi

case "$1" in
    --all)
        for v in "${VARIANTS_ALL[@]}"; do
            process_variant "$v"
        done
        ;;
    --restore)
        install_variant baseline
        ;;
    *)
        process_variant "$1"
        ;;
esac
