# HELIX Family: Marker File + Type/Methodology/Instance Linkage Relaxation

Status: design (Phase 3 of 6 of the marker+linkage workflow)
Date: 2026-06-04
Supersedes (in part): design-2026-06-03-helix-library-split.md §7.5 (heuristic
co-activation), §6.1 (type-level relationships), §6.1.1 (edge kinds — extended,
not replaced).
Coupled docs: plan-2026-06-03-helix-library-FINAL.md, implementation-plan-2026-06-04-helix-library-family.md, test-plan-2026-06-04-helix-library-family.md.

---

## §0 Architecture amendment (relative to design-2026-06-03-helix-library-split.md)

Two architectural changes land on top of the library/methodology split:

1. **Activation moves from heuristics to explicit declaration via a marker
   file `.helix.yml` at the repo root.** Today's detection signals
   (`workflows/methodology.yml` path, file globs, prompt patterns, the
   §7.5 precedence ladder with alphabetical tie-break) are FROZEN at
   today's behaviour and demoted to a fallback path that fires only when
   `.helix.yml` is absent. With a marker present, activation is
   deterministic and per-repo.

2. **Inter-artifact linkages are split three ways.** Today, `meta.yml`
   carries `relationships: {depends_on, informs, referenced_by}` at the
   TYPE level, mixing methodology-graph information with portable
   artifact shape. Under the relaxation:

   - **Library `meta.yml`** carries SHAPE ONLY (`required_sections`,
     `prompts`, `template`, `quality_checks`, `section_aliases`). No
     `relationships:`, no `can_link_to:`, no edge information of any
     kind. The Phase 1 inventory confirms this is already the de-facto
     pattern (most types have empty `relationships:`; helix-infra types
     declare none at all).
   - **Methodology `graph.yml`** declares which TYPE-PAIR edges are
     allowed in this methodology, with edge kind and per-pair
     cardinality / strength. The methodology's outbound
     cross-methodology edges live in a sibling `external_edges:` /
     `cross_methodology:` block in the same file.
   - **Instance frontmatter** (under `ddx.links:`) declares the specific
     edges THIS instance has, referencing siblings by stable id (never
     file path). The validator resolves edges against the active
     methodology graph(s), which are named by the marker.

The two changes are coupled: the marker file is the input that tells the
validator (and the skill) WHICH methodology graphs to load and validate
instance edges against. Cross-methodology edges (e.g. a product PRD that
informs an infra change-intent) work ONLY when both methodologies appear
in the active marker and the source methodology has authorized the edge
in its `external_edges:` block.

Everything from design-2026-06-03 §0–§5 (monorepo topology, library
contents, `meta.yml` shape, methodology skeleton, library type
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
methodology id; the same file declares which methodology flavors apply.

`.claude-plugin/methodologies.yml` was considered and rejected: it
couples the file to one agent harness. TOML was considered and rejected:
the rest of the family (graph.yml, meta.yml, methodology.yml) is YAML.

### 1.2 Schema

One required top-level key `methodologies:` (list). Optional top-level
keys `helix_version:`, `defaults:`, `cross_methodology_edges:`. Optional
per-entry keys `version:`, `concerns:`.

```yaml
# .helix.yml — schema (informal; JSON Schema at library/schemas/marker.schema.json)
helix_version: 1                       # marker schema version (REQUIRED in v1)

methodologies:                         # REQUIRED; list of {id, root, ...}
  - id: <plugin-id>                    # must match methodology.yml `id:`
    root: <repo-relative-path>         # where instances live; must stay inside repo
    version: "<semver>"                # OPTIONAL; advisory pin
    concerns:                          # OPTIONAL; couples with concerns slot model
      enabled:  [<concern-slug>, ...]
      disabled: [<concern-slug>, ...]

defaults:                              # OPTIONAL; resolves generic prompts
  methodology: <id>                    # must be one of the listed methodologies

cross_methodology_edges:               # OPTIONAL; per-repo allowlist
  allow:
    - from: <src-methodology>:<src-type>
      to:   <dst-methodology>:<dst-type>
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
existing HELIX install. Silently activating the first methodology found
hides drift. The banner is the explicit middle path.

### 1.4 Hard-fail rules (no partial activation on malformed marker)

A marker that exists must be valid or activation stops. Asymmetry is
intentional: the marker exists precisely to eliminate silent
misroutes; soft-failing it would reintroduce the failure mode it
prevents.

- **YAML parse error** → hard stop, print file + line + parse message.
- **`root:` escapes the repo root** → hard stop.
- **Duplicate `id:` in `methodologies:`** → hard stop.
- **`defaults.methodology:` not in `methodologies:`** → hard stop.
- **Unknown `id:` (no installed plugin matches)** → that entry is
  ignored with a diagnostic; OTHER entries proceed. Rationale: a
  missing plugin is recoverable (`install the plugin`) and shouldn't
  black-hole the entire repo.

### 1.5 Resolution of "which methodology is active right now"

When the marker lists 2+ methodologies, the skill chooses one per
invocation:

1. Explicit `/<methodology-id> <verb>` prefix wins.
2. `HELIX_METHODOLOGY=<id>` env var wins.
3. cwd under one methodology's `root:` wins.
4. `defaults.methodology:` in the marker wins.
5. If exactly one methodology is listed, it wins.
6. Otherwise emit the disambiguation banner from the prior §7.5 (single
   line; deterministic tie-break by listed order, NOT alphabetical —
   the marker IS the operator's intent).

### 1.6 Worked examples

**Product-only repo (common case).**

```yaml
helix_version: 1
methodologies:
  - id: helix
    root: docs/helix/
```

**Mixed monorepo (product + infra).**

```yaml
helix_version: 1

methodologies:
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
  methodology: helix

cross_methodology_edges:
  allow:
    - from: helix:prd
      to:   helix-infra:change-intent
      kind: informs
```

**Malformed (unknown methodology id).**

```yaml
helix_version: 1
methodologies:
  - id: helix
    root: docs/helix/
  - id: helix-mobile          # not installed
    root: docs/mobile/
```

Expected diagnostic (entry ignored, others proceed):

```
.helix.yml: unknown methodology id 'helix-mobile' at line 5.
Installed methodologies: [helix, helix-infra]
This entry is ignored. Other entries (helix) will activate.
To install: see https://<family-marketplace>/plugins
```

**Malformed (root escapes repo) — hard stop.**

```
.helix.yml: root path '../../shared/helix/' for methodology 'helix'
escapes the repo root (.git is at /repos/acme/). Refusing to activate.
Fix: use a repo-relative path that stays inside this repo.
```

---

## §2 Linkage relaxation (type / methodology / instance cut)

### 2.1 Layer 1 — Library type `meta.yml`: SHAPE ONLY

Removing `relationships:` from library `meta.yml` is a structural rule
the type validator enforces. A library type is portable across
methodologies; encoding edges at the type level re-couples it to one
methodology's vocabulary.

```yaml
# library/types/prd/meta.yml
id: prd
name: Product Requirements Document
summary: |
  Captures the WHAT and WHY of a product change. Methodology-agnostic shape.

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

### 2.2 Layer 2 — Methodology `graph.yml`: TYPE-PAIR allowed edges

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
methodology graph, not on the type and not in instance frontmatter.**
The graph row carries `required: true|false` (default `false`) and
optional `cardinality: one-to-one|one-to-many|many-to-many`. The same
type pair can appear in different activities with different strengths.

**Cross-methodology edges are declared by the SOURCE methodology only,
in an `external_edges:` block in the same `graph.yml`.** The target
methodology does not declare anything. Rationale: a separate bridge
file adds a third linkage location and creates the "who owns the
bridge?" drift mode the inventory already shows for un-graphed
methodologies. A bilateral declaration doubles the maintenance surface
for the advisory `informs` cases that are the only cross-methodology
edges anyone has asked for. If a future methodology needs ENFORCED
cross-methodology `requires`, that's a separate amendment.

```yaml
# product/workflows/graph.yml — fragment
version: 1
methodology:
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

external_edges:
  - to_methodology: helix-infra
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
resolved against the active methodologies' instance indexes. Path-based
references are rejected — they bake repo layout into documents.

Existing `ddx.id` and `ddx.review` fields are untouched and
runtime-managed. The relaxation is ADDITIVE: a document without
`ddx.links:` validates with a WARNING for the first deprecation cycle
(traceability degraded, shape still enforced). A migration script (§5)
proposes `ddx.links:` entries from existing body prose (FEAT/ADR
"Related" cells, `depends_on` lists already in some frontmatter, paired-with
prose in helix-infra).

```yaml
---
ddx:
  id: PRD-001
  type: prd                              # library type id
  methodology: helix                     # methodology that owns this instance
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
    - { kind: informs,   to: "helix-infra:CI-2026-06-runtime-boundary",
        cross_methodology: true }
---
```

Field rules:

- `kind:` must be one of the five closed kinds OR an `x-` namespaced
  string (warning, not error).
- `to:` is an id. For local edges, an id resolvable in this
  methodology's instance index. For cross-methodology edges, a
  qualified id `<methodology-id>:<instance-id>` and
  `cross_methodology: true`.
- `scope: intra-document` marks containment edges to in-body anchors
  (FR-n, US-n-ACm); these are NOT resolved against the cross-document
  index. They exist in frontmatter so traceability tooling can render
  PRD→FR→US chains without reparsing prose.
- `supersedes:` targets MAY use the `@v<n>` suffix when the prior
  generation has been archived; instance check warns if the target
  isn't marked superseded.

### 2.4 Resolution contract (binds all three layers)

The validator (§4) loads the marker, builds a per-methodology
`instance_index: {ddx.id → file_path}` by walking each methodology's
`root:`, then for each `ddx.links[]` entry:

1. Look up `(source_type, kind, target_type)` in the active
   methodology's `edges:` (or `external_edges:` if
   `cross_methodology: true`). If absent → error class I/G.
2. If the edge is in `external_edges:` and the target methodology is
   NOT in the active marker → WARNING (target unreachable in this
   repo), unless `--strict-cross-method` upgrades to error.
3. Resolve `to:` against the appropriate instance index. Unresolved →
   error (unless `scope: intra-document`).
4. Apply per-edge `required: true|false` against source-node
   cardinality — at-least-one-required edges generate errors only at
   activity-exit-gate time (a fresh PRD doesn't fail just for being new).

### 2.5 Drop list (what the relaxation removes)

- `relationships:` block from library `meta.yml` (Layer 1).
- `referenced_by:` / `informed_by:` from methodology `graph.yml`
  (computed inverse views).
- Path-based markdown links as canonical edges (still allowed as prose
  references; no longer the traceability source of truth).
- Implicit precedence rules 3 and 4 from prior §7.5 (subsumed by
  marker + §1.5 resolution chain).

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
   target methodology IF the target methodology is loaded.
3. **Acyclicity over `requires` + `contains`** modulo `allowed_cycles`.
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
authoring of a fresh node. This separates "this methodology demands
traceability" (graph) from "this PRD happens to inform two FEATs"
(instance).

`min_outgoing:` / `min_incoming:` on a node are sugar for combined
cardinality across multiple type pairs (e.g. "every FEAT must trace
upward to a PRD via informs" → `min_incoming: { informs: { prd: 1 } }`).
Either spelling is accepted; `required: true` on the edge is preferred
for single-pair constraints.

### 3.4 `allowed_cycles` — per type-pair-with-kind, with rationale

The HELIX 06-iterate → 01-frame loop is intentional. Cycle exemption
is declared at the methodology level, with rationale, scoped to a
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

### 3.5 Cross-methodology block — `external_edges:`

ONE canonical location, ONE direction (source authorizes). See §2.2
example. The validator never reads the target methodology's graph for
the cross edge; it only checks that the target methodology is in the
active marker (otherwise warn) and that the target id resolves in the
target methodology's instance index (otherwise warn).

This is intentional asymmetry. If `helix-infra` is silent about being
informed by `helix:prd`, that's fine — `informs` is advisory. If a
future methodology needs ENFORCED cross-methodology prerequisites (hard
`requires`), it must propose a bilateral mechanism; this design does
NOT extend `external_edges:` to handle that case.

### 3.6 Full worked example

See §2.2 for the methodology graph; see §2.3 for the matching instance
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
| `graph`    | 2     | methodology CI                      |
| `instance` | 3     | pre-commit hook, skill runtime, repo CI |
| `marker`   | 0     | consuming-repo CI (THE entrypoint)  |

The `marker` subcommand is the entrypoint a consuming repo runs: it
parses `.helix.yml`, dispatches `graph` against each declared
methodology, and dispatches `instance` against every doc under each
scope's `root:`. The other subcommands are individually invocable for
library CI and methodology CI to gate before publication.

### 4.2 CLI signatures

```text
# (1) Marker mode — consuming-repo entrypoint
helix_check.py marker <path-to-.helix.yml>
    [--strict]                        # warnings → errors
    [--json | --json-out PATH]
    [--no-instance]                   # marker+graphs only, skip walking scopes
    [--library-root PATH]             # override resolver chain (testing)

# (2) Graph mode — methodology-repo CI
helix_check.py graph <methodology-root>
    --types PATH [--types PATH ...]   # type catalog roots; repeatable
    [--schema PATH]                   # default: <library>/schemas/graph.schema.json
    [--strict] [--json | --json-out PATH]
    [--explain]                       # print resolved edge table

# (3) Instance mode — pre-commit hook + skill runtime
helix_check.py instance <doc-or-dir> [<doc-or-dir> ...]
    --marker <path-to-.helix.yml>     # required; selects active graphs
    [--scope <methodology-id>]        # restrict to one active methodology
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

Exit code reflects the HIGHEST violation class encountered. The run is
EXHAUSTIVE — every violation reachable from the input is collected and
emitted, not just the first. The deterministic-checks memory: one run
must surface everything; CI shouldn't need N rounds to drain a backlog.

### 4.4 Output format

- Human-readable to stderr by default (colorized when TTY).
- Structured JSON to stdout with `--json`, or to a file with
  `--json-out <path>`.
- Each violation is a record:
  `{code, layer, severity, instance_id, methodology, location, message, hint}`
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
     "methodology":"helix",
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
       the methodology's graph.yml under nodes/edges.
  hint: see docs/helix/02-design/design-2026-06-04-helix-family-marker-and-linkages.md §2.1
exit 3
```

**(b) Graph error (G-class) — methodology CI catches an illegal type-pair edge:**

```
$ python3 ../library/scripts/helix_check.py graph workflows/ \
      --types ../library/types --types workflows/artifacts
ERROR G201  product/workflows/graph.yml:42
  node `prd` declares informs -> `tech-spike`, but `tech-spike` is not
  a declared node in this methodology.
  active methodology: helix
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
  PRD-001 declares informs -> ADR-002, but the active methodology graph
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

---

## §5 Couples with prior design (what changes, what stays)

### 5.1 Simplified

- **§7.5 co-activation precedence** is largely subsumed. Rules 3
  (single-signal-wins) and 4 (alphabetical tie-break) are deleted; the
  marker IS the operator's intent. Rules 1, 2, 5 survive as a fallback
  block when `.helix.yml` is absent.
- **Per-methodology heuristic detection** (file globs, prompt
  patterns) is FROZEN. New methodologies do not add heuristics; they
  add marker support.
- **Validator drift mode** for instance-level checks is closed: the
  validator that interprets the marker is the same binary that
  validates types and graphs and instances; one upgrade surface.

### 5.2 Superseded

- **`relationships:` in `library/types/*/meta.yml`** is removed.
  Migration step in the family-readiness work strips it from all
  promoted types and validates absence.
- **`referenced_by:` and `informed_by:` keys** in any methodology
  graph are dropped; the validator computes inverse views.
- **Prior §6.1.1 edge-kind table** (three kinds) is extended to five
  (adds `contains`, `supersedes`); the three original kinds keep their
  semantics.

### 5.3 Stays

- **Monorepo topology, library contents, library type versioning**
  (design-2026-06-03 §0–§4) unchanged.
- **Methodology skeleton, activity manifests** (§5) unchanged.
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
walks the current `helix` and `helix-infra` repos and:

1. Strips `relationships:` from every `library/types/*/meta.yml` and
   collects the removed edges.
2. Folds the collected edges into the appropriate methodology's
   `graph.yml` `edges:` list with `required: false` (humans tighten
   later).
3. For each instance with body-prose ID citations (FEAT/ADR "Related"
   cells, helix-infra "Paired with" prose, frontmatter `depends_on`
   lists), proposes `ddx.links:` entries as a PR.
4. Adds a `.helix.yml` skeleton at the repo root.

The migration warns (not errors) on instances lacking `ddx.links:` for
the first cycle; the validator's instance-mode flag
`--require-links false` is the default during migration and flips to
true after the deprecation window.

---

## §6 Tradeoffs + open questions

### 6.1 Tradeoffs accepted

- **Marker hard-fails on malformed shape, soft-fails on unknown
  methodology id.** Asymmetric on purpose: the marker exists to
  eliminate silent misroutes, so a parse error must be loud; a
  missing-plugin id is recoverable and shouldn't black-hole the repo.
- **Heuristic fallback keeps two activation paths.** Zero migration
  friction for existing installs; cost is the legacy heuristic path
  must be kept tested. The path is FROZEN — no growth — so the cost is
  bounded.
- **Cross-methodology edges authorized only by source.** Asymmetric;
  the target may be surprised by inbound `informs`. Acceptable because
  `informs` is advisory-forward; if/when ENFORCED cross-methodology
  edges are needed, a separate bilateral mechanism gets designed.
- **Edge kinds CLOSED at five.** New semantics require a validator
  contract bump. `x-vendor-kind` escape hatch keeps experimentation
  cheap.
- **Instance edges resolved by id, not file path.** Bakes a stable id
  scheme into HELIX. Existing instances already have stable
  `ddx.id` values; helix-infra instances (no frontmatter today) must
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

- **Cross-methodology `requires` (enforced, not advisory)** — the only
  cross-methodology edges this design handles are `informs`. A real
  enforced prerequisite across methodologies (e.g. infra
  apply-evidence MUST precede a product release-notes) needs a
  bilateral mechanism; deferred to whichever methodology first asks.
- **Skill-time strictness** — does instance-mode at skill-invocation
  BLOCK on warnings or only on errors? `--strict` is the safest reading
  of the verification-exit-gate memory but raises the floor for every
  existing doc with soft frontmatter. Lean: warn for the deprecation
  cycle, then flip to error.
- **Nested markers** — a polyglot monorepo where one subtree wants its
  own family declaration distinct from the parent. Deferred. Schema
  reserves a `parent:` field for the future override semantics.
- **Pre-commit scope** — staged-only vs staged-plus-edge-targets.
  Targets-too catches rename-without-update; staged-only is faster.
  Default: targets-too with `--staged-only` flag.
- **Instance corpus indexing** — walk-on-invoke vs cached
  `.helix/index.json`. Default: walk; revisit if measurably slow on
  100+ doc corpora.
- **Structured fix suggestions** — should `hint:` be parseable
  `{action, from, to}` data the skill can auto-apply, or only prose?
  Lean prose; auto-apply risks the skill silently rewriting frontmatter
  incorrectly.
- **`intra-document` containment edges in frontmatter** — overlap with
  body anchors. May collapse to body-only in v2 if traceability tooling
  doesn't need them.
- **`supersedes:` as a methodology-level edge kind vs instance-only**
  — currently both. Could collapse to instance-only if no methodology
  needs to forbid supersession for a given type.
- **`helix_version:` field** — semver-tracked schema version for the
  marker; `validator_contract:` in graph.yml; `library_type_version:`
  in instances. Three version fields, three coupling questions. v1
  treats them as independent and additive; v2 may consolidate.
