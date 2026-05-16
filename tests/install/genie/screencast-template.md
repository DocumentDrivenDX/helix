# Genie screencast — what to capture

Required artifact per release: one screencast in
`tests/install/genie/recordings/` showing a clean HELIX install plus
the three verification prompts answered correctly.

## Capture sequence

1. **Terminal frame (~60 seconds)**:
   - Visible prompt: `bash scripts/build-genie-bundle.sh` and its
     output (the "Genie bundle built: ..." summary)
   - `python tests/install/genie/install.py` and its output
   - `python tests/install/genie/verify.py` and its output (asserting
     all checks pass)
2. **Browser frame (~3 minutes)**:
   - Open Databricks workspace
   - Open Genie Code in Agent mode
   - Start a new chat
   - Run prompt 1 (list modes); wait for full response
   - Run prompt 2 (catalog reachable); wait for full response
   - Run prompt 3 (smoke routing); wait for full response
3. **Closing terminal frame (~15 seconds)**:
   - Re-run `python tests/install/genie/verify.py` to show the install
     is still healthy after the chat exchanges

## File naming

```
tests/install/genie/recordings/
  <YYYY-MM-DD>-verify.mp4       # video (preferred for browser portion)
  <YYYY-MM-DD>-verify.json      # metadata sidecar (see test-procedure.md)
  <YYYY-MM-DD>-verify-terminal.gif   # optional: vhs-style gif of terminal frames
```

Use the install/verify date (UTC) as the prefix. Multiple captures on
the same date may add a suffix: `2026-05-16-verify-attempt2.mp4`.

## Quality bar

- Resolution: ≥ 1280×720 for the browser portion (Genie UI text is small)
- Frame rate: ≥ 15 fps (text legibility)
- Audio: not required; if present, do not include credential values
- Length: aim for under 5 minutes total
- Format: mp4 preferred for the browser portion; gif acceptable for
  terminal-only captures

## What must be readable

In playback at native resolution, a reviewer must be able to read:

- The terminal output lines confirming install + verify pass
- The Genie response text for each of the three prompts
- The classification labels in prompt 3's response (`ALIGNED`,
  `INCOMPLETE`, `DIVERGENT`, `UNDERSPECIFIED`, `STALE_PLAN`, `BLOCKED`)

## Redaction

Before sharing:

- Mask `DATABRICKS_HOST` if it identifies a customer workspace
- Mask any user names or org details that reveal account state
- Redact `DATABRICKS_TOKEN` if it appears in any visible env (it should
  not — the scripts never echo tokens)

## See also

- [test-procedure.md](test-procedure.md) — the prompts and pass criteria
- [docs/install/databricks-genie.md](../../../docs/install/databricks-genie.md)
