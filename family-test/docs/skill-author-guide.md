# Skill-author guide — author a bench row in <30 min

This guide walks you through adding ONE new conversation row to the
HELIX-family bench. The plan §15c P15 acceptance test: a new operator can
ship a valid row + paired negative control + non-vacuous discriminator in
≤30 minutes.

Design record: [`docs/helix/02-design/plan-2026-06-05-conversation-bench-and-autonomy.md`](../../docs/helix/02-design/plan-2026-06-05-conversation-bench-and-autonomy.md) §1, §1.4b, §15c P5/P15.

## Before you start (1 min)

You need:

- Decide a row id and category. The naming convention:

  | Prefix | Category |
  |---|---|
  | `C0**` / `C1**` / `C2**` | conversation library (happy paths, cascading) |
  | `AM-**` | autonomy matrix |
  | `SA-**` | stop_at (positive or near-miss negative) |
  | `CD-**` | graph-discrimination |
  | `EA-**` | edge-authority asymmetry |
  | `CI-**` | cross-instance |
  | `WC-**` | warm-context |
  | `VS-**` | verbose-but-stuck |

- A claim. One concrete observable behaviour you want to lock in: "the
  skill engages on prompt X" or "the skill refuses to write when the
  marker forbids" or "the skill consults graph.yml before authoring."
- A negative control. What would make the assertion flip from
  positive→negative? Removing the plugin? Changing the marker? Swapping
  `graph.yml`?

If you can't name a negative control that flips the verdict, your row is
**vacuous** (Invariant 3) — the runner will reject it with T042.

## Step 1 — copy a template (2 min)

The closest existing row in your category is the best template.

```sh
cp -r family-test/bench/conversations/C001-start-helix-project \
      family-test/bench/conversations/C026-your-row-slug
cd family-test/bench/conversations/C026-your-row-slug
```

Rename / clear fields:

- `README.md` — write 5–10 lines: what this asserts, why, the negative
  control rationale
- `workspace/` — adjust to match your fixture (or `rm -rf workspace`
  and re-author)
- `plugins.txt` — list the plugins to install (typically just the flow
  plugin under test, e.g. `methodology-product`)
- `autonomy.yml` — set `default: guided` unless your row tests a level
- `conversation.yml` — your turns (multi-turn first-class)
- `expected.yml` — the assertions

## Step 2 — write the prompt (3 min)

```yaml
# conversation.yml
turns:
  - user: |
      <your user prompt here, exactly as the operator would type it>
```

Multi-turn:

```yaml
turns:
  - user: |
      First turn — sets context.
  - user: |
      Second turn — the actual probe.
    cwd: services/api      # optional per-turn cwd override
    autonomy_override: autonomous   # optional per-turn autonomy override
```

Tips:

- Keep prompts short and natural. The router learns from verb anchors;
  avoid jargon the description doesn't claim.
- For routing rows use `family-test/bench/routing-evals/<flow>-*.jsonl`
  instead (one JSON line per probe). The conversation directory is
  overkill for single-utterance routing.

## Step 3 — pick the discriminator (5 min)

Browse the assertion DSL whitelist:

```sh
cat family-test/bench/library/schemas/discriminator-whitelist.yml
```

9 ids available at v1:

| id | use when you want to assert ... |
|---|---|
| `skill_tool_use` | the skill (didn't) engage |
| `read_before_write` | the agent (didn't) read context before mutating |
| `graph_edge_observed` | the agent (didn't) consult `graph.yml` |
| `scope_write_path` | writes (escaped) the marker root |
| `next_action_envelope` | a structured next-action JSON was (not) emitted |
| `confirmation_before_mutation` | the agent (didn't) ask before mutating |
| `refusal_no_write` | the agent (didn't) refuse without writing |
| `literal_or_banner_text` | a specific phrase/banner (didn't) appear |
| `route_decision` | routing landed on the expected `(flow, instance)` |

If none fits, you may need a new id — but a new id is a methodology
contract change (whitelist + runner + meta-tests + meta-test transcript
update together). Try harder to fit an existing id first.

Write the block:

```yaml
discriminator:
  assertion_id: skill_tool_use
  observable:
    matcher_type: skill_tool_use
    skill_id: helix
  expected_in_positive_run: present
  expected_in_negative_run: absent
  negative_control:
    plugins_remove: [methodology-product]
    rationale: |
      Removing methodology-product unregisters the helix skill from
      Claude's routing surface entirely; the agent cannot emit a
      Skill(helix) tool_use. Verdict flips present→absent.
```

The runner enforces:

- T040 — must have a `discriminator:` block
- T041 — `assertion_id` must be in the whitelist
- T042 — positive verdict ≠ negative verdict (else vacuous)
- T043 — observable matcher must parse
- T044 — `negative_control` must actually change what the observable sees
- T046 — new id must be in whitelist before use
- T047 — matcher args must not match `banned-matcher-patterns.yml`

## Step 4 — write Layer 1 assertions (5 min)

Use `expected.yml`'s `structural:` block for programmatic checks. The
discriminator covers one observable; Layer 1 covers everything else you
want to lock in.

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
```

Keep Layer 1 tight — every regex/path-match is a precommitment. If you
must paraphrase, that's Layer 2.

## Step 5 — (optional) Layer 2 semantic checks (3 min)

Use `semantic.yml` (separate file) for paraphrase-tolerant intent checks.
Judged by the LLM rubric at `judge/rubric-prompt.md`.

```yaml
prose_must_include:
  - intent: "Offers to create a product vision as the first artifact"
prose_must_NOT_include:
  - intent: "Claims a flow is active that's not in the marker"
```

Be specific. "Mentions HELIX" is loose; "Offers to create a product
vision" is sharp.

## Step 6 — (optional) Layer 3 envelope (3 min)

Use `envelope.yml` for structured next-action assertions.

```yaml
next_action:
  offered:
    - draft_artifact: product-vision
    - add_methodology_to_marker: helix
  not_offered:
    - draft_artifact: prd
```

Layer 3 runs in a separate envelope pass to avoid contaminating Layer 1.
Skip it unless the next-action shape is load-bearing.

## Step 7 — tag tier + category (1 min)

At the top of `expected.yml`:

```yaml
tier: must_pass_core           # or: exploratory
category: conversation-library # or: autonomy / stop_at / graph_discrim / ...
phase: P5
status: authored-pending-verification
notes: |
  <2–3 lines on what this proves + why the discriminator is non-vacuous>
```

`tier: must_pass_core` is a strong claim — regression breaks CI. Use
`exploratory` when you're prototyping or the row is informational.

## Step 8 — validate (2 min)

```sh
python family-test/bench/runner/helix_bench.py validate-row \
       family-test/bench/conversations/C026-your-row-slug
```

The validator runs T040–T047 plus shape checks WITHOUT making model
calls. Common rejections:

- T042 "vacuous": same verdict positive/negative. Re-think the negative
  control.
- T047 "matcher_vacuous": you used `.*`, `^ok$`, or the literal `helix`.
  Tighten the pattern (≥20 chars for `literal_or_banner_text`).
- T044 "no-op negative-control": `plugins_remove:` doesn't actually
  unregister the relevant skill. Check `plugins.txt`.

Iterate until validate-row exits 0.

## Step 9 — smoke-run (3 min)

```sh
python family-test/bench/runner/helix_bench.py run \
       family-test/bench/conversations/C026-your-row-slug --determinism 1
```

Runs the positive AND negative-control passes once each. Check the
verdict; if your row fails, browse the failure dump:

```sh
ls family-test/bench/failures/
cat family-test/bench/failures/C026-*/matcher-trace.json
cat family-test/bench/failures/C026-*/expected-vs-actual.diff
```

## Step 10 — full determinism (2 min)

```sh
python family-test/bench/runner/helix_bench.py run \
       family-test/bench/conversations/C026-your-row-slug --determinism 3
```

A row is **stable-pass** iff 3-of-3 PASS. If it's flaky:

- Tighten Layer 1 regexes (paraphrase leaked into a structural check)
- Move borderline intents to Layer 2 (judge tolerates paraphrase)
- Check the judge calibration if Layer 2 is flaking

## Common mistakes (and how the runner catches them)

| Mistake | Caught by |
|---|---|
| No discriminator block | T040 |
| Used an `assertion_id` not in the whitelist | T041, T046 |
| Positive and negative verdicts are the same | T042 |
| Matcher pattern is `.*` or `helix` | T047 banned-pattern |
| Negative control doesn't actually flip the observable | T044 |
| Layer 1 regex too tight; Layer 1 too loose | smoke-run flake, or judge mismatch |
| Authored against the wrong flow plugin | row stable-fails at engagement |
| Forgot `plugins.txt` includes the flow plugin | engagement fails in positive run |

## Adding a new `assertion_id` (the methodology change path)

If no whitelisted id fits, you're proposing a methodology contract change.

1. Open a PR that ALSO updates:
   - `library/schemas/discriminator-whitelist.yml` (add the id +
     matcher_type + matcher_params + description)
   - `family-test/bench/runner/helix_bench.py` (implement the matcher;
     wire it into the matcher dispatch)
   - `family-test/bench/runner/meta-tests/` (add a vacuous + a positive
     transcript exercising the new id)
   - `family-test/bench/golden-transcripts/` (add a golden + meta.yml)
   - `library/schemas/banned-matcher-patterns.yml` (add minimum lengths or
     banned literals specific to the new id)

2. Run `helix_bench self-test`. The new id must be exercised by both a
   vacuous-rejection meta-test and a positive meta-test.

3. The PR title is a contract change — codex-review on it before merge.

## Adversarial data fixtures (helix-data only)

If you're authoring under `methodology-data`, your artifact may need to
reference one of the 11 adversarial fixtures (F1–F11). The example at
`family-test/examples/helix-data-customer-events/` is the reference.
`helix_check.py example --adversarial-coverage` enforces that every
F1–F11 is referenced by ≥1 artifact.

## See also

- [`flows.md`](flows.md) — what the flows do
- [`bench.md`](bench.md) — the assertion DSL, three layers, ratchets
- [`autonomy.md`](autonomy.md) — autonomy-aware rows
- [`../bench/library/schemas/discriminator-whitelist.yml`](../bench/library/schemas/discriminator-whitelist.yml)
- [`../bench/library/schemas/banned-matcher-patterns.yml`](../bench/library/schemas/banned-matcher-patterns.yml)
- An existing row in your target category (best living template)
