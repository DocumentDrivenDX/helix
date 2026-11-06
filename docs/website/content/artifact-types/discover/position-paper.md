---
title: "Position Paper"
linkTitle: "Position Paper"
slug: position-paper
activity: "Discover"
artifactRole: "supporting"
weight: 90
generated: true
---

## Purpose

Answers: **What do we think about this, why should the audience agree, and
what would make us wrong?** It takes a side. It is not tied to one client.

## Example

<details open>
<summary>Show a worked example of this artifact</summary>

``````markdown
---
ddx:
  id: PP-001
  type: position-paper
  authoring:
    home: repo
  links:
    - {id: TA-001, kind: supported_by, rev: example}
---

# PP-001: New repository tooling should default to Python

## Thesis

**Thesis**: New command-line tooling in a repository that already uses Python
should be written in Python, not Node.js, unless a script needs a Node.js
library with no equivalent.

## Audience and Stakes

Maintainers choosing a runtime for a new tooling script. A second runtime in
a repository adds installation and upkeep for every contributor.

## Argument

1. Both runtimes handle text and file work comparably on the cited
   assessment. [TA-001, Comparison]
2. A repository with one runtime has less to install and maintain than one
   with two. Author's judgment.
3. So the existing runtime wins unless a library requires the other. Author's
   judgment.

## Objections and Answers

| Objection | Answer | Evidence |
|-----------|--------|----------|
| The team already writes JavaScript | Familiarity favors Node.js for that team; the thesis assumes the repository's existing runtime is Python | Author's judgment |
| Distribution of a single script may differ | The assessment has no finding on distribution; the thesis does not rely on it | TA-001, Contradictions and Gaps |

## Limits of the Position

The paper does not claim Python is better in general. It fails where the
repository's existing runtime is Node.js, or a required library exists only
for Node.js.

## Evidence

| Reference | Kind | Revision | Used for |
|-----------|------|----------|----------|
| TA-001 | Technology assessment | example | Argument step 1 |
``````

</details>

## Reference

<table class="helix-reference-table">
<tbody>
<tr><th>Activity</th><td><a href="../../../reference/glossary/activities/"><strong>Discover</strong></a> — Validate that an opportunity is worth pursuing before committing to a development cycle.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/00-discover/position-paper-PP-{number}-{subject}.md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Informs</th><td><a href="../../../artifact-types/design/decision-brief/">Decision Brief</a><br><a href="../../../artifact-types/iterate/deliverable/">Deliverable</a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Position Paper Generation Prompt&#10;&#10;Argue one position for a named audience on cited evidence, with the strongest&#10;objections answered and the limits stated.&#10;&#10;## Storage Location&#10;&#10;Store at: `docs/helix/00-discover/position-paper-PP-{number}-{subject}.md`,&#10;or the path the flow&#x27;s graph profile sets for this type (`locations:`).&#10;&#10;## Purpose&#10;&#10;Answers: **What do we think about this, why should the audience agree, and&#10;what would make us wrong?** It takes a side. It is not tied to one client.&#10;&#10;## Role Boundary&#10;&#10;A [[technology-assessment]] reports findings and takes no side; the paper&#10;argues from them and cites them by pinned revision. A [[decision-brief]]&#10;recommends for one named context; the paper does not. A paper may inform a&#10;brief; it never overrides a client&#x27;s requirements or decisions. A&#10;[[deliverable]] presents a paper to an audience; the paper is the source.&#10;&#10;## Method&#10;&#10;1. **State the thesis** as a claim a reader can reject.&#10;2. **Name the audience and the stakes.**&#10;3. **Build the argument** as ordered claims. Cite evidence for facts; label&#10;   judgments as the author&#x27;s.&#10;4. **Find the strongest objections,** including any raised by the cited&#10;   evidence, and answer each. An objection the evidence supports and the&#10;   paper cannot answer belongs in Limits.&#10;5. **State the limits:** what the paper does not claim and when it fails.&#10;6. **Pin the evidence** before publishing.&#10;&#10;## Writing for the reader&#10;&#10;Plain words, the thesis first. Do not present opinion as evidence, and do not&#10;drop a fact because it hurts the case. A figure appears only with its source.&#10;&#10;## Inputs&#10;&#10;- Technology assessments and briefs the argument rests on&#10;- The audience and what they decide</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---&#10;ddx:&#10;  id: PP-[number]&#10;  type: position-paper&#10;  authoring:&#10;    home: repo&#10;  links:&#10;    # - {id: &lt;technology assessment id&gt;, kind: supported_by, rev: &lt;pinned revision&gt;}&#10;    # - {id: &lt;technology brief id&gt;, kind: supported_by, rev: &lt;pinned revision&gt;}&#10;    # - {id: &lt;other paper or assessment id&gt;, kind: contradicts}&#10;---&#10;&#10;# PP-[number]: [The position as a claim]&#10;&#10;## Thesis&#10;&#10;**Thesis**: [The position in one or two sentences, as a claim a reader can&#10;disagree with.]&#10;&#10;## Audience and Stakes&#10;&#10;Who the paper is for and what they decide or do differently if persuaded.&#10;Name the audience by role, and say what is at stake for them.&#10;&#10;## Argument&#10;&#10;The case in order, each step a claim with its support. Label a claim of&#10;judgment as the author&#x27;s judgment; cite evidence for a claim of fact.&#10;&#10;1. [Claim]. [Evidence, pinned revision, or &quot;Author&#x27;s judgment&quot;]&#10;2. [Claim]. [Evidence or &quot;Author&#x27;s judgment&quot;]&#10;&#10;## Objections and Answers&#10;&#10;The strongest objections, including any the cited evidence raises.&#10;&#10;| Objection | Answer | Evidence |&#10;|-----------|--------|----------|&#10;| [Objection] | [Answer] | [Source or &quot;Author&#x27;s judgment&quot;] |&#10;&#10;## Limits of the Position&#10;&#10;What the paper does not claim, and the conditions under which the thesis&#10;would not hold.&#10;&#10;## Evidence&#10;&#10;| Reference | Kind | Revision | Used for |&#10;|-----------|------|----------|----------|&#10;| [Assessment, brief, or source] | [kind] | [revision or digest] | [claim] |</code></pre></details></td></tr>
</tbody>
</table>
