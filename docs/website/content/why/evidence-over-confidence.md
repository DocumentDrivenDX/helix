---
title: "The ‘E’ principle: Evidence over confidence"
weight: 2
---

> Confidence in quality comes from validation rather than how certain an agent sounds.

An agent can sound certain that a task is finished even when it has missed a requirement or left important behavior untested. HELIX calls confidence without enough supporting evidence “hallucinated confidence,” and makes checking the result part of completing the work.

## What needs to be checked

Before work begins, the task should describe what a successful result looks like. Acceptance criteria could determine what needs checking, whether that involves automated tests, examining an interface, observing the software in use, or reviewing a document.

For example, suppose a specification requires a data export to respect the filters selected in an interface. An agent might produce a correctly formatted file and pass tests for file creation while still exporting records the user excluded. Checking the file's contents against the selected filters would establish whether the implementation meets that requirement.

The checks should cover the behavior the task requires, with the amount of verification reflecting the scope of the change and the consequences of getting it wrong.

## Reviewing the result

A review of the result should also consider whether the work follows relevant requirements, specifications, and design decisions. Software can run successfully while still introducing an unrequested feature, ignoring a constraint, or leaving its documentation out of date.

A human or agent reviewer should examine the result against those documents and record specific findings. A separate review prompt or another model can help, but the review still needs to explain what was examined, what the checks showed, and what remains uncertain.

Sometimes the findings reveal an incomplete specification or a conflict between project documents. The team then needs to resolve the disagreement explicitly and update the affected documents and implementation before treating the issue as closed.

## When work is complete

An agent may close a task when it has authority to do so, and the required evidence supports that decision. Its completion record should explain what changed, what it checked, the results, and any remaining limitations, with enough detail for someone else to understand why the work was accepted.

When a required check cannot run, or a requirement remains unclear, the agent should state the gap and what would resolve it. Missing evidence must remain visible so that the person responsible can decide how to proceed.

These checks support a decision about the task's requirements under the conditions examined. However, they still cannot guarantee that the software will behave correctly in every future situation.

## Relationship to the other HELIX principles

**Human authority** determines who may accept the work and when an agent must ask for a decision. **Linked artifacts** preserve the requirements and findings behind that decision, while **intent over inference** keeps the review grounded in what the project is supposed to do.

**Execution feedback** carries problems found during verification back into the plans, documents, or code, where the team can make the smallest sufficient change to resolve them. The evidence then remains available to anyone who needs to understand or revisit the work.



