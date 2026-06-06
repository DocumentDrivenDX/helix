# Meta-tests (Phase 0b)

Per plan §1.4b / Phase 0b. Ten meta-tests run as part of `helix_bench.py
self-test`. Five are vacuous-discriminator rejections (MT01-MT05) that the
runner MUST refuse; five are positive synthetic transcripts that the runner
MUST accept and grade correctly.

| ID | Kind | Expected outcome |
|----|------|------------------|
| MT01 | reject | T042 — `expected_in_positive_run == expected_in_negative_run` |
| MT02 | reject | T041 — `assertion_id` not in whitelist |
| MT03 | reject | T040 — discriminator block missing |
| MT04 | reject | T044 — `negative_control` has no methodology-changing modification |
| MT05 | reject | T047 — matcher argument matches banned-pattern (vacuous) |
| MT06 | accept | `skill_tool_use` present |
| MT07 | accept | `read_before_write` ordered |
| MT08 | accept | `scope_write_path` present (all writes in-scope) |
| MT09 | accept | `refusal_no_write` present (refusal text + zero mutations) |
| MT10 | accept | `route_decision` present (explicit_skill_tool_use signal) |

Each row dir contains an `expected.yml`. Accept rows additionally carry a
`transcript.jsonl` so the runner can grade the matcher end-to-end.
