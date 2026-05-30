---
ddx:
  id: ADR-004
  depends_on:
    - helix.prd
---
# ADR-004: Artifact Dependencies Are Encoded in `meta.yml.relationships` Only (No Separate `dependencies.yaml`)

| Date | Status | Deciders | Related | Confidence |
|------|--------|----------|---------|------------|
| 2026-05-30 | Accepted | HELIX maintainers | artifact-schema, frame action, audit plan 2026-05-30 | High |

## Context

| Aspect | Description |
|--------|-------------|
| Problem | The artifact-type rubric historically expected each artifact-type directory to ship a separate `dependencies.yaml` file describing inputs, outputs, and validation rules. In practice, no such file exists for any artifact type, while the same information is already encoded in `meta.yml` under `relationships` (and adjacent `validation.*` sections). The audit (`docs/helix/02-design/plan-2026-05-30-artifact-types-and-concerns-audit.md`) found `dependencies.yaml` absent for 48/48 artifact types. |
| Current State | `meta.yml.relationships` already names `depends_on` and `informs` per artifact type. `meta.yml.validation` already carries `required_sections`, `quality_checks`, and friends. The phantom `dependencies.yaml` reference survives only in two prose locations: `workflows/actions/frame.md` (validation-gate step) and `workflows/activities/01-frame/README.md` (artifact-directory description). No consumer script actually opens a `dependencies.yaml` file: `scripts/helix_align_check.py` parses the spec stack from markdown (PRD, FEAT, US, ADR) and does not touch `dependencies.yaml`; `workflows/actions/reconcile-alignment.md` references "dependencies" only as a conceptual notion. |
| Requirements | The catalog must have a single source of truth for artifact-type dependencies. The rubric must stop asking for a file the catalog does not produce. Any consumer that currently mentions `dependencies.yaml` must be repointed at `meta.yml` so the rubric and the workflow agree. |

## Decision

We ratify **`meta.yml.relationships`** as the canonical encoding of artifact-type
dependencies, and we drop `dependencies.yaml` from the artifact-type rubric.
There is no second file. There is no generated projection.

- Type-level dependencies (`depends_on`, `informs`, peer relations) live in
  `meta.yml` under `relationships`. The structured shape is already defined in
  `workflows/artifact-schema.md` under "Recommended fields".
- Type-level validation (`required_sections`, `quality_checks`,
  `pattern_checks`, `automated_checks`) lives in `meta.yml` under `validation`.
- Instance-level dependencies (one artifact instance depending on another)
  continue to live in instance frontmatter under `ddx.depends_on`, exactly as
  `workflows/artifact-schema.md` already specifies. ADR-004 does not change
  that.

**Key Points**: one source of truth (`meta.yml`) | no `dependencies.yaml`
generation step | consumer prose realigned to `meta.yml`

## Consumer-side compatibility

We choose **option (a): update consumers to read `meta.yml` directly** over
option (b): generate a transient `dependencies.yaml` projection at build/check
time. Rationale:

- `scripts/helix_align_check.py` does not currently read `dependencies.yaml` at
  all. It parses markdown (`prd.md`, `FEAT-*.md`, `US-*.md`, `ADR-*.md`) and
  scans the code tree for `@covers` citations. There is no flat dependencies
  projection to preserve. Option (b) would invent a consumer that does not
  exist.
- `workflows/actions/reconcile-alignment.md` likewise does not open a
  `dependencies.yaml` file. Its references to "dependencies" are conceptual,
  not file-bound.
- The only two real `dependencies.yaml` mentions are prose in
  `workflows/actions/frame.md` (validation-gate step) and
  `workflows/activities/01-frame/README.md` (artifact-directory description).
  Both are documentation of *where validation rules live*, not code that opens
  a file. Repointing the prose at `meta.yml.validation` and
  `meta.yml.relationships` is a textual edit, no runtime impact.
- Option (b) would add a build/check step, a generated file, and a drift
  surface (projection out of sync with `meta.yml`) for no consumer benefit.
  That is the opposite of the audit's goal.

If a future consumer ever needs a flat dependencies graph, it can either parse
`meta.yml` directly or compose a projection at read time. That decision belongs
to that consumer, not to the catalog.

## Alternatives

| Option | Pros | Cons | Evaluation |
|--------|------|------|------------|
| Generate `dependencies.yaml` per artifact type from `meta.yml` as a build step | Preserves the historical rubric shape | Adds a generated file, a drift surface, and a build/check step with no consumer that needs it | Rejected: no consumer reads the file; cost without benefit |
| Hand-author both `dependencies.yaml` and `meta.yml.relationships` | Matches the historical rubric literally | Two sources of truth; 48 missing files; encodes the same data twice; drift inevitable | Rejected: contradicts single-source goal |
| **Ratify `meta.yml.relationships` as canonical and drop `dependencies.yaml` from the rubric** | One source of truth; matches what the catalog actually ships; no generation step; rubric stops lying about expected files | Existing prose in `frame.md` and `01-frame/README.md` must be updated in the same change | **Selected: smallest sufficient alignment** |

## Consequences

| Type | Impact |
|------|--------|
| Positive | Catalog has one place to look for artifact-type dependencies and one place to look for validation rules: `meta.yml`. |
| Positive | The rubric stops asking for a file that does not exist; the 48/48 absence reported by the audit is no longer a violation. |
| Positive | Workflow prose (`workflows/actions/frame.md`, `workflows/activities/01-frame/README.md`) is repointed at the file that actually carries validation rules, removing a documentation-to-reality gap. |
| Positive | No generated projection means no projection-drift class of failure to defend against. |
| Negative | The rubric line in `workflows/artifact-schema.md` ("Recommended fields") and the prose in `workflows/actions/frame.md` / `workflows/activities/01-frame/README.md` must be updated in lockstep with this ADR; any future doc that re-introduces `dependencies.yaml` must be rejected as drift. |
| Neutral | Instance-level dependencies in `ddx.depends_on` frontmatter are unaffected; this ADR is about type-level rubric, not instance-level graph. |

## Risks

| Risk | Prob | Impact | Mitigation |
|------|------|--------|------------|
| A future workflow re-introduces `dependencies.yaml` by force of habit | M | L | Audit gate: a grep for `dependencies.yaml` outside ADR-004 itself should return zero hits after this change |
| A future consumer wants a flat dependencies projection and reinvents it ad hoc | L | M | Consumers may compose a projection from `meta.yml` at read time; no canonical file required |
| The audit's "48/48 absent" finding gets re-reported because the rubric is read out of date | L | L | Update the rubric prose in the same commit as this ADR so the next audit sees the canonical shape |

## Validation

| Success Metric | Review Trigger |
|----------------|----------------|
| Grep for `dependencies.yaml` outside ADR-004 returns zero hits in `workflows/` and `scripts/` | A workflow doc or script re-introduces `dependencies.yaml` |
| `workflows/actions/frame.md` validation-gate step references `meta.yml.validation` (not `dependencies.yaml`) | A reviewer cannot tell where validation rules live for an artifact type |
| `workflows/activities/01-frame/README.md` artifact-directory description does not list `dependencies.yaml` | A new artifact type ships a `dependencies.yaml` instead of `meta.yml` updates |
| `workflows/artifact-schema.md` "Recommended fields" no longer implies a separate dependencies file | A consumer ships code that opens `dependencies.yaml` |

## References

- [Audit plan 2026-05-30](../plan-2026-05-30-artifact-types-and-concerns-audit.md)
- [PRD](../../01-frame/prd.md)
- [Artifact schema](../../../../workflows/artifact-schema.md)
- ADR-002: HELIX Tracker Write Safety Model
- ADR-003: Autonomy Spectrum
