# Copilot Instructions

This repository hosts HELIX — a software development methodology, an
artifact-type catalog, and a single routing skill for AI-assisted teams.
When responding to requests against this repo, follow the conventions
below.

## What HELIX is

- **Methodology + content + one skill.** HELIX ships artifact templates,
  authoring prompts, and quality criteria under `workflows/activities/`,
  plus a single routing skill at `skills/helix/SKILL.md`. There is no
  HELIX CLI, no tracker, no execution loop — those concerns belong to
  runtimes (DDx today, Claude Code, Codex CLI, and Databricks Genie Code).
- **Artifact authority hierarchy.** Vision → PRD → Features/Stories → Architecture +
  ADRs → Solution Designs + Technical Designs → Test Plans →
  Implementation Plans → Code. Conflicts resolve upward.
- **Seven-activity loop.** Discover → Frame → Design → Test → Build →
  Deploy → Iterate. Each activity has artifact types in
  `workflows/activities/<NN>-<activity>/`.

## Where to look first

When a request touches HELIX work (alignment, framing, design,
evolution, review, routing, or content placement), consult these
authoritative sources before suggesting changes:

- `skills/helix/SKILL.md` — the single routing skill. Contains the
  routing table that maps user intent to a workflow mode (`input`,
  `frame`, `align`, `validate`, `evolve`, `design`, `backfill`,
  `review`, `polish`, `check`/`next`, `build`, `run`, `commit`,
  `release`, `experiment`, `worker`), plus per-mode workflow contracts.
- `workflows/activities/<NN>-<activity>/artifacts/<type>/` — for each
  artifact type, the `template.md`, `prompt.md`, `meta.yml`, and
  example.
- `workflows/principles.md`, `workflows/artifact-hierarchy.md`,
  `workflows/artifact-schema.md`, `workflows/REFERENCE.md` —
  methodology invariants and schema.
- `docs/helix/01-frame/prd.md` — current product scope (notably R-4
  runtime-neutral content and R-7 per-runtime packages).
- `docs/install/` — per-runtime install guides (`claude-code.md`,
  `codex.md`, `copilot.md`, `databricks-genie.md`, `README.md`).
- `docs/resources/agents/` — engineer-facing notes on each agent's
  plugin/skill mechanism (Claude Code plugins, Codex CLI skills,
  Copilot instructions, Genie Code skills, DDx plugins, agentskills.io
  spec).

## Conventions

- **Routing skill is the only public HELIX entry point.** Do not
  propose creating new `helix-*` skills, slash commands, or CLI verbs.
  Add or refine a route inside `skills/helix/SKILL.md` instead.
- **No fork.** Per-runtime install guides exist so adopters can
  install HELIX; they must not localize or rewrite the methodology.
  Normative content lives only in `skills/helix/SKILL.md` and
  `workflows/`.
- **Runtime-neutral content.** The skill body and the catalog must
  work given only "read markdown, write markdown, search files" plus
  optional shell. Do not introduce runtime-specific commands (`ddx `,
  `helix `, `bead`, `.helix/`) into the skill's normative body or the
  catalog. Runtime-specific glue belongs in per-runtime packaging,
  not in HELIX content.
- **Authority is preserved on updates.** When threading a change
  through the artifacts, update higher-authority artifacts (vision,
  PRD) before lower ones (designs, tests, code). Use the routing
  skill's `evolve` mode contract as the procedure.
- **Templates govern artifact shape.** When authoring or improving an
  artifact instance, read its
  `workflows/activities/<NN>-<activity>/artifacts/<type>/template.md`
  and `prompt.md` first; conform to required sections.

## What this repo is NOT

- Not a CLI distribution: HELIX ships content (artifact templates + a
  routing skill), not a binary.
- Not a tracker: bead state lives in DDx (`~/Projects/ddx/.ddx/`),
  not in HELIX.
- Not a runtime: HELIX does not execute the work plan — runtimes
  (DDx, Claude Code, Codex CLI, GitHub Copilot, Databricks Genie Code)
  do, against the same content.

## Common requests and the right shape of response

- *"Use HELIX to align this PRD with the design docs."* → Apply the
  `align` mode contract from `skills/helix/SKILL.md`. Read the
  governing artifacts; classify gaps; produce a report with the
  four-field handoff (destination artifact type, deliverable shape,
  next workflow mode, evidence references).
- *"Frame a new feature."* → Apply `frame` mode. Read existing Frame
  artifacts first, then the relevant template and prompt before
  drafting.
- *"Evolve this requirement through the artifacts."* → Apply
  `evolve` mode. Walk the dependency graph in both directions; update
  from the highest-authority artifact down.
- *"Review the changes on this branch."* → Apply `review` mode.
  Inspect governing artifacts, changed implementation, tests; report
  findings ordered by severity with concrete evidence.

When in doubt about which mode applies, the `check` mode of the
routing skill decides among `build`, `design`, `align`, `backfill`,
`polish`, `wait`, `guidance`, or `stop`.

## Tools and verification

Whatever shell/file/search tools are available to you are sufficient
for HELIX work. The methodology assumes:

1. Read markdown files
2. Write markdown files
3. Search files by path or pattern
4. Optionally execute a shell command (verification, build, run modes)

If you can do 1–3, every HELIX alignment, framing, design, evolve,
validate, and review request is in scope. If you can also do 4, the
execution-oriented modes become available.

## See also

- [`docs/install/copilot.md`](../docs/install/copilot.md) — Copilot
  install guide
- [`docs/install/README.md`](../docs/install/README.md) — per-runtime
  install index with the no-fork policy
- [`docs/helix/00-discover/product-vision.md`](../docs/helix/00-discover/product-vision.md)
  — vision (authority root)
- [`docs/helix/01-frame/prd.md`](../docs/helix/01-frame/prd.md) — PRD
