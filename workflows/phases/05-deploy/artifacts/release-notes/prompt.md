# Release Notes Prompt

Create release-specific notes for one shipped rollout.

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

Lead with the most important highlights, then make required actions, breaking
changes, migrations, and known issues explicit. If no action is required or no
breaking changes exist, say that clearly.

Do not produce roadmap filler, a GTM plan, or a cross-functional launch
checklist. Launch coordination belongs in linked `phase:deploy` tracker work
plus the adjacent deploy artifacts (`deployment-checklist`, `monitoring-setup`,
and `runbook`), not inside release notes.

## Completion Criteria
- [ ] Release scope, audience, and channels are explicit
- [ ] Highlights and change summaries are limited to what actually shipped
- [ ] Required user or operator actions are explicit, or the document states none
- [ ] Breaking changes, migration guidance, and known issues are clear when relevant
- [ ] References point readers to deeper docs or support paths when needed

Use the template at `.ddx/plugins/helix/workflows/phases/05-deploy/artifacts/release-notes/template.md`.
