---
title: "Deployment Checklist — HELIX Plugin and Website Release"
slug: deployment-checklist
weight: 940
activity: "Deploy"
source: "05-deploy/deployment-checklist.md"
generated: true
---
# Deployment Checklist — HELIX Plugin and Website Release

## Release Scope

- Service or component: HELIX plugin (`.claude-plugin/`, `skills/`,
  `workflows/`) and the public website (`website/`, deployed to GitHub Pages).
- Version or commit: `vX.Y.Z` tag at the release commit SHA.
- Deployment window: Operator-driven; HELIX releases ship when the release
  bead reaches `Go` on this checklist. There is no fixed schedule.
- Release owner: HELIX maintainer cutting the tag.
- Rollback owner: Same operator (single-operator release flow).

## Pre-Deploy Checks

| Area | Check | Evidence or Command | Status |
|------|-------|---------------------|--------|
| Build | Skill packaging tests are green | `bash tests/validate-skills.sh` | [ ] |
| Build | Website builds clean (no Hugo errors, no broken shortcodes) | `cd website && hugo --gc --minify` | [ ] |
| Build | Reference generator runs without stale-mapping errors | `uv run scripts/generate-reference.py` | [ ] |
| Build | Workflow-paths pre-commit check passes | `lefthook run pre-commit --all-files` (or `git diff --check`) | [ ] |
| Config | No tracked secrets in repo | `git grep -nE 'OPENROUTER_API_KEY|ANTHROPIC_API_KEY|sk-[a-zA-Z0-9]'` returns only documentation | [ ] |
| Config | Plugin manifest version matches the tag | `grep '"version"' .claude-plugin/plugin.json` | [ ] |
| Data | No tracker drift between live `.ddx/beads.jsonl` and any docs being shipped as examples | `uv run scripts/generate-reference.py` (validates HELIX_REAL_EXAMPLES paths) | [ ] |
| Ops | `ddx work --dry-run` produces a coherent next-action summary against the release tag | `ddx work --dry-run` | [ ] |
| Ops | Release notes draft exists and references the tag | `docs/helix/05-deploy/release-notes.md` | [ ] |
| Ops | Demos still record cleanly | `cd website && bash record-demos.sh` (when demos changed in the release) | [ ] |

## Rollout Plan

| Stage | Action | Exit Condition |
|-------|--------|----------------|
| Local proof | Run all pre-deploy checks against the release commit | All checks above are checked |
| Tag and push | `git tag -a vX.Y.Z -m "..."` then `git push origin main vX.Y.Z` | Tag visible on origin; CI starts |
| Plugin publication | Plugin is consumed by users via repo URL — no separate registry push | Tag exists; `git fetch --tags` from a fresh clone resolves the manifest |
| Website rollout | GitHub Actions builds the site from the tagged commit and publishes to GitHub Pages | Pages workflow run succeeds; public URL serves the new content |
| Full rollout | Smoke-test the public site for the released artifact pages | Critical pages (`/`, `/why/`, `/use/`, `/artifacts/<each>/`) return 200 |

## Verification Checks

| Signal or Check | Expected Result | Evidence or Command | Status |
|-----------------|-----------------|---------------------|--------|
| Public site root reachable | HTTP 200 | `curl -fsS -o /dev/null -w '%{http_code}' https://documentdrivendx.github.io/helix/` | [ ] |
| Released artifact pages render | HTTP 200 with expected H1 | `curl -fsS https://documentdrivendx.github.io/helix/artifacts/contract/ \| grep -q "DDx"` | [ ] |
| Plugin install from tag works | A fresh clone of the tag installs and `ddx work --dry-run` runs | Manual: clone tag, run `ddx install helix --local . --force`, then `ddx work --dry-run` | [ ] |
| `ddx work` against a sample bead succeeds | `NEXT_ACTION` is one of the documented values | `ddx work --dry-run` in a sample repo | [ ] |
| No regressions in deterministic tests | All pass | `bash tests/validate-skills.sh` against the tag | [ ] |

## Rollback Triggers

| Trigger | Threshold or Condition | Immediate Action | Owner |
|---------|------------------------|------------------|-------|
| Public site fails to build under the new tag | Pages workflow run fails | Re-run the workflow once; if still failing, revert the tag commit and re-tag | Operator |
| Plugin install breaks for a fresh consumer | `ddx install helix --local . --force` exits non-zero on a clean checkout | Move the `vX.Y.Z` tag back one commit (`git tag -d` + force-push) only if no downstream consumers have pulled; otherwise issue a `vX.Y.Z+1` patch | Operator |
| Skill packaging tests regressed in CI on the tag | `tests/validate-skills.sh` fails on the tag in CI | Revert the offending change in a follow-up tag; do not silently amend the released tag | Operator |
| Critical artifact-reference page renders empty | A `HELIX_REAL_EXAMPLES_PUBLISHABLE` slug ships with a missing example | Patch release that flips the slug back off in `scripts/generate-reference.py` | Operator |

## Go or No-Go Decision

- Decision: [Go / Hold / Roll Back]
- Decision time: [ISO-8601 timestamp]
- Notes: Capture any deferred checks, exceptions, or known follow-up beads
  here. Reference the release-notes commit and the tag SHA so the decision
  is reconstructable from the tracker.
