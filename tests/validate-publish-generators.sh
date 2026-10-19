#!/usr/bin/env bash
# Run every generator in skills/helix/scripts/publish_generate.py on a small fixture shaped like the
# repository its trait detects, and check the row a reader needs most (publishing.md, Traits).
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
gen="$repo_root/skills/helix/scripts/publish_generate.py"
tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT
fail() { echo "FAIL: $*" >&2; exit 1; }
python3 -c 'import yaml, tomllib' 2>/dev/null || { echo "SKIP: needs Python 3.11 and PyYAML"; exit 0; }
make() { python3 "$gen" "$1" --root "$2" --page "$tmpdir/out/$1.md" --flow x --title T >/dev/null || fail "$1 wrote nothing"; }
expect() { grep -qF -- "$2" "$tmpdir/out/$1.md" || fail "$1: expected '$2' in: $(cat "$tmpdir/out/$1.md")"; }

r="$tmpdir/app"; mkdir -p "$r"
cat >"$r/databricks.yml" <<'Y'
resources:
  apps:
    web:
      config:
        env:
          # Which model answers (the tier names a gateway service).
          - name: APP_MODEL
            value: ${var.model}
          - name: APP_VOLUME
            value_from: uploads
targets:
  prod:
    resources:
      apps:
        web:
          config:
            env:
              - name: APP_SECRET_HOST
                value: internal.example.test
Y
make databricks-app-settings "$r"
expect databricks-app-settings '| `APP_MODEL` | every target | a bundle variable, set per target | Which model answers (the tier names a gateway service). |'
expect databricks-app-settings '| `APP_VOLUME` | every target | the app resource `uploads` |'
grep -q "internal.example.test" "$tmpdir/out/databricks-app-settings.md" && fail "a setting's value must never be published"

r="$tmpdir/jobs"; mkdir -p "$r/jobs"
cat >"$r/jobs/nightly.yml" <<'Y'
resources:
  jobs:
    nightly:
      name: nightly_load
      schedule: {quartz_cron_expression: "0 0 3 * * ?", timezone_id: UTC, pause_status: PAUSED}
      tasks:
        - task_key: land
        - task_key: load
          depends_on: [{task_key: land}]
Y
make databricks-jobs "$r"
expect databricks-jobs '| `nightly_load` | `0 0 3 * * ?` UTC (paused) | 2 | `jobs/nightly.yml` |'
expect databricks-jobs '`land` → `load`'

r="$tmpdir/lib"; mkdir -p "$r/src/kit"
printf 'from kit.core import Engine, run\n__all__ = ["Engine", "run"]\n' >"$r/src/kit/__init__.py"
printf 'class Engine:\n    """Runs the work."""\n\ndef run():\n    """Starts it."""\n' >"$r/src/kit/core.py"
make python-api "$r"
expect python-api '| `Engine` | `kit.core` | Runs the work. |'
expect python-api '| `run` | `kit.core` | Starts it. |'

r="$tmpdir/npm"; mkdir -p "$r/packages/ui"
printf '{"name": "@acme/ui", "version": "1.2.0", "description": "Widgets. More text.", "exports": {".": "./i.js"}, "bin": {"acme-ui": "./c.js"}}\n' >"$r/packages/ui/package.json"
make npm-packages "$r"
expect npm-packages '| `@acme/ui` | 1.2.0 | yes | Widgets. | `.` | `acme-ui` |'

r="$tmpdir/tf"; mkdir -p "$r/net"
printf 'resource "azurerm_network" "main" {}\nresource "azurerm_subnet" "a" {}\nresource "random_id" "x" {}\n' >"$r/net/main.tf"
make opentofu-resources "$r"
expect opentofu-resources '| `net` | 3 | azurerm 2, random 1 |'
grep -q '"main"' "$tmpdir/out/opentofu-resources.md" && fail "resource names must not be published"

r="$tmpdir/st"; mkdir -p "$r/pages"
printf '"""Past runs, and their evidence."""\nimport streamlit as st\n' >"$r/pages/2_Runs.py"
make streamlit-screens "$r"
expect streamlit-screens '| Runs | Past runs, and their evidence. |'

r="$tmpdir/catalog"; mkdir -p "$r/workflows/activities/02-design/artifacts/adr"
printf 'artifact:\n  name: Architecture Decision Record\n  id: adr\ndescription: |\n  One decision. With reasons.\n' >"$r/workflows/activities/02-design/artifacts/adr/meta.yml"
make helix-artifact-types "$r"
expect helix-artifact-types '| Architecture Decision Record | `adr` | One decision. |'

echo "OK: every publish_generate.py generator writes its reference from its fixture, and none publishes a value, a name, or an id it should not"
