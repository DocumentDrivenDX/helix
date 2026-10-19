# Activity 04: Build

The execution activity where we implement and refine governing intent with continuous verification.

## Purpose

Build implements authorized behavior across affected producers and consumers. Use execution feedback to improve cohesion, remove unnecessary operations and consolidate overlapping mechanisms. Existing tests can verify a mechanical change; new behavior or a regression may need additional proof.

## Key Principle

**Refine Through Execution**: Preserve required outcomes while simplifying the system and its verification. Use Red-Green-Refactor where a failing test supplies missing evidence; do not manufacture failing tests for every edit.

## Input Gate

Before starting Build activity, verify Test activity outputs:
- [ ] All test suites written and reviewed
- [ ] Existing coverage and any missing behavioral evidence are understood
- [ ] Coverage plan identifies scoped requirements and meaningful tests
- [ ] CI/CD pipeline configured for tests
- [ ] Test procedures documented
- [ ] Test infrastructure operational
- [ ] Applicable security verification is planned using existing or new tests
- [ ] SAST/DAST tools configured in CI/CD pipeline
- [ ] Security coding standards established

## Artifacts

### 1. Implementation Plan
**Location**: `artifacts/implementation-plan/`
**Output**: `docs/helix/04-build/implementation-plan.md`

Technical execution strategy:
- **Build Activities**: Incremental delivery approach
- **Component Order**: What to build first
- **Technology Setup**: Development environment
- **Coding Standards**: Conventions and patterns
- **Integration Points**: How components connect
- **Resource Planning**: Team assignments and timeline
- **Execution Strategy**: Plan-driven completion with optional independently scheduled work

`secure-coding` remains retired as a standalone HELIX artifact. Its useful
responsibility is already covered by the current build contract:

- `docs/helix/01-frame/security-requirements.md` defines the security obligations
- `docs/helix/01-frame/threat-model.md` and `docs/helix/02-design/security-architecture.md` define the design-level controls
- `docs/helix/03-test/security-tests.md` and build-activity security scans verify the implementation
- project concerns can add stack-specific practices without promoting a generic checklist into the core workflow

Reintroducing `secure-coding` as its own artifact would recreate the same thin,
duplicative checklist that HELIX already retired.

### Plan-Driven Execution

The implementation plan governs scope, ordering, acceptance evidence, and exit
criteria. After explicit implementation authorization, the runtime executes its
steps through verified completion, continuing ordinary debugging within scope.
Use compact continuation evidence alongside the plan for interruption recovery.
A step boundary does not require another user prompt or a separate work item.

Use work items only when explicitly selected by the user or required by the
active execution contract. Prefer one item for a coherent goal; split for
independent ownership, scheduling, parallel execution, or deferred work.
The selected runtime retains its claim, audit, and closure requirements.
See `workflows/references/work-item-first.md` for the shared contract.

## Core Workflow

### Implementation and Feedback

Trace the requested outcome through the existing interfaces and operations.
Reuse meaningful coverage and add tests for distinct gaps. Implement in coherent
increments, using Red-Green-Refactor where useful, then run applicable checks.
Simplify code and tests as evidence clarifies the design; refactoring need not
wait until every implementation step is complete.

Prefer changing an existing operation and updating its callers over adding an
overlapping API merely to keep the diff small. Respect actual compatibility
commitments. Inspect generated work and measured costs where they bear on the
change; passing tests do not justify redundant queries, caches or checks.

## Human vs AI Responsibilities

### Human Responsibilities
- **Code Review**: Ensure quality and maintainability
- **Architectural Integrity**: Maintain design decisions
- **Problem Solving**: Handle unexpected challenges
- **Performance Optimization**: Profile and optimize
- **Security Review**: Validate security practices

### AI Assistant Responsibilities
- **Code Generation**: Write code to pass tests
- **Test Implementation**: Create test files from specifications
- **Refactoring**: Improve code structure
- **Documentation**: Use descriptive names and concise language-native API documentation; retain comments for non-obvious rationale
- **Pattern Application**: Apply consistent coding patterns

## Build Activities

### Activity 1: Foundation

Establish governing behavior, relevant existing coverage and any missing proof.
Reuse the project's test infrastructure. A new failing test may establish a
regression or new behavior; an already passing suite can support refactoring.

### Activity 2: Core Build

Implement the bounded outcome across affected components. Integrate continuously
and verify behavior with appropriate tests. Remove superseded paths rather than
preserving them solely to avoid changing callers or tests.

### Activity 3: Quality (Refactor)

Consolidate overlapping responsibilities, remove redundant operations and assess
relevant measured costs. Revise or retire redundant and implementation-coupled
tests while retaining meaningful proof. Run applicable project checks and the
verification concern's observed-result contract before claiming completion.

## Quality Standards

### Code Quality Checklist
- [ ] **Single Responsibility**: Each function/class has one job
- [ ] **DRY**: No duplicated logic
- [ ] **YAGNI**: No speculative features
- [ ] **Readable**: Code explains itself
- [ ] **Testable**: Easy to test in isolation

### Test Quality Standards
- [ ] **Fast**: Tests run quickly
- [ ] **Independent**: Tests don't depend on each other
- [ ] **Repeatable**: Same result every time
- [ ] **Self-Validating**: Clear pass/fail
- [ ] **Timely**: Written before code

## Common Patterns

### Pattern: Contract Test First
```bash
# 1. Create contract test
test/contracts/cli_test.go

# 2. Run test - see it fail
make test  # FAIL: CLI not found

# 3. Create minimal implementation
cmd/cli.go

# 4. Run test - see it pass
make test  # PASS

# 5. Refactor if needed
# Improve structure while tests stay green
```

### Pattern: Integration Test Flow
```bash
# 1. Create integration test
test/integration/workflow_test.go

# 2. Test fails - components don't exist
make test  # FAIL: Components not found

# 3. Build components incrementally
internal/component1/
internal/component2/

# 4. Connect components
internal/workflow/

# 5. Test passes
make test  # PASS
```

## Build Guidelines

### Do's ✅
- Inspect existing implementation and coverage before adding mechanisms
- Use failing tests to establish missing behavior where useful
- Propagate required changes across affected callers
- Consolidate code and tests while preserving required outcomes
- Commit coherent verified changes

### Don'ts ❌
- Add parallel APIs merely to reduce edited lines
- Preserve redundant mechanisms because their private-detail tests expect them
- Weaken required assertions or suppress failures to force green
- Add unrelated features or cleanup

## Incremental Delivery

### Progress Tracking

Track verified outcomes, resolved risks and remaining work in the existing plan.
Test counts and growing coverage percentages alone do not establish progress.
Simplification may reduce code and test volume while preserving required proof.


### Continuous Integration
Every commit should:
1. Pass all existing tests
2. Not break previous functionality
3. Use sufficient existing or new behavioral coverage
4. Update documentation
5. Pass linting and formatting

## Common Pitfalls

### ❌ Avoid These Mistakes

1. **Writing Code Without Tests**
   - Bad: "I'll add tests later"
   - Good: Identify existing coverage; add a failing regression test for missing proof

2. **Big Bang Integration**
   - Bad: Build everything then integrate
   - Good: Integrate continuously as you build

3. **Over-Engineering**
   - Bad: Adding features "just in case"
   - Good: Clear responsibilities and no unnecessary mechanisms

4. **Test After Development**
   - Bad: Code complete, now writing tests
   - Good: Plan appropriate verification before implementing; reuse coverage where sufficient

5. **Ignoring Refactor Step**
   - Bad: Moving to next feature immediately
   - Good: Clean up before moving on

## Success Criteria

The Build activity is complete when:

1. **All Tests Pass**: 100% of specified tests green
2. **Coverage Met**: Governing behavior and critical paths verified under project targets
3. **Performance Verified**: Meets requirements under load
4. **Security Validated**: Passes security scans
5. **Documentation Complete**: Code and API documented
6. **Code Review Done**: Approved by team

## Next Activity: Deploy

Once Build is complete, proceed to Deploy activity for:
- Production deployment
- Environment configuration
- Release management
- Monitoring setup
- Go-live activities

Remember: Build creates the "what" - Deploy makes it available to users.

## Tools and Commands

### Development Workflow
```bash
# Run tests continuously
make watch-test

# Run specific test
make test TEST=TestContractCLI

# Check coverage
make coverage

# Run linting
make lint

# Format code
make fmt
```

### TDD Rhythm
```bash
# 1. RED: Write failing test
echo "test_cli_accepts_input()" > test_cli.py
pytest  # FAIL

# 2. GREEN: Make it pass
echo "def accept_input(): pass" > cli.py
pytest  # PASS

# 3. REFACTOR: Improve
# Refactor cli.py while keeping tests green
pytest  # STILL PASS
```

## Build Artifacts

By the end of Build activity, you should have:

1. **Source Code**: All production code
2. **Test Suite**: Meaningful coverage of governing behavior
3. **Documentation**: Relevant API documentation and README updates; comments only where they clarify non-obvious intent
4. **Build Scripts**: Compilation and packaging
5. **CI/CD Config**: Automated testing pipeline
6. **Deployment Package**: Ready for deployment

## Tips for Success

1. **Small Steps**: One test, one feature at a time
2. **Coherent Commits**: Commit verified changes with their affected tests
3. **Pair Programming**: Two eyes catch more issues
4. **Continuous Integration**: Test on every push
5. **Refactor Courageously**: Tests are your safety net

## Using AI Assistance

Build execution belongs to the runtime (see the Runtime Integration
Appendix below). Use the activity artifacts under
`activities/04-build/artifacts/` when you need supporting build documentation or
work-item guidance.

Common entry points:
- `artifacts/implementation-plan/`

AI is useful for implementation drafting and focused refactoring. Human review
must verify design fidelity, test intent, and security-sensitive changes.

## Runtime Integration Appendix

Build execution belongs to the runtime. An authorized implementation-ready
plan is its default input; an explicitly selected tracker may instead govern
claims, live status, and execution history. Do not discover tracker binaries
or consult optional adapter guides without selecting that adapter.

---

*"The only way to go fast is to go well." - Robert C. Martin*

*Build activity is where disciplined engineering practices pay off. Trust the process.*
