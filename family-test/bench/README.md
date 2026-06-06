# Conversation bench

Reproducible bench for HELIX-family skill engagement, cascading flow logic,
autonomy levels, and stop_at semantics. Drives Claude Code at a pinned
version and grades per-row outcomes via a typed three-layer assertion DSL.

Design record: [../../docs/helix/02-design/plan-2026-06-05-conversation-bench-and-autonomy.md](../../docs/helix/02-design/plan-2026-06-05-conversation-bench-and-autonomy.md).

## Layout

```
bench/
  runner/                  Runner skeleton, stream-json parser, matchers
  conversations/           Per-conversation dirs (conversation.yml + expected.yml)
  routing-evals/           Per-flow JSONL evals (positive / negative / ambiguous)
  golden-transcripts/      9 hand-curated stream-json goldens (one per assertion_id)
                           + transcript_schema.yml — catches CC stream-json drift
  judge/                   Layer-2 judge prompts + calibration set
  failures/                Runner dumps <row-id>-<timestamp>/ on row fail
  library/schemas/         discriminator-whitelist.yml, banned-matcher-patterns.yml
  bench-categories.yml     Diff-to-category mapper for PR escalation (P14)
  cc-version.lock          Pinned Claude Code version (§19.3)
```

## Pinned Claude Code

See `cc-version.lock`. CI bench job reads this; if the container CC version
doesn't match, the build fails. Re-validation cadence: 90 days OR when CC
hits a trigger version, whichever comes first.

## Assertion DSL

The runner accepts only assertion_ids listed in
`library/schemas/discriminator-whitelist.yml` (9 IDs in v1). Matcher
arguments are validated against `library/schemas/banned-matcher-patterns.yml`
to prevent vacuous discriminators (T047). Adding a new assertion_id is a
methodology contract change and must land in the whitelist alongside runner
and meta-test updates.

## Running

The runner ships in `runner/` (Phase 0a). `--self-test` drives meta-tests +
property tests + golden-schema checks + matcher-vacuity checks before any
bench run.
