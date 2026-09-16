#!/usr/bin/env bash
# Run the Innsigle CLI at the version this repo is tested against.
#
# Every caller (just recipes, scripts/innsigle-seal.sh, tests/validate-innsigle.sh,
# the website workflows) goes through this wrapper so the seal format and the
# `seal --all` role policy (Innsigle ADR-004) cannot drift between a
# contributor's machine and CI. Override the binary with INNSIGLE_BIN (for
# example `INNSIGLE_BIN=innsigle` for a global install, or a path to a checkout's
# src/cli.mjs) and the pin with INNSIGLE_VERSION.
set -euo pipefail

INNSIGLE_VERSION="${INNSIGLE_VERSION:-v0.5.0}"

if [ -n "${INNSIGLE_BIN:-}" ]; then
  # shellcheck disable=SC2086  # INNSIGLE_BIN may carry arguments ("node path/to/cli.mjs")
  exec $INNSIGLE_BIN "$@"
fi
exec npx --yes --package="github:DocumentDrivenDX/innsigle#${INNSIGLE_VERSION}" innsigle "$@"
