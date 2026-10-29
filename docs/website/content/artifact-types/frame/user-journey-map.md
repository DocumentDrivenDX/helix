---
title: "User Journey Map"
linkTitle: "User Journey Map"
slug: user-journey-map
activity: "Frame"
artifactRole: "supporting"
weight: 90
generated: true
---

## Purpose

User Journey Map is the **frame-level experience artifact**, and it is
optional. Its unique job is to show the whole experience a task involves,
including steps outside the product, so the team can see where the stories
cover the experience, where they leave gaps, and which opportunities it owns.

It is not a story, a user flow or a design. Stories own testable behavior; the
user flow owns views and transitions; wireframes own layout and states. The map
links to them by ID.

## Example

<details open>
<summary>Show a worked example of this artifact</summary>

``````markdown
---
ddx:
  id: example.user-journey-map.depositmatch.import-weekly-files
  authoring:
    home: repo
  depends_on:
    - example.feature-specification.depositmatch.csv-import
    - example.user-story.depositmatch.upload-csv
---

# UJM-001: Import a Client's Weekly Files

**Feature**: [[FEAT-001]] CSV Import and Column Mapping | **Map kind**: future-state | **Evidence**: research plan `pilot-reviewer-interviews` (6 interviews), pilot support tickets

## Actor and Scenario

- **Person**: Reconciliation lead. Reconciles 12 to 20 clients a week on a desktop; knows each client's books, not their export formats.
- **Task**: Import a client's weekly files (FEAT-001 Task Model).
- **Scenario**: Monday's bank and invoice exports for Acme Dental arrive by email. Maya brings them into DepositMatch, checks the columns and the rejected rows, and confirms the import so matching can start.
- **Trigger**: The client's weekly exports arrive.
- **End state**: The import is confirmed and match suggestions are ready, or Maya knows exactly what to ask the client to fix.

### Goals and Expectations

- Finish each client's import in under five minutes.
- Never let a wrong column produce plausible-looking matches.
- Know before matching which rows were left out and why.

## Journey Phases

| Phase | Actions | Thoughts | Emotion | Touchpoints | Stories / ACs |
|---|---|---|---|---|---|
| Receive | Saves the two attachments from the client's email | "Same format as last week, I hope." | neutral: routine | Email (outside the product) | uncovered: happens outside DepositMatch |
| Upload | Starts a new import and attaches both files | "Did it take both?" | neutral: brisk | upload | US-001-AC1, US-001-AC2 |
| Check columns | Confirms the saved mapping, fixes one renamed column | "If amount is wrong, every match is wrong." | negative: wary | mapping review | US-002-AC1, US-002-AC2 |
| Review rejections | Reads why 14 rows were rejected | "Are these mine to fix or the client's?" | negative: unsure | validation results | US-003-AC1 |
| Confirm | Confirms the import and moves to matching | "Good, that's done." | positive: relieved | import summary | US-003-AC2 |
| Follow up | Emails the client about the rejected rows | "They'll want the row numbers." (assumption) | neutral | Email (outside the product) | uncovered: no story exports the rejected rows |

## Insights

| Insight | Phase | Evidence |
|---|---|---|
| A renamed column is the most common reason an import goes wrong | Check columns | 4 of 6 interviews; 9 pilot support tickets |
| Reviewers copy rejected rows by hand into an email to the client | Follow up | 5 of 6 interviews |

## Opportunities

| Opportunity | Phase | Owner | Metric | Target |
|---|---|---|---|---|
| Flag a saved mapping whose column was renamed, before the reviewer confirms | Check columns | Import squad | Imports corrected after confirmation | hypothesis: under 1% |
| Export rejected rows with their row numbers and reasons | Follow up | Product | Median time from summary to client email | hypothesis: under 2 minutes |

## Story Coverage

| Phase | Covered by | Gap |
|---|---|---|
| Upload to Confirm | US-001, US-002, US-003 | None |
| Follow up | none | No story exports the rejected rows |
``````

</details>

## Reference

<table class="helix-reference-table">
<tbody>
<tr><th>Activity</th><td><a href="../../../reference/glossary/activities/"><strong>Frame</strong></a> — Define what the system should do, for whom, and how success will be measured.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/01-frame/journey-maps/UJM-{n}-{name}.md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Informs</th><td><a href="../../../artifact-types/design/user-flow/">User Flow</a><br><a href="../../../artifact-types/design/solution-design/">Solution Design</a><br><a href="../../../artifact-types/test/story-test-plan/">Story Test Plan</a><br><a href="../../../artifact-types/iterate/improvement-backlog/">Improvement Backlog</a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># User Journey Map Generation Prompt&#10;&#10;Map one person&#x27;s experience of one task, phase by phase, and trace each phase&#10;to the acceptance criteria that deliver it.&#10;&#10;## Purpose&#10;&#10;User Journey Map is the **frame-level experience artifact**, and it is&#10;optional. Its unique job is to show the whole experience a task involves,&#10;including steps outside the product, so the team can see where the stories&#10;cover the experience, where they leave gaps, and which opportunities it owns.&#10;&#10;It is not a story, a user flow or a design. Stories own testable behavior; the&#10;user flow owns views and transitions; wireframes own layout and states. The map&#10;links to them by ID.&#10;&#10;## Focus&#10;&#10;- Create `docs/helix/01-frame/journey-maps/UJM-XXX-[name].md` only when a task&#10;  spans several stories or views and the team needs the whole picture.&#10;- Pick one person from the PRD&#x27;s User Segments and one task from the feature&#10;  specification&#x27;s Task Model, and name both. If the PRD has no User Segments&#10;  or the feature has no Task Model, name the person and the task in plain words&#10;  from the PRD&#x27;s users and the feature&#x27;s stories instead. A second person or&#10;  task is a second map.&#10;- State goals and expectations before the phases; phases are judged against&#10;  them.&#10;- Name phases as the person&#x27;s stages (&quot;Notice&quot;, &quot;Prepare&quot;, &quot;Decide&quot;), not as&#10;  views. Include steps outside the product, such as an email or a phone call.&#10;- Per phase, write the actions, the person&#x27;s thoughts in their words, one&#10;  emotion (positive, neutral or negative, plus a word) and the touchpoints.&#10;- Ground thoughts and emotions in evidence: a research plan&#x27;s findings,&#10;  support data or analytics. Mark ungrounded entries &quot;(assumption)&quot;. Do not&#10;  invent research.&#10;- Trace every in-product phase to `US-&lt;n&gt;-AC&lt;m&gt;` IDs. Mark a phase no&#10;  criterion delivers as `uncovered:` with a reason; that gap is a finding.&#10;- Give every opportunity one owner and the metric that shows its effect. A&#10;  target is optional: label it a hypothesis unless evidence supports it, and do&#10;  not turn it into a delivery or release gate.&#10;- Name rows by what they say; do not number insights or opportunities.&#10;&#10;## Boundary Test&#10;&#10;| If you are writing... | Put it in... |&#10;|---|---|&#10;| The person&#x27;s phases, thoughts, emotions, insights, opportunities | User Journey Map |&#10;| The tasks a feature supports | Feature Specification (Task Model) |&#10;| Testable behavior and Given/When/Then criteria | User Stories |&#10;| Views, transitions and alternate paths | User Flow |&#10;| Layout, states and events of one view | Wireframe |&#10;| Ranked follow-up work | Improvement Backlog |&#10;&#10;## Completion Criteria&#10;&#10;- One person and one task, with a scenario, goals and expectations.&#10;- Phases run from trigger to end state.&#10;- Every in-product phase names its acceptance criteria or is marked uncovered.&#10;- Every thought and emotion cites evidence or is marked as an assumption.&#10;- Every opportunity has one owner and one metric; any target is supported or labelled a hypothesis.</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---&#10;ddx:&#10;  id: UJM-XXX&#10;  authoring:&#10;    home: repo&#10;  depends_on:&#10;    - FEAT-XXX&#10;    - US-XXX&#10;---&#10;&#10;# UJM-XXX: [Journey Name]&#10;&#10;**Feature**: [[FEAT-XXX]] | **Map kind**: [current-state | future-state] | **Evidence**: [research plan, support data, analytics, or &quot;assumption-based&quot;]&#10;&#10;## Actor and Scenario&#10;&#10;- **Person**: [PRD user segment, or the PRD user if it has no segments: role, context, a relevant constraint such as device, expertise or access]&#10;- **Task**: [The Task Model row in FEAT-XXX this journey carries out, by name, or the task in plain words if the feature has no Task Model]&#10;- **Scenario**: [What happens, from trigger to end state, in one or two sentences]&#10;- **Trigger**: [The event that starts the journey]&#10;- **End state**: [What is true when the person is done]&#10;&#10;### Goals and Expectations&#10;&#10;- [What the person is trying to achieve, in their terms]&#10;- [What they expect to happen: time, effort, feedback, control]&#10;&#10;## Journey Phases&#10;&#10;&lt;!-- Phases are the person&#x27;s stages, not views. Include steps outside the&#10;product. Emotion: positive / neutral / negative, plus a word. Mark ungrounded&#10;thoughts and emotions &quot;(assumption)&quot;. --&gt;&#10;&#10;| Phase | Actions | Thoughts | Emotion | Touchpoints | Stories / ACs |&#10;|---|---|---|---|---|---|&#10;| [Phase name] | [What the person does] | [&quot;What they think&quot;, in quotes] | [positive / neutral / negative: word] | [Channel, or a user-flow view] | [US-XXX-AC1, or &quot;uncovered: reason&quot;] |&#10;&#10;## Insights&#10;&#10;&lt;!-- Pain points and moments that matter, each with its evidence. --&gt;&#10;&#10;| Insight | Phase | Evidence |&#10;|---|---|---|&#10;| [Pain point or moment that matters] | [Phase] | [Research plan finding, support data, or &quot;assumption&quot;] |&#10;&#10;## Opportunities&#10;&#10;&lt;!-- Each opportunity has one owner and one metric. A target is optional:&#10;label it a hypothesis unless evidence supports it. It is not a delivery gate. --&gt;&#10;&#10;| Opportunity | Phase | Owner | Metric | Target |&#10;|---|---|---|---|---|&#10;| [What to change or add] | [Phase] | [Role or team] | [Metric; link its metric definition if one exists] | [Supported target, a hypothesis, or none] |&#10;&#10;## Story Coverage&#10;&#10;| Phase | Covered by | Gap |&#10;|---|---|---|&#10;| [Phase] | [US-XXX: AC IDs] | [None, or what no story delivers yet] |</code></pre></details></td></tr>
</tbody>
</table>
