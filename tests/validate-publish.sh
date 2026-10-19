#!/usr/bin/env bash
# Exercise skills/helix/scripts/publish_check.py and publish_site.py against a fixture project:
# provenance stamping, staleness pinned to a section, broken links and paths, the prose budget,
# unmapped watched files, and a site built from the pages (workflows/references/publishing.md).
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
check="$repo_root/skills/helix/scripts/publish_check.py"
site_builder="$repo_root/skills/helix/scripts/publish_site.py"
tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT
fail() { echo "FAIL: $*" >&2; exit 1; }

project="$tmpdir/project"
mkdir -p "$project/docs/helix/02-design" "$project/src" "$project/docs/guide/developer"
cat >"$project/.helix.yml" <<'EOF'
flows:
  - id: helix
    root: docs/helix/
publish:
  out: docs/guide
  flows: [developer]
  site:
    title: Fixture
    repo_url: https://example.test/org/fixture
EOF
cat >"$project/docs/helix/02-design/architecture.md" <<'EOF'
# Architecture

## Deployment

The app deploys as one container behind a proxy.

## Data Flow

A request enters at the proxy.

### Retries

A failed call is retried once.
EOF
printf 'def handle():\n    return 200\n' >"$project/src/app.py"
page="$project/docs/guide/developer/index.md"
cat >"$page" <<'EOF'
<!-- helix:publish flow=developer page=index kind=explanation voice=onboarding budget=800 -->
<!-- helix:source docs/helix/02-design/architecture.md#deployment -->
<!-- helix:source docs/helix/02-design/architecture.md#retries -->
<!-- helix:source src/app.py -->
# Overview

The app runs as one container behind a proxy. Requests reach `src/app.py`, which answers them.
The [architecture record](../../helix/02-design/architecture.md#deployment) has the detail.

```mermaid
flowchart LR
  user --> proxy --> app
```
EOF

run() { python3 "$check" "$@" --root "$project"; }

# Unstamped: every source is stale until the digests are recorded.
run check "$project/docs/guide" >"$tmpdir/out" 2>&1 && fail "an unstamped page should fail"
grep -q "never stamped" "$tmpdir/out" || fail "expected 'never stamped': $(cat "$tmpdir/out")"
run stamp "$page" >/dev/null
grep -Eq "helix:source docs/helix/02-design/architecture.md#deployment sha256:[0-9a-f]{16}" "$page" \
  || fail "stamp should record a 16-character digest"
run check "$project/docs/guide" >"$tmpdir/out" 2>&1 || fail "a stamped page should pass: $(cat "$tmpdir/out")"

# Staleness is pinned to the cited section: a change elsewhere in the file does not stale the page.
sed -i.bak 's/A request enters at the proxy./A request enters at the load balancer./' "$project/docs/helix/02-design/architecture.md"
run check "$project/docs/guide" >"$tmpdir/out" 2>&1 || fail "an uncited section's change should not stale the page"
sed -i.bak 's/one container behind a proxy./two containers behind a proxy./' "$project/docs/helix/02-design/architecture.md"
run check "$project/docs/guide" >"$tmpdir/out" 2>&1 && fail "a cited section's change should stale the page"
grep -Eq "^BLOCKING +stale .*architecture.md#deployment changed" "$tmpdir/out" || fail "expected stale: $(cat "$tmpdir/out")"
run stamp "$page" >/dev/null
# A pin can name a deeper heading: the H3 runs to the next heading of its level or higher.
sed -i.bak 's/retried once./retried twice./' "$project/docs/helix/02-design/architecture.md"
run check "$project/docs/guide" >"$tmpdir/out" 2>&1 && fail "a cited H3's change should stale the page"
grep -Eq "^BLOCKING +stale .*architecture.md#retries changed" "$tmpdir/out" || fail "expected stale H3: $(cat "$tmpdir/out")"
run stamp "$page" >/dev/null

# A missing source, a broken link, and a missing path are blocking.
cp "$page" "$tmpdir/page.bak"
printf '\nSee [the runbook](../../runbook.md) and `src/missing.py`.\n' >>"$page"
run check "$project/docs/guide" >"$tmpdir/out" 2>&1 && fail "a broken link should fail"
grep -Eq "^BLOCKING +broken-link " "$tmpdir/out" || fail "expected broken-link: $(cat "$tmpdir/out")"
grep -Eq "^BLOCKING +missing-path .*src/missing.py" "$tmpdir/out" || fail "expected missing-path: $(cat "$tmpdir/out")"
cp "$tmpdir/page.bak" "$page"
# A file the reader is told to create is named in the header, and only that file is excused.
printf '<!-- helix:creates tests/test_new.py -->\nCreate `tests/test_new.py`, not `tests/test_other.py`.\n' >>"$page"
run check "$project/docs/guide" >"$tmpdir/out" 2>&1 && fail "an unnamed missing path should still block"
grep -q "test_new.py" "$tmpdir/out" && fail "a file the header says the reader creates should pass: $(cat "$tmpdir/out")"
grep -Eq "^BLOCKING +missing-path .*test_other.py" "$tmpdir/out" || fail "expected test_other.py missing: $(cat "$tmpdir/out")"
cp "$tmpdir/page.bak" "$page"
sed -i.bak 's|helix:source src/app.py|helix:source src/gone.py|' "$page"
run check "$project/docs/guide" >"$tmpdir/out" 2>&1 && fail "a missing source should fail"
grep -Eq "^BLOCKING +missing-source .*src/gone.py" "$tmpdir/out" || fail "expected missing-source: $(cat "$tmpdir/out")"
cp "$tmpdir/page.bak" "$page"

# The page's budget comes from its header; a breach warns, and blocks with --strict-prose.
sed -i.bak 's/budget=800/budget=10/' "$page"
run check "$project/docs/guide" >"$tmpdir/out" 2>&1 || fail "a prose finding alone should only warn"
grep -Eq "^WARNING +prose.budget " "$tmpdir/out" || fail "expected prose.budget: $(cat "$tmpdir/out")"
run check "$project/docs/guide" --strict-prose >"$tmpdir/out" 2>&1 && fail "--strict-prose should block"
sed -i.bak 's/budget=10/budget=800/' "$page"

# A page whose header names no Diátaxis kind, or an unknown one, is reported.
sed -i.bak 's/kind=explanation/kind=essay/' "$page"
run check "$project/docs/guide" >"$tmpdir/out" 2>&1 || fail "an unknown kind should only warn"
grep -Eq "^WARNING +kind .*kind=essay" "$tmpdir/out" || fail "expected kind: $(cat "$tmpdir/out")"
sed -i.bak 's/kind=essay/kind=explanation/' "$page"

# A page that matches a pattern the project's handling forbids is blocked; so is writing outside
# publish.scope. Both need PyYAML, like the prose check.
if python3 -c 'import yaml' 2>/dev/null; then
  cp "$project/.helix.yml" "$tmpdir/helix.bak"
  printf 'handling:\n  patterns:\n    - "\\\\b[0-9]{3}-[0-9]{2}-[0-9]{4}\\\\b"\n' >>"$project/.helix.yml"
  printf '\nA claimant such as 123-45-6789 appears here.\n' >>"$page"
  run check "$project/docs/guide" >"$tmpdir/out" 2>&1 && fail "a handling pattern should block"
  grep -Eq "^BLOCKING +handling .*handling pattern" "$tmpdir/out" || fail "expected handling: $(cat "$tmpdir/out")"
  cp "$tmpdir/page.bak" "$page"
  run stamp "$page" >/dev/null
  # A generated drawing beside the pages is held to the same patterns.
  mkdir -p "$project/docs/guide/developer/architecture-views"
  printf '<svg><text>claimant 123-45-6789</text></svg>\n' >"$project/docs/guide/developer/architecture-views/x.svg"
  run check "$project/docs/guide" >"$tmpdir/out" 2>&1 && fail "a handling pattern in a drawing should block"
  grep -Eq "^BLOCKING +handling .*x.svg" "$tmpdir/out" || fail "expected handling on the drawing: $(cat "$tmpdir/out")"
  rm -r "$project/docs/guide/developer/architecture-views"
  sed -i.bak 's|^  out: docs/guide|  out: docs/guide\n  scope: svc|' "$project/.helix.yml"
  run check "$project/docs/guide" >"$tmpdir/out" 2>&1 && fail "pages outside publish.scope should block"
  grep -Eq "^BLOCKING +outside-scope .*outside publish.scope svc" "$tmpdir/out" || fail "expected outside-scope: $(cat "$tmpdir/out")"
  cp "$tmpdir/helix.bak" "$project/.helix.yml"
  # With no publish.out, pages go to guide/ beside the HELIX root, however deep it is.
  python3 - "$repo_root" <<'PY'
import sys
sys.path.insert(0, sys.argv[1] + "/skills/helix/scripts")
from publish_check import publish_out
assert publish_out({"flows": [{"root": "idrflow/docs/helix/"}]}) == "idrflow/docs/guide"
assert publish_out({"flows": [{"root": "docs/helix"}]}) == "docs/guide"
assert publish_out({"flows": [{"root": "docs/helix"}], "publish": {"out": "site/"}}) == "site"
PY
fi

# A file the flow watches (a new ADR) that no page cites is reported.
mkdir -p "$project/docs/helix/02-design/adr"
printf '# ADR-001: Use one container\n' >"$project/docs/helix/02-design/adr/ADR-001-one-container.md"
run check "$project/docs/guide" >"$tmpdir/out" 2>&1 || fail "unmapped should only warn"
grep -Eq "^WARNING +unmapped .*ADR-001-one-container.md" "$tmpdir/out" || fail "expected unmapped: $(cat "$tmpdir/out")"
cp "$project/.helix.yml" "$tmpdir/helix-ignore.bak"
sed -i.bak 's|^  flows: \[developer\]|  flows: [developer]\n  ignore: ["{helix}/02-design/adr/ADR-001-*.md"]|' "$project/.helix.yml"
run check "$project/docs/guide" >"$tmpdir/out" 2>&1 || true
if python3 -c 'import yaml' 2>/dev/null; then
  grep -q "ADR-001-one-container.md" "$tmpdir/out" && fail "publish.ignore should silence the ADR: $(cat "$tmpdir/out")"
fi
cp "$tmpdir/helix-ignore.bak" "$project/.helix.yml"

# The site: a section per flow, links rewritten, sources listed, Mermaid rendered client-side. A
# copied HTML page's links are rewritten too, relative to where it lands.
printf '<a href="index.md">Overview</a>\n' >"$project/docs/guide/developer/plate.html"
printf '\nThe [plate](plate.html) draws it.\n' >>"$page"
python3 "$site_builder" --root "$project" --site "$tmpdir/site" >"$tmpdir/site.out" 2>&1 || fail "site build failed: $(cat "$tmpdir/site.out")"
content="$tmpdir/site/content/developer/_index.md"
[ -f "$content" ] || fail "the flow's index page should become the section page"
grep -q "https://example.test/org/fixture/blob/main/docs/helix/02-design/architecture.md#deployment" "$content" \
  || fail "a link to a repository file should resolve to repo_url: $(cat "$content")"
grep -q "docs/helix/02-design/architecture.md#deployment" "$content" || fail "the page's sources should be in its front matter"
grep -q "^kind: explanation" "$content" || fail "the page's kind should be in its front matter"
grep -q 'href="../../../../developer/"' "$tmpdir/site/static/files/docs/guide/developer/plate.html" \
  || fail "a copied HTML page's links should become relative site links: $(cat "$tmpdir/site/static/files/docs/guide/developer/plate.html")"
if command -v hugo >/dev/null; then
  [ -f "$tmpdir/site/public/index.html" ] || fail "hugo should build the home page"
  grep -q 'class="mermaid"' "$tmpdir/site/public/developer/index.html" || fail "a mermaid block should render as pre.mermaid"
  grep -q "Built from 3 sources" "$tmpdir/site/public/developer/index.html" || fail "the page should list its sources"
  built="and built it with hugo"
else
  built="(hugo not installed; build skipped)"
fi

echo "OK: publish_check.py stamps, pins staleness to sections, blocks broken links, paths and sources, applies budgets, reports unmapped files and a missing page kind, blocks handling patterns and writes outside scope; publish_site.py wrote the site $built"
