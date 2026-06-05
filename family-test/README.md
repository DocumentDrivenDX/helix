# family-test — vertical slice proving the marker + linkage design

Self-contained playground that exercises the design at
`docs/helix/02-design/design-2026-06-04-helix-family-marker-and-linkages.md`
end-to-end without touching the existing helix tree.

## Layout

```
family-test/
├── library/                 minimal helix-library plugin (2 types)
├── methodology-product/     minimal helix product methodology (1 graph, ~6 types in scope)
├── consumer/                test workspaces with .helix.yml + instance docs
│   ├── clean/               valid baseline
│   ├── bad-edge-kind/       instance edge uses kind not in graph
│   ├── missing-target/      instance edge to nonexistent doc
│   ├── planned-forward/     status: planned escape hatch
│   └── malformed-marker/    .helix.yml hard-fail variants
└── run-tests.sh             driver — runs every scenario, asserts expected exit code
```

## Run it

```sh
bash family-test/run-tests.sh
```

Each scenario prints PASS / FAIL and the validator's actual exit code.
A FAIL means the design's claim about that scenario doesn't hold.

## What this proves

- Marker parsing + hard-fail rules M001-M006
- Graph parsing + type-pair edge resolution
- Instance frontmatter parsing + edge resolution against active graph
- Type-mode: library `meta.yml` rejected if it carries `relationships:`
- Forward references via `status: planned`
- Cross-methodology edge resolution (advisory `informs`)

## What this does NOT prove

- Real Claude Code skill activation (the SKILL.md prose drives an agent;
  to test, install both plugins in a real session and run a probe prompt)
- Library version-bump deprecation (would need 2+ library versions on disk)
- Pre-commit hook integration (just a CLI invocation here)
- Performance at scale (single-digit fixtures only)

These are flagged but out-of-scope for the slice.
