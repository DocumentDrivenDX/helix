#!/usr/bin/env bash
# Validate that the generated/published site content is current and complete.
#
# The site's reference content is a projection of upstream sources:
#   generate-reference.py : workflows/                 -> content/{artifact-types,concerns}
#   publish-artifacts.py  : docs/helix/                -> content/artifacts
#   publish-resources.py  : docs/resources/            -> content/research
#
# This gate re-runs the generators and fails if the committed output drifts
# from what the sources currently produce (stale output, hand-edits to
# generated pages, or a source added without regenerating). Because the
# generators wipe-and-rebuild, the drift check also proves coverage: a source
# with no rendered page would appear as an addition in the diff.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

content="docs/website/content"
generated_dirs=("$content/artifact-types" "$content/concerns" "$content/artifacts" "$content/research")

echo "Regenerating site reference content from upstream sources..."
uv run scripts/generate-reference.py >/dev/null
uv run scripts/publish-artifacts.py >/dev/null
uv run scripts/publish-resources.py >/dev/null

echo "Checking for drift in generated content..."
if ! git diff --quiet -- "${generated_dirs[@]}"; then
  echo "FAIL: generated site content is out of date with its sources." >&2
  echo "Run the generators and commit the result:" >&2
  echo "  uv run scripts/generate-reference.py" >&2
  echo "  uv run scripts/publish-artifacts.py" >&2
  echo "  uv run scripts/publish-resources.py" >&2
  echo "Drifted files:" >&2
  git --no-pager diff --stat -- "${generated_dirs[@]}" >&2
  exit 1
fi

# Coverage signal: every upstream concern and artifact-type has a rendered page.
src_concerns=$(find workflows/concerns -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')
# Family READMEs (e.g. README-auth-family.md) are published alongside concerns
# but are not concerns themselves; exclude them from the coverage count.
out_concerns=$(find "$content/concerns" -name '*.md' ! -name '_index.md' ! -name 'README-*.md' | wc -l | tr -d ' ')
src_arttypes=$(find workflows/activities/*/artifacts -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')
out_arttypes=$(find "$content/artifact-types" -name '*.md' ! -name '_index.md' | wc -l | tr -d ' ')

[[ "$src_concerns" == "$out_concerns" ]] || {
  echo "FAIL: $src_concerns concern sources but $out_concerns rendered concern pages" >&2; exit 1; }
[[ "$src_arttypes" == "$out_arttypes" ]] || {
  echo "FAIL: $src_arttypes artifact-type sources but $out_arttypes rendered pages" >&2; exit 1; }

echo "OK: generated content current and complete ($out_concerns concerns, $out_arttypes artifact types)"
