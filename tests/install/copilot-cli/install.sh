#!/usr/bin/env bash
# GitHub Copilot install: the canonical path is committing
# .github/copilot-instructions.md to the adopter repo. For this scenario
# we simulate adoption by copying the HELIX repo's own file into a
# scratch project, then exercising the Copilot CLI against it.

set -euo pipefail

if command -v gh >/dev/null 2>&1; then
  echo "gh version: $(gh --version | head -1)"
fi

# Set up a scratch adopter repo with HELIX's copilot-instructions vendored in.
SCRATCH=/tmp/copilot-helix-adopter
rm -rf "$SCRATCH"
mkdir -p "$SCRATCH/.github"
cp /workspace/helix/.github/copilot-instructions.md "$SCRATCH/.github/"

# Also vendor the routing skill so prompts can reference it.
mkdir -p "$SCRATCH/skills"
cp -r /workspace/helix/skills/helix "$SCRATCH/skills/"
mkdir -p "$SCRATCH/workflows"
ln -sf /workspace/helix/workflows "$SCRATCH/workflows"

git init -q "$SCRATCH" || true
echo "✓ scratch adopter repo at $SCRATCH"
echo "  .github/copilot-instructions.md: $(wc -l < "$SCRATCH/.github/copilot-instructions.md") lines"
