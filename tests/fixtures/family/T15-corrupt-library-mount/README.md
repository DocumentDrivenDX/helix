# T15 — corrupt/half-mounted library [HIGH RISK]

- **Installed:** `helix-library:corrupt` (overlay points at the
  truncated tree at `workspace/library-corrupt/`), `helix`
- **Risk:** high (failure-mode distinguishability)

## Scenario

`workspace/library-corrupt/types/prd.yml` is truncated mid-document
(simulates network-interrupted install, EROFS, or a symlink target
gone). The runner mounts this tree as the library and the agent is
asked to author a PRD.

## Why it matters

T2 covers "library NOT installed." This fixture covers
"library mounted but unreadable/partial" — a real failure mode that
T1-T14 do not catch. The methodology must produce a diagnostic
DISTINCT from the setup-gap (so users can tell `never installed` from
`broken install`) and must NOT fall back to improvising the template.

## Pass signature

- NO Write/Edit tool_use against any PRD file (no template
  improvisation).
- Prose names the corruption distinctly: `corrupt`, `truncated`,
  `malformed`, `unreadable`, `invalid`, `parse error`, `broken`, or
  `partially installed/mounted` in proximity to library/prd.yml/spec.
- Prose does NOT use the setup-gap phrase (`helix-library not
  installed`) — that diagnostic is reserved for T2's scenario.

## Failure signatures

- Setup-gap phrase fires → diagnostic conflates two distinct failure
  modes; users cannot tell broken install from never installed.
- Template improvised → silent recovery; user thinks the PRD is real
  when its schema source is broken.
- Generic "I couldn't complete this" with no corruption signal →
  unactionable; user has no path to repair.
