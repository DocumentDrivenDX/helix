---
title: Claude Code HELIX Recipe
weight: 21
---

Use this recipe when Claude Code is the agent runtime and HELIX provides the
artifact discipline. DDx is optional; Claude Code can apply HELIX by reading and
editing artifacts directly.

## What the runtime must provide

Claude Code must provide:

- Repository-aware context loading for the selected artifact files.
- File-scoped edits that avoid unrelated changes.
- A human approval point before implementation begins.
- A final response that maps changed files and evidence back to acceptance
  criteria.

Humans still own prioritization and artifact authority. Claude Code can propose
edits, but humans decide which artifact changes become governing context.

## Recipe 1: create the first artifact stack

Create these files in your project, using the artifact catalog as the shape:

- `docs/helix/00-discover/product-vision.md`
- `docs/helix/01-frame/prd.md`
- `docs/helix/02-plan/<feature>.md`
- `docs/helix/03-design/<feature>.md`
- `docs/helix/04-implement/<feature>-handoff.md`

Prompt Claude Code:

```text
Create the first HELIX artifact stack for <project>. Use these paths:
<paths>. Start from concise, decision-oriented documents. Mark unknowns as open
questions. Do not implement product code. Preserve this authority order:
vision -> PRD -> feature spec -> design -> implementation handoff.
```

Review the generated stack manually. Edit product facts, constraints, and
success criteria yourself before asking for implementation.

## Recipe 2: run the first alignment pass

Prompt Claude Code:

```text
Run a HELIX alignment pass over these files: <artifact paths>. Read each file in
authority order. Report contradictions, missing downstream coverage, vague
acceptance criteria, and stale assumptions. Patch only artifact files I name
after reviewing your findings.
```

After the findings:

- Accept or reject each proposed correction.
- Ask Claude Code to patch only the accepted artifact files.
- Keep open product questions in the artifacts instead of resolving them by
  invention.

Patch prompt:

```text
Apply only the accepted alignment edits to <artifact paths>. Do not touch code,
configuration, generated references, or unrelated documentation.
```

## Recipe 3: create the first implementation handoff

Prompt Claude Code:

```text
Create an implementation handoff from the aligned HELIX artifacts. Include:
governing artifact references, allowed write scope, explicit non-goals,
acceptance criteria, validation commands if known, and evidence expected in the
final response. Do not implement.
```

Then implement in a separate Claude Code session:

```text
Implement this HELIX handoff. Read only the named governing artifacts and files
needed for the allowed write scope. Do not modify out-of-scope areas. Do not
invent new requirements. If acceptance criteria are ambiguous, stop and ask.
Final response must list files changed and evidence for each criterion.
```

If Claude Code discovers new work, capture it as a follow-up note or issue in
your normal tracker. Do not let implementation expand the handoff silently.
