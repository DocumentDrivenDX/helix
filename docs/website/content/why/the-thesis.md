---
title: The Thesis
weight: 3
---

AI agents can take on substantial engineering work only when the project itself preserves the intent, decisions, standards, and evidence they need.

HELIX templatizes that knowledge into a structure through seven activities, reusable document patterns called artifact types, project-wide standards called concerns, and one `helix` skill that keeps the resulting documents aligned.

Agent sessions, file edits, trackers, queues, and validation remain the responsibility of the runtime. DDx serves as the reference runtime, while Claude Code, Codex, Databricks Genie, and manual workflows can also use HELIX as long as they can read and update the project artifacts.

## Seven activities organize the work

HELIX divides software development into seven [activities](https://documentdrivendx.github.io/helix/reference/glossary/activities/):

- **Discover** defines the problem, direction, and reason for the project.
- **Frame** turns that direction into requirements, PRDs, and feature specifications.
- **Design** records architecture choices, trade-offs, ADRs, and technical designs.
- **Test** defines how the team will check whether the work meets its commitments.
- **Build** turns the agreed intent and design into implementation work.
- **Deploy** prepares the software for release and operation through runbooks, monitoring, and related artifacts.
- **Iterate** uses reviews, metrics, and production evidence to improve what comes next.

These activities give each document a clear role and place in the project, but they are not meant to run in a fixed sequence. Work can move back and forth between them as implementation, testing, review, and production use reveal new information.

Each activity owns a set of [artifact types](https://documentdrivendx.github.io/helix/why/principles/#3-the-artifact-authority-hierarchy-governs-reconciliation). 

- A vision document explains why the project exists. 
- A PRD records what it must achieve. 
- A feature specification describes expected behaviour. 
- An ADR records an architectural decision. 
- A test plan explains how the team will check the result.

Each artifact type has a defined purpose, a template, an authoring prompt, and relationships to other artifacts.

Those relationships help describe what needs to be done when something changes.

- A change to the vision may require the team to review requirements, specifications, and designs.
- A failing test may expose a defect in the code or a gap in the specification.
- Production data may challenge an assumption recorded in the PRD.
- A new architectural constraint may affect several designs and implementation tasks.

HELIX uses an [authority hierarchy](https://documentdrivendx.github.io/helix/why/principles/#3-the-artifact-authority-hierarchy-governs-reconciliation) to resolve conflicts between what the project says should happen and what the code currently does. The code shows the current state of the system and the governing artifacts capture the intended state. When the two diverge, the conflict is made explicit and resolved through the appropriate artifact rather than allowing the implementation to quietly redefine the intent.

The `helix` skill can then identify which artifact is missing, stale, or inconsistent and direct the work back to the activity that owns it.

## Concerns carry standards across the project

Project-wide standards such as accessibility, security, and technology choices can affect specifications, designs, tests, deployment, and implementation across the repository.

HELIX records these standards as [concerns](https://documentdrivendx.github.io/helix/concerns/).

A project declares concerns such as its:

- technology stack
- accessibility requirements
- security rules
- observability strategy
- testing expectations
- infrastructure conventions

The team records each concern once, and HELIX makes it available wherever the standard applies. An agent working on a feature can receive the relevant concerns together with the task context instead of depending on someone to repeat the same requirements in every prompt.

Each concern also includes an [artifact-impact contract](https://documentdrivendx.github.io/helix/use/workflow/concerns/#artifact-impact-contract). This identifies which artifacts the team should review when it adds or changes that concern.

For example, adopting a new accessibility standard may require updates to feature specifications, interface designs, test plans, and acceptance criteria. The impact contract makes those consequences visible, while the alignment checks help identify documents that still reflect the earlier standard.

HELIX provides the structure for carrying the technologies and practices chosen through the work consistently.

## One `helix` skill keeps the project aligned

HELIX uses one public skill rather than a separate skill for every activity or type of work.

The `helix` skill reads the governing artifacts, identifies the scope of the request, selects the relevant workflow, and checks for missing information, stale documents, and contradictions. It then produces a plan for resolving what it found.

HELIX keeps the plan that the runtime executes connected to the documents and decisions that govern it.

This separation allows the same HELIX project to work across different runtimes. DDx may execute the work through its tracker and queue, while another runtime may use different commands or interfaces. The project knowledge and relationships remain the same.

Some decisions still need human authority.

An agent may find that two requirements conflict, that the available documents do not establish which option the team prefers, or that the next step would change the scope of the product. In those cases, the skill should surface the exact question, explain why the work cannot proceed safely, and wait for a decision.

Once the team records that decision in the appropriate artifact, the agent can continue from a clearer starting point.

## Verification continues until the work meets its commitments

HELIX keeps completion tied to the project's commitments and does not treat a successful command, a passing unit test, or an agent's claim of completion as enough evidence that the work is done.

The [verification exit gate](https://documentdrivendx.github.io/helix/use/workflow/#verification-exit-gate) checks each acceptance criterion using evidence appropriate to the feature and interface. A change may require automated tests, an interface check, a review against a specification, operational evidence, or a combination of these.

The [evolve-until-converged loop](https://documentdrivendx.github.io/helix/use/workflow/#evolve-until-converged) then checks the result against its specifications and active concerns. If the review finds a gap, the work continues until the remaining issue is resolved or requires a human decision.

## One repository can contain more than one flow scope

A single repository may contain several bodies of work that need their own artifacts and boundaries.

A product scope may own the vision, PRDs, feature specifications, designs, and tests for the software itself. A microsite scope in the same repository may own public information architecture, demonstrations, publishing rules, and website content.

HELIX calls these flow scopes.

The project's `.helix.yml` file declares which scopes are active. This also sets an authorization boundary for the skill: it can route work within the declared scopes and asks for clarification when a request could belong to more than one.

After it identifies the correct scope, domain lanes such as product, web, data, and infrastructure help narrow the context further. These lanes shape what the `helix` skill reads and considers; they do not require separate public skills.

This lets one repository support different kinds of work without mixing their documents or forcing every task to consider the entire project.

## What this gives a team

This structure gives humans and agents a common starting point.

**The project remains understandable as it grows.** New agents and team members can follow the relationships between requirements, decisions, designs, tests, and implementation evidence rather than reconstructing the project from code and conversations.

**Knowledge survives changes in people and tools.** The important context remains in the repository when a session ends, a team member leaves, or the project moves to another model or runtime.

**Teams can change runtimes without rebuilding the method.** DDx, Claude Code, Codex, Databricks Genie, and other tools may execute work differently, while the same artifacts, concerns, and authority rules continue to govern it.

**Each cycle improves the next one.** Testing, review, and production use generate evidence that flows back into requirements, specifications, designs, and future tasks. What the team learns becomes part of the project instead of disappearing with the session that discovered it.

## The same documents can support other audiences

The artifacts that guide engineering work can also support people outside the engineering team.

The `present` mode of the HELIX skill can turn a governed set of documents into a presentation, one-page summary, or brief written for a particular audience. It traces figures and claims back to the source artifacts, so the result reflects the decisions the team recorded rather than a summary reconstructed from memory.

[Decks and Briefs from Governed Documents](https://documentdrivendx.github.io/helix/use/decks-and-briefs/) explains how this works.

## Read more

The [Principles](https://documentdrivendx.github.io/helix/why/principles/) page explains the five ideas that guide HELIX: human authority, evidence, linked artifacts, intent, and execution feedback.

[Artifact Types](https://documentdrivendx.github.io/helix/artifact-types/) contains the full catalog of document patterns, while [Artifacts](https://documentdrivendx.github.io/helix/artifacts/) shows how HELIX applies those patterns to its own development. [Concerns](https://documentdrivendx.github.io/helix/concerns/) describes the standards that carry across activities, and [Research Foundations](https://documentdrivendx.github.io/helix/research/) collects the research and sources behind the methodology.

When you are ready to apply the method, [Use HELIX](https://documentdrivendx.github.io/helix/use/) covers installation, the first project artifacts, runtime choices, and the first artifact review.

