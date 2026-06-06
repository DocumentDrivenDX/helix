---
name: helix
description: |
  HELIX product methodology — drives the family's product flow.

  Activate this skill when the user asks to:
    - start, begin, or scaffold a helix project
    - create, draft, write, or edit a PRD (Product Requirements Document)
    - create, draft, write, or edit a product vision, opportunity canvas,
      feature specification, user story, ADR, technical design, test plan,
      runbook, or release notes
    - frame, design, test, build, deploy, or iterate on a product
    - plan a sprint or rollout for product work
    - review or audit a product methodology artifact
    - answer "what's next" in a product workflow

  Do NOT activate for infrastructure work (terraform/opentofu), website
  content authoring, or sales/ops work — those are sibling skills
  (helix-infra, helix-web, etc.).

  Distinct from helix-library (a data-only catalog plugin).
version: 0.2.0
license: MIT
---

# HELIX product methodology

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

- **Marker present and well-formed**: parse it. The set of `methodologies[]`
  entries is authoritative. If `helix` is listed, this skill is active for
  the listed `root:` scope. If `helix` is NOT listed but a different
  methodology is, defer to that methodology's skill — do not also activate.

- **Marker present and malformed** (YAML parse error, missing required keys,
  root outside repo, duplicate id, root resolves to nonexistent dir): STOP.
  Report the marker error verbatim with file and line. Do NOT fall back to
  heuristics. Per design §1.4: "the marker exists precisely to eliminate
  silent misroutes; soft-failing it would reintroduce the failure mode it
  prevents."

- **Marker absent, heuristic file present** (`workflows/methodology.yml`,
  `docs/helix/` tree, etc.): emit this banner verbatim before any other
  output:

      No .helix.yml found. Activating helix by heuristic (path: workflows/methodology.yml).
      Run /helix init-marker to make this explicit.

  Substitute the actual heuristic-path that triggered activation. Then
  proceed.

- **Marker absent, no heuristic**: report no active methodology. If asked
  for a machine-readable response, return `{"active": []}`. Do not
  improvise that helix is active.

### 3. Enforce scope

For every operation that writes or edits a file, check that the target path
is INSIDE the active methodology's `root:` from the marker. If the user
asks for a write outside that scope:

- Refuse the write.
- Surface the marker entry that scoped the methodology and the offending
  target path.
- Ask whether they want to (a) update the marker to broaden scope, or (b)
  redirect the write to under the scope, or (c) cancel.

Do NOT silently write outside scope. Scope is the marker's contract; the
skill enforces it.

When the marker declares multiple methodologies at different scopes, the
methodology whose `root:` contains the cwd wins. If cwd is outside every
declared scope, follow design §1.5 resolution chain (explicit prefix →
HELIX_METHODOLOGY env → cwd-under-root → defaults.methodology → single
entry → disambiguation banner with deterministic tie-break by listed
order).

### 4. Author / edit artifacts

When asked to author or edit an instance document, follow the type's
`template.md` and `prompt.md` from the helix-library plugin. Look up the
type via the methodology's `graph.yml` — every node points at a
`library:<slug>` or `local:<slug>` type, and the library tree mounts at
`~/.claude/plugins/<marketplace>/helix-library/<version>/`.

Instance edges (PRD → FEAT, ADR → technical-design, etc.) belong in the
instance's frontmatter under `ddx.links:` per design §2.3. Never embed
edges in the body or in this skill's prompts.

Cross-methodology edges (e.g. PRD informs `helix-infra:CI-NNN`) must be
declared in `external_edges:` of `workflows/graph.yml` first, then in the
instance frontmatter with `cross_methodology: true`.

### 5. Authorization boundary

The marker's `methodologies:` list is the authorization boundary. Per
design §1.5 rule 1, an explicit `/helix <verb>` prefix wins ONLY if helix
is a marker member. If the user runs `/helix-infra intent` and helix-infra
is NOT in `.helix.yml`, REJECT with a diagnostic naming the marker as the
authorization gate. Do not activate the other methodology even with
explicit prefix.

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

<!-- §7–§9 reserved for forthcoming activation/scope/authoring sections. -->

### 10. Do not auto-populate `ddx.links` from `graph.yml`

Per design §2.7 (Edge Authority Asymmetry, Invariant 1): the graph
declares what edges are *possible*; instance frontmatter declares what
edges are *actual*. The skill is the deliberator between them and MUST
NOT mechanically join one to the other.

**Prohibition.** When authoring or editing an instance document, you
MUST NOT write entries into `ddx.links` solely because `graph.yml`
permits a type-pair-with-kind edge between this instance's type and
another type present in the workspace. A graph edge is a *candidate
catalog*, not a populate instruction.

**Required behaviour.** When `graph.yml` declares a candidate edge from
this type to another type AND one or more concrete instance targets of
that other type exist in the workspace:

1. Enumerate the candidate targets (by `ddx.id` and short title).
2. Surface them in your reply as candidate edges, naming the edge kind
   from the graph (e.g., "PRD informs FEAT-001 (Checkout), FEAT-002
   (Order queue)?").
3. Ask the operator which (if any) to add to `ddx.links` before you
   write the file. The operator's explicit naming — by id, title, or
   "all of them" — is what authorizes the edge.
4. Write `ddx.links` with only the entries the operator named. If the
   operator declines all candidates, write `ddx.links: []` (or omit if
   the schema permits absence).

**Autonomy does NOT relax this.** Under `autonomy=guided`,
`autonomy=autonomous`, OR `autonomy=aggressive`, the prohibition holds.
`autonomous` excuses the skill from confirming each in-scope mechanical
write (creating the file under the marker's root, filling boilerplate
sections from the template, etc.). It does NOT excuse skipping edge
deliberation: writing an `ddx.links` entry the operator has not named is
out-of-scope at every autonomy level. Edge authoring is implicitly in
the `stop_at` set.

**Exception — operator already named the edge.** If the operator's
prompt explicitly names both endpoints AND the edge kind (e.g.,
"Create a PRD that informs FEAT-001 and FEAT-002"), you may write the
named edges into `ddx.links` directly under `autonomous`. Under
`guided` or `manual`, confirm before writing per those levels'
defaults. The trigger for the exception is operator naming, not graph
co-presence.

**Failure mode this prevents.** A skill that reads
`graph.yml`, sees `prd informs feature-specification`, scans the
workspace for FEATs, and writes `ddx.links: [FEAT-001, FEAT-002]`
without prompting has converted Layer 2 (possibility) into Layer 3
(actuality) by mechanical join. The graph stops being a candidate
catalog and starts being a populate instruction; instance edges stop
reflecting authoring intent and start reflecting type co-presence. This
erodes the traceability signal the three-layer split exists to
preserve.

The bench category `edge-asymmetry` (rows EA-01..EA-04) is the
regression test for this prohibition. Halting the bench on any
EA-NN failure is a P4 invariant.
