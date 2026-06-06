---
name: helix
description: HELIX product flow. Authors and edits PRDs, ADRs, technical designs, feature specs, user stories, test plans, runbooks, and release notes.
version: 0.2.0
license: MIT
---

# HELIX product flow

## Activation discipline (do these in order, every time the skill engages)

### 1. Locate the marker

Find `.helix.yml` by walking UP from the current working directory to the
git root (the directory containing `.git/`). Stop at the first `.helix.yml`
encountered. If the cwd is `/repo/services/api/docs/helix/` and the marker
lives at `/repo/.helix.yml`, you MUST find the parent marker — do not give
up after searching cwd only.

Concretely: run `git rev-parse --show-toplevel` (or fall back to walking up
until `.git/` is found), then check for `.helix.yml` at the top, then at
each level between top and cwd if the design ever supports nested markers
(v1 ignores nested per design §1.1; warn M010 if you find any beyond the
root one).

### 2. Decide activation state

- **Marker present and well-formed**: parse it. The set of `flows[]`
  entries (v2; legacy alias `methodologies[]:` accepted under M020 warn) is
  authoritative. If `helix` is listed, this skill is active for the listed
  `root:` scope. If `helix` is NOT listed but a different flow is, defer to
  that flow's skill — do not also activate.

- **Marker present and malformed** (YAML parse error, missing required keys,
  root outside repo, duplicate id, root resolves to nonexistent dir): STOP.
  Report the marker error verbatim with file and line. Do NOT fall back to
  heuristics. Per design §1.4: "the marker exists precisely to eliminate
  silent misroutes; soft-failing it would reintroduce the failure mode it
  prevents."

- **Marker absent, heuristic file present** (`workflows/methodology.yml`,
  `docs/helix/` tree, etc. — the legacy heuristic filename is retained for
  back-compat detection): emit this banner verbatim before any other
  output:

      No .helix.yml found. Activating helix by heuristic (path: workflows/methodology.yml).
      Run /helix init-marker to make this explicit.

  Substitute the actual heuristic-path that triggered activation. Then
  proceed.

- **Marker absent, no heuristic**: report no active flow. If asked
  for a machine-readable response, return `{"active": []}`. Do not
  improvise that helix is active.

### 3. Enforce scope

For every operation that writes or edits a file, check that the target path
is INSIDE the active flow's `root:` from the marker. If the user
asks for a write outside that scope:

- Refuse the write.
- Surface the marker entry that scoped the flow and the offending
  target path.
- Ask whether they want to (a) update the marker to broaden scope, or (b)
  redirect the write to under the scope, or (c) cancel.

Do NOT silently write outside scope. Scope is the marker's contract; the
skill enforces it.

When the marker declares multiple flows at different scopes, the
flow whose `root:` contains the cwd wins. If cwd is outside every
declared scope, follow design §1.5 resolution chain (explicit prefix →
HELIX_FLOW env (legacy HELIX_METHODOLOGY) → cwd-under-root →
defaults.flow (legacy defaults.methodology) → single entry →
disambiguation banner with deterministic tie-break by listed order).

### 4. Author / edit artifacts

When asked to author or edit an instance document, follow the type's
`template.md` and `prompt.md` from the helix-library plugin. Look up the
type via the flow's `graph.yml` — every node points at a
`library:<slug>` or `local:<slug>` type, and the library tree mounts at
`~/.claude/plugins/<marketplace>/helix-library/<version>/`.

Instance edges (PRD → FEAT, ADR → technical-design, etc.) belong in the
instance's frontmatter under `ddx.links:` per design §2.3. Never embed
edges in the body or in this skill's prompts.

Cross-flow edges (e.g. PRD informs `helix-infra:CI-NNN`) must be
declared in `external_edges:` of `workflows/graph.yml` first, then in the
instance frontmatter with `cross_flow: true` (legacy alias
`cross_methodology: true` accepted for one cycle).

### 5. Authorization boundary

The marker's `flows:` list (legacy `methodologies:`) is the authorization
boundary. Per design §1.5 rule 1, an explicit `/helix <verb>` prefix wins
ONLY if helix is a marker member. If the user runs `/helix-infra intent`
and helix-infra is NOT in `.helix.yml`, REJECT with a diagnostic naming
the marker as the authorization gate. Do not activate the other flow even
with explicit prefix.

### 6. Frontmatter round-trip

Never rewrite unknown frontmatter keys. When you edit an instance
document's body, preserve `ddx.id`, `ddx.review`, `ddx.links`, AND any
vendor-namespaced (`x-*`) or legacy (`relationships:`, `depends_on:`)
keys byte-equivalent. Key order is preserved (insertion-order dict +
`yaml.safe_dump(..., sort_keys=False)`).

Legacy → new key translation (e.g. `relationships:` → `ddx.links:`) is
done ONLY by the explicit migration script
`library/scripts/migrate_relationships_to_links.py`. Never translate as a
side effect of an incidental edit.
