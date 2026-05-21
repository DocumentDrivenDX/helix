# Release Notes — HELIX v0.3.3

## Release Scope

- Release identifier or version: `v0.3.3`
- Release date: 2026-04 (operator-driven; tag commit `0db3ea8`)
- Rollout window or environment: HELIX plugin (consumed by users via repo
  tag) and the public website at `https://documentdrivendx.github.io/helix/`
- Release owner: HELIX maintainer cutting the tag
- Source commit or build: `0db3ea8` (tag `v0.3.3`)

## Audience and Channels

| Audience | Why they care | Delivery channel |
|----------|---------------|------------------|
| HELIX plugin users | New CI behavior and review-threshold knob affect day-to-day queue-drain output | Plugin repo tag; release notes in `docs/helix/05-deploy/release-notes.md` |
| Website readers | Public docs at `documentdrivendx.github.io/helix/` updated to the tag | GitHub Pages rebuild; release-notes page |
| HELIX maintainers | Test-suite stability changes need to be folded into local development practice | Repo issues and the HELIX commit workflow |

## Highlights

- **CI stability**: skill packaging tests now filter spurious DDx update
  notices that were causing intermittent CI red without indicating a real
  regression.
- **Review-threshold knob**: A configurable threshold gates how aggressively
  the queue-drain loop triggers periodic alignment, giving operators more
  control over review cadence on long-running queues.
- **Plugin manifest correctness**: A dangling hooks reference in
  `.claude-plugin/plugin.json` was removed; fresh plugin installs no longer
  emit a manifest-validation warning.

## Changes and Fixes

### New or Improved

| Area | What changed | Who is affected |
|------|--------------|-----------------|
| Queue drain | `--review-threshold` accepted to tune periodic-alignment cadence | Operators running long queue-drain sessions |
| CI | Skill packaging tests filter DDx update notices from harness output before assertions | HELIX maintainers and contributors |
| Tracker / forge | Forge-agent discovery tracker issue added to capture follow-up work | HELIX maintainers |

### Fixes

| Issue or symptom | Resolution | User or operator impact |
|------------------|------------|-------------------------|
| Intermittent CI red on skill packaging tests from DDx update banners | Banner filter applied before stdout assertions | Stable green CI; no operator action |
| Manifest validation warning on plugin install | Dangling hooks reference removed from `.claude-plugin/plugin.json` | Fresh installs are clean |

## Breaking Changes and Required Actions

There are no breaking changes in `v0.3.3`. No operator action is required.

## Migration or Rollback Guidance

### Upgrade or Migration

1. Pull the new tag: `git fetch --tags && git checkout v0.3.3` in your
   HELIX checkout (or repoint your plugin install at the new tag).
2. Re-run `ddx install helix --local . --force` to refresh the local
   skill installation.
3. No tracker or schema migration is required — `.ddx/beads.jsonl` is
   forward-compatible.

### Rollback or Hold Guidance

- Pause rollout when: a downstream consumer reports `--review-threshold`
  parsing errors, or when `bash tests/validate-skills.sh` regresses against
  the new tag in CI.
- Roll back using: `git checkout v0.3.2` and re-run
  `ddx install helix --local . --force`. The previous tag is fully
  compatible with the current `.ddx/beads.jsonl` schema.
- Ask for help in: the HELIX repo issue tracker.

## Known Issues and Support

| Issue | Who is affected | Workaround or next step |
|------|------------------|-------------------------|
| Forge-agent discovery is tracked as a follow-up bead but not yet implemented | Operators wanting auto-discovery of forge agents | Continue using explicit agent configuration; track the linked tracker issue |

## References

- Deployment checklist: [`deployment-checklist.md`](deployment-checklist.md)
- Runbook: [`runbook.md`](runbook.md)
- Plugin manifest: `.claude-plugin/plugin.json`
- Support or escalation path: HELIX repo issue tracker
