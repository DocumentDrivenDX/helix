---
ddx:
  id: PP-001
  type: position-paper
  authoring:
    home: repo
  links:
    - {id: TA-001, kind: supported_by, rev: example}
---

# PP-001: New repository tooling should default to Python

## Thesis

**Thesis**: New command-line tooling in a repository that already uses Python
should be written in Python, not Node.js, unless a script needs a Node.js
library with no equivalent.

## Audience and Stakes

Maintainers choosing a runtime for a new tooling script. A second runtime in
a repository adds installation and upkeep for every contributor.

## Argument

1. Both runtimes handle text and file work comparably on the cited
   assessment. [TA-001, Comparison]
2. A repository with one runtime has less to install and maintain than one
   with two. Author's judgment.
3. So the existing runtime wins unless a library requires the other. Author's
   judgment.

## Objections and Answers

| Objection | Answer | Evidence |
|-----------|--------|----------|
| The team already writes JavaScript | Familiarity favors Node.js for that team; the thesis assumes the repository's existing runtime is Python | Author's judgment |
| Distribution of a single script may differ | The assessment has no finding on distribution; the thesis does not rely on it | TA-001, Contradictions and Gaps |

## Limits of the Position

The paper does not claim Python is better in general. It fails where the
repository's existing runtime is Node.js, or a required library exists only
for Node.js.

## Evidence

| Reference | Kind | Revision | Used for |
|-----------|------|----------|----------|
| TA-001 | Technology assessment | example | Argument step 1 |
