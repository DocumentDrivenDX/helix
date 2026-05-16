# vhs script: capture the DDx install scenario as a .gif
#
# Run: vhs tests/install/ddx/record.tape
# Output: tests/install/ddx/recording.gif

Output recording.gif

Set FontSize 14
Set Width 1200
Set Height 700
Set Theme "Dracula"
Set Shell "bash"

Type "# HELIX install scenario: DDx"
Enter
Sleep 500ms

Type "docker build -t helix-install-test:ddx ."
Enter
Sleep 8s

Type "docker run --rm -v $PWD/../../..:/workspace/helix:ro helix-install-test:ddx"
Enter
Sleep 10s
