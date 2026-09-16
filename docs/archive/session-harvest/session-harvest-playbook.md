# Session-Harvest Playbook

A reproducible loop for mining local AI-coding-agent sessions (Claude Code, Codex)
to find (a) recurring use cases worth baking into HELIX and (b) deficiencies in the
ddx/HELIX ecosystem that the operator had to manually paper over.

The premise: every prompt an operator types is either **intentful** (irreducible
human steering — product/design/architecture decisions only a human can make) or
**deficiency-papering** (the prompt only exists because the methodology or the agent
failed to do something it should have done automatically). The papering prompts are
a backlog. Driving that backlog toward zero is the goal.

## 1. Harvest (deterministic)

`scripts/harvest_sessions.py` extracts operator-typed prompts from local sessions and
filters out injected machine context (environment/permission blocks, codex goal
re-injection, subagent notifications, `AGENTS.md` injections, sidechains, tool
results). It does no judgement — it produces a clean, reproducible corpus.

```sh
# human-readable digest, grouped by project, last 4 days
scripts/harvest_sessions.py --since 4

# machine corpus for downstream analysis
scripts/harvest_sessions.py --since 7 --format jsonl

# scope to one project / harness
scripts/harvest_sessions.py --since 4 --project myrepo --harness codex
```

Sources (auto-discovered; override with `--claude-root` / `--codex-root`):

- Claude Code — `~/.claude/projects/<encoded-cwd>/<uuid>.jsonl` (often a symlink)
- Codex — `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl`

Corpora contain private cross-project prompts. **Do not commit them.** Write them to
a scratch dir outside the repo (e.g. `~/.cache/helix-harvest/`).

## 2. Classify (sharded judgement)

The intentful-vs-papering split is judgement, so hand it to a model. Shard by project
(one analysis agent per project) so each stays in context, and have each agent run the
harvester itself for reproducibility. Each agent returns:

- **Recurring use cases** — candidates to bake into HELIX, with frequency.
- **Deficiency-papering** — what the system should have done, with severity and
  short evidence snippets.
- **Genuinely intentful prompts** — leave alone.
- **One-line verdict** — fraction papering vs intent, biggest single gap.

Then synthesize across shards: rank deficiencies by **breadth × severity** (a gap that
recurs across many projects outranks a deep one-off).

## 3. Triage into work

The papering categories are the backlog. For each ranked deficiency:

- If HELIX-ownable (a methodology gate, concern, ratchet, or artifact), file it against
  HELIX.
- If runtime-ownable (durable task state, dispatch ergonomics, cross-repo work-state),
  file it against ddx.

Recurring deficiency categories seen in practice:

| Category | What the system should do instead |
|---|---|
| "Done" ≠ usable | An agent must exercise the runtime boundary (real client, real network, `apply`) before declaring done — not stop at green unit tests. |
| No durable loop state | The loop/task layer owns the cursor (progress, DONE list, file targets) so the operator never re-injects it. |
| Hand-pasted converge loop | "review until it converges, then implement, then review again" is an enforced mode, not boilerplate the operator types. |
| Agent stalls for affirmation | A pre-approved plan runs to completion without per-step "yes/continue" checkpoints. |
| Unrequested stubs / gold-plating | YAGNI is a build exit gate: no legacy shims, no speculative changes, no scope the task didn't request. |
| Spec/doc drift | Reconcile against spec is in the done-criteria, not a separate follow-up prompt. |

## 4. Measure (close the loop)

Re-harvest on a cadence. **Papering-rate per category is the metric** — it should fall
as gates land. This connects directly to the HELIX bench: a gate that works shows up as
fewer papering prompts in the next harvest.
