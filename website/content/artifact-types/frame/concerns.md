---
title: "Project Concerns"
linkTitle: "Project Concerns"
slug: concerns
activity: "Frame"
artifactRole: "core"
weight: 12
generated: true
---

## Purpose

Project Concerns declare the cross-cutting context that should travel with
downstream work. Their unique job is to keep recurring technology, quality,
data, security, UX, operations, and convention guidance attached to the areas
where it matters.

Concerns are not principles. Principles guide judgment when two valid options
compete. Concerns name active domains whose practices must be considered during
design, test, implementation, and review. Concerns are not ADRs either: an ADR
records a specific decision, while a concern keeps the resulting practices
available to future work.

## Example

<details open>
<summary>Show a worked example of this artifact</summary>

``````markdown
---
ddx:
  id: example.concerns.depositmatch
  depends_on:
    - example.product-vision.depositmatch
    - example.prd.depositmatch
    - example.principles.depositmatch
  review:
    self_hash: 34738dd02d95489bcc3c00b5be15b630ae9fb15ab4f99f45d0ec1ecd1d3f1c6e
    deps:
      example.prd.depositmatch: c9c24e1694af4548a6deaad8d92059e365da110148bd9adc44d8640dff9770a4
      example.principles.depositmatch: bb37a1addd5c152f068dd5c416b6a4ae217847242d0d1b7f9e64406b671de0ed
      example.product-vision.depositmatch: 8abbb2fcb552b536f07829f57d91ef3ae8dbf52a6066955222e83d196b59b5ae
    reviewed_at: "2026-05-15T04:11:24Z"
---

# Project Concerns

Project Concerns declare active cross-cutting context for DepositMatch. They are
not principles, requirements, ADRs, test plans, or implementation tasks.

## Active Concerns

| Concern | Source | Areas | Why Active | Key Practices |
|---------|--------|-------|------------|---------------|
| `csv-import-integrity` | project-local | `area:ui`, `area:api`, `area:data` | CSV import is the only v1 ingestion path, and bad mappings would corrupt review trust. | Validate required columns, preserve source row identity, save per-client mappings, and reject ambiguous files before matching. |
| `financial-data-security` | project-local | `area:api`, `area:data`, `area:infra` | Deposit and invoice data include customer financial records. | Encrypt customer financial data at rest, exclude financial fields from analytics, and keep audit logs access-controlled. |
| `reviewer-auditability` | project-local | `area:ui`, `area:api`, `area:data` | Trust depends on visible evidence, reviewer attribution, and reversible corrections. | Show evidence before acceptance, record reviewer and timestamp, preserve correction history, and avoid destructive edits. |
| `a11y-wcag-aa` | library | `area:ui` | Reviewers may work through dense queues for long sessions. | Use accessible table controls, keyboard review actions, visible focus states, and non-color-only confidence indicators. |

## Project Overrides

| Concern | Practice | Override | Authority |
|---------|----------|----------|-----------|
| `a11y-wcag-aa` | Generic form and page guidance | Apply WCAG AA patterns specifically to reconciliation queues, import mapping tables, and exception triage controls. | Needs ADR before launch if queue interaction patterns diverge from standard controls. |

## Area Labels

This project uses the following area labels for concern scoping:

- `area:ui` — reviewer workspace, import mapping, match review, exception queue
- `area:api` — upload, matching, review, exception, export endpoints
- `area:data` — deposit, invoice, match, evidence, exception, audit storage
- `area:infra` — hosting, secrets, backups, deployment, monitoring
- `area:testing` — import fixtures, matching confidence checks, audit-log verification

## Concern Conflicts

| Conflict | Resolution |
|----------|------------|
| `csv-import-integrity` vs. reviewer speed | Reject bad files early. Do not let speed bypass validation that protects source-row identity. |
| `financial-data-security` vs. reviewer-auditability | Keep audit trails complete, but redact financial fields from analytics and restrict audit-log access. |
| `a11y-wcag-aa` vs. dense queue efficiency | Preserve keyboard speed and visual density only when focus, labels, and non-color indicators remain accessible. |
``````

</details>

## Reference

<table class="helix-reference-table">
<tbody>
<tr><th>Activity</th><td><a href="/reference/glossary/activities/"><strong>Frame</strong></a> — Define what the system should do, for whom, and how success will be measured.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/01-frame/concerns.md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>HELIX documents</th><td><a href="https://github.com/DocumentDrivenDX/helix/blob/main/docs/helix/01-frame/concerns.md"><code>docs/helix/01-frame/concerns.md</code></a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Concerns Selection Prompt

Guide the user through selecting project concerns from the library and
declaring any project-specific concerns or overrides.

## Purpose

Project Concerns declare the cross-cutting context that should travel with
downstream work. Their unique job is to keep recurring technology, quality,
data, security, UX, operations, and convention guidance attached to the areas
where it matters.

Concerns are not principles. Principles guide judgment when two valid options
compete. Concerns name active domains whose practices must be considered during
design, test, implementation, and review. Concerns are not ADRs either: an ADR
records a specific decision, while a concern keeps the resulting practices
available to future work.

## Reference Anchors

Use these local resource summaries as grounding:

- `docs/resources/microsoft-azure-well-architected-framework.md` grounds
  cross-cutting quality and operational concerns as actionable practices,
  risks, and tradeoffs.
- `docs/resources/sei-quality-attribute-scenarios.md` grounds quality
  attributes as concrete scenarios and practices, not bare labels.

## Approach

1. Inspect the Product Vision, PRD, Principles, architecture notes, existing
   repository structure, dependencies, deployment files, and current concern
   library at `workflows/concerns/`.

2. List available concerns from `workflows/concerns/`
   grouped by category. Include project-local candidate concerns only when the
   repo clearly has a recurring cross-cutting domain that the library does not
   cover.

3. For each category, infer what you can from the repo and ask only for
   unresolved choices:
   - Tech stack: &quot;What language, runtime, and package manager does this
     project use?&quot;
   - Data: &quot;What database or data layer?&quot;
   - Infrastructure: &quot;Where will this deploy?&quot;
   - Quality: &quot;Do you need accessibility (a11y), internationalization (i18n),
     or observability (o11y) support?&quot;

4. For each selected concern:
   - State why it is active for this project.
   - Declare the area labels where it applies.
   - Capture the key practices that downstream work needs.
   - If overriding library practices, cite the governing ADR when available.
   - If no ADR exists for a significant override, mark it as needing an ADR.

5. Declare the project&#x27;s area labels — which `area:*` labels will work items use?
   The default set is: `ui`, `api`, `data`, `infra`, `cli`.

6. Check for practice conflicts between selected concerns and resolve them.

7. Write `docs/helix/01-frame/concerns.md`.

## Key Rules

- Concerns are composable. Selecting multiple is normal and expected.
- A concern must be active. Do not include a domain just because it is
  generally good practice.
- Project overrides take full precedence over library practices.
- Every override should reference a governing ADR when possible.
- The area taxonomy declared here controls which concerns are injected
  into which work items via `&lt;context-digest&gt;`.
- If a concern describes product behavior, move it to the PRD or a feature
  spec.
- If a concern records a one-time technical choice, move it to an ADR.
- If a concern describes build order, move it to the implementation plan.</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---
ddx:
  id: concerns
---

# Project Concerns

Project Concerns declare active cross-cutting context for downstream work. They
are not principles, requirements, ADRs, test plans, or implementation tasks.

## Active Concerns

&lt;!-- Select from workflows/concerns/ or declare project-local
     entries. Include only concerns that change downstream work across more
     than one artifact or implementation area. --&gt;

| Concern | Source | Areas | Why Active | Key Practices |
|---------|--------|-------|------------|---------------|
| [concern-name] | [library or project-local] | `area:*` | [Why this changes downstream work] | [Practices downstream work must consider] |

## Project Overrides

&lt;!-- Override specific library practices only when the project has a real reason.
     Cite the governing ADR when available. --&gt;

| Concern | Practice | Override | Authority |
|---------|----------|----------|-----------|
| [concern-name] | [library practice] | [project-specific override] | [ADR-NNN or &quot;Needs ADR&quot;] |

## Area Labels

This project uses the following area labels for concern scoping:

&lt;!-- Declare which area labels work items use. Concerns are injected into
     downstream context based on matching labels against each concern&#x27;s area
     scope. --&gt;

- `area:ui` — user-facing interfaces
- `area:api` — backend services and endpoints
- `area:data` — database, storage, data pipeline
- `area:infra` — deployment, CI/CD, infrastructure
- `area:cli` — command-line tools

## Concern Conflicts

&lt;!-- Resolve conflicts between active concerns. --&gt;

| Conflict | Resolution |
|----------|------------|
| [Concern A] vs. [Concern B] | [How downstream work should decide] |</code></pre></details></td></tr>
</tbody>
</table>
