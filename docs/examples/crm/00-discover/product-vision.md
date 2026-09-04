---
ddx:
  id: crm.vision
  authoring:
    home: repo
---

# Product Vision

## Mission Statement

A focused CRM for small B2B sales teams that keeps contact, pipeline, and
activity data in one place so reps spend their day selling instead of
maintaining records.

## Positioning

For small-to-mid-size B2B sales teams (2–25 reps) who today juggle contacts in
spreadsheets, deals in chat threads, and reminders in their inbox, this CRM is
a browser-based sales record-keeping system that gives every rep, manager, and
admin a single shared view of the pipeline. Unlike enterprise CRMs that
require weeks of configuration and a full-time admin, this CRM is usable on
day one with the defaults a typical sales team already follows.

## Vision

A sales team adopts the CRM in an afternoon. Contacts and accounts are
imported from a CSV; reps add notes and log calls as they happen; the manager
runs a weekly pipeline review from the same view their reps see. No one
maintains a parallel "real" spreadsheet because the CRM is faster and more
truthful than the spreadsheet would be.

**North Star**: A sales team can run its weekly pipeline review entirely from
the CRM, with no parallel spreadsheets or hand-collated reports, within one
week of adoption.

## User Experience

Monday morning. A sales rep opens the CRM in the browser. The home view shows
the deals she owns, ordered by next step and close date. She clicks into the
top one, sees the last call note (her own, from Friday), and the email thread
she logged. She updates the next-step date to Thursday, adds a note about
pricing sensitivity, and moves to the next deal.

At 10am her manager opens the same CRM, switches to the team pipeline view,
and sees every rep's open opportunities by stage and value. He spots two deals
without next steps and pings the owning reps in the CRM's activity log.

At noon the CRM admin (a sales ops contractor who works two days a week)
imports a CSV of leads from last week's webinar. She maps the columns,
previews the result, and assigns the leads to reps in round-robin.

Nobody opened a spreadsheet.

## Target Market

| Attribute | Description |
|-----------|-------------|
| Who | Small B2B sales teams (2–25 reps) at companies $1M–$50M revenue, selling considered-purchase products with multi-touch sales cycles |
| Pain | Pipeline state lives in spreadsheets, chat, and inboxes; managers can't see the whole picture; onboarding a new rep means re-explaining the spreadsheet conventions; deals fall through the cracks when reps change |
| Current Solution | Spreadsheets + email + chat; sometimes a heavyweight CRM (Salesforce, HubSpot) that they don't fully use because configuration costs more than the value they extract |
| Why They Switch | Existing tools either require dedicated admin work or leave the team coordinating by hand; this CRM gives them the 80% that matters with the 20% setup |

## Key Value Propositions

| Value Proposition | Customer Benefit |
|-------------------|------------------|
| Opinionated defaults for B2B sales | Usable on day one; no schema design required |
| Single shared pipeline view | Manager and rep see the same data; no reconciliation calls |
| Activity logging built into the daily workflow | Pipeline data stays current because logging is the workflow |
| Browser-based multi-user SaaS | No installs; works on any device the team already uses |
| Simple CSV import/export | Bring data in from spreadsheets; take it out if the team outgrows the tool |

## Success Definition

| Metric | Target |
|--------|--------|
| Time-to-first-value | A new team can run their first pipeline review from the CRM within one week of signup |
| Weekly active reps | ≥ 80% of seats log at least one activity per week (measured 30 days after onboarding) |
| Pipeline freshness | ≥ 90% of open opportunities have a next-step date updated in the last 14 days |
| Adoption depth | ≥ 70% of customer teams use contact, opportunity, *and* activity logging within 30 days |
| Retention | ≥ 85% of teams active in month 3 are still active in month 6 |

## Why Now

Small B2B teams have lived with the same forced choice for a decade:
spreadsheets that drift, or enterprise CRMs that cost more in setup time than
they return in pipeline visibility. Two changes make a focused mid-market CRM
viable now: (1) browser-based SaaS infrastructure has commoditized the
operational layer (auth, hosting, backups) that made standalone CRMs expensive
to ship, and (2) the cost of clean opinionated defaults — one well-designed
sales workflow rather than a configuration framework — has dropped
substantially with modern web stacks. The market opening is the team that's
too big for spreadsheets and too small for Salesforce.

## Review Checklist

- [x] Mission statement is specific — names the user (small B2B sales teams), the problem (data scattered), and the approach (single shared system)
- [x] Positioning statement differentiates from the current alternative (enterprise CRMs and spreadsheets)
- [x] Vision describes a desired end state (team operates from CRM, no parallel spreadsheets), not a feature list
- [x] North star is a single measurable sentence (run weekly pipeline review from the CRM within one week)
- [x] User experience section describes a concrete scenario (Monday morning rep + manager + admin), not abstract benefits
- [x] Target market identifies specific pain points (pipeline state scattered) and switching triggers (existing tools either too heavy or too light)
- [x] Value propositions map to customer benefits, not internal capabilities
- [x] Success metrics are measurable (≥80% WAU, ≥90% freshness, etc.)
- [x] Why Now section names specific changes (SaaS infra commoditization; opinionated-defaults cost drop)
- [x] No implementation details — architecture left to design activity
