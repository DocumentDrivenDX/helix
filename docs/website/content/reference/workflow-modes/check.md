---
title: "Check And Next"
slug: check
weight: 30
generated: true
---

Generated from [`workflows/modes/check.md`](https://github.com/DocumentDrivenDX/helix/blob/main/workflows/modes/check.md), the mode contract the HELIX skill loads. Edit that file, not this page.

Use when the safe next action is ambiguous, when the user asks "what's
next" / "what's blocked" / "plan the change", or when a single ask
straddles two or more flows declared in the marker (e.g. the prompt
names a data-pipeline artifact whose blocker is an infra prerequisite).

1. Inspect the requested scope, relevant governing artifacts, and known
   blockers. Consult work tracking only when it informs the question.
2. Decide conservatively among design, alignment, backfill, polish, runtime
   handoff, wait, guidance, or stop.
3. Do not dispatch another workflow silently.
4. Explain the recommended next step and its evidence; never prescribe a CLI
   command.

## Flow disambiguation

Applies at activation (SKILL.md §Activation Discipline step 3) before any
routing:

- **Several distinct flows and an ambiguous verb** (for example `helix` and
  `helix-infra`, prompt "plan the rollout"): resolve cwd-under-root →
  `defaults.flow` → single entry. If none resolves, emit the disambiguation
  banner naming both candidate flows with their roots and ask which applies.
  Do not silently pick one, and do not route to the infra lane under `helix`
  because the prompt contains an infra-adjacent noun.
- **Several helix instances** (`instance:` values with different roots): if
  cwd lies inside exactly one root, choose it and say so; otherwise emit the
  banner listing instances and roots, then stop until the operator chooses.

## Cross-flow ask — owner-flow first, then prerequisite fan-out

A **cross-flow ask** is any prompt whose answer requires consulting more
than one flow in the marker. Three shapes recur:

- **Single-artifact ask whose blocker lives in another flow.** Example:
  "The monitoring dashboard needs a DNS record. Set this up." The
  monitoring-setup artifact is owned by `helix-data` (it lives under
  `pipelines/<scope>/` per the marker); the DNS record is owned by
  `helix-infra`. The data flow is the **owner-flow** because it owns
  the artifact named in the prompt. Infra is a **prerequisite-flow**
  that must satisfy a precondition before the data-flow item ships.
- **Multi-flow status query.** Example: "What's blocked across the
  project?" / "What's next?" against a marker with two or more flows.
  Every active flow in the marker is a candidate owner — none can be
  silently dropped.
- **PRD-needs-infra ask.** Example: "The PRD needs new infra — plan
  it." Product owns the PRD (owner-flow); infra owns the provisioning
  artifact downstream. The PRD edit and the infra plan are TWO
  artifacts in TWO flows, linked by a cross-flow edge.

Cross-flow contract (every cross-flow ask):

1. **Resolve the owner flow first.** Identify the flow whose `root:` owns
   the named artifact (or the artifact the prompt's noun phrase most
   directly names). Do not jump straight to the prerequisite flow because
   its verb (DNS, deploy, provision) appears in the prompt. The artifact's
   home flow wins.
2. **Read the owner-flow's named upstream artifacts.** From the
   marker's `root:` for the owner-flow, locate and Read the artifact
   the prompt references (e.g. `monitoring-setup.md`,
   `data-product-brief.md`, `prd-*.md`) BEFORE proposing any action.
   For each upstream named in `ddx.links:` or `informs` edges that
   the answer depends on, Read it too. Catalogue which artifacts
   exist (with path + status from frontmatter) and which are missing.
3. **Read relevant prerequisite flows.** When a governing artifact identifies a
   prerequisite in another flow, read that flow's scoped artifact before
   recommending work there. Give a next step for each flow that owns part of
   the requested outcome.
4. **For a multi-flow status query** ("what's blocked across the
   project?", "what's next?"), inspect every relevant flow listed in the
   marker before reporting per-flow status. Answering from generic prose alone
   without reading the scoped artifacts is the failure mode this rule prevents.

Answer concisely by naming the owner flow, relevant evidence, any prerequisite
flow that affects the result, and the recommended next action. Mention artifact
status when it changes that recommendation.

Do not skip owner-flow resolution because the prompt is short or the
prerequisite verb is loud. Do not collapse multiple flows into a single
undifferentiated answer.

## Source-Code Boundaries

Check the `modularity-and-encapsulation` source-code baseline in `workflows/references/concern-resolution.md`. Missing selection, map, or checker evidence blocks source feature readiness; recommend explicit adoption/design work. Legacy artifact validity remains separate. Check does not silently re-select concerns or edit existing adoption decisions.
