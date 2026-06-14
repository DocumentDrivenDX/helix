# HELIX Website Voice

This guide applies the `public-site` profile from
[`workflows/voice.yml`](../../workflows/voice.yml) to public website copy:
home, install, why, use, skills, platforms, reference landing pages, cards,
banners, and generated page preambles. It does not change HELIX methodology
terms; it defines how to introduce them to a reader seeing HELIX for the first
time.

## Reader

Write for a smart software builder who has not read the HELIX repo, the DDx
tracker, or previous design discussions. The reader may know agents, specs,
PRDs, ADRs, CI, and documentation sites. Do not assume they know HELIX terms.

Each page or module should stand mostly on its own:

- Name the thing being discussed before using shorthand.
- State why the reader should care.
- Link to the canonical definition after a local explanation.
- Give the reader a next action.

## Page Intro Contract

The first body paragraph of every hand-authored public page must answer:

- What this page covers.
- What the reader likely knows, has installed, or is trying to decide.
- What the reader can do after reading it.

Short pages can answer all three in one paragraph. Reference pages can be more
direct, but they still need a plain-language first sentence.

## First-Use Definition Contract

Define HELIX-specific terms on first meaningful use. A link alone is not a
definition. Use a short local definition, then link if the term has a canonical
page.

Good:

```text
A concern is a cross-cutting rule set, such as accessibility or observability,
that downstream artifacts and runtime work inherit.
```

Avoid:

```text
Concerns propagate through the flow.
```

## Standalone Card Contract

Cards must not rely on the page around them to explain the click.

Each card needs:

- A title naming the destination or object.
- A subtitle saying what the reader gets, who uses it, or what happens after
  the click.
- Concrete nouns over internal labels.

Bad:

```text
Artifact Types
Browse the reusable catalog.
```

Good:

```text
Artifact Types
Browse HELIX document patterns: PRDs, ADRs, test plans, runbooks, and the
templates used to write them.
```

## Definition Map

Use these definitions and destinations unless a page has stronger local
authority.

| Term | Public definition | Canonical destination | Use notes |
| --- | --- | --- | --- |
| artifact type | A reusable HELIX document shape with a purpose, template, prompt, relationships, and quality criteria. | `/artifact-types/` | Use for the catalog entry, not for a project's concrete document. |
| artifact | A concrete project document created from an artifact type, such as a PRD, ADR, test plan, or runbook. | `/artifacts/` | The `/artifacts/` tree is HELIX's own example docs, not a rulebook for adopters. |
| catalog | The generated reference set of artifact types and concerns that HELIX uses to decide what documents and rule sets exist. | `/artifact-types/` and `/concerns/` | Name the specific catalog when possible: artifact-type catalog or concern catalog. |
| routing skill | The portable `helix` skill that reads artifacts, chooses a workflow mode, and tells the agent what bounded work to do next. | `/skills/` | Do not imply the skill is a runtime or queue runner. |
| runtime | The tool or environment that executes agent work, loads context, stores work items, runs checks, or records evidence. | `/use/#how-helix-fits-your-runtime` | DDx is the reference runtime, not a HELIX requirement. |
| flow scope | One governed artifact root in a repository, such as product docs or website docs. | `/use/multiple-flows/` | Use when one repository has more than one HELIX-governed area. |
| domain lane | A subject lens, such as product, web, data, or infrastructure, that shapes context and stop rules after the flow scope is known. | `/use/multiple-flows/` | A lane is not a separate public skill. |
| concern | A cross-cutting rule set, such as accessibility, security, observability, or a tech stack, that selected artifacts and runtime work inherit. | `/concerns/` | Link the specific concern page when naming one. |
| authority hierarchy | The conflict-resolution order from vision and requirements down to design, tests, implementation plans, and source code. | `/reference/glossary/concepts/#artifact-authority-hierarchy` | First use: artifact authority hierarchy. Later uses: authority hierarchy. |
| dogfood docs | HELIX's own project artifacts, published as examples of the methodology applied to HELIX itself. | `/artifacts/` | Prefer "example docs" in public copy unless the page explains dogfooding. |
| example docs | HELIX's own published artifacts that show how the method looks in practice. | `/artifacts/` | Use this reader-facing phrase on landing pages and cards. |
| bead | A DDx work item used by the reference runtime to track bounded execution and evidence. | `/reference/glossary/tracker/#beads` | Define as DDx-owned. Do not present beads as required for HELIX adoption. |

## Term Policy

Hard-ban these terms in public website copy unless quoting a source title,
command output, or historical artifact:

- authority order
- checkout CLI
- HELIX platform
- magic
- seamless
- robust
- leverage
- transform
- revolutionize
- adopter doctrine
- source traceability
- generated area
- dogfood corpus
- dogfood artifacts
- bare reusable catalog

Avoid bare `dogfood`. Prefer "HELIX's own example docs" or "example docs from
this repository." If "dogfood" appears on a maintainer-facing reference page,
the same sentence or preceding paragraph must define it.

Context-gated terms may appear only when the sentence or surrounding paragraph
names the specific meaning:

- agent: say which agent or runtime role.
- workflow: say whether this means HELIX activities, a bounded skill mode, or a
  runtime execution loop.
- flow: prefer `flow scope` when discussing multi-scope configuration.
- lane: prefer `domain lane` and name the lane.
- catalog: say artifact-type catalog or concern catalog.
- automation: name the script, check, runtime, or generated source.
- evidence: name the evidence type, such as test output, review finding, CI
  result, or generated diff.
- review: say whether this means deterministic repo checks, sloptimizer review,
  Claude review, or HELIX alignment review.
- routing skill: say this means the portable `helix` skill, not a runtime.
- runtime-neutral: say which runtime boundary the copy is protecting.
- artifact discipline: say which artifact rule, link, or authority relationship
  is in scope.
- methodology layer: say whether the page means HELIX templates, concerns,
  workflow modes, or the routing skill.

## Generated-Source Ownership

Generated visible copy is still public copy. Fix it in the source generator or
upstream source document, not by hand-editing generated output.

- `artifact-types/` and `concerns/` copy comes from `workflows/`.
- `artifacts/` copy comes from `scripts/publish-artifacts.py` and source
  documents under `docs/helix/`.
- `research/` copy comes from `docs/resources/`.

Generated historical bodies may contain old terms as evidence. The public
banner, landing-page intro, collection intro, card text, and metadata must use
reader-facing language.

## Review

Use two review passes:

1. Sloptimizer pass: remove AI-writing tics, vague claims, and filler.
2. Public voice pass: check first-use definitions, standalone cards, page intro
   contract, and reader-facing terms.

Claude or another model can review as a cold novice reader. Treat that review as
evidence: fold in findings, waive them with a reason, or file follow-up beads.
Deterministic repo checks are the merge gates. Sloptimizer and Claude review are
review evidence for prose quality, reader confusion, and unsupported claims;
they do not replace repo-owned validators.
