#!/usr/bin/env bash
# Exercise `documentor check-pages`, `stamp`, and `site` against a fixture project:
# provenance stamping, staleness pinned to a section, broken links and paths, the prose budget,
# unmapped watched files, and a site built from the pages (workflows/references/publishing.md).
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
rg="${DOCUMENTOR:-documentor}"
command -v "$rg" >/dev/null 2>&1 || { echo "FAIL: documentor is not on PATH; run the tests with uv (just test)"; exit 1; }
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

run() { local cmd="$1"; shift; [ "$cmd" = check ] && cmd=check-pages; $rg "$cmd" "$@" --root "$project"; }

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
  python3 - <<'PY'
from documentor.lib import publish_out
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
$rg site --root "$project" --site "$tmpdir/site" >"$tmpdir/site.out" 2>&1 || fail "site build failed: $(cat "$tmpdir/site.out")"
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
  grep -q 'class="mermaid' "$tmpdir/site/public/developer/index.html" || fail "a mermaid block should render as pre.mermaid"
  grep -q "Built from 3 sources" "$tmpdir/site/public/developer/index.html" || fail "the page should list its sources"
  [ "$(grep -c "Built from" "$tmpdir/site/public/developer/index.html")" = 1 ] || fail "the sources should be listed once"
  grep -q 'class="card"' "$tmpdir/site/public/index.html" || fail "the home page should have a card per audience"
  grep -q "Overview" "$tmpdir/site/public/index.html" || fail "the home page should list each audience's pages"
  grep -q 'class="kind"' "$tmpdir/site/public/developer/index.html" || fail "the page's kind should sit above its title"
  ! grep -q "hextra" "$tmpdir/site/hugo.yaml" || fail "the default site needs no theme module"
  built="and built it with hugo"
else
  built="(hugo not installed; build skipped)"
fi

# The Hextra target writes the same content with the theme as a module, and its home lists the pages.
printf '  site: {title: Fixture, target: hextra}\n' >/dev/null
$rg site --root "$project" --site "$tmpdir/hextra" --target hextra --no-build >"$tmpdir/site.out" 2>&1 || fail "hextra scaffold failed: $(cat "$tmpdir/site.out")"
grep -q "github.com/imfing/hextra" "$tmpdir/hextra/hugo.yaml" || fail "the hextra site imports the theme"
grep -q "^- \[Overview\](developer/)" "$tmpdir/hextra/content/_index.md" || fail "the hextra home should list each page: $(cat "$tmpdir/hextra/content/_index.md")"

# A page that cites a test names one that exists: a Python node id, or a JS test file and its title.
mkdir -p "$project/tests" "$project/web"
printf 'class TestTurns:\n    def test_a_turn_locks(self):\n        pass\n\ndef test_saves(x):\n    pass\n' >"$project/tests/test_turns.py"
printf 'test("opens the pane", () => {});\n' >"$project/web/pane.test.ts"
cp "$page" "$tmpdir/page-tests.bak"
printf '\nProved by `tests/test_turns.py::TestTurns::test_a_turn_locks`, `tests/test_turns.py::test_saves[case-1]`, and `web/pane.test.ts` "opens the pane".\n' >>"$page"
run stamp "$page" >/dev/null
run check "$project/docs/guide" >"$tmpdir/out" 2>&1 || fail "existing tests should pass: $(cat "$tmpdir/out")"
printf 'And `tests/test_turns.py::test_gone`, and `web/pane.test.ts` "closes the pane".\n' >>"$page"
run check "$project/docs/guide" >"$tmpdir/out" 2>&1 && fail "a missing test should block"
grep -Eq "^BLOCKING +missing-test .*defines no test_gone" "$tmpdir/out" || fail "expected missing-test: $(cat "$tmpdir/out")"
grep -Eq "^BLOCKING +missing-test .*no test titled \"closes the pane\"" "$tmpdir/out" || fail "expected the JS title: $(cat "$tmpdir/out")"
cp "$tmpdir/page-tests.bak" "$page"
run stamp "$page" >/dev/null

# Into a repository's own site instead: a mkdocs site gets the pages under its docs directory and a
# nav fragment; a Hugo site gets them as a content section with front matter. Neither is built here.
printf 'site_name: Fixture\ndocs_dir: site-docs\nnav:\n  - Home: index.md\n' >"$project/mkdocs.yml"
$rg site --root "$project" --target mkdocs --no-build >"$tmpdir/site.out" 2>&1 || fail "mkdocs emit failed: $(cat "$tmpdir/site.out")"
[ -f "$project/site-docs/guide/developer/index.md" ] || fail "the page should land under the mkdocs docs directory"
grep -q "Developers:" "$project/site-docs/guide/nav.yml" || fail "a nav fragment should name the audience: $(cat "$project/site-docs/guide/nav.yml")"
grep -q "https://example.test/org/fixture/blob/main/docs/helix/02-design/architecture.md#deployment" "$project/site-docs/guide/developer/index.md" \
  || fail "repository links should resolve to repo_url in the mkdocs copy"
grep -q "helix:publish" "$project/site-docs/guide/developer/index.md" && fail "the emitted copy should not carry the provenance header"
# When the guide already lives inside the docs directory, nothing is copied or deleted: only the nav.
printf 'site_name: Fixture\ndocs_dir: docs\n' >"$project/mkdocs.yml"
mkdir -p "$project/docs/api" && printf '# API\n' >"$project/docs/api/index.md"
cp "$project/.helix.yml" "$tmpdir/helix-delegate.bak"
printf '  delegate:\n    developer/api: {tool: pdoc, url: ../../api/index.md}\n' >>"$project/.helix.yml"
$rg site --root "$project" --target mkdocs --no-build >"$tmpdir/site.out" 2>&1 || fail "in-place mkdocs failed: $(cat "$tmpdir/site.out")"
[ -f "$page" ] && grep -q "helix:publish" "$page" || fail "an in-place guide must be left alone"
grep -q "developer/index.md" "$project/docs/guide/nav.yml" || fail "the in-place nav should point at the pages: $(cat "$project/docs/guide/nav.yml")"
grep -q ": api/index.md" "$project/docs/guide/nav.yml" || fail "a delegated page's url should be docs-relative in the nav: $(cat "$project/docs/guide/nav.yml")"
cp "$tmpdir/helix-delegate.bak" "$project/.helix.yml"
rm -r "$project/mkdocs.yml" "$project/site-docs" "$project/docs/guide/nav.yml"
mkdir -p "$project/website/content"
printf 'baseURL: /\ntitle: Fixture\nmodule:\n  imports:\n    - path: github.com/imfing/hextra\n' >"$project/website/hugo.yaml"
$rg site --root "$project" --target hugo --no-build >"$tmpdir/site.out" 2>&1 || fail "hugo emit failed: $(cat "$tmpdir/site.out")"
[ -f "$project/website/content/guide/developer/_index.md" ] || fail "the page should become a section of the existing Hugo site"
grep -q "^type: docs" "$project/website/content/guide/developer/_index.md" || fail "a Hextra site's pages get type: docs"
grep -q "^sources:" "$project/website/content/guide/developer/_index.md" || fail "front matter should carry the sources"
rm -r "$project/website"

echo "OK: documentor check-pages stamps, pins staleness to sections, blocks broken links, paths and sources, applies budgets, reports unmapped files and a missing page kind, blocks handling patterns and writes outside scope; documentor site wrote a self-contained site $built, scaffolds Hextra on request, and emits into mkdocs and Hugo sites"
