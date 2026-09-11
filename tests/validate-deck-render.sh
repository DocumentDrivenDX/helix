#!/usr/bin/env bash
# Deck render loop: render the catalog deliverable example to .pptx, run the
# pptx file validator (when the Anthropic pptx skill is on this host), then
# deck-qa.py; fail on any blocking geometry finding.
#
# pptxgenjs must be resolvable by node: set NODE_PATH, or PPTXGENJS_NODE_PATH
# to a node_modules directory that holds pptxgenjs@3.12.0.
# PPTX_VALIDATOR may name the skill's scripts/office/validate.py and
# PPTX_VALIDATOR_PYTHON a python with lxml and defusedxml.
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
renderer="$repo_root/skills/helix/scripts/render-deck.js"
qa="$repo_root/skills/helix/scripts/deck-qa.py"
example="$repo_root/workflows/activities/06-iterate/artifacts/deliverable/example.md"
tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT
fail() { printf 'deck render validation failed: %s\n' "$*" >&2; exit 1; }

for cand in "${PPTXGENJS_NODE_PATH:-}" "$repo_root/skills/helix/scripts/node_modules" "$repo_root/node_modules"; do
  [ -n "$cand" ] && [ -d "$cand/pptxgenjs" ] && export NODE_PATH="$cand${NODE_PATH:+:$NODE_PATH}" && break
done
node -e "require('pptxgenjs')" 2>/dev/null || fail "pptxgenjs not resolvable; npm i pptxgenjs@3.12.0 and set PPTXGENJS_NODE_PATH"

node "$renderer" "$example" "$tmpdir/example.pptx" >"$tmpdir/render.log" 2>&1 \
  || fail "render-deck.js failed: $(cat "$tmpdir/render.log")"
[ -s "$tmpdir/example.pptx" ] || fail "renderer wrote no .pptx"

validator="${PPTX_VALIDATOR:-}"
if [ -z "$validator" ]; then
  # several plugin versions may be installed; the newest knows pptxgenjs's notesMasterIdLst placement
  validator="$(ls -t "$HOME/Library/Application Support/Claude/local-agent-mode-sessions/skills-plugin"/*/*/skills/pptx/scripts/office/validate.py 2>/dev/null | head -1 || true)"
fi
if [ -n "$validator" ] && [ -f "$validator" ]; then
  vpython="${PPTX_VALIDATOR_PYTHON:-python3}"
  if "$vpython" -c "import lxml, defusedxml" 2>/dev/null; then
    "$vpython" "$validator" "$tmpdir/example.pptx" >"$tmpdir/validate.log" 2>&1 \
      || fail "pptx validator rejected the render: $(tail -20 "$tmpdir/validate.log")"
    echo "pptx validator: pass"
  else
    echo "pptx validator: skipped ($vpython lacks lxml/defusedxml; set PPTX_VALIDATOR_PYTHON)"
  fi
else
  echo "pptx validator: skipped (pptx skill not found; set PPTX_VALIDATOR)"
fi

python3 "$qa" "$tmpdir/example.pptx" --out "$tmpdir/qa" >"$tmpdir/qa.log" 2>&1 \
  || fail "deck-qa.py reported blocking findings:
$(grep -E 'BLOCKING|^FAIL' "$tmpdir/qa.log")"
grep -E '^(OK|FAIL)|rasterized|raster skipped' "$tmpdir/qa.log"
echo "OK: catalog deliverable example renders, validates, and passes deck-qa.py"
