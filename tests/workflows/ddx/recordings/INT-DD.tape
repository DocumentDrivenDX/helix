# vhs script: capture the DDx + HELIX integration test (INT-DD)
#
# Shows: install HELIX → create SCN-01 bead → run ddx work --once → verify artifacts
#
# Run:
#   cd <helix-repo>
#   vhs tests/workflows/ddx/recordings/INT-DD.tape
# Output:
#   tests/workflows/ddx/recordings/INT-DD.gif

Output tests/workflows/ddx/recordings/INT-DD.gif

Set FontSize 14
Set Width 1400
Set Height 800
Set Theme "Dracula"
Set Shell "bash"

# Title
Type "# HELIX on DDx: Integration Test (SCN-01 Bootstrap)"
Enter
Sleep 500ms

# Navigate to test directory
Type "cd tests/workflows/ddx"
Enter
Sleep 1s

# Show the intent seed
Type "cat ../../fixtures/recipe-app/seed/intent.txt"
Enter
Sleep 2s

# Install HELIX locally
Type "ddx install helix --local ../.. --force"
Enter
Sleep 3s

# Verify installation
Type "ls -la ~/.ddx/plugins/helix/ | head -10"
Enter
Sleep 2s

# Initialize test workspace
Type "cd /tmp && mkdir helix-ddx-test && cd helix-ddx-test"
Enter
Sleep 1s

Type "ddx bead init"
Enter
Sleep 1s

# Copy fixture baseline
Type "cp -r $OLDPWD/../../fixtures/recipe-app/baseline/* ."
Enter
Sleep 1s

# Create the SCN-01 bead
Type "INTENT='Build a recipe-sharing app for amateur cooks...'"
Enter
Sleep 500ms

Type "ddx bead create 'SCN-01: Bootstrap recipe-sharing app' --type task --priority 1 --labels helix,phase:test,activity:frame"
Enter
Sleep 2s

# Show the bead we just created
Type "ddx bead ready --json | jq '.[] | {id, title}'[:1]"
Enter
Sleep 2s

# Run the execution
Type "ddx work --once --json | jq '.results[] | {route, status}'"
Enter
Sleep 5s

# Check for artifacts
Type "ls -la docs/helix/00-discover/ docs/helix/01-frame/ 2>/dev/null | grep -E '\\.md$'"
Enter
Sleep 2s

# Show artifact header
Type "head -20 docs/helix/01-frame/prd.md"
Enter
Sleep 3s

# Final status
Type "echo 'INT-DD Test: Complete ✓'"
Enter
Sleep 500ms
