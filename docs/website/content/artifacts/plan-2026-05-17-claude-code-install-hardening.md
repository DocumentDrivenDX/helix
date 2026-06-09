---
title: "Plan: harden the Claude Code install surface"
slug: plan-2026-05-17-claude-code-install-hardening
weight: 510
activity: "Design"
source: "02-design/plan-2026-05-17-claude-code-install-hardening.md"
generated: true
---

> **Source identity** (from `02-design/plan-2026-05-17-claude-code-install-hardening.md`):

```yaml
ddx:
  id: plan.claude-code-install-hardening
  status: draft
```

# Plan: harden the Claude Code install surface

**Date:** 2026-05-17
**Status:** Draft, awaiting maintainer decision on the four open
questions below.
**Source:** Audit of the "pure Claude" install surface (manifests,
docs, tests) on 2026-05-17 surfaced five concrete issues spanning
HIGH, MEDIUM, and LOW user impact.

## Goal

Bring the Claude Code install path from "documented and partially
tested" to "documented, consistent, and verifiably tested against the
canonical user flow." Resolve the five issues identified in the audit
and add the release-time gates that would have caught them before
v0.4.1 shipped.

## The five issues

| ID | Severity | Summary |
|---|---|---|
| **A1** | MEDIUM | `marketplace.json` lists `"repo": "easel/helix"` while `plugin.json` lists `"repository": "DocumentDrivenDX/helix"`. Docs follow marketplace.json. Both repos exist and carry the v0.4.1 release; install works either way, but the canonical home is ambiguous. |
| **A2** | HIGH | `tests/install/claude-code/install.sh` uses `--plugin-dir` symlink, not the documented `claude plugin marketplace add` + `claude plugin install` flow. The user-facing install path is unverified. |
| **A3** | MEDIUM | `tests/install/claude-code/Dockerfile` curls `https://claude.ai/install.sh` as a guess and falls back to a `WARN:` log on failure. The CI container may have no `claude` binary, silently degrading the functional check. |
| **A4** | LOW | The `claude plugin list` example in `docs/install/claude-code.md` shows `helix  0.3.4`. Current is `0.4.1`. |
| **A5** | MEDIUM | `.github/workflows/test.yml` runs deploy-artifact + state-rules + skills validation. It does NOT run `tests/install/*` or `just install-test`. The Claude Code (and every other runtime) install scenarios are exercised only when someone runs `just install-test` locally. |

## Cross-cutting note

A1 and A5 are NOT Claude Code-specific; they affect every runtime's
install surface. A2 has parallels in `tests/install/codex-cli/` and
`tests/install/copilot-cli/` which similarly use filesystem-copy
shortcuts rather than the canonical marketplace/registry flows. This
plan addresses the Claude Code instances directly and proposes
follow-up beads for the other runtimes once the patterns are
established.

## Decisions to resolve before implementation

| Question | Options | Recommendation |
|---|---|---|
| Which repo is the canonical public home for HELIX? | (a) `easel/helix` (personal handle, current marketplace + docs) (b) `DocumentDrivenDX/helix` (org repo, current `plugin.json` `repository` field) (c) both, with one as primary mirror | **Maintainer-only decision.** Need to know intent — is HELIX a personal project under your handle, or an org-published project under DocumentDrivenDX? |
| Should the marketplace flow test run on every PR, or release-tag only? | (a) every PR (catches breakage fast, network-dependent) (b) release-tag only (validates the published bundle, no per-PR network cost) (c) both — `--plugin-dir` on PR + marketplace flow on release | **(c) both.** `--plugin-dir` tests HEAD; marketplace tests the published release. Different concerns; both worth catching. |
| Functional checks (real `claude -p` call) in CI: where do API keys live? | (a) GitHub Actions secrets (b) only run functional checks locally, never in CI (c) require operator opt-in via repository_dispatch | **(a) GitHub Actions secrets**, gated to release-tag runs to control token spend. Same posture as the Genie e2e (no per-PR LLM cost). |
| Should we publish the install-test screencast as a release asset, or keep it ad-hoc? | (a) auto-capture and attach to each tagged release (b) keep ad-hoc; record only when reviewing | **(a) auto-capture.** Once `vhs` is wired into the install-test workflow, attaching the `.gif` is free. Useful release evidence. |

## Phases of work

### Phase A — Decisions

Maintainer answers the four questions above. Decision log at the
bottom of this plan gets filled in. No code changes in this phase.

**Deliverable:** decision log resolved.

### Phase B — Fix manifest + doc consistency (A1)

After the repo-canonical-home decision lands:

- If `easel/helix` is canonical: update `plugin.json` `repository` and
  `homepage` fields to point at `easel/helix`. Leave docs and
  marketplace as-is.
- If `DocumentDrivenDX/helix` is canonical: update
  `marketplace.json` `plugins[].source.repo` to `DocumentDrivenDX/helix`.
  Replace every occurrence of `easel/helix` in `docs/install/`,
  `tests/install/`, and `.github/` with `DocumentDrivenDX/helix`.

Either way, end state: one canonical repo name across `plugin.json`,
`marketplace.json`, `docs/install/*`, `.github/workflows/*`, and
`tests/install/*`. Grep-able assertion: `grep -rE 'easel/helix|DocumentDrivenDX/helix'`
returns a single repo name (the chosen one) across all those files.

**Deliverable:** consistent repo references across the install
surface. Lint added to `tests/validate-install-consistency.sh` (new)
that fails when the two manifests reference different repos.

### Phase C — Verify and replace the Claude Code install URL (A3)

The `https://claude.ai/install.sh` URL in the Dockerfile is a guess.
Real install options to investigate:

- npm package — likely `@anthropic-ai/claude-code` or
  `@anthropic-ai/claude`. Pin a known-good version.
- Anthropic's official install script — URL needs to be confirmed via
  the Claude Code docs.
- Pre-built tarball under
  `https://github.com/anthropics/claude-code/releases/...` — pattern
  used by other Anthropic tools.

Plan:

1. Dispatch a research pass (claude-code-guide agent) to confirm the
   current canonical install command for the Claude Code CLI in a
   non-interactive environment.
2. Update `tests/install/claude-code/Dockerfile` to use that command.
3. Remove the `|| echo "WARN: ..."` silent-fallback. If the install
   fails, the test should fail — not silently degrade to layout-only
   checks.

**Deliverable:** Dockerfile installs Claude Code CLI reliably from a
documented source. `docker build` followed by `docker run claude
--version` succeeds.

### Phase D — Split install.sh into `--plugin-dir` vs marketplace tests (A2)

Rename `tests/install/claude-code/install.sh` to
`install-plugindir.sh` (clarifying its scope). Add a new
`install-marketplace.sh` that exercises the actual marketplace flow:

```bash
#!/usr/bin/env bash
set -euo pipefail

echo "claude version:"
claude --version

echo "→ claude plugin marketplace add <repo>"
claude plugin marketplace add <chosen-repo>

echo "→ claude plugin install helix@helix --scope user -y"
claude plugin install helix@helix --scope user -y

echo "→ claude plugin list"
claude plugin list
```

Update `verify.sh` to run against whichever path was used (parameterize
by the install location: `~/.claude/plugins/helix/skills/helix` for
both `--plugin-dir` symlink and marketplace install).

Update `run-scenarios.sh` (or whatever the runtime harness scaffold
becomes in FEAT-014) to optionally exercise both install paths.

**Deliverable:** two install paths verifiable. PR-time runs
`install-plugindir.sh`; release-tag runs both, including
`install-marketplace.sh` which tests the actual published release.

### Phase E — Wire install-test into CI (A5)

Two new GitHub Actions jobs:

1. **PR + main runs**: extend `.github/workflows/test.yml` with a
   `install-test-static` job that runs the static portion of
   `tests/install/run-all.sh` (no Docker builds, no LLM calls — just
   the shared `verify-skill-layout.sh` against the in-repo
   `skills/helix/`). Cost: zero. Catches frontmatter regressions and
   layout breakage immediately.

2. **Release-tag runs**: extend
   `.github/workflows/release-genie-bundle.yml` (or add a new
   `install-test-release.yml`) with a `install-test-full` job that:
   - Builds the Docker images under `tests/install/{ddx,claude-code,codex-cli,copilot-cli}/`.
   - Runs the install scenarios with `TEST_FUNCTIONAL=1`.
   - Requires `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GH_TOKEN`,
     `DATABRICKS_HOST`/`DATABRICKS_TOKEN` as GitHub Actions secrets.
   - Optionally captures `vhs` screencasts as artifacts.

   This job validates that the published v$.$.$ release is actually
   installable on each runtime. Fails the release if any runtime
   scenario fails. Genie scenarios remain manual (browser-only;
   `genie:catalog-unreachable` tag still allowed where applicable).

**Deliverable:** install-test runs in CI on the appropriate cadence;
broken release pipeline halts at the install-test step instead of
publishing.

### Phase F — Capture Claude Code screencast (related to A4)

`tests/install/claude-code/record.tape` exists but no `.gif` has been
captured. Once Phase D is in place:

```bash
vhs tests/install/claude-code/record.tape
```

produces `recording.gif`. Commit (or attach as release asset per the
Phase A.4 decision).

**Deliverable:** committed or released `tests/install/claude-code/recording.gif`
showing the marketplace install flow end-to-end.

### Phase G — Refresh stale example output + add release checklist (A4)

- Edit `docs/install/claude-code.md` to show `helix  0.4.1` in the
  example `claude plugin list` output. Note the example version
  alongside.
- Add a `docs/helix/05-deploy/release-checklist.md` (or extend an
  existing release-notes doc) noting that example outputs in
  `docs/install/*.md` should be refreshed when a release ships. Keeps
  staleness from becoming chronic.

**Deliverable:** current example output; release checklist exists
that catches future staleness.

### Phase H — Validate end-to-end, tag patch release if needed

After Phases B–G land:

- Run `just install-test` locally; confirm all four terminal scenarios
  pass.
- If marketplace.json changed in Phase B (repo URL fix), cut `v0.4.2`
  to publish the corrected manifest. Otherwise no release needed.
- Re-run the Genie e2e (with cookies + clean instructions) to confirm
  no regression on that scenario.

**Deliverable:** all five issues from the audit are closed, validated,
either shipped (if a release is needed) or merged into main.

## Suggested bead set

1 epic + 11 children. Following the FEAT-013/014/015 patterns:

| ID | Phase | Title | Priority |
|---|---|---|---|
| epic | — | Epic: harden the Claude Code install surface (5 audit findings) | 1 |
| C1 | A | (Manual) Maintainer answers four decisions | 0 |
| C2 | B | Reconcile repo URL across manifests + docs (A1) | 0 |
| C3 | B | Add `tests/validate-install-consistency.sh` lint | 1 |
| C4 | C | Research + document the canonical Claude Code CLI install command (A3) | 0 |
| C5 | C | Update `tests/install/claude-code/Dockerfile` with verified install URL | 1 |
| C6 | D | Split `install.sh` → `install-plugindir.sh` + `install-marketplace.sh` (A2) | 0 |
| C7 | E | Add `install-test-static` job to `.github/workflows/test.yml` (A5 — PR runs) | 1 |
| C8 | E | Add `install-test-full` job for release-tag runs (A5 — full Docker matrix) | 1 |
| C9 | F | Capture Claude Code screencast via vhs | 2 |
| C10 | G | Refresh stale `claude plugin list` example (A4) | 2 |
| C11 | G | Add release checklist that catches future example staleness | 2 |
| C12 | H | Tag v0.4.2 if Phase B shipped a manifest change | 2 |

Priorities reflect impact: A2 (HIGH, C6) and A5 (MEDIUM blocker for
release safety, C7-C8) are P0/P1. A1 (C2) is P0 because everything
downstream depends on knowing which repo is canonical.

## Risks and decisions deferred

1. **Other runtime scenarios likely have parallel A2-style gaps.**
   Codex CLI install.sh uses `cp -r` not `npx skills add`. Copilot
   uses a scratch-repo simulation, not real Copilot-Chat invocation.
   These are separate fix beads — file as follow-ups under the
   FEAT-013 epic (which is closed) or under a new "install-coverage
   hardening" umbrella. **Recommendation:** add to FEAT-015 epic or
   a parallel umbrella; out of scope for this Claude-Code-focused
   plan.

2. **API key secrets in CI cost real money.** A release-tag run with
   `TEST_FUNCTIONAL=1` against Claude Code + Codex CLI + Copilot CLI
   = ~$2-5 per release. At a release cadence of 1-2/week this is
   negligible. Still worth budgeting: cap at $10/run, fail fast on
   token usage exceeding that, etc.

3. **`vhs` screencast determinism.** vhs records terminal sessions
   deterministically given the same script and base image. If
   Anthropic changes the `claude --version` output or `claude plugin
   list` formatting, the recording will look stale. Mitigation: keep
   `.tape` files short and focused on layout-stable output;
   re-record on every release tag.

4. **Marketplace flow requires Claude Code 2.x.** Older versions don't
   have `claude plugin marketplace add`. The Dockerfile install needs
   to pin a version that has the marketplace subcommand.

## Decision log (resolved 2026-05-17)

- Canonical repo home: **`DocumentDrivenDX/helix`** (org repo). The
  current `plugin.json` `repository` field is correct; `marketplace.json`
  and every `easel/helix` reference under `docs/install/`,
  `tests/install/`, and `.github/` is the side that updates.
- Marketplace flow test cadence: **both PR and release-tag.**
  `install-plugindir.sh` runs on every PR (HEAD smoke, no network);
  `install-marketplace.sh` runs on release tag (validates the
  published bundle).
- Functional checks in CI: **GitHub Actions secrets, release-tag
  only.** Same posture as the Genie e2e. PR runs are static-only and
  free.
- Screencast distribution: **auto-capture and attach to release.**
  Once `vhs` is wired into the install-test workflow, the `.gif` is a
  release asset alongside the bundle.

## See also

- `docs/install/claude-code.md` — current user-facing install guide
- `docs/resources/agents/claude-code-plugins.md` — Claude Code plugin
  mechanism reference (the source-of-truth for what's supposed to work)
- `tests/install/claude-code/` — current test scaffold
- `.github/workflows/test.yml` — current CI test job
- `.github/workflows/release-genie-bundle.yml` — release workflow that
  ships bundle + installer; candidate host for `install-test-full`
- `docs/helix/03-test/test-plans/STP-014-helix-workflow-coverage.md`
  — broader workflow coverage plan; this install hardening plan is
  upstream of it
