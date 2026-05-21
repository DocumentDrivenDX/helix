---
title: "CONTRACT-003: DDx Adapter Boundary"
slug: CONTRACT-003-ddx-adapter-boundary
weight: 260
activity: "Design"
source: "02-design/contracts/CONTRACT-003-ddx-adapter-boundary.md"
generated: true
collection: contracts
---

> **Source identity** (from `02-design/contracts/CONTRACT-003-ddx-adapter-boundary.md`):

```yaml
ddx:
  id: CONTRACT-003
  type: contract
  activity: design
  depends_on:
    - helix.prd
    - CONTRACT-001
    - CONTRACT-002
  status: draft
  review:
    self_hash: 30e3e4320bc0643c904e92ee797d6ad8942a480edfae85a158c3a17054323a52
    deps:
      CONTRACT-001: a3a48304a395b3d52c41f7b833e639f4a5ae986e62f58284821687306d3049fb
      CONTRACT-002: 473794ceba3db29b84547ece5a9c2d976471c67a8f2cba39750220edb188685a
      helix.prd: 703d5ebaa378d037fd5ff6cbdf43e015ee014ca6a29b5df0b4c67ba9b117a510
    reviewed_at: "2026-05-15T04:11:24Z"
```

# CONTRACT-003: DDx Adapter Boundary

**Status:** Draft
**Owner:** HELIX maintainers
**Related:** [PRD](../../01-frame/prd.md) (R-4, R-7),
[Minimal Runtime Contract](../../../docs/install/README.md#minimal-runtime-contract),
[CONTRACT-001](CONTRACT-001-ddx-helix-boundary.md),
[CONTRACT-002](CONTRACT-002-helix-execution-doc-conventions.md),
[Artifact Schema](../../../workflows/artifact-schema.md)

## Purpose

After the HELIX scope collapse (2026-Q2), HELIX is methodology + artifact
catalog + one routing skill. DDx is no longer HELIX's platform substrate; it is
one of three target runtimes — alongside Claude Code and Databricks Code Genie.

This contract redraws the boundary in that new shape:

> **DDx is a runtime that adapts HELIX content for its specific surfaces. HELIX
> portable behavior ends at the minimal runtime contract; DDx-specific behavior
> begins there.**

CONTRACT-001 captured the old shape, where HELIX was built on DDx and delegated
execution, tracking, and queue management to it. That remains a useful guide to
shared integration objects but reads the relationship in the wrong direction
after the collapse. CONTRACT-003 supersedes the directional framing of
CONTRACT-001; it does not invalidate the shared-object definitions or audit
findings therein.

## What HELIX Provides (DDx Consumes)

DDx consumes three portable content artifacts from HELIX:

### 1. Artifact catalog — `workflows/`

The canonical location is `workflows/` in the HELIX repo. When installed via
`ddx install helix`, the catalog lands under
`.ddx/plugins/helix/workflows/activities/<activity>/artifacts/<type>/`.

Each artifact type exposes:

| File | Purpose |
|---|---|
| `meta.yml` | Artifact-type metadata per `workflows/artifact-schema.md` |
| `template.md` | Markdown skeleton for new instances |
| `prompt.md` | Authoring guidance for agents or humans |
| `example.md` | Canonical illustrative instance |

DDx may index these files into its doc-graph and make them discoverable for
search, alignment, and bead-authoring assistance. It must not modify their
content during indexing or treat its own index as the schema authority.

### 2. Routing skill — `skills/helix/SKILL.md`

The single skill entry point. Its frontmatter shape is:

```yaml
---
name: helix
description: <routing hint text>
argument-hint: "[intent or scope]"
---
```

Three keys only; no DDx-specific fields. DDx discovers the skill via the
standard plugin skill loader and invokes it the same way Claude Code or Genie
would — by presenting the frontmatter and body to the active agent session.
DDx must not inject DDx-specific fields into the skill frontmatter or copy the
skill body into its own runtime store in a divergent form.

### 3. Artifact-type schema — `workflows/artifact-schema.md`

The normative schema for `meta.yml` and `ddx:` instance frontmatter. DDx is the
current reference consumer (the `ddx:` namespace is historical). DDx must treat
this document as the schema authority. If DDx extends the schema, it must file
changes here and not define a parallel schema in its own docs.

**What HELIX does NOT provide:** a tracker, a queue, an execution loop, a CLI,
bead IDs, execution evidence, metrics, or runtime state. Those are DDx concerns.

## What DDx Provides as Runtime

DDx provides the execution layer that HELIX's content runs inside. This does not
make DDx authoritative over HELIX content; it makes DDx responsible for the
following surfaces:

### 1. Bead tracker

DDx owns bead storage (`.ddx/beads.jsonl`), bead lifecycle (open → executing →
closed), and queue ordering (`ReadyExecution()`). HELIX content may describe
the shape of a well-formed bead, but HELIX does not store, claim, or close
beads. DDx does.

### 2. Execute-loop and dispatch

`ddx agent execute-loop` is DDx's queue-drain primitive. `ddx agent execute-bead`
is the single-bead primitive. HELIX routing skill may invoke `build` or `run`
modes that ultimately call these, but the invocation path goes through the
agent session, not through a HELIX-owned subprocess. DDx owns harness
selection, model routing, and session management.

### 3. Evidence and metrics

DDx writes execution evidence to `.ddx/exec/runs/`. HELIX content can author
execution documents (`EXEC-*.md`) that describe what DDx should validate;
DDx runs the validations and writes the results. HELIX does not write to the
evidence store.

### 4. File checkpoint and prose checker

`ddx checkpoint` and `ddx doc prose` are DDx-owned. HELIX content describes
when a checkpoint is appropriate and authors `validation.pattern_checks` in
`meta.yml` in a form DDx's prose checker can enforce; DDx executes both.
<!-- TODO: verify with DDx maintainers — auto-checkpoint before execute-bead
     tracked as ddx-91bc770a; per-artifact-type rule scoping in ddx doc prose
     tracked as PRD R-9 — confirm DDx bead exists for the latter -->

### 5. Plugin packaging

`ddx install helix` is DDx's plugin installer. It copies the HELIX catalog and
skill into `.ddx/plugins/helix/`. The DDx plugin manifest (format owned by DDx)
wraps the HELIX content. HELIX does not define the plugin manifest format;
DDx does.

## The Interface

### What DDx reads from HELIX

| Artifact | Location | DDx usage |
|---|---|---|
| Artifact-type metadata | `meta.yml` per artifact type | Doc-graph indexing, prose-checker rules |
| Artifact templates | `template.md` per artifact type | Surface to agents for bead authoring assistance |
| Authoring prompts | `prompt.md` per artifact type | Surface to agents during frame, design, evolve |
| Artifact schema | `workflows/artifact-schema.md` | Authoritative field definitions for `ddx:` frontmatter |
| Routing skill body | `skills/helix/SKILL.md` | Loaded into agent sessions via plugin skill loader |
| Instance frontmatter | `ddx:` block in project `docs/helix/` files | `ddx.id`, `ddx.depends_on`, `ddx.type`, `ddx.status` for graph traversal and queue dep-resolution |

DDx must consume these as read-only inputs. Indexing and caching are fine;
modifying the catalog source is not.

### What DDx writes

| Artifact | Location | Notes |
|---|---|---|
| Beads | `.ddx/beads.jsonl` | Owned by DDx; HELIX does not write here directly |
| Execution runs | `.ddx/exec/runs/` | DDx persists run manifests and evidence |
| Plugin layout | `.ddx/plugins/helix/` | DDx installs HELIX content here; source stays in `workflows/` |
| Runtime events | `.ddx/events/` or inline bead fields | DDx writes `execute-loop-*` fields; HELIX must not write these |
| Session/transcript capture | DDx session store | DDx-owned; not part of HELIX artifact schema |

### What the runtime contract requires (minimum)

From `docs/install/README.md`, items 1–3 are required for all HELIX routes:

1. Read markdown files from the project filesystem.
2. Write markdown files to the project filesystem.
3. Search files by path or pattern.

Item 4 (shell execution) is optional; DDx satisfies it fully. DDx is therefore
a full-capability HELIX runtime. The DDx adapter may expose additional surfaces
(bead tracker, execute-loop, metrics), but those are DDx extensions, not HELIX
requirements.

### Execute-loop result surface (DDx → HELIX skill)

When the HELIX routing skill's `build` or `run` modes delegate to
`ddx agent execute-loop --once --json`, the skill reads
`results[].bead_id` for post-cycle bookkeeping and `results[].status`
(`success`, `no_changes`, `execution_failed`, `land_conflict`,
`post_run_check_failed`, `structural_validation_failed`) to decide workflow
continuation. Full payload shape and status semantics are defined in
CONTRACT-001 §DDx -> HELIX, which remains authoritative for this surface.

## What Is NOT in Scope

### HELIX must not know about

- Bead IDs, bead lifecycle, or claim mechanics. HELIX content may mention
  "work items" generically; it must not depend on `.ddx/beads.jsonl` format.
- DDx internal fields (`execute-loop-retry-after`, `execute-loop-failed-routes`,
  etc.). These must not appear in HELIX artifact templates, prompts, or skill
  body.
- DDx plugin manifest format. HELIX does not own or define the
  `.ddx/plugins/helix/` layout; it only defines the source content.
- DDx model-routing, harness selection, or power-class labels. HELIX skill may
  request a tier constraint in `build`/`run` modes, but must not embed DDx
  model names or harness names in its normative body.

### DDx must not require

- A particular execute-bead contract beyond the minimal runtime contract
  (read-file, write-file, search-files). DDx may offer a richer contract as an
  opt-in; it must not mandate it for HELIX content to be usable.
- HELIX artifacts to carry DDx-specific fields as required fields. All DDx
  operational fields in `ddx:` frontmatter must be ignorable by Claude Code and
  Genie without changing artifact meaning (per artifact-schema §consumer
  responsibilities and §optional extension fields).
- HELIX to implement a queue, a tracker, or an execution loop. If DDx needs
  queue semantics, DDx provides them.

## Migration Notes: Boundary Leak Ledger

This ledger records the concrete boundary leaks identified during the
2026-Q2 scope-collapse audit and their current repository state. Keep entries
when they remain useful as an audit trail; reopen them only if a later edit
reintroduces the DDx-specific coupling.

### LEAK-1 — Commit guidance now uses runtime-neutral execution language

- **Status:** Resolved
- **Evidence:** `skills/helix/SKILL.md` §Commit

The earlier leak was the `commit` workflow contract naming DDx-specific
history markers such as `execute-bead` and `[ddx-*]`. The current contract now
says to "Preserve history produced by runtime-managed execution," which keeps
the rule portable across DDx, Claude Code, and Genie while preserving the
intent of the original safeguard.

### LEAK-2 — Review workflow no longer conditions follow-up work on DDx tracking

- **Status:** Resolved
- **Evidence:** `skills/helix/SKILL.md` §Review

The earlier leak was a DDx/HELIX-specific conditional around filing durable
follow-up work. The current review contract unconditionally requires durable
follow-up work for actionable findings, leaving the storage surface to the
runtime.

### LEAK-3 — Operating discipline now states bead-first rules generically

- **Status:** Resolved
- **Evidence:** `skills/helix/SKILL.md` §Operating Discipline

The earlier leak named DDx explicitly in the operating-discipline rule for
checking governed work before editing files. The current text generalizes this
to "projects with governed work records," which preserves the discipline
without tying it to one runtime.

### LEAK-4 — Artifact schema now distinguishes canonical source from DDx install path

- **Status:** Resolved
- **Evidence:** `workflows/artifact-schema.md` §Directory layout conventions

The earlier leak treated `.ddx/plugins/helix/workflows/` as the installed
catalog location without clarifying that the path varies by runtime. The
artifact schema now states that install paths are runtime-specific, names the
DDx plugin path only as the DDx-managed example, and keeps `workflows/` in the
HELIX repo as the canonical source.

### LEAK-5 — CONTRACT-001 already carries a pre-collapse supersession note

- **Status:** Resolved
- **Evidence:** `docs/helix/02-design/contracts/CONTRACT-001-ddx-helix-boundary.md`
header note

The earlier leak was the directional framing in CONTRACT-001 that described
DDx as HELIX's "platform substrate" without any scope-collapse context. The
current document already opens with a note that marks that framing as
pre-collapse and points readers to CONTRACT-003 for the current runtime-adapter
boundary.

No currently open boundary leaks are recorded here. New entries should be added
only when a file in the repository again crosses the minimal runtime contract
described above.

## Validation Checklist

The adapter boundary is healthy when all of the following are true:

- [ ] Zero hits for `ddx `, `execute-bead`, `[ddx-`, or `.ddx/` in
      `skills/helix/SKILL.md` normative body (PRD R-4 acceptance test)
- [ ] `workflows/artifact-schema.md` is the schema authority; no parallel
      DDx-internal schema redefines `ddx:` frontmatter
- [ ] DDx operational fields in `ddx:` frontmatter are ignorable by Claude Code
      and Genie without changing artifact meaning
- [ ] HELIX routing skill invokes DDx execution through the agent session, not
      via subprocess calls embedded in skill prose
- [ ] `docs/install/ddx.md` covers all DDx-specific packaging, naming, and
      invocation notes; none of that detail appears in `skills/helix/SKILL.md`
- [ ] Every boundary-leak ledger entry has current evidence and is either
      resolved or linked to active follow-up work

## References

- [PRD](../../01-frame/prd.md) — R-4 (runtime-neutral), R-7 (per-runtime packages), Constraints
- [Minimal Runtime Contract](../../../docs/install/README.md#minimal-runtime-contract)
- [Claude Code install guide](../../../docs/install/claude-code.md)
- [Artifact Schema](../../../workflows/artifact-schema.md)
- [Routing Skill](../../../skills/helix/SKILL.md)
- [CONTRACT-001: DDx / HELIX Boundary Contract](CONTRACT-001-ddx-helix-boundary.md) — pre-collapse shared-object definitions, still authoritative for execute-loop result surface
- [CONTRACT-002: HELIX Execution-Document Conventions](CONTRACT-002-helix-execution-doc-conventions.md)
