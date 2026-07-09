---
ddx:
  id: example.data-flow-analysis.depositmatch
---

# Data Flow Analysis

## Flow Summary

- Process name: Manual Deposit-to-Invoice Reconciliation
- Frequency: Weekly, every Friday
- Current state: Manual
- Business value: Ensures each client's bank deposits are matched to the
  correct outstanding invoice so the firm's books close accurately and real
  collection gaps get followed up on, instead of drifting unnoticed.

## Actors

| Actor | Type | Role in This Flow |
|-------|------|--------------------|
| Bookkeeper | Person | Downloads exports, matches deposits to invoices, resolves exceptions, updates invoice status |
| Client contact | Person | Occasionally emails to clarify an ambiguous or split deposit |
| Bank export job | Automated System | Nightly job that refreshes the bank portal's downloadable deposit CSV |

## Sources and Sinks

| Direction | System or Location | What It Provides or Receives |
|-----------|---------------------|-------------------------------|
| Source | Bank portal CSV export | Weekly list of incoming deposits (date, amount, payer reference, memo) |
| Source | Accounting platform invoice export | Outstanding invoices per client (invoice ID, amount due, due date) |
| Sink | Shared reconciliation spreadsheet | Master record of which deposit matched which invoice, and reviewer notes |
| Sink | Accounting platform invoice status field | Manually flipped to "Paid" for confirmed matches |

## Data and Data Structures

| Name | Format | Direction | Key Fields / Schema Notes |
|------|--------|-----------|-----------------------------|
| `bank_deposits.csv` | File (CSV) | Input | `date`, `amount`, `payer_ref`, `memo`; column order has changed without notice when the bank updated its export tool |
| `invoices_export.xlsx` | File (Excel) | Input | `invoice_id`, `client_id`, `amount_due`, `due_date` |
| `reconciliation-tracker.xlsx` | Spreadsheet | Output | One row per deposit: `deposit_id`, `matched_invoice_id`, `status`, `reviewer`, `notes`; layout differs per client, no canonical template |
| Invoice status field | UI field (accounting platform) | Output | Free-text-adjacent status dropdown, flipped manually per confirmed match |

## Transformations

| Step | What Happens | Performed By |
|------|---------------|--------------|
| 1 | Download the weekly bank CSV from the portal | Bookkeeper |
| 2 | Export the outstanding invoice list from the accounting platform | Bookkeeper |
| 3 | Compare deposit amount and payer name against open invoices to guess a match, then record it in the tracker spreadsheet | Bookkeeper |
| 4 | Flag ambiguous deposits (partial payments, multiple candidate invoices) in a "Needs Review" tab | Bookkeeper |
| 5 | For each confirmed match, manually set the invoice status to "Paid" in the accounting platform | Bookkeeper |

## Constraints

| Constraint | Detail |
|------------|--------|
| Format | Bank CSV column order is not contractually stable; it has silently broken spreadsheet formulas before |
| Timing | Must finish by Friday close-of-business so weekend ACH deposits don't roll into the next batch and confuse the count |
| Volume | 50-200 deposits per week per client at pilot-scale firms |
| Access | Bookkeeper needs manual read access to both the bank portal and the accounting platform; neither exposes an API today |

## Scale and Complexity

| Dimension | Assessment |
|-----------|------------|
| Manual steps | 5, all performed by one person |
| Systems touched | 3 (bank portal, accounting platform, spreadsheet) |
| Overall complexity | Medium — the per-deposit logic is simple, but volume and exception handling make it slow and error-prone |

## Risks, Assumptions, and Modernization Notes

- **Risks**: Matches are eyeballed with no audit trail of who decided what
  or why; a silent bank CSV schema change breaks spreadsheet formulas without
  warning; nothing prevents the same deposit from being matched twice.
- **Assumptions**: The bank CSV export format is stable enough to script
  against for an initial migration pass; the accounting platform will
  eventually expose an API instead of requiring a manual status flip.
- **Modernization Recommendations**: Replace manual matching with
  DepositMatch's suggested-match review queue (see
  [[product-vision]]); keep a human in the loop for exceptions, but replace
  free-form spreadsheet editing with a reviewable, audited decision log.

## Notes

Each client's spreadsheet layout is slightly different because bookkeepers
customized their own copies over time — there is no single canonical
template in use today, which will complicate any bulk import during
migration.

## Cross-References

- [[data-design]] — Design-phase target-state entity model this analysis may
  inform once a future solution is chosen.
