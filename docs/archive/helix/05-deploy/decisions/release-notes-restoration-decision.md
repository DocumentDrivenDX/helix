# Release Notes — Restoration Decision

> Historical decision; superseded by the worked example at `docs/helix/05-deploy/release-notes.md`.

`release-notes` is restored as the canonical deploy-activity artifact for
release-specific communication that summarizes user-visible or operator-visible
changes.

## Decision

This artifact is restored rather than retired.

Current HELIX still names `release-notes` in `workflows/DDX.md`,
`workflows/state-machine.yaml`, `deployment-checklist`, and
`feature-registry`. The deploy state machine also still expects release notes
to be published before the activity exits. The intent therefore still exists in
the live contract even though the original artifact stub was pruned.

## Why It Exists

- `deployment-checklist` is the technical go or no-go surface for rollout.
- `monitoring-setup` defines the signals and dashboards that prove rollout
  health.
- `runbook` explains what operators do when the rollout degrades or needs
  rollback or recovery.
- `release-notes` tell users and operators what actually changed, why it
  matters, and whether they need to do anything.
- `CHANGELOG.md` is not a full replacement. A changelog is a repository-level
  history log; release notes are a release-scoped communication artifact with
  audience filtering, impact framing, and action guidance.

## Canonical Inputs

- release scope, version, and deployment window
- shipped features, fixes, and operator-visible changes
- breaking changes, migration steps, and rollout caveats
- known issues, rollback guidance, or support escalation paths
- links to deeper docs such as deployment checklist, runbook, or feature docs

## Minimum Prompt Bar

- Keep the document scoped to one actual release and only the changes that
  shipped in it.
- Write for readers who need impact and action, not implementation trivia or
  roadmap filler.
- Make required user or operator actions explicit, or say explicitly that no
  action is required.
- Separate highlights from detailed changes, breaking changes, and known
  issues so the release is scannable.
- Include migration, rollback, or support guidance when the release changes how
  a user upgrades or an operator responds.
- Distinguish release notes from technical rollout artifacts and from broader
  launch or GTM coordination.

## Minimum Template Bar

- release scope, version, and date
- audience and communication channels
- highlights
- shipped changes and fixes
- breaking changes and required actions
- migration or rollback guidance
- known issues and support path

## Canonical Replacement Status

`release-notes` is not replaced by `deployment-checklist`, `runbook`, or
`CHANGELOG.md`. Those surfaces answer different questions:

- the checklist decides whether to release
- the runbook explains how to respond operationally
- the changelog records repository history
- release notes communicate the release itself

The deleted `gtm-plan` artifact stays retired. `release-notes` cover the
release communication that HELIX standardizes, while broader launch
coordination or adoption planning belongs in linked `activity:deploy` tracker
issues or project-specific business planning outside the portable artifact set.

The deleted prompt and template were too generic to justify keeping. Restoration
is warranted only with a tighter prompt and template bar that forces
release-scoped, audience-aware communication.
