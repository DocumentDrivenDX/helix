---
title: "Practice Guide"
linkTitle: "Practice Guide"
slug: practice-guide
activity: "Discover"
artifactRole: "supporting"
weight: 90
generated: true
---

## Purpose

A short guide for the people responsible for a system: what a practice is, the problem it solves, how it works,
why it is worth having, how to start, the reference setup, what running it involves, what each of the four
executive readers should expect, questions to ask the team, and the common mistakes. It advocates. It carries no citations, no
source list and no document identifiers: the evidence behind it is kept apart, as working notes and a source
ledger, and every statement in the guide must be one that evidence supports. Where the support is reasoning and
not measurement, the guide gives the reasoning and states no measured effect.

A guide is written in ordinary connected prose for a reader who is not a specialist in the practice. It opens
with the point, never with a description of its reader or of itself.

## Example

<details open>
<summary>Show a worked example of this artifact</summary>

``````markdown
---
ddx:
  id: practice-guide-continuous-integration
  type: practice-guide
  authoring:
    home: repo
---

# Continuous Integration

Continuous integration is the practice of building and testing every change
automatically and merging work into the shared codebase in small pieces.
A team that works this way finds conflicts and faults within minutes of
introducing them.

## The problem

Software written by several people has to be combined, and combining it gets
harder as the amount of change grows. Consider three
developers who each spend three weeks on a separate feature, working on
their own copies of the code. Each feature works when tested alone.

When the three are merged, the application fails in ways none of the
developers observed, because each feature was written against code the
others have since changed. Resolving the conflicts takes a further week and
the release date slips. The developers did competent work. The cost came from
merging late, when the differences were large and the deadline was near.

## How it works

Continuous integration has three parts. First, every change a developer
submits is built and tested automatically by a build service, so that a fault
is reported within minutes. Second, work in progress is kept up to date. The latest shared code is merged
into each open change regularly and the change is tested again, so that it is
always checked against what the rest of your team has done. Third, your team
keeps changes small and short-lived. It tracks how long each change stays open
and how large it is, with the aim of merging work within days.

The term is sometimes used more narrowly, for teams in which every developer
merges into the shared code at least once a day. That is the same practice
taken further, and teams generally gain more the closer they get to it.

## Benefits

Merging becomes routine. A day's work merges with few conflicts, and those
that occur are easy to resolve because the code involved is small and recent.
Faults are also cheaper to fix. When a test fails a few minutes after a small
change, the cause is almost certainly in that change, whereas a failure after
a large merge could come from anywhere in it.

Small changes improve code review as well. A reviewer can read a short change
carefully and respond the same day, while long changes tend to wait and then
receive a superficial review. Because the shared code always builds and
passes its tests, there is always a version that can be demonstrated, tested
or released.

## Getting started

1. Automate the build so that a single command produces the application from
   a clean copy of the code.
2. Run the build and tests on every change, using the build service provided
   by the code host, and display the result alongside the change under
   review.
3. Write automated tests, beginning with the most important behavior, and add
   tests with each new piece of work.
4. Prevent a change from being merged until it passes against the latest
   shared code.
5. When the shared build fails, fix it or revert the change responsible
   before doing other work.
6. Record how long changes stay open and how large they are, set a target
   for each, and review the figures every few weeks.

## Reference setup

The setup has four parts. The code is kept in a hosted repository with one
shared branch that represents the current state of the product. A build
service, which runs the build and tests for each change and reports the
result, is connected to that repository. The instructions for the build are a
file stored in the repository alongside the code, so that they are reviewed
and versioned like everything else. The shared branch is protected, so that a
change cannot join it until the build service reports success.

GitHub Actions, GitLab CI and Azure Pipelines are the common build services,
and each is part of the corresponding code hosting product. If you already
host your code with one of them, you have the service available. If you have
several applications, keep a standard build definition that new projects
copy, so that each one starts with the practice in place.

## Deployment

Builds can run on machines provided by the vendor or on your own. In either case the build service needs credentials for the systems it
deploys to, which makes it a security-sensitive system. It should be given the minimum access
it needs. Secrets should be held in its protected store and kept out of the
code, and the right to change build definitions should be limited.

Build speed determines whether the practice holds, because developers stop
waiting for results that take an hour. The main build should finish in about
ten minutes, with slower tests run in parallel or moved to a later stage.

The package produced by the build should be numbered and used unchanged for
testing and release, so that what is released is what was tested. Feature
flags, which are switches that hide unfinished functionality from users,
allow incomplete work to be merged without being released.

## Views

### Risk & Compliance

Every change is tested and recorded before it is merged, which provides
evidence of control over what reaches production. The build service holds
credentials and needs the same access controls as production systems.

### Finance

The build service is often included with code hosting. The main cost is
developer time spent writing and maintaining automated tests.

### IT Operations

Operations runs the build service and manages its credentials and capacity.
The practice depends on the build being fast and reliable.

### Apps Dev

Developers write tests alongside code, divide work into small changes, and
repair a broken build before continuing other work. Merging and review take
less time as a result.

## Questions for your team

- What happens automatically when a developer submits a change?
- How long does that take to report back?
- Can a change that fails its tests reach the shared code?
- How long does a typical change stay open, and how large is it?
- When the build last broke, how long did it take to fix?

## Common mistakes

The most common failure is to install the build service without changing how
your team works. If builds run on every change but changes still stay open for
weeks, the work is not being integrated and the benefits do not appear. Slow
builds have a similar effect, because developers stop waiting for the result.

A build that is left failing teaches your team to disregard it, so a failure
should be fixed, or the change responsible reverted, straight away. Two
further problems are a test suite that covers too little, which makes a
passing build misleading, and large changes, which wait longest to be reviewed
and are the hardest to merge.
``````

</details>

## Reference

<table class="helix-reference-table">
<tbody>
<tr><th>Activity</th><td><a href="../../../reference/glossary/activities/"><strong>Discover</strong></a> — Validate that an opportunity is worth pursuing before committing to a development cycle.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/00-discover/practice-guide-[practice-name].md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Informs</th><td><a href="../../../artifact-types/discover/position-paper/">Position Paper</a><br><a href="../../../artifact-types/discover/technology-assessment/">Technology Assessment</a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Practice Guide generation prompt&#10;&#10;Write a guide to one practice for the people responsible for a system. The first reader owns or sponsors the&#10;system and is not a specialist in the practice. The others are the four reader views: Risk &amp; Compliance,&#10;Finance, IT Operations and Apps Dev.&#10;&#10;Write a guide only for a practice that no technology assessment covers. Where an assessment covers the subject,&#10;explain the practice at the front of that assessment, so that a reader is handed one document per subject and&#10;the advice is stated once.&#10;&#10;Work in this order.&#10;&#10;1. Gather the evidence first, in notes kept outside the guide: what each public source says, and whether a&#10;   benefit is argued, reported from use, or measured. A guide is not the place for that record.&#10;2. Write the guide from those notes, to the template. Say only what the notes support. Where the support is&#10;   reasoning, write the reasoning. State no measured effect that nobody measured.&#10;3. Put no citation, link, source list, document identifier or repository path in the guide, and no word about&#10;   how it was researched, reviewed or built.&#10;4. Use the `human-facing` voice (`workflows/voice.yml`) and the writing pass&#10;   (`workflows/references/writing-pass.md`). Open with the point: two sentences on what the practice is and what&#10;   teams use it for. Never open by describing the reader or the guide. Speak to the reader as &quot;you&quot; and &quot;your&#10;   team&quot;.&#10;5. Write connected paragraphs under plain headings. A guide written as slogans reads as machine-made: avoid a&#10;   bold phrase followed by a clipped sentence, one-line paragraphs for effect, and &quot;X, not Y&quot;. Bold a term only&#10;   where it is defined. Keep lists for the steps and the questions.&#10;6. In Reference setup, name what to stand up: what the application does, the shared service the organization&#10;   runs, and where the result ends up. Say what the shared service buys and what it costs, and give the smallest&#10;   version a single team can start with. Name a product only as an example of a kind of tool, with a clause&#10;   saying what it is. A choice between products belongs in a technology assessment.&#10;7. In Views, answer each of the four readers&#x27; first question as it applies to this practice, under the headings&#10;   Risk &amp; Compliance, Finance, IT Operations and Apps Dev. Say Not applicable, with the reason, where one does&#10;   not arise.&#10;8. Aim for about 1,000 words. Render the guide and read every page before showing it to anyone.</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---&#10;ddx:&#10;  id: practice-guide-[name]&#10;  type: practice-guide&#10;  authoring:&#10;    home: repo&#10;---&#10;&#10;# [Practice name]&#10;&#10;[Two sentences: what the practice is, and what teams use it for.]&#10;&#10;## The problem&#10;&#10;[Two paragraphs. A general statement of the difficulty, then one concrete, ordinary case in the third person&#10;(&quot;Consider a team that ...&quot;) showing how it plays out and what it costs. No blame, no drama.]&#10;&#10;## How it works&#10;&#10;[One or two paragraphs describing the practice in operation. Define each term in bold where it first appears.&#10;If the practice is commonly confused with a neighbor, or the name is used in two senses, say so here.]&#10;&#10;## Benefits&#10;&#10;[Two or three paragraphs. The main benefit first, tied back to the case above. Then the others. Reasoning is&#10;written as reasoning.]&#10;&#10;## Getting started&#10;&#10;[One sentence of framing if needed, then up to six numbered steps in order of value, each a complete sentence&#10;or two. Say which steps a small or early system can stop at.]&#10;&#10;## Reference setup&#10;&#10;[The concrete arrangement this library recommends, so that a reader can tell their team what to stand up. Two&#10;to four paragraphs:&#10;1. The parts, in the order the work or data flows. For most practices there are three: what the application&#10;   does (in an open standard where one exists), the shared service the organization runs to receive or enforce&#10;   it, and where the result ends up. Name each product and say in a clause what it is.&#10;2. Why the shared service in the middle is worth having: applications are configured once, policy is applied&#10;   in one place, and the product behind it can change without changing the applications. State its cost.&#10;3. The smallest version a single small team can start with, and what changes when it grows into the full&#10;   setup.&#10;Write &quot;we recommend&quot; only for what this library advises.]&#10;&#10;## Deployment&#10;&#10;[Two to four paragraphs for the people who will run it: hosting choices, the decisions that affect cost and&#10;compliance, how sensitive data and credentials are protected, and who is responsible out of hours. Do not&#10;repeat the reference setup. Where this library has a paper on the choice of tool, name it by title in a&#10;closing sentence.]&#10;&#10;## Views&#10;&#10;[The four reader views, under these exact headings and in this order. Each gets two or&#10;three sentences answering its question as it applies to a practice. A view that does not arise says &quot;Not&#10;applicable&quot; and why. No heading is left out.]&#10;&#10;### Risk &amp; Compliance&#10;&#10;[Can we defend how we do this to a regulator, client or auditor? What the practice gives this reader as a&#10;control or a record, and what to ask for.]&#10;&#10;### Finance&#10;&#10;[What does adopting it cost, now and as it grows, and what are we committed to? Name the cost drivers and what&#10;controls them. Give no figure the evidence lacks.]&#10;&#10;### IT Operations&#10;&#10;[Who runs it, and what happens at 2 a.m.? What operations stands up, owns and answers for.]&#10;&#10;### Apps Dev&#10;&#10;[How does it change the way teams build, and what will slow them down? What developers do differently and what&#10;they get for it.]&#10;&#10;## Questions for your team&#10;&#10;[Five questions a sponsor can ask without specialist knowledge.]&#10;&#10;## Common mistakes&#10;&#10;[Two paragraphs covering four or five mistakes, each with what to do instead, in running prose.]</code></pre></details></td></tr>
</tbody>
</table>
