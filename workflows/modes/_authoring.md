# Authoring (shared contract)

Load this contract for any mode that creates or edits an artifact instance.

## Governing artifacts authored elsewhere

A governing artifact with `authoring.home: external-tool` is read through
its `authoring.connector` when the host exposes that connector (live read of
`authoring.origin`), otherwise through its checked-in Markdown body. A
checked-out artifact with no body and no connector is a prerequisite gap,
not something to paraphrase from memory. Never write through a connector.

## Consult the graph before authoring

When the user asks for a new artifact of type `T` in the active methodology `M`
(per the resolved marker), consult `M`'s graph before drafting. This is the
runtime use of the methodology graph: the same edges the validator checks
govern what the skill should surface as prerequisites at authoring time.

1. Read `M`'s `graph.yml`, bound via §Catalog Resolution (in-tree
   `workflows/graph.yml`, a marker `graph:` pointer, or the `references/`
   floor — whichever resolves first).
2. Find the node `n` whose `type` matches `library:T` or `local:T`.
3. Enumerate incoming edges to `n` whose `kind` is one of
   `{requires, contains, informs}`.
4. For each such edge `(src → n, kind, required)`:
   - If `required: true` AND no instance of `src.type` exists in this
     methodology's instance scope, **surface this as a prerequisite**. Per the
     resolved §Autonomy level, either ask whether to draft `src` first
     (`low`/`medium`), or draft `src` autonomously then `n` (`high`).
   - If `required: false` AND no instance of `src.type` exists, note it as a
     "consider also drafting" but do not block authoring of `n`.
5. Only after prerequisites are present (or the operator has explicitly chosen
   to skip them) proceed to author the requested artifact.
6. After authoring, populate `ddx.links` to point at existing upstream
   instances. **Do not invent links**: per Edge Authority Asymmetry, types
   declare what is possible and instances declare what is actual. Every
   `ddx.links` entry is a deliberate authoring decision, never a mechanical
   projection of a graph edge.

Graph consultation is **per-authoring**, not per-session: re-consult on every
new artifact request because the instance scope may have changed since the
previous turn (operator-side edits, parallel work, evolve passes).

If the graph carries a **non-standard or locally-added edge** (a project's
`workflows/graph.yml` introduces an edge not in the canonical HELIX library —
e.g. `prd requires market-validation-brief`), the same rules apply: a graph
edge governs what the skill surfaces, regardless of whether the edge matches
general HELIX knowledge. Surfacing only the canonical edges and skipping the
graph-declared ones is a graph-consultation defect, not an acceptable
shorthand.
