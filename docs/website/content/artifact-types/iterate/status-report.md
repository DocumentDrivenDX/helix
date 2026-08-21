---
title: "Status Report"
linkTitle: "Status Report"
slug: status-report
activity: "Iterate"
artifactRole: "supporting"
weight: 90
generated: true
---

## Purpose

Status Report is the **iteration record** of the iterate loop. Its unique job
is to report each committed outcome's status against the iteration plan's
IDs, with evidence per claim, the trades executed under the plan's trade
rules, the blockers and the decisions they need, and next steps.

It is a point-in-time record, not a live surface. The runtime tracker owns
minute-to-minute status; the report freezes an honest snapshot for the
review, the checkpoint, or the stakeholder update.

## Example

<details open>
<summary>Show a worked example of this artifact</summary>

``````markdown
---
ddx:
  id: example.status-report.depositmatch
  depends_on:
    - example.iteration-plan.depositmatch
---

# Status Report

| | |
|---|---|
| **Iteration** | IT-05 |
| **As Of** | Fri 12 Jun 2026 |
| **Kind** | Iteration review |
| **Audience** | Team + pilot-bank operations lead |
| **Plan** | iteration-plan-IT-05.md |

## Summary

> The iteration goal landed: a real anonymized pilot export imports with
> validated rows and actionable errors, demoed live. The Best and Better
> outcomes were traded per the plan's rules to protect it. The anonymization
> field-list question needs a decision before IT-06 planning.

## Outcome Status

| ID | Workstream | Tier | Outcome | Status | Evidence |
|----|------------|------|---------|--------|----------|
| WS-1-good | WS-1 | 🟢 Good | A real anonymized pilot export imports with validated rows | done | Three anonymized fixtures committed under `fixtures/pilot/`; US-003 test suite green (14 tests, each citing its AC); live demo at review |
| WS-1-better | WS-1 | 🔵 Better | Upload p95 latency watch item on pilot dashboard | dropped | Traded 9 Jun per trade rules to protect WS-1-good after error-class count doubled |
| WS-1-best | WS-1 | 🟣 Best | Per-row error messages include remediation hints | dropped | First drop under trade rules, 4 Jun |

## Changes and Trades

- WS-1-best dropped 4 Jun, WS-1-better dropped 9 Jun — both per the plan's
  trade order (Best first, then Better), called by the Delivery Lead. No
  Good-tier escalations.

## Blockers and Risks

| Blocker / Risk | Outcome Affected | Needs | Owner |
|----------------|------------------|-------|-------|
| Anonymization strips two fields matching may depend on | IT-06 roadmap slot | Operations lead to confirm field list by 16 Jun | Priya |

## Next Steps

- File WS-1-better (latency watch) back into the improvement backlog → Priya → 15 Jun
- Confirm anonymization field list with operations lead → Priya → 16 Jun
- Cut IT-06 iteration plan from roadmap order 2 → Delivery Lead → 15 Jun

## Review Checklist

- [x] Every row traces to an iteration-plan outcome ID
- [x] Every done or at-risk claim cites evidence — no phantom claims
- [x] Trades reference the plan's trade rules or name their approver
- [x] Decisions needed name their decider
``````

</details>

## Reference

<table class="helix-reference-table">
<tbody>
<tr><th>Activity</th><td><a href="../../../reference/glossary/activities/"><strong>Iterate</strong></a> — Measure, align, and improve. Close the feedback loop back into the planning strand.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/06-iterate/status-report-[iteration-id]-[date].md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Informs</th><td><a href="../../../artifact-types/iterate/improvement-backlog/">Improvement Backlog</a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Status Report Generation Prompt&#10;&#10;Record how an iteration stands against its plan.&#10;&#10;## Purpose&#10;&#10;Status Report is the **iteration record** of the iterate loop. Its unique job&#10;is to report each committed outcome&#x27;s status against the iteration plan&#x27;s&#10;IDs, with evidence per claim, the trades executed under the plan&#x27;s trade&#10;rules, the blockers and the decisions they need, and next steps.&#10;&#10;It is a point-in-time record, not a live surface. The runtime tracker owns&#10;minute-to-minute status; the report freezes an honest snapshot for the&#10;review, the checkpoint, or the stakeholder update.&#10;&#10;## Focus&#10;&#10;- Author a report only when it has an audience — a review, a client&#10;  checkpoint, a stakeholder update. The tracker already shows live status;&#10;  a report nobody reads is ceremony.&#10;- Report against the plan&#x27;s outcome IDs — never introduce outcomes the plan&#10;  does not carry; a new outcome is a plan change first.&#10;- Claims-vs-reality applies to every status, not just done: done and at-risk&#10;  cite the proof or the threat (demo, test, commit, metric), on-track cites&#10;  the observable progress so far, dropped cites the trade or escalation. An&#10;  evidence-free claim is a phantom claim and blocks.&#10;- Record trades explicitly. A dropped Best or Better per the trade rules is&#10;  a one-line entry; a Good at risk is an escalation that names its decider —&#10;  Good outcomes are never traded.&#10;- Route review learnings onward: findings that should compete for future&#10;  attention belong in the improvement backlog, not in the report&#x27;s tail.&#10;- Write for the named audience; a client-facing report may subset the&#10;  outcomes but never contradict the internal one.&#10;- Tier labels carry over from the plan&#x27;s convention: emoji plus a&#10;  non-breaking space (U+00A0) plus the word — 🟢 Good, 🔵 Better, 🟣 Best.&#10;&#10;## Boundary Test&#10;&#10;| If you are writing... | Put it in... |&#10;|---|---|&#10;| One iteration&#x27;s committed outcomes, owners, and dates | Iteration Plan |&#10;| Live task status, assignees, execution history | runtime work item or issue |&#10;| Point-in-time outcome status with evidence | Status Report |&#10;| Measurement interpretation for the iteration | Metrics Dashboard |&#10;| Prioritized follow-up candidates from learnings | Improvement Backlog |&#10;&#10;## Completion Criteria&#10;&#10;- Every outcome row traces to a plan ID.&#10;- Every done or at-risk claim cites evidence.&#10;- Trades reference the plan&#x27;s rules or name their approver.&#10;- Every needed decision names its decider.</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---&#10;ddx:&#10;  id: status-report&#10;---&#10;&#10;# Status Report&#10;&#10;| | |&#10;|---|---|&#10;| **Iteration** | [id — matches the iteration plan] |&#10;| **As Of** | [date] |&#10;| **Kind** | [mid-iteration checkpoint / iteration review] |&#10;| **Audience** | [team / client / stakeholders] |&#10;| **Plan** | [link to the governing iteration plan] |&#10;&#10;## Summary&#10;&#10;&gt; [Three sentences max: is the goal on track, what changed, what needs a&#10;&gt; decision.]&#10;&#10;## Outcome Status&#10;&#10;Tier labels carry over from the plan: emoji plus a non-breaking space&#10;(U+00A0) — 🟢 Good · 🔵 Better · 🟣 Best.&#10;&#10;| ID | Workstream | Tier | Outcome | Status | Evidence |&#10;|----|------------|------|---------|--------|----------|&#10;| [WS-1-good] | [WS-1] | 🟢 Good | [outcome from the plan] | [on-track / at-risk / done / dropped] | [every status cites evidence: done/at-risk cite the proof or the threat (demo, test, commit, metric); on-track cites the observable progress so far; dropped cites the trade or escalation] |&#10;&#10;## Changes and Trades&#10;&#10;- [Trade executed per the plan&#x27;s trade rules, or scope change with who&#10;  approved it — &quot;none&quot; is a valid entry]&#10;&#10;## Blockers and Risks&#10;&#10;| Blocker / Risk | Outcome Affected | Needs | Owner |&#10;|----------------|------------------|-------|-------|&#10;| [blocker] | [ID] | [decision or dependency required] | [name] |&#10;&#10;## Next Steps&#10;&#10;- [Action → owner → date]&#10;&#10;## Review Checklist&#10;&#10;- [ ] Every row traces to an iteration-plan outcome ID&#10;- [ ] Every done or at-risk claim cites evidence — no phantom claims&#10;- [ ] Trades reference the plan&#x27;s trade rules or name their approver&#10;- [ ] Decisions needed name their decider</code></pre></details></td></tr>
</tbody>
</table>
