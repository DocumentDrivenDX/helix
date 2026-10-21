#!/usr/bin/env bash
# Exercise `documentor estate` on two fixture repositories: an agreed
# connection renders as one edge; a one-sided claim blocks; a system outside the estate warns
# (workflows/references/architecture-model.md, "The estate").
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
rg="${DOCUMENTOR:-documentor}"
command -v "$rg" >/dev/null 2>&1 || { echo "FAIL: documentor is not on PATH; run the tests with uv (just test)"; exit 1; }
tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT
fail() { echo "FAIL: $*" >&2; exit 1; }

mkdir -p "$tmpdir/alpha/docs/helix/02-design" "$tmpdir/beta/docs/helix/02-design"
cat >"$tmpdir/alpha/docs/helix/02-design/architecture-model.toml" <<'EOF'
[system]
id = "alpha"
repo = "org/alpha"

[[element]]
id = "alpha"
name = "Alpha"
kind = "system"
status = "built"
evidence = [{ path = "app.py", contains = "app" }]

[[element]]
id = "beta"
name = "Beta"
kind = "external"
status = "built"
system = "beta"
evidence = [{ path = "config.toml", contains = "beta" }]

[[element]]
id = "gamma"
name = "Gamma"
kind = "external"
status = "decided"
system = "gamma"
evidence = [{ path = "config.toml", contains = "gamma" }]

[[relation]]
from = "alpha"
to = "beta"
label = "calls over HTTP"
status = "built"
evidence = [{ path = "client.py", contains = "beta" }]
EOF
cat >"$tmpdir/beta/docs/helix/02-design/architecture-model.toml" <<'EOF'
[system]
id = "beta"
repo = "org/beta"

[[element]]
id = "beta"
name = "Beta"
kind = "system"
status = "built"
evidence = [{ path = "app.py", contains = "app" }]

[[element]]
id = "alpha"
name = "Alpha"
kind = "external"
status = "built"
system = "alpha"
evidence = [{ path = "auth.py", contains = "alpha" }]

[[relation]]
from = "alpha"
to = "beta"
label = "HTTP, signed"
status = "built"
evidence = [{ path = "routes.py", contains = "alpha" }]
EOF
cat >"$tmpdir/estate.toml" <<EOF
title = "Fixture estate"
takeaway = "Two systems, one connection."
[[system]]
id = "alpha"
repo = "org/alpha"
path = "$tmpdir/alpha"
[[system]]
id = "beta"
repo = "org/beta"
path = "$tmpdir/beta"
EOF

# Agreed: both sides state alpha -> beta; gamma is named but outside the estate.
$rg estate render --config "$tmpdir/estate.toml" --out "$tmpdir/estate.md" >"$tmpdir/out" 2>&1 \
  || fail "an agreed estate should pass: $(cat "$tmpdir/out")"
grep -Eq "^WARNING +unresolved .*'gamma'" "$tmpdir/out" || fail "expected unresolved gamma: $(cat "$tmpdir/out")"
grep -q 'alpha -->|"calls over HTTP"| beta' "$tmpdir/estate.md" || fail "expected one solid edge: $(cat "$tmpdir/estate.md")"
grep -q "| alpha | beta | calls over HTTP | HTTP, signed |" "$tmpdir/estate.md" || fail "expected both sides in the table"
grep -q "org/alpha@worktree" "$tmpdir/estate.md" || fail "expected the model's commit (worktree for a plain directory)"

# The explained estate: an agent writes it from the digest of the models, a second one checks it,
# and the page keeps the landscape and the tables as evidence. A fake agent stands in for both.
cat >"$tmpdir/agent.py" <<'PY'
import sys
model, prompt = sys.argv[1], sys.stdin.read()
open(sys.argv[2], "a").write(f"{model} {'check' if prompt.startswith('You are checking') else 'write'}\n")
if prompt.startswith("You are checking"):
    print("VERDICT: pass")
else:
    print("Here it is.\n\n## Where things sit\n\nAlpha and Beta.\n\n## What each system does\n\nAlpha calls Beta.\n\n"
          "## How they connect\n\nAlpha reads from Beta.\n\n## Journeys across systems\n\nNone.\n\n## Open questions\n\nGamma.")
PY
$rg estate write --config "$tmpdir/estate.toml" --dry-run >"$tmpdir/prompt" 2>&1 || fail "estate write --dry-run: $(cat "$tmpdir/prompt")"
grep -q "^- connection " "$tmpdir/prompt" || fail "the writer's brief should hold every connection from the models"
grep -q "^- Open questions" "$tmpdir/prompt" || fail "the brief should name the sections"
$rg estate write --config "$tmpdir/estate.toml" --out "$tmpdir/explained.md" \
  --agent "python3 $tmpdir/agent.py {model} $tmpdir/calls" >"$tmpdir/out" 2>&1 || fail "estate write: $(cat "$tmpdir/out")"
grep -q "written=agent-opus reviewed=" "$tmpdir/explained.md" || fail "the page should name its writer and its evaluator"
grep -q '^```mermaid' "$tmpdir/explained.md" || fail "the page keeps the landscape"
grep -q "^## How they connect" "$tmpdir/explained.md" || fail "the page holds the agent's sections"
grep -q "Here it is" "$tmpdir/explained.md" && fail "text before the first section should be dropped"
grep -q "^### Connections" "$tmpdir/explained.md" || fail "the generated tables stay as evidence"
[ "$(cat "$tmpdir/calls")" = "$(printf 'opus write\nsonnet check')" ] || fail "one writer call, one evaluator call: $(cat "$tmpdir/calls")"

# One-sided: beta no longer says alpha calls it.
sed -i.bak '/^\[\[relation\]\]/,$d' "$tmpdir/beta/docs/helix/02-design/architecture-model.toml"
$rg estate check --config "$tmpdir/estate.toml" >"$tmpdir/out" 2>&1 && fail "a one-sided claim should block"
grep -Eq "^BLOCKING +one-sided +alpha's model says alpha -> beta .*beta's model \(org/beta\) does not" "$tmpdir/out" \
  || fail "expected one-sided: $(cat "$tmpdir/out")"

# A model whose [system] id is not the estate's, or that cannot be read, blocks.
sed -i.bak 's/^id = "beta"$/id = "delta"/' "$tmpdir/beta/docs/helix/02-design/architecture-model.toml"
$rg estate check --config "$tmpdir/estate.toml" >"$tmpdir/out" 2>&1 && fail "a mismatched [system] id should block"
grep -Eq "^BLOCKING +no-system " "$tmpdir/out" || fail "expected no-system: $(cat "$tmpdir/out")"
rm "$tmpdir/beta/docs/helix/02-design/architecture-model.toml"
$rg estate check --config "$tmpdir/estate.toml" >"$tmpdir/out" 2>&1 && fail "a missing model should block"
grep -Eq "^BLOCKING +missing-model " "$tmpdir/out" || fail "expected missing-model: $(cat "$tmpdir/out")"

echo "OK: documentor estate composes two models into one landscape, writes the explained estate through a writer and an evaluator, blocks a one-sided connection, a mismatched or missing model, and warns about a system outside the estate"
