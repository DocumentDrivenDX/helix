#!/usr/bin/env bash
# Assert that the `ddx.authoring` block of every artifact carrying a `ddx:`
# frontmatter block is internally consistent; see workflows/artifact-schema.md.
#
#   home: repo           -> no other authoring field is permitted except
#                           export, which lists rendered-output paths (e.g.
#                           a deliverable's pptx/pdf) rather than a checkout
#   home: external-tool  -> state, tool, and origin are present, and state is
#                           one of checked-out / checked-in
#   state: checked-in    -> export is present, the file it names exists, and
#                           the body below the frontmatter is non-empty
#   export_sha256        -> optional; 64 lowercase hex, and when the export
#                           file exists it must digest to that value
#
# The presence of `ddx.authoring.home` itself is checked by
# scripts/check-authoring-home.sh; a file missing it is skipped here so one
# defect is not reported twice.
#
# Only the leading frontmatter block is inspected, so `ddx:` appearing inside a
# fenced example in prose is not a match.
set -uo pipefail

roots=(docs/helix docs/examples docs/resources workflows)
fail=0

sha256_of() {
  if command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$1" | awk '{print $1}'
  elif command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$1" | awk '{print $1}'
  fi
}

while IFS= read -r f; do
  fm=$(awk 'NR==1 && $0 !~ /^---[[:space:]]*$/{exit} /^---[[:space:]]*$/{n++; next} n==1{print} n>=2{exit}' "$f")
  grep -q '^ddx:' <<<"$fm" || continue

  # The authoring block: every `    key: value` line under `  authoring:`.
  auth=$(awk '/^  authoring:[[:space:]]*$/{n=1; next} n && /^    [A-Za-z0-9_]+:/{print; next} n{exit}' <<<"$fm")
  home=$(sed -n 's/^    home:[[:space:]]*\([^[:space:]]*\)[[:space:]]*$/\1/p' <<<"$auth")
  [ -n "$home" ] || continue

  field() { sed -n "s/^    $1:[[:space:]]*\(.*[^[:space:]]\)[[:space:]]*$/\1/p" <<<"$auth"; }
  keys=$(sed -n 's/^    \([A-Za-z0-9_]*\):.*/\1/p' <<<"$auth")

  if [ "$home" = "repo" ]; then
    extra=$(grep -vE '^(home|export)$' <<<"$keys" | paste -sd ', ' -)
    if [ -n "$extra" ]; then
      echo "ERROR: $f declares home: repo with other authoring fields ($extra)"
      fail=1
    fi
    continue
  fi

  state=$(field state)
  export_path=$(field export)
  export_sha=$(field export_sha256)

  for required in state tool origin; do
    if [ -z "$(field "$required")" ]; then
      echo "ERROR: $f declares home: external-tool without ddx.authoring.$required"
      fail=1
    fi
  done

  case "$state" in
    checked-out | checked-in | '') ;;
    *)
      echo "ERROR: $f has ddx.authoring.state: $state (expected checked-out or checked-in)"
      fail=1
      ;;
  esac

  if [ "$state" = "checked-in" ]; then
    if [ -z "$export_path" ]; then
      echo "ERROR: $f is checked in without ddx.authoring.export"
      fail=1
    elif [ ! -f "$export_path" ]; then
      echo "ERROR: $f names a missing export file: $export_path"
      fail=1
    fi
    body=$(awk '/^---[[:space:]]*$/{n++; next} n>=2' "$f" | tr -d '[:space:]')
    if [ -z "$body" ]; then
      echo "ERROR: $f is checked in with an empty body; a check-in lands content"
      fail=1
    fi
  fi

  if [ -n "$export_sha" ]; then
    if ! grep -qE '^[0-9a-f]{64}$' <<<"$export_sha"; then
      echo "ERROR: $f has a malformed ddx.authoring.export_sha256 (expected 64 lowercase hex)"
      fail=1
    elif [ -n "$export_path" ] && [ -f "$export_path" ]; then
      actual=$(sha256_of "$export_path")
      if [ -n "$actual" ] && [ "$actual" != "$export_sha" ]; then
        echo "ERROR: $f has a stale body: $export_path digests to $actual, not $export_sha"
        fail=1
      fi
    fi
  fi
done < <(find "${roots[@]}" -name '*.md' -type f 2>/dev/null | sort)

if [ "$fail" -ne 0 ]; then
  echo
  echo "An external-tool artifact names its tool and its write surface, and a"
  echo "checked-in one carries the content it checked in:"
  echo
  echo "  ddx:"
  echo "    id: <id>"
  echo "    authoring:"
  echo "      home: external-tool"
  echo "      state: checked-in       # or checked-out"
  echo "      tool: <tool>"
  echo "      origin: <url>           # permanent write surface"
  echo "      export: <repo-relative path to the committed original>"
  echo "      export_sha256: <sha-256 of that file, optional>"
  echo
  echo "When home: repo, no other authoring field is permitted except export"
  echo "(rendered-output paths, e.g. a deliverable's pptx/pdf)."
  echo
  echo "See workflows/artifact-schema.md (External-tool fields) and"
  echo "workflows/conventions.md (Authoring Home) for the checkout cycle."
fi

exit $fail
