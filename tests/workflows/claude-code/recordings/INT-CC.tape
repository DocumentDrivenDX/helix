# vhs script: HELIX Claude Code integration test (INT-CC)
# Demonstrates the structure and workflow of the HELIX skill integration tests

Output INT-CC.gif

Set FontSize 14
Set Width 1200
Set Height 700
Set Theme "Dracula"
Set Shell "bash"

Type "# HELIX Claude Code Integration Test (INT-CC)"
Enter
Sleep 500ms

Type "# Test structure: scenarios → stream-json parsing → skill activation verification"
Enter
Sleep 500ms

Type "# Scenario 1: Bootstrap TODO list app with HELIX framing"
Enter
Sleep 300ms

Type "cat tests/workflows/claude-code/scenarios/bootstrap.prompt"
Enter
Sleep 1s

Type "I want to build a TODO list app. Use HELIX to capture the framing artifacts."
Enter
Sleep 500ms

Type "# Expected outputs from bootstrap scenario:"
Enter
Sleep 300ms

Type "cat tests/workflows/claude-code/expected/bootstrap.expect"
Enter
Sleep 1.5s

Type "# Test harness verifies tool_use events in stream-json output"
Enter
Sleep 500ms

Type "# See: tests/workflows/claude-code/run-scenarios.sh for implementation"
Enter
Sleep 500ms

Type "# Run all scenarios (requires ANTHROPIC_API_KEY):"
Enter
Sleep 300ms

Type "bash tests/workflows/claude-code/run-scenarios.sh"
Enter
Sleep 2s
