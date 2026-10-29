# UX Builder marketplace integration plan

## Scope and authority

The operator authorized packaging UX Builder and listing it in HELIX on
2026-10-29. HELIX's FEAT-004 governs plugin packaging; its
`packaged-design-system` concern governs project adoption. The UX Builder PR owns
its implementation and release. This change only adds distribution and guidance.

## Technical approach and boundaries

Add one independently versioned `ux-builder` entry to the existing shared
marketplace. Use the published Claude/Codex Git-subdirectory source shape and pin
a tested full Git commit SHA. Keep the marketplace name `helix` and existing
HELIX install identity. No source vendoring, submodule or npm runtime dependency
is added to HELIX. Its single public routing skill stays unchanged.

Exact host formats are owned by the published
[Claude marketplace reference](https://code.claude.com/docs/en/plugins/marketplace-reference)
and [Codex packaging documentation](https://developers.openai.com/plugins/build/plugins).
No new custom schema or product domain model is introduced. The validator checks
this repository's chosen Git-source policy, not every format either host supports.

The marketplace validator owns entry identity/source integrity. Existing install
validation owns HELIX manifest/version consistency and resolves its entry by name.
Neither imports UX Builder runtime code or connects to npm. UX Builder's plugin
runner uses the consumer project's dependencies and its installed documentation.

## Implementation sequence

1. Complete/test ux-builder packaging and create its PR.
2. Add the pinned listing, independent of HELIX version/release logic.
3. Replace both positional lookups in install validation with name lookup.
4. Add tests for entry reordering, missing/duplicate names, missing/invalid pins,
   and path escape. Wire these into the existing install-consistency gate.
5. Document installation, runtime prerequisites, explicit project adoption,
   skill-source coexistence and release ordering. Open a dependent draft PR.

## Validation

Run `just test-install-consistency`, `just test`, `claude plugin validate .`, and
`git diff --check`. Use a clean/isolated host configuration to install the actual
Git source and verify discovery. Runtime UX behavior remains covered by the
upstream plugin and SDK suites. Never claim live workflow execution from manifest
validation alone.

## Security and rollback

The listing adds no hook or automatic npm install. Full Git pins prevent silent
source movement. No credentials or consumer state are changed by validation.
Adoption is a project decision recorded through `packaged-design-system`.
Revert/remove the listing to roll back distribution; consumer documents remain.

## Execution and continuation

The user authorized both PRs; no tracker mutations or release publication is
included. No token/spending limit was specified and runtime metering is unavailable.
Initial listing uses the tested packaging PR commit. Keep it draft until that
change is merged/released, update to the release revision, and verify actual
marketplace installation before making it ready. Final PR text records exact
check results and its upstream dependency.
