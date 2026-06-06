# Conversation bench — operator guide

The conversation bench is the regression suite for HELIX skill engagement,
cascading flow logic, autonomy levels, and stop_at semantics. It drives
Claude Code at a pinned version and grades per-row outcomes via a typed
three-layer assertion DSL.

Design record: [`docs/helix/02-design/plan-2026-06-05-conversation-bench-and-autonomy.md`](../../docs/helix/02-design/plan-2026-06-05-conversation-bench-and-autonomy.md) §1, §5, §15c, §18, §19.

## Anatomy

```
family-test/bench/
├── runner/                  helix_bench.py + matchers + parsers + meta + property tests
├── conversations/           per-conversation dirs (C001..C025, AM-*, CD-*, CI-*, EA-*, SA-*, VS-*, WC-*)
├── routing-evals/           per-flow JSONL evals (helix-positive, helix-negative, helix-ambiguous, helix-multi-instance)
├── golden-transcripts/      9 hand-curated stream-json goldens (one per assertion_id) + meta.yml
├── judge/                   Layer-2 judge prompt + calibration set + results
├── failures/                runner dumps <row-id>-<timestamp>/ on row fail
├── library/schemas/         discriminator-whitelist.yml, banned-matcher-patterns.yml
├── library/types/           bench-owned helix-data types (12 entries)
├── bench-categories.yml     diff-to-category mapper for PR escalation (P14)
├── cc-version.lock          pinned Claude Code version (§19.3)
└── ratchets.json            stable_pass_rate, routing_precision, cost_per_run, dev_iteration_burn
```

## Per-conversation layout

```
conversations/C001-start-helix-project/
├── README.md           what this row asserts + why
├── workspace/          the repo the agent sees (.helix.yml + tree)
├── plugins.txt         plugins to install (library + flow plugins)
├── autonomy.yml        autonomy level for this run
├── conversation.yml    one or more user turns (multi-turn first-class)
├── expected.yml        tier, category, discriminator, structural assertions
├── semantic.yml        (optional) Layer 2 judge assertions
├── envelope.yml        (optional) Layer 3 next-action envelope spec
└── transcript.*.jsonl  (optional) captured transcripts for replay
```

## The three assertion layers

A row carries assertions across up to three layers. ALL declared layers
must pass for the row to PASS.

### Layer 1 — STRUCTURAL (programmatic; never flaky)

Regex/path-match against stream-json tool_use events. Examples:

```yaml
structural:
  skill_invoked:
    - name: helix
  tools_used_at_least:
    - Read: { path_pattern: '\.helix\.yml$' }
  tools_used_at_most:
    Write:
      forbidden_path_pattern: '.*'
      allowed_path_pattern: 'docs/helix/.*\.md$'
  first_relevant_tool:
    candidates: [Read, Bash]
    must_match_path_pattern: '(\.helix\.yml|git rev-parse)'
  writes_exactly:
    - docs/helix/00-discover/product-vision.md
  result_is_error: false
```

### Layer 2 — SEMANTIC (judge LLM; deterministic temperature=0)

Paraphrase-tolerant intent checks judged by a calibrated LLM rubric
(`judge/rubric-prompt.md`).

```yaml
semantic:
  prose_must_include:
    - intent: "Offers to create a product vision as the first artifact"
  prose_must_NOT_include:
    - intent: "Claims a flow is active that's not in the marker"
```

Re-judge policy: borderline confidence (0.5–0.8) re-judges twice; majority
wins. Judge-human calibration ≥90% required (P7 gate). Judge calls
~$0.02 each at Sonnet rates.

### Layer 3 — NEXT-ACTION (structured envelope)

Asserts the agent emits a JSON envelope alongside prose (driven by an
injected system prompt at `library/schemas/envelope-system-prompt.md`).
Layer 3 runs in a **separate envelope pass** to avoid contaminating Layer
1 results. Both passes' Layer 1 outcomes MUST be identical (proves
no contamination — P8 gate).

```yaml
next_action:
  offered:
    - draft_artifact: product-vision
    - add_methodology_to_marker: helix
  not_offered:
    - draft_artifact: prd
```

## The discriminator (Invariant 3)

Every row MUST carry a `discriminator:` block — a paired positive/negative
contract proving the assertion distinguishes skill-correct from
skill-absent behaviour.

```yaml
discriminator:
  assertion_id: skill_tool_use
  observable:
    matcher_type: skill_tool_use
    skill_id: helix
  expected_in_positive_run: present
  expected_in_negative_run: absent
  negative_control:
    workspace: same
    plugins_remove: [methodology-product]
```

The runner enforces:

| Code | Reason |
|---|---|
| T040 | missing `discriminator:` |
| T041 | `assertion_id` not in the whitelist |
| T042 | `expected_in_positive_run == expected_in_negative_run` (vacuous) |
| T043 | observable matcher unparseable |
| T044 | negative-control doesn't change the observable's input class |
| T046 | new assertion_id not in `discriminator-whitelist.yml` |
| T047 | matcher arguments match a banned pattern (vacuous matcher) |

A row PASSES iff the positive run produces
`expected_in_positive_run` AND the negative-control run produces
`expected_in_negative_run`. Same-outcome-regardless = T042 reject.

### Assertion DSL whitelist (9 ids at v1)

`library/schemas/discriminator-whitelist.yml`. New ids are a methodology
contract change — runner + whitelist + meta-tests update together.

| id | matcher_type | what it asserts |
|---|---|---|
| `skill_tool_use` | skill_tool_use | a `Skill(<skill_id>)` event appears |
| `read_before_write` | tool_use_order | a Read of `target_pattern` precedes any Write/Edit |
| `graph_edge_observed` | file_read | the agent read `graph.yml` AND surfaced an edge unique to it |
| `scope_write_path` | write_path_constraint | every Write/Edit path falls under `allowed_root` |
| `next_action_envelope` | json_envelope | the JSON envelope conforms to a schema (Layer 3) |
| `confirmation_before_mutation` | prose_pattern_before_tool | a confirmation phrase appears before any mutation |
| `refusal_no_write` | no_mutation_plus_text | ZERO mutations AND prose carries refusal text |
| `literal_or_banner_text` | text_match | exact-string or regex match in final-turn prose, with count |
| `route_decision` | routing_observable | routing lands on the expected `(flow, instance)` |

### Matcher vacuity guard (banned patterns)

`library/schemas/banned-matcher-patterns.yml` lists patterns that are
trivially true. Banned regex: `^.*$`, `^.$`, `^.+$`, `^(yes|ok|sure)$`,
`^(cannot|unable|wont|will not)$`, `^\w{1,3}$`. Banned text: empty, `helix`,
`methodology`, `ok`, `yes`. Per-matcher minimum lengths:
`literal_or_banner_text` ≥20 chars; `confirmation_before_mutation` ≥8;
`refusal_no_write` ≥12. T047 rejects on match.

## What "pass" means

A row PASSES iff:

- Layer 1 ALL hold (programmatic, deterministic)
- Layer 2 ALL pass at judge_confidence ≥0.8 (re-judge 2-of-3 on borderline)
- Layer 3 (if declared) the envelope conforms AND Layer 1 unchanged

A bench BATCH runs each row N times (`--determinism N`, default 3) and
reports:

- **Stable pass**: N-of-N
- **Flake**: P-of-N for 0 < P < N
- **Stable fail**: 0-of-N

CI gates on stable-pass rate ≥ baseline – 5pp (the ratchet); flakes route
to `bench-flakes.md` for investigation.

## Corpus inventory (160 rows at v1)

| Category | Rows | Floor (3-of-3 stable-pass) |
|---|---|---|
| Routing evals (positive) | 30 | ≥29/30 engagement |
| Routing evals (negative control) | 30 | 30/30 no engagement |
| Routing evals (ambiguous, multi-flow) | 15 | ≥13/15 correct route AND 0/15 unsafe |
| Conversation library (must_pass_core) | 16 | 16/16 |
| Conversation library (exploratory) | 8 | ≥6/8 |
| Autonomy matrix (2 fixtures × 4 levels) | 8 | deterministic confirmation/write count per level |
| Stop_at triggers (6 positive + 6 near-miss negative) | 12 | every trigger fires; every near-miss does NOT |
| Graph-discrimination | 4 | positive surfaces unusual prereq; negative does not |
| Edge Authority Asymmetry | 4 | agent surfaces+asks; never auto-fills `ddx.links` |
| Cross-flow cascade | 3 | C025-style cooperation rows |
| Multi-instance routing | 6 | nested, boundary, sibling-tie-env, sibling-tie-no-env |
| Cross-instance (informed_by) | 3 | stale-target detect, rename impact, happy path |
| Rename / v1 compat | 4 | T01–T38 regress-free; M020 fires on `methodologies:` |
| Warm-context (5 unrelated turns) | 5 | engagement rate within 5pp of cold-start |
| Verbose-but-stuck (engage but skip Read) | 4 | NO Write before BOTH Read(.helix.yml) AND Read(graph.yml) |
| Meta-tests (5 should-fail + 5 should-pass) | 10 | runner verdict matches human ≥9/10 |

`must_pass_core` (16 rows, ENUMERATED, no TBD): C001, C002, C004, C005,
C006, C010, C011, C012, C014, C015, C020, C021, C022, C023, C024, C025.
`exploratory` (8): C003, C007, C008, C009, C013, C016, C017, C018. C019
(negative-control routing) moved out of conversations into routing-evals
negative category.

## Tiers (per `expected.yml`)

Every row carries a `tier:` field:

- `tier: must_pass_core` — regression here is a hard CI fail. Cannot be
  demoted to `exploratory` without a design-doc change.
- `tier: exploratory` — informational; counted in stable-pass rate but
  does not gate CI on individual regression.

## Running the bench

### Self-test (must pass before any real run)

```sh
helix_bench self-test
```

Runs:

1. 10 meta-test transcripts through Layer 1+2 (vacuous-discriminator
   rejections MT01–MT05, then 5 positive)
2. Property-based generators (100 cases each for read_before_write,
   scope_write_path, skill_tool_use, graph_edge_observed)
3. Golden-transcript schema check (9 goldens vs `transcript_schema.yml`)
4. Matcher-vacuity check against `banned-matcher-patterns.yml`

Exit 0 required before `helix_bench run` is permitted.

### Single row

```sh
helix_bench validate-row family-test/bench/conversations/C001-start-helix-project
helix_bench run         family-test/bench/conversations/C001-start-helix-project --determinism 3
```

### Routing evals only

```sh
helix_bench routing-evals family-test/bench/routing-evals/helix-positive.jsonl
```

### Full bench

```sh
helix_bench run --all --determinism 3
```

### CI

`just bench` drives the same surfaces. The CI workflow runs
`diff-to-category.py` against the PR's changed files, intersects with
`bench-categories.yml`, and executes the matched subset. Any unmatched
path → full bench. Touching SKILL.md → conversation + routing. Touching
`stop-at-triggers.yml` → stop_at rows only. Pure-docs → self-test only.

## Failure observability

On row failure the runner dumps to
`family-test/bench/failures/<row-id>-<timestamp>/`:

- `transcript.jsonl` — the raw stream-json
- `matcher-trace.json` — per-matcher input + verdict + diff
- `expected-vs-actual.diff` — structured diff of declared vs observed
- `negative-control.diff` — diff between positive and negative runs

These are the minimum artefacts to debug a flake without re-running.

## Costs (plan §19)

| Tier | When | Cost |
|---|---|---|
| `self-test` | every PR | $0 (synthetic) |
| Affected category | every PR | ~$2–$50 per run |
| Full bench | main merge | ~$45/run |
| Nightly thirds | rotating | ~$15/run avg |
| Weekly full + judge calibration | weekly | ~$50/run |

Monthly steady-state ~$1590. P0–P15 dev-iteration burn ~$1850 one-time,
tracked under a separate `dev_iteration_burn` ratchet so steady-state cost
is not conflated with setup.

## Ratchets (plan §19.4)

`ratchets.json` carries four streams:

- `stable_pass_rate` — alert on 5pp drop run-over-run
- `routing_precision` — alert on 2pp drop on the positive set
- `cost_per_run` — alert on 25% above baseline (rolling 30-day)
- `dev_iteration_burn` — informational; no automatic gate

Baselines are NULL until the first post-P14 main-merge full bench.

## Claude Code version pin

`cc-version.lock` pins the CC version we test against (currently `2.1.163`).
CI fails if the container CC version doesn't match. Re-validation cadence:
90 days OR when CC hits a trigger version (`2.2.x` / `2.1.200+`).

Golden transcripts double-protect against schema drift within a CC version
(events get added; tool_use shape evolves). Each golden carries its
`cc_version` and expected verdict; `--self-test` re-validates them on
every run.

## Halt conditions

Each phase has a halt condition. Selected:

- **P0**: meta-test < 10/10 OR property test fails OR runner accepts a
  vacuous discriminator. Halt — the bench itself is broken.
- **P1**: no description shape clears positives ≥29/30 AND negatives 30/30
  AND ambiguous ≥13/15 AND 0/15 unsafe. Halt — engagement approach needs
  rethink (likely slash-required mode or `when_to_use` adoption).
- **P3**: autonomy levels produce non-deterministic confirmation counts
  across 3 runs. Halt — SKILL.md §8 is not crisp enough.
- **P4**: auto-population fixture passes (skill silently writes
  `ddx.links` from graph). Halt — load-bearing invariant violation.

## See also

- [`flows.md`](flows.md) — what the bench is testing for
- [`autonomy.md`](autonomy.md) — what the matrix rows verify
- [`skill-author-guide.md`](skill-author-guide.md) — how to add a row in <30min
