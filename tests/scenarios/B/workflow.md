# Scenario B Workflow Expectations

## Starting Input Form

### Sparse input
```text
Build a REST API for managing user profiles with OAuth authentication. Needs to scale to 10k users initially.
```

### Typical bounded beads
- user-profile CRUD API implementation
- OAuth login flow implementation
- rate limiting and operational envelope
- PostgreSQL-backed persistence design / implementation

This scenario is the **resolvable-ambiguity** case. It should exercise medium/high autonomy behavior around operational choices without introducing a true contradiction.

## Expected Graph / Artifact Changes

Minimum planning artifacts are listed in `expected-artifacts.txt`.

Expected shape:
- PRD capturing scale and deployment constraints
- feature split between profile management, OAuth auth, and rate limiting
- user stories for CRUD behavior and login flow
- ADRs for database and auth-provider decisions
- architecture guidance for Docker deployment and service shape
- bounded implementation beads for API, auth, and rate limiting work

## Expected Required Validations

Required validations should confirm:
- PostgreSQL remains the selected persistence layer
- OAuth2 / OIDC constraints are respected
- profile API behavior is covered by tests or equivalent required checks
- rate-limiting behavior is verified
- Docker/deployment assumptions are not silently dropped

## Expected Ratchets / Observations

Expected observations:
- runtime metrics: tokens, duration, cost, harness, model
- auth / security evidence
- rate-limit or throughput-related observations where available

If ratchets are defined, likely candidates are:
- required auth-flow correctness
- no regression against API / auth contract expectations

## Autonomy-Level Expectations

### Low
- ask before each graph step
- ask before creating ADRs or downstream artifacts
- ask before selecting the initial OAuth provider or concrete rate-limit defaults
- no DDx dispatch before approval

### Medium
- proceed through deterministic artifact creation
- ask on meaningful ambiguity such as provider choice, default rate limits, or framework choice
- do not classify these choices as physics-level conflicts

### High
- continue through resolvable ambiguity
- create escalation beads for unresolved but non-blocking choices when traceability is needed
- dispatch bounded work to DDx once a bead is ready

## Mergeable vs Preserve-Only Expectations

### Mergeable path
A mergeable path exists when:
- PostgreSQL is respected
- OAuth2 / OIDC is respected
- required validations pass
- open operational choices are either resolved or captured as non-blocking escalations

### Preserve-only path
Preserve is expected when:
- required auth or rate-limit validations fail
- the attempt violates PostgreSQL / OAuth constraints
- runtime evidence shows a failed required execution or ratchet regression

A DDx preserve result here should return control to HELIX for escalation, follow-up beads, or user input. It is not automatically a physics-level conflict.
