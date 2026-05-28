---
title: Platforms
weight: 5
---

HELIX is portable methodology content: artifact templates, an artifact-type
schema, and an alignment/planning skill. A platform is the runtime around that
content. It may provide a tracker, agent harness, review workflow, evidence
store, or only a conversational interface.

The same HELIX artifact stack can move across platforms because the core
contract is plain Markdown plus a small amount of frontmatter.

## Boundary: method first, runtime second

HELIX's public spine is the [artifact-type catalog](/artifact-types/), the
[worked HELIX artifacts](/artifacts/), and the [portable skill](/skills/) that
keeps them aligned. Platforms are integration choices around that spine.

DDx is the reference runtime because it demonstrates tracker-backed execution,
queueing, and evidence capture. It is not required to adopt HELIX, and the
methodology should remain understandable without installing DDx.

## Choose the amount of runtime you want

{{< cards >}}
  {{< card link="#ddx" title="DDx" subtitle="Reference integration with tracker, queue, agent execution, and evidence capture." icon="terminal" >}}
  {{< card link="#claude-code" title="Claude Code" subtitle="Use HELIX skills directly in an agent session while keeping artifacts in the repo." icon="sparkles" >}}
  {{< card link="#codex" title="Codex" subtitle="Use HELIX as repository guidance for code-focused agent sessions and reviews." icon="code" >}}
  {{< card link="#databricks" title="Databricks" subtitle="Use HELIX artifacts and alignment planning around data and analytics engineering work." icon="database" >}}
{{< /cards >}}

## Decision matrix

Choose the platform by the operating contract you need, not by where HELIX
"lives." HELIX lives in the artifacts. The platform only decides how planning,
execution, review, and evidence are routed.

| Platform | Best fit | Runtime owns | You still own | Avoid when |
| --- | --- | --- | --- | --- |
| DDx | Queue-backed delivery with traceable work, claims, dependencies, and evidence | Tracker, ready queue, bounded execution loop, measurement records | Product judgment, artifact authority, review decisions | You only need occasional planning or conversational review |
| Claude Code | Interactive artifact planning, design refinement, and repo-local edits | Agent session, skill invocation, file edits under human steering | Scope control, acceptance criteria, final review | You need durable queue semantics across many workers |
| Codex | Code-focused implementation and review against repository guidance | Terminal-oriented agent work, patching, code review, local reasoning | Bead scope, validation choices, merge readiness | The work is mostly product discovery with no code or artifact changes |
| Databricks | Data products, notebooks, jobs, analytics apps, and platform engineering | Domain runtime, notebooks/jobs, workspace execution, data evidence | Markdown artifact authority, promotion criteria, governance | You expect HELIX to replace Databricks workflows or permissions |
| Manual or mixed | High-judgment planning, small teams, or staged adoption | Human coordination and selected agent sessions | The full operating loop and evidence discipline | Nobody is accountable for keeping artifacts current |

If you are unsure, start manually for one change, add Claude Code or Codex for
agent assistance, then adopt DDx only when queueing and evidence capture are
worth the additional runtime structure.

## DDx

DDx is the reference runtime integration for HELIX. Use it when you want HELIX
artifacts connected to a local tracker, dependency-aware work queue, agent
execution harness, and evidence model.

DDx is useful for teams that want repeatable execution around the artifact
stack: work items, claims, dependencies, reviews, and measured outcomes.

{{< cards >}}
  {{< card link="/use/ddx-runtime" title="Using HELIX with DDx" subtitle="Install and operate the reference runtime integration." icon="terminal" >}}
{{< /cards >}}

### First 30 minutes with DDx

1. Put the governing HELIX artifacts in the repository, or generate the
   initial stack from the templates.
2. Run `ddx bead ready` to see whether execution work is already shaped.
3. Convert any broad plan into bounded beads before starting implementation.
4. Claim one bead with `ddx bead update <id> --claim`.
5. Execute only that bead, record validation or evidence on the bead, then
   close it when the acceptance criteria are satisfied.

### DDx usage contract

DDx is allowed to own queue mechanics: claims, dependencies, ready-work
detection, execution loops, and measurement records. It should not become the
product spine. Product direction still flows through HELIX artifacts, and
runtime evidence should point back to those artifacts instead of replacing
them.

## Claude Code

Claude Code can use HELIX as a skill package and artifact discipline. The
common pattern is direct agent interaction: ask Claude to read the governing
artifacts, invoke the HELIX alignment/planning skill, and apply the resulting
plan to Markdown files or code changes.

Use this path when your team wants interactive steering and review, but does
not need a runtime-owned queue for every change.

In this mode, treat the HELIX skill as the product surface and any historical
`helix-*` wrappers as compatibility aids, not methodology requirements.

### First 30 minutes with Claude Code

1. Open a repo that contains the HELIX artifact stack.
2. Ask Claude to read the governing artifacts before proposing work.
3. Invoke the HELIX alignment/planning skill for the intended scope.
4. Review the plan before allowing edits.
5. Keep the change bounded to the reviewed scope and update artifacts when the
   implementation changes the product contract.

### Claude Code usage contract

Claude Code is strongest as an interactive planning and editing partner. Use it
for alignment reviews, design refinement, artifact maintenance, and bounded
implementation passes. Do not treat a chat transcript as the system of record:
accepted decisions need to land in the Markdown artifacts, tracker, or code.

## Codex

Codex can use HELIX as repository-native guidance for implementation, review,
and documentation work. The artifact stack gives the agent a stable authority
order: product vision first, then requirements, designs, tests, implementation
plans, and code.

Use this path when most work happens in code review or terminal-driven agent
sessions, and you want HELIX to supply durable context rather than a separate
platform.

### First 30 minutes with Codex

1. Identify the bead, pull request, or explicit scope Codex should operate on.
2. Point Codex at the relevant HELIX artifacts and acceptance criteria.
3. Require a bounded edit plan before file changes.
4. Let Codex modify only the files in scope.
5. Decide explicitly which checks Codex may run, and record any skipped
   validation in the handoff.

### Codex usage contract

Codex should use HELIX as authority for repository work: code changes,
implementation notes, documentation edits, and reviews. It should not invent
scope beyond the bead or reviewed plan. When Codex discovers missing product
direction, the correct output is an artifact update or follow-up work item,
not silent expansion of the implementation.

## Databricks

Databricks teams can use HELIX around data products, analytics apps, notebooks,
jobs, and platform engineering work. HELIX does not require a particular
source-control or execution substrate; the important part is that the runtime
can read and write the governing Markdown artifacts and surface an alignment
plan for review.

Use this path when the implementation runtime is already Databricks, but the
team still needs durable intent, design, testing, deployment, and iteration
artifacts.

### First 30 minutes with Databricks

1. Choose the product surface: notebook, job, dashboard, pipeline, model, or
   platform capability.
2. Capture the durable intent in HELIX artifacts outside the transient
   workspace state.
3. Define the acceptance evidence: data checks, job runs, query outputs,
   dashboard review, model metrics, or deployment gates.
4. Ask the agent or operator to produce an alignment plan before changing
   notebooks, jobs, or pipelines.
5. Promote only changes whose runtime evidence can be traced back to the
   artifact contract.

### Databricks usage contract

Databricks owns domain execution: clusters, notebooks, jobs, permissions,
catalogs, data quality checks, and workspace-specific deployment mechanics.
HELIX owns the durable planning record. Keep design, acceptance, and promotion
criteria in Markdown so they remain reviewable outside the Databricks runtime.

## Manual or mixed operation

You can also use HELIX without a dedicated platform. Keep the artifacts in
your repository, ask an agent to apply the alignment skill against them, and
review the proposed plan before any implementation work begins.

Many teams will mix modes: manual planning for high-judgment changes, Claude
or Codex for interactive implementation, DDx for queued execution, and
Databricks for domain-specific runtime work.

When mixing modes, keep the artifact catalog and alignment skill as the shared
contract. Let each runtime own only the mechanics it is good at.

### First 30 minutes manually

1. Pick one change and name the governing artifact that justifies it.
2. Write or update the requirement, design note, or acceptance criteria before
   implementation starts.
3. Ask an agent for an alignment check, or do the same review manually against
   the artifact-type catalog.
4. Choose the execution surface: human edit, Claude Code, Codex, DDx, or
   Databricks.
5. Record the outcome where the next operator will look first: artifact,
   tracker, pull request, or release note.

### Manual or mixed usage contract

Manual operation is valid when judgment matters more than automation. Mixed
operation is valid when different runtimes are best for different activities. The
non-negotiable rule is that the artifacts remain the shared source of truth:
each runtime may add evidence or edits, but none should become a private fork
of the plan.
