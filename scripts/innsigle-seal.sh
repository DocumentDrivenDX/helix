#!/usr/bin/env bash
# Seal microsite content sources with Innsigle colophon attestations.
#
# For every markdown source under docs/website/content/, produce a signed
# claim at .innsigle/public/claims/<slug>.attestation.json, where <slug> is
# the source path with every non-alphanumeric run replaced by "-" (the badge
# partial, website/layouts/_partials/components/comments.html, derives the
# same slug at build time). Files whose existing claim digest still matches
# are skipped, so re-runs seal only what changed.
#
# Composition mapping (ratified 2026-08-26):
#   pages the generators stamp with `generated: true` frontmatter
#   (scripts/generate-reference.py, publish-artifacts.py, publish-resources.py)
#                               -> model-primary
#   everything else (curated)   -> mixed
# Frontmatter, not path, decides: research/_index.md is hand-authored even
# though it lives in a generated tree.
#
# Requires: .innsigle/config.json (from `innsigle init --onepassword`), the
# 1Password CLI (`op`) signed in, jq, and the innsigle CLI (global install
# or npx fallback). The private key is read from 1Password into a mode-600
# temp file for the duration of the run and shredded on exit.
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$repo_root"

config=".innsigle/config.json"
content_root="docs/website/content"
claims_dir=".innsigle/public/claims"
site_url="https://documentdrivendx.github.io/helix"

[ -f "$config" ] || {
  echo "ERROR: $config not found. Run the one-time key ceremony first:" >&2
  echo "  npx --package=github:DocumentDrivenDX/innsigle innsigle init --onepassword --site-url $site_url/" >&2
  exit 1
}
command -v jq >/dev/null || { echo "ERROR: jq required" >&2; exit 1; }
command -v op >/dev/null || { echo "ERROR: 1Password CLI (op) required" >&2; exit 1; }

if command -v innsigle >/dev/null; then
  INNSIGLE=(innsigle)
else
  INNSIGLE=(npx --yes --package=github:DocumentDrivenDX/innsigle innsigle)
fi

issuer_id="$(jq -r '.issuer.id' "$config")"
issuer_name="$(jq -r '.issuer.name' "$config")"
key_id="$(jq -r '.issuer.key_id' "$config")"
key_url="$(jq -r '.issuer.key_url' "$config")"
key_ref="$(jq -r '.onepassword.private_key_ref' "$config")"
keys_json="$(jq -r '.paths.keys' "$config")"

workdir="$(mktemp -d)"
trap 'rm -rf "$workdir"' EXIT
key_pem="$workdir/key.pem"
umask 077
op read "$key_ref" > "$key_pem"

mkdir -p "$claims_dir"

sealed=0 skipped=0 failed=0
while IFS= read -r -d '' f; do
  rel="${f#"$content_root"/}"
  slug="$(printf '%s' "$rel" | sed -E 's/[^a-zA-Z0-9]+/-/g; s/^-+//; s/-+$//')"
  att="$claims_dir/$slug.attestation.json"
  digest="$(openssl dgst -sha256 -r "$f" | cut -d' ' -f1)"

  if [ -f "$att" ] && [ "$(jq -r '.payload.subjects[0].digest.value' "$att")" = "$digest" ]; then
    skipped=$((skipped+1)); continue
  fi

  if awk 'NR==1&&$0!="---"{exit 1} NR>1&&$0=="---"{exit 1} NR>1&&/^generated: true$/{found=1} END{exit !found}' "$f"; then
    kind="model-primary"
  else
    kind="mixed"
  fi

  colo="$workdir/colo.json"; claim="$workdir/claim.json"
  "${INNSIGLE[@]}" colo example --kind "$kind" > "$colo"
  "${INNSIGLE[@]}" claim build \
    --content "$f" \
    --uri "$site_url/$rel" \
    --colo "$colo" \
    --issuer-id "$issuer_id" --issuer-name "$issuer_name" \
    --key-id "$key_id" --key-url "$key_url" \
    --out "$claim" >/dev/null
  "${INNSIGLE[@]}" sign --claim "$claim" --key "$key_pem" --out "$att" >/dev/null
  if "${INNSIGLE[@]}" verify --attestation "$att" --content "$f" --keys "$keys_json" >/dev/null; then
    echo "sealed ($kind): $rel"
    sealed=$((sealed+1))
  else
    echo "VERIFY FAILED: $rel" >&2
    rm -f "$att"
    failed=$((failed+1))
  fi
done < <(find "$content_root" -name '*.md' -type f -print0 | sort -z)

# Remove claims whose page no longer exists (deleted or renamed), so /.well-known never publishes an orphan.
removed=0
expected="$workdir/expected-slugs"
find "$content_root" -name '*.md' -type f | sed -e "s#^$content_root/##" -E -e 's/[^a-zA-Z0-9]+/-/g; s/^-+//; s/-+$//' | sort -u > "$expected"
for att in "$claims_dir"/*.attestation.json; do
  [ -f "$att" ] || continue
  slug="$(basename "$att" .attestation.json)"
  if ! grep -Fxq "$slug" "$expected"; then
    echo "removed orphan claim: $(basename "$att")"; rm -f "$att"; removed=$((removed+1))
  fi
done

echo "innsigle-seal: $sealed sealed, $skipped up to date, $failed failed, $removed orphan claims removed"
[ "$failed" -eq 0 ]
