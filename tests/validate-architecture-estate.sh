#!/usr/bin/env bash
# Exercise skills/helix/scripts/architecture_estate.py on two fixture repositories: an agreed
# connection renders as one edge; a one-sided claim blocks; a system outside the estate warns
# (workflows/references/architecture-model.md, "The estate").
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
estate="$repo_root/skills/helix/scripts/architecture_estate.py"
tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT
fail() { echo "FAIL: $*" >&2; exit 1; }
python3 -c 'import tomllib' 2>/dev/null || python3 -c 'import tomli' 2>/dev/null \
  || { echo "SKIP: architecture_estate.py needs Python 3.11 (tomllib) or tomli"; exit 0; }

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
python3 "$estate" render --config "$tmpdir/estate.toml" --out "$tmpdir/estate.md" >"$tmpdir/out" 2>&1 \
  || fail "an agreed estate should pass: $(cat "$tmpdir/out")"
grep -Eq "^WARNING +unresolved .*'gamma'" "$tmpdir/out" || fail "expected unresolved gamma: $(cat "$tmpdir/out")"
grep -q 'alpha -->|"calls over HTTP"| beta' "$tmpdir/estate.md" || fail "expected one solid edge: $(cat "$tmpdir/estate.md")"
grep -q "| alpha | beta | calls over HTTP | HTTP, signed |" "$tmpdir/estate.md" || fail "expected both sides in the table"
grep -q "org/alpha@worktree" "$tmpdir/estate.md" || fail "expected the model's commit (worktree for a plain directory)"

# One-sided: beta no longer says alpha calls it.
sed -i.bak '/^\[\[relation\]\]/,$d' "$tmpdir/beta/docs/helix/02-design/architecture-model.toml"
python3 "$estate" check --config "$tmpdir/estate.toml" >"$tmpdir/out" 2>&1 && fail "a one-sided claim should block"
grep -Eq "^BLOCKING +one-sided +alpha's model says alpha -> beta .*beta's model \(org/beta\) does not" "$tmpdir/out" \
  || fail "expected one-sided: $(cat "$tmpdir/out")"

# A model whose [system] id is not the estate's, or that cannot be read, blocks.
sed -i.bak 's/^id = "beta"$/id = "delta"/' "$tmpdir/beta/docs/helix/02-design/architecture-model.toml"
python3 "$estate" check --config "$tmpdir/estate.toml" >"$tmpdir/out" 2>&1 && fail "a mismatched [system] id should block"
grep -Eq "^BLOCKING +no-system " "$tmpdir/out" || fail "expected no-system: $(cat "$tmpdir/out")"
rm "$tmpdir/beta/docs/helix/02-design/architecture-model.toml"
python3 "$estate" check --config "$tmpdir/estate.toml" >"$tmpdir/out" 2>&1 && fail "a missing model should block"
grep -Eq "^BLOCKING +missing-model " "$tmpdir/out" || fail "expected missing-model: $(cat "$tmpdir/out")"

echo "OK: architecture_estate.py composes two models into one landscape, blocks a one-sided connection, a mismatched or missing model, and warns about a system outside the estate"
