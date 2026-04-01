---
name: helix-evolve
description: Thread a new requirement through the artifact stack — update governing docs, detect conflicts, create tracker issues. Use when requirements change, features are requested, or incidents reveal needed capabilities.
argument-hint: '"requirement description" [--scope S] [--artifact ID] [--from source]'
---

# Evolve: Propagate Requirements Through the Artifact Stack

When a new requirement arrives — feature request, constraint change, incident
learning, spec amendment — this skill threads it through the full governing
artifact stack from vision down to tracker issues.

## When to Use

- A new feature is requested or a capability needs to be added
- An incident or bug reveals a missing constraint or policy
- An existing spec needs amendment (new acceptance criteria, changed behavior)
- Customer feedback identifies a gap in the current design
- A dependency or constraint changes (new library, API version, compliance rule)

## What It Does

1. Analyzes the requirement and identifies affected subsystems
2. Discovers which governing artifacts need updating
3. Detects conflicts with existing artifacts and open work
4. Updates artifacts in authority order (vision → specs → designs → test plans)
5. Creates properly triaged tracker issues for implementation
6. Wires dependencies to existing open issues
7. Produces an evolution report with conflicts flagged for human resolution

## Examples

```bash
# New feature requirement
helix evolve "Add WAL compression support with configurable algorithms"

# Scoped amendment
helix evolve --scope area:wal "WAL segments should support LZ4 and zstd compression"

# Target a specific artifact
helix evolve --artifact SD-017 "Verification engine needs loom support for concurrency testing"

# Incident-driven requirement
helix evolve --from incident "INC-042: ingest pipeline needs circuit breakers to prevent cascade failure"
```

## References

- Action prompt: `workflows/actions/evolve.md`
- Authority order: `workflows/actions/implementation.md` (Authority Order section)
- Triage validation: `scripts/tracker.sh` (tracker_validate_create)
- Tracker conventions: `workflows/TRACKER.md`
