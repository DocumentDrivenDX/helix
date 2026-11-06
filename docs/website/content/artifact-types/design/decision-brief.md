---
title: "Decision Brief"
linkTitle: "Decision Brief"
slug: decision-brief
activity: "Design"
artifactRole: "supporting"
weight: 90
generated: true
---

## Purpose

Answers: **Given this context, which option do we recommend, why, on what
conditions, and what would change the answer?** It sits before an ADR. It is
the argument; the ADR is the record of what was decided.

## Example

<details open>
<summary>Show a worked example of this artifact</summary>

``````markdown
---
ddx:
  id: DB-001
  type: decision-brief
  status: draft
  authoring:
    home: repo
  links:
    - {id: component-profile-postgresql-reusable, kind: evaluates, rev: example}
---

# DB-001: Which database should the document-search service use?

## Context

A small team is building a document-search service that stores documents
and their metadata and serves interactive queries from a web application. The
team already runs a relational database for its other services and wants to
avoid operating a second kind of store unless the benefit is clear. This brief
covers the choice of database engine for the service. Where it is hosted is a
separate decision and out of scope.

| Bound | Source | Effect on the choice |
|-------|--------|----------------------|
| Transactions must be atomic across a document and its metadata | PRD, Data Integrity | Excludes options without multi-row transactions |
| Metadata varies by document type | PRD, Search | Favors options with a native semi-structured type |
| Team operates one relational engine today | Current state | Adds cost to a second engine |

## Decision

Choose the database engine for the document-search service. The service
owner decides.

## Options

- **Extend the existing relational engine.** Use the engine already in
  production for the service's tables. Evidence: the engine's technology brief.
- **PostgreSQL.** A separate relational engine with a native binary JSON type.
  Evidence: PostgreSQL technology brief (component-profile-postgresql-reusable).
- **Status quo plus a search index.** Keep the current engine and add a
  separate search service for metadata queries. Evidence: none yet.

## Evaluation

| Criterion | Existing engine | PostgreSQL | Existing engine plus search index |
|-----------|-----------------|------------|-----------------------------------|
| Atomic multi-row transactions | Unknown (not researched) | Documented transactions and constraints | Unknown (not researched) |
| Semi-structured metadata | Unknown (not researched) | `jsonb` with indexing and containment operators | Unknown (not researched) |
| Added operating cost | None | A second engine to run | A second service to run |

The only option with cited evidence here is PostgreSQL; the other two need
their own briefs before the comparison is complete.

## Recommendation

**Recommendation**: Do not decide yet. PostgreSQL meets the transaction and
metadata bounds on the public record, but the existing engine has not been
researched, and it carries no added operating cost. Write the existing
engine's technology brief, then re-evaluate.

What would change it: a brief showing the existing engine lacks a native
semi-structured type or multi-row transactions would make PostgreSQL the
recommendation.

## Risks and Unknowns

| Risk or unknown | Bears on | Route |
|-----------------|----------|-------|
| Existing engine not researched | All criteria | Write its technology brief |
| Search-index option has no evidence | All criteria | Write a brief if it stays in scope |

## Evidence

| Reference | Kind | Revision | Used for |
|-----------|------|----------|----------|
| PostgreSQL technology brief (component-profile-postgresql-reusable) | Technology brief | example | Transactions, semi-structured metadata |
``````

</details>

## Reference

<table class="helix-reference-table">
<tbody>
<tr><th>Activity</th><td><a href="../../../reference/glossary/activities/"><strong>Design</strong></a> — Decide how to build it. Capture trade-offs, contracts, and architecture decisions.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/02-design/decision-brief-DB-{number}-{decision-name}.md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Informs</th><td><a href="../../../artifact-types/design/adr/">ADR</a><br><a href="../../../artifact-types/design/solution-design/">Solution Design</a><br><a href="../../../artifact-types/iterate/deliverable/">Deliverable</a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Decision Brief Generation Prompt&#10;&#10;Frame one decision in one context, compare the options against that context&#10;on cited evidence, and recommend, so a reviewer can check the argument before&#10;the decision is made. The brief is advisory.&#10;&#10;## Storage Location&#10;&#10;Store at: `docs/helix/02-design/decision-brief-DB-{number}-{decision-name}.md`,&#10;or the path the flow&#x27;s graph profile sets for this type (`locations:`).&#10;&#10;## Purpose&#10;&#10;Answers: **Given this context, which option do we recommend, why, on what&#10;conditions, and what would change the answer?** It sits before an ADR. It is&#10;the argument; the ADR is the record of what was decided.&#10;&#10;## Role Boundary&#10;&#10;A [[component-profile]] (reusable or contextual) records what is known about&#10;one component; the brief uses it as evidence and does not restate it. An ADR&#10;records a decision once taken; a brief recommends before one is. The brief&#10;never overrides requirements, approved decisions, or concerns: it names them&#10;as bounds in Context and reasons within them. If the recommendation&#10;conflicts with an approved decision, say so as a risk and route it to the&#10;owner; do not argue the decision away inside the brief.&#10;&#10;## Method&#10;&#10;1. **Frame the decision.** One decision, one context, one decider. If two&#10;   choices can vary independently (what to build on, where to run it), write&#10;   two briefs or two clearly separate sections.&#10;2. **Collect the bounds.** From the project&#x27;s requirements, approved ADRs, and&#10;   [[concerns]], list what narrows the choice. Cite each by id or path.&#10;3. **List the options,** including the status quo and any option a reviewer&#10;   will ask &quot;why not?&quot; about.&#10;4. **Gather evidence.** Cite technology briefs and component profiles by&#10;   pinned revision. Evidence from outside the project is advisory; it informs&#10;   the evaluation and does not set a requirement.&#10;5. **Evaluate every option on the same criteria,** drawn from the bounds. A&#10;   cell with no evidence says Unknown.&#10;6. **Recommend.** One option for this context, its conditions, why it beats&#10;   the strongest alternative, and what would change it.&#10;7. **Record risks and unknowns** with a route. An owner, date, or figure&#10;   appears only if a project artifact states it.&#10;8. **Pin the evidence** before approval: every reference carries the revision&#10;   it was read at.&#10;&#10;## Writing for the reviewer&#10;&#10;The reader is a reviewer, often outside the team, who will check the argument&#10;not the author. Plain words, claims in the sentence, citations after. State&#10;the recommendation first in Recommendation, not in a closing paragraph, and&#10;say what would change it. Do not inflate a conditional recommendation into a&#10;certainty.&#10;&#10;## Inputs&#10;&#10;- Requirements, approved ADRs, concerns, and principles that bound the choice&#10;- Technology briefs and component profiles for each option&#10;- The current state, for the status quo option</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---&#10;ddx:&#10;  id: DB-[number]&#10;  type: decision-brief&#10;  status: draft&#10;  authoring:&#10;    home: repo&#10;  links:&#10;    # - {id: &lt;technology brief or component profile id&gt;, kind: evaluates, rev: &lt;pinned revision&gt;}&#10;    # - {id: &lt;concern id&gt;, kind: addresses}&#10;    # - {id: &lt;source id&gt;, kind: supported_by, rev: &lt;pinned revision&gt;}&#10;---&#10;&#10;# DB-[number]: [Decision as a question]&#10;&#10;## Context&#10;&#10;The situation the decision is made in, and what bounds it. Name the&#10;requirements, approved decisions, and concerns that apply, each by id or&#10;path, and the constraints that are fixed. Say what is out of scope,&#10;including any decision that can vary independently of this one.&#10;&#10;| Bound | Source | Effect on the choice |&#10;|-------|--------|----------------------|&#10;| [Requirement, decision, concern, or constraint] | [id or path] | [How it narrows the options] |&#10;&#10;## Decision&#10;&#10;The one decision to be made, as a sentence a reviewer can answer yes or no&#10;to or choose among options for, and who decides.&#10;&#10;## Options&#10;&#10;Every option, including the status quo. One paragraph each: what it is and&#10;the briefs or profiles it rests on.&#10;&#10;- **[Option A]**: [what it is]. Evidence: [reference, pinned revision]&#10;- **[Option B]**: [what it is]. Evidence: [reference, pinned revision]&#10;&#10;## Evaluation&#10;&#10;All options against the same criteria, drawn from Context. Each cell cites&#10;evidence or says Unknown.&#10;&#10;| Criterion | [Option A] | [Option B] |&#10;|-----------|------------|------------|&#10;| [Criterion from Context] | [Finding, source] | [Finding, source] |&#10;&#10;[Two to four sentences on what separates the options for this context.]&#10;&#10;## Recommendation&#10;&#10;**Recommendation**: [Option] for [this context], on these conditions: [the&#10;conditions]. [One to three sentences on why it fits this context better than&#10;the strongest alternative.]&#10;&#10;What would change it: [the evidence or change in context that would reverse&#10;the recommendation].&#10;&#10;## Risks and Unknowns&#10;&#10;| Risk or unknown | Bears on | Route |&#10;|-----------------|----------|-------|&#10;| [Risk or open question] | [Criterion or option] | [Spike, owner decision, or accepted] |&#10;&#10;## Evidence&#10;&#10;Each reference this brief relies on, with the revision it was read at.&#10;&#10;| Reference | Kind | Revision | Used for |&#10;|-----------|------|----------|----------|&#10;| [Technology brief, profile, source] | [kind] | [revision or digest] | [criterion or option] |</code></pre></details></td></tr>
</tbody>
</table>
