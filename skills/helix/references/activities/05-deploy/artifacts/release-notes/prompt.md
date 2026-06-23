# Release Notes Prompt

Create release-specific notes for one shipped rollout.

## Purpose

Release Notes are the **audience-facing release communication artifact**. Their
unique job is to tell users, operators, support, and internal stakeholders what
actually shipped, who is affected, what action is required, what is known to be
limited or risky, and where to find deeper operational details.

Release Notes are not a deployment checklist, runbook, changelog, launch plan,
or roadmap update. They communicate release impact after scope is known.

## Reference Anchors

Use this local resource summary as grounding:

- `docs/resources/keep-a-changelog.md` grounds human-readable release
  communication grouped by user-impacting change.

## Required Inputs
- release scope, version, and date
- shipped features, fixes, and operator-visible changes
- breaking changes, migrations, or rollout caveats
- known issues and support or rollback guidance
- links to deeper docs such as feature docs, deployment checklist, or runbook

## Produced Output
- `docs/helix/05-deploy/release-notes.md`

## Focus

Keep the document tightly scoped to what actually shipped in this release.
Write for readers who need to understand impact quickly: what changed, who is
affected, and what action they need to take.

Differentiate release notes from adjacent surfaces:

- `deployment-checklist` decides whether rollout can proceed
- `runbook` explains operator response procedures
- `CHANGELOG.md` records repository history
- `release-notes` communicate the release itself to users and operators

## Boundary Test

| If you are writing... | Put it in... |
|---|---|
| Go/no-go checks and rollback triggers | Deployment Checklist |
| Incident response or operational procedures | Runbook |
| Raw commit/PR history | Changelog |
| User/operator impact, actions, caveats, and support paths | Release Notes |
| Future roadmap promises | Product planning artifacts |

Lead with the most important highlights, then make required actions, breaking
changes, migrations, and known issues explicit. If no action is required or no
breaking changes exist, say that clearly.

Do not produce roadmap filler, a GTM plan, or a cross-functional launch
checklist. Launch coordination belongs in linked `activity:deploy` tracker work
plus the adjacent deploy artifacts (`deployment-checklist`, `monitoring-setup`,
and `runbook`), not inside release notes.

## Completion Criteria
- [ ] Release scope, audience, and channels are explicit
- [ ] Highlights and change summaries are limited to what actually shipped
- [ ] Required user or operator actions are explicit, or the document states none
- [ ] Breaking changes, migration guidance, and known issues are clear when relevant
- [ ] References point readers to deeper docs or support paths when needed

Use the template at `workflows/activities/05-deploy/artifacts/release-notes/template.md`.
