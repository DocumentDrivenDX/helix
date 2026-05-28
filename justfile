# HELIX development tasks

# Run all tests
test: test-deploy-artifacts test-state-rules test-skills test-context-digests test-demo-fixtures

# Serve the HELIX microsite at the canonical local review URL.
website-serve:
    bash website/scripts/serve-local.sh

# Validate deploy artifact graph consistency
test-deploy-artifacts:
    bash tests/validate-deploy-artifacts.sh

# Validate state detection rules
test-state-rules:
    bash tests/validate-state-rules.sh

# Run skill package validation
test-skills:
    bash tests/validate-skills.sh

# Validate live tracker context-digest coverage
test-context-digests:
    bash tests/validate-context-digests.sh

# Validate demo prompt fixtures
test-demo-fixtures:
    bash tests/validate-demo-fixtures.sh

# Run all tests and check for stale references
check: test lint

# Lint for common issues
lint:
    @echo "Checking for stale command references..."
    @! grep -rn 'NEXT_ACTION.*IMPLEMENT\b' workflows/ tests/ --include='*.sh' --include='*.md' 2>/dev/null | grep -v 'BUILD|IMPLEMENT' || (echo "FAIL: stale IMPLEMENT references found" && exit 1)
    @! grep -rn 'NEXT_ACTION.*\bPLAN\b' workflows/actions/check.md tests/ 2>/dev/null | grep -v 'DESIGN|PLAN_STATUS\|PLAN_DOCUMENT\|PLAN_ROUNDS' || (echo "FAIL: stale PLAN references found" && exit 1)
    @echo "Checking git diff..."
    @git diff --check || true
    @echo "Lint OK"

# Lint hand-authored site prose for AI-writing patterns (see docs/website/CLAUDE.md)
lint-prose:
    vale docs/website/content

# Verify generated/published site content is current and complete
test-website-generated:
    bash tests/validate-website-generated.sh

# Install HELIX via DDx (refresh the local snapshot)
install:
    ddx install helix --force

# Build the Databricks Genie skill bundle (dist/genie-bundle/helix/)
genie-build:
    bash scripts/build-genie-bundle.sh

# Install the Genie bundle to a Databricks workspace
# Requires DATABRICKS_HOST and DATABRICKS_TOKEN env vars
genie-install:
    python scripts/install-genie.py

# Verify a Genie install (offline static checks, no chat API)
genie-verify:
    python scripts/verify-genie.py

# Run the per-runtime install test scenarios (Docker + screencasts)
install-test:
    bash tests/install/run-all.sh

# Show test count
count:
    @echo "Skill files: $(find skills -name 'SKILL.md' | wc -l)"
    @echo "Test scripts: $(ls tests/*.sh tests/*.py 2>/dev/null | wc -l)"
