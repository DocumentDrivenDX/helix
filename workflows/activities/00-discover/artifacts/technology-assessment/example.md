---
ddx:
  id: TA-001
  type: technology-assessment
  authoring:
    home: repo
  links:
    - {id: component-profile-nodejs-reusable, kind: evaluates, rev: example}
    - {id: component-profile-python-reusable, kind: evaluates, rev: example}
assessment:
  criteria: [script-distribution, text-and-file-handling, dependency-isolation]
  subjects:
    - {id: component-profile-nodejs-reusable, label: Node.js}
    - {id: component-profile-python-reusable, label: Python}
  ratings:
    - {criterion: script-distribution, subject: component-profile-nodejs-reusable, gap: Unknown (not in the brief)}
    - {criterion: script-distribution, subject: component-profile-python-reusable, gap: Unknown (not in the brief)}
    - {criterion: text-and-file-handling, subject: component-profile-nodejs-reusable, finding: Brief section Capabilities}
    - {criterion: text-and-file-handling, subject: component-profile-python-reusable, finding: Brief section Capabilities}
    - {criterion: dependency-isolation, subject: component-profile-nodejs-reusable, finding: Brief section Technology and Operations}
    - {criterion: dependency-isolation, subject: component-profile-python-reusable, finding: Brief section Technology and Operations}
---

# TA-001: Node.js and Python for command-line tooling

## Scope

Compares Node.js and Python as runtimes for repository tooling scripts: file
and text handling, packaging, and distribution of a single script. Excludes
web services and data science workloads.

## Criteria

| Criterion | Definition | Concern |
|-----------|------------|---------|
| Script distribution | How a single script is run on a machine that lacks the runtime's packages | none |
| Text and file handling | Standard-library support for reading, parsing, and writing text files | none |
| Dependency isolation | How a script declares and isolates its own dependencies | none |

## Technologies

- **Node.js**: a JavaScript runtime. Brief: component-profile-nodejs-reusable
- **Python**: a general-purpose language runtime. Brief: component-profile-python-reusable

## Comparison

| Criterion | Node.js | Python |
|-----------|---------|--------|
| Script distribution | Unknown (not in the brief) | Unknown (not in the brief) |
| Text and file handling | Brief section Capabilities | Brief section Capabilities |
| Dependency isolation | Brief section Technology and Operations | Brief section Technology and Operations |

## Findings

On the cited briefs the technologies are comparable for text and file
handling. Script distribution is not covered by either brief, so no finding is
made.

## Contradictions and Gaps

| Item | Sources or gap | Route |
|------|----------------|-------|
| Neither brief covers single-script distribution | Both briefs | Extend each brief, then re-read this criterion |

## Evidence

| Reference | Kind | Revision | Used for |
|-----------|------|----------|----------|
| component-profile-nodejs-reusable | Technology brief | example | Text handling, isolation |
| component-profile-python-reusable | Technology brief | example | Text handling, isolation |
