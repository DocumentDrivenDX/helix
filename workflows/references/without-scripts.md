# Without Scripts

HELIX needs a host that can read, write, and search files. No mode requires running code. The scripts beside the skill are optional tools that make some checks repeatable, and this page says how to do each one by hand.

## Rules

1. **Run a script only through uv:** `uv run --script <skill-dir>/scripts/<name>.py <args>`. Each script declares its own dependencies and ships a lock file. Do not run one with `python` or `python3`, and do not install packages for it.
2. **When uv is missing, or the host cannot run commands, work by hand** from the section below. Do not stop, and do not ask the user to install anything before you continue. You may say that uv would let the script run.
3. **Say what was done which way.** In the handoff, name each script that did not run, what you checked by hand, and what you did not check. A hand check is never reported as a script passing.
4. **A script that fails to start has checked nothing.** Report the error and work by hand.

The scripts' other files (`prose_audit.py`, `figure_attributes.py`, `structured_blocks.py`) are parts of `validate-instance.py` and `assessment-tables.py`. Their rules are in those two sections.

## validate-instance.py

Read the instance, its type's `meta.yml` and `template.md`, and the flow's profile (`profiles/<profile>.yml`; `software-delivery` when the flow names none). Findings are **blocking** or **warning**. As in `modes/validate.md`, a finding is evidence to assess and not an automatic gate.

**Scope and tier.** When `ddx.scope` is set and `validation.by_scope.<scope>` exists, its `required_sections`, `pattern_checks`, and `automated_checks` replace the type's. When the profile's `validation.default` does not include `all` and the publish tier was not asked for, every blocking finding becomes a warning except frontmatter, link, and structured-block findings, which stay blocking. Lifecycle status selects nothing.

**Frontmatter and links.**

- A file without `ddx:` is acceptable. A `ddx:` block must be a mapping with `id`, and `authoring.home` of `repo` or `external-tool`.
- Each `ddx.links` entry is an id string, or a mapping with `id`.
- Warn on a `kind` outside `informed_by`, `informs`, `addresses`, `evaluates`, `supported_by`, `contradicts`, `answers`, or, when the profile's `edge_kinds` is not empty, outside that list (`informed_by` and `informs` are always allowed). An empty or missing list restricts nothing.
- `authority` is `advisory` or `governing`. `governing` blocks when the profile grants only advisory authority for that scope: `cross_graph` for a link with `graph:`, else `within_graph`. The defaults are advisory across graphs and positional within one.
- An `answers` link names `question:`, a whole number of 1 or more.
- At the publish tier, each link whose kind is in `validation.pin_links.kinds` has `rev: git:<7-40 hex>` or `rev: sha256:<64 hex>`.

**Content.**

- `required_sections`: each id matches an H2. To make the id from a heading, lower-case it, turn each run of other characters into `_`, and trim `_`. For a YAML artifact, each id is a key.
- `pattern_checks`: count the regular expression's matches and compare with `expected` (a number means exactly that many; `>=N`, `>N`, `<=N`, `<N`, and `==N` compare).
- `placeholder`: outside code fences, `[TODO]`, `TBD`, `<placeholder>`, `[Fill in]`, and `[NEEDS CLARIFICATION` block. A bracketed capitalized phrase that is not a link, such as `[Name]`, is a warning.
- A citation of repository history (a pull request number, a pull request or commit URL, or a commit hash) is a warning.

**`automated_checks` types.** Run only the types the `meta.yml` entries name, each at its entry's `severity` (blocking when it gives none).

| Type | Rule |
|---|---|
| `unique_constraint` | Values of `field` do not repeat. Read them from table columns and `**Label**: value` lines; a field ending `_id` also reads `id`. |
| `not_equals` | No value of `field` equals `value`. |
| `module_boundaries` | Skip when there is no `## Module Boundaries`; otherwise exactly one. `**Source Applicability**:` is `source; <reason>` or `source-free; <reason>`. A source project fills `**Integration Owners**`, `**Construction Policy**`, and `**Boundary Check**`, and has a table with at least one row filling Module, Responsibility / Owned Types, Public API, Allowed Dependencies, and Forbidden Dependencies. |
| `ux_coverage` | Skip when there is no `## UX Coverage`; otherwise exactly one. Its table (Pattern, Disposition, AC IDs or reason) lists each of `navigation`, `keyboard-overlays`, `async-actions`, `forms`, `data-states`, `destructive-actions` once. `not-applicable` gives a concrete reason. `covered` gives unique `US-<n>-AC<n>` ids, each with one row under `## Acceptance Criteria Test Mapping` that fills the test, the asserted behavior, and the file or command. |
| `findings_sources` | When `## Findings` exists, the first table under `### Claims` has a Source column, filled for every claim (`-`, `n/a`, and `none` are empty). |
| `reader_views` | `## Views` has `###` headings `Risk & Compliance`, `Finance`, `IT Operations`, and `Apps Dev`, none empty; one that does not apply says Not applicable or Not researched. A document with no Views section gets a warning only. |
| `limits_table` | A table under `## Limits of the Position` has exactly the columns Condition, Option that wins, Evidence, and at least one row. No table is a warning only. |

**Visuals.** Each fenced `visual` block has `id=<id>` on its opening line (lowercase letters, digits, hyphens; unique, counting Mermaid `%% id:` names). Its body is a YAML mapping with a `source` and no `kind`, or with `kind`, `form`, and `question`. Kinds and forms: flow (network, pipeline, zoned, lanes); sequence (lifelines, ladder); structure (stack, tree, nested, entities); state (machine, lifecycle); timeline (milestones, roadmap, history); comparison (matrix, quadrant, before-after); metric (stat, bar, line, meter). A pair the type's `visuals:` does not list is a warning.

**Figures.** A `{...}` list naming `basis`, `source`, or `accessed` blocks unless: no name repeats; `basis` is `published`, `third-party`, or `not-published`; and, except for `not-published`, `source` is given and `accessed` is a real `YYYY-MM-DD` date. Ignore code, HTML comments, and link destinations.

**Prose.** Only for a type with `prose.audience: human`, and not for a path matching `prose.exempt` in `.helix.yml`. Take the limits for the type's voice profile from `voice.yml`: words per sentence, sentences per paragraph or list item, words per table cell, and any `prose.budget_words`. Flag each breach and each phrase under `prose.avoid_phrases`, `information_only`, and `pronouns` (a quoted or code mention does not count). Findings are warnings unless the project sets `prose.strict: true`. Count paragraphs, list items, and table cells; skip frontmatter, headings, code fences, comments, generated blocks between `<!-- name: ... -->` and `<!-- /name -->`, and lines matching `prose.skip_lines`. Block quotes and collapsed `<details>` are checked but left out of the budget.

**Structured blocks** (`assessment:`, `recommendations:`, `weights:`): check the next section's data rules. They block.

## assessment-tables.py

A document needs this only when its front matter holds an `assessment:`, `recommendations:`, or `weights:` block. The block is the record; the tables are written from it. Change the block, then rewrite the table. Never edit a table to differ from its block. When you write tables by hand, say so in the handoff, so a later script run can confirm them.

**Shared files.** `criteria.yml` (`criteria:` entries with `id`, `label`, and optional `definition`, `concern`, `view`; each of `label`, `definition`, and `concern` is a single line of text; unique ids; no weights) sits in the nearest ancestor directory that has it, searching no higher than the one holding `.helix.yml`. A `views.yml` beside it (`views:` entries with unique `id` and a `label`) makes every `view:` one of those ids. A `keys.yml`, found the same way, maps short lower-case keys to document ids under `keys:`. A key is not itself a document id, appears once, and is not also a linked id. A key may stand for a subject or a `based_on` assessment inside a block, never in `ddx.links`. A document that uses a key records it under a top-level `keys:`, matching `keys.yml`.

**Placement and data rules.** `assessment:` belongs only on a technology assessment; `recommendations:` and `weights:` only on a position paper.

- **Assessment:** `criteria` is a list of ids from `criteria.yml` without repeats. `subjects` is at least two different `{id, label}` entries, each linked in `ddx.links` as `evaluates` or `supported_by` without `graph:`. `ratings` has exactly one entry for every criterion and subject, each with exactly one of `finding` or `gap`, on one line. Optional `comparison.rows` is `criteria` (default) or `subjects`; `comparison.tables` places every criterion in exactly one list. No weights anywhere in it.
- **Recommendations:** a non-empty list. Each has `subject` (linked as above) and `context`, a pair that appears once; `stance` of `recommended`, `conditional` (which needs `conditions`), `watch`, or `avoid`; `rationale`; `based_on`, a non-empty list of `{assessment, criteria}`, each assessment linked as `supported_by` and each criterion in `criteria.yml`; `since` and a later `review_by` as `YYYY-MM-DD`; and `approved_by` with `approved_on`, both or neither. `label`, `context`, and `conditions` are one line. At the publish tier each `based_on` link has a pinned `rev`.
- **Weights:** a non-empty list of `{criterion, weight, reason}`. `weight` is `decisive`, `important`, or `minor`, never a number. `reason` is one line. Each criterion appears once, is in `criteria.yml`, and has a `finding` (not only a gap) in an assessment the paper links as `supported_by`. Search the assessments under the directory holding `criteria.yml`.

**The tables.** Replace only the table; leave the prose around it. Trim each cell and write `|` inside a cell as `\|`. In the line under the header, give each column as many hyphens as its header has characters, plus two.

| Section (first table unless said otherwise) | Columns | Rows |
|---|---|---|
| `## Criteria` | Criterion, Definition, Concern | One per criterion in the block's order: its label, its definition, its concern or `none` |
| `## Comparison`, rows are criteria | Criterion, then each subject's label | One per criterion: its label, then each subject's finding or gap |
| `## Comparison`, rows are subjects | Option, then each criterion's label | One per subject: its label, then each finding or gap |
| `## Recommendations` | Technology, Stance, Context, Conditions, Based on | One per entry: `label` or the subject id; the stance name with `(Approved)` when `approved_by` is set, else `(Proposed)`; context; conditions or empty; the `based_on` assessment ids joined by `, ` |
| `## Decision Criteria` | Criterion, Weight, Why | One per weight: the criterion's label; Decisive, Important, or Minor; the reason |

Stance names are Recommended, Use with conditions, Watch, and Avoid. The Comparison section has one table for each list in `comparison.tables` (one table of all criteria when there is none), and no other tables. With keys, resolve each key to its document id before building the cells.

## pin-sources.py

A pin records which revision of each source a document was issued from. It applies to `ddx.links` mappings whose kind is `informed_by`, `evaluates`, or `supported_by`. A link with `graph:`, or whose id no tracked Markdown file in this repository has, belongs to the runtime; report it as external.

- **Pin:** find the tracked file whose front matter has that `ddx.id`, then run `git log -1 --format=%H -- <file>` and add `rev: git:<that commit>` under the link. Leave an existing `rev` alone. A file with no commit cannot be pinned; it must be committed first. Check `git status -- <file>`: uncommitted changes are not in the pin, so say so.
- **Without git commands**, record `rev: sha256:<64 hex>` of the file's bytes if the host can compute a hash. It lets a reader verify the content but not recover it. Never type a hash or commit id you did not read from a tool. If the host can do neither, leave the link unpinned, report that the document cannot be issued as pinned from this host, and name what is needed (git).
- **Check:** `git show <commit>:<file>` must return the source. Compare it with the current file and report any difference as drift; the document keeps its pinned content.
- **Materialize:** write each `git show` result into the target directory under the source's path.

## check-deliverable.py

Run these over a deck, brief, or one-pager script. Read `deliverables/slide-patterns.yml`, `deliverables/theme.yml`, and the chosen flow in `deliverables/flows/<flow>.yml`. Items are blocking unless marked as warnings.

- **Structure:** `## Brief`, `## Story`, `## Content`, `## Sources`, `## Assumptions and gaps`, and `## Render` exist. Units are `### <n>. <title>` under Content, each with `**Pattern**`, `**Body**`, `**Visual**`, `**Notes**`, and `**Sources**` lines. Patterns come from `slide-patterns.yml`. Sources has `S<n>` rows; each unit cites at least one, and only existing ones.
- **Placeholders:** none of the markers listed under `validate-instance.py`. A bracketed capitalized phrase is a warning.
- **Titles:** unless the flow's `heading_style` is `label`, the document title and every unit title outside `appendix-sources` makes a claim: at least three words, and not a label such as Overview, Background, Results, Summary, or Next steps. A title has no "N of M" count. A brief or one-pager writes titles in sentence case. At most 10 words (aim for 8).
- **Title and shape writing:** apply the headline pass and shape pass in `actions/present.md` and the human-facing voice profile to titles, bullets, and visual cells: no contrastive reversal, colon list, imperative chain, listicle count, stacked negation, forced triplet, flattery, slogan, universal claim, mannered or marketing phrase, invented status, internal code, catalog count, hedge, em dash, or narration of the document. This is judgement. The script also matches fixed phrase lists that are not repeated here, so report that those lists were not matched.
- **Visuals:** specific, at least six words, saying what is shown, its series, and its source. In a `kind:` spec no field value contains a period followed by a space. Any owner, date, or likelihood and impact grade in a spec appears in Sources or in Assumptions and gaps.
- **Vocabulary:** no HELIX ids or terms (artifact ids, work item, acceptance criteria, artifact graph, ddx, activity names used as stages) in a title, body, or notes. Warn on project jargon the audience would need defined.
- **Numbers:** every figure of two or more characters in a body or visual spec appears in the Sources table. Layout fields in a spec do not count.
- **Limits (warnings):** the pattern's bullet, word, and title limits. For a brief or one-pager, multiply word limits by 2.5 and bullet counts by 1.5. Warn on more consecutive units of one pattern than the density limit (double it for documents), a one-pager over `max_words_one_pager` (450), two shapes on a slide that say the same thing, neighboring titles with no content word in common, and a deck with more than 12 content slides.
- **Deck order:** `title` first. End with `ask-next-steps` then `appendix-sources`; when the flow does not require the ask, end with `appendix-sources`.
- **Coverage:** Brief has `**Breadth**: survey` or `deep-dive`. Story has a `**Concept coverage**` table marking each group `covered` or `omitted`, with a reason of three words or more for an omission. A survey covers at least five groups. Every Must cover item is covered; no unit mentions a Must omit item.
- **Render:** lists at least one rendered target path. Warn when it does not record that each page was rendered and inspected, naming what the host lacks, or when `ddx.authoring.export` is not one path.

## corpus-inventory.py

It lists candidates before anyone decides what to say. By hand, for the declared scope:

1. Make one row per Markdown file: authority rank, type, title, heading claims, and size. Rank by activity directory, `00-discover` as 1 through `06-iterate` as 7. A README or principles file ranks with frame (2), and anything else ranks last (9).
2. **Structure:** from `graph.yml`, the activity gates, and the concerns index, list the authority chain, how changes propagate between layers, the gates and floors, and what runs unasked. These are concept groups even when no document names them.
3. **Roles and hand-offs:** note who approves, confirms, reviews, decides, stops, infers, or records, and for whom.
4. **Authority floor:** every heading and table row of the top-ranked documents is a candidate, however rarely it recurs.
5. **Recurrence:** group the other terms that appear in two or more documents.

A hand inventory of a large scope may not read every file. Say which files you read and which you did not.
