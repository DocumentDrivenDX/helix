---
ddx:
  id: helix.product-vision
  authoring:
    home: repo
  review:
    self_hash: dba26d9ad36984f23ce0aad01480508498f22e60ea083221d4ea06c511fee010
    deps: {}
    reviewed_at: "2026-09-16T01:53:39Z"
---

# Product Vision

## Mission Statement

HELIX is a methodology and artifact catalog for AI-assisted software teams. It
packages decades of document discipline — PRDs, design documents, test plans,
alignment reviews — as portable templates plus one skill that keeps everything
in sync as the work moves. Like the double helix of DNA, two strands run
together: the document strand holds intent, design, and tests; an execution
runtime turns those into code.

## Positioning

For software teams using AI agents to build production systems but losing time
to inconsistent specifications, drifting designs, and ad-hoc prompting, HELIX
is a portable development methodology delivered as artifact templates and a
single planning skill. Unlike one-off prompt libraries or vendor-locked
workflow tools, HELIX is a methodology you adopt, not a platform you join —
its content runs on any agent runtime that reads and writes markdown.

## Vision

HELIX becomes the default discipline for AI-assisted software development.
Teams adopt it the way they adopted test-driven development: not because of a
tool, but because the practice produces durably better software. Agents
authoring against HELIX's templates produce specifications and designs at a
level human reviewers actually trust. The skill helps teams keep governing
artifacts coherent as priorities and implementation evolve. Specifications
describe desired state; an implementation audit compares that state with
observed evidence when requested.

**North Star**: A team writes its product intent once, and the rest of the
governing artifacts — features, designs, tests, code — stay aligned with that
intent through every change, without the team rewriting documents by hand.

## User Experience

A team wants to add OAuth login. They describe the intent to their agent. The
agent reads the request, the relevant governing artifacts, and relationships
that can affect the change.

The agent identifies which artifacts the request affects and compares them
where needed. It finds that the security architecture and one accepted
decision constrain the change, and that affected feature specs, stories, and a
test plan need updates. It proposes an authority-ordered plan. The team may
also ask for a scoped implementation audit, which compares accepted
specifications with code and test evidence.

The team reviews and approves the plan. The runtime creates work items if
requested and tracks their execution. A conversational review can end with a
human-readable report; a runtime may request structured output when it needs
to process findings.

The team never invoked a HELIX command, because there isn't one. They invoked
their agent, and the agent invoked HELIX's skill.

## Target Market

| Attribute | Description |
|-----------|-------------|
| Who | Software teams using AI agents (Claude Code, Cursor, Databricks Genie, Copilot Workspace) for non-trivial development |
| Pain | Artifact drift across sessions; agents make local decisions that conflict with global intent; specs and code diverge silently; reviews catch problems too late |
| Current Solution | Ad hoc prompting, manual document maintenance, hoping for the best |
| Why They Switch | HELIX gives agents and humans the same methodology — every change traces back to a governing artifact, and the alignment skill catches drift early |

## Key Value Propositions

| Capability | Customer Benefit |
|---|---|
| Authority-ranked artifact catalog | Every document has a clear governing relationship; changes propagate predictably |
| Single alignment skill | Catches drift early without walking the artifact tree by hand |
| Portable content | Run on any runtime that reads markdown — DDx, Databricks Genie, Claude Code, anything |
| Desired-state specifications | Requirements remain clear before and after implementation |
| Methodology, not platform | Adopt incrementally; no vendor lock-in |
| Layered authority as control | Agents act only within what the layer above authorizes; a change enters at the top layer it affects and propagates down |
| Governed human hand-offs | People decide and approve, agents draft and check; autonomy level, stop triggers, and approval mark where judgment enters |

## Success Definition

| Metric | Target |
|--------|--------|
| Runtime breadth | 3 documented runtime deployments (DDx, Databricks Genie, one other) within 12 months |
| Adoption | 50+ public repos using HELIX templates as their artifact catalog within 18 months |
| Alignment quality | Healthy artifact sets average < 3 alignment findings per skill run |
| Authoring quality | PRDs and feature specs authored from HELIX templates pass first-pass review at measurably higher rates than free-form equivalents |
| Skill portability | Skill body contains zero runtime-specific commands; portability check passes on every release |

## Why Now

AI-assisted development has crossed from novelty to default practice. Most
professional developers ship AI-touched code daily. But the practice is
uneven: agents produce work that is locally good but globally inconsistent,
because the disciplines human teams developed over decades — PRDs, design
documents, test plans, alignment reviews — have not been packaged into
something agents can apply uniformly.

The agents are ready. The methodology has been ad hoc. The Genie / Cursor /
Claude Code era will have its TDD-equivalent practice. HELIX is the bet on
what it looks like: document-driven, agent-friendly, portable.
