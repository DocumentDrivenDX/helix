# vhs script: Claude Code install scenario → recording.gif

Output recording.gif

Set FontSize 14
Set Width 1200
Set Height 700
Set Theme "Dracula"
Set Shell "bash"

Type "# HELIX install scenario: Claude Code"
Enter
Sleep 500ms

Type "docker build -t helix-install-test:claude-code ."
Enter
Sleep 15s

Type 'docker run --rm -e ANTHROPIC_API_KEY -v $PWD/../../..:/workspace/helix:ro helix-install-test:claude-code'
Enter
Sleep 10s
