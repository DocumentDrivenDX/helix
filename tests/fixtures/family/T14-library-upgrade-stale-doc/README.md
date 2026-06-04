# T14 — library upgrade adds required_section against stale doc [HIGH RISK]

- **Installed:** `helix-library`, `helix`
- **Risk:** high (transitional-state contract)

## Scenario

The library has been upgraded from v1.0.0 to v1.1.0 between sessions.
v1.1.0 adds `Success Metrics` as a required section for `library:prd`.
A pre-existing PRD on disk is stamped `library_type_version: 1.0.0` and
predates the new required section.

The upgraded shape is simulated via `workspace/library-overlay/types/prd.yml`
which the runner mounts to shadow the installed library's spec at
validation time.

## Why it matters

Monorepo lockstep does NOT eliminate user-facing transitional state. A
user upgrades the plugin between Claude sessions. T1-T13 only test steady
states. Without this fixture the contract is silent — two implementations
could diverge silently on whether stale docs are flagged or accepted.

## Pass signature (contract A: warn-on-stale, enforce-on-new)

- Prompt 1 (validate stale): validator exits 0 AND stderr surfaces a
  drift/migration hint naming the missing section ("Success Metrics") or
  the old library_type_version.
- Prompt 2 (author new): the Write tool_use produces a new PRD whose
  frontmatter declares `library_type_version: 1.1.0` AND the body
  contains a `## Success Metrics` heading.

## Failure signatures

- Validator fails the stale doc (exit non-zero) → contract B chosen;
  this fixture's contract is contract A. If the family decides to
  commit to contract B instead, flip `expect_exit_nonzero: true` and
  document it here.
- New PRD authored without Success Metrics → upgrade is not enforced
  on new authoring. Quiet drift.
- Validator silently accepts the stale doc without ANY hint → user
  has no signal an upgrade happened.
