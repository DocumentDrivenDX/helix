#!/usr/bin/env bash
# Gate: every microsite page carries a verifiable Innsigle seal.
#
# Source side — for every *.md under docs/website/content there must be a
# claim at .innsigle/public/claims/<slug>.attestation.json (slug = path
# relative to the content root, non-alphanumeric runs -> "-", trimmed; the
# same rule scripts/innsigle-seal.sh and the badge partial use) whose sha256
# digest matches the current source bytes and whose signature verifies
# against .innsigle/public/keys.json (checked with the innsigle CLI).
#
# Build side — the site is built here with hugo stderr captured; any warning
# starting with "innsigle:" (the partial refusing to render a stale seal)
# fails. Then website/public must carry /.well-known/innsigle/keys.json and
# every page's HTML must contain the innsigle-colophon element.
#
# Fix unsealed or stale pages with `just innsigle-seal`.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

content_root="docs/website/content"
claims_dir=".innsigle/public/claims"
keys_json=".innsigle/public/keys.json"
site_dir="website/public"
base_url="https://documentdrivendx.github.io/helix/"

# Locally the gate skips (exit 0, with a message) when Hugo or the innsigle CLI is not available, so `just test`
# stays runnable on a host without them; CI sets INNSIGLE_REQUIRED=1 and a skip becomes a failure there.
skip() { if [ "${INNSIGLE_REQUIRED:-0}" = 1 ]; then echo "FAIL: $*" >&2; exit 1; fi; echo "SKIP: innsigle gate: $*"; exit 0; }
command -v hugo >/dev/null || skip "hugo not installed"
if command -v innsigle >/dev/null; then
  INNSIGLE=(innsigle)
else
  INNSIGLE=(npx --yes --package=github:DocumentDrivenDX/innsigle innsigle)
  # the CLI prints its usage and exits 1 on --help, so test the output, not the status; capture it first
  # (piping straight into grep -q would close the pipe early and, under pipefail, read a working CLI as missing)
  probe="$("${INNSIGLE[@]}" --help 2>&1 || true)"
  grep -q 'innsigle' <<<"$probe" || { echo "$probe" | tail -5 >&2; skip "innsigle CLI not resolvable (npx needs network, or install it globally)"; }
fi

[ -f "$keys_json" ] || { echo "FAIL: $keys_json missing" >&2; exit 1; }

# No claims at all means the one-time key ceremony has not run; say that in three lines instead of one per page.
if [ -z "$(find "$claims_dir" -name '*.attestation.json' -print -quit 2>/dev/null)" ]; then
  echo "FAIL: no claims under $claims_dir; the site has never been sealed." >&2
  echo "  1. npx --package=github:DocumentDrivenDX/innsigle innsigle init --onepassword --site-url $base_url" >&2
  echo "  2. just innsigle-seal   3. git add .innsigle/public && git commit" >&2
  exit 1
fi

fail=0
pages=0 valid=0 missing=0 stale=0 badsig=0
while IFS= read -r -d '' f; do
  pages=$((pages+1))
  rel="${f#"$content_root"/}"
  slug="$(printf '%s' "$rel" | sed -E 's/[^a-zA-Z0-9]+/-/g; s/^-+//; s/-+$//')"
  att="$claims_dir/$slug.attestation.json"
  if [ ! -f "$att" ]; then
    missing=$((missing+1)); [ "$missing" -le 20 ] && echo "UNSEALED: $rel" >&2; continue
  fi
  digest="$(openssl dgst -sha256 -r "$f" | cut -d' ' -f1)"
  if [ "$(jq -r '.payload.subjects[0].digest.value' "$att")" != "$digest" ]; then
    echo "STALE: $rel (edited since sealing)" >&2; stale=$((stale+1)); continue
  fi
  if ! "${INNSIGLE[@]}" verify --attestation "$att" --content "$f" --keys "$keys_json" >/dev/null 2>&1; then
    echo "BAD SIGNATURE: $rel ($att)" >&2; badsig=$((badsig+1)); continue
  fi
  valid=$((valid+1))
done < <(find "$content_root" -name '*.md' -type f -print0 | sort -z)

[ "$missing" -gt 20 ] && echo "... and $((missing-20)) more unsealed pages" >&2
# Orphans: a claim whose page no longer exists would still be published under /.well-known; the seal script removes them.
orphans=0
expected="$(mktemp)"
find "$content_root" -name '*.md' -type f | sed -e "s#^$content_root/##" -E -e 's/[^a-zA-Z0-9]+/-/g; s/^-+//; s/-+$//' | sort -u > "$expected"
for att in "$claims_dir"/*.attestation.json; do
  [ -f "$att" ] || continue
  slug="$(basename "$att" .attestation.json)"
  if ! grep -Fxq "$slug" "$expected"; then
    echo "ORPHAN: $att names no current page (run just innsigle-seal to remove it)" >&2; orphans=$((orphans+1))
  fi
done
rm -f "$expected"
echo "claims: $pages pages, $valid valid, $missing unsealed, $stale stale, $badsig bad signature, $orphans orphan claims"
[ $((missing+stale+badsig+orphans)) -eq 0 ] || fail=1

echo "Building site..."
hugo_err="$(mktemp)"
trap 'rm -f "$hugo_err"' EXIT
(cd website && hugo --gc --minify --baseURL "$base_url" >/dev/null 2>"$hugo_err") || {
  echo "FAIL: hugo build failed" >&2; cat "$hugo_err" >&2; exit 1; }
if grep -q 'innsigle:' "$hugo_err"; then
  echo "FAIL: hugo reported innsigle warnings:" >&2
  grep 'innsigle:' "$hugo_err" >&2
  fail=1
fi

[ -f "$site_dir/.well-known/innsigle/keys.json" ] || {
  echo "FAIL: $site_dir/.well-known/innsigle/keys.json missing" >&2; fail=1; }

rendered=0 unrendered=0
while IFS= read -r -d '' f; do
  rel="${f#"$content_root"/}"
  case "$rel" in
    _index.md) html="$site_dir/index.html" ;;
    */_index.md) html="$site_dir/${rel%/_index.md}/index.html" ;;
    *) html="$site_dir/${rel%.md}/index.html" ;;
  esac
  if [ -f "$html" ] && grep -q 'innsigle-colophon' "$html"; then
    rendered=$((rendered+1))
  else
    unrendered=$((unrendered+1)); [ "$unrendered" -le 20 ] && echo "NO SEAL RENDERED: $rel -> $html" >&2
  fi
done < <(find "$content_root" -name '*.md' -type f -print0 | sort -z)
echo "rendered: $rendered pages with a seal, $unrendered without"
[ "$unrendered" -eq 0 ] || fail=1

if [ "$fail" -ne 0 ]; then
  echo "FAIL: Innsigle seal gate. Run \`just innsigle-seal\` and commit .innsigle/public/claims/." >&2
  exit 1
fi
echo "OK: every page sealed and rendering a verified Innsigle seal"
