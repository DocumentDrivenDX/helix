# Authoring

Load this contract when a mode creates or edits an artifact instance.
Use the active voice profile and shared writing guidance when they apply.
Tracker work and gates follow `workflows/references/work-item-first.md`;
report shape follows `workflows/modes/_report.md`.

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

For `authoring.home: external-tool`, follow `skills/helix/SKILL.md` §8
(Externally authored artifacts). Never edit the body to change its content;
route edits to `authoring.origin`.
