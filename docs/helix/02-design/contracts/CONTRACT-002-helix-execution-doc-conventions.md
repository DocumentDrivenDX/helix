# CONTRACT-002: HELIX Execution-Document Conventions

**Status:** Draft  
**Owner:** HELIX maintainers  
**Related:** [CONTRACT-001](CONTRACT-001-ddx-helix-boundary.md), [FEAT-011](../../01-frame/features/FEAT-011-slider-autonomy.md), [TD-011](../technical-designs/TD-011-slider-autonomy-implementation.md), [Quality Ratchets](../../../workflows/ratchets.md)

## Purpose

This contract defines how HELIX authors the execution documents and metric /
ratchet declarations that DDx will discover and run.

It is an authoring contract, not a DDx implementation spec.

- **HELIX owns**: where these artifacts live, how they are named, how they
  link to governing artifacts, and which ones are merge-blocking versus
  observational.
- **DDx owns**: discovery, execution, result capture, metric projection,
  preserve / merge mechanics, and runtime storage.

The goal is to make execution artifacts deterministic enough for fixture-based
workflow testing and repeatable prompt iteration.

## Scope Boundary

This contract covers:
- execution-document location and naming
- linking rules to FEAT / US / TD / TP and other governing artifacts
- required versus observational execution semantics
- metric definition references
- ratchet declaration linkage
- relationship between execution docs, implementation beads, and verification
  passes

This contract does **not** define:
- DDx graph internals
- DDx execution-run storage
- DDx metric projection internals
- project-specific enforcement scripts or floor fixture formats

## Execution Document Locations and Naming

### Primary location
HELIX execution documents live under:

```text
docs/helix/03-test/executions/
```

This keeps them in the test / verification layer of the artifact stack,
alongside test plans, while still making them graph-authored documents that DDx
can discover.

### Naming convention
Execution documents use this filename pattern:

```text
EXEC-<nnn>-<slug>.md
```

Examples:
- `EXEC-001-auth-flow-validation.md`
- `EXEC-002-api-contract-conformance.md`
- `EXEC-003-coverage-ratchet-enforcement.md`

Rules:
- `EXEC-<nnn>` must be unique within the repository
- `<slug>` should describe the validation purpose, not the implementation
  detail
- the filename slug should match the document title closely enough for humans
  to navigate easily

### Document identity
Execution documents should use normal HELIX / DDx graph identity patterns:

```yaml
---
ddx:
  id: EXEC-001
  depends_on:
    - TP-036
    - FEAT-011
---
```

The body should also reference governing artifacts using `[[ID]]` syntax.

## Linking Rules to Governing Artifacts

Execution documents are never orphaned. Each one must link to the artifact(s)
that justify its existence.

### Minimum linking requirements
Every execution document must link to at least one governing artifact via both:
- frontmatter graph dependencies (`ddx.depends_on` or legacy-compatible form)
- body references using `[[ID]]`

### Preferred governing links
Use the nearest authoritative artifact that explains **why** the validation
exists.

| Execution purpose | Minimum governing link |
|---|---|
| feature-level validation | `FEAT-*` or `US-*` |
| implementation / design validation | `TD-*` or `TP-*` |
| cross-cutting technical validation | `ADR-*` and/or `SD-*` |
| workflow / policy validation | workflow doc or contract doc ID |
| ratchet enforcement | metric definition + ratchet policy source |

### Linking examples
A feature-backed execution doc should usually look like:

```yaml
---
ddx:
  id: EXEC-002
  depends_on:
    - FEAT-011
    - TP-011
---
```

```markdown
# EXEC-002: Slider autonomy verification

**Governing Feature**: [[FEAT-011]]  
**Governing Test Plan**: [[TP-011]]
```

### No redundant authority chains
Do not link to every upstream artifact when one nearer governing artifact is
sufficient. Prefer the nearest artifact that directly defines the behavior
being checked.

## Required vs Observational Execution Semantics

Execution documents must explicitly communicate whether their result blocks
landing.

### Required executions
A required execution is merge-blocking. Use this when failure means the current
attempt must not land.

Declare it explicitly in the document metadata:

```yaml
execution:
  required: true
```

Required executions should be used for:
- correctness-critical validations
- build / type / lint gates that must pass before landing
- contract conformance that would make the result invalid if broken
- ratchet enforcement when regression must prevent merge
- validations explicitly called out as mandatory in a governing artifact

### Observational executions
An observational execution records evidence but does not by itself block merge.

Declare it explicitly:

```yaml
execution:
  required: false
```

Observational executions should be used for:
- exploratory measurements
- trend collection
- advisory diagnostics
- early candidate validations not yet promoted to merge blockers

### Required is not implied by location
An execution doc in `03-test/executions/` is **not** automatically required.
The blocking behavior must be explicit in its metadata and justified by its
linked governing artifacts.

## Metric and Ratchet Declaration Conventions

### Metric definitions
Metric definitions live under:

```text
docs/helix/06-iterate/metrics/<name>.yaml
```

Existing HELIX metric definitions already follow this pattern.

Each execution document that produces or enforces a metric should reference the
metric definition by path and by name.

Example:

```yaml
execution:
  required: true
metric:
  name: principles-injection-alignment
  definition: docs/helix/06-iterate/metrics/principles-injection-alignment.yaml
```

### Ratchet-backed executions
When an execution enforces a ratchet, it should reference:
- the metric definition it measures
- the ratchet policy source in `workflows/ratchets.md`
- the project floor fixture or enforcement command, if one exists

Example:

```yaml
execution:
  required: true
metric:
  name: coverage
  definition: docs/helix/06-iterate/metrics/coverage.yaml
ratchet:
  policy: workflows/ratchets.md#test-coverage-ratchet
  enforcement: project floor fixture + enforcement command
```

### Separation of concerns
- metric definitions define **what is measured**
- ratchet policy defines **how regression is judged**
- execution docs define **when / why the measurement runs for a workflow step**

Do not collapse all three concerns into one file.

## Relationship to Phase Gates and Existing Workflow Docs

HELIX already contains workflow-gate YAML files such as:
- `workflows/phases/*/input-gates.yml`
- `workflows/phases/*/exit-gates.yml`

These remain the source of truth for generic phase gate requirements.

Execution docs should relate to them as follows:

### Phase gates
Phase gate YAML describes the gate requirement at the workflow level.

### Execution docs
Execution docs provide the graph-authored validation artifact that DDx can
select and run for a specific bead / governing artifact path.

### Metric docs
Metric YAML defines the measured quantity and command shape.

### Ratchet policy
`workflows/ratchets.md` defines the ratchet pattern and how floor enforcement
fits into HELIX.

Execution docs may reference phase gate YAML or ratchet policy, but should not
restate those contracts unnecessarily.

## Relationship to Implementation Beads and Verification Passes

Execution docs are the bridge between governing artifacts and DDx-managed
verification.

### During implementation
When HELIX dispatches an implementation bead, DDx should be able to discover
execution docs linked to that bead's governing artifacts.

### During verification
Those execution docs define which validations are expected to run for the
current attempt.

### During preserved-attempt analysis
Observational and required execution results both remain useful inputs to:
- preserve vs merge interpretation
- follow-on bead creation
- prompt iteration
- ratchet review

### Convention for author intent
If a bead is expected to trigger a particular validation, there should be a
clear graph path from the bead's governing artifact(s) to the execution doc.
If that path is not obvious, the execution doc is under-linked.

## Minimum Authoring Checklist

Before an execution document is considered ready, verify:

- [ ] it lives under `docs/helix/03-test/executions/`
- [ ] its filename follows `EXEC-<nnn>-<slug>.md`
- [ ] it has a unique graph identity in frontmatter
- [ ] it links to its governing artifact(s) in frontmatter and body
- [ ] `execution.required` is explicitly set to `true` or `false`
- [ ] any metric reference points to a concrete file under `docs/helix/06-iterate/metrics/`
- [ ] any ratchet reference points to `workflows/ratchets.md` and the project enforcement source
- [ ] the document clearly states what it validates and why that validation exists
- [ ] the document is specific enough to support deterministic fixture authoring later

## References

- [CONTRACT-001: DDx / HELIX Boundary Contract](CONTRACT-001-ddx-helix-boundary.md)
- [FEAT-011: Slider Autonomy Control](../../01-frame/features/FEAT-011-slider-autonomy.md)
- [TD-011: Slider Autonomy Implementation](../technical-designs/TD-011-slider-autonomy-implementation.md)
- [Quality Ratchets](../../../workflows/ratchets.md)
- `workflows/phases/*/input-gates.yml`
- `workflows/phases/*/exit-gates.yml`
- `docs/helix/06-iterate/metrics/*.yaml`
