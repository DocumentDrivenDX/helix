# vhs script: Codex CLI install scenario → recording.gif

Output recording.gif

Set FontSize 14
Set Width 1200
Set Height 700
Set Theme "Dracula"
Set Shell "bash"

Type "# HELIX install scenario: OpenAI Codex CLI"
Enter
Sleep 500ms

Type "docker build -t helix-install-test:codex-cli ."
Enter
Sleep 20s

Type 'docker run --rm -e OPENAI_API_KEY -v $PWD/../../..:/workspace/helix:ro helix-install-test:codex-cli'
Enter
Sleep 12s
