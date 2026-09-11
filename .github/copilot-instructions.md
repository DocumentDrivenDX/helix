# Copilot Instructions

This repository hosts HELIX: a software development methodology, an
artifact-type catalog, and one routing skill. Copilot users get HELIX
through that `helix` skill, not through this file. This file is a pointer,
not a copy of the skill.

## Read the skill first

Copilot has no skill tool, so before answering any request that touches
HELIX work (aligning, framing, designing, evolving, reviewing, or placing
content), read `skills/helix/SKILL.md` in full and follow it. The skill
routes the request to a mode; each mode's contract lives in
`workflows/modes/<mode>.md` and the skill says when to load it. Templates,
prompts, and quality criteria live under `workflows/activities/`. Do not
paraphrase the skill from memory and do not keep a summary of it here.

## Copilot-specific rules

- Chat-only surfaces (IDE chat, github.com chat) have no working
  directory. When a mode needs the project tree (refresh and similar batch
  operations), ask for or use an explicitly named project root; do not
  guess one.
- The routing skill is the only public HELIX entry point. Do not propose
  new `helix-*` skills, slash commands, or CLI verbs; refine a route inside
  `skills/helix/SKILL.md` instead.
- Keep the skill body and the catalog runtime-neutral. Do not add
  Copilot-specific commands or glue to `skills/` or `workflows/`.

## See also

- `docs/install/README.md`, section "GitHub Copilot": how adopter repos
  vendor the skill and commit this file.
- `docs/helix/00-discover/product-vision.md` and
  `docs/helix/01-frame/prd.md`: the vision and PRD that govern this repo.
