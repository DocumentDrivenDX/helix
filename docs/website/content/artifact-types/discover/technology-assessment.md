---
title: "Technology Assessment"
linkTitle: "Technology Assessment"
slug: technology-assessment
activity: "Discover"
artifactRole: "supporting"
weight: 90
generated: true
---

## Purpose

Answers: **How do these technologies compare on these criteria, on the
evidence we hold?** It is reusable: no project, client, or deployment context
appears in it.

## Example

<details open>
<summary>Show a worked example of this artifact</summary>

``````markdown
---
ddx:
  id: TA-001
  type: technology-assessment
  authoring:
    home: repo
  links:
    - {id: component-profile-nodejs-reusable, kind: evaluates, rev: example}
    - {id: component-profile-python-reusable, kind: evaluates, rev: example}
assessment:
  criteria: [script-distribution, text-and-file-handling, dependency-isolation]
  subjects:
    - {id: component-profile-nodejs-reusable, label: Node.js}
    - {id: component-profile-python-reusable, label: Python}
  ratings:
    - {criterion: script-distribution, subject: component-profile-nodejs-reusable, gap: Unknown (not in the brief)}
    - {criterion: script-distribution, subject: component-profile-python-reusable, gap: Unknown (not in the brief)}
    - {criterion: text-and-file-handling, subject: component-profile-nodejs-reusable, finding: Brief section Capabilities}
    - {criterion: text-and-file-handling, subject: component-profile-python-reusable, finding: Brief section Capabilities}
    - {criterion: dependency-isolation, subject: component-profile-nodejs-reusable, finding: Brief section Technology and Operations}
    - {criterion: dependency-isolation, subject: component-profile-python-reusable, finding: Brief section Technology and Operations}
---

# TA-001: Node.js and Python for command-line tooling

## Scope

Compares Node.js and Python as runtimes for repository tooling scripts: file
and text handling, packaging, and distribution of a single script. Excludes
web services and data science workloads.

## Criteria

| Criterion | Definition | Concern |
|-----------|------------|---------|
| Script distribution | How a single script is run on a machine that lacks the runtime's packages | none |
| Text and file handling | Standard-library support for reading, parsing, and writing text files | none |
| Dependency isolation | How a script declares and isolates its own dependencies | none |

## Technologies

- **Node.js**: a JavaScript runtime. Brief: component-profile-nodejs-reusable
- **Python**: a general-purpose language runtime. Brief: component-profile-python-reusable

## Comparison

| Criterion | Node.js | Python |
|-----------|---------|--------|
| Script distribution | Unknown (not in the brief) | Unknown (not in the brief) |
| Text and file handling | Brief section Capabilities | Brief section Capabilities |
| Dependency isolation | Brief section Technology and Operations | Brief section Technology and Operations |

## Findings

On the cited briefs the technologies are comparable for text and file
handling. Script distribution is not covered by either brief, so no finding is
made.

## Contradictions and Gaps

| Item | Sources or gap | Route |
|------|----------------|-------|
| Neither brief covers single-script distribution | Both briefs | Extend each brief, then re-read this criterion |

## Evidence

| Reference | Kind | Revision | Used for |
|-----------|------|----------|----------|
| component-profile-nodejs-reusable | Technology brief | example | Text handling, isolation |
| component-profile-python-reusable | Technology brief | example | Text handling, isolation |
``````

</details>

## Reference

<table class="helix-reference-table">
<tbody>
<tr><th>Activity</th><td><a href="../../../reference/glossary/activities/"><strong>Discover</strong></a> — Validate that an opportunity is worth pursuing before committing to a development cycle.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/00-discover/technology-assessment-TA-{number}-{subject}.md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Informs</th><td><a href="../../../artifact-types/design/decision-brief/">Decision Brief</a><br><a href="../../../artifact-types/discover/position-paper/">Position Paper</a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Technology Assessment Generation Prompt&#10;&#10;Compare technologies on stated criteria from reusable technology briefs, and&#10;state findings a later decision can rely on.&#10;&#10;## Storage Location&#10;&#10;Store at: `docs/helix/00-discover/technology-assessment-TA-{number}-{subject}.md`,&#10;or the path the flow&#x27;s graph profile sets for this type (`locations:`).&#10;&#10;## Purpose&#10;&#10;Answers: **How do these technologies compare on these criteria, on the&#10;evidence we hold?** It is reusable: no project, client, or deployment context&#10;appears in it.&#10;&#10;## Role Boundary&#10;&#10;A [[component-profile]] with `scope: reusable` records one technology; the&#10;assessment compares several and cites each brief by pinned revision rather&#10;than restating it. A [[decision-brief]] recommends for one context; the&#10;assessment never does. A [[position-paper]] argues a stance; the assessment&#10;reports. If a reader needs &quot;so which one&quot;, the assessment ends and a&#10;Decision Brief begins.&#10;&#10;## Method&#10;&#10;1. **State the scope** and the technologies, including the version lines.&#10;2. **Define the criteria** before grading, from concerns where one applies.&#10;3. **Read each brief.** Grade every technology on every criterion from a&#10;   brief section; where no brief speaks, write Unknown.&#10;4. **Compare** in one table, cells citing sources. To keep the ratings as&#10;   data, put them in an `assessment:` front matter block (criteria ids from&#10;   `criteria.yml` at the flow root, a one-line finding or a stated gap for every criterion&#10;   and subject) and run `assessment-tables.py --write`; the Criteria and&#10;   Comparison tables are generated from it.&#10;5. **Write findings** only where criteria separate the technologies.&#10;6. **Record disagreement.** When two sources conflict, cite both, link with&#10;   `contradicts`, and leave the conflict open until new evidence settles it.&#10;7. **Pin the briefs** before publishing.&#10;&#10;## Writing for the reviewer&#10;&#10;Findings are claims with citations after them. Do not rank, score, or&#10;recommend. A tie or an unknown is a finding.&#10;&#10;## Inputs&#10;&#10;- Reusable technology briefs for each technology&#10;- Concerns that define criteria</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---&#10;ddx:&#10;  id: TA-[number]&#10;  type: technology-assessment&#10;  authoring:&#10;    home: repo&#10;  links:&#10;    # - {id: &lt;technology brief id&gt;, kind: evaluates, rev: &lt;pinned revision&gt;}&#10;    # - {id: &lt;source id&gt;, kind: supported_by, rev: &lt;pinned revision&gt;}&#10;    # - {id: &lt;other assessment id&gt;, kind: contradicts}&#10;  # Optional: criteria and ratings as data. The Criteria and Comparison tables below are then&#10;  # generated from it (`assessment-tables.py --write`) and cannot drift from it. Criteria are&#10;  # ids from `criteria.yml` at the flow root (entries: id, label, definition, concern). A&#10;  # `keys.yml` beside it may map short names to document ids; subjects and ratings accept a&#10;  # key, while `ddx.links` keep the full id and pinned rev.&#10;# assessment:&#10;#   criteria: [&lt;criterion id from the graph&#x27;s criteria.yml&gt;]&#10;#   subjects: [{id: &lt;technology brief id or a key from keys.yml&gt;, label: &lt;name in the table&gt;}]&#10;#   ratings:&#10;#     - {criterion: &lt;id&gt;, subject: &lt;brief id&gt;, finding: &quot;&lt;finding, source&gt;&quot;}&#10;#     - {criterion: &lt;id&gt;, subject: &lt;brief id&gt;, gap: Not published}&#10;---&#10;&#10;# TA-[number]: [Subject: what is compared]&#10;&#10;## Scope&#10;&#10;What is compared and what is not. Name each technology and version line,&#10;the kind of use the comparison speaks to, and what is excluded.&#10;&#10;## Criteria&#10;&#10;Each criterion, defined, with the concern it comes from when one applies.&#10;&#10;| Criterion | Definition | Concern |&#10;|-----------|------------|---------|&#10;| [Criterion] | [What is measured or checked] | [Concern id, or none] |&#10;&#10;## Technologies&#10;&#10;One line each, with the technology brief it rests on.&#10;&#10;- **[Technology A]**: [what it is]. Brief: [id, pinned revision]&#10;- **[Technology B]**: [what it is]. Brief: [id, pinned revision]&#10;&#10;## Comparison&#10;&#10;Every technology on every criterion. Each cell cites a brief section or says&#10;Unknown.&#10;&#10;| Criterion | [Technology A] | [Technology B] |&#10;|-----------|----------------|----------------|&#10;| [Criterion] | [Finding, source] | [Finding, source] |&#10;&#10;## Findings&#10;&#10;What the comparison shows, one short paragraph per criterion that&#10;separates the technologies. No recommendation for a project.&#10;&#10;## Contradictions and Gaps&#10;&#10;Where sources disagree (both cited), and what no brief covers.&#10;&#10;| Item | Sources or gap | Route |&#10;|------|----------------|-------|&#10;| [Conflict or gap] | [Sources] | [Research, spike, or accepted] |&#10;&#10;## Evidence&#10;&#10;| Reference | Kind | Revision | Used for |&#10;|-----------|------|----------|----------|&#10;| [Technology brief or source] | [kind] | [revision or digest] | [criterion] |</code></pre></details></td></tr>
</tbody>
</table>
