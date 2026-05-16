# vhs script: Copilot CLI install scenario → recording.gif

Output recording.gif

Set FontSize 14
Set Width 1200
Set Height 700
Set Theme "Dracula"
Set Shell "bash"

Type "# HELIX install scenario: GitHub Copilot CLI"
Enter
Sleep 500ms

Type "docker build -t helix-install-test:copilot-cli ."
Enter
Sleep 25s

Type 'docker run --rm -e GH_TOKEN -v $PWD/../../..:/workspace/helix:ro helix-install-test:copilot-cli'
Enter
Sleep 12s
