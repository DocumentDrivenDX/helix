# Writing the HELIX site content

Voice and conventions for the hand-authored pages in this tree. Read this before
drafting or editing one.

## Scope

This guide governs the hand-authored narrative: `_index.md` and the pages under
`why/`, `use/`, `install/`, `platforms/`, `skills/`, and `reference/`.
It extends the methodology-level Documentation Voice contract in
[`workflows/conventions.md`](../../workflows/conventions.md); these site rules
are stricter editorial guidance for public pages, not a separate HELIX voice.

It does not govern the generated and published trees, which are projections of
upstream sources and must be edited there, not here:

- `artifact-types/` and `concerns/` come from `workflows/` via
  `scripts/generate-reference.py`.
- `artifacts/` comes from `docs/helix/` via `scripts/publish-artifacts.py`.
- `research/` comes from `docs/resources/` via `scripts/publish-resources.py`.

The rules below are enforced mechanically by Vale (`.vale.ini`, style package
`.vale/styles/Helix/`). Run `just lint-prose` before committing.

## Voice

- Explain the methodology plainly. State what an activity, artifact, or concern
  does and why it earns its place. A reader should finish a page knowing what to
  do next.
- Let the substance carry the page. Drop hype verbs (transforms, revolutionizes,
  supercharges). Prefer plain verbs: defines, enforces, propagates, blocks.
- Earn emphasis. Show the reader why something matters with a concrete example
  or consequence rather than asserting that it is important.

## Honesty and claims

- Scope every claim to what HELIX actually does. If a gate runs only at build
  exit, say so. Do not imply coverage the methodology does not provide.
- Credit prior art and alternatives. HELIX borrows from waterfall, agile, and
  spec-driven practice. Name what it keeps and what it drops.
- Lead with the durable point. A structural commitment (specs are the contract,
  concerns propagate once) outlasts any single workflow detail.
- State caveats in line, next to the claim they qualify, not in a footnote.

## Anti-slop

Run the `avoid-ai-writing` skill on every draft, then do its second-pass audit
for survivors. The mechanized rules:

- No em dashes in prose. Use a comma, colon, parentheses, or two sentences.
- No "it's not X, it's Y" constructions. No compulsive rule-of-three. No bolded
  inline-header bullets and no bold TL;DR labels; use plain bullets.
- No marketing or call-to-action blocks. No `delve / leverage / seamless /
  robust / landscape / realm`-type filler. Vary sentence length.
- Stop leaning on "honest", "honestly", "the honest version", "worth noting", or
  "the real X". These are tics. State the point or the caveat directly.

## Structure

- `why/` pages make an argument: state the claim once, support it, give the
  reader a takeaway. Link to the relevant `use/` page rather than re-explaining
  procedure.
- `use/` pages are procedures: prerequisites, numbered steps, expected result.
  Point to `reference/` and the generated catalogs for definitions.
- Do not repeat a concept across pages. Define it once and link to it.

## Naming and references

- **HELIX** is the methodology and artifact catalog (this repo: templates,
  concerns, workflows, and one skill). **DDx** is the separate runtime that owns
  the loop, the graph, beads, and the CLI. Keep the boundary clear: HELIX content
  should read sensibly even where DDx is not present.
- Use the methodology's own terms consistently: **activities** (discover, frame,
  design, test, build, deploy, iterate), **artifacts**, **concerns**, **beads**.
- The GitHub organization is **DocumentDrivenDX**; link
  `https://github.com/DocumentDrivenDX/helix`.

## Files and links

- One H1 per page; the page title comes from front matter, so do not add a
  second top-level heading in the body.
- Cross-links between content pages are relative and use the Hugo page path
  (for example `/why/the-thesis/`), not a filesystem path.
- After renaming a page or changing its slug, re-point every link to it and any
  nav or menu entry in `hugo.yaml`.
