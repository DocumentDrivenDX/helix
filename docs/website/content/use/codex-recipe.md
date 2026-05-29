---
title: Codex HELIX Recipe
weight: 22
---

Use this recipe when Codex is the implementation agent and HELIX supplies the
planning, alignment, and handoff contract. DDx is not required.

## Install the HELIX skill

HELIX ships as a routing skill (`skills/helix/SKILL.md`, compliant with the
agentskills.io specification) plus the artifact catalog under
`workflows/activities/`. Installing the skill makes HELIX discoverable in any
Codex session.

The recommended path uses the Skills CLI, which needs Node.js:

```bash
npx skills add DocumentDrivenDX/helix -a codex
```

For scripted or Docker environments without Node, clone the repo over HTTPS and
copy the skill into the Codex discovery path:

```bash
git clone https://github.com/DocumentDrivenDX/helix /tmp/helix-src
mkdir -p ~/.codex/skills/helix
cp -r /tmp/helix-src/skills/helix/* ~/.codex/skills/helix/
```

Either way, Codex auto-discovers the skill at session start. The full procedure,
including DDx symlinks and Docker auth, is in the
[GitHub install guide](https://github.com/DocumentDrivenDX/helix/blob/main/docs/install/codex.md).

## What the runtime must provide

Codex, or the environment around it, must provide:

- Explicit working directory and file scope.
- Clear instructions about which artifacts govern the task.
- A way to apply direct file edits.
- A final response that names changed files and unresolved follow-up.
- Optional validation commands, only when the human asks Codex to run them.

Codex works best when the handoff is narrow. Treat the prompt as the execution
boundary.

## Recipe 1: create the first artifact stack

Ask Codex to create only the artifact files, not implementation code.

Prompt:

```text
In <repo>, create a minimal HELIX artifact stack for <project>. Write only these
files: <artifact paths>. Use product vision, PRD, feature spec, design note, and
implementation handoff. Keep unknowns explicit. Do not run tests. Do not edit
code. Final response: exact files changed.
```

Human edit pass:

- Tighten the product facts and non-goals.
- Replace inferred requirements with explicit decisions.
- Add real constraints such as compliance, deployment, data ownership, or
  supported platforms.
- Remove implementation details that are not justified by upstream artifacts.

## Recipe 2: run the first alignment pass

Prompt:

```text
Run a HELIX alignment review for <artifact paths>. Findings first. For each
finding, cite the downstream artifact, the governing upstream artifact, and the
specific correction needed. Do not edit files until I approve. Do not inspect or
modify unrelated areas.
```

After approving corrections:

```text
Apply the approved alignment edits only to <artifact paths>. Keep the authority
order intact. Do not touch implementation files, generated references, tracker
state, or site navigation.
```

## Recipe 3: create the first implementation handoff

Prompt:

```text
Create a HELIX implementation handoff for <feature>. Use the aligned artifacts
as authority. Include allowed write scope, files to avoid, acceptance criteria,
validation expectations, and final-response requirements. Do not implement.
```

Implementation prompt:

```text
You are implementing this HELIX handoff in <repo>. Own only this write scope:
<paths>. Avoid these paths: <paths>. Read each required file at most once before
editing. Do not run tests unless explicitly asked. Do not revert or overwrite
other workers' changes. Final response: summary and exact files changed.
```

This prompt shape makes the runtime responsibilities explicit: Codex receives
authority, scope, validation policy, and evidence requirements from the human
instead of from a DDx queue.
