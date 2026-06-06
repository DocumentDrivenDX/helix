#!/usr/bin/env bash
# Claude Code install scenario.
#
# Three modes:
#   default (per-PR gate): NO persistent install. verify.sh loads via
#     `claude --plugin-dir /workspace/helix` and parses init JSON to assert
#     the plugin + skill registered cleanly. Catches load-time defects in
#     THIS revision (not whatever GitHub HEAD happens to be).
#   TEST_LOCAL_MARKETPLACE=1 (per-PR marketplace flow): rewrites
#     marketplace.json `source` to a local path so the real `plugin install`
#     code path runs against THIS revision.
#   TEST_PUBLISHED=1 (post-merge smoke): runs the documented marketplace flow
#     against the published GitHub repo. Catches HTTPS-clone regressions.

set -euo pipefail

echo "claude version:"
claude --version

if [[ "${TEST_PUBLISHED:-}" == "1" ]]; then
  echo
  echo "→ real marketplace install from published repo (HTTPS clone from GitHub)"
  claude plugin marketplace add DocumentDrivenDX/helix
  echo y | claude plugin install helix@helix --scope user

elif [[ "${TEST_LOCAL_MARKETPLACE:-}" == "1" ]]; then
  echo
  echo "→ marketplace install against the LOCAL checkout (rewrites marketplace.json)"
  cp -r /workspace/helix /tmp/helix-local
  # Claude Code's git-clone source needs a fetchable repo; init one in /tmp.
  cd /tmp/helix-local
  git init -q
  git add -A
  git -c user.email=ci@helix -c user.name=ci commit -qm seed
  cd /
  python3 - <<'PY'
import json
p = "/tmp/helix-local/.claude-plugin/marketplace.json"
m = json.load(open(p))
m["plugins"][0]["source"] = {"source": "url", "url": "file:///tmp/helix-local"}
json.dump(m, open(p, "w"), indent=2)
PY
  claude plugin marketplace add /tmp/helix-local
  echo y | claude plugin install helix@helix --scope user

else
  echo
  echo "→ default per-PR mode: no persistent install."
  echo "  verify.sh loads via --plugin-dir and parses init JSON."
fi

if [[ "${TEST_PUBLISHED:-}" == "1" || "${TEST_LOCAL_MARKETPLACE:-}" == "1" ]]; then
  echo
  echo "claude plugin list:"
  claude plugin list 2>&1
fi
