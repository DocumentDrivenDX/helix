#!/usr/bin/env bash
# Seal microsite content sources with Innsigle colophon attestations.
#
# Thin wrapper over `innsigle seal --all` (Innsigle v0.5.0, ADR-004). The CLI
# walks `content_globs` from .innsigle/config.json (docs/website/content/**/*.md),
# writes one claim per source at .innsigle/public/claims/<slug>.attestation.json
# (slug = path relative to the content root, non-alphanumeric runs -> "-"; the
# badge partial website/layouts/_partials/components/comments.html derives the
# same slug at build time), skips claims that are already up to date, and
# removes claims whose page no longer exists.
#
# Two keys, one issuer (ADR-004):
#   pages the generators stamp with `generated: true` frontmatter
#   (scripts/generate-reference.py, publish-artifacts.py, publish-resources.py)
#       -> model-primary, signed by the BUILD key (CI: INNSIGLE_BUILD_KEY)
#   everything else (curated)
#       -> mixed, signed by the HUMAN key (1Password, never in CI)
# Frontmatter, not path, decides: research/_index.md is hand-authored even
# though it lives in a generated tree. A file whose key is absent is skipped,
# not failed, so `just innsigle-seal` on a laptop seals the curated pages and
# leaves the generated ones to CI; `--role human` / `--role build` restrict the
# run to one key and fail when that key is missing.
#
# Only human-key claims are committed. Build-key claims are minted by CI at
# every build, so they never go stale in git.
#
# Requires: .innsigle/config.json (committed), and for the human role the
# 1Password CLI (`op`) signed in.
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$repo_root"

[ -f .innsigle/config.json ] || {
  echo "ERROR: .innsigle/config.json not found (it is committed; are you in the repo?)" >&2
  exit 1
}
case " $* " in
  *" --role build "*) ;;
  *) command -v op >/dev/null || echo "note: 1Password CLI (op) not found; curated pages will be skipped" >&2 ;;
esac

exec bash scripts/innsigle-cli.sh seal --all "$@"
