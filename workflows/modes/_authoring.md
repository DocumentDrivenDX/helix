# Authoring

Load this contract when a mode creates or edits an artifact instance.
Use the active voice profile and shared writing guidance when they apply.
Tracker work and gates follow `workflows/references/work-item-first.md`;
report shape follows `workflows/modes/_report.md`.

## Work on material gaps

Apply `workflows/principles.md` §Living documents and material gaps.

## Consult relevant authority

Read the target and the governing artifacts that can affect the requested
change. Use the bound graph to find relevant content; do not traverse unrelated
branches. If upstream content is missing, identify the material uncertainty it
leaves. Use existing intent and the authority hierarchy when sufficient; block
only an affected action that requires an unresolved decision or evidence.

When creating an artifact, add only supported `ddx.links` relationships. Do not
invent links or mechanically copy every graph edge. For an existing artifact,
preserve its frontmatter, operator-added content, and unknown keys.

## Factual authority

Templates, examples and rubrics supply document shape and quality criteria;
they are not evidence about the project. Names, ownership, acronym expansions,
priorities, dates and behavioral requirements must come from the operator or
relevant governing sources. Keep unsupported proposals visibly identified as
assumptions/open decisions at the permitted autonomy level; never propagate
an example's facts as established authority. Higher autonomy changes when to
ask, not what counts as evidence.

An alignment, refresh or wording pass preserves established meaning unless a
semantic change is authorized. Distinguish factual/behavioral changes from
mechanical cleanup in the reviewable diff and closeout. Do not remove a real
deadline as status prose, or add a contract field while calling the pass
cosmetic. Review repeated edits against their governing source before spreading
a new fact across artifacts; correct unsupported propagation without replacing
it with another guess.

## External standards

Define unfamiliar standards and acronyms on first use. When an artifact adopts
a standard's exact vocabulary or identifiers, verify them against its published
source and identify the source and release. Link an available project resource
summary where useful; a missing summary does not block authoring.

## External-tool artifacts

For `authoring.home: external-tool`, follow `skills/helix/SKILL.md` §8
(Externally authored artifacts). Never edit the body to change its content;
route edits to `authoring.origin`.
