---
ddx:
  id: helix.design-family-marker-linkages
  review:
    self_hash: 3d8827c818c248f746908e51f24d6c0f6df1b568e5a91d9d39cd76e63a4e4267
    deps: {}
    reviewed_at: "2026-06-14T02:36:35Z"
---

# HELIX Family: Marker File + Type/Flow/Instance Linkage Relaxation

Status: design (Phase 3 of 6 of the marker+linkage workflow)
Date: 2026-06-04
Supersedes (in part): design-2026-06-03-helix-library-split.md §7.5 (heuristic
co-activation), §6.1 (type-level relationships), §6.1.1 (edge kinds — extended,
not replaced).
Coupled docs: plan-2026-06-03-helix-library-FINAL.md, implementation-plan-2026-06-04-helix-library-family.md, test-plan-2026-06-04-helix-library-family.md.

---

> **Supersession note (2026-06-14):** This is a historical design document.
> The marker schema (`flows:`, `helix_version:`, `cross_flow_edges:`) and the
> three-layer instance linkage model remain canonical. The following claims are
> retracted or superseded:
>
> - **Sibling flow architecture** — `helix-infra`, `helix-web`, `helix-data`
>   references throughout this doc are *historical illustrations only*; they are
>   not shipping public HELIX flows. The current architecture is a single `helix`
>   flow. See `docs/helix/architecture.md` for the current shape.
> - **HELIX-public env-var routing** — `HELIX_FLOW` / `HELIX_METHODOLOGY` are
>   runtime-owned dispatch flags, not HELIX public product surface.
> - **HELIX-public CLI interpretations** — `/<flow-id>` prefix routing,
>   `--flow` / `--methodology` flags are runtime-owned; not a HELIX skill
>   public interface.
> - **Validator and schema references** — `library/schemas/*.schema.json` and
>   `library/scripts/helix_check.py` are aspirational design; these files do
>   not ship in the current codebase.

---

## §0 Architecture amendment (relative to design-2026-06-03-helix-library-split.md)

### §0.1 Terminology

This document uses the v2 family terminology: a HELIX flow is what was called a methodology in v1. The marker key `flows:` is canonical; `methodologies:` is accepted via the M020 deprecation alias for one cycle. CLI flag `--flow` is canonical; `--methodology` is a one-cycle alias. Env var `HELIX_FLOW` supersedes `HELIX_METHODOLOGY` (still accepted). See plan-2026-06-05-conversation-bench-and-autonomy.md §11 for the full rename mapping. _[Runtime-owned: `HELIX_FLOW`, `HELIX_METHODOLOGY`, `--flow`, and `--methodology` are DDx/runtime dispatch mechanisms — not HELIX public product surface; see supersession note above.]_

Two architectural changes land on top of the library/flow split:

1. **Activation moves from heuristics to explicit declaration via a marker
   file `.helix.yml` at the repo root.** Today's detection signals
   (`workflows/methodology.yml` path, file globs, prompt patterns, the
   §7.5 precedence ladder with alphabetical tie-break) are FROZEN at
   today's behaviour and demoted to a fallback path that fires only when
   `.helix.yml` is absent. With a marker present, activation is
   deterministic and per-repo.

2. **Inter-artifact linkages are split three ways.** Today, `meta.yml`
   carries `relationships: {depends_on, informs, referenced_by}` at the
   TYPE level, mixing flow-graph information with portable
   artifact shape. Under the relaxation:

   - **Library `meta.yml`** carries SHAPE ONLY (`required_sections`,
     `prompts`, `template`, `quality_checks`, `section_aliases`). No
     `relationships:`, no `can_link_to:`, no edge information of any
     kind. The Phase 1 inventory confirms this is already the de-facto
     pattern (most types have empty `relationships:`; helix-infra types (historical illustration)
     declare none at all).
   - **Flow `graph.yml`** declares which TYPE-PAIR edges are
     allowed in this flow, with edge kind and per-pair
     cardinality / strength. The flow's outbound
     cross-flow edges live in a sibling `external_edges:` /
     `cross_flow:` block in the same file.
   - **Instance frontmatter** (under `ddx.links:`) declares the specific
     edges THIS instance has, referencing siblings by stable id (never
     file path). The validator resolves edges against the active
     flow graph(s), which are named by the marker.

The two changes are coupled: the marker file is the input that tells the
validator (and the skill) WHICH flow graphs to load and validate
instance edges against. Cross-flow edges (e.g. a product PRD that
informs an infra change-intent) work ONLY when both flows appear
in the active marker and the source flow has authorized the edge
in its `external_edges:` block.

Everything from design-2026-06-03 §0–§5 (monorepo topology, library
contents, `meta.yml` shape, flow skeleton, library type
versioning) stays. §6 (graph) is extended (additional edge kinds,
`external_edges:`). §7.5 (co-activation precedence) is partly
superseded: rules 1, 2, 5 survive as fallback; rules 3, 4 are subsumed
by the marker. §8 conflicts already resolved stay resolved.

---

## §1 Marker file

### 1.1 Location and discovery

`.helix.yml` at the repository root — the directory containing `.git/`,
or the cwd if no git root is found. Single file, no nested overrides in
v1. The dotfile-at-root convention matches `.editorconfig`, `.gitignore`,
`.prettierrc`. The name `helix` is the FAMILY name (marketplace), not a
flow id; the same file declares which flow flavors apply.

`.claude-plugin/methodologies.yml` was considered and rejected: it
couples the file to one agent harness. TOML was considered and rejected:
the rest of the family (graph.yml, meta.yml, methodology.yml) is YAML.

**Discovery walk + stray-marker rule.** The validator walks upward from
cwd to the git root searching for `.helix.yml`. The FIRST one found is
the active marker. After resolution the validator scans the whole tree
under the git root for additional `.helix.yml` files; every stray
marker (any `.helix.yml` other than the active one) emits warning
**M010** ("nested .helix.yml found; v1 ignores nested markers, parent:
semantics reserved for v2"). v1 ignores them; v2 may flip M010 to error
or use the reserved `parent:` field to implement nested overrides.

A separate `helix_check.py marker --discover` mode runs ONLY the tree
scan (no activation) for one-shot linting: it prints every `.helix.yml`
under cwd with its relative path and an exit code of 0 if exactly one
marker is found, otherwise non-zero. CI invokes `--discover` to catch
stray markers that the activation walk would warn about silently.

### 1.2 Schema

One required top-level key `flows:` (list). Optional top-level
keys `helix_version:`, `defaults:`, `cross_flow_edges:`. Optional
per-entry keys `version:`, `concerns:`.

```yaml
# .helix.yml — schema (informal; JSON Schema at library/schemas/marker.schema.json)
helix_version: 1                       # marker schema version (REQUIRED in v1)

flows:                         # REQUIRED; list of {id, root, ...}
  - id: <plugin-id>                    # must match methodology.yml `id:`
    root: <repo-relative-path>         # where instances live; must stay inside repo
    version: "<semver>"                # OPTIONAL; advisory pin
    concerns:                          # OPTIONAL; couples with concerns slot model
      enabled:  [<concern-slug>, ...]
      disabled: [<concern-slug>, ...]

defaults:                              # OPTIONAL; resolves generic prompts
  flow: <id>                    # must be one of the listed flows

cross_flow_edges:               # OPTIONAL; per-repo allowlist
  allow:
    - from: <src-flow>:<src-type>
      to:   <dst-flow>:<dst-type>
      kind: <edge-kind>
```

### 1.3 Fallback when marker is absent

A missing `.helix.yml` does NOT block activation. The skill falls
through to the frozen-today heuristics (the §7.5 detection block in the
prior design) and emits ONE banner on first activation per session:

```
No .helix.yml found. Activating <id> by heuristic (path: workflows/methodology.yml).
Run /helix init-marker to make this explicit.
```

Heuristic activation is FROZEN — no new detection signals get added; the
marker is the growth path. Refusing to activate would punish every
existing HELIX install. Silently activating the first flow found
hides drift. The banner is the explicit middle path.

### 1.4 Hard-fail rules (no partial activation on malformed marker)

A marker that exists must be valid or activation stops. Asymmetry is
intentional: the marker exists precisely to eliminate silent
misroutes; soft-failing it would reintroduce the failure mode it
prevents.

- **YAML parse error** → hard stop (M001), print file + line + parse message.
- **`root:` escapes the repo root** → hard stop (M002).
- **Duplicate `id:` in `flows:`** → hard stop (M003).
- **`defaults.flow:` not in `flows:`** → hard stop (M004).
- **Unknown `id:` (no installed plugin matches)** → that entry is
  ignored with diagnostic M005; OTHER entries proceed. Rationale: a
  missing plugin is recoverable (`install the plugin`) and shouldn't
  black-hole the entire repo.
- **`root:` path resolves to a directory that does not exist on disk
  (or exists but is not a directory)** → hard stop M006, naming the
  offending entry and the unresolved path. The marker is supposed to
  eliminate typos in scope declarations; silently treating a missing
  scope as "zero instances" reintroduces the false-green failure mode.
  Escape hatch: `--allow-empty-scope` demotes M006 to a warning so a
  fresh repo can declare `root: docs/helix/` before any instances
  exist. CI runs without that flag and catches dead scopes.

### 1.5 Resolution of "which flow is active right now"

When the marker lists 2+ flows, the skill chooses one per
invocation:

1. Explicit `/<flow-id> <verb>` prefix wins.
2. `HELIX_FLOW=<id>` env var wins. _(runtime-owned — see supersession note)_
3. cwd under one flow's `root:` wins.
4. `defaults.flow:` in the marker wins.
5. If exactly one flow is listed, it wins.
6. Otherwise emit the disambiguation banner from the prior §7.5 (single
   line; deterministic tie-break by listed order, NOT alphabetical —
   the marker IS the operator's intent).

### 1.6 Worked examples

**Product-only repo (common case).**

```yaml
helix_version: 1
flows:
  - id: helix
    root: docs/helix/
```

**Mixed monorepo (product + infra).** _[Historical illustration — `helix-infra` is not a shipping public flow; see supersession note above.]_

```yaml
helix_version: 1

flows:
  - id: helix
    root: docs/helix/
    version: "1.0.0"
    concerns:
      enabled:  [accessibility, verification, measurement]
      disabled: [sample-data]
  - id: helix-infra
    root: infra/terraform/
    version: "0.2.0"

defaults:
  flow: helix

cross_flow_edges:
  allow:
    - from: helix:prd
      to:   helix-infra:change-intent
      kind: informs
```

**Malformed (unknown flow id).** _[Historical illustration — `helix-infra` in the diagnostic below is not a shipping public flow; see supersession note above.]_

```yaml
helix_version: 1
flows:
  - id: helix
    root: docs/helix/
  - id: helix-mobile          # not installed
    root: docs/mobile/
```

Expected diagnostic (entry ignored, others proceed):

```
.helix.yml: unknown flow id 'helix-mobile' at line 5.
Installed flows: [helix, helix-infra]
This entry is ignored. Other entries (helix) will activate.
To install: see https://<family-marketplace>/plugins
```

**Malformed (root escapes repo) — hard stop.**

```
.helix.yml: root path '../../shared/helix/' for flow 'helix'
escapes the repo root (.git is at /repos/acme/). Refusing to activate.
Fix: use a repo-relative path that stays inside this repo.
```

---

## §2 Linkage relaxation (type / flow / instance cut)

### 2.1 Layer 1 — Library type `meta.yml`: SHAPE ONLY

Removing `relationships:` from library `meta.yml` is a structural rule
the type validator enforces. A library type is portable across
flows; encoding edges at the type level re-couples it to one
flow's vocabulary.

```yaml
# library/types/prd/meta.yml
id: prd
name: Product Requirements Document
summary: |
  Captures the WHAT and WHY of a product change. Flow-agnostic shape.

required_sections:
  - summary
  - problem
  - users
  - functional_requirements
  - non_functional_requirements
  - success_metrics
  - out_of_scope

section_aliases:
  functional_requirements: [functional-requirements, frs, fr]
  non_functional_requirements: [non-functional-requirements, nfrs, nfr]

quality_checks:
  - id: success_metrics_measurable
    description: Each success metric has a measurable target.
    severity: blocking

prompts:
  generation: prompt.md
  review:     review.md

template:
  file: template.md

tags: [framing, requirements]
version: 1.0.0
# INVARIANT: no `relationships:`, no `can_link_to:`, no edge information of any kind.
```

The type validator (§4) hard-fails on any `meta.yml` that carries a
`relationships:` key under exit code class 3 (T-class).

**Library type version semantics (semver).** The `version:` on a
library type is semver-tracked. The validator interprets shape changes:

- **Adding** a `required_sections` entry is a MAJOR bump.
- **Renaming** a section without an alias is a MAJOR bump.
- **Adding** an optional/aliased section, tightening a `quality_check`
  severity, adding a `section_aliases` entry are MINOR bumps.
- **Documentation / `summary` / `tags` / prompt prose** edits are PATCH bumps.

The library publish gate (T-mode validator) emits **T010** if a
shape-affecting change ships without bumping `version:` accordingly.

**Instance-shape resolution against version.** Type-shape checks
validate against the currently-resolved library version (the version
on disk now), NOT against the instance's advisory `library_type_version:`
pin. BUT the instance pin gates whether NEW constraints fire as ERROR
vs DEPRECATION-WARNING:

- If `library_type_version:` declared on the instance has the SAME
  major as the currently-resolved library version → constraints fire
  as errors (normal mode).
- If `library_type_version:` has a LOWER major than the currently-
  resolved version → NEWLY-introduced required sections fire as
  **I010 deprecation warning** for one major-version cycle, citing
  the prior-major pin and the major bump that introduced the new
  section. The hook does not block; CI in --strict mode upgrades
  I010 to error.
- If the instance has no `library_type_version:` field → treat as
  matching current major (no grace period). Authors who want grace
  must opt in by pinning.

This closes the verification-exit-gate failure mode where a library
update silently breaks pre-commit on every uncommitted ADR: a major
bump gives in-flight instances one cycle to migrate.

### 2.2 Layer 2 — Flow `graph.yml`: TYPE-PAIR allowed edges

The graph declares which type-pair edges are allowed and at what
strength. Edge kinds are CLOSED at five values:

| Kind          | Semantics                                                                                  | Acyclicity walk? |
| ------------- | ------------------------------------------------------------------------------------------ | ---------------- |
| `requires`    | Hard prerequisite. Target must exist before source is dispatchable.                        | Yes              |
| `informs`     | Forward soft edge; traceability only.                                                      | No               |
| `contains`    | Parent → child decomposition (PRD contains FR; FEAT contains user-story).                  | Yes              |
| `supersedes`  | Replacement edge. Type-pair declares "this type may supersede instances of that type."     | No (instance-only chain) |
| `may_surface` | Optional production from a node's working session.                                         | No               |

The inventory's `referenced_by` and `informed_by` are DROPPED at this
layer — they were inverse views of `informs` / `requires` and were the
source of the "PRD informs test-plan vs test-plan referenced_by PRD"
double-encoding bug Phase 1 caught. The validator computes inverse
views from forward edges on demand.

Extensibility: edge kinds outside the five are accepted as
`x-<vendor>-<kind>` (e.g. `x-team-blocks`) and the validator ignores
them. Renderers may surface them. Promoting an `x-` kind to a closed
kind costs a validator contract bump (§4).

**Cardinality and strength live on the type-pair edge in the
flow graph, not on the type and not in instance frontmatter.**
The graph row carries `required: true|false` (default `false`) and
optional `cardinality: one-to-one|one-to-many|many-to-many`. The same
type pair can appear in different activities with different strengths.

**Cross-flow edges are declared by the SOURCE flow only,
in an `external_edges:` block in the same `graph.yml`.** The target
flow does not declare anything. Rationale: a separate bridge
file adds a third linkage location and creates the "who owns the
bridge?" drift mode the inventory already shows for un-graphed
flows. A bilateral declaration doubles the maintenance surface
for the advisory `informs` cases that are the only cross-flow
edges anyone has asked for. If a future flow needs ENFORCED
cross-flow `requires`, that's a separate amendment.

**`external_edges[]` entries MUST NOT carry `required: true`.** The
graph validator hard-fails (**G104**) any external edge with
`required: true`. Rationale: enforced cross-flow prerequisites
are the deferred bilateral-mechanism case (§6.2); permitting
`required: true` on an external edge would let a downstream
flow silently invalidate every existing source-flow
instance the moment the edge gets added to the graph. With external
edges always advisory, adding a new external edge never invalidates
existing instances retroactively — only new instances feel the
optional `informs` traceability slot.

Additionally, **`external_edges[].kind:` MUST be `informs` or an
`x-`-namespaced kind** (G105). `requires` / `contains` /
`supersedes` are forbidden across flows in v1; they imply
enforcement or instance lifecycle the bilateral mechanism is needed
to safely express.

```yaml
# product/workflows/graph.yml — fragment
version: 1
flow:
  id: helix
  library_version: "^1.0.0"
  validator_contract: 1

activities:
  - { id: 00-discover, exit_gate: discover-validation }
  - { id: 01-frame,    exit_gate: prd-validation }
  - { id: 02-design,   exit_gate: design-validation }
  - { id: 03-test,     exit_gate: test-validation }
  - { id: 04-build,    exit_gate: build-validation }
  - { id: 06-iterate,  exit_gate: iteration-validation }

nodes:
  - id: product-vision
    type: library:product-vision
    activity: 00-discover
    cardinality: singleton
    role: anchor
  - id: prd
    type: library:prd
    activity: 01-frame
    cardinality: many
  - id: feature-specification
    type: library:feature-specification
    activity: 01-frame
    cardinality: many
  - id: user-story
    type: library:user-stories
    activity: 01-frame
    cardinality: many
  - id: adr
    type: library:adr
    activity: 02-design
    cardinality: many
    scope: cross-cutting
  - id: technical-design
    type: library:technical-design
    activity: 02-design
    cardinality: many
  - id: test-plan
    type: library:test-plan
    activity: 03-test
    cardinality: many
  - id: implementation-plan
    type: library:implementation-plan
    activity: 04-build
    cardinality: many

edges:
  - { from: product-vision,        to: prd,                   kind: informs,    required: true  }
  - { from: prd,                   to: feature-specification, kind: informs,    required: true  }
  - { from: prd,                   to: principles,            kind: informs,    required: false }
  - { from: feature-specification, to: user-story,            kind: contains,   required: true  }
  - { from: feature-specification, to: technical-design,      kind: informs,    required: false }
  - { from: prd,                   to: test-plan,             kind: informs,    required: true  }
  - { from: adr,                   to: technical-design,      kind: informs,    required: false }
  - { from: technical-design,      to: implementation-plan,   kind: informs,    required: true  }
  - { from: test-plan,             to: implementation-plan,   kind: informs,    required: true  }
  - { from: adr,                   to: adr,                   kind: supersedes, required: false }

allowed_cycles:
  - from_type: implementation-plan
    to_type:   prd
    kind:      informs
    rationale: |
      06-iterate learnings re-open 01-frame. Each pass is a new walk;
      superseding PRD instances carry `supersedes: [PRD-003]` in frontmatter.

external_edges:  # [historical illustration — helix-infra is not a shipping public flow; see supersession note]
  - to_flow: helix-infra        # historical illustration — not a shipping public flow
    from_type:      prd
    to_type:        change-intent
    kind:           informs
    cardinality:    one-to-many
    required:       false
    rationale: |
      A product PRD may request infrastructure work that lands as a
      change-intent in the active infra scope. The infra graph does
      not mirror this edge — informs is advisory-forward.
```

### 2.3 Layer 3 — Instance frontmatter: ACTUAL edges by id

Edges in instance frontmatter live under `ddx.links:` as a LIST (same
target may appear with different kinds). Targets are id strings
resolved against the active flows' instance indexes. Path-based
references are rejected — they bake repo layout into documents.

Existing `ddx.id` and `ddx.review` fields are untouched and
runtime-managed. The relaxation is ADDITIVE: a document without
`ddx.links:` validates with a WARNING for the first deprecation cycle
(traceability degraded, shape still enforced). A migration script (§5)
proposes `ddx.links:` entries from existing body prose (FEAT/ADR
"Related" cells, `depends_on` lists already in some frontmatter, paired-with
prose in helix-infra (historical illustration)).

```yaml
---
ddx:
  id: PRD-001
  type: prd                              # library type id
  flow: helix                     # flow that owns this instance
  library_type_version: 1.0.0            # advisory; pairs with marker version

  review:                                # runtime-managed; unchanged
    self_hash: 2b22383538b33c6ecee57f43d85128dfef7d56254766b757aa36439e35f2bfc9
    deps: {}
    reviewed_at: "2026-05-24T23:26:16Z"

  links:                                 # author-managed; new
    - { kind: informs,   to: FEAT-001 }
    - { kind: informs,   to: FEAT-002 }
    - { kind: contains,  to: FR-1, scope: intra-document }
    - { kind: supersedes, to: PRD-001@v0 }
    - { kind: informs,   to: "helix-infra:CI-2026-06-runtime-boundary",   # historical illustration
        cross_flow: true }
---
```

Field rules:

- `kind:` must be one of the five closed kinds OR an `x-` namespaced
  string (warning, not error).
- `to:` is an id. For local edges, an id resolvable in this
  flow's instance index. For cross-flow edges, a
  qualified id `<flow-id>:<instance-id>` and
  `cross_flow: true`.
- `scope: intra-document` marks containment edges to in-body anchors
  (FR-n, US-n-ACm); these are NOT resolved against the cross-document
  index. They exist in frontmatter so traceability tooling can render
  PRD→FR→US chains without reparsing prose.
- `supersedes:` targets MAY use the `@v<n>` suffix when the prior
  generation has been archived; instance check warns if the target
  isn't marked superseded.
- `status:` on an individual edge entry is one of `present` (default)
  or `planned`. `planned` is the typed escape hatch for forward
  references to unauthored docs: the iterative-design case where the
  PRD is authored before its FEATs exist. `status: planned` downgrades
  the unresolved-target error **I101** to warning **I103** (forward
  reference unresolved) outside of exit-gate checks. At exit-gate
  time for the source activity, a `status: planned` entry that STILL
  fails to resolve is upgraded back to error I101 — the planned slot
  is for in-flight work, not permanent escape. A `status: planned`
  entry that DOES resolve to an existing id is itself an error
  (**I104** "use status: present once the target exists") so authors
  don't leave the placeholder marker after the target is authored.
  The I101 diagnostic mentions both the nearest-id hint AND the
  `status: planned` option, so authors can distinguish typo vs. forward
  reference at the point of failure.

### 2.4 Resolution contract (binds all three layers)

The validator (§4) loads the marker, builds a per-flow
`instance_index: {ddx.id → file_path}` by walking each flow's
`root:`, then for each `ddx.links[]` entry:

1. Look up `(source_type, kind, target_type)` in the active
   flow's `edges:` (or `external_edges:` if
   `cross_flow: true`). If absent → error class I/G.
2. If the edge is in `external_edges:`, distinguish two unreachable
   modes:
   - **2a** target flow absent from the active marker but its
     plugin IS installed on disk → WARNING **I120** ("link to inactive
     flow; add `<id>:` to .helix.yml or remove the edge").
   - **2b** target flow plugin NOT installed on disk → WARNING
     **I121** ("link to uninstalled flow; install
     `<plugin-id>` or remove the edge"). Distinct diagnostics matter
     because the operator's next step differs.
   Both downgradable-by-default to error via
   `--cross-methodology-edges deny` or `--strict-cross-method`. At
   graph-load time the active flow's `external_edges:` are
   themselves walked; any entry whose target flow is absent
   from the marker emits **G140** once per graph load (not per
   instance edge that uses it), to surface graph drift even before
   any instance references it.
3. Resolve `to:` against the appropriate instance index. Unresolved →
   error I101 (unless `scope: intra-document` or
   `status: planned` — see §2.3).
4. Apply per-edge `required: true|false` against source-node
   cardinality — at-least-one-required edges generate errors only at
   activity-exit-gate time (a fresh PRD doesn't fail just for being new).
   `required: true` is NEVER honored on `external_edges:` (rejected at
   graph-load time by G104 in §2.2); cross-flow edges therefore
   never invalidate existing instances retroactively when added.

### 2.5 Frontmatter write contract

The skill MUST round-trip instance frontmatter through a
key-preserving emitter so that incidental edits never silently rewrite
shape. Specifically:

1. **Preserve unknown keys verbatim.** Use stdlib `yaml.safe_load`
   into an `OrderedDict` (or insertion-ordered dict, Python ≥ 3.7),
   then `yaml.safe_dump(..., sort_keys=False, allow_unicode=True)` so
   round-trip preserves key order. Unknown top-level keys
   (`depends_on:`, `relationships:`, vendor-namespaced `x-*:`) MUST
   survive the round-trip byte-equivalent (modulo trailing whitespace
   normalization).
2. **Legacy → new key translation is migration-script-only.** The
   skill never translates legacy `depends_on:` or `relationships:`
   into `ddx.links:` on incidental edits. Translation is performed
   ONLY by the explicit migration script in §5.4. Determinism rule:
   two `/helix` agent runs on the same legacy-frontmatter PRD must
   produce byte-equivalent frontmatter.
3. **Validator surfaces coexistence.** When both legacy and new keys
   are present on the same instance, the validator emits warning
   **W005** ("legacy + ddx.links coexist; run
   `library/scripts/migrate_relationships_to_links.py` to consolidate")
   pointing at the migrate command. The hook does not block on W005.
4. **No drop on rewrite.** A skill that strips a key it does not
   understand on rewrite is a contract violation tested by T32.

### 2.6 Drop list (what the relaxation removes)

- `relationships:` block from library `meta.yml` (Layer 1).
- `referenced_by:` / `informed_by:` from flow `graph.yml`
  (computed inverse views).
- Path-based markdown links as canonical edges (still allowed as prose
  references; no longer the traceability source of truth).
- Implicit precedence rules 3 and 4 from prior §7.5 (subsumed by
  marker + §1.5 resolution chain).

### 2.7 Edge Authority Asymmetry (Invariant 1)

The three layers do not merely partition shape from edges from instances —
they assign distinct **authorities** to each layer, and the skill is the
deliberator between them.

- **Layer 1 (library `meta.yml`)** declares the type's intrinsic shape.
  It has NO authority over edges. Whether two types may relate is decided
  one layer up.
- **Layer 2 (flow `graph.yml`)** declares what edges are
  *possible* — the type-pair-with-kind whitelist (cf. §2.2). An edge
  appearing in `graph.yml` is a **candidate**, not an obligation.
- **Layer 3 (instance frontmatter `ddx.links`)** declares what edges are
  *actual* for a specific document. Every instance edge is a deliberate
  authoring decision.

**The skill MUST NOT mechanically populate `ddx.links` from `graph.yml`
edges.** Auto-populating instance edges from type-pair candidates — at
any autonomy level, including `autonomous` and `aggressive` — is a
contract violation. The graph enumerates what *could* be linked; the
skill's job is to surface those candidates to the operator (or, when the
operator has clearly named both endpoints, to confirm the link is
intentional) and only then write the edge into `ddx.links`.

**Why this asymmetry holds.** A graph edge `prd informs feature-specification`
declares that *some* PRDs *may* inform *some* feature-specifications. It
does NOT declare that the PRD being authored right now informs FEAT-001,
FEAT-002, or any particular FEAT instance. That decision is content —
it belongs to the human author. The skill that infers "graph says
informs, so I'll wire ddx.links to every FEAT" turns a possibility
catalog into a mechanical join and erodes the traceability signal the
graph is supposed to certify.

**Autonomy does not relax this.** `autonomy=autonomous` excuses the skill
from confirming each *in-scope mechanical write* (e.g., creating the PRD
file under the marker's root). It does NOT excuse skipping the
deliberation that turns a graph candidate into an instance edge —
deliberation is the asymmetry. Under `autonomous`, the skill must still
surface candidate edges and ask before populating `ddx.links`. The
`stop_at` set therefore implicitly includes "writing an `ddx.links` entry
not previously named by the operator" at every autonomy level.

**How the bench enforces.** The conversation bench category
`edge-asymmetry` (plan §1.5b, rows EA-01..EA-04) supplies a workspace
with existing FEAT-001 and FEAT-002, a graph declaring
`prd informs feature-specification` (required:false), and the prompt
"Create a PRD". The runner asserts the agent surfaces FEAT-001 / FEAT-002
as candidate informs targets and asks before writing `ddx.links`. Rows
EA-01/EA-02 run under `autonomy=guided`; EA-03/EA-04 run under
`autonomy=autonomous`. PASS in both autonomy levels requires the same
deliberation prose. A failure mode where the skill writes
`ddx.links: [FEAT-001, FEAT-002]` silently — even when authoring the PRD
file is in-scope — fails the row and halts the bench (P4 halt
condition).

---

## §3 graph.yml format + worked example

### 3.1 On-disk format and validation contract

`graph.yml` is hand-authored YAML. A JSON Schema
`library/schemas/graph.schema.json` accompanies it at
`validator_contract: 1`. The validator parses YAML, validates against
the schema for structural shape, then runs the four semantic checks
JSON Schema cannot express:

1. **Type resolution** — every `nodes[].type` resolves: `library:<slug>`
   exists in the pinned library catalog; `local:<slug>` exists under
   `workflows/artifacts/<slug>/meta.yml`.
2. **Edge endpoint resolution** — every `edges[].from/to` references a
   declared node id; every `external_edges[].from_type` is a local
   node; every `external_edges[].to_type` is plausible against the
   target flow IF the target flow is loaded.
3. **Acyclicity over `requires` + `contains`** modulo `allowed_cycles`.
   **Self-loop rule (per S5 review item):** a type-pair edge with
   `from_type == to_type` on a kind in the acyclicity walk
   (`requires`, `contains`) is treated as a one-node cycle. It
   requires an explicit `allowed_cycles` entry for that
   (from_type, to_type, kind) triple; without one the validator
   emits **G103** ("same-type self-loop on walked kind requires
   allowed_cycles entry"). Self-loops on non-walked kinds
   (`informs`, `supersedes`, `may_surface`) pass without an
   `allowed_cycles` entry, but the schema-level check emits a single
   **G133** info-level note per graph listing them so they cannot
   accidentally proliferate.
4. **Exit-gate role** — every `activities[].exit_gate` references a
   node with `role: exit-gate`.

### 3.2 Edge-kind reconciliation with prior §6.1.1

The prior design declared three kinds: `requires`, `informs`,
`may_surface`. This design EXTENDS to five by adding `contains` (PRD →
FR-n; FEAT → user-story) and `supersedes` (ADR → prior ADR; PRD → prior
PRD). Rationale: the Phase 1 inventory found both shapes in the wild
already (containment by ID prefix, supersession in ADR status tables);
typed slots let instance frontmatter declare them rather than burying
them in prose.

### 3.3 Strength annotation

Per-edge `required: true|false` (default `false`) on the type-pair edge
declares whether instances of the source type MUST emit at least one
edge of this kind to the target type. The validator translates
`required: true` into an exit-gate-time check; it does NOT block
authoring of a fresh node. This separates "this flow demands
traceability" (graph) from "this PRD happens to inform two FEATs"
(instance).

`min_outgoing:` / `min_incoming:` on a node are sugar for combined
cardinality across multiple type pairs (e.g. "every FEAT must trace
upward to a PRD via informs" → `min_incoming: { informs: { prd: 1 } }`).
Either spelling is accepted; `required: true` on the edge is preferred
for single-pair constraints.

### 3.4 `allowed_cycles` — per type-pair-with-kind, with rationale

The HELIX 06-iterate → 01-frame loop is intentional. Cycle exemption
is declared at the flow level, with rationale, scoped to a
type-pair-and-kind triple:

```yaml
allowed_cycles:
  - from_type: implementation-plan
    to_type:   prd
    kind:      informs
    rationale: |
      Iteration learnings re-open framing. Each pass is a new walk
      modeled by superseding PRD instances.
```

Instance-level supersession chains (a runaway 17-deep chain) get a
runtime warning at instance-check time; they are not a graph violation.

### 3.5 Cross-flow block — `external_edges:`

ONE canonical location, ONE direction (source authorizes). See §2.2
example. The validator never reads the target flow's graph for
the cross edge; it only checks that the target flow is in the
active marker (otherwise warn) and that the target id resolves in the
target flow's instance index (otherwise warn).

This is intentional asymmetry. If `helix-infra` (historical illustration) is silent about being
informed by `helix:prd`, that's fine — `informs` is advisory. If a
future flow needs ENFORCED cross-flow prerequisites (hard
`requires`), it must propose a bilateral mechanism; this design does
NOT extend `external_edges:` to handle that case.

### 3.6 Full worked example

See §2.2 for the flow graph; see §2.3 for the matching instance
frontmatter; see §4.3 for the validator runs against both.

---

## §4 Validator semantics + CLI

### 4.1 One binary, four subcommands

`library/scripts/helix_check.py` — single py3-stdlib script, no
dependencies. Lives in the library (the monorepo decision: one
validator, one CI, no by-copy drift).

| Subcommand | Layer | Caller                              |
| ---------- | ----- | ----------------------------------- |
| `type`     | 1     | library CI                          |
| `graph`    | 2     | flow CI                      |
| `instance` | 3     | pre-commit hook, skill runtime, repo CI |
| `marker`   | 0     | consuming-repo CI (THE entrypoint)  |

The `marker` subcommand is the entrypoint a consuming repo runs: it
parses `.helix.yml`, dispatches `graph` against each declared
flow, and dispatches `instance` against every doc under each
scope's `root:`. The other subcommands are individually invocable for
library CI and flow CI to gate before publication.

### 4.2 CLI signatures

```text
# (1) Marker mode — consuming-repo entrypoint
helix_check.py marker <path-to-.helix.yml>
    [--strict]                        # warnings → errors
    [--json | --json-out PATH]
    [--no-instance]                   # marker+graphs only, skip walking scopes
    [--library-root PATH]             # override resolver chain (testing)

# (2) Graph mode — flow-repo CI
helix_check.py graph <flow-root>
    --types PATH [--types PATH ...]   # type catalog roots; repeatable
    [--schema PATH]                   # default: <library>/schemas/graph.schema.json
    [--strict] [--json | --json-out PATH]
    [--explain]                       # print resolved edge table

# (3) Instance mode — pre-commit hook + skill runtime
helix_check.py instance <doc-or-dir> [<doc-or-dir> ...]
    --marker <path-to-.helix.yml>     # required; selects active graphs
    [--scope <flow-id>]        # restrict to one active flow
    [--cross-methodology-edges allow|warn|deny]   # default: warn
    [--staged-only]                   # hook optimization
    [--strict] [--json | --json-out PATH]

# (4) Type mode — library-repo CI
helix_check.py type <types-root>
    [--self-test]                     # run packaged fixtures
    [--strict] [--json | --json-out PATH]
```

### 4.3 Exit-code classes

| Code | Class | Meaning                                                          |
| ---- | ----- | ---------------------------------------------------------------- |
| 0    | -     | clean                                                            |
| 1    | I     | instance-level violation (edge target missing, frontmatter bad)  |
| 2    | G     | graph-level violation (cycles, missing exit gate, bad type ref)  |
| 3    | T     | type-level violation (library meta.yml has `relationships:`, etc) |
| 4    | M     | marker-level violation (`.helix.yml` malformed)                  |
| 5    | R     | resolver / install error (library not found on disk)             |
| 64   | U     | usage error (bad flag)                                           |

W-class records (W003, W004, W005, R020 etc.) are warnings that do not
raise the exit code under default flags; under `--strict` they
upgrade to the matching error class (W003 → T003 contextually,
W004 → I050, etc.). The summary block always includes a `W:` count
so the JSON consumer can surface warnings even at exit 0.

Exit code reflects the HIGHEST violation class encountered. The run is
EXHAUSTIVE — every violation reachable from the input is collected and
emitted, not just the first. The deterministic-checks memory: one run
must surface everything; CI shouldn't need N rounds to drain a backlog.

### 4.4 Output format

- Human-readable to stderr by default (colorized when TTY).
- Structured JSON to stdout with `--json`, or to a file with
  `--json-out <path>`.
- Each violation is a record:
  `{code, layer, severity, instance_id, flow, location, message, hint}`
  with codes namespaced `T###` `G###` `I###` `M###` `R###`.

```json
{
  "run_id": "2026-06-04T10:42:11Z",
  "subcommand": "marker",
  "input": ".helix.yml",
  "exit_code": 1,
  "summary": {"T":0, "G":1, "I":2, "M":0, "R":0},
  "violations": [
    {"code":"I101","layer":"instance","severity":"error",
     "instance_id":"PRD-001",
     "location":"docs/helix/01-frame/PRD-001.md:frontmatter.ddx.links[0]",
     "message":"edge target FEAT-099 not found in instance corpus",
     "hint":"check the id; nearest matches: FEAT-009, FEAT-019"},
    {"code":"G201","layer":"graph","severity":"error",
     "flow":"helix",
     "location":"product/workflows/graph.yml:edges[7]",
     "message":"edge type 'informs' not allowed between 'prd' and 'adr' under active graph",
     "hint":"ADR is informed_BY prd; the edge belongs on the ADR side as informs from prd"}
  ]
}
```

### 4.5 Where validation runs

Instance validation runs at THREE points, all calling the same binary
with the same flags:

1. **Pre-commit hook** — installed by `just install-hooks` in any repo
   with `.helix.yml`. Operates on staged files plus their declared edge
   targets (catch rename-without-update). `--staged-only` is a speed
   override.
2. **Skill runtime** — every `/helix` mode that reads or writes an
   artifact calls `helix_check.py instance <path> --marker .helix.yml`
   on the artifact it's about to mutate AND on any instance it cites.
   Failures surface as setup-gap-style messages, not silent dispatch.
3. **Repo CI** — the backstop. Catches `--no-verify` hook bypass.

The hook is the fastest feedback; the agent check catches drift the
agent introduces; CI is the truth-on-merge gate. All three are the
same code path.

### 4.6 Three worked error messages

**(a) Type-shape error (T-class) — library CI catches a malformed promoted type:**

```
$ python3 scripts/helix_check.py type types/
ERROR T003  library/types/feature-specification/meta.yml
  relationships block is present on a library type (forbidden under
  linkage-relaxation; relationships belong in graph.yml, not meta.yml).
  fix: delete the `relationships:` key; encode the type-pair edges in
       the flow's graph.yml under nodes/edges.
  hint: see docs/helix/02-design/design-2026-06-04-helix-family-marker-and-linkages.md §2.1
exit 3
```

**(b) Graph error (G-class) — flow CI catches an illegal type-pair edge:**

```
$ python3 ../library/scripts/helix_check.py graph workflows/ \
      --types ../library/types --types workflows/artifacts
ERROR G201  product/workflows/graph.yml:42
  node `prd` declares informs -> `tech-spike`, but `tech-spike` is not
  a declared node in this flow.
  active flow: helix
  fix: either add a node `tech-spike` to graph.yml, or remove the edge.
  hint: did you mean `feature-specification`?

ERROR G104  product/workflows/graph.yml:17
  type `adr` resolves to library:adr, but graph declares overrides
  that re-require an already-required section (additive-only rule).
exit 2
```

**(c) Instance error (I-class) — pre-commit hook on a PR adding PRD-001:**

```
$ python3 .../helix_check.py instance docs/helix/01-frame/PRD-001.md \
      --marker .helix.yml
ERROR I101  docs/helix/01-frame/PRD-001.md:frontmatter.ddx.links[0]
  PRD-001 declares informs -> FEAT-099, but no instance with id FEAT-099
  was found under any declared scope.
  scopes searched: docs/helix/ (helix)
  nearest ids: FEAT-009, FEAT-019, FEAT-013
  fix: correct the id, or create the missing FEAT-099 first.

ERROR G201  docs/helix/01-frame/PRD-001.md:frontmatter.ddx.links[1]
  PRD-001 declares informs -> ADR-002, but the active flow graph
  (helix) forbids `informs` between `prd` and `adr`.
  allowed edges from prd: informs->feature-specification, informs->user-stories,
                          informs->principles, informs->test-plan
  fix: ADRs are informed_BY the prd; the edge belongs on ADR-002 as
       informs from prd, not on PRD-001.

WARN  I003  docs/helix/01-frame/PRD-001.md:frontmatter.ddx.links[2]
  edge to FEAT-013 has no `kind:` — defaulting to `informs` per graph.
  hint: explicit `kind:` recommended in strict mode.
exit 1
```

All three errors come from ONE run. No short-circuit.

### 4.7 Performance contract + instance index cache

The marker / instance walk re-reads every doc under each scope's
`root:` on each invocation. With three invocation points (hook,
skill, CI) and 5000+ instance corpora possible, the naive walk is the
ergonomic risk: a slow pre-commit gets `--no-verify`-d.

**Budget.** Marker-mode wall-clock budget on a 2024-class laptop
(stdlib py3, no native deps):

| Corpus size | Budget |
| ----------- | ------ |
| ≤ 100 docs  | 2s     |
| ≤ 1,000 docs | 5s    |
| ≤ 10,000 docs | 30s  |
| > 10,000     | emits R-class warning **R020** ("consider --cache; perf budget exceeded") |

When R020 fires the validator recommends `.helix/index.json` cache
mode but completes the run.

**Cache mode** (`--cache .helix/index.json`, or `--cache` shorthand
defaulting to that path):

- The validator persists `{doc_path, mtime_ns, ddx.id, edges_hash}`
  for every successfully-parsed instance.
- On subsequent runs the validator `stat()`s each doc; only docs
  whose mtime_ns > cache re-parse. Renames are detected by missing
  path + unchanged id; deletes by missing path + missing id.
- `.helix/index.json` is a derived artifact (`.gitignore`-d by the
  hook installer); corruption forces a full re-walk on next run, not
  a hard failure. Cache parity is asserted by a checksum over
  `sorted([(doc_path, ddx.id, edges_hash)])` that the validator emits
  with `--json`.
- The pre-commit hook defaults to cache mode; CI defaults to no-cache
  for fully-deterministic results.

**Incremental mode** (`--changed-only <git-ref>`): the validator
asks git for the diff against `<git-ref>` and limits the walk to
changed docs plus their declared edge targets (catch
rename-without-update). Designed for `pre-push` hooks against
upstream/main.

---

## §5 Couples with prior design (what changes, what stays)

### 5.1 Simplified

- **§7.5 co-activation precedence** is largely subsumed. Rules 3
  (single-signal-wins) and 4 (alphabetical tie-break) are deleted; the
  marker IS the operator's intent. Rules 1, 2, 5 survive as a fallback
  block when `.helix.yml` is absent.
- **Per-flow heuristic detection** (file globs, prompt
  patterns) is FROZEN. New flows do not add heuristics; they
  add marker support.
- **Validator drift mode** for instance-level checks is closed: the
  validator that interprets the marker is the same binary that
  validates types and graphs and instances; one upgrade surface.

### 5.2 Superseded

- **`relationships:` in `library/types/*/meta.yml`** is removed.
  Migration step in the family-readiness work strips it from all
  promoted types and validates absence.
- **`referenced_by:` and `informed_by:` keys** in any flow
  graph are dropped; the validator computes inverse views.
- **Prior §6.1.1 edge-kind table** (three kinds) is extended to five
  (adds `contains`, `supersedes`); the three original kinds keep their
  semantics.

### 5.3 Stays

- **Monorepo topology, library contents, library type versioning**
  (design-2026-06-03 §0–§4) unchanged.
- **Flow skeleton, activity manifests** (§5) unchanged.
- **Catalog resolution chain** (§7.3) unchanged; the validator's
  `--library-root` flag uses the same chain.
- **Cross-cutting nodes** (ADR, concerns, principles — §8.5)
  unchanged; they remain nodes in `graph.yml` with `scope:
  cross-cutting`.
- **`allowed_cycles:`** (§6.1.2) extended (per type-pair-with-kind),
  not replaced.
- **`ddx.id`, `ddx.review`** instance frontmatter fields unchanged and
  runtime-managed.

### 5.4 Migration

A one-shot script (`library/scripts/migrate_relationships_to_links.py`)
walks the current `helix` and `helix-infra` repos (historical — `helix-infra` is
not a shipping public flow; see supersession note) and:

1. Strips `relationships:` from every `library/types/*/meta.yml` and
   collects the removed edges.
2. Folds the collected edges into the appropriate flow's
   `graph.yml` `edges:` list with `required: false` (humans tighten
   later).
3. For each instance with body-prose ID citations (FEAT/ADR "Related"
   cells, helix-infra "Paired with" prose (historical illustration), frontmatter `depends_on`
   lists), proposes `ddx.links:` entries as a PR.
4. Adds a `.helix.yml` skeleton at the repo root.

The migration warns (not errors) on instances lacking `ddx.links:` for
the first cycle; the validator's instance-mode flag
`--require-links false` is the default during migration and flips to
true after the deprecation window.

**Transition phase matrix (resolves S7 review item).** The relaxation
ships in two named library versions with explicit validator-contract
behavior at each phase. `helix_version:` in the marker is the operator
opt-in to strict-from-day-one.

| Phase | Library version | Marker `helix_version:` | Library `meta.yml relationships:` | Instance lacks `ddx.links:` | `--require-links` default |
| ----- | --------------- | ----------------------- | --------------------------------- | --------------------------- | ------------------------- |
| A     | 1.0.0           | 1                       | T-warning (W003), not error       | W-warning (W004)            | false                     |
| A     | 1.0.0           | 2                       | T-error (T003)                    | I-error (I050)              | true                      |
| B     | 1.1.0 (~30 days after A) | 1              | T-error (T003)                    | W-warning (W004)            | false                     |
| B     | 1.1.0           | 2                       | T-error (T003)                    | I-error (I050)              | true                      |
| C     | 1.2.0 (≥60 days after A) | any            | T-error                           | I-error (I050)              | true                      |

Phase A ships the validator and migration script; the library
publishes type strips in a migration PR but does not break consumer
repos that still have legacy frontmatter. Phase B is the cutover for
the LIBRARY: in-tree types must be clean. Phase C is the cutover for
INSTANCES: every consumer must have run the migration or pinned
explicitly. Operators who want strict-mode from day one set
`helix_version: 2` in the marker; the validator then enforces Phase B
+ C behavior regardless of library version.

The migration script ships with a `--dry-run` mode (default) that
prints proposed edits without writing; CI in consumer repos uses
`--dry-run --require-clean` to fail the build if migration would
edit any file (signal that the migration PR has not landed yet).

---

## §6 Tradeoffs + open questions

### 6.1 Tradeoffs accepted

- **Marker hard-fails on malformed shape, soft-fails on unknown
  flow id.** Asymmetric on purpose: the marker exists to
  eliminate silent misroutes, so a parse error must be loud; a
  missing-plugin id is recoverable and shouldn't black-hole the repo.
- **Heuristic fallback keeps two activation paths.** Zero migration
  friction for existing installs; cost is the legacy heuristic path
  must be kept tested. The path is FROZEN — no growth — so the cost is
  bounded.
- **Cross-flow edges authorized only by source.** Asymmetric;
  the target may be surprised by inbound `informs`. Acceptable because
  `informs` is advisory-forward; if/when ENFORCED cross-flow
  edges are needed, a separate bilateral mechanism gets designed.
- **Edge kinds CLOSED at five.** New semantics require a validator
  contract bump. `x-vendor-kind` escape hatch keeps experimentation
  cheap.
- **Instance edges resolved by id, not file path.** Bakes a stable id
  scheme into HELIX. Existing instances already have stable
  `ddx.id` values; helix-infra instances (historical illustration; no frontmatter today) must
  acquire `ddx.id` as part of the migration.
- **`contains:` and `supersedes:` are graph-level edge kinds AND
  instance-level annotations.** Slightly redundant for cases where
  supersession is always intra-type, but symmetric with other edges and
  makes traceability rendering uniform.
- **Pre-commit hook is the executable-spec gate.** Determined `--no-verify`
  users bypass; mitigated by CI being the backstop.
- **Validator is one binary with four subcommands** (not four scripts):
  shared resolver, single exit-code contract, harder to drift. Cost:
  more surface in one file; py3-stdlib-only discipline must hold harder.
- **`referenced_by` / `informed_by` dropped from on-disk graphs.**
  Readers grep'ing those keys break; replaced by validator-computed
  inverse views in JSON output.

### 6.2 Open questions

- **Cross-flow `requires` (enforced, not advisory)** — the only
  cross-flow edges this design handles are `informs`. A real
  enforced prerequisite across flows (e.g. infra
  apply-evidence MUST precede a product release-notes) needs a
  bilateral mechanism; deferred to whichever flow first asks.
- **Skill-time strictness** — does instance-mode at skill-invocation
  BLOCK on warnings or only on errors? `--strict` is the safest reading
  of the verification-exit-gate memory but raises the floor for every
  existing doc with soft frontmatter. Lean: warn for the deprecation
  cycle, then flip to error.
- **Nested markers** — a polyglot monorepo where one subtree wants its
  own family declaration distinct from the parent. Deferred to v2; v1
  emits warning M010 for any stray nested marker (§1.1) so the case is
  visible. Schema reserves a `parent:` field for v2 override semantics.
- **Pre-commit scope** — staged-only vs staged-plus-edge-targets.
  Targets-too catches rename-without-update; staged-only is faster.
  Default: targets-too with `--staged-only` flag.
- **Instance corpus indexing** — RESOLVED in §4.7: walk by default,
  `.helix/index.json` cache opt-in via `--cache` (hook default),
  R020 warning when corpus exceeds the budget.
- **Structured fix suggestions** — should `hint:` be parseable
  `{action, from, to}` data the skill can auto-apply, or only prose?
  Lean prose; auto-apply risks the skill silently rewriting frontmatter
  incorrectly.
- **`intra-document` containment edges in frontmatter** — overlap with
  body anchors. May collapse to body-only in v2 if traceability tooling
  doesn't need them.
- **`supersedes:` as a flow-level edge kind vs instance-only**
  — currently both. Could collapse to instance-only if no flow
  needs to forbid supersession for a given type.
- **`helix_version:` field** — semver-tracked schema version for the
  marker; `validator_contract:` in graph.yml; `library_type_version:`
  in instances. Three version fields, three coupling questions. v1
  treats them as independent and additive; v2 may consolidate.
