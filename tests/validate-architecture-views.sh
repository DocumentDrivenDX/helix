#!/usr/bin/env bash
# Exercise skills/helix/scripts/architecture_views.py on a project shaped unlike the one it came from:
# a nested HELIX root, no [theme] (the default palette), no facts script, and evidence that drifts
# (workflows/references/architecture-model.md).
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python3 -c 'import tomllib' 2>/dev/null || { echo "SKIP: architecture_views.py needs Python 3.11 (tomllib)"; exit 0; }
H="$repo_root/skills/helix/scripts"; T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
mkdir -p "$T/proj/svc/docs/helix/02-design"
cd "$T/proj"
printf 'flows:\n  - id: helix\n    root: svc/docs/helix/\n' > .helix.yml
printf 'def main():\n    return 1\n' > svc/app.py
cat > svc/docs/helix/02-design/architecture-model.toml <<'TOML'
[system]
id = "svc"
[[element]]
id = "svc"
name = "Service"
kind = "system"
status = "built"
evidence = [{ path = "svc/app.py", contains = "def main" }]
[[element]]
id = "db"
name = "Database"
kind = "store"
status = "decided"
evidence = [{ path = "svc/app.py", contains = "return 1" }]
[[relation]]
from = "svc"
to = "db"
label = "reads"
status = "decided"
evidence = [{ path = "svc/app.py", contains = "return 1" }]
[[view]]
id = "context"
elements = ["svc", "db"]
TOML
printf '# Architecture\n\n<!-- architecture-view: context -->\n<!-- /architecture-view -->\n' > svc/docs/helix/02-design/architecture.md
python3 "$H/architecture_views.py" --check >/dev/null 2>&1 && { echo "FAIL: an empty view should be stale"; exit 1; }
python3 "$H/architecture_views.py" | grep -q "written"
python3 "$H/architecture_views.py" --check | grep -q "match"
grep -q "blue outline = Service's code" svc/docs/helix/02-design/architecture.md
grep -q 'svc -.->|"reads"| db' svc/docs/helix/02-design/architecture.md
sed -i.bak 's/return 1/return 2/' svc/app.py
out="$(python3 "$H/architecture_views.py" --check 2>&1)" && { echo "FAIL: drifted evidence should fail"; exit 1; }
grep -q "no longer contains 'return 1'" <<<"$out" || { echo "FAIL: expected the drift: $out"; exit 1; }
sed -i.bak 's/return 2/return 1/' svc/app.py

# The page views: a stack, a cast, a deployment drawn as SVG, and a journey that walks relations.
python3 - svc/docs/helix/02-design/architecture-model.toml <<'PY'
import re, sys
path = sys.argv[1]
text = open(path).read()
text = text.replace('kind = "system"\n', 'kind = "system"\nlayer = "Service"\njob = "Answers requests."\ntier = 1\nzone = "Apps"\n')
text = text.replace('kind = "store"\n', 'kind = "store"\nlayer = "Data"\njob = "Keeps rows."\ntier = 2\nzone = "Data"\n')
text = text.replace('label = "reads"\n', 'label = "reads"\nstep = 1\nnote = "The service reads a row."\n')
text += """
[[view]]
id = "stack"
type = "stack"
elements = ["svc", "db"]
[[view]]
id = "cast"
type = "cast"
elements = ["svc", "db"]
[[view]]
id = "where"
type = "deployment"
elements = ["svc", "db"]
[[journey]]
id = "read"
title = "A read"
[[journey.step]]
from = "svc"
to = "db"
label = "reads a row"
[[view]]
id = "read"
type = "journey"
journey = "read"
elements = []
[[view]]
id = "guide"
type = "field-guide"
document = "field-guide.html"
title = "One read."
takeaway = "A reader asks; the service reads."
elements = ["svc", "db"]
[[view.group]]
id = "app"
label = "Service"
elements = ["svc"]
[[view.group]]
id = "data"
label = "Data"
elements = ["db"]
"""
open(path, "w").write(text)
PY
for v in stack cast where read; do printf '<!-- architecture-view: %s -->\n<!-- /architecture-view -->\n' "$v" >> svc/docs/helix/02-design/architecture.md; done
python3 "$H/architecture_views.py" | grep -q "written"
doc=svc/docs/helix/02-design/architecture.md
grep -q "| Service | \*\*Service\*\* |" "$doc" || { echo "FAIL: stack: $(cat "$doc")"; exit 1; }
grep -q "| \*\*Database\*\* | Keeps rows. | decided, not built |" "$doc" || { echo "FAIL: cast"; exit 1; }
grep -q "svc->>db: 1 · reads a row" "$doc" || { echo "FAIL: journey"; exit 1; }
grep -q "\[!\[where\](architecture-views/where.svg)\](architecture-views/where.svg)" "$doc" || { echo "FAIL: deployment link"; exit 1; }
grep -q ">reads</text>" svc/docs/helix/02-design/architecture-views/where.svg || { echo "FAIL: deployment svg"; exit 1; }
guide=svc/docs/helix/02-design/field-guide.html
grep -q '<g id="svc">' "$guide" && grep -q '<g id="db">' "$guide" || { echo "FAIL: field guide boxes"; exit 1; }
grep -q "01 / SERVICE" "$guide" && grep -q "02 / DATA" "$guide" || { echo "FAIL: field guide lanes"; exit 1; }
grep -q "<li><strong>Reads.</strong> The service reads a row.</li>" "$guide" || { echo "FAIL: field guide walkthrough"; exit 1; }
grep -q "<script" "$guide" && { echo "FAIL: the field guide carries no script"; exit 1; }
python3 "$H/architecture_views.py" --check | grep -q "match"
# A field guide without lanes, or with a numbered step off its plate, is refused before anything is written.
sed -i.bak '/^id = "app"$/,/^elements = \["svc"\]$/d; /^id = "data"$/,/^elements = \["db"\]$/d; /^\[\[view.group\]\]$/d' svc/docs/helix/02-design/architecture-model.toml
out="$(python3 "$H/architecture_views.py" --check 2>&1)" && { echo "FAIL: a field guide without lanes should be refused"; exit 1; }
grep -q "view guide: a field guide needs groups" <<<"$out" || { echo "FAIL: expected the lanes problem: $out"; exit 1; }
mv svc/docs/helix/02-design/architecture-model.toml.bak svc/docs/helix/02-design/architecture-model.toml
python3 "$H/architecture_views.py" --check | grep -q "match"
echo "OK: architecture_views.py: nested HELIX root, default theme, no facts hook, evidence drift, and the stack, cast, deployment, journey and field-guide views"
