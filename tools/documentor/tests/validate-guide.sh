#!/usr/bin/env bash
# Exercise the documentor CLI end to end on a repository that has never had a guide:
# init detects and records the traits, build generates what it can and lists what an agent must
# write, check fails until every page exists and is current, review records an evaluation, and a
# changed source makes a page stale again (workflows/modes/guide.md).
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
rg="${DOCUMENTOR:-documentor}"
command -v "$rg" >/dev/null 2>&1 || { echo "FAIL: documentor is not on PATH; run the tests with uv (just test)"; exit 1; }
tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT
fail() { echo "FAIL: $*" >&2; exit 1; }

p="$tmpdir/repo"
mkdir -p "$p/docs/helix/01-frame" "$p/plugins/review"
printf 'flows:\n  - id: helix\n    root: docs/helix/\n' >"$p/.helix.yml"
printf '# Vision\n\n## Mission\n\nReview claims.\n' >"$p/docs/helix/01-frame/vision.md"
printf 'schema_version = 1\n[workflow]\nid = "review"\ntitle = "Claim review"\ndescription = "Reviews a claim."\nareas = ["Billing"]\nmodel = "balanced"\ntools = []\n[evals]\nsuite = "e.jsonl"\n' >"$p/plugins/review/plugin.toml"
git -C "$p" init -q && git -C "$p" add -A

# init: the plug-in trait is detected and recorded.
$rg init --root "$p" --write >"$tmpdir/out" 2>&1 || fail "init: $(cat "$tmpdir/out")"
grep -q "plugin-manifests" "$p/.helix.yml" || fail "init should record the trait: $(cat "$p/.helix.yml")"

# build: the generated page is written; the written pages are listed for the agent; check fails.
$rg build --root "$p" --no-site >"$tmpdir/out" 2>&1 || fail "build: $(cat "$tmpdir/out")"
[ -f "$p/docs/guide/user/workflows.md" ] || fail "build should generate the workflows page"
grep -Eq "MISSING +index +tutorial +written" "$tmpdir/out" || fail "status should list the missing tutorial: $(cat "$tmpdir/out")"
grep -q "For the agent" "$tmpdir/out" || fail "status should give the agent its work list"
$rg check --root "$p" >/dev/null 2>&1 && fail "check should fail while pages are missing"

# The agent writes the pages (here, minimal ones), stamps them, and they await evaluation.
for page in index about using; do
  printf '<!-- helix:publish flow=user page=%s kind=how-to voice=public-site budget=200 -->\n<!-- helix:source docs/helix/01-frame/vision.md#mission -->\n# %s\n\nThe tool reviews claims.\n' "$page" "$page" >"$p/docs/guide/user/$page.md"
  $rg stamp "$p/docs/guide/user/$page.md" --root "$p" >/dev/null
done
$rg status --root "$p" >"$tmpdir/out" 2>&1 || true
grep -Eq "REVIEW +about" "$tmpdir/out" || fail "a written, unevaluated page should await review: $(cat "$tmpdir/out")"
for page in index about using; do $rg review "$p/docs/guide/user/$page.md" --root "$p" --by evaluator >/dev/null; done
grep -Eq "reviewed=[0-9-]{10}/evaluator" "$p/docs/guide/user/about.md" || fail "review should stamp the header"
$rg check --root "$p" >"$tmpdir/out" 2>&1 || fail "a complete, evaluated guide should pass: $(cat "$tmpdir/out")"

# A changed source makes the written page stale, and a new plug-in the generated one.
printf '# Vision\n\n## Mission\n\nReview and pay claims.\n' >"$p/docs/helix/01-frame/vision.md"
$rg check --root "$p" >"$tmpdir/out" 2>&1 && fail "a changed source should fail the check"
grep -Eq "STALE +about" "$tmpdir/out" || fail "expected the written page stale: $(cat "$tmpdir/out")"

# A project adopts a page it already had: a glob adds it, a mapping stands it in for an audience page,
# and `skip` drops an audience page. Adopted pages keep their text and are not held to the writing pass.
mkdir -p "$p/docs/howto"
printf '# Using the review tool\n\nThis is a very long hand-written sentence that goes on and on well past the limit the writing pass sets for a sentence in the onboarding voice, and nobody rewrites it.\n' >"$p/docs/howto/review-tool.md"
printf '# Start here\n\nOpen the tool.\n' >"$p/docs/start.md"
git -C "$p" add -A   # existing pages are found among the files git tracks
printf '  existing:\n    user:\n      - "docs/howto/*.md"\n  skip: [user/about]\n' >>"$p/.helix.yml"
python3 - "$p/.helix.yml" <<'PY'
import sys, yaml
path = sys.argv[1]; data = yaml.safe_load(open(path))
data["publish"]["existing"] = {"user": ["docs/howto/*.md"]}
data["publish"]["pages"] = {"user": [{"id": "index", "title": "Start here", "kind": "tutorial", "task": "Start.", "sources": []}]}
open(path, "w").write(yaml.safe_dump(data, sort_keys=False))
PY
$rg status --root "$p" >"$tmpdir/out" 2>&1 || true
grep -Eq "ADOPT +review-tool" "$tmpdir/out" || fail "an adopted page without a header awaits adoption: $(cat "$tmpdir/out")"
grep -q " about " "$tmpdir/out" && fail "a skipped audience page should not be planned: $(cat "$tmpdir/out")"
$rg adopt "$p/docs/howto/review-tool.md" --audience user --kind how-to --root "$p" >/dev/null || fail "adopt failed"
grep -q "existing=yes" "$p/docs/howto/review-tool.md" || fail "adopt should add the header"
$rg review "$p/docs/howto/review-tool.md" --root "$p" --by adopter >/dev/null || fail "an adopted page is reviewable despite its prose: $($rg review "$p/docs/howto/review-tool.md" --root "$p" --by adopter 2>&1)"

# build also assembles the site (the self-contained layout needs no network).
if command -v hugo >/dev/null; then
  for page in index about using; do $rg stamp "$p/docs/guide/user/$page.md" --root "$p" >/dev/null; done
  $rg build --root "$p" --site "$tmpdir/site" >/dev/null 2>&1 || fail "build with the site failed"
  [ -f "$tmpdir/site/public/user/workflows/index.html" ] || fail "the site should hold the generated page"
fi
echo "OK: documentor takes a repository from no guide to a checked, evaluated guide and its site, and catches it going stale"
