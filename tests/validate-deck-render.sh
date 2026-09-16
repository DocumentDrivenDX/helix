#!/usr/bin/env bash
# Deck render lane. Geometry half always runs when node and pptxgenjs are present; the raster half runs when
# LibreOffice and pdftoppm are present. Without node or pptxgenjs the lane SKIPS with a message (exit 0), so it
# can sit in `just test` on every host; set DECK_RENDER_REQUIRED=1 to make a skip a failure (CI with the toolchain).
#
# What it proves:
#   1. the renderer's pure libraries pass their unit tests (node --test)
#   2. the catalog example renders in all four looks and deck-qa.py finds nothing blocking (geometry)
#   3. the renderer and check-deliverable.py parse the example's units the same way
#   4. a deck with a known text collision and a table past the margin is CAUGHT by deck-qa.py
#   5. a script whose text cannot fit makes the renderer exit 1 with a message, and deck-qa.py blocks the autofit
#   6. with no icon rasterizer on PATH, the render still succeeds and says badges fell back to numbers
#   7. (raster hosts) the example rasterizes and, when the pptx skill is installed, validates
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
scripts="$repo_root/skills/helix/scripts"
renderer="$scripts/render-deck.js"
qa="$scripts/deck-qa.py"
checker="$scripts/check-deliverable.py"
example="$repo_root/workflows/activities/06-iterate/artifacts/deliverable/example.md"
overflow="$repo_root/tests/fixtures/validate-deck-render/overflow-deck.md"
icons="$repo_root/tests/fixtures/validate-deck-render/icons-deck.md"
tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT
fail() { printf 'deck render validation failed: %s\n' "$*" >&2; exit 1; }
skip() { if [ "${DECK_RENDER_REQUIRED:-0}" = 1 ]; then fail "$*"; fi; echo "SKIP: deck render lane: $*"; exit 0; }

command -v node >/dev/null 2>&1 || skip "node not installed"
for cand in "${PPTXGENJS_NODE_PATH:-}" "$scripts/node_modules" "$repo_root/node_modules"; do
  [ -n "$cand" ] && [ -d "$cand/pptxgenjs" ] && export NODE_PATH="$cand${NODE_PATH:+:$NODE_PATH}" && break
done
node -e "require('pptxgenjs')" 2>/dev/null || skip "pptxgenjs not resolvable (npm ci in skills/helix/scripts, or set PPTXGENJS_NODE_PATH)"

# 1. library unit tests
node --test "$repo_root/tests/render/" >"$tmpdir/unit.log" 2>&1 || fail "library unit tests: $(tail -30 "$tmpdir/unit.log")"
echo "render libraries: unit tests pass"

# 2. four looks, geometry only
for look in editorial technical bold classic; do
  node "$renderer" "$example" "$tmpdir/example-$look.pptx" --look "$look" >"$tmpdir/render-$look.log" 2>&1 \
    || fail "render-deck.js failed for look $look: $(cat "$tmpdir/render-$look.log")"
  python3 "$qa" "$tmpdir/example-$look.pptx" --no-raster >"$tmpdir/qa-$look.log" 2>&1 \
    || fail "deck-qa.py blocking findings for look $look: $(grep -E 'BLOCKING|^FAIL' "$tmpdir/qa-$look.log")"
done
echo "four looks: render and pass geometry checks"

# 3. parser agreement
python3 "$checker" "$example" --dump-units >"$tmpdir/py-units.json"
node -e '
const { parseScript } = require(process.argv[1] + "/lib/script");
const fs = require("fs");
const js = parseScript(fs.readFileSync(process.argv[2], "utf8")).units.map(u => ({ n: u.n, title: u.title, pattern: u.pattern, bullets: u.body, visual: u.visual }));
const py = JSON.parse(fs.readFileSync(process.argv[3], "utf8"));
const a = JSON.stringify(js), b = JSON.stringify(py);
if (a !== b) { console.error("renderer and checker parse units differently:\n" + a.slice(0, 600) + "\n---\n" + b.slice(0, 600)); process.exit(1); }
' "$scripts" "$example" "$tmpdir/py-units.json" || fail "unit parsers disagree"
echo "parsers: renderer and checker agree on the example's units"

# 4. deck-qa catches known defects
node "$repo_root/tests/render/make-broken-deck.js" "$tmpdir/broken.pptx" >/dev/null 2>&1 || fail "could not write the broken deck"
if python3 "$qa" "$tmpdir/broken.pptx" --no-raster >"$tmpdir/broken.log" 2>&1; then fail "deck-qa.py passed a deck with a collision and an overflowing table"; fi
grep -q 'text-collision' "$tmpdir/broken.log" || fail "deck-qa.py missed the text collision: $(cat "$tmpdir/broken.log")"
grep -Eq 'table-overflow|off-slide' "$tmpdir/broken.log" || fail "deck-qa.py missed the table past the margin: $(cat "$tmpdir/broken.log")"
echo "deck-qa.py: catches a text collision and a table past the margin"

# 5. unfit text is reported, not hidden
if node "$renderer" "$overflow" "$tmpdir/overflow.pptx" >"$tmpdir/overflow.log" 2>&1; then fail "render-deck.js exited 0 on a script whose text cannot fit"; fi
grep -q 'does not fit\|clamped' "$tmpdir/overflow.log" || fail "render-deck.js did not say what failed to fit: $(cat "$tmpdir/overflow.log")"
if python3 "$qa" "$tmpdir/overflow.pptx" --no-raster >"$tmpdir/overflow-qa.log" 2>&1; then fail "deck-qa.py passed a deck whose autofit shrinks below the floor"; fi
grep -Eq 'text-autofit|text-overflow' "$tmpdir/overflow-qa.log" || fail "deck-qa.py did not block the shrunken text: $(cat "$tmpdir/overflow-qa.log")"
echo "unfit text: renderer exits 1 with a message; deck-qa.py blocks"

# 6. icon fallback
mkdir -p "$tmpdir/bin"; ln -s "$(command -v node)" "$tmpdir/bin/node"; ln -s "$(command -v python3)" "$tmpdir/bin/python3"
PATH="$tmpdir/bin" node "$renderer" "$icons" "$tmpdir/noicons.pptx" >"$tmpdir/noicons.log" 2>&1 || fail "render failed without a rasterizer: $(cat "$tmpdir/noicons.log")"
grep -q 'badges fall back to numbers' "$tmpdir/noicons.log" || fail "no fallback message without a rasterizer: $(cat "$tmpdir/noicons.log")"
node "$renderer" "$icons" "$tmpdir/icons.pptx" >"$tmpdir/icons.log" 2>&1 || fail "icon fixture failed to render: $(cat "$tmpdir/icons.log")"
python3 "$qa" "$tmpdir/icons.pptx" --no-raster >/dev/null 2>&1 || fail "icon fixture has blocking geometry findings"
echo "icons: render succeeds without a rasterizer and says so; with one, the badges pass geometry"

# 7. raster hosts
if command -v soffice >/dev/null 2>&1 || [ -x /Applications/LibreOffice.app/Contents/MacOS/soffice ]; then
  validator="${PPTX_VALIDATOR:-}"
  if [ -z "$validator" ]; then
    validator="$(find "$HOME/Library/Application Support/Claude/local-agent-mode-sessions/skills-plugin" -path '*/skills/pptx/scripts/office/validate.py' 2>/dev/null | head -1 || true)"
  fi
  if [ -n "$validator" ] && [ -f "$validator" ]; then
    vpython="${PPTX_VALIDATOR_PYTHON:-python3}"
    if "$vpython" -c "import lxml, defusedxml" 2>/dev/null; then
      "$vpython" "$validator" "$tmpdir/example-editorial.pptx" >"$tmpdir/validate.log" 2>&1 \
        || fail "pptx validator rejected the render: $(tail -20 "$tmpdir/validate.log")"
      echo "pptx validator: pass"
    else
      echo "pptx validator: skipped ($vpython lacks lxml/defusedxml; set PPTX_VALIDATOR_PYTHON)"
    fi
  else
    echo "pptx validator: skipped (pptx skill not found; set PPTX_VALIDATOR)"
  fi
  python3 "$qa" "$tmpdir/example-editorial.pptx" --out "$tmpdir/qa" >"$tmpdir/qa.log" 2>&1 \
    || fail "deck-qa.py reported blocking findings on raster: $(grep -E 'BLOCKING|^FAIL' "$tmpdir/qa.log")"
  grep -E '^(OK|FAIL)|rasterized|raster skipped|raster failed' "$tmpdir/qa.log"
else
  echo "raster: skipped (no LibreOffice on this host)"
fi
echo "OK: deck render lane"
