# HELIX Action: Write Story Tests

Reuse or extend tests for the story's governing behavior. Add failing tests where they establish missing behavior or reproduce a regression; do not generate another suite when existing assertions suffice.

## Prerequisites

- [ ] User story with clear acceptance criteria
- [ ] Design specifications available
- [ ] Test environment and frameworks configured

## Action Workflow

### 1. Analyze Story

For each acceptance criterion, identify:
- Specific behavior, inputs, and expected outputs
- Edge cases and error conditions
- Test level (unit, integration, contract, E2E)
- Test data and mock requirements

### 2. Write Tests

Structure tests by acceptance criterion:

```javascript
describe('User Story: [Story Title]', () => {
  describe('AC1: [Description]', () => {
    it('should [expected behavior] when [condition]', () => {
      // Arrange -> Act (will fail) -> Assert
    });
    it('should handle [edge case]', () => { /* ... */ });
    it('should [error handling] when [error condition]', () => { /* ... */ });
  });
});
```

### 3. Validate

- Existing passing tests are reused; new tests detect the intended missing behavior or failure
- Each acceptance criterion has corresponding tests
- Tests are independent and can run in isolation

## Outputs

- `tests/unit/[story-id]/` - Unit tests
- `tests/integration/[story-id]/` - Integration tests
- `tests/contract/[story-id]/` - Contract tests
- `tests/e2e/[story-id]/` - E2E tests
- `tests/data/[story-id]/` - Test data specifications

## Test Pyramid

Choose unit, integration or E2E coverage according to the behavior and failure
risk. Use existing suites and avoid duplicating the same evidence across layers;
fixed percentages do not determine the appropriate strategy.

## Quality Gates

- [ ] All acceptance criteria have corresponding tests
- [ ] Edge cases and error conditions covered
- [ ] Tests are independent and repeatable
- [ ] Tests detect meaningful failures without depending on private implementation steps
- [ ] Test coverage meets project standards
