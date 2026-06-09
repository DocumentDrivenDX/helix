# Bucket E — hook + CI integration

Phase 5 of the vertical-slice validation plan.

## Results

| Probe | Result   | Evidence |
|-------|----------|----------|
| E1 lefthook integration   | PASS     | `e1-output.txt`, `run-e1-lefthook.sh` |
| E2 GitHub Actions workflow | PASS     | `e2-output.txt`, `../../.github/workflows/family-validation.yml` |
| E3 --changed-only correctness | DEFERRED | `e3-output.txt` (validator lacks the flag) |

## E1 — lefthook

- Config: `family-test/consumer/clean/.lefthook.yml` (uses `$FAMILY_TEST_ROOT`
  for portability).
- Harness: `run-e1-lefthook.sh` builds an isolated git repo from the clean
  fixture, installs lefthook, then runs two commits:
  1. baseline (clean change) — hook allows, exit 0.
  2. failure (broken instance copied from `consumer/bad-edge-kind/`) —
     hook aborts with exit 1, output contains `I101`.
- The harness restores the repo on exit (tempdir removed).

## E2 — GitHub Actions

- Workflow: `family-test/.github/workflows/family-validation.yml`.
- Runs `bash run-tests.sh` (full driver) + a clean-fixture assertion +
  a spot-check loop over expected-failure fixtures.
- GitHub Actions only reads workflows from the repo root, so the file
  under `family-test/` documents the contract; activation requires
  copying or symlinking to `/.github/workflows/`. The plan accepts the
  workflow file's existence as the Phase-5 deliverable.

## E3 — --changed-only

- The validator does not yet expose `--changed-only <ref>`. Per the
  brief, this is marked deferred. Notes on the eventual test shape are
  in `e3-output.txt`.
