#!/usr/bin/env bash
# Claude Code verify: layout + init-JSON load probe (always) + optional LLM
# functional check (TEST_FUNCTIONAL=1).
#
# Three install modes use different on-disk + load layouts:
#   default (per-PR): no persistent install. We load via `--plugin-dir
#     /workspace/helix` for the init-JSON probe AND the static layout check
#     walks the same path. No symlinks, no registry writes.
#   TEST_LOCAL_MARKETPLACE=1: install.sh persisted to ~/.claude/plugins/cache.
#   TEST_PUBLISHED=1: same persistent layout as LOCAL_MARKETPLACE but cloned
#     from GitHub HEAD.

set -euo pipefail

SHARED_VERIFY="/workspace/helix/tests/install/shared/verify-skill-layout.sh"

# Locate the skill on disk.
if [[ "${TEST_PUBLISHED:-}" == "1" || "${TEST_LOCAL_MARKETPLACE:-}" == "1" ]]; then
  SKILL_ROOT="$(ls -d "$HOME"/.claude/plugins/cache/*/helix/*/skills/helix 2>/dev/null | head -1)"
  if [[ -z "$SKILL_ROOT" ]]; then
    SKILL_ROOT="$(ls -d "$HOME"/.claude/plugins/cache/*/skills/helix 2>/dev/null | head -1)"
  fi
  if [[ -z "$SKILL_ROOT" ]]; then
    echo "FAIL: no skill found under ~/.claude/plugins/cache/"
    echo "contents of ~/.claude/plugins/cache/:"
    find "$HOME/.claude/plugins/cache/" -maxdepth 4 2>/dev/null || echo "(cache dir missing)"
    exit 1
  fi
  echo "→ skill resolved at: $SKILL_ROOT"
  echo "→ claude plugin list:"
  claude plugin list 2>&1
  # Reject persisted plugins that loaded with errors.
  if claude plugin list 2>&1 | grep -q "failed to load"; then
    echo "FAIL: plugin list reports 'failed to load'"
    exit 1
  fi
else
  SKILL_ROOT="/workspace/helix/skills/helix"
fi

echo "→ static layout checks"
bash "$SHARED_VERIFY" "$SKILL_ROOT"

# init-JSON load probe — ALWAYS runs (cheap, deterministic).
# Asserts the plugin + skill register cleanly when claude starts the session.
# Requires auth (ANTHROPIC_API_KEY env or mounted ~/.claude/.credentials.json).
echo
echo "→ init-JSON load probe (asserts plugin loads + helix:helix registers)"
if [[ -n "${ANTHROPIC_API_KEY:-}" || -f "$HOME/.claude/.credentials.json" ]]; then
  PROBE_OUT="$(mktemp)"
  PLUGIN_DIR_ARG=""
  if [[ "${TEST_PUBLISHED:-}" != "1" && "${TEST_LOCAL_MARKETPLACE:-}" != "1" ]]; then
    PLUGIN_DIR_ARG="--plugin-dir /workspace/helix"
  fi
  set +e
  echo "ack" | claude $PLUGIN_DIR_ARG -p --output-format stream-json --verbose \
    >"$PROBE_OUT" 2>&1
  RC=$?
  set -e
  INIT_LINE="$(grep '"subtype":"init"' "$PROBE_OUT" | head -1 || true)"
  if [[ -z "$INIT_LINE" ]]; then
    echo "FAIL: no init line in claude -p output (rc=$RC)"
    head -20 "$PROBE_OUT"
    rm -f "$PROBE_OUT"
    exit 1
  fi
  python3 - "$INIT_LINE" <<'PY' || { rm -f "$PROBE_OUT"; exit 1; }
import json, sys
init = json.loads(sys.argv[1])
plugins = init.get("plugins", [])
skills = init.get("skills", [])
mcp = init.get("mcp_servers", [])
helix_plugin = [p for p in plugins if p.get("name") == "helix"]
if not helix_plugin:
    print(f"FAIL: plugins[] missing helix (got: {[p.get('name') for p in plugins]})", file=sys.stderr)
    sys.exit(1)
if "helix:helix" not in skills:
    print(f"FAIL: skills[] missing helix:helix (got: {skills})", file=sys.stderr)
    sys.exit(1)
helix_mcp_failed = [s for s in mcp if s.get("name", "").startswith("plugin:helix:") and s.get("status") == "failed"]
if helix_mcp_failed:
    print(f"FAIL: plugin's MCP servers failed to load: {[s['name'] for s in helix_mcp_failed]}", file=sys.stderr)
    sys.exit(1)
print(f"ok: plugin helix registered, helix:helix skill loaded, {len(mcp)} MCP server(s) ok")
PY
  rm -f "$PROBE_OUT"
else
  echo "SKIP: no ANTHROPIC_API_KEY and no ~/.claude/.credentials.json — init probe needs auth"
  if [[ "${TEST_PUBLISHED:-}" == "1" ]]; then
    echo "      published install smoke continues with static layout checks only"
  else
    echo "      (set ANTHROPIC_API_KEY in CI secrets, or mount credentials for local dev)"
    echo "FAIL: per-PR install gate requires auth — refusing to claim PASS on static-only checks"
    exit 1
  fi
fi

if [[ "${TEST_FUNCTIONAL:-}" == "1" ]]; then
  if [[ -z "${ANTHROPIC_API_KEY:-}" ]]; then
    echo "FAIL: TEST_FUNCTIONAL=1 but ANTHROPIC_API_KEY not set"
    exit 1
  fi
  echo
  echo "→ LLM functional check: ask Claude to list HELIX modes"
  PLUGIN_DIR_ARG=""
  if [[ "${TEST_PUBLISHED:-}" != "1" && "${TEST_LOCAL_MARKETPLACE:-}" != "1" ]]; then
    PLUGIN_DIR_ARG="--plugin-dir /workspace/helix"
  fi
  RESPONSE="$(echo 'List the HELIX routing modes you can route to. Be concise.' | claude $PLUGIN_DIR_ARG -p 2>&1)"
  echo "response excerpt:"
  echo "$RESPONSE" | head -20
  EXPECTED=("align" "frame" "evolve" "review" "design")
  MISSING=()
  for mode in "${EXPECTED[@]}"; do
    grep -qiF "$mode" <<<"$RESPONSE" || MISSING+=("$mode")
  done
  if (( ${#MISSING[@]} > 0 )); then
    echo "FAIL: response missing expected modes: ${MISSING[*]}"
    exit 1
  fi
  echo "ok: response names align/frame/evolve/review/design"
fi

echo
echo "claude-code scenario: PASS"
