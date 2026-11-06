# Graph profiles

A graph profile binds a flow (`.helix.yml` `flows[].profile`) to a subset of the
artifact catalog plus relationship, authority, and validation rules. Artifact
types stay reusable across profiles; a profile selects and parameterizes them.
See ADR-015 and ADR-016.

A flow without `profile:` uses `software-delivery`, so every existing marker is
unchanged. An unknown profile id is a malformed marker.

Profile file shape (`workflows/profiles/<id>.yml`):

| Key | Meaning |
|-----|---------|
| `profile.id` | Profile id; must equal the file name. |
| `profile.description` | One line. |
| `types` | `all`, or the artifact-type ids the profile selects. Every id must exist in the catalog. |
| `locations` | Optional per-type output path override, relative to the flow root. Overrides `meta.yml output.location`. |
| `edge_kinds` | Link kinds (`ddx.links[].kind`) the profile accepts, beyond `depends_on`, `informs`, `supersedes`. |
| `authority.within_graph` | `positional` (existing: upstream activity governs downstream) or `advisory` (nothing in the graph governs by position). |
| `authority.cross_graph` | Always `advisory` unless the consuming flow grants `governing`. |
| `validation.draft` / `validation.published` | Which `meta.yml validation` tiers apply at each `ddx.status`. |

The software-delivery graph is `workflows/graph.yml`. Other profiles' graphs are
generated to `workflows/profiles/<id>.graph.yml` by
`python3 scripts/generate_graph.py --profile <id>`.
