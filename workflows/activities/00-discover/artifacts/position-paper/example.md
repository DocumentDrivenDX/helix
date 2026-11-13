---
ddx:
  id: PP-001
  type: position-paper
  authoring:
    home: repo
  links:
    - {id: TA-001, kind: supported_by, rev: example}
    - {id: component-profile-python-reusable, kind: supported_by, rev: example}
recommendations:
  - subject: component-profile-python-reusable
    label: Python
    context: repository-tooling
    stance: conditional
    conditions: The repository already uses Python and no script needs a Node.js-only library.
    rationale: One runtime is less to install and maintain than two, and the cited assessment finds the two comparable for text and file work.
    based_on: [{assessment: TA-001, criteria: [text-and-file-handling]}]
    since: 2026-11-06
    review_by: 2027-02-06
weights:
  - criterion: text-and-file-handling
    weight: decisive
    reason: Repository tooling is mostly reading and rewriting text files.
  - criterion: dependency-isolation
    weight: minor
    reason: Tooling scripts here lean on the standard library.
---

# PP-001: New repository tooling should default to Python

## Thesis

**Thesis**: New command-line tooling in a repository that already uses Python
should be written in Python, not Node.js, unless a script needs a Node.js
library with no equivalent.

## Audience and Stakes

Maintainers choosing a runtime for a new tooling script. A second runtime in
a repository adds installation and upkeep for every contributor.

## Decision Criteria

| Criterion | Weight | Why |
|-----------|--------|-----|
| Text and file handling | Decisive | Repository tooling is mostly reading and rewriting text files. |
| Dependency isolation | Minor | Tooling scripts here lean on the standard library. |

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

## Recommendations

| Technology | Stance | Context | Conditions | Based on |
|------------|--------|---------|------------|----------|
| Python | Use with conditions (Proposed) | repository-tooling | The repository already uses Python and no script needs a Node.js-only library. | TA-001 |

## Limits of the Position

The paper does not claim Python is better in general.

| Condition | Option that wins | Evidence |
|-----------|------------------|----------|
| The repository's existing runtime is Node.js | Node.js | Author's judgment: argument step 2 favours whichever runtime is already there |
| A script needs a library that exists only for Node.js | Node.js | Author's judgment |

## Transition Path

Existing Node.js scripts stay as they are. The position covers new tooling
only, so nothing is rewritten.

## Evidence

| Reference | Kind | Revision | Used for |
|-----------|------|----------|----------|
| TA-001 | Technology assessment | example | Argument step 1 |
