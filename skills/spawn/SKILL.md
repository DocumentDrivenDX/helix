---
name: helix-spawn
description: Launch the HELIX multi-agent swarm. Use when the user wants `helix spawn` behavior and `ntm` is available.
argument-hint: "[spawn args]"
disable-model-invocation: true
---

# Spawn

Launch the HELIX multi-agent swarm through the CLI.

## Steps

1. Run `helix spawn $ARGUMENTS`.
2. Report the spawned session details or any missing prerequisite such as `ntm`.
3. Do not simulate swarm execution if the prerequisite tooling is absent.
