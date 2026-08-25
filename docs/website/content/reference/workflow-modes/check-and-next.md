---
title: "Check And Next"
slug: check-and-next
weight: 130
generated: true
---

Generated from [`skills/helix/SKILL.md`](https://github.com/DocumentDrivenDX/helix/blob/main/skills/helix/SKILL.md), the HELIX skill. Edit the skill, not this page.

Use when the safe next action is ambiguous, when the user asks "what's
next" / "what's blocked" / "plan the change", or when a single ask
straddles two or more flows declared in the marker (e.g. the prompt
names a data-pipeline artifact whose blocker is an infra prerequisite).

1. Inspect the queue, governing artifacts, and known blockers.
2. Decide conservatively among design, alignment, backfill, polish, runtime
   handoff, wait, guidance, or stop.
3. Do not dispatch another workflow silently.
4. When recommending the next action against a specific gap, name it using
   the §Align gap-to-implementation handoff shape: destination artifact
   type, deliverable shape, suggested next workflow mode, and evidence
   references (paths plus line numbers). Never prescribe a CLI command.
5. If missing tracked work is discovered, create or recommend explicit work
   before returning the next action.

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
3. **Fan out to prerequisite flows.** For each cross-flow
   prerequisite the owner-flow surfaces (e.g. the monitoring-setup
   prose says "dashboard URL needs DNS"; the PRD's acceptance
   criteria require a new VPC), read that prerequisite flow's scoped
   artifacts before drafting the prerequisite-flow action. Each active flow
   that owns part of the answer gets its own scoped artifact read and its own
   handoff in the response.
4. **For a multi-flow status query** ("what's blocked across the
   project?", "what's next?"), inspect every relevant flow listed in the
   marker before reporting per-flow status. Answering from generic prose alone
   without reading the scoped artifacts is the failure mode this rule prevents.

Cross-flow response shape (always emit all three):

- **Named upstream artifacts and their state.** A list of the
  artifacts the answer depends on, each annotated `exists` (with
  path + frontmatter `status:` if present) or `missing` (with the
  graph node that says it should exist). Example:
  `pipelines/customer-events/monitoring-setup.md` (exists,
  status: in-progress); `infra/dns/customer-events.tf` (missing,
  required by monitoring-setup prose).
- **Cross-flow prerequisites.** Name each prerequisite as
  "`<owner-flow>` needs `<prerequisite-flow>` to <verb> <object>
  before `<owner-flow>` can <ship-verb> <artifact>". Example:
  "helix-data needs helix-infra to provision the DNS record for
  `customer-events.metrics.example.com` before helix-data can mark
  monitoring-setup ready."
- **Concrete next action per flow.** For each flow with an action
  pending, emit a §Align gap-to-implementation handoff: destination
  artifact type (e.g. `network-iac` under `infra/`), the flow's domain lane
  when relevant, suggested workflow mode or runtime handoff, and evidence paths
  with line numbers (e.g. `pipelines/customer-events/monitoring-setup.md:20`).
  Never prescribe a CLI command; the operator chooses dispatch.

Do not skip owner-flow resolution because the prompt is short or the
prerequisite verb is loud. Do not collapse multiple flows into a single
undifferentiated answer.
