# Plan: Conversation-bench + Autonomy slider + Flow model

- **Date:** 2026-06-05 (revised in-turn with flow-model additions)
- **Status:** plan, awaiting review
- **Companions:**
  - [design-2026-06-04-helix-family-marker-and-linkages.md](./design-2026-06-04-helix-family-marker-and-linkages.md)
  - [validation-plan-2026-06-05-vertical-slice-completion.md](./validation-plan-2026-06-05-vertical-slice-completion.md)
  - [validation-results-2026-06-05.md](./validation-results-2026-06-05.md)
- **Trigger:** v2 Bucket A swept 8 probes in Docker. 7 of 8 showed `skill_calls = []` — the helix skill *loads* but does not *engage* on prompts like "Create a PRD for X." The agent authors from general knowledge, ignoring the marker. v1 and v2 both prove the marker / linkage architecture is sound when the skill engages; both fail to prove the skill engages reliably. This plan addresses three coupled gaps: a behavioural test corpus, the skill-engagement levers themselves, and an autonomy slider that controls how aggressively the engaged skill proceeds.

## What this plan covers

1. **The conversation bench** — a corpus of utterances + expected behaviour the family validates against. Replaces the ad-hoc Bucket A probe set with a growable library.
2. **Skill engagement repair** — the `description:` keyword surface, slash commands, routing evals, and the skill-router contract. Without this, no marker matters.
3. **Cascading flow logic** — the graph used at *runtime* (not just validation): when user asks for type X, the skill consults `graph.yml` for prerequisites and either authors them or offers to.
4. **Autonomy slider** — a sibling-to-marker declaration that controls ask-vs-do behaviour. Skill+documents say *what's next*; autonomy says *whether to ask before doing it*.
5. **Flow model (new — §11–§14)** — promote "methodology" to "flow" in terminology and schema; add the missing **data-pipeline** flow; let a single flow be **instantiated multiple times** in one repo; and define how flows **share documents** when they cooperate.

These five are tightly coupled: the bench tests engagement, engagement enables cascading, cascading is shaped by autonomy, and all of it runs over a family of cooperating flows (not a single methodology).

## §0.5 Named invariants (load-bearing, copy into design doc §2.7–§2.9)

Three principles that govern every section below. Buried in prose elsewhere; promoted to first-class names here so the bench runner and validator can refuse work that violates them.

**Invariant 1 — Edge Authority Asymmetry.** Types declare what's *possible*. Instances declare what's *actual*. The skill is the *deliberator* between them. The skill MUST NOT mechanically populate `ddx.links` from graph edges; every instance edge requires a deliberate authoring decision. Auto-populating ddx.links from graph candidates is a contract violation regardless of autonomy level. The bench includes negative-control rows that catch any future code path that auto-fills instance edges from type definitions (see §1.5b row category "edge-asymmetry").

**Invariant 2 — Engagement Precedes Authority.** Marker authority, scope enforcement, and cascade logic are all meaningless until the skill *engages*. A bench claim like "the marker rejected /helix-infra" is only sound if the skill engaged in the first place. P1 (engagement gate, §6) is the floor; every downstream phase verifies engagement first, then the downstream behaviour. The runner refuses to execute a conversation that asserts downstream behaviour without first asserting engagement.

**Invariant 3 — Discriminating Tests Only.** Every bench row must distinguish skill-correct behaviour from skill-absent behaviour. A row that passes whether the skill engaged or not is noise. Every conversation in §1.5 / §1.5b carries a **paired negative control** — same prompt, plugin uninstalled or marker absent — that MUST produce a different observable outcome. The runner rejects conversations that ship without a discriminator at load time (T040 error).

## What this plan does NOT cover

- The remaining v2 Bucket A probes (a2-a7) — they're real defects but blocked on engagement first.
- Bucket C frontmatter round-trip — also blocked on engagement.
- The stdlib-only validator port — pure mechanical follow-up.
- Real monorepo reorganization — happens after this plan delivers, not before.

---

## §1 The conversation bench

### 1.1 What it is

A growable corpus of *behavioural contracts*: each entry is a user utterance (or short conversation), an expected agent behaviour, and the runtime context (marker state, autonomy level, plugins). The bench is the regression suite for skill engagement and the iteration surface for prompt/SKILL.md tuning.

The existing `tests/fixtures/family/T*/` matrix tests **the validator** (does a static analyzer catch contract violations?). The conversation bench tests **the agent** (does it route, engage, and offer the right next step?). These are complementary, not competing.

### 1.2 Per-conversation layout

```
family-test/bench/conversations/
└── C001-lets-start-a-helix-project/
    ├── README.md                 # what this scenario asserts and why
    ├── workspace/                # the repo the agent sees (.helix.yml + tree)
    ├── plugins.txt               # plugins to install (library + methodologies)
    ├── autonomy.yml              # autonomy level for this run (optional)
    ├── conversation.yml          # one or more user prompts (multi-turn)
    └── expected.yml              # structural + semantic assertions
```

### 1.3 `conversation.yml` shape

```yaml
turns:
  - user: |
      Let's start a helix project for a coffee-ordering app.
    # Optionally:
    # autonomy_override: guided  # override the workspace's autonomy.yml for this turn
    # cwd: services/api          # change cwd inside the workspace for this turn
```

Multi-turn conversations are first-class. Turns alternate user → agent; the runner replays the prior turns' assistant outputs as conversation history when sending each new user turn.

### 1.4 `expected.yml` shape — the assertion model

Three layers, layered loose-to-strict. A conversation must satisfy ALL layers it declares.

**Each conversation MUST carry a discriminator** per Invariant 3 (§0.5). Codex's blocking finding #2 (2026-06-05): a prose discriminator is shape-correct but meaning-vacuous. Replace with a **typed assertion DSL**:

```yaml
discriminator:
  # Required: assertion_id from the whitelist (§1.4b)
  assertion_id: skill_tool_use                     # one of the whitelist
  # The SAME observable query runs in positive AND negative.
  observable:
    matcher_type: skill_tool_use
    skill_id: helix
  # Verdicts must be opposite in positive and negative runs:
  expected_in_positive_run: present
  expected_in_negative_run: absent
  # Negative-control modification (auto-applied by runner):
  negative_control:
    workspace: same
    plugins_remove: [methodology-product]          # methodology plugin REMOVED
```

The runner enforces (T040-T044):
- **T040**: missing `discriminator:` → reject row
- **T041**: `assertion_id` not in whitelist → reject row
- **T042**: `expected_in_positive_run == expected_in_negative_run` → reject as vacuous
- **T043**: observable matcher unparseable → reject row
- **T044**: negative-control modification doesn't actually change the observable's input class → reject as no-op

A row PASSES only if positive run produces `expected_in_positive_run` AND negative-control run produces `expected_in_negative_run`. If both produce the same outcome regardless of skill presence, the discriminator is meaningless and the bench refuses to grade it.

### 1.4b Discriminating observable whitelist (typed assertion DSL)

The set of allowed `assertion_id` values, each tied to a specific matcher type. The runner's loader validates against this whitelist:

```yaml
# library/schemas/discriminator-whitelist.yml
allowed_assertions:
  - id: skill_tool_use
    matcher_type: skill_tool_use
    matcher_params: [skill_id]              # required
    description: |
      Asserts a Skill(<skill_id>) tool_use event appears in stream-json.
      Positive: present; negative-control: absent (after plugin removal).

  - id: read_before_write
    matcher_type: tool_use_order
    matcher_params: [first_tool, second_tool, target_pattern]
    description: |
      Asserts a Read(target_pattern) tool_use appears at an earlier index
      than any Write/Edit. Positive: ordered; negative-control: absent or
      reversed.

  - id: graph_edge_observed
    matcher_type: file_read
    matcher_params: [graph_path, expected_edge_signature]
    description: |
      Asserts the agent read the methodology graph.yml file. The
      negative-control swaps the workspace's graph.yml for one lacking
      the expected_edge_signature; positive must still surface the edge,
      negative must NOT surface it (proves graph drove the answer, not
      training).

  - id: scope_write_path
    matcher_type: write_path_constraint
    matcher_params: [allowed_root, forbidden_pattern]
    description: |
      Asserts all Write/Edit tool_use file_paths fall under allowed_root.
      Negative-control: plugin removed; agent's writes WILL escape root
      (proving the marker drove the constraint, not general intuition).

  - id: next_action_envelope
    matcher_type: json_envelope
    matcher_params: [envelope_schema_path]
    description: |
      Asserts the agent emits a JSON envelope conforming to schema.
      Layer 3 only — runs in a separate envelope pass (§1.4 ordering
      constraint).
```

Codex's "vacuous discriminator" meta-tests (added to the meta-tests category in §1.5b; 5 of the 10 are now intentionally vacuous discriminators):

| Meta-test | What it checks |
|---|---|
| MT01 | discriminator with `expected_in_positive == expected_in_negative` → runner rejects (T042) |
| MT02 | discriminator with unknown `assertion_id` → runner rejects (T041) |
| MT03 | discriminator missing `negative_control` → runner rejects (T040) |
| MT04 | discriminator where `plugins_remove` doesn't include any methodology plugin → runner rejects (T044) |
| MT05 | discriminator whose observable is structurally valid but the matcher always matches every transcript → runner rejects (T043 by static check + smoke run) |

The remaining 5 meta-tests are positive synthetic transcripts that exercise each whitelisted `assertion_id` correctly. The runner's `--self-test` mode runs all 10 before every bench run; CI gate halts on any failure.

```yaml
# Layer 1 — STRUCTURAL (programmatic; never flaky)
structural:
  skill_invoked:                    # the skill MUST be called via the Skill tool
    - name: helix
      # Optionally pin the args slot:
      args_pattern: "frame|discover|intent"
  no_skill_invoked: []               # the skill MUST NOT be called (negative control)
  tools_used_at_least:               # this tool must appear at least once
    - Read: { path_pattern: ".helix.yml$" }
  tools_used_at_most:                # NO Write/Edit outside this glob (scope guard)
    Write:
      forbidden_path_pattern: ".*"
      allowed_path_pattern: "docs/helix/.*\\.md$"
  first_relevant_tool:               # the FIRST tool of these names must match
    candidates: [Read, Bash]
    must_match_path_pattern: "(\\.helix\\.yml|git rev-parse)"
  writes_exactly:                    # exact file paths (for one-shot autonomous probes)
    - "docs/helix/00-discover/product-vision.md"
  result_is_error: false

# Layer 2 — SEMANTIC (judge LLM; deterministic temperature=0)
semantic:
  prose_must_include:
    - intent: "Offers to create a product vision as the first artifact"
      not_exact_string: true        # judge can match paraphrase
    - intent: "Names the active methodology (helix) and why it activated"
  prose_must_NOT_include:
    - intent: "Mentions adding a non-helix methodology (e.g. helix-infra)"
    - intent: "Claims a methodology is active that's not in the marker"

# Layer 3 — NEXT-ACTION (the cascade)
next_action:
  offered:                           # the agent explicitly offers (or executes) ONE of these
    - draft_artifact: product-vision
    - add_methodology_to_marker: helix
  not_offered:
    - draft_artifact: prd            # PRD requires vision first; should NOT be offered ahead
```

Layer 1 is regex/path-match against stream-json — never flaky if the underlying behaviour is deterministic. Layer 2 uses a judge LLM at `temperature=0` with a structured rubric prompt; flakier but covers paraphrase. Layer 3 is a structured-output assertion that requires the agent to emit a JSON envelope alongside prose (we wire this via a `--system-prompt-file` instruction the bench runner injects, OR via the autonomy contract — see §4.6).

**Layer ordering constraint (anti-contamination).** Layer 3's system-prompt injection (the JSON envelope) changes the agent's behaviour. To prevent Layer 3 from contaminating Layer 1 results, the runner executes Layer 1 + Layer 2 in a "no-envelope" pass and Layer 3 in a separate "envelope" pass per conversation. Both passes must satisfy their layers independently; if a conversation declares Layer 3, it runs twice. Layer 1 outcomes in the envelope pass are recorded but only the no-envelope outcomes count toward the row's pass/fail. Cost trade-off acknowledged: rows declaring Layer 3 double their model calls; budget §19 accounts for this.

### 1.5 Initial corpus — what we seed v1 with

| ID | Utterance | Workspace state | Active flows | Autonomy | Expected behaviour |
|---|---|---|---|---|---|
| C001 | "Let's start a helix project for a coffee-ordering app" | empty | none | guided | Skill fires; explains HELIX briefly; offers to add product flow marker + create product-vision |
| C002 | "Let's create a PRD" | empty | none | guided | Skill fires; "no marker" diagnostic; offers to add product flow + create vision (PRD's prereq) |
| C003 | "Let's create a PRD" | has product-vision but no marker | none | guided | Skill fires; offers to add product flow marker; PRD draft proceeds with vision as informs |
| C004 | "Let's create a PRD" | marker active, vision exists | helix | guided | Skill fires; drafts PRD that informs from vision; ddx.links populated |
| C005 | "Let's create a PRD" | marker active, no vision | helix | guided | Skill fires; surfaces vision-prerequisite; offers to draft vision first |
| C006 | "Let's create a PRD" | marker active, no vision | helix | autonomous | Skill fires; drafts vision THEN PRD without asking |
| C007 | "Let's create a website" | empty | none | guided | Skill fires; offers to add helix-web methodology + create page-spec/IA artifact |
| C008 | "Let's manage our infrastructure" | empty | none | guided | Skill fires; offers to add helix-infra + create change-intent |
| C009 | "Let's deploy the site" | helix-web marker active, build complete | helix-web | guided | Skill fires; routes to deploy activity within helix-web (NOT helix-infra) |
| C010 | "Let's deploy the site" | both helix-web and helix-infra active, site at services/web/ | both | guided | Skill fires; cwd-disambiguates to helix-web's deploy flow |
| C011 | "What methodologies are active here?" | marker has helix + helix-infra | both | any | Skill fires; literal answer derived from marker (NOT prose guess) |
| C012 | "Create an ADR for choosing Postgres" | helix active, no vision/PRD yet | helix | guided | Skill fires; ADRs are cross-cutting and OK without upstream artifacts; drafts ADR with empty depends_on chain |
| C013 | "Update the PRD to add a new requirement" | PRD-001 exists | helix | guided | Skill fires; Edit (not Write); preserves frontmatter byte-equivalent; ddx.links unchanged |
| C014 | "/helix-infra intent: rotate the provider" | marker has helix only | helix | guided | Skill REJECTS; cites marker as authorization boundary; no write |
| C015 | "What's next?" | helix marker, vision exists, no PRD | helix | guided | Skill fires; reads graph; suggests PRD as the next downstream node |
| C016 | "Plan the rollout" (ambiguous) | both helix and helix-infra active | both | guided | Skill fires; disambiguation banner; asks which flow |
| C017 | (same as C016) | both active, autonomy=autonomous | both | autonomous | Skill picks defaults.methodology from marker without asking |
| C018 | "Let's iterate on the current sprint" | helix active, multiple PRDs | helix | guided | Skill fires; routes to 06-iterate activity; offers metrics-dashboard or improvement-backlog |
| C019 | (random non-methodology question) "What's the population of Tokyo?" | helix active | helix | guided | Skill does NOT fire (negative control — random questions don't engage methodology) |
| C020 | "Help me understand HELIX" | empty | none | guided | Skill fires; explains the methodology; offers to set up a marker |

20 entries cover: positive engagement (C001-C010, C012, C015, C018, C020), cascading prerequisites (C002, C003, C005, C006), authorization boundary (C014), autonomy gradient (C006, C017 vs C005, C016), negative control (C019), multi-flow disambiguation (C009, C010, C016, C017), surface-naming (C011).

### 1.5b Corpus inventory — what v1 ships (150 rows, by category)

The 20 entries above are the happy-path seed. Full v1 corpus inventory by verification target:

| Category | Rows | What it verifies |
|---|---|---|
| **Routing evals (positive)** | 30 | Each row: prompt → expected Skill tool_use within 2 events. 95% precision required. Hand-authored across 4 flows × multiple verb shapes. |
| **Routing evals (negative control)** | 30 | Each row: prompt → NO Skill tool_use. 100% recall required. "What's Tokyo's population", "Debug this regex", "Write a SQL query", etc. Catches over-eager routing. |
| **Routing evals (ambiguous, multi-flow)** | 15 | Each row: prompt could plausibly match 2+ flows; assertion specifies which wins per §1.5 resolution chain. |
| **Conversation library (happy paths)** | 25 | C001-C025 from §1.5 + §12.6 (full 25, including helix-data rows). Each carries a paired negative control per §0.5 Invariant 3. |
| **Autonomy matrix** | 8 | 2 fixtures × 4 levels (manual/guided/autonomous/aggressive). Same prompt; assert confirmation count and write count differ per level deterministically. |
| **Stop_at triggers (positive + near-miss negative)** | 12 | Per codex finding #5: 6 positive rows (one per trigger: marker_edit, cross_methodology_edge_creation, branch_or_merge, secret_read, large_diff, apply) + **6 paired near-miss negatives** (`.env.example` must NOT fire secret_read; `terraform plan` must NOT fire apply; 499-line edit must NOT fire large_diff; `gh pr view` / `git status` must NOT fire branch_or_merge; non-cross-instance link must NOT fire cross_methodology_edge_creation; Read/Bash on `.helix.yml` (not Write) must NOT fire marker_edit). Each positive proves matcher fires; each negative proves matcher avoids false positives. |
| **Graph-discrimination** | 4 | Custom non-standard edge in graph.yml (e.g., `library:prd requires library:market-validation-brief`). Positive: agent surfaces the unusual prerequisite (proves graph was read). Negative: same workspace without the edge, agent must NOT surface it. Confirms the cascade logic actually consults graph.yml rather than relying on general HELIX knowledge. |
| **Edge Authority Asymmetry** | 4 | Per §0.5 Invariant 1. Graph: `prd informs feature-specification` (required: false). Workspace: existing FEAT-001, FEAT-002. Prompt: "Create a PRD." PASS if agent surfaces candidate links and asks. FAIL if agent silently auto-populates ddx.links. Run at autonomy=guided AND autonomy=autonomous; assertion contract: even autonomous requires deliberation, not auto-fill. |
| **Cross-flow cascade** | 3 | §14.1 scenarios: PRD-needs-infra (helix → helix-infra), pipeline-needs-DNS (helix-data → helix-infra), "what's blocked" (multi-flow status query). |
| **Multi-instance routing** | 6 | Cwd-resolution algorithm verification per §13.6b: (1) no match falls through, (2) single match, (3) nested roots — longest wins, (4) boundary, (5) sibling-tie with env override, (6) sibling-tie without env — emits banner, asks user. Sibling-tie path-component matching specifically (codex #6) MUST NOT silently auto-select alphabetically. |
| **Cross-instance lineage** | 3 | C027 plus 2 more: stale-target detection (target instance superseded), instance-rename impact analysis. |
| **Rename / v1-compat** | 4 | M020 legacy-key alias fires; existing T01-T38 fixtures still pass; fresh v2 marker with `flows:` validates; migration script v1→v2 idempotent. |
| **Warm-context** | 5 | Replay 5 unrelated turns of conversation history before sending the probe. Each: a conversation row from the happy-path set, asserted to still engage despite context dilution. |
| **Verbose-but-stuck** | 4 | Skill engages (Skill tool_use fires) but skips reading marker/graph before writing. Assertion: NO Write tool_use occurs before BOTH Read(.helix.yml) AND Read(graph.yml) appear in the stream. Catches the v2 evidence failure mode where helix loaded but didn't gate writes on context. |
| **Meta-tests (synthetic agent responses)** | 10 | Hand-author 5 "should pass" and 5 "should fail" fake stream-json transcripts. Run them through the Layer 1 + Layer 2 assertion engine. Human classification MUST agree with assertion verdict on ≥9/10. Confirms the bench itself isn't broken before we trust it on real runs. |

**Total: 150 rows.** Authoring effort: ~50h (routing evals are fast at ~5min each; conversations are ~20min each with the paired-negative requirement; matrix/trigger/discrimination rows are ~15min each from templates). Reflected in §6 sequencing P0–P15.

This inventory is the v1 ship requirement, NOT aspirational. Each row has a named verification target above; the bench runner's manifest lists them by category and refuses to skip a category at CI gate time.

### 1.6 What "pass" means

A conversation PASSES iff:
- Layer 1 assertions ALL hold (programmatic, deterministic)
- Layer 2 assertions ALL pass via judge LLM with `judge_confidence >= 0.8` AND `agreement_2_of_3` if we re-judge (avoids judge flakiness for borderline cases)
- Layer 3 assertions hold

A bench RUN reports per-conversation pass/fail, an aggregate pass rate, and a per-conversation evidence dump under `family-test/probe-evidence/bench/C<id>/`.

A bench BATCH (used in CI / iteration) runs each conversation N times (`--determinism N`, default 3) and reports flakiness (PASS in N-of-N vs P-of-N). Flake-tolerant policy: a conversation is "stable-pass" iff N-of-N runs PASS. "Flaky" if P-of-N for P < N but > 0. "Stable-fail" if 0-of-N. CI gates on stable-pass; flakes route to an investigation queue.

### 1.7 Bench is a corpus, not a contract

The bench is a *living* corpus we add to as defects surface. It is NOT a fixed contract the design must hit. The right framing: each conversation is a hypothesis about what the family should do, and the bench tells us where reality diverges. When reality wins (e.g., we accept that "what's the population of Tokyo" should sometimes engage the skill for context-establishment), we update the expectation. The bench is not infallible authority; the methodology and the user's judgement are.

### 1.8 Why not generative?

We could LLM-generate conversation candidates and have a judge score them. Tempting, but premature: we don't yet trust the engagement signal, so generated tests would mostly test the generator. v1 corpus is hand-authored; once we have a stable engagement floor, v2 corpus can grow via LLM augmentation with human review.

---

## §2 Skill engagement repair

### 2.1 Why engagement fails today

v2 probe sweep evidence:
- `skill_calls = []` in 7 of 8 probes
- A1 prompt "Create a PRD for a coffee-ordering service" → agent writes a PRD straight from general knowledge
- A4 prompt "/helix-infra intent: …" → Claude responds "Unknown command: /helix-infra"

Two diagnoses, one for each failure mode:

**a) The skill's `description:` field doesn't claim the work.** SKILL.md says:

> HELIX product methodology. Activates when `.helix.yml` lists `helix` as active OR when fallback heuristics fire. Distinct from the helix-library skill, which is data-only.

That's a positioning statement, not a router input. Claude's skill router scans descriptions for keyword anchors when deciding which (if any) skill matches a user prompt. "Create a PRD" doesn't match any noun in the description. So the router doesn't surface helix to Claude as a candidate skill.

**b) Slash commands aren't registered.** A4 expected `/helix-infra` to be a routable slash command. Claude reports "Unknown command" because we never declared it. Slash commands are first-class in the plugin manifest and have to be wired explicitly.

### 2.2 The fix — description as anchor surface

Rewrite SKILL.md frontmatter to surface the verbs and nouns the router needs:

```yaml
---
name: helix
description: |
  HELIX product methodology — drives the family's product flow.

  Activate this skill when the user asks to:
    - start, begin, or scaffold a helix project
    - create, draft, write, or edit a PRD (Product Requirements Document)
    - create, draft, write, or edit a product vision, opportunity canvas,
      feature specification, user story, ADR, technical design, test plan,
      runbook, or release notes
    - frame, design, test, build, deploy, or iterate on a product
    - plan a sprint or rollout for product work
    - review or audit a product methodology artifact
    - answer "what's next" in a product workflow

  Do NOT activate for infrastructure work (terraform/opentofu), website
  content authoring, or sales/ops work — those are sibling skills
  (helix-infra, helix-web, etc.).

  Distinct from helix-library (a data-only catalog plugin).
version: 0.2.0
license: MIT
---
```

The key change: the description LISTS the verbs and nouns. Claude routes a user prompt to the skill with the highest description match. "Create a PRD" now matches; "Update the PRD" matches; "What's next?" matches when combined with "product workflow" context.

### 2.3 Slash commands as the explicit override

Even with strong descriptions, users may want guaranteed routing. Wire slash commands in `.claude-plugin/plugin.json` (or whatever the current spec uses):

```json
{
  "name": "helix",
  "version": "0.2.0",
  "skills": "./skills/",
  "slashCommands": [
    {"name": "helix",         "description": "Engage HELIX (auto-route by verb)"},
    {"name": "helix-frame",   "description": "Engage HELIX framing (PRD, FEAT, US)"},
    {"name": "helix-design",  "description": "Engage HELIX design (ADR, TD)"},
    {"name": "helix-iterate", "description": "Engage HELIX iterate (metrics)"},
    {"name": "helix-review",  "description": "Audit a HELIX artifact"}
  ]
}
```

helix-infra ships `helix-infra`, `helix-infra-intent`, `helix-infra-plan`, `helix-infra-apply-verify`. helix-web ships `helix-web`, `helix-web-design`, `helix-web-build`, `helix-web-deploy`.

Slash-command names MUST be globally unique across installed plugins. Per the v1 implementation plan's open question (slash-namespace ADR, deferred to v1.1), we use plugin-prefixed names (`helix-frame` not `frame`) to avoid collisions. C014's expected rejection of `/helix-infra` works because the slash command IS registered by helix-infra but the marker forbids activation; the skill enforces the marker check.

### 2.4 Routing evals — `evals/routing.jsonl`

Per the integration-test contract memory ([[project_skill_integration_test_contract]]): assert skill ACTIVATION via stream-json tool_use + negative control. Apply that pattern here.

Each methodology plugin ships `evals/routing.jsonl`:

```jsonl
{"prompt": "Create a PRD for a coffee app", "expected_skill": "helix"}
{"prompt": "Draft an ADR for choosing Postgres", "expected_skill": "helix"}
{"prompt": "What's next in this project?", "expected_skill": "helix", "context": "product-shaped repo"}
{"prompt": "Add a Cloudflare DNS zone for example.com", "expected_skill": "helix-infra"}
{"prompt": "Rotate the AWS provider version", "expected_skill": "helix-infra"}
{"prompt": "Build a marketing site for our launch", "expected_skill": "helix-web"}
{"prompt": "Deploy the docs site to Cloudflare Pages", "expected_skill": "helix-web"}
{"prompt": "What's the population of Tokyo?", "expected_skill": null}
{"prompt": "Help me debug a regex", "expected_skill": null}
```

The bench runner reads these and runs a low-overhead probe per row: invoke claude with all family methodology plugins installed, send the prompt, parse for which `Skill(...)` tool_use fires. Assert it matches `expected_skill` (or null = no skill engaged).

This is a fast loop (~1s per row when batched) and gives us a real routing signal. Aim for 100+ rows by v1 ship, growing as defects surface.

### 2.5 Wired into existing test surfaces

- `family-test/bench/routing-evals/<methodology>.jsonl` lives next to `conversations/`
- `bash family-test/bench/run-routing-evals.sh` runs them all
- `just bench` runs routing evals + the conversation bench
- CI gates on `--strict` mode: routing eval pass rate >= 90%, conversation bench stable-pass rate >= 80% (initial; bump as iteration improves things)

### 2.6 What we expect to land

After §2 implementation, A1 should reliably fire `Skill(helix)` and respect the marker. A4's `/helix-infra` should be a recognized slash command. The v2 sweep should go from 1/8 to 6/8 or 7/8 passing. Remaining failures are then *real* skill-prompt defects (§3 cascade logic gaps) rather than engagement failures.

---

## §3 Cascading flow logic — graph at runtime

### 3.1 What this fixes

C002 and C005 fail today because the skill doesn't know that a PRD requires a vision. The information IS in `graph.yml` (the `informs` and `requires` edges) but the skill prose doesn't *consult* it.

When the user says "let's create a PRD" with autonomy=guided:

1. Skill engages (§2)
2. Skill reads `.helix.yml`, identifies active methodology (helix)
3. Skill reads helix's `graph.yml`
4. Skill looks up the node for `library:prd`
5. Skill finds incoming `requires` and `informs` edges: `product-vision informs prd` (`required: true`)
6. Skill checks the instance index for `library:product-vision` instances; finds none
7. Skill SURFACES the prerequisite: "A PRD's framing is informed by a product vision. None exists yet. Want me to draft a vision first, then the PRD?"

This is the graph used as runtime routing aid, not just as validator input.

### 3.2 SKILL.md additions

Section §1 (Locate the marker) already lands. Add a new §7 to SKILL.md:

> **§7 Consult the graph before authoring.**
>
> When the user asks for a new artifact of type `T` in the active methodology M:
>
> 1. Read M's `workflows/graph.yml`.
> 2. Find the node `n` where `n.type` matches `library:T` or `local:T`.
> 3. Enumerate incoming edges to `n` with `kind` in `{requires, contains, informs}`.
> 4. For each such edge `(src → n, kind, required)`:
>    - If `required: true` AND no instance of `src.type` exists in this methodology's scope, surface this as a prerequisite. Per the autonomy slider (§8), either ask whether to draft `src` first, or draft it autonomously.
>    - If `required: false` AND no instance of `src.type` exists, note it as a "consider also drafting" but do not block.
> 5. Once prerequisites are present (or the user has chosen to skip them), proceed to author the requested artifact.
> 6. After authoring, populate `ddx.links` to point at the upstream instances. Do NOT invent links; only link to existing instances unless `status: planned` is acceptable per the marker.

### 3.3 Adding methodology to marker (cascading flow trigger)

C001 / C002 scenario: user asks for HELIX work in a repo with no `.helix.yml`. Per §2 the skill engages; per autonomy=guided the skill offers to add the marker before doing anything else:

```
This repo has no .helix.yml. I'll add one for the product flow so HELIX
methodologies can run here. The file declares which flows are active
and where their artifacts live.

Proposed .helix.yml:

    helix_version: 1
    methodologies:
      - id: helix
        root: docs/helix/

OK to add this?
```

Under autonomy=autonomous, the skill just adds the marker and proceeds. Under autonomy=manual, the skill stops and asks for explicit confirmation. See §4.

### 3.4 Multi-methodology detection from prompts

C007 ("Let's create a website") and C008 ("Let's manage our infrastructure") engage helix's skill router via the description's catch-all "do NOT activate for" clauses pointing at sibling skills. The right behaviour: each methodology's SKILL.md description claims its own verbs. helix-web's description claims "website, page-spec, IA, design system." helix-infra's claims "terraform, tofu, infrastructure, cloudflare, DNS."

When the user prompt matches helix-web's verbs and helix-web is NOT in the marker, the helix-web skill (when installed) should engage, detect the missing marker entry, and offer to add it — same pattern as §3.3 but for a different methodology.

When ambiguity is real (C010, C016: both helix-web and helix-infra could plausibly own "deploy the site"), §1.5 resolution chain applies: cwd-under-scope wins; otherwise the disambiguation banner asks the user.

---

## §4 Autonomy slider

### 4.1 What it is

An orthogonal declaration alongside the marker: *given that a methodology is active, how aggressively should the skill proceed without asking?* The skill+documents define WHAT's next; autonomy defines WHETHER to ask before doing it.

### 4.2 Where it lives

Layered config, resolved in order (last wins):

1. **Repo default** — `.helix.yml` carries an optional `autonomy:` key (committed, team-level baseline)
2. **User local** — `~/.config/helix/autonomy.yml` (per-user override, never committed)
3. **Repo user local** — `.helix-autonomy.yml` in the repo root (gitignored, per-user-per-repo override)
4. **Env var** — `HELIX_AUTONOMY=<level>` (per-invocation override; CI uses this)
5. **Prompt prefix** — `/helix-autonomous frame ...` (per-prompt override, see §4.5)

Default if none set: `guided`.

The marker (committed) declares which flows are ACTIVE (a structural team decision); autonomy declares how the agent operates within those flows (often a personal preference, sometimes a team policy). Splitting the files lets each be set/version-controlled at the right granularity. Combining them into `.helix.yml` was considered and rejected: per-user autonomy preferences would otherwise either pollute the committed marker or be untrackable.

### 4.3 Levels

| Level | What the skill does | When to use |
|---|---|---|
| `manual` | Engages, reads context, surfaces *what would happen*. Asks for explicit confirmation before ANY tool use (Read, Write, Edit, Bash). | Learning the methodology, building trust, security-sensitive contexts. |
| `guided` (default) | Engages, reads context freely, asks before any Write/Edit/Bash that changes state. Cascade prerequisites are surfaced and asked about. | Day-to-day human-in-the-loop work. |
| `autonomous` | Engages, reads, writes, cascades automatically. Stops only at irreducible decisions (e.g. choosing between two equally-valid graph routes; ambiguous methodology activation). | Trusted automation; CI; one-shot deliveries with known scope. |
| `aggressive` | Engages, marches through the entire methodology graph autonomously, only stopping at unrecoverable ambiguity or external-resource gates (e.g. needs a secret you haven't provided). | Demos, batched bootstrap, dry-runs. Carries risk; not a default. |

A fifth level `off` disables autonomy declaration entirely — the skill behaves as if no autonomy file existed (which today means `guided`). Used to neutralize a layered config without removing it.

### 4.4 Schema

```yaml
# .helix-autonomy.yml or repo-default in .helix.yml under `autonomy:`
autonomy:
  default: guided                    # required
  per_methodology:                   # optional, overrides default for a methodology
    helix:        guided
    helix-infra:  manual             # extra caution on infra
    helix-web:    autonomous
  per_activity:                      # optional, overrides for an activity name
    "01-frame":   guided
    "05-deploy":  manual             # never auto-deploy
  stop_at:                           # specific events ALWAYS pause regardless of level
    - cross_methodology_edge_creation
    - marker_edit                    # adding methodology to .helix.yml
    - branch_or_merge                # git state changes
    - secret_read                    # accessing .env / credentials files
```

`stop_at` is a per-repo list of HARD stops the skill must always confirm before executing, regardless of level. It's the safety net under aggressive automation.

### 4.5 Per-prompt override

Two surfaces:

- **Slash prefix**: `/helix-autonomous frame draft a vision and PRD for X` engages helix at level=autonomous for this turn only. `/helix-manual` forces manual mode.
- **Env var**: `HELIX_AUTONOMY=autonomous claude -p "..."` for headless / CI runs.

The prefix is per-turn (one prompt). The env var is per-invocation (lifespan of the claude process).

### 4.6 How the skill consults autonomy

Add SKILL.md §8:

> **§8 Apply the autonomy level.**
>
> Before any tool use that mutates state (Write, Edit, Bash that writes, git, install), determine the effective autonomy:
>
> 1. Read the per-prompt override (slash prefix or `HELIX_AUTONOMY` env).
> 2. If absent, read `.helix-autonomy.yml` from the repo root.
> 3. If absent, read `~/.config/helix/autonomy.yml`.
> 4. If absent, read `.helix.yml`'s `autonomy:` block.
> 5. Default to `guided` if no source defines it.
>
> Then dispatch:
>
> - `manual` → state the proposed action, list its effects, ask "OK to proceed?"
> - `guided` → state the proposed action briefly, ask before *first* state-changing tool use of this conversation. Subsequent state-changing tool uses within the same turn proceed silently UNLESS the action touches a `stop_at` event.
> - `autonomous` → proceed without asking; surface results after the fact. Stop on `stop_at` or irreducible ambiguity.
> - `aggressive` → as `autonomous` but also takes initiative across the full graph (e.g. drafts ALL prerequisites + the requested artifact in one pass).

The bench tests this matrix via conversations C005 (guided, asks) vs C006 (autonomous, just does) vs C017 (autonomous, multi-flow disambiguation).

### 4.7 Stop-at semantics

`stop_at` events the skill MUST always confirm. Each trigger is a precise pattern the validator, bench, and skill all consult from a single committed file:

`library/skill-prompts/stop-at-triggers.yml`:

```yaml
triggers:
  - id: marker_edit
    matcher:
      tool_use_name: [Write, Edit]
      file_path_pattern: '(^|/)\.helix\.yml$|(^|/)\.helix-autonomy\.yml$'
    rationale: Marker is a load-bearing team decision; never edit without confirmation.

  - id: cross_methodology_edge_creation
    matcher:
      tool_use_name: [Write, Edit]
      content_must_match: 'cross_methodology:\s*true|cross_instance:\s*true'
    rationale: Cross-method coupling deserves an explicit moment.

  - id: branch_or_merge
    matcher:
      tool_use_name: Bash
      command_pattern: '^\s*(git\s+(checkout|merge|push|reset|rebase|cherry-pick)|gh\s+pr\s+(merge|create))'
    rationale: Hardly anything the skill should auto-do at the git level.

  - id: secret_read
    matcher:
      tool_use_name: [Read, Bash]
      target_pattern: '\.env(\.|$)|\.tfvars$|credentials\.json$|\.pem$|id_rsa(\.pub)?$|private_key|\.key$|secrets/'
    rationale: Even in autonomous mode, secrets are a stop.

  - id: large_diff
    matcher:
      tool_use_name: [Write, Edit]
      content_line_count_min: 500       # per-tool_use, not aggregated
    rationale: Avoid runaway autonomous edits.

  - id: apply
    matcher:
      tool_use_name: Bash
      command_pattern: '\b(tofu|terraform)\s+apply\b|\bdatabricks\s+(jobs|pipelines)\s+(run|update)\b|\bkubectl\s+(apply|delete|patch)\b'
    rationale: Production-affecting infra/deploy commands always confirm.
```

The validator (G-class new code G150) loads this file at graph mode start; it's a shape-validated YAML with the rules engine versioned via `library/skill-prompts/stop-at-triggers.schema.json`. Repos extend via `stop_at_extensions:` in `.helix-autonomy.yml`; the union of base + extensions is the active trigger set. Base triggers cannot be removed (only extended) — `stop_at` is a hard floor, not negotiable per repo, per Invariant 2's protection of autonomous mode.

**Bench rows (§1.5b "Stop_at triggers" category)** verify each trigger: setup that exercises the trigger under autonomy=aggressive; assert the agent stops with an explicit confirmation prompt before executing the matched tool_use.

### 4.8 What "one-shot" looks like in practice

User runs `HELIX_AUTONOMY=aggressive claude -p "build a coffee-ordering app from scratch"`.

Skill engages (description matches "build … app"), reads no marker (none exists), under aggressive autonomy:

1. Drafts `.helix.yml` listing helix at `docs/helix/`. *No confirm: marker_edit is in stop_at? Yes. → Confirm.* Falls back to guided behaviour for this one step.
2. After marker confirmed, drafts `docs/helix/00-discover/product-vision.md`.
3. Drafts `docs/helix/01-frame/PRD-001.md` with `ddx.links: [{kind: informs, to: VISION-001}]`.
4. Drafts FEATs and user-stories per the graph's `contains` edges.
5. Hits `branch_or_merge` stop if it wants to commit; asks; proceeds on user OK.
6. Reports the full work back as a summary.

aggressive ≠ uncontrolled. `stop_at` is the safety net that keeps the user in the loop for irreversibles. The bench validates the loop holds.

---

## §5 Test infrastructure

### 5.1 Runner stack

```
family-test/bench/
├── conversations/           §1 conversation library
├── routing-evals/           §2 fast routing probes per methodology
├── judge/                   §5.2 LLM-judge prompts + harness
├── docker/                  Docker harness (already exists; reused)
├── run-bench.sh             top-level driver — runs everything
├── run-conversations.sh     conversation library only
├── run-routing.sh           routing evals only
└── report.py                aggregates per-run results into a markdown report
```

The Docker harness from family-test/docker/ stays as-is. The bench layers on top: a conversation runner that takes a conversation dir, materializes the workspace + plugins + autonomy + marker, drives the multi-turn dialog through the harness, and asserts via Layer 1/2/3.

### 5.2 Judge LLM

Layer 2 (semantic) assertions use a judge LLM call:

- Model: same family as the agent under test (claude-sonnet-4-6 baseline; lighter haiku for speed)
- Temperature: 0
- System prompt: a fixed rubric that takes (expected intent, actual prose) and returns `{matches: bool, confidence: float, rationale: string}`
- Re-judge policy: borderline cases (confidence 0.5-0.8) are re-judged 2 more times; majority wins

Judge LLM cost ≈ 1 cent per conversation per Layer-2 assertion. 100 conversations × 5 assertions × 3 judge runs = ~1500 judge calls per bench batch, ~$15 worst case. Acceptable for iteration; we batch in CI to once per merge to main.

### 5.3 Determinism + flakiness reporting

Each conversation runs `--determinism N` (default 3). Aggregator records:

- **Stable pass**: N-of-N
- **Flake**: P-of-N for 0 < P < N (recorded with per-run pass/fail signature)
- **Stable fail**: 0-of-N

CI gate: stable-pass rate >= configured threshold (initial 80%, ratcheted up via the existing ratchet pattern). Flakes route to `bench-flakes.md` for investigation.

### 5.4 CI wiring

- `just bench` — local runner; iterates fast
- `just bench --routing` — fast routing-only pass (~30s)
- GitHub Actions: `bench.yml` runs the full bench on every PR touching `family-test/bench/` or `family-test/methodology-*/skills/`
- Ratchet: a separate `bench-ratchet.yml` records stable-pass / flake rates monthly and prevents regression (matches the existing helix ratchet pattern)

### 5.5 Out of band — judge calibration

Once a quarter, sample 20 random Layer-2 judgements and have a human review. If human-judge disagreement > 5%, retune the rubric. Lightweight; covers judge drift.

---

## §6 Implementation sequencing

Order matters: each step unblocks the next.

| Step | What | Effort | Verification |
|---|---|---|---|
| **6.1** | SKILL.md description rewrite + slashCommands wiring (§2.2, §2.3) | 2h | Routing evals: `Create a PRD` → Skill(helix); `/helix-frame` recognized |
| **6.2** | Bench runner skeleton — Layer 1 only, no judge yet (§5.1) | 4h | C001/C004/C019 pass on hand-run |
| **6.3** | Routing-evals JSONL + runner (§2.4) | 2h | 50+ rows, 90%+ pass rate |
| **6.4** | Conversation library v1 (20 entries from §1.5) | 6h | 14 of 20 stable-pass (70% floor) |
| **6.5** | Autonomy schema + skill consultation (§4) | 4h | C005 (guided asks) and C006 (autonomous proceeds) both stable-pass |
| **6.6** | Cascade logic in SKILL.md (§3.2) + bench validates C002/C003/C005 | 3h | C005 surfaces vision prerequisite with autonomy=guided |
| **6.7** | Judge LLM harness + Layer 2 assertions (§5.2) | 4h | 5+ conversations exercise Layer 2; judge calibration noted |
| **6.8** | Layer 3 next-action structured assertions (§1.4) | 3h | C001 asserts offered=draft_artifact:product-vision |
| **6.9** | Helix-web methodology skeleton + slashCommands + description (§3.4) | 5h | C007 stable-pass |
| **6.10** | Multi-flow disambiguation via cwd + marker §1.5 (already in SKILL.md, extend bench) | 2h | C010/C016/C017 stable-pass |
| **6.11** | `stop_at` plumbing + tests (§4.7) | 3h | aggressive scenario refuses to edit marker without confirm |
| **6.12** | CI wiring + ratchet (§5.4) | 2h | GHA gates on stable-pass rate >= 80% |
| **6.13** | Documentation pass — autonomy.md, bench.md, skill-author guide | 4h | Operator can author a new bench entry in <30min |

Total: ~44 hours (~5.5 days). Within the family architecture's overall budget; smaller than v1 implementation plan (~55h) because the test-first work front-loads the gates.

Each step ships independently behind the gate. If §6.1 doesn't move routing-eval pass rate above ~60%, halt — the description anchor approach isn't the right lever and we need to dig deeper before continuing.

---

## §7 Risks I'm signing up for

1. **Description-anchor approach may not move routing reliably.** Claude's skill router heuristics are not fully documented; if "Create a PRD" still routes to a generic answer, we may need stronger surfaces (custom slash commands as the ONLY route; hard-required prefix). Mitigation: §6.1 is the early gate; halt and rethink if routing-eval pass rate stays below 60%.

2. **Judge LLM flakiness.** Layer 2 assertions add variability and cost. Mitigation: §5.5 calibration; layer-1 contracts are the floor; semantic assertions are advisory until trusted.

3. **Autonomy mis-clicks.** A user with autonomy=aggressive could trigger unexpected writes. Mitigation: `stop_at` defaults to the destructive set; aggressive is NOT a default; the SKILL.md hard-codes the safety list.

4. **Conversation corpus rot.** Seeded entries reflect *current* assumptions about good agent behaviour. They will become stale. Mitigation: each conversation has a `README.md` documenting WHY this is expected; periodic prune; deliberate freshness reviews.

5. **Method-specific bench growth.** As helix-web, helix-infra, helix-sales accrue, the bench grows multiplicatively. Mitigation: shared shape (conversation.yml + expected.yml), per-methodology subdirs, routing evals are the per-methodology surface; cross-method conversations live in a `cross/` subdir.

6. **Slash-command collisions across methodologies.** v1 implementation plan deferred the slash-namespace ADR. This plan assumes plugin-prefixed slash commands (`helix-frame` not `frame`). If two methodologies both want `/build`, they collide unless namespaced. Resolution: enforce prefix in the methodology's plugin.json validator; fail at install time.

7. **The autonomy file proliferates.** Three levels of config (repo, user-global, user-local) is a lot. Mitigation: documented precedence; `helix-doctor autonomy --resolve` command that prints the effective level + where it came from. Low cost to add.

---

## §8 Acceptance — when this plan ships

- §6.1-6.4: routing evals >= 90%, conversation bench v1 >= 14/20 stable-pass.
- §6.5-6.6: C005 vs C006 demonstrate the autonomy slider working (one asks, one doesn't).
- §6.7-6.8: judge LLM operational, Layer 3 next-action assertions on 5+ conversations.
- §6.9-6.10: helix-web ships + multi-flow scenarios pass.
- §6.11-6.12: stop_at protects irreversibles; CI gates regressions.
- §6.13: a new operator can author a bench conversation in under 30 minutes.

Once these hold, the family is "iteration-ready": skill defects surface as bench failures; SKILL.md changes ship behind bench gates; autonomy is observable and tunable. The monorepo reorganization (deferred from prior plans) then happens against a measured floor of reliability.

---

## §9 Open questions for review

1. **`autonomy:` inside `.helix.yml` vs separate `.helix-autonomy.yml`?** I'm choosing separate (per §4.2 rationale). Codex might disagree; the trade is single-file simplicity vs. per-user vs team config separation.
2. **Judge LLM cost ceiling for CI.** ~$15 per bench batch is modest; do we want to gate (e.g. only judge a 20-conversation subset on PR; full 100 on merge)?
3. **Routing eval threshold for §6.1 halt.** Proposed 60%. Could be too lenient (we accept too much) or too strict (we halt on noise). Codex view?
4. **`stop_at` defaults.** The list in §4.7 reflects my intuition. Operator experience may add `external_api_call`, `delete`, `force_push`, etc. Worth specifying as a starting set in v1 or letting it accrete?
5. **Slash-command namespace.** Per v1 implementation plan, this was deferred. This plan assumes plugin-prefix. Do we want the ADR now, before slashCommands ship in §6.1?

---

## §10 Out of scope for this plan

- The actual stdlib-only validator port (still mechanical follow-up).
- The monorepo reorganization (lands after this).
- helix-sales / helix-ops / other future flows (this plan introduces helix-data; sales/ops still later).
- DDx bead schema `graph_node:` field changes.
- Cross-flow *enforced* `requires` edges (this plan keeps cross-flow to advisory `informs` for v1; §13.4 sketches the v2 enforced-edge approach).

---

## §11 Terminology shift — methodology → flow

HELIX is no longer a single methodology with one workflow. It is a **family of cooperating flows**. The terminology should reflect that.

| Old term | New term | Why |
|---|---|---|
| methodology | flow | "Flow" reads naturally for "product flow," "data-pipeline flow," "infra flow." "Methodology" is heavier and harder to compose. |
| methodology plugin | flow plugin | Per-flow plugin (helix, helix-infra, helix-web, helix-data) |
| methodology graph (`workflows/graph.yml`) | flow graph (`workflows/graph.yml`) | File name stays; concept is a flow's type-pair graph |
| methodology activation | flow activation | When a flow's skill engages for a given prompt + marker |
| HELIX (capitalised) | HELIX | Unchanged. Names the family. |

The marker's top-level list of active flows changes key name: `methodologies:` → `flows:`. v1-shape markers (with `methodologies:`) keep working via a one-cycle deprecation alias (validator emits **M020 warn**: "`methodologies:` is the legacy key; rename to `flows:` before v2 lands"). v2 schema turns it into M020 error.

### 11.1 What changes in artifacts

- `docs/helix/02-design/design-2026-06-04-helix-family-marker-and-linkages.md` — refactor in place; rename every "methodology" → "flow" except in historical context references; add a §0.1 "Terminology" block explaining the rename and the deprecation alias.
- `docs/helix/02-design/validation-plan-2026-06-05-vertical-slice-completion.md` — same rename pass.
- This plan — already uses "flow" in new sections; older sections renamed in the same edit pass.
- README at the family root (`family-test/README.md`, eventually `helix/README.md`) — promote the flow concept to top-billing: "HELIX is a family of cooperating flows for product, data pipeline, infrastructure, website, and more."
- `library/schemas/marker.schema.json` — accepts BOTH `flows:` and `methodologies:` for one cycle; emits M020 on the latter.
- `SKILL.md` files — every methodology reference becomes flow.

The rename is mechanical but touches many files. We do it as a single PR in §6.0 (added below).

### 11.2 What doesn't change

- The directory structure `library/types/`, `<flow>/workflows/graph.yml`, `<flow>/skills/<id>/SKILL.md` etc.
- The on-disk file names — `.helix.yml`, `graph.yml`, `meta.yml`.
- The plugin marketplace shape.
- Existing per-flow content (helix, helix-infra) — only their internal "methodology" prose updates.

### 11.3 Why now

We're about to ship slash commands (§2.3), a conversation bench (§1), and a fourth flow (data-pipeline). All of these will codify "methodology" in user-visible surfaces if we don't rename first. Cheaper to rename now than to deprecate slash names and bench fixtures later.

---

## §12 The data-pipeline flow (helix-data)

The fourth flow ships alongside helix, helix-infra, helix-web. It owns the type space the family currently fits into `data-prd`, `data-architecture`, `data-design`, `data-quality-expectations`, `metric-definition`, `metrics-dashboard` — but generalises beyond product-data.

### 12.1 What it covers

Data-pipeline flow handles the lifecycle of:

- Ingest → transform → publish pipelines (Airflow, dbt, Databricks DLT, Dataflow, Beam, Flink, custom)
- Data contracts (producers ↔ consumers)
- Quality enforcement (expectations, freshness SLAs, schema evolution)
- Lineage and observability of data assets
- Migration and backfill operations

Not in scope for helix-data: the apps that emit or consume data (those are helix product flow); the cloud accounts and IAM that host them (helix-infra); the UI dashboards that visualise them (helix-web).

### 12.2 Activities — data-native lifecycle (revised post-codex)

Codex's review flagged the initial 7-activity sketch as product-shape copy-paste. Data engineering has different gates: source profiling matters, contracts precede design, governance and PII are first-class, operate replaces deploy because data pipelines don't ship-and-forget.

Revised lifecycle:

| Activity | Purpose | Primary artifacts |
|---|---|---|
| 00-discover/profile | Identify the data product, profile source schemas + freshness + PII, enumerate consumers, define SLAs | `data-product-brief`, `source-profile`, `consumer-inventory` |
| 01-contract | Specify producer→consumer contracts: schemas, freshness SLAs, evolution policy, PII classification | `data-contract`, `data-quality-expectations`, `governance-classification` |
| 02-design | Topology, medallion layers, transformations, storage, idempotency, partitioning, late-arrival handling, ADRs | `data-architecture`, `data-design`, ADRs |
| 03-validate | Quality contracts as executable tests; backfill rehearsal; reconciliation harness | `data-quality-tests`, `backfill-plan`, `reconciliation-suite` |
| 04-build | Pipeline code, orchestration, lineage instrumentation, implementation plan | `implementation-plan`, `lineage-spec` |
| 05-operate | Production rollout + ongoing operation (deploy folds in here unless the flow has explicit deployment gates): monitoring, incident response, freshness/cost tuning | `runbook`, `monitoring-setup`, `metrics-dashboard` |
| 06-evolve/backfill | Schema evolution, reprocessing strategy, deprecation of consumers, breaking-change communication | `evolution-plan`, `deprecation-notice`, `improvement-backlog` |

Seven activities, but with data-native shape: 00 acquires source truth before declaring intent; 01 contracts are first-class (NOT inside design); 03 is `validate` not `test` (data validation is structurally distinct from unit/integration testing); 05 collapses build/deploy/operate because pipelines run continuously; 06 names the long-tail concern data engineers actually have (schema evolution + backfills + deprecation).

helix-data reuses library types where they fit (ADR, monitoring-setup, runbook, metrics-dashboard, improvement-backlog) and adds data-specific types listed above.

### 12.3 New library type shapes (added to `library/types/`)

Each type ships with `meta.yml` declaring `required_sections`, plus a `template.md`, `prompt.md`, and `example.md`. Shapes below are pinned at the section level so the validator (T-class) can gate them.

`data-product-brief`:
- problem
- consumers
- data_sources
- freshness_sla
- success_metrics
- non_consumers (out-of-scope)
- open_questions

`source-profile`:
- source_system
- schema_snapshot
- volume_estimates
- freshness_observed
- pii_classification
- producers_contacted
- risks_and_unknowns

`consumer-inventory`:
- consumer
- purpose
- read_pattern (batch/streaming/interactive)
- freshness_required
- contract_version
- dependency_strength (hard/soft)

`data-contract`:
- producer
- consumer (or "all qualified consumers")
- schema_versioning_policy
- semantic_field_definitions
- freshness_sla
- evolution_policy (breaking/non-breaking surface)
- termination_clauses

`data-quality-expectations`:
- bronze_expectations (raw schema integrity)
- silver_expectations (transformed semantics)
- gold_expectations (consumer-facing invariants)
- escalation_when_failed
- override_policy

`governance-classification`:
- pii_fields
- access_tier (public/internal/restricted/secret)
- retention_policy
- residency_constraints
- audit_log_requirements

`data-quality-tests`:
- test_inventory (id, name, expectation_id, run_frequency)
- fixtures
- known_failures (acknowledged drift)

`backfill-plan`:
- trigger
- scope (date range, partition selector)
- safety_checks_pre_run
- rollback_strategy
- expected_runtime
- communication_to_consumers

`reconciliation-suite`:
- reconciliation_rules (source vs sink invariants)
- alert_thresholds
- response_runbook_ref

`lineage-spec`:
- emitter_strategy (OpenLineage, dbt-style, custom)
- nodes_to_emit
- consumer_of_lineage (Marquez, DataHub, custom)

`evolution-plan`:
- breaking_changes
- migration_window
- consumer_notification_plan
- rollback_plan
- success_criteria

`deprecation-notice`:
- artifact_being_deprecated
- successor
- consumers_affected
- timeline
- final_decommission_date

Total: 12 new library types. Each adds ~50 lines of files (meta + template + prompt + example). ~600 lines of catalog content authoring. Reflected in P9 effort budget.

### 12.4 Slash commands

```
/helix-data
/helix-data-discover
/helix-data-contract
/helix-data-design
/helix-data-validate
/helix-data-build
/helix-data-operate
/helix-data-evolve
```

### 12.5 SKILL.md description verbs

```
Activate this skill when the user asks to:
  - design, build, validate, or operate a data pipeline
  - profile a data source or document a producer schema
  - specify a data contract or producer/consumer schema
  - declare PII classification or governance posture
  - author data-prd, data-product-brief, data-architecture,
    data-design, data-quality-expectations, data-quality-tests,
    backfill-plan, evolution-plan, or deprecation-notice
  - design Bronze/Silver/Gold medallion topologies
  - plan dbt models, Airflow DAGs, Databricks DLT/SDP, Glue, Beam,
    Flink pipelines
  - design backfill or reconciliation strategy
  - plan schema evolution or consumer deprecation
  - investigate freshness regression or data-quality alert
```

### 12.6 Cross-flow edges helix-data participates in

- `helix:prd informs helix-data:data-product-brief` (product PRD frames the data product)
- `helix-data:data-product-brief informs helix-infra:change-intent` (pipeline needs new infra)
- `helix-data:metrics-dashboard informs helix:improvement-backlog` (metrics feed product iteration)
- `helix-web:design-system informs helix-data:metrics-dashboard` (dashboards inherit visual language)

All advisory `informs`, declared in each source flow's `external_edges:` (per the existing cross-flow rule, §13.4 doesn't change this).

### 12.7 Worked example — verification artifact for P9

A complete walked-through example ships at `family-test/examples/helix-data-customer-events/`. The example is a real-shaped scenario (Stripe webhook events → S3 → Glue → Redshift consumed by analytics + ops) that produces:

```
examples/helix-data-customer-events/
├── README.md                                       overview + walkthrough
├── docs/helix/
│   ├── 00-discover/
│   │   ├── data-product-brief.md
│   │   ├── source-profile-stripe.md
│   │   └── consumer-inventory.md
│   ├── 01-contract/
│   │   ├── data-contract-stripe-events.md
│   │   ├── data-quality-expectations.md
│   │   └── governance-classification.md
│   ├── 02-design/
│   │   ├── data-architecture.md
│   │   ├── data-design.md
│   │   └── adr/ADR-001-glue-vs-spark.md
│   ├── 03-validate/
│   │   ├── data-quality-tests.md
│   │   ├── backfill-plan.md
│   │   └── reconciliation-suite.md
│   ├── 04-build/
│   │   ├── implementation-plan.md
│   │   └── lineage-spec.md
│   ├── 05-operate/
│   │   ├── runbook.md
│   │   ├── monitoring-setup.md
│   │   └── metrics-dashboard.md
│   └── 06-evolve/
│       ├── evolution-plan.md
│       └── deprecation-notice.md
└── .helix.yml                                       methodologies: [{id: helix-data, root: docs/helix/}]
```

The example is validated by `helix_check.py marker examples/helix-data-customer-events/.helix.yml --strict` exiting 0. CI re-runs this on every helix-data PR. The example is the operator's reference for what a complete data-pipeline scope looks like.

helix-data shipping verifiable means the example walks clean end-to-end. No flow is real until its worked example validates.

**Adversarial data fixtures (codex finding #7).** Static marker validation is necessary but NOT sufficient — it doesn't surface idempotency, late arrivals, PII, lineage gaps, or reconciliation failures. The worked example MUST ship with these six fixture scenarios committed under `examples/helix-data-customer-events/fixtures/`, each tied to specific artifacts:

| Fixture scenario | What it adversarially exercises | Which artifacts must reference it |
|---|---|---|
| **F1 — Duplicate webhook ID** | Idempotency on retry; deduplication strategy | `data-contract`, `data-quality-tests`, `runbook` |
| **F2 — Late event arrival** (delivered out-of-order by 6h) | Late-arrival handling; watermark policy | `data-design`, `data-quality-tests`, `monitoring-setup` |
| **F3 — Schema-version drift** (producer adds optional field; producer changes type of existing field) | Schema evolution policy; backwards compatibility surface | `data-contract`, `evolution-plan`, `data-quality-tests` |
| **F4 — PII-bearing field surfaced** (email in webhook payload that was supposed to be tokenized) | PII classification + redaction; access tier downgrade | `governance-classification`, `data-design`, `runbook` |
| **F5 — Customer-initiated deletion** (right-to-be-forgotten request requires propagating delete through pipeline) | Redaction propagation; consumer notification | `governance-classification`, `evolution-plan`, `deprecation-notice`, `runbook` |
| **F6 — Source/sink reconciliation mismatch** (Stripe says N events, Redshift shows N-7) | Reconciliation rules + escalation path | `reconciliation-suite`, `runbook`, `monitoring-setup` |

Each fixture is committed as `fixtures/F<n>-<slug>.yml` describing the scenario + expected handling. The worked example's artifacts MUST include references to these fixtures by ID (the validator checks that the listed artifacts mention F1-F6 by ID — bench validates F1-F6 coverage via `helix_check.py example --adversarial-coverage`).

Without these adversarial fixtures, the worked example is a sanitized sketch that proves the schema but not the methodology. With them, the example proves helix-data's lifecycle stages actually catch the failure modes data engineers care about.

### 12.8 Bench corpus additions

| ID | Utterance | Active flows | Autonomy | Expected |
|---|---|---|---|---|
| C021 | "Let's set up a customer-ingest pipeline" | none | guided | helix-data engages; offers to add helix-data to marker; drafts data-product-brief |
| C022 | "Define a data contract for the customer events" | helix-data | guided | helix-data engages; drafts contract; if no producer/consumer identified, asks |
| C023 | "Add quality checks for the orders pipeline" | helix-data | guided | helix-data engages; drafts data-quality-expectations; suggests testable EXPECT rules |
| C024 | "Backfill the last 90 days of customer events" | helix-data, autonomy=manual | manual | helix-data engages; refuses to execute; drafts backfill-plan; asks for explicit approve |
| C025 | "Our PRD needs a new metric we can measure" | helix + helix-data both active | guided | Cross-flow: helix engages first (PRD), surfaces that the metric needs helix-data; offers to draft a data-product-brief and a metric-definition |

These extend §1.5's table to 25 entries for v1; data-pipeline flow has 5 dedicated rows including one cross-flow scenario.

---

## §13 Multi-instance flows + document sharing

### 13.1 The need

A single repo may run the same flow in multiple subtrees. Two examples:

- **Monorepo with multiple data pipelines** (`pipelines/customer-ingest/`, `pipelines/orders-fulfillment/`) each independently using the helix-data flow.
- **Monorepo with multiple product surfaces** (`services/api/`, `services/admin/`) each using helix product flow.

Today's marker can't express this — every flow's `root:` is unique, and re-listing a flow with two roots collides on the `id` key.

### 13.2 Marker schema v2 — `instance:` discriminator

Add an optional `instance:` field per entry. The unique key becomes `(id, instance)`. `instance:` defaults to `default`.

```yaml
helix_version: 2

flows:
  - id: helix
    instance: api               # default omitted in this example
    root: services/api/docs/helix/
  - id: helix
    instance: admin
    root: services/admin/docs/helix/
  - id: helix-data
    instance: customer-ingest
    root: pipelines/customer-ingest/docs/helix/
  - id: helix-data
    instance: orders
    root: pipelines/orders-fulfillment/docs/helix/
  - id: helix-infra
    root: infra/                # instance defaults to "default"
```

The validator (M-class) enforces `(id, instance)` uniqueness (M030); duplicates are hard-fail. The cwd-routing rule (§1.5) is extended: cwd-under-root resolves to one `(id, instance)` pair; ambiguity (cwd under two roots, possible with nested scopes) falls to the explicit prefix / env / default chain.

### 13.3 Instance-qualified document ownership

Instance documents carry the qualified id:

```yaml
ddx:
  id: PRD-001
  type: prd
  flow: helix
  instance: api
  ...
```

`ddx.methodology:` is renamed to `ddx.flow:`. v1 documents with `ddx.methodology:` continue to validate during the deprecation cycle (W005 → W020 path).

The validator (I-class) computes instance indexes per `(flow, instance)`. Within an instance, `ddx.links` resolve against that instance's index. Cross-instance links are a new shape (§13.4).

### 13.4 Cross-instance document sharing

Two flows (or two instances of the same flow) may want to reference the same document. Three sub-cases:

#### Case A — Read-only cross-instance reference

`helix.admin:PRD-007` informs `helix.api:FEAT-014` (api team's feature was informed by the admin team's PRD). Declared the same way as cross-flow edges:

```yaml
# in helix/api flow's graph.yml
external_edges:
  - from_type: feature-specification
    to_flow: helix
    to_instance: admin
    to_type: prd
    kind: informed_by    # NEW kind: inverse advisory (we are informed by them)
    cardinality: many-to-one
    required: false
```

Instance frontmatter:

```yaml
ddx:
  id: FEAT-014
  type: feature-specification
  flow: helix
  instance: api
  links:
    - { kind: informed_by, to: "helix.admin:PRD-007", cross_instance: true }
```

`informed_by` is the inverse of `informs` — used when the SOURCE flow's graph doesn't authorise outbound (it's a different team's flow that already shipped) but the TARGET flow wants to record the lineage. Advisory only.

#### Case B — Shared-document model

A single document is OWNED by one `(flow, instance)` and explicitly REFERENCED by others. This is what `informs`/`informed_by` already cover.

Variant: when one doc is co-authored by two flows (e.g. a contract sits between product and data), it remains owned by ONE flow per the marker, but both flows can SUBSCRIBE to it via the bench (and the doctor reports `unaligned-coauthor` if the two flows' frontmatter expectations diverge).

#### Case C — Same physical document mounted into multiple flows

Rejected for v1. Symlinks or two-flow ownership of a single file path is a footgun (multiple `ddx.flow:` claims). If two flows truly need shared state, the right move is a single owner + cross-instance reads (Case A).

### 13.5 Instance autonomy

Autonomy can be set per `(flow, instance)`:

```yaml
autonomy:
  default: guided
  per_flow:
    "helix.api":   guided
    "helix.admin": autonomous
    "helix-data.customer-ingest": manual
    "helix-data.orders":          autonomous
    "helix-infra":                manual
```

`per_methodology:` is renamed `per_flow:`.

### 13.6 Bench corpus additions for multi-instance

| ID | Utterance | Marker | Autonomy | Expected |
|---|---|---|---|---|
| C026 | "Create a PRD" (cwd `services/api/`) | helix.api + helix.admin | guided | helix engages, scopes to api; PRD lands under api/ |
| C027 | "Reference admin's PRD from this feature" | both instances active | guided | helix engages; adds `informed_by` link to `helix.admin:PRD-007`; surfaces external_edges authorisation |
| C028 | "Add a data pipeline for orders" | helix.api + helix-data.customer-ingest | guided | helix-data engages; offers to add a NEW instance `helix-data.orders` to marker; multi-instance plumbing |
| C029 | "What's active here?" (cwd `pipelines/orders-fulfillment/`) | helix.api + helix-data.customer-ingest + helix-data.orders | guided | Skill names `helix-data.orders` only (cwd-disambiguates) |
| C030 | "Set autonomy to autonomous for the admin PRD work" | helix.api + helix.admin | guided | Skill offers to edit `.helix-autonomy.yml` to add `per_flow: { "helix.admin": autonomous }` |

Five more bench rows — 30 total for v1 ship.

### 13.6b Cwd-resolution algorithm (multi-instance disambiguation)

Per codex finding #6 (2026-06-05), this algorithm uses **path-component-aware matching** (not string-prefix). Equal-depth ties at the SAME or SIBLING level return **ambiguous** — never silent alphabetical selection.

```
Given: marker M with flows = [(f1, i1, root1), (f2, i2, root2), ...]
       cwd C (absolute path)
       repo_root R (path containing .git/)

Definitions:
  components(P) = path P split on /, with empty trailing component removed
                  (e.g., components("/a/b/") = ["a", "b"])
  is_path_prefix(A, B) = components(A) is a prefix of components(B)
                  (NOT string prefix; "a/bc/" is NOT a path prefix of "a/bcd/")

1. Resolve all roots to absolute: abs_root_k = R / root_k
2. Compute candidates: K = { k : is_path_prefix(abs_root_k, C) OR abs_root_k == C }
3. If |K| == 0:
     no scope matches → fall through to next rule in §1.5
     (HELIX_METHODOLOGY env → defaults.methodology → single entry → disambiguation banner)
4. If |K| == 1:
     return that single (flow, instance)
5. If |K| > 1 (nested or overlapping roots):
     compute depth_k = len(components(abs_root_k)) for each k in K
     let K_max = { k in K : depth_k is maximal }
     5a. If |K_max| == 1:
           return that (flow, instance)
     5b. If |K_max| > 1 (genuine ambiguity — siblings at equal depth, or
         identical-root-with-different-flows):
           return ambiguous; fall through to disambiguation step:
              i. HELIX_METHODOLOGY env if it names one of K_max → that one
              ii. defaults.methodology if it names one of K_max → that one
              iii. else emit the §1.5 disambiguation banner naming all K_max
                   candidates; ASK the user. NEVER silently pick alphabetically.
```

Rationale change from prior version: alphabetical tiebreak can silently route a user's write to the wrong sibling instance — exactly the failure mode the marker was supposed to eliminate. Path-component matching also prevents the silent failure where one root is a textual prefix of another but not a parent (`services/api/` vs `services/api-admin/`).

Documented in `library/scripts/helix_check.py` as `resolve_cwd_to_instance()`. Verified by 6 bench rows in §1.5b "Multi-instance routing" category (was 4; expanded for codex #6):
1. no match — falls through
2. single match — returns it
3. nested roots, longest wins — returns innermost
4. boundary (cwd == root) — returns that root
5. sibling roots at equal depth, env present — env wins
6. sibling roots at equal depth, no env — emits banner, asks user (does NOT auto-route)

### 13.7 Validator changes for multi-instance

Add to `helix_check.py`:

- M030: duplicate `(id, instance)` in marker → hard stop
- M031: `instance:` declared as empty string → M001 (already covers empty values)
- I130: cross-instance reference to non-existent `(flow, instance)` → error (analogous to I101)
- I131: cross-instance reference where target instance is in marker but not authorised by `external_edges` → warn

Edge resolver builds `instance_index: {(flow, instance, id): file_path}` instead of `{id: file_path}`. Walks each flow-instance's `root:` separately. Instance-local edges resolve against the source's instance index only.

### 13.8 Cost of the schema bump

`helix_version: 1` markers continue to work for one minor cycle. Their `methodologies:` block is treated as `flows:` with `instance: default`. M020 (legacy key) warns. v2 markers (`helix_version: 2`) MUST use `flows:` + optional `instance:`. The migration script from prior plans (`migrate_relationships_to_links.py`) gets a sibling `migrate_marker_v1_to_v2.py` that rewrites v1 markers and instance docs in place.

The cost is real but the timing is right: this plan is the largest single addition to the family architecture so far; folding the marker bump into the same iteration avoids two breaking changes spaced apart.

---

## §14 Cooperating flows — interaction patterns

When multiple flows are active in one repo, they cooperate via:

1. **Cross-flow `external_edges`** (already in design): one flow authorises outbound informs to another.
2. **Marker-mediated activation**: only flows the marker lists can act in this repo. Engagement of a non-marker flow's slash command is rejected (§A5/A4).
3. **Cwd-disambiguated routing** (§1.5): when multiple flows could plausibly engage, cwd-under-root wins.
4. **Shared library types**: every flow draws its artifact types from the same `library/`. ADR, principles, concerns are universal; flow-specific types extend.
5. **Cross-instance lineage** (§13.4): documents owned by one flow-instance can be referenced from another.

### 14.1 Where cooperation gets sharp

Three concrete scenarios the bench must cover (extending §1.5):

| Scenario | Expected behaviour |
|---|---|
| Product PRD declares it needs a data pipeline. Marker has helix + helix-data. | helix engages first; surfaces helix-data prerequisite; offers to also fire helix-data to draft a `data-product-brief` and link cross-flow |
| Data pipeline's monitoring-setup needs cloudflare DNS for the dashboard URL. Marker has helix-data + helix-infra. | helix-data engages; surfaces helix-infra prerequisite; offers to author a helix-infra change-intent and link cross-flow |
| User says "what's blocked?" in a multi-flow project | helix engages (catch-all for "what's next/blocked"); reads ALL active flows' graphs; reports per-flow exit-gate status |

### 14.2 What this means for SKILL.md

Each flow's SKILL.md gains a §9:

> **§9 Cross-flow awareness.**
>
> When authoring an artifact that has a cross-flow edge in your graph's `external_edges:`, check whether the target flow is active in the marker. If yes, surface the cross-flow link as a draft suggestion (or auto-author it per autonomy). If no, note that the cross-flow link would be ideal but the target flow is not active in this repo; offer to add it to the marker.

This is what makes the four flows actually *cooperate* instead of merely co-exist.

---

## §15 Revised implementation sequencing (SUPERSEDED — see §15b)

The original 17-step sequencing here was superseded by the §15b 15-phase plan after fresh-pass review. Retained as historical record below; do not execute from this section.



The original §6 sequencing assumed three flows (helix, helix-infra, helix-web). With the additions in §11-§14, sequencing becomes:

| Step | What | Effort | Verification |
|---|---|---|---|
| **§6.0 (NEW)** | Terminology rename pass (methodology → flow) across the design docs, marker schema (with M020 alias), and SKILL.md prose. Marker schema accepts both keys for one cycle. | 4h | grep finds no "methodology" outside historical refs; v1 markers still validate |
| §6.1 | SKILL.md description rewrite + slashCommands wiring (§2.2, §2.3) | 2h | Routing evals: `Create a PRD` → Skill(helix); `/helix-frame` recognised |
| §6.2 | Bench runner skeleton — Layer 1 only, no judge yet (§5.1) | 4h | C001/C004/C019 pass on hand-run |
| §6.3 | Routing-evals JSONL + runner (§2.4) | 2h | 50+ rows, 90%+ pass rate |
| §6.4 | Conversation library v1 (25 entries from §1.5 + §12.6 data conversations) | 8h | 18 of 25 stable-pass (72% floor) |
| §6.5 | Autonomy schema + skill consultation (§4) | 4h | C005 (guided asks) and C006 (autonomous proceeds) both stable-pass |
| §6.6 | Cascade logic in SKILL.md (§3.2) + bench validates C002/C003/C005 | 3h | C005 surfaces vision prerequisite |
| §6.7 | Judge LLM harness + Layer 2 assertions (§5.2) | 4h | 5+ conversations exercise Layer 2 |
| §6.8 | Layer 3 next-action structured assertions (§1.4) | 3h | C001 asserts offered=draft_artifact:product-vision |
| §6.9 | Helix-web flow scaffold + slashCommands + description (§3.4) | 5h | C007 stable-pass |
| **§6.9b (NEW)** | Helix-data flow scaffold (§12) — activities, library type adds (data-product-brief, consumer-inventory, data-quality-tests, backfill-plan), graph.yml, SKILL.md | 8h | C021-C025 stable-pass; helix-data ADR self-validates |
| §6.10 | Multi-flow disambiguation via cwd + marker §1.5 (extend bench) | 2h | C010/C016/C017 stable-pass |
| **§6.10b (NEW)** | Multi-instance marker support (§13) — schema v2, validator M030/I130/I131, instance-aware index | 6h | C026-C029 stable-pass; v1 marker still validates with M020 warn |
| **§6.10c (NEW)** | Cross-instance/`informed_by` edge support (§13.4) | 3h | C027 (cross-instance reference) stable-pass |
| §6.11 | `stop_at` plumbing + tests (§4.7) | 3h | aggressive scenario refuses to edit marker without confirm |
| §6.12 | CI wiring + ratchet (§5.4) | 2h | GHA gates on stable-pass rate ≥ 80% |
| **§6.12b (NEW)** | Marker v1→v2 migration script + bench | 3h | tool rewrites a v1 marker corpus to v2 cleanly; idempotent |
| §6.13 | Documentation pass — autonomy.md, bench.md, flows.md (NEW), skill-author guide | 6h | Operator can author a bench entry in <30min; flow concept top-billed in README |

Total: ~73 hours (~9 days). Up from the prior 44h. The new additions (§6.0, §6.9b, §6.10b/c, §6.12b) account for ~24h; the rest is +3h for the wider bench corpus and +3h docs.

(End of superseded §15. Active sequencing is §15b below.)

---

## §15b Active sequencing (15 phases, ~102h)

Reshape after fresh-pass review. Codex's smart deferral concerns absorbed (routing gate first; data-native lifecycle; trigger spec file) WITHOUT dropping scope (everything still in v1). Heavier than §15 because the verification floor is now specified per claim.

Gate model: each phase has a verification floor; the next phase does not start until that floor is met. Floors are measurable (precision/recall numbers, fixture pass counts), not "the team feels good." The order is dependency-driven; some phases can run in parallel where flagged.

| Phase | What | Effort | Gate (must be measurable) |
|---|---|---|---|
| **P0 — Foundation** | Bench runner skeleton (Layer 1 only); routing-eval runner; CC version pin (§19); cost-tracking infra (§19); discriminator-required loader with typed assertion DSL whitelist (§1.4b); **property-based tests for Layer 1 assertions** (codex #8 — promoted from v1.1 deferral). Property generators produce transcripts with known properties (e.g., `read_before_write` true/false) and verify the assertion engine classifies them correctly | 12h | Synthetic-input meta-test passes 10/10 (5 vacuous-discriminator rejections + 5 valid positives); property tests cover ≥4 assertion types (skill_tool_use, read_before_write, scope_write_path, graph_edge_observed); runner rejects rows failing T040-T044 |
| **P1 — Engagement gate (NEEDS ABLATION)** | Description anchors + slash commands + 75-row routing-eval set (30 pos + 30 neg + 15 ambig); ablation across 4 description shapes (baseline / verb-list / `when_to_use` / minimal); truncation-budget probe via `/doctor` | 8h | Integer confusion-matrix gates (per codex finding #3): positives **≥29/30** skill engagement; negatives **30/30** no engagement; ambiguous **≥13/15** correct route AND **0/15** unsafe unauthorized routes. Precision/recall computed for report; integer counts are the gate. Hard halt if no description shape clears all four integer thresholds. |
| **P2 — Cascade discrimination** | SKILL.md cascade prose (§3.2); graph-discrimination fixtures (custom non-standard edge); 4 rows verify graph was read | 6h | Discrimination fixture passes (agent surfaces unusual prereq) AND negative-control passes (agent does NOT surface it when edge absent) |
| **P3 — Autonomy matrix + stop_at trigger spec** | 4-level autonomy (`manual`/`guided`/`autonomous`/`aggressive`); stop_at trigger spec file (`library/skill-prompts/stop-at-triggers.yml`); 8 matrix rows + 6 trigger rows | 10h | Confirmation count + write count contract holds across all 4 levels; every stop_at type fires under `aggressive`; spec file shape-validated by validator |
| **P4 — Edge Authority Asymmetry** | Named invariant added to design §2.7; 4 negative fixtures; SKILL.md §10 explicitly prohibits auto-population | 4h | Auto-population fixture FAILS when skill silently writes ddx.links; PASSES when skill surfaces and asks (under both guided AND autonomous) |
| **P5 — Conversation library (25 rows; split must_pass_core / exploratory)** | C001-C025 from §1.5 + §12.8; each with paired negative control + typed discriminator. Each row carries `tier: must_pass_core` or `tier: exploratory` in `expected.yml`. **must_pass_core** rows (15): C001, C002, C005, C006, C012, C014, C019, C020, C021, C022, C024, C025, plus 3 chosen during P5 authoring. **exploratory** rows (10): everything else. | 12h | **must_pass_core: 15/15 stable-pass 3-of-3.** **exploratory: ≥7/10 stable-pass 3-of-3.** No row marked must_pass_core may regress to exploratory without a written rationale + design-doc change. Per codex finding #4: do not ship with known core failures. |
| **P6 — Warm-context (5 rows)** | Replay 5 unrelated turns of history before each probe; assert engagement holds | 3h | All 5 stable-pass 3-of-3; engagement rate matches cold-start within 5pp |
| **P7 — Layer 2 judge LLM (semantic)** | Judge prompt + calibration set + harness; apply to 10 conversations; cost tracking | 6h | Judge agreement with human classification ≥ 90% on the calibration set; cost per judge call within §19 budget |
| **P8 — Layer 3 next-action structured assertions** | JSON envelope injection (separate pass to avoid contaminating Layer 1); 5 conversations exercise it | 4h | Layer 1 outcomes IDENTICAL across no-envelope and envelope passes (proves no contamination); Layer 3 assertions on 5 rows stable-pass |
| **P9 — helix-data (data-native lifecycle, 12 library types, worked example)** | Codex's data-native activities (§12.2 revised); 12 new library types with shapes (§12.3); helix-data graph.yml + SKILL.md; full worked example walked end-to-end (§12.7); 5 bench rows | 16h | Worked example validates clean (`helix_check.py marker --strict` exit 0); 5 helix-data bench rows stable-pass; cross-flow `external_edges` validate |
| **P10 — Multi-instance schema v2 + cwd-resolution algorithm** | Marker schema v2 (`flows:` + optional `instance:`); validator M030/I130/I131; cwd-resolution algorithm (§13.6b); 4 routing rows | 8h | All existing T01-T38 fixtures pass; 4 multi-instance routing rows stable-pass; nested-root and boundary cases deterministic |
| **P11 — Cross-instance + `informed_by` edges** | Validator I130/I131; bench rows for stale-target detection + impact analysis; cross-instance reference resolves | 4h | Stale-target row: validator emits I131 within 100ms; impact analysis report lists the stale target; cross-instance happy path stable-pass |
| **P12 — Terminology rename + M020 alias** | Bulk codemod methodology→flow across design docs, validator, SKILL.md prose; M020 deprecation alias on marker key | 5h | Zero regressions in any T01-T38 fixture under both v1 (`methodologies:`) and v2 (`flows:`) shapes; M020 fires correctly on v1; M020 is silent on v2 |
| **P13 — Verbose-but-stuck verification** | 4 rows targeting "skill engages but doesn't read marker/graph before writing"; SKILL.md §1.5 ordering rule | 4h | Ordering assertion fires on all 4 rows; positive rows show Read → Read → Write order; negative-control rows show Write before Read |
| **P14 — CI + cost gate + ratchet** | GitHub Actions; cost-per-run cap; ratchet on stable-pass rate + cost trend | 4h | Full bench runs in CI; cost ≤ §19 budget; ratchet alerts on >5% stable-pass regression OR >25% cost regression |
| **P15 — Documentation + author guide** | `flows.md`, `bench.md`, `autonomy.md`, `skill-author-guide.md`; how to author a new bench row in <30min | 6h | New operator authors a valid bench row + paired negative + discriminator in ≤30min during dogfood test |

**Total: ~145h (~18 days).** Per codex finding #10 — honest accounting after the assertion DSL work (P0 +4h), property tests in P0 (P0 +4h), 6 near-miss negatives for stop_at (P3 +4h), adversarial data fixtures for helix-data (P9 +8h), expanded multi-instance routing rows (P10 +2h), must_pass_core/exploratory authoring discipline (P5 +4h), and the typed-DSL meta-tests (~5h migration of meta-test category). Codex's read of 140-160h is now within plan; previous 108h was hand-waving.

The total includes corpus authoring (~55h after the must_pass_core split work, was 50h). No deferrals. Codex's "one change" (typed DSL + property tests + category gates) is absorbed.

### 15b.1 What can run in parallel

- **P1 and P0 setup** overlap: routing-eval runner is part of P0 foundation; ablation matrix in P1 uses it
- **P5 corpus authoring** runs alongside P2/P3/P4 — corpus authors can work while the validator/skill code is in flight
- **P9 helix-data worked example authoring** runs in parallel with the library type shape definitions
- **P15 documentation** can be drafted alongside P10/P11; finalized after P14

Practical sequencing on a single contributor: P0 → P1 (hard gate) → P2 → P3 → P4 → P5 (corpus author) → P6 → P7 → P8 → P9 → P10 → P11 → P12 → P13 → P14 → P15. With parallelism on a team of 2: foundation + engagement gate first (P0+P1), then pair on (validator/scaffold work) ‖ (corpus authoring) ‖ (docs).

### 15b.2 Halt conditions (each phase has one)

- **P0**: meta-test passes < 10/10 OR property tests fail OR runner accepts a vacuous discriminator. Halt — the bench itself is broken, no point grading anything on top of it.
- **P1**: no description shape clears the integer thresholds (positives ≥29/30 AND negatives 30/30 AND ambiguous ≥13/15 with 0 unsafe). Halt and rethink the engagement approach — likely needs slash-command-required mode or `when_to_use` adoption.
- **P2**: graph-discrimination fixture passes via general HELIX knowledge, not graph.yml reading. Halt and add stronger graph-reading instrumentation to SKILL.md.
- **P3**: autonomy levels produce non-deterministic confirmation counts across 3 runs. Halt and tighten SKILL.md §8 prose; the levels are not crisp enough.
- **P4**: auto-population fixture passes (skill silently writes ddx.links). Halt — this is a load-bearing invariant violation; needs SKILL.md hard prohibition + bench-mode runner check.
- **P9**: worked example fails to validate after authoring. Halt — the new library type shapes are wrong; iterate before declaring helix-data ready.
- **P12**: any existing T01-T38 fixture regresses after rename. Halt and identify which rename step broke compat; the M020 alias is the contract here.

### 15b.3 Verification floor totals (revised post-codex-2)

Across all phases:
- **158 bench rows** (75 routing + 25 conversations [15 must_pass_core + 10 exploratory] + 8 autonomy + 12 stop_at [6 positive + 6 near-miss negative] + 4 graph-discrim + 4 edge-asymmetry + 3 cross-flow + 6 multi-instance [was 4] + 3 cross-instance + 4 rename + 5 warm-context + 4 verbose-stuck + 10 meta-tests [5 vacuous-discriminator rejections + 5 positive] = 163; the 158 number excludes 5 meta-tests that are runner self-checks not bench rows)
- 5 worked examples (1 per flow: helix product, helix-infra, helix-web, helix-data; plus the cross-flow example showing 2 flows cooperating)
- **6 adversarial data fixtures** for helix-data (F1-F6 per §12.7) committed alongside the worked example
- 1 CC version pin + re-validation cadence
- 1 cost budget + ratchet
- **1 typed assertion DSL whitelist** (`library/schemas/discriminator-whitelist.yml`) — 5 assertion_ids at v1; new IDs require runner + schema bump
- 12 named invariants spec'd (§0.5 + per-phase preconditions)

Every row, example, fixture, gate, and invariant maps to a phase. Nothing is left as "we'll figure out testing later."

---

## §16 Updated risks

In addition to §7's risks:

8. **Terminology rename is invasive.** Touches design docs, SKILL.md, marker, validator, install docs, every fixture readme. Mitigation: single PR via codemod (`sed -i` with a curated word list + manual review); deprecation alias on the marker key gives a one-cycle escape valve.

9. **Multi-instance marker schema is a v2.** v1 markers MUST keep working during the cycle. Mitigation: validator accepts both shapes; M020 / W020 warn but don't block; migration script ready before v2 hard-stops the old shape.

10. **Cross-instance edges could explode in number.** A 5-flow repo with 3 instances each = up to 30 cross-edges per type. Mitigation: cross-instance edges are advisory `informs/informed_by` only; no enforced cardinality; rendering tools can collapse by default.

11. **helix-data overlaps with the existing data-* types.** The existing HELIX types (`data-prd`, `data-architecture`) were product-data flavoured. Promoting them to helix-data ownership risks breaking existing instances. Mitigation: the library type meta.yml stays methodology-agnostic; helix-data's graph.yml references them via `library:data-prd` like any other flow. Existing instances under helix product flow continue to validate; cross-flow edges document the handoff.

12. **Four flows × many slash commands = command soup.** Mitigation: per-flow prefix is mandatory (slash-namespace ADR finally lands as part of §6.1); bench routing-evals enforce that no flow ships a colliding command name.

---

## §17 Additional open questions

In addition to §9's questions:

6. **Should `instance:` default to `default` or be required?** Requiring it makes single-instance markers more verbose; defaulting makes the multi-instance case slightly more error-prone (you can declare instance: default twice by accident; M030 catches it but it's a footgun).

7. **Should cross-flow `informed_by` edges count toward `required` cardinality?** Probably not (advisory direction), but worth a codex pin.

8. **Is helix-data's activity set right at 7 activities?** Or does data-pipeline want fewer (Discover, Build, Operate)? Codex pass should sharpen this.

9. **Should the marker schema bump be a separate plan?** §13's marker v2 is substantial. Argument for separate: smaller blast radius per PR. Argument for combined: avoids two breaking changes spaced apart. Current plan: combined. Worth reconsidering at review.

10. **How aggressively does the bench corpus need to grow before §6.13 ships?** 25 conversations is a lot to author. We could ship a smaller v1 (15 conversations covering only the critical scenarios) and grow to 25 in §6.13. Trade: less coverage at gate vs. faster ship. **Decided after fresh-pass review: 150 rows ship at v1 per §1.5b.** Smaller v1 lets verification gaps hide. The corpus is the contract.

---

## §18 Meta-verification — testing the test itself

The bench is software. Like any software it can be wrong. Before we trust the bench's verdicts on the skill, we must verify the bench's verdicts on synthetic input where we already know the answer.

### 18.1 Synthetic transcripts (the 10-row meta-test category)

Hand-author 10 fake stream-json transcripts:

- **5 should-pass**: a transcript that REALLY shows the skill engaging correctly. The Layer 1 + (where applicable) Layer 2 assertions must verdict PASS on each. The bench runner is correct on these.
- **5 should-fail**: a transcript that subtly fails — e.g., agent writes correct file path but didn't read marker first; agent reads marker but writes to wrong scope; agent surfaces the right next-step but in the wrong prose phrasing. The assertions must verdict FAIL on each. The bench catches the subtle defects.

Author the 10 transcripts BEFORE finalizing the assertion regex/prose. Run them through the bench. Human classifier (the plan author) records expected verdict. Bench verdict must match human verdict on ≥9 of 10. If <9, the assertions are wrong and the bench has a known unreliability before any real run.

### 18.2 Calibration set for the judge LLM

Layer 2 (semantic) judgements need a separate calibration set:

- 20 paired (expected intent, actual prose) examples drawn from real probe evidence
- For each, the plan author records the human verdict
- Run them through the judge LLM at temperature=0
- Judge verdict must agree with human verdict on ≥18 of 20 (90%)
- If <18, retune the judge rubric prompt; re-run

Calibration runs quarterly OR on judge prompt change OR on model upgrade. Disagreement >10% halts judge-LLM use until rubric retuned.

### 18.3 Property-based testing of Layer 1 (NOT deferred — codex finding #8 promoted to P0)

Property generators produce stream-json transcripts with known properties — e.g., a transcript where `Read(.helix.yml)` provably precedes any `Write` (or provably does not). The assertion engine MUST classify each generated transcript correctly. Properties tested:

- `read_before_write` matcher correctly identifies ordered vs reversed vs missing
- `scope_write_path` matcher correctly identifies in-scope vs out-of-scope vs no-write
- `skill_tool_use` matcher correctly identifies skill_id presence
- `graph_edge_observed` matcher correctly identifies file-read-of-graph

100 generated cases per property at v1 ship; failures dump the offending transcript + expected vs actual verdict. Property tests run in CI on every PR (cheap; no model calls; pure assertion-engine exercise).

This catches the failure mode "the assertion engine has a bug that lets every transcript pass" before any real bench run grades production behavior on top of it.

### 18.4 Bench-runner self-test

The runner itself ships with a `--self-test` mode that runs the 10 synthetic transcripts before EVERY full bench run. If self-test fails, the bench refuses to grade any real run. This is the most basic protection against "the bench is silently broken."

CI gate: `helix_bench self-test` MUST exit 0 before `helix_bench run` is permitted on a PR.

---

## §19 Cost budget + Claude Code version pin + ratchet

### 19.1 Cost model

Per the §1.5b inventory:

| Category | Rows | Model calls per row | Determinism | Total calls/run |
|---|---|---|---|---|
| Routing evals | 75 | 1 (single probe) | 3 | 225 |
| Conversation library | 25 | 2 avg (multi-turn) | 3 | 150 |
| Autonomy matrix | 8 | 2 avg | 3 | 48 |
| Stop_at triggers | 6 | 1 | 3 | 18 |
| Graph-discrimination | 4 | 1 | 3 | 12 |
| Edge Authority Asymmetry | 4 | 1 | 3 | 12 |
| Cross-flow cascade | 3 | 3 avg | 3 | 27 |
| Multi-instance routing | 4 | 1 | 3 | 12 |
| Cross-instance | 3 | 1 | 3 | 9 |
| Rename / compat | 4 | 1 | 3 | 12 |
| Warm-context | 5 | 6 avg (replayed history) | 3 | 90 |
| Verbose-but-stuck | 4 | 1 | 3 | 12 |
| Meta-tests | 10 | 0 (synthetic) | 1 | 0 |

Total model calls per full bench run: ~627. At Sonnet rates ~$0.06/call → ~$38/full-run. Plus Layer 2 judge calls (~80 rows × 3 = 240 calls @ ~$0.02 each) → ~$5. Plus Layer 3 envelope-pass calls (~5 rows × 2 = 10 extra) → ~$1. **Full bench: ~$44 per complete run.**

### 19.2 Budget gates (revised per codex finding #9)

Codex correctly flagged that routing-only PR runs miss regressions in autonomy, stop_at, bench runner, and schema code. Better tiering:

- **Every PR**: `helix_bench self-test` (10 meta-tests, $0) + static validators ($0) + property-based tests ($0) + **affected category tests**. The runner identifies the affected category from the PR's file diff:
  - Touches `methodology-*/skills/*/SKILL.md` → conversation library + routing evals (~$48/run)
  - Touches `library/scripts/helix_check.py` → static validators + meta-tests (~$0)
  - Touches `stop-at-triggers.yml` → stop_at trigger rows (~$2/run)
  - Touches `graph.yml` files → graph-discrimination rows (~$2/run)
  - Touches marker schema → rename/compat rows (~$2/run)
  - Touches any of the above OR any `methodology-*/` content → escalate to full bench (~$44/run)
- **`main` merge**: full bench (~$44/run)
- **Nightly**: rotating thirds of full bench (~$15/run avg)
- **Weekly**: full bench + judge calibration sample (~$50/run)
- **Manual full-bench-with-fuzzing**: workflow_dispatch only; budget approved separately

Monthly cost estimate at 50 PR runs (avg ~$10/run with mix) + 10 main merges + 30 nightly thirds + 4 weekly = 500 + 440 + 450 + 200 = **~$1590/month**. Down from ~$2240 because most PRs run smaller affected-category surface, not full routing-only-vs-full bifurcation. Ratchet (§19.4) catches runaway cost.

### 19.3 Claude Code version pin

Skill router behaviour depends on Claude Code's internals, which are evolving. Without a pin we test against a moving target.

`family-test/bench/cc-version.lock`:

```
claude_code_version: 2.1.163
pinned_at: 2026-06-05
last_validated: 2026-06-05
re_validation_required_after: 2026-09-05    # 90 days
re_validation_trigger_versions:
  - 2.2.x
  - 2.1.200+
```

CI bench job reads this; if container CC version doesn't match, build fails. Re-validation requires running the full bench AND the meta-tests against the new CC version AND comparing stable-pass rates: regression >5% halts the upgrade.

### 19.4 Ratchet

Three ratchets, all in `family-test/bench/ratchets.json`:

- **stable_pass_rate**: minimum % of rows stable-pass; current rate updates after each main-merge bench; alerts if next run drops > 5pp
- **routing_precision**: positive-prompt precision must not regress > 2pp
- **cost_per_run**: alerts if monthly cost trends > 25% above baseline

Ratchets are the existing helix pattern; reuse the existing ratchet runner script.

---

## §20 Failure-modes catalog (what catches what)

For every load-bearing claim in this plan, the row category that catches its violation:

| Claim | Caught by |
|---|---|
| Skill engages on PRD prompts | Routing evals (positive) |
| Skill does NOT engage on irrelevant prompts | Routing evals (negative) |
| Skill consults graph.yml before authoring | Graph-discrimination + Verbose-but-stuck |
| Skill reads marker before any state-changing tool_use | Discriminator on every state-changing row |
| Cascade surfaces required prerequisites | Conversation library (C002, C003, C005, C006) |
| Authorization boundary rejects unauthorized flows | Conversation library (C014) |
| Autonomy ask-vs-do contract holds per level | Autonomy matrix |
| Stop_at triggers fire correctly | Stop_at trigger rows |
| Multi-instance cwd routing is deterministic | Multi-instance routing rows |
| Cross-instance edges resolve | Cross-instance rows |
| Edge Authority Asymmetry holds (no auto-populate) | Edge Authority Asymmetry rows |
| Cross-flow cascade chains work | Cross-flow cascade rows |
| Rename keeps v1 markers working | Rename / compat rows + T01-T38 re-run |
| Warm context doesn't degrade engagement | Warm-context rows |
| Bench itself is correct | Meta-tests + self-test |
| Cost doesn't run away | Cost ratchet + budget gates |
| CC version changes don't silently break | CC version pin + re-validation cadence |

Every claim has a catcher; every catcher is in §1.5b inventory; every inventory category has a phase that produces it. The plan is self-consistent at the verification level.
