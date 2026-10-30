---
ddx:
  id: example.user-journey-map.depositmatch.import-weekly-files
  authoring:
    home: repo
  depends_on:
    - example.feature-specification.depositmatch.csv-import
    - example.user-story.depositmatch.upload-csv
---

# UJM-001: Import a Client's Weekly Files

**Feature**: [[FEAT-001]] CSV Import and Column Mapping | **Map kind**: future-state | **Evidence**: research plan `pilot-reviewer-interviews` (6 interviews), pilot support tickets

## Actor and Scenario

- **Person**: Reconciliation lead. Reconciles 12 to 20 clients a week on a desktop; knows each client's books, not their export formats.
- **Task**: Import a client's weekly files (FEAT-001 Task Model).
- **Scenario**: Monday's bank and invoice exports for Acme Dental arrive by email. Maya brings them into DepositMatch, checks the columns and the rejected rows, and confirms the import so matching can start.
- **Trigger**: The client's weekly exports arrive.
- **End state**: The import is confirmed and match suggestions are ready, or Maya knows exactly what to ask the client to fix.

### Goals and Expectations

- Finish each client's import in under five minutes.
- Never let a wrong column produce plausible-looking matches.
- Know before matching which rows were left out and why.

## Journey Phases

| Phase | Actions | Thoughts | Emotion | Touchpoints | Stories / ACs |
|---|---|---|---|---|---|
| Receive | Saves the two attachments from the client's email | "Same format as last week, I hope." | neutral: routine | Email (outside the product) | uncovered: happens outside DepositMatch |
| Upload | Starts a new import and attaches both files | "Did it take both?" | neutral: brisk | upload | US-001-AC1, US-001-AC2 |
| Check columns | Confirms the saved mapping, fixes one renamed column | "If amount is wrong, every match is wrong." | negative: wary | mapping review | US-002-AC1, US-002-AC2 |
| Review rejections | Reads why 14 rows were rejected | "Are these mine to fix or the client's?" | negative: unsure | validation results | US-003-AC1 |
| Confirm | Confirms the import and moves to matching | "Good, that's done." | positive: relieved | import summary | US-003-AC2 |
| Follow up | Emails the client about the rejected rows | "They'll want the row numbers." (assumption) | neutral | Email (outside the product) | uncovered: no story exports the rejected rows |

## Insights

| Insight | Phase | Evidence |
|---|---|---|
| A renamed column is the most common reason an import goes wrong | Check columns | 4 of 6 interviews; 9 pilot support tickets |
| Reviewers copy rejected rows by hand into an email to the client | Follow up | 5 of 6 interviews |

## Opportunities

| Opportunity | Phase | Owner | Metric | Target |
|---|---|---|---|---|
| Flag a saved mapping whose column was renamed, before the reviewer confirms | Check columns | Import squad | Imports corrected after confirmation | hypothesis: under 1% |
| Export rejected rows with their row numbers and reasons | Follow up | Product | Median time from summary to client email | hypothesis: under 2 minutes |

## Story Coverage

| Phase | Covered by | Gap |
|---|---|---|
| Upload to Confirm | US-001, US-002, US-003 | None |
| Follow up | none | No story exports the rejected rows |
