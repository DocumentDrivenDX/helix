# INT-DD: DDx Integration Test — HELIX Skill Activation

This test harness exercises DDx as the reference runtime for HELIX skill activation and artifact production.

## Scope

**What it tests:**
- HELIX skill installation via `ddx install helix --local <source>`
- SCN-01 Bootstrap workflow: sparse intent → vision.md + prd.md artifacts
- Routing decision recorded in execution evidence (manifest.json)
- Negative control: no routing/artifacts without HELIX installed

**What it does NOT test:**
- Full workflow coverage (scenarios 2–6 are planned as follow-on beads)
- All per-scenario expectations (see `tests/workflows/fixtures/recipe-app/`)
- Per-runtime parity (DDx is the reference; other runtimes tested separately)

## Files

- **`run-scenarios.sh`** — Orchestrator script that:
  1. Creates temp workspace with ddx
  2. Installs HELIX from local source
  3. Creates SCN-01 bootstrap bead
  4. Runs `ddx work --once --json`
  5. Validates routing decision and artifact production
  6. Optional negative control: verifies no routing without HELIX

- **`fixtures/seed-bead.json`** — Minimal bead spec for SCN-01 (reference only; script creates beads programmatically)

- **`expected/scn-01-assertions.sh`** — Assertion checks for validation (checks manifest.json routing + artifact structure)

- **`recordings/INT-DD.tape`** — vhs script for screencast (run: `vhs tests/workflows/ddx/recordings/INT-DD.tape`)

## Usage

### Run the test (requires `ANTHROPIC_API_KEY` for routing)

```bash
bash tests/workflows/ddx/run-scenarios.sh
```

Exit code 0 on success (all assertions passed).

### With negative control

```bash
bash tests/workflows/ddx/run-scenarios.sh --no-skill
```

Also tests that removing HELIX prevents skill activation.

### Generate screencast

```bash
vhs tests/workflows/ddx/recordings/INT-DD.tape
```

Output: `tests/workflows/ddx/recordings/INT-DD.gif`

## Assertions

### 1. Routing decision recorded

Checks `.ddx/executions/<timestamp>/manifest.json` for:
- `harness` field (e.g., "claude", "codex")
- `model` field (e.g., "opus", "sonnet")

Routing recorded as `harness/model` (e.g., `claude/opus`).

### 2. Artifact existence

Verifies after execution:
- `docs/helix/00-discover/product-vision.md` OR
- `docs/helix/01-frame/prd.md`

(HELIX may produce both; test accepts either as evidence of activation.)

### 3. Frontmatter validation

If prd.md exists, checks for:
- `ddx:` frontmatter block with required fields

### 4. Negative control (optional)

Without HELIX installed:
- No routing decision in execution evidence
- No HELIX artifacts produced

## Expected behavior

**Success:**
```
→ Routing decision recorded (claude/opus)
✓ Assertion 2a: product-vision.md exists
✓ Assertion 3: PRD carries ddx: frontmatter
✓ Core assertions passed
```

**Without API key (routing incomplete):**
```
! No execution manifest found (may be awaiting agent execution or API key)
✓ Assertion 2a: product-vision.md exists
! PRD missing ddx: frontmatter (artifact produced but not yet HELIX-governed)
```

**Without HELIX (negative control):**
```
✓ Assertion 4: No HELIX routing without skill (no bead execution)
```

## Dependencies

- `ddx` CLI (v0.6.2+)
- Bash 4+
- `jq` (for JSON parsing)
- `git` (implicit, since this is a git repo)
- `ANTHROPIC_API_KEY` environment variable (optional; routing will fail without it)

## Troubleshooting

### Test workspace issues

The script creates workspaces at `/tmp/ddx_test_<pid>` to avoid character validation issues in ddx ID generation. If you see "invalid id: charset" errors, check that the directory path doesn't contain dots or special characters.

### Bead creation hangs

If `ddx bead create` hangs indefinitely, ensure:
- ddx is properly initialized (`ddx bead init` has run)
- No prior hanging ddx processes exist (`pkill -f ddx`)
- The temporary directory has normal permissions

### No execution evidence

If `.ddx/executions/` remains empty after `ddx work --once`:
- The bead may not have been picked up (check `ddx bead ready`)
- The agent harness may not be configured (check ddx configuration)
- API key may be missing or invalid (export `ANTHROPIC_API_KEY`)

## Integration with CI/CD

Expected invocation:

```bash
export ANTHROPIC_API_KEY="sk-..."
bash tests/workflows/ddx/run-scenarios.sh
```

On failure, the script exits nonzero. Logs are printed to stdout/stderr for inspection.

## Related

- `docs/helix/03-test/test-plans/TP-014-helix-workflow-coverage.md` — Full test plan (scenarios 1–7)
- `tests/workflows/fixtures/recipe-app/` — Shared fixture data (intent seeds, baseline artifacts, expectations)
- `tests/workflows/genie/` — Genie Code integration test (browser-based variant)
- `docs/install/ddx.md` — DDx-specific HELIX invocation guide
