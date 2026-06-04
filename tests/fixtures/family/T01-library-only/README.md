# T1 — library only

## Scenario

Only `helix-library` is installed. No methodology plugin is mounted.

## Why it matters

The library is a **data plugin**. By itself it does not own a
methodology skill and must not silently route methodology work. This
fixture proves the library is inert without a consumer methodology.

## What passes

The agent either (a) describes the library types as a catalog without
committing to a methodology, or (b) states plainly that no methodology
skill is active. Either is fine; the assertion is on absence of
methodology routing, not on a specific catalog listing.

## What fails

The agent picks a methodology unprompted (e.g. starts a HELIX
discover-phase walk) — that would mean a stray skill mounted from the
library tree.

## Risk

Low. Mostly a sanity check that data plugins don't accidentally route.
