# vhs script: Codex CLI HELIX integration test → INT-CX.gif

Output INT-CX.gif

Set FontSize 14
Set Width 1200
Set Height 700
Set Theme "Dracula"
Set Shell "bash"

Type "# HELIX integration test: OpenAI Codex CLI"
Enter
Sleep 500ms

Type "cd tests/workflows/codex-cli"
Enter
Sleep 500ms

Type "# Run the complete integration test harness"
Enter
Sleep 300ms

Type "bash run-scenarios.sh"
Enter
Sleep 20s
