# C007 — "Let's create a website"; empty workspace (guided, exploratory)

**Category:** conversation library (plan §1.5 row C007)
**Phase:** P5b
**Tier:** exploratory

## Scenario

Workspace state:
- Empty repository. No `.helix.yml`, no docs/, no prior artifacts.

Operator says: "Let's create a website for the coffee shop."

## Expected behaviour

Per plan §1.5 and §5.1: helix-web's SKILL.md description claims the
verbs "website, page-spec, IA, design system." The verb "create a
website" routes to helix-web (not helix-product, not helix-infra).

Under `autonomy=guided` the skill MUST:

1. Engage as helix-web (description anchor on "website").
2. Surface the marker addition: "add helix-web to .helix.yml".
3. Offer to draft the first helix-web artifact (page-spec OR
   information-architecture / IA).
4. ASK before the first state-changing tool_use (marker write OR
   artifact draft).

## Why exploratory

helix-web doesn't exist yet at full fidelity in v1 (per plan §6.9 it's
a P5b/P6 scaffold). The row probes the description-router boundary
("website" → helix-web, NOT helix-product). Until helix-web ships with
its full SKILL.md description, the discrimination is approximate — the
verb claim drives engagement but the cascade to page-spec is not yet
hard-wired. Marked exploratory per plan §5 row C007.

## Negative control

Plugin removed (`plugins_remove: [methodology-web]`). Without
helix-web's SKILL.md description carrying the "website" verb, the
agent will not surface helix-web as the methodology to add and the
helix-web-naming matcher cannot fire.
