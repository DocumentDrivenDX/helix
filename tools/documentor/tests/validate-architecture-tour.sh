#!/usr/bin/env bash
# Exercise `documentor tour`: a deployment view becomes Eraser input
# (zones as groups, boxes inside them, routed connectors with pinned labels), a journey becomes
# the walkthrough, a ux-builder theme colors it, and a model change redraws it with no hand edit.
# The render step (js/render.mjs) runs only when Node, @eraserlabs/diagrams (ERASER_MODULES),
# and a Chromium (CHROMIUM_PATH) are present.
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
rg="${DOCUMENTOR:-documentor}"
command -v "$rg" >/dev/null 2>&1 || { echo "FAIL: documentor is not on PATH; run the tests with uv (just test)"; exit 1; }
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
mkdir -p "$T/proj/docs/helix/02-design"
cd "$T/proj"
printf 'def main():\n    return 1\n' > app.py
# A local @ux-builder/tokens build with two themes, so the test never fetches the package.
printf 'flows:\n  - id: helix\n    root: docs/helix/\npublish:\n  theme: {tokens: tokens}\n' > .helix.yml
mkdir -p tokens/resolved
cat > tokens/manifest.json <<'JSON'
{"themes": [{"name": "blueprint", "default": "dark", "appearances": ["dark"]},
            {"name": "helix", "default": "light", "appearances": ["light"]}]}
JSON
python3 - <<'PY'
import json
def tokens(ground, accent, text):
    return {"tokens": {"piq-color-ground": ground, "piq-color-surface": ground, "piq-color-surface-sunken": ground,
                       "piq-color-border": text, "piq-color-ground-recessed": text, "piq-color-text": text,
                       "piq-color-text-strong": text, "piq-color-text-muted": text, "piq-color-accent": accent,
                       "piq-font-body": "Inter, sans-serif"}}
json.dump(tokens("#0D1520", "#4FB3FF", "#E6EDF5"), open("tokens/resolved/blueprint.dark.json", "w"))
json.dump(tokens("#FFFFFF", "#2F6F8F", "#2E3440"), open("tokens/resolved/helix.light.json", "w"))
PY
M=docs/helix/02-design/architecture-model.toml
cat > "$M" <<'TOML'
[system]
id = "svc"
name = "Service"
[[element]]
id = "user"
name = "Reader"
kind = "person"
status = "built"
tier = 1
zone = "People"
evidence = [{ path = "app.py", contains = "def main" }]
[[element]]
id = "svc"
name = "Service"
detail = "the app's own code"
kind = "system"
status = "built"
tier = 2
zone = "Apps"
evidence = [{ path = "app.py", contains = "def main" }]
[[element]]
id = "db"
name = "Database"
detail = "rows, the app's"
kind = "store"
status = "decided"
tier = 3
zone = "Data"
evidence = [{ path = "app.py", contains = "return 1" }]
[[relation]]
from = "user"
to = "svc"
label = "HTTPS"
status = "built"
evidence = [{ path = "app.py", contains = "def main" }]
[[relation]]
from = "svc"
to = "db"
label = "reads"
why = "rows live there"
status = "decided"
evidence = [{ path = "app.py", contains = "return 1" }]
[[journey]]
id = "read"
title = "A read"
takeaway = "One request, one [row](app.py)."
[[journey.step]]
from = "user"
to = "svc"
label = "asks for a row"
[[journey.step]]
from = "svc"
to = "db"
label = "reads it"
[[view]]
id = "deployment"
type = "deployment"
elements = ["user", "svc", "db"]
TOML

$rg tour --root . --view deployment --journey read --theme blueprint --out out >/dev/null
python3 - out <<'PY'
import json, sys
out = sys.argv[1]
d = json.load(open(f"{out}/eraser.json"))
walk = json.load(open(f"{out}/walkthrough.json"))
theme = json.load(open(f"{out}/theme.json"))
groups = {e["id"] for e in d["entities"] if e["tag"] == "Group"}
shapes = {e["id"]: e for e in d["entities"] if e["tag"] == "Shape"}
assert groups == {"zone-people", "zone-apps", "zone-data"}, groups
assert shapes["db"]["containerId"] == "zone-data", shapes["db"]
assert shapes["db"].get("borderStyle") == "dashed", "a decided element is drawn dashed"
assert shapes["svc"]["borderColor"] == theme["accent"], "the system's own code carries the accent"
assert "’" in shapes["db"]["texts"][1]["text"], "an apostrophe is typographic, not sanitized"
links = {c["id"]: c for c in d["connections"]}
assert set(links) == {"user--svc", "svc--db"}, links
for c in links.values():
    assert c["fromPort"] == "bottom" and c["toPort"] == "top", c
    assert len(c["points"]) >= 2 and "labelPlacement" in c, c
assert links["svc--db"].get("lineStyle") == "dashed"
assert [s["edge"] for s in walk["steps"]] == ["user--svc", "svc--db"], walk
assert walk["steps"][1]["caption"] == "Reads it: rows live there.", walk["steps"][1]
assert walk["lead"] == "One request, one row.", "links are reduced to their words"
assert theme["id"] == "blueprint", theme
assert theme["accent"] == "#4FB3FF" and theme["ground"] == "#0D1520", "the colors are the ux-builder theme's"
PY

# A model change redraws it: move the database beside the service, and its box changes zone.
sed -i.bak 's/tier = 3/tier = 2/; s/zone = "Data"/zone = "Apps"/' "$M"
$rg tour --root . --view deployment --theme helix --out moved >/dev/null
python3 - moved <<'PY'
import json, sys
d = json.load(open(f"{sys.argv[1]}/eraser.json"))
shapes = {e["id"]: e for e in d["entities"] if e["tag"] == "Shape"}
assert shapes["db"]["containerId"] == "zone-apps", shapes["db"]
walk = json.load(open(f"{sys.argv[1]}/walkthrough.json"))
assert [s["edge"] for s in walk["steps"]] == ["user--svc", "svc--db"], "no journey: the view's relations"
PY
out="$($rg tour --root . --view deployment --theme nonesuch --out x 2>&1)" \
  && { echo "FAIL: an unknown theme should be refused"; exit 1; }
grep -q "no theme named nonesuch" <<<"$out" || { echo "FAIL: expected the refusal: $out"; exit 1; }

modules="${ERASER_MODULES:-}"
if command -v node >/dev/null && [ -n "$modules" ] && [ -d "$modules/@eraserlabs/diagrams" ] && [ -n "${CHROMIUM_PATH:-}" ]; then
  node "$repo_root/src/documentor/architecture/js/render.mjs" out | grep -q "(0 warnings)" || { echo "FAIL: render warned"; exit 1; }
  grep -q 'data-mdp-id="svc--db"' out/present.html
  grep -q 'id="play"' out/present.html && grep -q 'function camFor' out/present.html \
    || { echo "FAIL: the presentation should play on the stage, with its camera"; exit 1; }
  echo "architecture_tour: rendered"
else
  echo "architecture_tour: render skipped (set ERASER_MODULES and CHROMIUM_PATH)"
fi
echo "PASS: architecture_tour"
