# Codex CLI HELIX Integration Tests

This harness exercises the HELIX skill routing behavior with the OpenAI Codex CLI runtime.

## What it tests

- **Skill installation** — HELIX can be placed in Codex's skill discovery paths
- **Skill activation** — Codex invokes HELIX when asked for bootstrap, routing, or verification
- **Behavioral correctness** — responses contain HELIX-specific terminology and modes
- **Negative control** — uninstalled skill produces different behavior (no skill invocation)

## Install location ambiguity

Codex CLI supports two skill installation paths depending on installer version:

- **Path A** (newer): `~/.codex/skills/helix/` (primary, [agentskills.io](https://agentskills.io) standard)
- **Path B** (older): `~/.agents/skills/helix/` (legacy)

The test harness checks both locations during skill installation and verifies the skill is discoverable at whichever path the installer chose. See [docs/install/codex.md:36](../../docs/install/codex.md) for version history.

## Running the tests

### Prerequisites

- Docker (builds the test image)
- `jq` (optional, for JSON parsing if available)
- `OPENAI_API_KEY` or `CODEX_API_KEY` environment variable

### Basic run

```bash
export OPENAI_API_KEY="sk-..."
bash tests/workflows/codex-cli/run-scenarios.sh
```

Exit 0 on all scenarios passing; nonzero if any fail.

### Negative control (--no-skill)

```bash
bash tests/workflows/codex-cli/run-scenarios.sh --no-skill
```

Verifies that HELIX behavior is absent when the skill is not installed. This test currently runs as a side effect of the main run and documents any gaps.

## Test scenarios

| Scenario | Purpose | Observable |
|---|---|---|
| `install-verify` | Confirms skill can be discovered | Response mentions SKILL.md, helix, workflows |
| `skill-list` | Lists routing modes | Response contains: input, frame, align, evolve, design, review |
| `bootstrap` | Runs a framing scenario | Response names product-vision, prd, and uses frame/input modes |

## Expected output

```
→ Building Docker image: helix-int-test:codex-cli
→ Test temp directory: /tmp/...
→ Loaded routing evaluations from: .../evals/routing.jsonl
→ Running scenario: install-verify
→   Input: Confirm HELIX is installed...
→   ✓ Scenario passed: install-verify
→ Running scenario: skill-list
→   Input: List the HELIX routing modes...
→   ✓ Scenario passed: skill-list
→ Running scenario: bootstrap
→   Input: I want to build a TODO list app...
→   ✓ Scenario passed: bootstrap
→ Running negative control: skill uninstalled
→   ✓ Negative control: Skill behavior absent when skill uninstalled

→ Test Results
→ ============
→ Passed: 3/3
→   ✓ install-verify
→   ✓ skill-list
→   ✓ bootstrap
→ All scenarios passed
```

## Activation signal

**Note on structured output:** Codex CLI versions differ in whether they expose tool/skill invocation events in machine-readable format. The harness uses Codex's **behavioral signal** (response contains HELIX-specific terminology and modes) as the activation indicator, as this is:

1. **Runtime-neutral**: works across Codex versions regardless of output format
2. **User-observable**: reflects what the user would actually see
3. **Highest-confidence**: asserts end-to-end routing behavior, not just tool-call metadata

If a future Codex version exposes structured `tool_use` events (like Claude Code's `stream-json` format), the harness can evolve to validate both the structured signal AND the behavioral signal for increased confidence.

## Recording

Generate a screencast with vhs:

```bash
cd tests/workflows/codex-cli/recordings
vhs < INT-CX.tape
```

Output: `INT-CX.gif` (committed to the repo, linked in [docs/install/codex.md](../../docs/install/codex.md))

## See also

- [docs/install/codex.md](../../docs/install/codex.md) — Codex CLI skill installation guide
- [tests/workflows/claude-code/](../claude-code/) — Claude Code equivalent harness
- [tests/install/codex-cli/](../../tests/install/codex-cli/) — Docker image definition
- [skills/helix/SKILL.md](../../skills/helix/SKILL.md) — HELIX routing skill
