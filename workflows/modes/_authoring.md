# Authoring

Load this contract when a mode creates or edits an artifact instance.
Use the active voice profile and shared writing guidance when they apply.

## Consult relevant authority

Read the target and the governing artifacts that can affect the requested
change. Use the bound graph to identify required prerequisites and meaningful
relationships; do not traverse unrelated branches. If a required prerequisite
is missing, follow the active autonomy contract or the user's direction before
proceeding. A non-required relationship may inform the work when relevant, but
does not block it.

When creating an artifact, add only supported `ddx.links` relationships. Do not
invent links or mechanically copy every graph edge. For an existing artifact,
preserve its frontmatter, operator-added content, and unknown keys.

## External standards

Define unfamiliar standards and acronyms on first use. When an artifact adopts
a standard's exact vocabulary or identifiers, verify them against its published
source and identify the source and release. Link an available project resource
summary where useful; a missing summary does not block authoring.

## External-tool artifacts

For `authoring.home: external-tool`, read through the configured connector when
available; otherwise use the checked-in body. Do not edit the copy to change
content. Route edits to `authoring.origin`. Treat `state: checked-out` as stale.
For `checked-in`, a mismatched export digest means the body is stale; a missing
digest means freshness is unknown. If the runtime cannot produce a faithful
check-in, leave the state unchanged and explain the limitation.
