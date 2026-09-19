#!/usr/bin/env bash
# Gate: every microsite page carries a verifiable Innsigle seal, signed by the
# right key (Innsigle ADR-004), and the built site renders it.
#
# Source side — `innsigle verify --all` (pinned via scripts/innsigle-cli.sh)
# maps every claim under .innsigle/public/claims/ back to its source under
# docs/website/content, checks the sha256 digest against the current bytes and
# the signature against .innsigle/public/keys.json, and lists unsealed sources.
# On top of that this gate enforces the key policy:
#   curated page (no `generated: true`)  -> claim signed by the HUMAN key
#   generated page (`generated: true`)   -> claim signed by the BUILD key
# and, once a build key is configured, that the human key has endorsed it.
#
# Build side — the site is built here with hugo stderr captured; a warning
# starting with "innsigle:" that says a page's seal is stale (edited since
# sealing) is reported but does not fail — that is just unsigned content,
# not a broken one. Other "innsigle:" warnings (unreadable source, unsupported
# digest) do fail. Then website/public must serve /.well-known/innsigle/keys.json
# and every sealed page's HTML must carry the colophon quoting its attestation.
#
# Unsigned content is not a build blocker: a curated page that was never sealed
# or was edited since its last seal (STALE) only warns, everywhere, including
# CI — sealing requires the human key (1Password, never in CI), so a
# contributor without desktop access to it cannot be blocked from merging.
# What still fails the build is evidence of a broken or wrong signature: a
# claim signed by the wrong key, an orphaned/ambiguous claim, or a claim the
# CLI cannot parse.
#
# Strictness. Build-key claims are minted by CI, not committed, so:
#   INNSIGLE_REQUIRED=1 (CI)  generated pages must be sealed and rendered, and
#                             the build key must exist and be endorsed
#   otherwise (a laptop)      generated pages may be unsealed unless
#                             INNSIGLE_BUILD_KEY is set; a missing endorsement
#                             is a warning
# Fix curated pages with `just innsigle-seal`; see `just innsigle-build-key`
# and `just innsigle-endorse` for the build key.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

content_root="docs/website/content"
claims_dir=".innsigle/public/claims"
keys_json=".innsigle/public/keys.json"
config=".innsigle/config.json"
site_dir="website/public"
base_url="https://documentdrivendx.github.io/helix/"
strict="${INNSIGLE_REQUIRED:-0}"

# Locally the gate skips (exit 0, with a message) when a tool is not available, so `just test` stays
# runnable on a host without them; CI sets INNSIGLE_REQUIRED=1 and a skip becomes a failure there.
skip() { if [ "$strict" = 1 ]; then echo "FAIL: $*" >&2; exit 1; fi; echo "SKIP: innsigle gate: $*"; exit 0; }
command -v hugo >/dev/null || skip "hugo not installed"
command -v jq >/dev/null || skip "jq not installed"
# the CLI prints its usage and exits 1 on --help, so test the output, not the status; capture it first
# (piping straight into grep -q would close the pipe early and, under pipefail, read a working CLI as missing)
probe="$(bash scripts/innsigle-cli.sh --help 2>&1 || true)"
grep -q 'seal --all' <<<"$probe" || { echo "$probe" | tail -5 >&2; skip "innsigle CLI (v0.5.0+) not resolvable (npx needs network; see scripts/innsigle-cli.sh)"; }

[ -f "$config" ] || { echo "FAIL: $config missing (it is committed)" >&2; exit 1; }
[ -f "$keys_json" ] || { echo "FAIL: $keys_json missing" >&2; exit 1; }

fail=0
human_id="$(jq -r '.issuer.key_id' "$config")"
build_id="$(jq -r '.keys.build.key_id // empty' "$config")"
require_all=0; [ "$strict" = 1 ] && require_all=1
have_build=0; [ -n "${INNSIGLE_BUILD_KEY:-}" ] && have_build=1
[ "$require_all" = 1 ] && have_build=1

# --- issuer document: roles and the human -> build endorsement -------------------------------------
jq -e --arg id "$human_id" '.keys[] | select(.key_id == $id and .role == "human" and .revoked_at == null)' "$keys_json" >/dev/null \
  || { echo "FAIL: $keys_json lacks an unrevoked key $human_id with role human" >&2; fail=1; }
endorsement_file=""
if [ -n "$build_id" ]; then
  jq -e --arg id "$build_id" '.keys[] | select(.key_id == $id and .role == "build" and .revoked_at == null)' "$keys_json" >/dev/null \
    || { echo "FAIL: $keys_json lacks an unrevoked key $build_id with role build (keys.build in $config)" >&2; fail=1; }
  url="$(jq -r --arg id "$build_id" '.endorsements[]? | select(.subject_key_id == $id) | .attestation_url' "$keys_json" | head -1)"
  endorsement_file=".innsigle/public/endorsements/${url##*/}"
  if [ -z "$url" ] || [ ! -f "$endorsement_file" ]; then
    endorsement_file=""
    if [ "$strict" = 1 ]; then echo "FAIL: build key $build_id is not endorsed by the human key (just innsigle-endorse)" >&2; fail=1
    else echo "WARN: build key $build_id is not endorsed yet (just innsigle-endorse)" >&2; fi
  elif ! jq -e --arg h "$human_id" --arg b "$build_id" \
      '(.payload.type | endswith("/key-endorsement/v1")) and .payload.endorsement.subject_key_id == $b and .signatures[0].key_id == $h' \
      "$endorsement_file" >/dev/null; then
    echo "FAIL: $endorsement_file is not a key-endorsement of $build_id signed by $human_id" >&2; fail=1
  fi
elif [ "$strict" = 1 ]; then
  echo "FAIL: $config has no keys.build; generated pages need the build key (just innsigle-build-key)" >&2; fail=1
fi

# --- source side: crypto from the CLI, key policy here ---------------------------------------------
is_generated() { awk 'NR==1&&$0!="---"{exit 1} NR>1&&$0=="---"{exit 1} NR>1&&/^generated: true$/{found=1} END{exit !found}' "$1"; }
report="$(mktemp)"; cli_err="$(mktemp)"
trap 'rm -f "$report" "$cli_err"' EXIT
bash scripts/innsigle-cli.sh verify --all >"$report" 2>"$cli_err" || true
grep -q '^INVALID: no \|^INVALID: cannot' "$cli_err" && { echo "FAIL: innsigle verify --all could not run:" >&2; cat "$cli_err" >&2; exit 1; }

valid=0 broken=0 stale=0 unsealed_curated=0 unsealed_generated=0 policy=0
stale_srcs="$(mktemp)"
while IFS= read -r line; do
  case "$line" in
    "VALID all "*) ;;
    "VALID "*)
      src="${line#VALID }"; src="${src% (*}"
      fname="${line##*(}"; fname="${fname%)}"
      signer="$(jq -r '.signatures[0].key_id' "$claims_dir/$fname")"
      if is_generated "$src"; then
        if [ -n "$build_id" ] && [ "$signer" != "$build_id" ]; then
          echo "WRONG KEY: $src is generated but sealed by $signer, not the build key (CI reseals it)" >&2; policy=$((policy+1)); continue
        fi
      elif [ "$signer" != "$human_id" ]; then
        echo "WRONG KEY: $src is curated but sealed by $signer, not the human key" >&2; policy=$((policy+1)); continue
      fi
      valid=$((valid+1)) ;;
    "UNSEALED "*)
      src="${line#UNSEALED }"
      if is_generated "$src"; then
        unsealed_generated=$((unsealed_generated+1))
        [ "$have_build" = 1 ] && [ "$unsealed_generated" -le 20 ] && echo "UNSEALED: $src (generated; the build key should have sealed it)" >&2
      else
        unsealed_curated=$((unsealed_curated+1)); [ "$unsealed_curated" -le 20 ] && echo "WARN: $src is curated and unsealed (run just innsigle-seal when you can)" >&2
      fi ;;
    "STALE "*)
      src="${line#STALE }"; src="${src% (*}"
      stale=$((stale+1)); echo "$src" >> "$stale_srcs"
      [ "$stale" -le 20 ] && echo "WARN: $src claim is stale (edited since sealing?) — run just innsigle-seal when you can" >&2 ;;
    *) echo "$line" >&2; broken=$((broken+1)) ;;  # ORPHAN, AMBIGUOUS, INVALID(reason)
  esac
done < "$report"
[ "$unsealed_curated" -gt 20 ] && echo "... and $((unsealed_curated-20)) more unsealed curated pages" >&2
[ "$stale" -gt 20 ] && echo "... and $((stale-20)) more stale claims" >&2
echo "claims: $valid valid, $stale stale (warn), $broken orphan/ambiguous/invalid, $policy wrong key, $unsealed_curated curated unsealed (warn), $unsealed_generated generated unsealed"
[ $((broken+policy)) -eq 0 ] || fail=1
if [ "$unsealed_generated" -gt 0 ]; then
  if [ "$have_build" = 1 ]; then fail=1
  else echo "note: generated pages are sealed by the build key in CI; set INNSIGLE_BUILD_KEY to seal them here" >&2; fi
fi

# --- build side -------------------------------------------------------------------------------------
echo "Building site..."
hugo_err="$(mktemp)"
trap 'rm -f "$report" "$cli_err" "$stale_srcs" "$hugo_err"' EXIT
(cd website && hugo --gc --minify --baseURL "$base_url" >/dev/null 2>"$hugo_err") || {
  echo "FAIL: hugo build failed" >&2; cat "$hugo_err" >&2; exit 1; }
stale_warn="$(grep 'innsigle:' "$hugo_err" | grep 'no longer matches its seal' || true)"
other_warn="$(grep 'innsigle:' "$hugo_err" | grep -v 'no longer matches its seal' || true)"
if [ -n "$stale_warn" ]; then
  echo "WARN: hugo skipped rendering stale seals (run just innsigle-seal when you can):" >&2
  echo "$stale_warn" >&2
fi
if [ -n "$other_warn" ]; then
  echo "FAIL: hugo reported innsigle warnings:" >&2
  echo "$other_warn" >&2
  fail=1
fi

[ -f "$site_dir/.well-known/innsigle/keys.json" ] || {
  echo "FAIL: $site_dir/.well-known/innsigle/keys.json missing" >&2; fail=1; }
if [ -n "$endorsement_file" ] && [ ! -f "$site_dir/.well-known/innsigle/endorsements/$(basename "$endorsement_file")" ]; then
  echo "FAIL: endorsement not published under $site_dir/.well-known/innsigle/endorsements/" >&2; fail=1
fi

# Hugo lowercases every URL path, so ADR-002.md publishes at adr-002/. The published paths are matched
# against an exact listing rather than [ -f ], because a case-insensitive filesystem would hide a case mismatch.
published="$(mktemp)"
(cd "$site_dir" && find . -name 'index.html' -type f | sed 's#^\./##' | sort) > "$published"
rendered=0 unrendered=0 unsealed_pages=0
while IFS= read -r -d '' f; do
  rel="${f#"$content_root"/}"
  slug="$(printf '%s' "$rel" | sed -E 's/[^a-zA-Z0-9]+/-/g; s/^-+//; s/-+$//')"
  if [ ! -f "$claims_dir/$slug.attestation.json" ]; then
    unsealed_pages=$((unsealed_pages+1)); continue  # already accounted for on the source side
  fi
  if grep -Fxq "$f" "$stale_srcs"; then
    unsealed_pages=$((unsealed_pages+1)); continue  # stale claim, already warned on the source side
  fi
  case "$rel" in
    _index.md) page="index.html" ;;
    */_index.md) page="${rel%/_index.md}/index.html" ;;
    *) page="${rel%.md}/index.html" ;;
  esac
  page="$(printf '%s' "$page" | tr 'A-Z' 'a-z')"
  html="$site_dir/$page"
  if grep -Fxq "$page" "$published" && grep -q 'innsigle-colophon' "$html" && grep -q 'application/innsigle+json' "$html"; then
    rendered=$((rendered+1))
  else
    unrendered=$((unrendered+1)); [ "$unrendered" -le 20 ] && echo "NO SEAL RENDERED: $rel -> $html" >&2
  fi
done < <(find "$content_root" -name '*.md' -type f -print0 | sort -z)
rm -f "$published"
echo "rendered: $rendered pages quoting their seal, $unrendered sealed pages without one, $unsealed_pages pages with no claim"
[ "$unrendered" -eq 0 ] || fail=1

if [ "$fail" -ne 0 ]; then
  echo "FAIL: Innsigle seal gate found a broken or wrong-key signature (see WRONG KEY / ORPHAN / AMBIGUOUS / INVALID lines above), not just unsigned content." >&2
  exit 1
fi
echo "OK: every sealed page verifies and renders its seal"
