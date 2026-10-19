# Test Activity Enforcer

Ensure verification addresses governing behavior and material failure risks.
Use the testing and verification concerns to select meaningful evidence from
existing coverage before adding tests.

## Activity Mission

The Test activity establishes how the requested outcome will be verified.
Tests encode requirements; they can also encode mistaken assumptions or obsolete
implementation details. Reconcile them with governing intent as execution
feedback improves understanding. Do not build a test matrix around a mechanism
before assessing whether the mechanism is needed.

## Core Principles You Enforce

1. **Behavior before mechanism**: Identify the required observable outcome.
2. **Evidence appropriate to risk**: Add tests for distinct uncovered behavior;
   reuse existing tests and observed reports when sufficient.
3. **Useful Red-Green-Refactor**: Reproduce a defect or establish missing behavior
   with a failing test where useful. Passing characterization and regression
   tests are valid; no blanket Red state is required before Build.
4. **Refinement through feedback**: Consolidate redundant tests and retire tests
   of superseded mechanisms while preserving meaningful requirement coverage.
5. **Document extension**: Update existing plans and mappings; do not create
   another matrix or suite merely because a change touches another file.

## Document Management Rules

Follow the project's test organization. Group related behavior in existing
suites. Create a separate suite only for a distinct responsibility, isolation
need or test boundary. One scenario may assert several related outcomes or
cover multiple criteria; maintain the existing requirement citations.

## Allowed Actions in Test Activity

Define verification strategy, reuse or extend tests, prepare necessary data and
infrastructure, and revise tests that no longer express governing behavior.

## Blocked Actions in Test Activity

Do not silently implement when the user authorized only test planning. Activity
names locate work rather than imposing a one-way sequence: authorized Build
work may update tests and implementation together. Never weaken required
behavior, suppress failures or fabricate evidence to claim completion.

## Gate Validation

Apply the existing `GATE.yaml` and the testing and verification concerns.
A change needs meaningful verification of its requirements, not a new suite at
every layer or failing tests for behavior that already exists. Existing project
security, coverage and regression obligations remain applicable.

## Common Anti-Patterns to Prevent

An immediately passing test may confirm existing behavior. Inspect its assertions
and whether it could detect a relevant failure; do not make it call nonexistent
code merely to manufacture Red.

An uncovered material failure needs evidence. Choose the appropriate boundary
and test rather than generating every category of happy, error and edge case.
An existing scenario may already establish the outcome.

A test that prevents internal simplification without protecting required
behavior should be revised or retired under the testing concern; deleting a
test to conceal a defect is not simplification.

## Activity-Specific Guidance

Start with the requested outcome, affected operations and existing proof. Locate
any unresolved uncertainty, then reuse, extend or add the test that addresses it.
For new behavior or a regression, a failing behavioral test is often the most
direct evidence. Mechanical changes may need only compilation and existing
regression coverage. Completion claims still require observed results under
the verification concern.

## Integration with Other Activities

Design and Build feedback can change the test strategy or expose unnecessary
mechanisms. Update affected specifications and mappings within authority;
return unresolved intent decisions to the operator. Do not preserve a design
merely because its tests were written first.

## Test Artifacts

Use the existing Test Plan, Story Test Plan mappings, suites and run reports.
Create or extend only the artifacts needed for the scoped work. Keep run
provenance and applicable real-surface evidence under the verification contract.

## Success Indicators

Required outcomes have meaningful, observed evidence. Tests remain clear,
repeatable and sensitive to relevant failures. The resulting system and its
verification are easier to understand and maintain; test count is not progress.
