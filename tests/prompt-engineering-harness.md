# HELIX Prompt Engineering Harness (Live Testing)

This harness tests **actual agent behavior** across autonomy levels using live model runs. Model selection and performance ARE part of the test surface - we're measuring how well different models execute HELIX prompts under different autonomy constraints.

## Philosophy

- Test with **live agents**, not virtual replay
- Model choice is a **test variable**, not an implementation detail
- Measure **real outputs** from real model runs
- Accept variance between runs; use statistical measures
- Each test run produces **measurable artifacts** for comparison
- Track performance across models to inform selection decisions

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Test Scenario (Vision Statement + Constraints)              │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  Model Selection                                             │
│  • claude-3.5-sonnet (default, balanced)                    │
│  • claude-3.7-sonnet (high reasoning)                       │
│  • gpt-4o-codex (code-focused)                              │
│  • gpt-5.2-codex (latest code model)                        │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  Autonomy Level + Config                                     │
│  • Low: Ask questions, push back                            │
│  • Medium: Obvious decisions + questions                    │
│  • High: Complete stack with assumptions                    │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  Live Agent Execution                                        │
│  ddx agent run --harness claude|codex                       │
│  • Real API calls, real tokens                              │
│  • Captured output for analysis                             │
│  • Timeout protection (max 15 min per test)                 │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  Artifact Generation                                         │
│  • Vision → PRD → FEAT → US → SD → TD → TP                  │
│  • Each layer measured against acceptance criteria           │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  Measurement & Scoring                                       │
│  • Completeness, Quality, Correctness, Efficiency            │
│  • Statistical aggregation across multiple runs              │
│  • Model comparison matrices                                │
└──────────────────────────────────────────────────────────────┘
```

---

## Test Scenarios

### Scenario A: Simple CLI Tool (Baseline)

**Vision Statement**:
> "Build a CLI tool that converts temperatures between Celsius, Fahrenheit, and Kelvin. Should support batch conversion from files and have a clean API."

**Constraints**:
- Language: TypeScript or Rust
- Must include tests
- Must have help documentation  
- Target: Single developer, weekend project

**Expected Artifact Stack**:
```
Vision → PRD → 
  FEAT-001-core-conversion → US-001-cli-interface → TD-001 → TP-001 → Code
  FEAT-002-batch-files → US-002-file-io → TD-002 → TP-002 → Code
```

**Autonomy Level Tests**:

| Level | Expected Behavior | Measurement Criteria |
|-------|------------------|---------------------|
| **Low** | Asks clarifying questions before creating artifacts | ≥3 specific questions, 0-1 artifacts created |
| **Medium** | Creates PRD with assumptions documented, asks remaining questions | PRD + FEATs created, ≤2 open questions |
| **High** | Complete artifact stack (PRD→FEAT→US→TD→TP) with reasonable defaults | ≥90% of expected artifacts, all decisions traceable |

---

### Scenario B: Web API with Auth (Medium Complexity)

**Vision Statement**:
> "Build a REST API for managing user profiles with OAuth authentication. Needs to scale to 10k users initially."

**Constraints**:
- Must use PostgreSQL
- OAuth2/OIDC required
- Rate limiting needed
- Docker deployment
- Team of 3 developers

**Expected Artifact Stack**:
```
Vision → PRD → 
  FEAT-001-user-management → US-001-create-profile, US-002-update-profile → TDs → TPs
  FEAT-002-oauth-auth → US-003-login-with-google, US-004-token-refresh → TDs → TPs  
  FEAT-003-rate-limiting → US-005-api-throttling → TD → TP
Architecture: ADR-001-database-choice (Postgres), ADR-002-auth-provider
```

**Autonomy Level Tests**:

| Level | Expected Behavior | Measurement Criteria |
|-------|------------------|---------------------|
| **Low** | Questions on auth provider, framework choice, rate limit values | ≥4 questions covering key decisions |
| **Medium** | PRD + ADRs created, assumptions documented for common choices | PRD + 2 ADRs, operational details questioned |
| **High** | Complete stack including OAuth flow designs, DB schema, API specs | Full hierarchy with ADRs, all constraints addressed |

---

### Scenario C: Complex System (Full Stack)

**Vision Statement**:
> "Build a real-time collaborative document editor like Google Docs. Multiple users editing simultaneously with conflict resolution."

**Constraints**:
- Real-time sync required (< 100ms latency)
- Must handle 100 concurrent editors per doc
- Web-based, works offline
- Conflict resolution algorithm needed
- Team of 5, 3-month timeline

**Expected Artifact Stack**:
```
Vision → PRD → 
  FEAT-001-realtime-sync → US-001-cursor-tracking, US-002-change-propagation → TDs (OT/CRDT) → TPs
  FEAT-002-conflict-resolution → US-003-merge-strategy → TD (algorithm choice) → TP
  FEAT-003-offline-support → US-004-local-storage, US-005-sync-on-reconnect → TDs → TPs
Architecture: ADR-001-sync-algorithm (OT vs CRDT), ADR-002-websocket-provider
```

**Autonomy Level Tests**:

| Level | Expected Behavior | Measurement Criteria |
|-------|------------------|---------------------|
| **Low** | Pushes back on timeline, questions algorithm choice, clarifies requirements | Challenges feasibility, ≥5 critical questions |
| **Medium** | PRD with risk flags, ADR for sync algorithm, operational questions | PRD + 1-2 ADRs, concerns documented as risks |
| **High** | Complete technical design including CRDT/OT approach, WebSocket architecture | Full stack with complex decisions justified |

---

## Measurement Framework

### Metric 1: Completeness Score (0-100)

```bash
#!/bin/bash
# tests/measures/completeness.sh

measure_completeness() {
    local scenario="$1"
    local expected_file="tests/scenarios/$scenario/expected-artifacts.txt"
    
    # List of expected artifacts for this scenario
    mapfile -t expected < "$expected_file"
    local total=${#expected[@]}
    local found=0
    
    # Check each expected artifact exists
    for artifact in "${expected[@]}"; do
        if [ -f "docs/helix/$artifact" ] || \
           find docs/helix/ -name "*$artifact*" -type f >/dev/null 2>&1; then
            ((found++))
        fi
    done
    
    # Calculate percentage
    echo $(( (found * 100) / total ))
}

# Usage: measure_completeness "A"
```

**Targets by autonomy level**:
- Low: N/A (questions only, artifacts not expected)
- Medium: ≥60% of core artifacts (PRD + key FEATs/USs)
- High: ≥90% of full artifact stack

### Metric 2: Quality Score (0-100)

```bash
#!/bin/bash
# tests/measures/quality.sh

measure_quality() {
    local score=0
    
    # PRD quality checks (if exists)
    if [ -f "docs/helix/01-frame/prd.md" ]; then
        grep -q "## Requirements" docs/helix/01-frame/prd.md && ((score+=25))
        grep -q "## Constraints" docs/helix/01-frame/prd.md && ((score+=25))
    fi
    
    # Cross-reference traceability (minimum 5 refs)
    local ref_count=$(grep -r '\[\[.*\]\]' docs/helix/ 2>/dev/null | wc -l)
    [ $ref_count -ge 5 ] && ((score+=25))
    
    # Acceptance criteria in user stories
    if grep -rq "## Acceptance Criteria" docs/helix/01-frame/user-stories/ 2>/dev/null; then
        ((score+=25))
    fi
    
    echo $score
}
```

**Targets**: ≥75 for medium autonomy, ≥85 for high autonomy

### Metric 3: Decision Correctness (0-100)

```bash
#!/bin/bash
# tests/measures/correctness.sh

measure_correctness() {
    local scenario="$1"
    local score=100
    
    # Load constraints for this scenario
    mapfile -t constraints < "tests/scenarios/$scenario/constraints.txt"
    
    # Check each constraint was respected
    for constraint in "${constraints[@]}"; do
        case "$constraint" in
            *"PostgreSQL"*)
                if ! grep -rq "PostgreSQL\|postgres" docs/helix/02-design/ 2>/dev/null; then
                    ((score-=30))  # Major violation
                fi
                ;;
            *"TypeScript"*|"Rust"*)
                if ! grep -rqE "(TypeScript|Rust)" docs/helix/02-design/ 2>/dev/null; then
                    ((score-=20))  # Language not specified
                fi
                ;;
        esac
    done
    
    # Bonus for documented assumptions
    local assumption_count=$(grep -r "Assumption:" docs/helix/ 2>/dev/null | wc -l)
    [ $assumption_count -gt 0 ] && ((score+=10))
    
    # Cap at 100
    [ $score -gt 100 ] && score=100
    
    echo $score
}
```

**Target**: ≥90 (constraints must be respected)

### Metric 4: Efficiency Score (tokens per artifact)

```bash
#!/bin/bash
# tests/measures/efficiency.sh

measure_efficiency() {
    # Get token usage from last agent run
    local tokens=$(cat ~/.ddx/agent-stats.json 2>/dev/null | jq '.total_tokens' || echo "0")
    
    # Count artifacts created
    local artifact_count=$(find docs/helix/ -name "*.md" -type f 2>/dev/null | wc -l)
    
    [ $artifact_count -eq 0 ] && echo "N/A" && return
    
    echo $(( tokens / artifact_count ))
}
```

**Target**: Track trend, lower is better but not at expense of quality

### Metric 5: Autonomy Behavior Score (Low mode only)

For low autonomy, we measure **question quality**, not artifacts:

```bash
#!/bin/bash
# tests/measures/autonomy-behavior.sh

measure_low_autonomy_behavior() {
    local score=0
    
    # Check agent asked questions before creating major artifacts
    if [ ! -f "docs/helix/01-frame/prd.md" ]; then
        ((score+=50))  # Correctly held off on PRD creation
    fi
    
    # Count clarifying questions in conversation log
    local question_count=$(grep -iE "(should|what|which|how)" ~/.ddx/conversation-log.json 2>/dev/null | wc -l)
    
    if [ $question_count -ge 3 ]; then
        ((score+=50))  # Asked sufficient questions
    fi
    
    echo $score
}
```

**Target**: ≥80 for low autonomy (should ask, not assume)

---

## Test Execution Workflow

### Phase 1: Run Live Agent Tests

```bash
#!/bin/bash
# tests/run-live-test.sh

set -euo pipefail

SCENARIO="${1:-A}"          # A | B | C
AUTONOMY="${2:-medium}"     # low | medium | high  
MODEL="${3:-claude-3.5-sonnet}"  # Model to test
RUNS="${4:-3}"              # Number of runs for statistical significance

# Create isolated test workspace
WORKSPACE="/tmp/helix-test-$SCENARIO-$AUTONOMY-$MODEL-$(date +%s)"
mkdir -p "$WORKSPACE"
cd "$WORKSPACE"

# Initialize minimal HELIX project structure
git init
mkdir -p docs/helix/{01-frame,02-design,03-test}

# Set autonomy configuration
cat > .helix/slider-config.yaml << EOF
autonomy_level: "$AUTONOMY"
speculative_allowed: $([ "$AUTONOMY" = "high" ] && echo "true" || echo "false")
conflict_handling:
  resolvable: "escalate"
  physics_level: "block"
EOF

# Load vision statement for this scenario
VISION=$(cat "/Users/erik/Projects/helix/tests/scenarios/$SCENARIO/vision.md")

echo "=== Running Test ==="
echo "Scenario: $SCENARIO"
echo "Autonomy: $AUTONOMY"  
echo "Model: $MODEL"
echo "Workspace: $WORKSPACE"
echo ""

# Run agent with specified model
export CLAUDE_MODEL="$MODEL"  # Or appropriate env var for model selection

timeout 900 ddx agent run \
    --harness claude \
    --text "$VISION" || {
        echo "ERROR: Agent run failed or timed out"
        exit 1
}

# Capture results
echo ""
echo "=== Measuring Results ==="

# Run all measurements
completeness=$(bash /Users/erik/Projects/helix/tests/measures/completeness.sh "$SCENARIO")
quality=$(bash /Users/erik/Projects/helix/tests/measures/quality.sh)
correctness=$(bash /Users/erik/Projects/helix/tests/measures/correctness.sh "$SCENARIO")

if [ "$AUTONOMY" = "low" ]; then
    autonomy_score=$(bash /Users/erik/Projects/helix/tests/measures/autonomy-behavior.sh)
else
    efficiency=$(bash /Users/erik/Projects/helix/tests/measures/efficiency.sh)
fi

# Output results
echo ""
echo "=== Results ==="
echo "Completeness: $completeness/100"
echo "Quality: $quality/100"
echo "Correctness: $correctness/100"
if [ "$AUTONOMY" != "low" ]; then
    echo "Efficiency: $efficiency tokens/artifact"
else
    echo "Autonomy Behavior: $autonomy_score/100"
fi

# Save results for aggregation
cat > "$WORKSPACE/results.json" << EOF
{
  "scenario": "$SCENARIO",
  "autonomy": "$AUTONOMY",
  "model": "$MODEL",
  "timestamp": "$(date -Iseconds)",
  "metrics": {
    "completeness": $completeness,
    "quality": $quality,
    "correctness": $correctness
  }
}
EOF

# Determine pass/fail based on targets
TARGET_COMPLETENESS=([low]=0 [medium]=60 [high]=90)
if [ "$AUTONOMY" != "low" ]; then
    if [ $completeness -ge ${TARGET_COMPLETENESS[$AUTONOMY]} ] && \
       [ $quality -ge 75 ] && \
       [ $correctness -ge 90 ]; then
        echo ""
        echo "✓ PASS"
        exit 0
    fi
fi

echo ""
echo "✗ FAIL - below targets"
exit 1
```

### Phase 2: Statistical Aggregation (Multiple Runs)

```bash
#!/bin/bash
# tests/aggregate-results.sh

SCENARIO="$1"
AUTONOMY="$2"
MODEL="$3"

# Find all result files for this configuration
results=$(find /tmp -name "helix-test-$SCENARIO-$AUTONOMY-$MODEL-*/results.json" 2>/dev/null)

if [ -z "$results" ]; then
    echo "No results found"
    exit 1
fi

# Parse and aggregate using jq
echo "=== Statistical Summary ==="
echo "Scenario: $SCENARIO, Autonomy: $AUTONOMY, Model: $MODEL"
echo ""

for result in $results; do
    cat "$result"
done | jq -s '
  {
    runs: length,
    completeness: {
      mean: ([.[].metrics.completeness] | add / length),
      min: ([.[].metrics.completeness] | min),
      max: ([.[].metrics.completeness] | max)
    },
    quality: {
      mean: ([.[].metrics.quality] | add / length),
      min: ([.[].metrics.quality] | min),
      max: ([.[].metrics.quality] | max)
    },
    correctness: {
      mean: ([.[].metrics.correctness] | add / length),
      min: ([.[].metrics.correctness] | min),
      max: ([.[].metrics.correctness] | max)
    }
  }
'

echo ""
echo "Recommendation:"
completeness_mean=$(for result in $results; do cat "$result"; done | jq -s '[.[].metrics.completeness] | add / length')
if (( $(echo "$completeness_mean >= 80" | bc -l) )); then
    echo "Model performs well on this scenario/autonomy combination"
else
    echo "Consider prompt refinement or different model selection"
fi
```

### Phase 3: Model Comparison Matrix

```bash
#!/bin/bash
# tests/compare-models.sh

SCENARIO="$1"
AUTONOMY="$2"

echo "=== Model Comparison: Scenario $SCENARIO, Autonomy $AUTONOMY ==="
echo ""

for model in claude-3.5-sonnet claude-3.7-sonnet gpt-4o-codex; do
    results=$(find /tmp -name "helix-test-$SCENARIO-$AUTONOMY-$model-*/results.json" 2>/dev/null | head -1)
    
    if [ -n "$results" ]; then
        completeness=$(cat "$results" | jq '.metrics.completeness')
        quality=$(cat "$results" | jq '.metrics.quality')
        correctness=$(cat "$results" | jq '.metrics.correctness')
        
        echo "$model: C=$completeness Q=$quality Cr=$correctness"
    else
        echo "$model: No results yet"
    fi
done
```

---

## Test Matrix

Run this matrix to establish baseline performance across models and autonomy levels:

| Scenario | Autonomy | Models to Test | Runs Each |
|----------|----------|----------------|-----------|
| A (Simple) | Low | claude-3.5, gpt-4o-codex | 2 |
| A (Simple) | Medium | All models | 3 |
| A (Simple) | High | All models | 3 |
| B (Medium) | Low | claude-3.5 | 2 |
| B (Medium) | Medium | All models | 3 |
| B (Medium) | High | All models | 3 |
| C (Complex) | Medium | claude-3.7, gpt-5.2-codex | 2 |
| C (Complex) | High | claude-3.7, gpt-5.2-codex | 2 |

**Total**: ~40 agent runs to establish comprehensive baseline

---

## Success Criteria for Merge

Before merging slider autonomy feature:

### Minimum Requirements
1. **Scenario A passes at all autonomy levels** with claude-3.5-sonnet (completeness ≥90%, quality ≥80, correctness ≥95)
2. **Scenario B passes at medium/high autonomy** with claude-3.5-sonnet (completeness ≥75%, quality ≥75, correctness ≥90)
3. **Low autonomy correctly asks questions** without creating major artifacts (autonomy behavior score ≥80)

### Model Selection Guidance
After testing, document which models work best for each scenario:

```markdown
## Recommended Models by Scenario

| Scenario | Autonomy | Best Model | Notes |
|----------|----------|------------|-------|
| A | Any | claude-3.5-sonnet | Balanced performance/cost |
| B | Medium/High | claude-3.7-sonnet | Better at complex reasoning |
| C | High | gpt-5.2-codex | Superior technical design generation |
```

### Cost Considerations
Track token usage to inform cost decisions:

```bash
# After all tests complete
find /tmp -name "results.json" -exec cat {} \; | jq -s '
  group_by(.model) | 
  map({
    model: .[0].model,
    total_tokens: (map(.metrics.tokens // 0) | add),
    avg_per_run: ((map(.metrics.tokens // 0) | add) / length)
  })
'
```

---

## Iterative Improvement Loop

```bash
#!/bin/bash
# tests/improve-prompts.sh

SCENARIO="$1"
AUTONOMY="$2"

echo "=== Prompt Improvement Loop ==="
echo ""

while true; do
    # Run test
    bash /Users/erik/Projects/helix/tests/run-live-test.sh "$SCENARIO" "$AUTONOMY" claude-3.5-sonnet
    
    results=$?
    
    if [ $results -eq 0 ]; then
        echo ""
        echo "✓ Test passed - prompts are working well"
        break
    fi
    
    echo ""
    echo "Test failed. Analyzing gaps..."
    
    # Identify which metrics failed
    completeness=$(bash /Users/erik/Projects/helix/tests/measures/completeness.sh "$SCENARIO")
    quality=$(bash /Users/erik/Projects/helix/tests/measures/quality.sh)
    
    if [ $completeness -lt 60 ]; then
        echo "Issue: Low completeness - agent not creating expected artifacts"
        echo "Fix: Review helix-frame or helix-design prompts for clarity"
    fi
    
    if [ $quality -lt 75 ]; then
        echo "Issue: Low quality - artifacts missing required sections"
        echo "Fix: Add explicit section requirements to skill prompts"
    fi
    
    echo ""
    read -p "Edit prompts and re-run? (y/n): " choice
    [ "$choice" != "y" ] && exit 1
    
    # Open relevant prompt files for editing
    nvim .agents/skills/helix-frame/SKILL.md .agents/skills/helix-design/SKILL.md
done
```

---

## Next Steps

1. **Create scenario fixtures**: Write vision statements and expected artifacts for A, B, C
2. **Run baseline tests**: Execute test matrix with current HELIX prompts
3. **Measure gaps**: Identify which metrics fail most often
4. **Refine prompts**: Update skill prompts based on failure patterns
5. **Re-test**: Verify improvements with fresh runs
6. **Document model recommendations**: Based on comparative results

This harness tests **real agent performance** with measurable, repeatable criteria. Model selection becomes data-driven rather than guesswork.
