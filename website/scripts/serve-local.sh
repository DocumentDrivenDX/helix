#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

uv run --project ../tools/documentor documentor schemas --root ..

echo "Starting HELIX microsite at http://eitri:1315/helix/"
echo "Local review paths must include /helix, for example:"
echo "  http://eitri:1315/helix/artifact-types/discover/product-vision/"

exec hugo server \
  --bind 0.0.0.0 \
  --baseURL http://eitri:1315/helix/ \
  --port 1315 \
  --appendPort=false \
  --disableFastRender \
  "$@"
