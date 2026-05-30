# Copilot CLI HELIX Integration Tests

This harness exercises the HELIX skill routing behavior with the GitHub Copilot CLI runtime.

## What it tests

- **Instruction installation** — HELIX can be installed via `.github/copilot-instructions.md`
- **Instruction activation** — Copilot CLI reads and applies HELIX instructions for bootstrap, routing, or verification
- **Behavioral correctness** — responses contain HELIX-specific terminology and modes
- **Negative control** — instructions absent produces different behavior (no HELIX signal)

## Activation signal: Copilot CLI behavioral signal

**Important caveat:** GitHub Copilot CLI (`gh copilot suggest`) is **shell-command-oriented**, not free-form chat. It differs from chat-based runtimes in how it exposes skill activation:

- **Claude Code**: tool_use events in structured `stream-json` format
- **Codex CLI**: LLM output with semantic routing signal
- **Copilot CLI**: shell suggestions with context from `.github/copilot-instructions.md`

Copilot CLI **does not expose a direct tool/skill-invocation event**. Instead, the harness validates the **behavioral signal**:

1. **Strongest signal available**: response contains HELIX-specific terminology (routing modes, artifact names) proving that instructions were read
2. **User-observable**: reflects what the user would actually see
3. **Runtime-neutral**: works across Copilot versions regardless of underlying API changes

If GitHub exposes structured invocation metadata in a future Copilot release, the harness can evolve to validate both structural AND behavioral signals.

## Running the tests

### Prerequisites

- Docker (builds the test image)
- `GITHUB_TOKEN` environment variable with Copilot license
  - Token must belong to a GitHub Pro, GitHub Copilot Business, or GitHub Copilot Enterprise user
  - Personal access token (PAT) or GitHub CLI authentication (via `gh auth`)

### Basic run

```bash
export GITHUB_TOKEN="github_pat_..."
bash tests/workflows/copilot-cli/run-scenarios.sh
```

Exit 0 on all scenarios passing; nonzero if any fail.

### Negative control (--no-helix)

```bash
bash tests/workflows/copilot-cli/run-scenarios.sh --no-helix
```

Verifies that HELIX behavior is absent when instructions are not installed. This test currently runs as a side effect of the main run and documents any gaps.

## Test scenarios

| Scenario | Purpose | Observable |
|---|---|---|
| `install-verify` | Confirms instructions can be discovered | Response mentions helix, SKILL.md, workflows |
| `skill-list` | Lists routing modes | Response contains: input, frame, align, evolve, design, review |
| `bootstrap` | Runs a framing scenario | Response names product-vision, prd, and uses frame/input modes |

## Expected output

```
→ Building Docker image: helix-int-test:copilot-cli
→ Test temp directory: /tmp/...
→ Running scenario: install-verify
→   Input: Confirm HELIX is installed...
→   ✓ Scenario passed: install-verify
→ Running scenario: skill-list
→   Input: List the HELIX routing modes...
→   ✓ Scenario passed: skill-list
→ Running scenario: bootstrap
→   Input: I want to build a TODO list app...
→   ✓ Scenario passed: bootstrap
→ Running negative control: HELIX instructions removed
→   ✓ Negative control: HELIX not referenced when instructions absent

→ Test Results
→ ============
→ Passed: 3/3
→   ✓ install-verify
→   ✓ skill-list
→   ✓ bootstrap
→ All scenarios passed
```

## Activation signal limitations and evidence trail

**Limitation**: Copilot CLI's `gh copilot suggest` surface is suggest-shaped (command suggestions) rather than narrative chat. The response may be brief or terse compared to chat surfaces.

**Evidence trail**: The harness captures:
1. Full response text from `gh copilot suggest`
2. Git status (behavioral evidence) if the repo state changed
3. Exit code (0 = success, nonzero = error)

**Why this matters**: Multi-file authoring (e.g., creating new documents) works better in Copilot IDE Chat or cloud agent. For Copilot CLI, the test focuses on **plan and recommendation** output (which mode to use, where to start) rather than **artifact generation**.

## Recording

Generate a screencast with vhs:

```bash
cd tests/workflows/copilot-cli/recordings
vhs < INT-CP.tape
```

Output: `INT-CP.gif` (committed to the repo, linked in [docs/install/copilot.md](../../docs/install/copilot.md))

## See also

- [docs/install/copilot.md](../../docs/install/copilot.md) — Copilot CLI skill installation guide
- [tests/workflows/codex-cli/](../codex-cli/) — Codex CLI equivalent harness
- [tests/workflows/claude-code/](../claude-code/) — Claude Code equivalent harness
- [tests/install/copilot-cli/](../../tests/install/copilot-cli/) — Docker image definition
- [skills/helix/SKILL.md](../../skills/helix/SKILL.md) — HELIX routing skill
