# T17 — graph.yml dangling requires edge [HIGH RISK]

- **Installed:** `helix-library`, `helix`
- **Risk:** high (graph-correctness gate)

## Scenario

`requires: [01-frame/this-node-does-not-exist]` — the target node id
is not defined anywhere in the file.

## Why it matters

A dangling requires edge is a silent skip at methodology walk time
(the runtime says "prerequisite satisfied" because the prereq does
not exist). Companion to T16 — same risk class (graph correctness),
different failure shape. Validator must catch.

## Pass signature

Exit non-zero AND stderr matches `(?i)dangling|unknown node|undefined
node|not defined|not found` AND names the missing target
`01-frame/this-node-does-not-exist`.

## Failure signatures

- Exit 0 → dangling edge silently accepted.
- Diagnostic without the missing node id → unactionable.
