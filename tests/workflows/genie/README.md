# Genie Code HELIX Workflow Integration Test

This directory contains the Playwright-based integration test for HELIX skill activation on Databricks Genie Code. The test drives the Genie chat surface via headless Chromium, exercises three key scenarios, and asserts on structural DOM signals that the HELIX skill engaged.

## Overview

- **Driver**: `genie-playwright-driver.py` — Playwright script that automates Genie chat
- **Orchestrator**: `run-scenarios.sh` — Bash wrapper for dependency checks, recording management, and result reporting
- **Scenarios**:
  - `install-verify` — Confirm HELIX skill is installed and discoverable
  - `skill-list` — List HELIX workflow modes (asserts skill activation)
  - `bootstrap` — Bootstrap a TODO list app with HELIX framing (asserts skill activation + artifact generation)
- **Evaluations**: `evals/routing.jsonl` — Expected routing modes and artifacts for each scenario
- **Recordings**: `recordings/INT-GN.webm` + `recordings/INT-GN-events.json` — Playwright webm screencast + per-prompt event logs

## Prerequisites

1. **Databricks workspace** with HELIX skill installed (`docs/install/databricks-genie.md`)
2. **Genie Code enabled** in the workspace
3. **Python 3.8+** with Playwright installed:
   ```bash
   pip install playwright
   playwright install chromium
   ```
4. **DBAUTH session cookie** (obtained from browser DevTools or workspace auth flow)

## Running the tests

### 1. Get DBAUTH cookie

In Databricks (using any browser):
1. Open DevTools (F12)
2. Go to Application → Cookies
3. Find `DBAUTH` cookie and copy its value
4. Save to a file (e.g., `/tmp/dbauth.txt`)

### 2. Set environment

```bash
export DATABRICKS_HOST="https://adb-123456789.azuredatabricks.net"
export DATABRICKS_WORKSPACE_URL="https://adb-123456789.azuredatabricks.net/?o=123456789"
export DBAUTH_COOKIE_PATH="/tmp/dbauth.txt"
export HELIX_REPO_PATH="."  # or path to helix repo
```

### 3. Run the test

```bash
bash tests/workflows/genie/run-scenarios.sh
```

### 4. Verify recordings

After a successful run:
- `tests/workflows/genie/recordings/INT-GN.webm` — Playwright headless Chromium recording (screencast)
- `tests/workflows/genie/recordings/INT-GN-events.json` — Aggregated per-scenario event logs

## Test assertions

### Activation assertion (AC #2)

Each scenario checks for a structural DOM signal that HELIX skill engaged:

1. **install-verify**: May not invoke skill; passes on expected text patterns
2. **skill-list**: Checks for `helix` text in DOM + skill-related indicators
3. **bootstrap**: Checks for `helix` text + artifact creation in workspace

Selectors used for detection:
- `:has-text("helix")`
- `[class*="skill"]` / `[class*="tool"]`
- `[data-skill="helix"]`
- Content grep for "helix" + "skill/tool" in page text

### Negative control (AC #3)

Run with `--no-skill` flag to verify activation assertions fail when HELIX is uninstalled:

```bash
bash tests/workflows/genie/run-scenarios.sh --no-skill
```

Expected: Script exits nonzero due to missing skill activation signals.

## Files

```
tests/workflows/genie/
  README.md                          # This file
  run-scenarios.sh                   # Main orchestrator script
  genie-playwright-driver.py         # Playwright automation driver
  scenarios/
    install-verify.prompt            # Scenario 1 prompt
    skill-list.prompt                # Scenario 2 prompt (requires @helix prefix)
    bootstrap.prompt                 # Scenario 3 prompt (bootstrap workflow)
  expected/
    install-verify.expect            # Expected text patterns
    skill-list.expect                # Expected modes/activities
    bootstrap.expect                 # Expected artifacts
  evals/
    routing.jsonl                    # Routing expectations (prompt → mode → artifacts)
  recordings/
    INT-GN.webm                      # Playwright webm screencast (committed after test)
    INT-GN-events.json               # Aggregated event logs (committed after test)
    INT-GN-events.json.template      # Example structure
```

## Troubleshooting

### "Chat input field not found"

- Genie UI may have changed; update selectors in `genie-playwright-driver.py::_run_scenario()`

### "DBAUTH cookie file not found"

- Verify `DBAUTH_COOKIE_PATH` env var points to a readable file
- Cookie file should contain just the DBAUTH token value (no prefix)

### "Playwright not installed"

```bash
pip install playwright
playwright install chromium
```

### "Response wait timeout"

- Genie may be slow; adjust `timeout_seconds` in `_wait_for_response()`
- Check workspace logs for skill execution errors

### "No HELIX skill activation detected"

For `skill-list` and `bootstrap` scenarios, the driver looks for a structural DOM signal. If this fails:

1. Check browser console for errors (run manually against workspace)
2. Verify HELIX skill is installed: `curl https://workspace/api/2.0/workspace/get-status /Users/<you>/.assistant/skills/helix/SKILL.md`
3. Update DOM selectors in `_detect_skill_activation()` if Genie UI changed

## Recording playback

The webm recording captures the full automated flow. To watch:

```bash
mpv tests/workflows/genie/recordings/INT-GN.webm
# or
ffplay tests/workflows/genie/recordings/INT-GN.webm
```

The recording is the screencast evidence of the test, including:
1. Workspace page load + Genie Code panel opening
2. Each prompt typed and submitted
3. HELIX skill response (or failure if negative control)
4. Full response text + any artifact creation

## See also

- `docs/install/databricks-genie.md` — HELIX on Genie Code installation guide
- `docs/helix/03-test/test-plans/TP-014-helix-workflow-coverage.md` — Full workflow test plan
- `tests/install/genie/` — Offline verification (file presence, frontmatter parsing)
- `tests/workflows/claude-code/` — Parallel integration test for Claude Code (stream-json assertion pattern)
