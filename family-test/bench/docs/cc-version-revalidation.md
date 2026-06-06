# Claude Code version re-validation

The bench pins one Claude Code version in
[`../cc-version.lock`](../cc-version.lock). The pin is load-bearing because
skill-router behaviour — which skills CC activates for a given prompt, how
SKILL.md frontmatter is parsed, how stream-json events are emitted — is
internal to CC and changes without API contract. Grading rows against a
moving target invalidates ratchet history.

## Why the pin exists

- **Skill activation is internal.** CC decides which skill engages from a
  given user turn. That decision rule is unspecified and version-dependent.
  Bench rows that assert "skill X engaged" are only comparable across rows
  graded by the same CC.
- **stream-json shape drifts.** The runner parses CC's stream-json output
  for `tool_use`, `tool_result`, and message envelopes. New CC versions can
  rename fields or add events. `golden-transcripts/transcript_schema.yml`
  catches the drift but only at parse time.
- **Ratchets compound.** `ratchets.json` records `stable_pass_rate`,
  `routing_precision`, `cost_per_run`, `dev_iteration_burn` against a
  baseline. If the baseline was set on CC 2.1.163 and a new CC version
  raises pass rates by 4% for free, the ratchet looks like a win when
  nothing changed in HELIX.

## When to re-validate

Whichever comes first:

1. **90 days** since `last_validated` (currently 2026-06-05 → 2026-09-05).
2. **Trigger version ships** — any version in
   `re_validation_trigger_versions` (currently `2.2.x` and `2.1.200+`).
3. **Stream-json parse failure** in `helix_bench self-test` on a CC version
   newer than the pin, even within the window.

## What re-validation means

Re-validation is not "bump the version string." It is a full re-baseline:

1. Rebuild the bench Docker image with the new CC version. Update the
   image's `CLAUDE_CODE_VERSION` build arg and confirm `claude --version`
   inside the container matches.
2. Run `python3 family-test/bench/runner/helix_bench.py self-test`. This
   runs matcher property tests, meta-tests, golden-transcript schema check,
   and matcher-vacuity checks. If self-test fails on the new CC, halt —
   the runner needs work before any bench run is meaningful.
3. Run the full bench:
   `python3 family-test/bench/runner/helix_bench.py run --all --determinism 3`.
4. Compare each ratchet stream against `ratchets.json` baseline:
   - `stable_pass_rate`: regression > 5% halts the upgrade.
   - `routing_precision`: regression > 5% halts the upgrade.
   - `cost_per_run`: regression > 20% triggers a budget review (warn,
     not halt).
   - `dev_iteration_burn`: informational only.
5. If all gates pass: update `cc-version.lock`:
   - `claude_code_version:` → new version
   - `last_validated:` → today
   - `re_validation_required_after:` → today + 90 days
   - update `ratchets.json` baselines to the new measurements
   - commit with subject `cc(revalidate): bump pin to <new-version>`
6. If gates fail: keep the old pin. File a bead documenting which streams
   regressed and by how much, so the regression can be triaged before the
   next attempt.

## Procedure step-by-step

```bash
# 1. Build new image
cd family-test/bench
docker build --build-arg CLAUDE_CODE_VERSION=<new> -t helix-bench:<new> .
docker run --rm helix-bench:<new> claude --version
#    → confirm matches <new>

# 2. Self-test
docker run --rm -v "$PWD:/bench" helix-bench:<new> \
    python3 /bench/runner/helix_bench.py self-test

# 3. Full bench (writes cost-log.jsonl + per-row failure dumps)
docker run --rm -v "$PWD:/bench" helix-bench:<new> \
    python3 /bench/runner/helix_bench.py run --all --determinism 3 \
    > /tmp/bench-revalidate-<new>.log

# 4. Compare against ratchets baseline
python3 family-test/bench/runner/helix_bench.py ratchets compare \
    --baseline family-test/bench/ratchets.json \
    --run /tmp/bench-revalidate-<new>.log

# 5. If green: update pin
$EDITOR family-test/bench/cc-version.lock
git add family-test/bench/cc-version.lock family-test/bench/ratchets.json
git commit -m "cc(revalidate): bump pin to <new-version>"
```

## Surfacing the deadline

The pre-commit hook (`lefthook.yml` → `check-cc-revalidation`) WARNS (does
not block) on every commit when `re_validation_required_after` is in the
past. The CI nightly job runs
`family-test/bench/runner/check-cc-revalidation.sh` and prints the same
warning to the workflow log so the deadline can't be missed by working
exclusively in CI.
