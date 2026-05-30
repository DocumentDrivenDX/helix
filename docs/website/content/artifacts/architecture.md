---
title: "Architecture"
slug: architecture
weight: 300
activity: "Design"
source: "02-design/architecture.md"
generated: true
---

> **Source identity** (from `02-design/architecture.md`):

```yaml
ddx:
  id: helix.architecture
  depends_on:
    - helix.prd
    - CONTRACT-003
  review:
    self_hash: 49f65c706c77f174496e63379eb42676296da9527a504c90a81c204746968b0c
    deps:
      CONTRACT-003: 30e3e4320bc0643c904e92ee797d6ad8942a480edfae85a158c3a17054323a52
      helix.prd: 703d5ebaa378d037fd5ff6cbdf43e015ee014ca6a29b5df0b4c67ba9b117a510
    reviewed_at: "2026-05-15T04:11:24Z"
```

# Architecture

HELIX is a methodology and artifact catalog for AI-assisted software teams. It
ships portable content and a single routing skill. Architecturally it is three
things:

1. An **artifact catalog** in `workflows/` — templates, prompts, metadata, and
   examples for every artifact type across the seven HELIX activities.
2. A **routing skill** in `skills/helix/SKILL.md` — the single agent-facing
   surface that reads and writes the catalog's artifact instances.
3. A **methodology specification** in `workflows/` — the artifact
   authority hierarchy, activity
   conventions, artifact-type schema, principles, and the alignment skill
   contract, expressed in runtime-neutral terms.

HELIX does not provide a CLI, tracker, queue, or execution loop. Those are
runtime concerns. The boundary between HELIX portable content and any
specific runtime is defined in
[CONTRACT-003](/artifacts/contracts/contract-003-ddx-adapter-boundary/).

## Level 1: System Context

```mermaid
graph TB
    team["Software team<br/>(engineer, PM, tech lead)"]
    skill["HELIX routing skill<br/>skills/helix/SKILL.md"]
    catalog["Artifact catalog<br/>workflows/activities/…"]
    artifacts["Project artifact graph<br/>docs/&lt;project&gt;/helix/"]
    runtime["Runtime<br/>(DDx / Claude Code / Genie / …)"]

    team -->|"invokes skill via agent"| runtime
    runtime -->|"loads and runs"| skill
    skill -->|"reads artifact types from"| catalog
    skill -->|"reads/writes instances in"| artifacts
    runtime -->|"executes work derived from"| artifacts
```

| Element | Type | Purpose |
|---------|------|---------|
| Software team | Human | Authors governing artifacts; approves plans; steers alignment |
| HELIX routing skill | This system | Single skill entry point: routing, alignment, planning, review |
| Artifact catalog | This system | Canonical artifact type definitions — templates, prompts, metadata |
| Project artifact graph | Per-project | Instances of HELIX artifact types for a specific project |
| Runtime | External | Executes skill sessions; owns tracker, queue, evidence, packaging |

The team never invokes a HELIX command, because there is not one. They invoke
their agent runtime, and the runtime invokes the HELIX routing skill.

## Level 2: Container Diagram

```mermaid
graph TB
    subgraph helix["HELIX (this system)"]
        skill["skills/helix/SKILL.md<br/>Routing skill"]
        catalog["workflows/activities/…<br/>Artifact catalog<br/>templates · prompts · meta.yml"]
        schema["workflows/artifact-schema.md<br/>Instance schema"]
        wfdocs["workflows/<br/>Methodology spec<br/>principles · concerns · activities"]
    end

    subgraph project["Project (dogfood or adopter)"]
        instances["docs/helix/<br/>Artifact instances<br/>activity-numbered layout"]
    end

    subgraph runtime["Any compliant runtime"]
        engine["Execution engine<br/>tracker · queue · loop · evidence"]
        packages["Per-runtime packages<br/>DDx plugin · Claude Code skill · Genie skill"]
    end

    skill -->|"reads artifact types"| catalog
    skill -->|"reads/writes"| instances
    catalog -->|"instances conform to"| schema
    packages -->|"wraps same source"| skill
    packages -->|"wraps same source"| catalog
    engine -->|"loads skill into agent session"| skill
    engine -->|"installs per runtime contract"| packages
```

| Container | Technology | Responsibilities |
|-----------|------------|-----------------|
| `skills/helix/SKILL.md` | Markdown (skill frontmatter + body) | Single agent-facing surface; all routing modes; reads/writes artifact instances |
| `workflows/activities/` | Markdown + YAML | Artifact type definitions: template, prompt, meta.yml, example per type |
| `workflows/artifact-schema.md` | Markdown spec | Normative schema for `meta.yml` and `ddx:` instance frontmatter |
| `workflows/` (non-activity dirs) | Markdown | Methodology spec: principles, concerns, activity contracts, alignment guidance |
| `docs/helix/` | Markdown + YAML | Project artifact instances; authored from catalog templates |
| Per-runtime packages | Runtime-specific metadata | Thin wrappers that expose same source to DDx, Claude Code, Genie |
| Runtime execution engine | Runtime-specific | Tracker, queue, loop, evidence — outside HELIX boundary |

## Artifact Catalog

The artifact catalog is HELIX's primary structural element. It defines every
artifact type a HELIX-governed project may produce, organized by the seven
HELIX activities:

| Activity | Activity slug | Typical artifact types |
|----------|-----------|------------------------|
| Discover | `00-discover` | Product vision, opportunity brief, constraints |
| Frame | `01-frame` | PRD, feature specs, user stories, risks |
| Design | `02-design` | Architecture, ADRs, solution designs, technical designs, contracts |
| Test | `03-test` | Test plans, test strategies, acceptance criteria |
| Build | `04-build` | Implementation plans, execution documents |
| Deploy | `05-deploy` | Release plans, operations runbooks, rollout docs |
| Iterate | `06-iterate` | Alignment reviews, metrics, retrospectives |

Each artifact type in the catalog provides four files:

| File | Purpose |
|------|---------|
| `meta.yml` | Artifact-type metadata per the artifact schema |
| `template.md` | Markdown skeleton for new instances |
| `prompt.md` | Authoring guidance for agents or humans |
| `example.md` | Canonical illustrative instance |

The full `meta.yml` schema — required fields, recommended fields, validation
entries, id-format, dependency declarations, and extension sections — is
specified in [`workflows/artifact-schema.md`](https://github.com/DocumentDrivenDX/helix/blob/main/workflows/artifact-schema.md).

### Authority hierarchy

Every artifact type declares its position in the artifact authority
hierarchy. Higher-level artifacts govern lower-level ones; conflicts
resolve upward:

```
product vision
  └─ PRD
       └─ feature specs / user stories
            └─ architecture · ADRs
                 └─ solution designs · technical designs
                      └─ test plans
                           └─ implementation plans · code
```

The routing skill's `evolve` mode threads changes downward through this order;
`align` mode audits consistency across it. The authority hierarchy is a
HELIX invariant — no runtime changes it.

### Artifact instance frontmatter

Project artifact instances carry YAML frontmatter under the `ddx:` key. The
namespace is historical (DDx is the reference consumer); it does not mean
artifacts require DDx. Minimal instance frontmatter:

```yaml
---
ddx:
  id: FEAT-001
  type: feature-spec
  depends_on:
    - helix.prd
  status: draft
---
```

`ddx.id` is the only required field. `ddx.depends_on` builds the traceability
graph the routing skill traverses. Full field definitions are in
[`workflows/artifact-schema.md`](https://github.com/DocumentDrivenDX/helix/blob/main/workflows/artifact-schema.md).

## Routing Skill

`skills/helix/SKILL.md` is the single agent-facing surface. Any runtime that
loads the skill exposes the same capability set.

### What the skill reads and writes

| Reads | Writes |
|-------|--------|
| Artifact catalog (`workflows/activities/…`) — type definitions, templates, prompts | Project artifact instances (`docs/helix/…`) — new or updated content |
| Project artifact instances — current state of the dependency graph | Alignment reports, work-item descriptions, design documents |
| Methodology docs (`workflows/`) — principles, concerns, activity contracts | Follow-up work descriptions (runtime surfaces these as tracker items, GitHub issues, or markdown stubs) |

The skill never writes to a tracker, queue, or evidence store. Those are runtime
responsibilities.

### Routing modes

| Mode | Purpose |
|------|---------|
| `input` | Convert rough intent into governed work |
| `frame` | Create or refine vision, PRD, feature specs, user stories |
| `align` | Identify drift, gaps, and contradictions across the artifact graph |
| `validate` | Check one artifact instance against its type template and prompt |
| `evolve` | Thread a changed requirement through the authority hierarchy |
| `design` | Author a technical design before implementation |
| `backfill` | Reconstruct missing artifacts from evidence |
| `review` | Fresh-eyes review of plans, PRs, or recent work |
| `polish` | Refine work items for execution readiness |
| `check` / `next` | Decide the safe next action when intent is ambiguous |
| `build` / `run` | Bounded implementation pass or operator loop (delegates to runtime) |
| `commit` | Commit verified work with traceable message |
| `release` | Cut a HELIX content release |

### Skill composability

The routing skill reads the artifact catalog at runtime; it does not bundle
catalog content inside the skill body. This means:

- Any runtime that installs the HELIX package exposes the same routing modes.
- Catalog updates (new artifact types, revised templates) take effect without
  changing the skill body.
- The skill body contains zero runtime-specific commands (PRD R-4). Per-runtime
  packaging notes live in `docs/install/<runtime>.md`.

The skill's normative behavior is self-contained. Runtimes may surface
additional affordances (bead authoring, ddx work delegation, prose checking)
through their own packaging layers; those extensions live in per-runtime
packaging, not in the skill body.

## Artifact Schema as Runtime Contract

[`workflows/artifact-schema.md`](https://github.com/DocumentDrivenDX/helix/blob/main/workflows/artifact-schema.md)
is the contract that lets any compliant runtime register and consume HELIX
artifact types. A runtime claiming HELIX compatibility must:

1. Read `meta.yml` for artifact-type metadata.
2. Resolve `ddx.id` and `ddx.depends_on` in instance frontmatter for graph
   traversal.
3. Treat `workflows/artifact-schema.md` as the schema authority — not its own
   internal documentation.
4. Preserve unknown fields rather than stripping them.

The schema is intentionally open. Runtimes may add extension fields under `ddx:`
for operational state, but those fields must be ignorable by other runtimes
without changing artifact meaning.

Minimum runtime primitives required to run the alignment skill:

1. Read markdown files from the project filesystem.
2. Write markdown files to the project filesystem.
3. Search files by path or pattern.

Shell execution (item 4) is optional. A runtime satisfying only items 1–3 can
run every HELIX routing mode that does not involve direct code execution.

## Packaging

HELIX ships as three distribution packages around the same source content
(PRD R-7). The source in `workflows/` and `skills/helix/` is never forked.

| Package | Target runtime | Format | Install |
|---------|---------------|--------|---------|
| DDx plugin | DDx | DDx plugin manifest + catalog layout under `.ddx/plugins/helix/` | `ddx install helix` |
| Claude Code skill | Claude Code | Skill frontmatter + symlinked content under `.claude/skills/` | Copy or symlink |
| Databricks Genie skill | Databricks Genie | Genie skill descriptor + bundled catalog | Genie skill loader |

Per-runtime packaging notes — install paths, invocation details, DDx-specific
bead conventions, Genie-specific descriptor fields — live in `docs/install/`.
None of that detail appears in the routing skill body or the artifact catalog.

The adapter boundary between HELIX portable content and DDx-specific surfaces is
specified in [CONTRACT-003](/artifacts/contracts/contract-003-ddx-adapter-boundary/).
DDx is one reference runtime, not the architecture center.

## Documentation Projection

HELIX maintains two complementary documentation trees:

| Tree | Role |
|------|------|
| `workflows/` | Methodology specification — artifact-type schema, activity contracts, principles, concerns, alignment guidance. This is the normative content. |
| `docs/helix/` | Dogfood — HELIX's own governing artifacts, authored from HELIX templates. The dogfood is itself subject to alignment skill runs. |

`workflows/` is what adopters install; `docs/helix/` demonstrates the
methodology applied to HELIX's own development. The Hugo microsite (when
generated) is a read-only projection of both trees, not a source of truth.

Methodology invariants — principles, ratchets, activity contracts — are
maintained in `workflows/principles.md` and `workflows/ratchets.md`. Before
relying on either for design decisions, verify the current state in the file;
both are in active flux.

## DDx as One Reference Runtime

DDx is the reference runtime for HELIX's own development. HELIX uses DDx for
bead tracking, ddx work dispatch, and execution evidence on its own work
items. This is HELIX-using-DDx, not HELIX-coupled-to-DDx — the same
relationship any adopter has with their chosen runtime.

The DDx adapter boundary is defined in
[CONTRACT-003](/artifacts/contracts/contract-003-ddx-adapter-boundary/). In brief:

- HELIX provides to DDx: artifact catalog, routing skill, artifact-type schema.
- DDx provides to HELIX (as runtime): bead tracker, ddx work, evidence
  store, plugin packaging, prose checker.
- Neither side owns the other's internals.

CONTRACT-003 also catalogs known boundary leaks — places in the current
codebase where runtime-specific language has crept into HELIX portable content —
and describes the resolution for each.

## Quality Attributes

| Attribute | Strategy |
|-----------|---------|
| Runtime portability | Skill body and catalog contain zero runtime-specific commands; portability check on every release (PRD R-4) |
| Authority-hierarchy coherence | `align` mode audits consistency; `evolve` mode propagates change from the highest-authority artifact down |
| Catalog completeness | Seven-activity coverage; each type has template, prompt, meta, example |
| Self-application | `docs/helix/` is authored from HELIX templates; alignment skill runs catch dogfood drift (PRD R-6) |
| Schema openness | Consumers add extension fields; unknown fields are preserved, not stripped |
| Distribution breadth | Three packaging targets (DDx, Claude Code, Genie); source never forked (PRD R-7) |

## References

- [Product Vision](/artifacts/product-vision/)
- [PRD](/artifacts/prd/) — especially R-4 (runtime-neutral), R-5 (methodology spec), R-7 (packaging)
- [CONTRACT-003: DDx Adapter Boundary](/artifacts/contracts/contract-003-ddx-adapter-boundary/) — the boundary between HELIX and DDx
- [Artifact Schema](https://github.com/DocumentDrivenDX/helix/blob/main/workflows/artifact-schema.md) — normative schema for `meta.yml` and `ddx:` frontmatter
- [Routing Skill](https://github.com/DocumentDrivenDX/helix/blob/main/skills/helix/SKILL.md) — the single agent-facing surface
- [workflows/principles.md](https://github.com/DocumentDrivenDX/helix/blob/main/workflows/principles.md)
- [workflows/ratchets.md](https://github.com/DocumentDrivenDX/helix/blob/main/workflows/ratchets.md)
