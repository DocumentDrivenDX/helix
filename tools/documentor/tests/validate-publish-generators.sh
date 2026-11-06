#!/usr/bin/env bash
# Run every generator in `documentor generate` on a small fixture shaped like the
# repository its trait detects, and check the row a reader needs most (publishing.md, Traits).
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
rg="${DOCUMENTOR:-documentor}"
command -v "$rg" >/dev/null 2>&1 || { echo "FAIL: documentor is not on PATH; run the tests with uv (just test)"; exit 1; }
tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT
fail() { echo "FAIL: $*" >&2; exit 1; }
make() { $rg generate "$1" --root "$2" --page "$tmpdir/out/$1.md" --flow x --title T >/dev/null || fail "$1 wrote nothing"; }
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

r="$tmpdir/api"; mkdir -p "$r"
cat >"$r/openapi.json" <<'J'
{"openapi": "3.1.0", "paths": {"/claims/{id}": {"get": {"tags": ["claims"], "summary": "Read one claim. Returns 404 when absent."}},
 "/claims": {"post": {"tags": ["claims"], "summary": "Open a claim."}}},
 "components": {"schemas": {"Claim": {"example": {"ssn": "123-45-6789"}}}}}
J
make openapi-api "$r"
expect openapi-api '| claims | `/claims/{id}` | GET | Read one claim. |'
expect openapi-api 'with 1 schemas'
grep -q "123-45-6789" "$tmpdir/out/openapi-api.md" && fail "schema example values must not be published"

r="$tmpdir/cli"; mkdir -p "$r/src/tool"
printf '[project]\nname = "tool"\n[project.scripts]\ntool = "tool.cli:app"\n' >"$r/pyproject.toml"
cat >"$r/src/tool/cli.py" <<'P'
import typer
app = typer.Typer()

@app.command()
def compile_spec(path: str):
    """Compile a spec. Writes SQL beside it."""

@app.command(name="check")
def check_it():
    """Check a spec."""

run_app = typer.Typer()
app.add_typer(run_app, name="run")

@run_app.command("setup")
def run_setup():
    """Create the catalog."""
P
make cli-commands "$r"
expect cli-commands '| `tool compile-spec` | Compile a spec. |'
expect cli-commands '| `tool check` | Check a spec. |'
expect cli-commands '| `tool run setup` | Create the catalog. |'

r="$tmpdir/argparse"; mkdir -p "$r/src/tool"
printf '[project]\nname = "tool"\n[project.scripts]\ntool = "tool.cli:main"\n' >"$r/pyproject.toml"
cat >"$r/src/tool/cli.py" <<'P'
"""tool.

Usage:
    tool init    [--write]      set the project up
    tool status  [--json]       what is behind
"""
import argparse

def init():
    """Create the config. Writes beside the code."""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("init", "status"))
    sub = parser.add_subparsers()
    sub.add_parser("serve", help="Run the server. Blocks.")
P
make cli-commands "$r"
expect cli-commands '| `tool init` | Create the config. |'
expect cli-commands '| `tool status` | what is behind |'
expect cli-commands '| `tool serve` | Run the server. |'

r="$tmpdir/mcp"; mkdir -p "$r/server"
cat >"$r/server/main.py" <<'P'
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("tools")

@mcp.tool()
def search_matters(query: str) -> str:
    """Find matters by name. Case-insensitive."""
P
printf '{"mcpServers": {"docs": {"command": "npx", "args": ["-y", "docs-mcp"]}, "api": {"url": "https://mcp.example.test/sse?token=SECRET"}}}\n' >"$r/.mcp.json"
make mcp-tools "$r"
expect mcp-tools '| `search_matters` | Find matters by name. | `server/main.py` |'
expect mcp-tools '| `docs` | `npx -y docs-mcp` |'
expect mcp-tools '| `api` | `https://mcp.example.test` |'
grep -q "SECRET" "$tmpdir/out/mcp-tools.md" && fail "a server URL's path and query must not be published"

echo "OK: every documentor generator writes its reference from its fixture, and none publishes a value, a name, or an id it should not"
