# T16 — graph.yml cycle without allowed_cycles [HIGH RISK]

- **Installed:** `helix-library`, `helix`
- **Risk:** high (graph-correctness gate)

## Scenario

`workspace/graph.yml` declares `01-frame/node-a requires
02-design/node-b` AND `02-design/node-b requires 01-frame/node-a` —
a cycle, with no `allowed_cycles` annotation.

## Why it matters

Runtime methodology walks on a cyclic graph are either infinite
loops or arbitrary tie-breaks (nondeterministic). Design §10 sells
the validator as gating this. T10/T11 only test the `binds:` field
namespacing — two implementations could both pass T10/T11/T12 yet
differ on whether they catch cycles. This fixture pins it.

## Pass signature

`exit non-zero` AND stderr matches `(?i)cycle|cyclic|circular` AND
names BOTH `01-frame/node-a` and `02-design/node-b`.

## Failure signatures

- Exit 0 → cycle silently accepted.
- Exit non-zero but stderr names only one node → unactionable.
- Validator hangs (infinite traversal during cycle check) → runner
  must enforce a wall-clock timeout (recommend 10s per validator
  invocation).
