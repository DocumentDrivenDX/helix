# T24 — artifact-instance link respects artifact graph → validator clean [HIGH RISK]

**Flow classification:** current artifact-instance link control. This fixture
does not define a scope-instance or multi-flow routing rule.

## Scenario

The workspace has a valid `.helix.yml` declaring helix only, an
in-tree `graph.yml` declaring `prd informs feature-specification`,
and a PRD-001 instance with `ddx.links: [{ kind: informs, to: FEAT-001 }]`
plus a FEAT-001 instance that exists in the corpus.

## Why it matters

Positive path for the artifact linkage relaxation. The validator must:
1. Read the marker, resolve scope to docs/helix/.
2. Walk the corpus, build instance_index {PRD-001, FEAT-001}.
3. For each ddx.links[] entry, look up (source_type, kind,
   target_type) in graph.edges → permitted.
4. Resolve `to:` against instance_index → resolved.
5. Exit 0.

If this fails, the whole relaxation is dead. Pair with T25/T26 to
disambiguate which step regresses.

## What passes

- `helix_check.py marker .helix.yml` exits 0.
- No I-class or G-class violations in stderr.

## What fails

- Any non-zero exit.
- Any violation record in JSON output.

## Risk

HIGH. Positive baseline for the artifact-instance resolution contract.
