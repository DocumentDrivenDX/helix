# HELIX Artifact Schema

Status: Canonical schema specification

HELIX defines a portable artifact catalog and a portable artifact instance
shape. The schema is intentionally substrate-neutral: a human team, DDx,
Claude Code, Databricks Genie, or another runtime can read the same catalog and
artifact frontmatter without becoming the authority for the schema.

HELIX adopts the `ddx:` frontmatter namespace as the shared instance schema
because DDx is the current reference consumer and already ships the loader that
uses this shape. The namespace name is historical. It is not a statement that
HELIX artifacts require DDx.

## Scope

This specification covers four layers:

1. Artifact-type metadata in `meta.yml` files.
2. Instance metadata in Markdown frontmatter under the `ddx:` key.
3. Naming, directory, ID, and activity progression conventions.
4. Known consumers and the parts of the schema they read.

The schema is open. Consumers must ignore fields they do not understand unless a
field is required by this document. Artifact types may define domain-specific
extension sections when the common schema is not expressive enough.

## Artifact-type metadata: `meta.yml`

Each artifact type in the catalog may include a `meta.yml` file next to its
`template.md` and `prompt.md` files. The metadata describes the artifact type,
not a specific project artifact instance.

Canonical location:

```text
workflows/activities/<activity-number>-<activity-name>/artifacts/<artifact-type>/meta.yml
```

Example path:

```text
workflows/activities/02-design/artifacts/adr/meta.yml
```

### Required fields

| Field | Type | Meaning |
| --- | --- | --- |
| `artifact.name` | string | Human-readable artifact type name, such as `Product Vision` or `ADR`. |
| `artifact.id` | string | Stable artifact-type identifier. Use kebab-case unless the type has a widely used acronym convention. |
| `artifact.type` | string | Broad artifact class, such as `document`, `registry`, `checklist`, `plan`, `report`, or `implementation`. |
| `artifact.activity` | string | HELIX activity that owns this type. Use the activity slug, such as `discover`, `frame`, `design`, `test`, `build`, `deploy`, or `iterate`. |
| `description` | string | Practical description of what the artifact is for and when a team should create it. |
| `output.location` | string | Conventional location for instances of this type in a HELIX project. |
| `output.format` | string | Expected output format. Markdown is the default catalog format. |

### Recommended fields

| Field | Type | Meaning |
| --- | --- | --- |
| `artifact.level` | string | Granularity tier the artifact targets, such as `project`, `feature`, `story`, or `interface`. Use when the type can exist at multiple levels of the artifact hierarchy. |
| `artifact.optional` | boolean | Whether the artifact type is conditional rather than generally expected in its activity. Omit or set `false` for normal activity artifacts. |
| `voice` | string or mapping | Voice profile for generated and reviewed instances of this artifact type. Omit to inherit `artifact-signal` from `workflows/voice.yml`; use a string for a direct profile reference or a mapping when the type needs a primary profile plus bounded overrides. |
| `output.naming` | string | Naming pattern for an instance, such as `prd.md`, `FEAT-{number}-{title}.md`, or `ADR-{number}-{title}.md`. |
| `output.examples` | list | Example filenames demonstrating the naming pattern. |
| `id_format` | mapping | Identifier shape for instances of this type. See [Instance ID format](#instance-id-format-id_format) below. |
| `reuse_policy` | string | Human-readable rule explaining whether instances are write-once, updated in place, superseded, or replaced. |
| `dependencies.requires` | list | Inputs needed before this artifact can be authored responsibly. These are planning dependencies, not necessarily runtime blockers. |
| `dependencies.enables` | list | Artifacts, decisions, or activity work this artifact unlocks. |
| `dependencies.relates_to` | list | Peer or adjacent artifacts that should be considered together. |
| `validation.required_sections` | list | Sections an instance should contain. |
| `validation.required_fields` | list | Structured fields or table columns an instance should contain. |
| `validation.quality_checks` | list | Human or automated checks that determine whether the artifact is useful enough to depend on. |
| `validation.pattern_checks` | list | Regex checks a consumer can run mechanically against instance content. |
| `validation.automated_checks` | list | Rule-based checks beyond regex, such as uniqueness constraints. |
| `variables` | list | Template variables expected when generating an instance. |
| `prompts.generation` | string | Prompt file used to generate the artifact, usually `prompt.md`. |
| `prompts.review` | string | Inline or referenced review guidance. |
| `prompts.update` | string | Inline or referenced update guidance. |
| `template.file` | string | Template filename relative to the artifact-type directory. Usually `template.md`. |
| `template.sections` | list or mapping | Named sections the template contains, optionally with section-specific guidance. |
| `example.file` | string | Single canonical example filename relative to the artifact-type directory. |
| `examples` | list | Example files for the artifact type. Examples are illustrative, not governing unless explicitly marked. |
| `workflow.creation_order` | number or string | Relative order inside an activity. Lower values generally come earlier. |
| `workflow.review_cycles` | number or string | Expected review depth before the artifact becomes dependable. |
| `workflow.approval_required` | boolean | Whether explicit approval is expected before downstream artifacts depend on this artifact. |
| `workflow.approvers` | list | Roles that should approve the artifact when approval is required. |
| `workflow.update_triggers` | list | Events that should cause the artifact to be revisited. |
| `relationships` | mapping | Traceability relationships such as `informed_by` and `informs` that are useful but do not fit `dependencies`. |
| `references` | list | External references, books, papers, or grounding resources for the artifact type. Each entry typically has `title`, `file`, and `relationship`. |
| `tags` | list | Search and classification labels for the artifact type. |
| `version` | string | Schema or template version for the artifact type metadata. |
| `last_updated` | string | Last meaningful update date for the artifact type metadata. Use ISO `YYYY-MM-DD` when possible. |

### Instance ID format (`id_format`)

Numbered artifact types declare an `id_format` mapping describing how
instance IDs are shaped:

| Field | Type | Meaning |
| --- | --- | --- |
| `prefix` | string | Uppercase identifier prefix, such as `ADR`, `FEAT`, `TP`. |
| `pattern` | string | Regular expression an instance ID must match, such as `ADR-[0-9]{3}`. |
| `example` | string | A concrete valid ID, such as `ADR-001`. |
| `description` | string | Human-readable rule covering numbering, reuse, and supersession. |

Singleton artifact types (one instance per project) may omit `id_format`
because their `ddx.id` is fixed (for example `helix.product-vision`).

### Voice profile (`voice`)

HELIX artifact types may declare the voice profile that authoring,
validation, refresh, and optional prose-review tools should apply. The
canonical profile registry lives at:

```text
workflows/voice.yml
```

If `voice` is omitted from a `meta.yml`, consumers must apply the registry's
`default_profile`, currently `artifact-signal`. This default is intentional:
HELIX artifacts are durable signal shared by humans and LLMs, not public
marketing copy and not runtime execution state.

Use a direct string when the whole artifact type uses one profile:

```yaml
voice: artifact-signal
```

Use a mapping when the artifact type has a primary profile and bounded
section-level overrides:

```yaml
voice:
  profile: artifact-signal
  overrides:
    press_release: public-site
    generated_context: machine-facts
```

Consumers must ignore unknown mapping keys and preserve them when rewriting
metadata. They must treat unknown profile references as validation failures
because an unknown profile changes authoring behavior.

The standard profiles are:

| Profile | Conciseness | Intended use |
| --- | ---: | --- |
| `machine-facts` | 1/10 | Extracted facts, context digests, generated indexes, and other machine-facing state. |
| `artifact-signal` | 2/10 | HELIX artifacts, templates, prompts, metadata, alignment reports, and validation reports. |
| `public-site` | 3/10 | Microsite pages, public demos, generated public introductions, and catalog summaries for novice readers. |

Sloptimizer and other prose tools may consume these profiles when installed,
but HELIX does not require them. The profile is methodology data; optional
tools are enforcement or rewrite engines.

### Dependency entries

Entries under `dependencies.requires` and `dependencies.enables` use a small
open shape:

| Field | Type | Meaning |
| --- | --- | --- |
| `input` | string | Name of an input required by this artifact. Used in `requires`. |
| `output` | string | Name of an output this artifact enables. Used in `enables`. |
| `type` | string | Kind of dependency, such as `artifact`, `external`, `decision`, `validation`, or `insight`. |
| `activity` | string | Activity slug or activity directory name when the dependency crosses activities. |
| `path` | string | Artifact-type id, conventional instance path fragment, or other project-relative locator. |
| `required` | boolean | Whether the dependency is required for normal use. |
| `relationship` | string | Human-readable explanation of why the dependency matters. |
| `note` | string | Additional implementation guidance. |

Consumers should treat missing `required` as `false` unless the dependency is
listed in a required context by a specific artifact type.

### Validation entries

`validation.quality_checks` entries should use this shape:

| Field | Type | Meaning |
| --- | --- | --- |
| `check` | string | Stable check identifier in snake_case. |
| `description` | string | Human-readable rule. |
| `severity` | string | `blocking`, `warning`, or `informational`. |

`validation.pattern_checks` entries are regex-based:

| Field | Type | Meaning |
| --- | --- | --- |
| `pattern` | string | Regular expression to search for. |
| `expected` | string or number | Expected match condition, such as `0`, `>=1`, or `>0`. |
| `message` | string | Failure message. |

`validation.automated_checks` entries are rule-based when regex is not enough:

| Field | Type | Meaning |
| --- | --- | --- |
| `check` | string | Named automated rule. |
| `type` | string | Rule type, such as `unique_constraint`. |
| `field` | string | Field the rule applies to. |
| `not_equals` | string | Disallowed placeholder or value. |

### Extension sections

Artifact types may add domain-specific top-level sections. Existing examples
include sections such as `registry_rules`, `risk_management`,
`feasibility_dimensions`, `decision_framework`, `spike_types`,
`success_criteria`, `quality_indicators`, `monitoring`, and `reporting`.

Extension sections are allowed when they document reusable semantics for that
artifact type. They should not redefine the common fields above. Consumers that
do not understand an extension section must preserve it when rewriting metadata
and ignore it when deciding schema validity.

## Instance frontmatter: the `ddx:` block

Markdown artifact instances may include YAML frontmatter. HELIX reserves the
`ddx:` key for portable artifact identity and graph metadata.

Minimal instance frontmatter:

```yaml
---
ddx:
  id: PRD
---
```

Instance with graph metadata:

```yaml
---
ddx:
  id: TD-014
  type: technical-design
  activity: design
  depends_on:
    - US-009
    - ADR-003
---
```

### Required field

| Field | Type | Meaning |
| --- | --- | --- |
| `ddx.id` | string | Stable artifact instance ID used for traceability and dependency references. |

### Recommended fields

| Field | Type | Meaning |
| --- | --- | --- |
| `ddx.type` | string | Artifact-type id from `artifact.id`, such as `prd`, `adr`, or `technical-design`. Recommended when `id` alone does not identify the type. |
| `ddx.activity` | string | Activity slug that owns this instance. Recommended for generated or moved artifacts. |
| `ddx.depends_on` | list of strings | Artifact instance IDs that must be considered before this artifact is complete or dependable. |
| `ddx.status` | string | Artifact lifecycle state, such as `draft`, `review`, `approved`, `deprecated`, or `superseded`. |
| `ddx.supersedes` | list of strings | Prior artifact IDs replaced by this artifact. |
| `ddx.superseded_by` | string | Artifact ID that replaces this artifact. |
| `ddx.owner` | string | Person, role, or team responsible for maintaining the artifact. |
| `ddx.updated` | string | Last meaningful update date in ISO `YYYY-MM-DD` format. |
| `ddx.tags` | list of strings | Instance-level labels for search and routing. |

### Optional extension fields

Consumers may define additional fields under `ddx:` when they are portable and
safe to ignore. Current catalog examples include `parking_lot: true`, which
marks a deferred-work artifact as a parking lot. Runtime-specific operational
state should not be stored in artifact frontmatter unless another runtime can
ignore it without changing artifact meaning.

Do not put queue claims, assignees, process IDs, local branch names, or
runtime-only execution state in `ddx:`. Those belong to the runtime's tracker or
workspace state.

## `depends_on` graph semantics

`ddx.depends_on` defines a directed artifact graph. An edge from artifact `A` to
artifact `B` means `A` depends on `B`:

```text
A --depends_on--> B
```

Consumers should interpret this graph as follows:

| Rule | Semantics |
| --- | --- |
| Identity | Each dependency value references another artifact's `ddx.id`, not a file path. |
| Direction | Dependencies point upstream toward the artifact being relied on. |
| Blocking | A dependency is blocking for artifact completion when the downstream artifact cannot be responsibly approved without the upstream artifact. |
| Traceability | A dependency also creates traceability even when no automation blocks on it. |
| Activity order | Dependencies usually point to the same or earlier HELIX activity. Later-activity dependencies are allowed only for explicit feedback loops, reviews, reports, or supersession. |
| DAG preference | The graph should be acyclic for normal activity progression. Cycles indicate either an iterative review loop that should be modeled explicitly or an artifact split that needs refinement. |
| Missing IDs | A missing dependency target is a warning while drafting and blocking before publishing or depending on the artifact. |
| External inputs | External systems, services, people, and research inputs should appear in artifact content or `meta.yml` dependencies, not in `ddx.depends_on`, unless they have their own HELIX artifact instance ID. |

## ID naming conventions

Artifact IDs should be stable, short enough to cite, and specific enough to
avoid collisions within a project.

| Pattern | Use |
| --- | --- |
| `helix.<slug>` | Project-level singleton artifacts where a namespace avoids collisions, such as `helix.prd` or `helix.architecture`. |
| `<TYPE>-XXX` | Numbered artifacts with many instances, such as `FEAT-001`, `US-014`, `ADR-003`, `SD-002`, `TD-009`, `STP-004`, or `RISK-001`. |
| `<slug>` | Generic singleton artifacts where the project context is clear, such as `contract` or `metrics-dashboard`. |
| `<TYPE>-<slug>` | Named instances where numbers are not useful, such as `SPIKE-cache-policy` or `METRIC-build-time`. |

Rules:

1. Do not reuse an ID after an artifact has been published, superseded, or
   retired.
2. Prefer uppercase prefixes for established document families: `FEAT`, `US`,
   `ADR`, `SD`, `TD`, `TP`, `POC`, `RISK`, and `SPIKE`.
3. Use zero-padded numbers when the family is sequential.
4. Use lowercase kebab-case for artifact-type IDs and file slugs.
5. Keep `ddx.id` stable even if the file is moved or renamed.
6. Use `ddx.supersedes` and `ddx.superseded_by` rather than changing historical
   IDs to force alignment.

## Directory layout conventions

The installed catalog path varies by runtime; see `docs/install/` for
runtime-specific paths. For DDx-managed runtimes the catalog lives under
`workflows/`; other runtimes use their own conventions.
Project instances conventionally live under `docs/helix/`.

Catalog layout (example — DDx runtime):

```text
<runtime-catalog-root>/activities/
  00-discover/artifacts/<artifact-type>/
    meta.yml
    prompt.md
    template.md
    example.md
  01-frame/artifacts/<artifact-type>/
  02-design/artifacts/<artifact-type>/
  03-test/artifacts/<artifact-type>/
  04-build/artifacts/<artifact-type>/
  05-deploy/artifacts/<artifact-type>/
  06-iterate/artifacts/<artifact-type>/
```

Instance layout:

```text
docs/helix/
  00-discover/
  01-frame/
  02-design/
  03-test/
  04-build/
  05-deploy/
  06-iterate/
```

Conventions:

1. Activity directory numbers define reading order and publication order.
2. Activity slugs define semantic ownership.
3. Singleton artifacts usually live directly in the activity directory.
4. Multi-instance artifact families may live in plural subdirectories, such as
   `features/`, `adrs/`, `solution-designs/`, or `technical-designs/`.
5. Generated projections, such as a website or reference export, must preserve
   enough source path and ID information for readers to trace back to the
   canonical artifact.
6. Runtime state directories, such as tracker files or worker logs, are not part
   of the artifact schema.

## Activity progression conventions

HELIX activities form a directional artifact progression:

| Activity | Purpose | Typical artifact dependency direction |
| --- | --- | --- |
| `00-discover` | Establish opportunity, vision, business context, and constraints. | Root inputs. |
| `01-frame` | Convert opportunity into product scope, requirements, features, stories, risks, and policy. | Depends on discover artifacts. |
| `02-design` | Decide architecture, solution shape, contracts, and implementation approach. | Depends on frame artifacts. |
| `03-test` | Define verification strategy and concrete test expectations. | Depends on frame and design artifacts. |
| `04-build` | Plan and execute implementation slices. | Depends on test, design, and frame artifacts. |
| `05-deploy` | Prepare release, operations, rollout, and support. | Depends on build and design artifacts. |
| `06-iterate` | Measure outcomes and feed changes back into discovery, framing, design, or build. | May depend on any prior activity and may create follow-up work. |

Progression is not a waterfall rule. Feedback is expected. When a later activity
changes an earlier assumption, update or supersede the earlier artifact and let
the dependency graph show the new source of truth.

## Consumer responsibilities

Consumers should be conservative readers and careful writers:

1. Read required common fields.
2. Preserve unknown fields.
3. Treat missing required common fields as schema errors.
4. Treat missing recommended fields as quality warnings unless a specific
   workflow makes them blocking.
5. Resolve `ddx.depends_on` by artifact ID first, then by configured project
   indexes or source path hints.
6. Never make runtime-specific behavior the only way to interpret an artifact.

## Consumer table

| Consumer | Role | Reads | Writes | Authority boundary |
| --- | --- | --- | --- | --- |
| Manual operation | Human or agent reads catalog files and maintains artifacts directly. | `meta.yml`, `template.md`, `prompt.md`, `ddx.id`, `ddx.depends_on`, source paths. | Artifact content and optional frontmatter. | Can use the schema without DDx. Human judgment decides workflow state. |
| DDx reference consumer | Current reference runtime for tracking, artifact loading, and queue execution in HELIX development. | Artifact-type metadata, `ddx:` frontmatter, IDs, dependencies, labels, and project paths. | Tracker state, generated artifacts, and runtime-specific records outside the artifact schema. | DDx validates and consumes the schema but does not own it. HELIX owns this specification. |
| Hugo microsite projection | Documentation projection for readers. | Catalog metadata, examples, instance paths, titles, descriptions, and activity layout. | Generated website content. | Must present projected docs as a view of canonical artifacts, not as the source of truth. |
| Claude Code plugin / skill packaging | Runtime integration for invoking HELIX skills and shared resources. | Prompts, templates, workflow docs, and portable artifact schema. | Skill/package metadata and generated artifacts when directed by the user. | Should not require DDx-specific tracker state to understand artifacts. |
| Future runtime integrations | Databricks Genie, other agent runtimes, CI jobs, or custom tools. | Required common fields, `ddx:` frontmatter, dependency graph, activity layout. | Runtime-specific state in their own stores; artifacts only through the open schema. | Must treat DDx as a reference implementation, not as the schema authority. |

## Compatibility rules

1. Adding optional or recommended fields is backwards-compatible.
2. Removing required fields is a breaking schema change.
3. Renaming `ddx:` is a breaking schema change and should not be done lightly.
4. New consumers should support at least `ddx.id` and `ddx.depends_on` before
   claiming HELIX artifact compatibility.
5. Existing artifacts that lack frontmatter may still be valid prose artifacts,
   but they are not fully graph-addressable until they have a `ddx.id`.
6. The artifact catalog may be richer than a given consumer. Partial consumers
   should declare which fields they read.
