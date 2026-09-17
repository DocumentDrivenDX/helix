#!/usr/bin/env bash
# One-time ceremony: create the BUILD signing key (Innsigle ADR-004).
#
# The build key seals generated pages (`generated: true`) in CI so the human
# key never leaves 1Password. This script:
#   1. generates an ed25519 keypair under .innsigle/keys/build/ (gitignored)
#   2. adds its public half to .innsigle/public/keys.json with role "build"
#      (and marks the existing house key role "human")
#   3. records the key id under keys.build in .innsigle/config.json
# and then prints the two steps only the operator can do: store the private
# key as the INNSIGLE_BUILD_KEY GitHub secret and endorse it with the human
# key (`just innsigle-endorse`).
#
# Run it once, from the repo root. It refuses to run twice unless --rotate is
# given: rotation marks the current build key revoked_at in keys.json (never
# deleted; published claims may name it), drops its endorsement, moves the
# local PEMs aside, and mints a replacement. After a rotation the secret must
# be replaced and the new key endorsed again.
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$repo_root"

config=".innsigle/config.json"
keys_json=".innsigle/public/keys.json"
key_dir=".innsigle/keys/build"
repo_slug="DocumentDrivenDX/helix"

command -v jq >/dev/null || { echo "ERROR: jq required" >&2; exit 1; }
[ -f "$config" ] || { echo "ERROR: $config not found" >&2; exit 1; }
[ -f "$keys_json" ] || { echo "ERROR: $keys_json not found" >&2; exit 1; }
rotate=0; [ "${1:-}" = "--rotate" ] && rotate=1
old_id="$(jq -r '.keys.build.key_id // empty' "$config")"
if [ -n "$old_id" ] && [ "$rotate" = 0 ]; then
  echo "ERROR: $config already has keys.build ($old_id); pass --rotate to revoke it and mint a replacement" >&2
  exit 1
fi
if [ "$rotate" = 1 ]; then
  [ -n "$old_id" ] || { echo "ERROR: --rotate given but $config has no keys.build" >&2; exit 1; }
  now="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  tmp="$(mktemp)"
  jq --arg id "$old_id" --arg now "$now" '
    .keys |= map(if .key_id == $id and .revoked_at == null then . + {revoked_at: $now} else . end)
    | .endorsements = [(.endorsements // [])[] | select(.subject_key_id != $id)]
  ' "$keys_json" > "$tmp" && mv "$tmp" "$keys_json"
  rm -f ".innsigle/public/endorsements/$(printf '%s' "$old_id" | sed -E 's/[^a-zA-Z0-9]+/-/g').attestation.json"
  [ -d "$key_dir" ] && mv "$key_dir" "$key_dir.revoked-$(date -u +%Y%m%dT%H%M%SZ)"
  echo "revoked build key $old_id (keys.json revoked_at=$now; endorsement dropped; local PEMs moved aside)"
fi
[ -e "$key_dir/ed25519.priv.pem" ] && { echo "ERROR: $key_dir/ed25519.priv.pem already exists" >&2; exit 1; }

umask 077
bash scripts/innsigle-cli.sh keygen --out-dir "$key_dir" 2>/dev/null
build_id="$(tr -d '\n' < "$key_dir/key-id.txt")"
build_pub="$(tr -d '\n' < "$key_dir/ed25519.pub.raw.b64url")"
human_id="$(jq -r '.issuer.key_id' "$config")"
now="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

tmp="$(mktemp)"
jq --arg human "$human_id" --arg id "$build_id" --arg pub "$build_pub" --arg now "$now" '
  .keys |= map(if .key_id == $human then . + {role: "human"} else . end)
  | .keys += [{key_id: $id, alg: "ed25519", public_key: $pub, created_at: $now, revoked_at: null, role: "build"}]
  | .endorsements //= []
' "$keys_json" > "$tmp" && mv "$tmp" "$keys_json"

tmp="$(mktemp)"
jq --arg human "$human_id" --arg id "$build_id" '
  .keys.human = ((.keys.human // {}) + {key_id: $human, role: "human"})
  | .keys.build = {key_id: $id, role: "build"}
' "$config" > "$tmp" && mv "$tmp" "$config"

cat <<MSG
ok: build key $build_id
    private half: $key_dir/ed25519.priv.pem (gitignored; back it up somewhere private, e.g. 1Password)
    public half:  added to $keys_json (role build); id recorded in $config (keys.build)

Next, in order:
  1. gh secret set INNSIGLE_BUILD_KEY --repo $repo_slug < $key_dir/ed25519.priv.pem
  2. just innsigle-endorse       # human key endorses the build key (op signed in)
  3. git add $config $keys_json .innsigle/public/endorsements && git commit
MSG
