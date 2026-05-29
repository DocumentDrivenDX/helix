---
title: "Release Notes"
linkTitle: "Release Notes"
slug: release-notes
activity: "Deploy"
artifactRole: "core"
weight: 11
generated: true
---

## Purpose

Release Notes are the **audience-facing release communication artifact**. Their
unique job is to tell users, operators, support, and internal stakeholders what
actually shipped, who is affected, what action is required, what is known to be
limited or risky, and where to find deeper operational details.

Release Notes are not a deployment checklist, runbook, changelog, launch plan,
or roadmap update. They communicate release impact after scope is known.

## Example

<details open>
<summary>Show a worked example of this artifact</summary>

``````markdown
---
ddx:
  id: example.release-notes.depositmatch.csv-import
  depends_on:
    - example.deployment-checklist.depositmatch.csv-import
    - example.implementation-plan.depositmatch
  review:
    self_hash: 3f1390445de6ce94fda9daf662dce73605ddf07d6ea73f7f0acde563b9af7360
    deps:
      example.deployment-checklist.depositmatch.csv-import: 02e9e7c9c29b4a335e0e2eceacaaaa6673018042db2a706f89293ab6f58abcbf
      example.implementation-plan.depositmatch: 8f48b07ab604fe52786de7648f7ab37da251cfade0ea38bb4e802082d4f977de
    reviewed_at: "2026-05-15T04:11:24Z"
---

# Release Notes - DepositMatch CSV Import v1

## Release Scope

- Release identifier or version: `release-2026-05-12-csv-import`
- Release date: 2026-05-12
- Rollout window or environment: staged pilot rollout
- Release owner: Engineering lead
- Source commit or build: `release-2026-05-12-csv-import`

## Audience and Channels

| Audience | Why they care | Delivery channel |
|----------|---------------|------------------|
| Pilot reconciliation leads | They can start weekly reconciliation by uploading bank and invoice CSV files for one client. | In-app release note and pilot email |
| Support | They need to recognize CSV upload, file-type, and storage errors. | Support runbook update and team channel |
| Operators | They need to monitor upload health and disable `csvImportV1` if triggers fire. | Deployment checklist and on-call channel |

## Highlights

- Reviewers can create a draft import session by uploading one bank deposit CSV
  and one invoice export CSV for a client.
- DepositMatch rejects non-CSV files before parsing and explains which file
  must be replaced.
- Accepted uploads preserve source file metadata needed for later mapping,
  validation, evidence, and audit trails.

## Required Actions Summary

- Users: no account action required; pilot users should export bank and invoice
  CSV files before starting an import.
- Operators: monitor upload error rate, p95 upload latency, and log-redaction
  checks during pilot rollout.
- Support: route CSV file-type problems to the upload troubleshooting path;
  do not ask users to send raw financial CSVs over email.

## Changes and Fixes

### New or Improved

| Area | What changed | Who is affected |
|------|--------------|-----------------|
| CSV import | Added draft import-session creation for one bank CSV and one invoice CSV. | Pilot reconciliation leads |
| Upload errors | Added structured non-CSV rejection before parsing. | Pilot users and support |
| Source metadata | Recorded file name, source type, size, and upload context for accepted files. | Reviewers, support, operators |

### Fixes

| Issue or symptom | Resolution | User or operator impact |
|------------------|------------|-------------------------|
| None in this release | This is the first pilot release of CSV import. | N/A |

## Breaking Changes and Required Actions

There are no breaking changes and no required migrations for users. Operators
must complete the deployment checklist before enabling `csvImportV1` for pilot
firms.

| Change | Impact | Required action | Deadline or trigger |
|--------|--------|-----------------|---------------------|
| New `import_sessions` and `import_files` tables | Operator-visible migration | Verify migration during staged rollout | Before enabling `csvImportV1` |

## Migration or Rollback Guidance

### Upgrade or Migration

1. Deploy API and web build with `csvImportV1` disabled.
2. Apply `import_sessions` and `import_files` migration.
3. Enable `csvImportV1` for one pilot firm after staging checks pass.

### Rollback or Hold Guidance

- Pause rollout when: upload endpoint 5xx exceeds 1% for 15 minutes, any raw
  CSV row value appears in logs, or any partial metadata commit is observed.
- Roll back using: deployment checklist rollback triggers.
- Ask for help in: on-call channel for operators; pilot-support channel for
  user questions.

## Known Issues and Support

| Issue | Who is affected | Workaround or next step |
|------|------------------|-------------------------|
| Column mapping is not part of this release note scope | Pilot reviewers | Mapping review is the next step after upload and is covered by follow-on release notes. |
| Bank feeds and accounting API sync are not available | Pilot firms | Continue exporting CSV files from existing systems. |
| Uploads larger than 10 MB are rejected | Pilot reviewers | Export a smaller date range or split the file before upload. |

## References

- Deployment checklist: `example.deployment-checklist.depositmatch.csv-import`
- Feature specification: `example.feature-specification.depositmatch.csv-import`
- API contract: `example.contract.depositmatch.import-session-api`
- Support path: pilot-support channel
``````

</details>

## Reference

<table class="helix-reference-table">
<tbody>
<tr><th>Activity</th><td><a href="../../../reference/glossary/activities/"><strong>Deploy</strong></a> — Ship to users with appropriate operational support, monitoring, and rollback plans.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/05-deploy/release-notes.md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>HELIX documents</th><td><a href="https://github.com/DocumentDrivenDX/helix/blob/main/docs/helix/05-deploy/release-notes.md"><code>docs/helix/05-deploy/release-notes.md</code></a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Release Notes Prompt&#10;&#10;Create release-specific notes for one shipped rollout.&#10;&#10;## Purpose&#10;&#10;Release Notes are the **audience-facing release communication artifact**. Their&#10;unique job is to tell users, operators, support, and internal stakeholders what&#10;actually shipped, who is affected, what action is required, what is known to be&#10;limited or risky, and where to find deeper operational details.&#10;&#10;Release Notes are not a deployment checklist, runbook, changelog, launch plan,&#10;or roadmap update. They communicate release impact after scope is known.&#10;&#10;## Reference Anchors&#10;&#10;Use this local resource summary as grounding:&#10;&#10;- `docs/resources/keep-a-changelog.md` grounds human-readable release&#10;  communication grouped by user-impacting change.&#10;&#10;## Required Inputs&#10;- release scope, version, and date&#10;- shipped features, fixes, and operator-visible changes&#10;- breaking changes, migrations, or rollout caveats&#10;- known issues and support or rollback guidance&#10;- links to deeper docs such as feature docs, deployment checklist, or runbook&#10;&#10;## Produced Output&#10;- `docs/helix/05-deploy/release-notes.md`&#10;&#10;## Focus&#10;&#10;Keep the document tightly scoped to what actually shipped in this release.&#10;Write for readers who need to understand impact quickly: what changed, who is&#10;affected, and what action they need to take.&#10;&#10;Differentiate release notes from adjacent surfaces:&#10;&#10;- `deployment-checklist` decides whether rollout can proceed&#10;- `runbook` explains operator response procedures&#10;- `CHANGELOG.md` records repository history&#10;- `release-notes` communicate the release itself to users and operators&#10;&#10;## Boundary Test&#10;&#10;| If you are writing... | Put it in... |&#10;|---|---|&#10;| Go/no-go checks and rollback triggers | Deployment Checklist |&#10;| Incident response or operational procedures | Runbook |&#10;| Raw commit/PR history | Changelog |&#10;| User/operator impact, actions, caveats, and support paths | Release Notes |&#10;| Future roadmap promises | Product planning artifacts |&#10;&#10;Lead with the most important highlights, then make required actions, breaking&#10;changes, migrations, and known issues explicit. If no action is required or no&#10;breaking changes exist, say that clearly.&#10;&#10;Do not produce roadmap filler, a GTM plan, or a cross-functional launch&#10;checklist. Launch coordination belongs in linked `activity:deploy` tracker work&#10;plus the adjacent deploy artifacts (`deployment-checklist`, `monitoring-setup`,&#10;and `runbook`), not inside release notes.&#10;&#10;## Completion Criteria&#10;- [ ] Release scope, audience, and channels are explicit&#10;- [ ] Highlights and change summaries are limited to what actually shipped&#10;- [ ] Required user or operator actions are explicit, or the document states none&#10;- [ ] Breaking changes, migration guidance, and known issues are clear when relevant&#10;- [ ] References point readers to deeper docs or support paths when needed&#10;&#10;Use the template at `workflows/activities/05-deploy/artifacts/release-notes/template.md`.</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---&#10;ddx:&#10;  id: release-notes&#10;---&#10;&#10;# Release Notes - [Release / Version]&#10;&#10;## Release Scope&#10;&#10;- Release identifier or version: [tag, version, or name]&#10;- Release date: [YYYY-MM-DD]&#10;- Rollout window or environment: [production, staged rollout, region]&#10;- Release owner: [name or role]&#10;- Source commit or build: [SHA, image tag, or build link]&#10;&#10;## Audience and Channels&#10;&#10;| Audience | Why they care | Delivery channel |&#10;|----------|---------------|------------------|&#10;| [end users] | [impact] | [email, docs, in-app, status page] |&#10;| [operators or support] | [impact] | [runbook, team channel, incident channel] |&#10;| [internal stakeholders] | [impact] | [release post, team update] |&#10;&#10;## Highlights&#10;&#10;- [highest-value shipped change]&#10;- [second important change]&#10;- [critical fix or operational improvement]&#10;&#10;## Required Actions Summary&#10;&#10;- Users: [none or required action]&#10;- Operators: [none or required action]&#10;- Support: [none or required action]&#10;&#10;## Changes and Fixes&#10;&#10;### New or Improved&#10;&#10;| Area | What changed | Who is affected |&#10;|------|--------------|-----------------|&#10;| [feature or workflow] | [summary] | [users, operators, admins] |&#10;| [feature or workflow] | [summary] | [users, operators, admins] |&#10;&#10;### Fixes&#10;&#10;| Issue or symptom | Resolution | User or operator impact |&#10;|------------------|------------|-------------------------|&#10;| [bug or failure mode] | [what is fixed] | [why it matters] |&#10;| [bug or failure mode] | [what is fixed] | [why it matters] |&#10;&#10;## Breaking Changes and Required Actions&#10;&#10;If there are no breaking changes or required actions, state that explicitly.&#10;&#10;| Change | Impact | Required action | Deadline or trigger |&#10;|--------|--------|-----------------|---------------------|&#10;| [breaking change] | [who is affected] | [migration or config step] | [before upgrade, after rollout] |&#10;&#10;## Migration or Rollback Guidance&#10;&#10;### Upgrade or Migration&#10;&#10;1. [step one]&#10;2. [step two]&#10;3. [validation step]&#10;&#10;### Rollback or Hold Guidance&#10;&#10;- Pause rollout when: [condition]&#10;- Roll back using: [runbook entrypoint or command]&#10;- Ask for help in: [channel, team, or support path]&#10;&#10;## Known Issues and Support&#10;&#10;| Issue | Who is affected | Workaround or next step |&#10;|------|------------------|-------------------------|&#10;| [known issue] | [audience] | [workaround, mitigation, or ETA] |&#10;| [known issue] | [audience] | [workaround, mitigation, or ETA] |&#10;&#10;## References&#10;&#10;- Deployment checklist: [link]&#10;- Runbook: [link]&#10;- Feature docs or changelog: [link]&#10;- Support or escalation path: [link]</code></pre></details></td></tr>
</tbody>
</table>
