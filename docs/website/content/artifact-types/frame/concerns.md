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
<tr><th>Activity</th><td><a href="../../../reference/glossary/activities/"><strong>Frame</strong></a> — Define what the system should do, for whom, and how success will be measured.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/01-frame/concerns.md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>HELIX documents</th><td><a href="https://github.com/DocumentDrivenDX/helix/blob/main/docs/helix/01-frame/concerns.md"><code>docs/helix/01-frame/concerns.md</code></a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Concerns Selection Prompt&#10;&#10;Guide the user through selecting project concerns from the library and&#10;declaring any project-specific concerns or overrides.&#10;&#10;## Purpose&#10;&#10;Project Concerns declare the cross-cutting context that should travel with&#10;downstream work. Their unique job is to keep recurring technology, quality,&#10;data, security, UX, operations, and convention guidance attached to the areas&#10;where it matters.&#10;&#10;Concerns are not principles. Principles guide judgment when two valid options&#10;compete. Concerns name active domains whose practices must be considered during&#10;design, test, implementation, and review. Concerns are not ADRs either: an ADR&#10;records a specific decision, while a concern keeps the resulting practices&#10;available to future work.&#10;&#10;## Reference Anchors&#10;&#10;Use these local resource summaries as grounding:&#10;&#10;- `docs/resources/microsoft-azure-well-architected-framework.md` grounds&#10;  cross-cutting quality and operational concerns as actionable practices,&#10;  risks, and tradeoffs.&#10;- `docs/resources/sei-quality-attribute-scenarios.md` grounds quality&#10;  attributes as concrete scenarios and practices, not bare labels.&#10;&#10;## Approach&#10;&#10;1. Inspect the Product Vision, PRD, Principles, architecture notes, existing&#10;   repository structure, dependencies, deployment files, and current concern&#10;   library at `workflows/concerns/`.&#10;&#10;2. List available concerns from `workflows/concerns/`&#10;   grouped by category. Include project-local candidate concerns only when the&#10;   repo clearly has a recurring cross-cutting domain that the library does not&#10;   cover.&#10;&#10;3. For each category, infer what you can from the repo and ask only for&#10;   unresolved choices:&#10;   - Tech stack: &quot;What language, runtime, and package manager does this&#10;     project use?&quot;&#10;   - Data: &quot;What database or data layer?&quot;&#10;   - Infrastructure: &quot;Where will this deploy?&quot;&#10;   - Quality: &quot;Do you need accessibility (a11y), internationalization (i18n),&#10;     or observability (o11y) support?&quot;&#10;&#10;4. For each selected concern:&#10;   - State why it is active for this project.&#10;   - Declare the area labels where it applies.&#10;   - Capture the key practices that downstream work needs.&#10;   - If overriding library practices, cite the governing ADR when available.&#10;   - If no ADR exists for a significant override, mark it as needing an ADR.&#10;&#10;5. Declare the project&#x27;s area labels — which `area:*` labels will work items use?&#10;   The default set is: `ui`, `api`, `data`, `infra`, `cli`.&#10;&#10;6. Check for practice conflicts between selected concerns and resolve them.&#10;&#10;7. Write `docs/helix/01-frame/concerns.md`.&#10;&#10;## Key Rules&#10;&#10;- Concerns are composable. Selecting multiple is normal and expected.&#10;- A concern must be active. Do not include a domain just because it is&#10;  generally good practice.&#10;- Project overrides take full precedence over library practices.&#10;- Every override should reference a governing ADR when possible.&#10;- The area taxonomy declared here controls which concerns are injected&#10;  into which work items via `&lt;context-digest&gt;`.&#10;- If a concern describes product behavior, move it to the PRD or a feature&#10;  spec.&#10;- If a concern records a one-time technical choice, move it to an ADR.&#10;- If a concern describes build order, move it to the implementation plan.</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---&#10;ddx:&#10;  id: concerns&#10;---&#10;&#10;# Project Concerns&#10;&#10;Project Concerns declare active cross-cutting context for downstream work. They&#10;are not principles, requirements, ADRs, test plans, or implementation tasks.&#10;&#10;## Active Concerns&#10;&#10;&lt;!-- Select from workflows/concerns/ or declare project-local&#10;     entries. Include only concerns that change downstream work across more&#10;     than one artifact or implementation area. --&gt;&#10;&#10;| Concern | Source | Areas | Why Active | Key Practices |&#10;|---------|--------|-------|------------|---------------|&#10;| [concern-name] | [library or project-local] | `area:*` | [Why this changes downstream work] | [Practices downstream work must consider] |&#10;&#10;## Project Overrides&#10;&#10;&lt;!-- Override specific library practices only when the project has a real reason.&#10;     Cite the governing ADR when available. --&gt;&#10;&#10;| Concern | Practice | Override | Authority |&#10;|---------|----------|----------|-----------|&#10;| [concern-name] | [library practice] | [project-specific override] | [ADR-NNN or &quot;Needs ADR&quot;] |&#10;&#10;## Area Labels&#10;&#10;This project uses the following area labels for concern scoping:&#10;&#10;&lt;!-- Declare which area labels work items use. Concerns are injected into&#10;     downstream context based on matching labels against each concern&#x27;s area&#10;     scope. --&gt;&#10;&#10;- `area:ui` — user-facing interfaces&#10;- `area:api` — backend services and endpoints&#10;- `area:data` — database, storage, data pipeline&#10;- `area:infra` — deployment, CI/CD, infrastructure&#10;- `area:cli` — command-line tools&#10;&#10;## Concern Conflicts&#10;&#10;&lt;!-- Resolve conflicts between active concerns. --&gt;&#10;&#10;| Conflict | Resolution |&#10;|----------|------------|&#10;| [Concern A] vs. [Concern B] | [How downstream work should decide] |</code></pre></details></td></tr>
</tbody>
</table>
