---
title: Supervising Agent Work
weight: 5
---

This page is for people who direct a coding agent but do not write code
themselves: analysts, product managers, and domain experts building tools for
problems they know better than any developer. The agent writes the code. Your
job is to decide what it should build, notice when it does something risky,
and check whether the result works. HELIX calls this division
[human authority](../../why/human-authority/): humans decide, agents draft.

You do not need syntax, algorithms, or framework internals for that job. You
need a working model of your system, the habit of writing intent down before
the agent starts, and three questions you ask before you accept any change.

## Write intent before the agent builds

HELIX puts [intent over inference](../../why/intent-over-inference/). If you
have not written down what "done" looks like, the agent will define it,
and its definition will be whatever it managed to produce. Start with the
smallest artifact stack in the [Manual HELIX Recipe](../manual-recipe/): a
short vision or product brief, then a feature specification whose acceptance
criteria say what must be true, how someone can tell, and what must not break.

If writing that from a blank page is hard, ask the HELIX skill to
[grill](../../reference/workflow-modes/grill/) you. Grill mode asks one
question at a time, offers a recommended answer for each, and writes nothing
until you agree on what is wanted. The answers become the acceptance criteria.

Tests, lint rules, and CI checks are acceptance criteria too: ones the computer
checks on every change. You do not have to write them. You do have to read
their names and confirm they describe what you asked for.

## Know your system

Before you change a project, be able to sketch it: what runs in the browser,
what runs on a server, where the source of truth for the data lives, which
outside services it depends on, where its secrets are kept, and how it gets
deployed. Ask the agent to explain the project box by box until you can draw
it from memory.

Treat existing code as evidence of what the system does today, not as the
authority on what it should do. When code and the governing documents
disagree, the documents win, and the disagreement is a finding to resolve.

## Three questions before you accept a change

### What changed?

Read the summary and the list of changed files, not only the
agent's description of them. Agents add things nobody asked for: a second
programming language, a new dependency, their own virtual environment, or
database-specific workarounds in code meant to run on more than one database.
Agents also under-deliver while claiming done, leaving stubs or placeholders
on the path you asked for. The
[scope-discipline concern](../../concerns/scope-discipline/) names both
failures; remove what the change did not need and reopen what it did not
finish.

### How do I know it works?

A report that the work is finished is a claim
([evidence over confidence](../../why/evidence-over-confidence/)).
The [verification concern](../../concerns/verification/) requires observed
evidence of the running system: run the tool the way its users will and
compare the result to your acceptance criteria. To check the code against the
documents without reading the code, ask the HELIX skill to
[align](../../reference/workflow-modes/align/) and read its findings.

### How do I undo it?

Most changes under version control can be reverted. Some
cannot: deleting data, sending a message to another person, running a schema
migration, publishing a release. HELIX's base stop triggers make the agent
stop and ask before reading secrets, running git branch or merge commands,
making very large edits, or applying infrastructure changes. Treat any action
whose undo takes more than reverting a commit the same way: you decide, and
the agent prepares the action and waits. HELIX's
[principles](../../why/principles/) say to prefer reversible decisions.

## Keep changes small

Ask for one small change at a time, merged once CI passes and a reviewer
approves. A short diff is one you and your reviewer can read line by line,
including everything the agent added. Long-lived branches drift and become
harder to review.

## Where to go next

- [Getting Started](../getting-started/) creates the first HELIX documents.
- [Manual HELIX Recipe](../manual-recipe/) runs HELIX from an ordinary chat
  session, with prompts you can copy.
- The [CRM example](https://github.com/DocumentDrivenDX/helix/tree/main/docs/examples/crm)
  shows a one-line request growing into a governed document stack.
