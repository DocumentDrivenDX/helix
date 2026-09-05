#!/usr/bin/env bash
# Assert that every artifact carrying a `ddx:` frontmatter block declares
# `ddx.authoring.home`. Required field; see workflows/artifact-schema.md.
#
# Only the leading frontmatter block is inspected, so `ddx:` appearing inside a
# fenced example in prose is not a match.
set -uo pipefail

roots=(docs/helix docs/examples docs/resources workflows)
fail=0

while IFS= read -r f; do
  fm=$(awk 'NR==1 && $0 !~ /^---[[:space:]]*$/{exit} /^---[[:space:]]*$/{n++; next} n==1{print} n>=2{exit}' "$f")
  grep -q '^ddx:' <<<"$fm" || continue
  if ! grep -q '^  authoring:' <<<"$fm" || ! grep -q '^    home:[[:space:]]*\(repo\|external-tool\)[[:space:]]*$' <<<"$fm"; then
    echo "ERROR: $f carries a ddx: block without a valid ddx.authoring.home"
    fail=1
  fi
done < <(find "${roots[@]}" -name '*.md' -type f 2>/dev/null | sort)

if [ "$fail" -ne 0 ]; then
  echo
  echo "Every graph-addressable artifact declares where it is authored:"
  echo
  echo "  ddx:"
  echo "    id: <id>"
  echo "    authoring:"
  echo "      home: repo            # or external-tool"
  echo
  echo "See workflows/artifact-schema.md (Authoring home) and"
  echo "workflows/conventions.md (Authoring Home) for the classification test."
fi

exit $fail
