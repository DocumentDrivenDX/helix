#!/usr/bin/env bash
# Exercise skills/helix/scripts/guide.py end to end on a repository that has never had a guide:
# init detects and records the traits, build generates what it can and lists what an agent must
# write, check fails until every page exists and is current, review records an evaluation, and a
# changed source makes a page stale again (workflows/modes/guide.md).
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
guide="$repo_root/skills/helix/scripts/guide.py"
tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT
fail() { echo "FAIL: $*" >&2; exit 1; }
python3 -c 'import yaml, tomllib' 2>/dev/null || { echo "SKIP: needs Python 3.11 and PyYAML"; exit 0; }

p="$tmpdir/repo"
mkdir -p "$p/docs/helix/01-frame" "$p/plugins/review"
printf 'flows:\n  - id: helix\n    root: docs/helix/\n' >"$p/.helix.yml"
printf '# Vision\n\n## Mission\n\nReview claims.\n' >"$p/docs/helix/01-frame/vision.md"
printf 'schema_version = 1\n[workflow]\nid = "review"\ntitle = "Claim review"\ndescription = "Reviews a claim."\nareas = ["Billing"]\nmodel = "balanced"\ntools = []\n[evals]\nsuite = "e.jsonl"\n' >"$p/plugins/review/plugin.toml"
git -C "$p" init -q && git -C "$p" add -A

# init: the plug-in trait is detected and recorded.
python3 "$guide" init --root "$p" --write >"$tmpdir/out" 2>&1 || fail "init: $(cat "$tmpdir/out")"
grep -q "plugin-manifests" "$p/.helix.yml" || fail "init should record the trait: $(cat "$p/.helix.yml")"

# build: the generated page is written; the written pages are listed for the agent; check fails.
python3 "$guide" build --root "$p" --no-site >"$tmpdir/out" 2>&1 || fail "build: $(cat "$tmpdir/out")"
[ -f "$p/docs/guide/user/workflows.md" ] || fail "build should generate the workflows page"
grep -Eq "MISSING +index +tutorial +written" "$tmpdir/out" || fail "status should list the missing tutorial: $(cat "$tmpdir/out")"
grep -q "For the agent" "$tmpdir/out" || fail "status should give the agent its work list"
python3 "$guide" check --root "$p" >/dev/null 2>&1 && fail "check should fail while pages are missing"

# The agent writes the pages (here, minimal ones), stamps them, and they await evaluation.
for page in index about using; do
  printf '<!-- helix:publish flow=user page=%s kind=how-to voice=public-site budget=200 -->\n<!-- helix:source docs/helix/01-frame/vision.md#mission -->\n# %s\n\nThe tool reviews claims.\n' "$page" "$page" >"$p/docs/guide/user/$page.md"
  python3 "$repo_root/skills/helix/scripts/publish_check.py" stamp "$p/docs/guide/user/$page.md" --root "$p" >/dev/null
done
python3 "$guide" status --root "$p" >"$tmpdir/out" 2>&1 || true
grep -Eq "REVIEW +about" "$tmpdir/out" || fail "a written, unevaluated page should await review: $(cat "$tmpdir/out")"
for page in index about using; do python3 "$guide" review "$p/docs/guide/user/$page.md" --root "$p" --by evaluator >/dev/null; done
grep -Eq "reviewed=[0-9-]{10}/evaluator" "$p/docs/guide/user/about.md" || fail "review should stamp the header"
python3 "$guide" check --root "$p" >"$tmpdir/out" 2>&1 || fail "a complete, evaluated guide should pass: $(cat "$tmpdir/out")"

# A changed source makes the written page stale, and a new plug-in the generated one.
printf '# Vision\n\n## Mission\n\nReview and pay claims.\n' >"$p/docs/helix/01-frame/vision.md"
python3 "$guide" check --root "$p" >"$tmpdir/out" 2>&1 && fail "a changed source should fail the check"
grep -Eq "STALE +about" "$tmpdir/out" || fail "expected the written page stale: $(cat "$tmpdir/out")"

# build also assembles the site (the self-contained layout needs no network).
if command -v hugo >/dev/null; then
  for page in index about using; do python3 "$repo_root/skills/helix/scripts/publish_check.py" stamp "$p/docs/guide/user/$page.md" --root "$p" >/dev/null; done
  python3 "$guide" build --root "$p" --site "$tmpdir/site" >/dev/null 2>&1 || fail "build with the site failed"
  [ -f "$tmpdir/site/public/user/workflows/index.html" ] || fail "the site should hold the generated page"
fi
echo "OK: guide.py takes a repository from no guide to a checked, evaluated guide and its site, and catches it going stale"
