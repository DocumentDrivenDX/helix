# Scenario A Workflow Expectations

## Starting Input Form

### Sparse input
```text
Build a CLI tool that converts temperatures between Celsius, Fahrenheit, and Kelvin. Should support batch conversion from files and have a clean API.
```

### Typical bounded beads
- core conversion implementation
- batch file processing
- help / documentation completion
- conversion test coverage

This scenario is the **mergeable baseline**. It should be simple enough to separate autonomy behavior from domain ambiguity.

## Expected Graph / Artifact Changes

Minimum planning artifacts are listed in `expected-artifacts.txt`.

Expected shape:
- PRD describing CLI scope and constraints
- feature split between core conversion and batch processing
- user stories for CLI interaction and file processing
- technical designs for CLI API and file handling
- bounded implementation beads linked to those artifacts

## Expected Required Validations

Required validations should confirm:
- unit-tested temperature conversion correctness
- batch file processing behavior
- CLI help / usage output exists
- artifact traceability remains intact for produced work

## Expected Ratchets / Observations

Scenario A should primarily use **observational** runtime metrics:
- tokens
- elapsed duration
- cost
- harness / model

If a ratchet is applied here, it should be conservative and easy to satisfy. Scenario A is not intended to be preserve-only by default.

## Autonomy-Level Expectations

### Low
- ask before first graph step
- ask before creating each downstream artifact
- do not dispatch DDx work before explicit approval

### Medium
- proceed through obvious planning steps without asking at every step
- ask only if a meaningful ambiguity appears, such as whether to choose TypeScript or Rust
- once a bounded bead is ready, DDx dispatch is reasonable

### High
- select a reasonable default when the language choice is still open, but record the assumption
- continue through the planning stack without waiting on routine choices
- DDx dispatch should normally be merge-eligible if required validations pass

## Mergeable vs Preserve-Only Expectations

### Mergeable path
This scenario should usually be **merge-eligible** when:
- required validations pass
- constraints are respected
- artifacts are complete enough for the bounded bead

### Preserve-only path
A preserve outcome is acceptable only when caused by:
- failed required validations
- a ratchet regression
- a prompt/workflow mistake that reduced completeness or correctness

Preserve is **not** the default expectation for Scenario A.
