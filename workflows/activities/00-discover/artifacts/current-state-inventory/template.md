---
ddx:
  id: current-state-inventory
  authoring:
    home: repo
---

# Current-State Inventory: [Estate or Domain Name]

Register of what the organization already has, each entry graded for evidence.
Captured during Discover to ground architecture and modernization decisions in
the estate as it is. **This is a survey, not a target.** Target state,
recommendations and decisions belong in [[architecture]] and its ADRs.

One instance covers one estate or domain. A large organization produces
several — by business unit, by platform, or by capability area.

## Scope and Boundary

- Estate: [What this inventory covers]
- Surveyed: [Date range the evidence was gathered]
- Excluded: [What is deliberately out of scope, and why]
- Owner: [Who maintains this inventory]

## Evidence Grades

Every entry carries exactly one grade. State the vocabulary here so a reader
knows what each grade licenses them to claim.

| Grade | Means |
|-------|-------|
| **Evidenced** | A named source attests it exists and works this way. Cited, with a date. |
| **Partial** | It exists, but a design-defining fact about it is unrecorded. |
| **Assumed** | Claimed — on a slide, in conversation — with no source. It may be real; we cannot say so. |
| **Aspirational** | Target state. It does not exist today, and this entry does not claim it does. |
| **Spike-open** | A design-defining fact is assumed *and* blocks a decision. Name the decision it blocks. |

An entry graded **Evidenced** with no citation is **Assumed**. Grade honestly:
an inventory that flatters the estate is worse than no inventory, because it
is trusted.

## Inventory

Group by whatever structure the estate actually has — capability, layer,
owning function, vendor. Keep one grouping scheme for the whole instance.

### [Group name]

| Component | Supplier / incumbent | Grade | Evidence |
|-----------|----------------------|-------|----------|
| [Name] | [Who provides it, or *No incumbent*] | [Grade] | [Named source and date, or what is missing] |

## Totals

Tally from the inventory above **in this revision**. Never carry totals
forward from a previous one — a stale total is a false claim about how much
is known.

| Grade | Count | Share |
|-------|-------|-------|
| Evidenced | [n] | [%] |
| Partial | [n] | [%] |
| Aspirational | [n] | [%] |
| Assumed | [n] | [%] |
| Spike-open | [n] | [%] |

**[n] of [total] entries have no evidence they exist** — the Assumed and
Aspirational rows. State this plainly; do not leave the reader to count.

## Open Questions

| # | Question | Blocks | Owner |
|---|----------|--------|-------|
| 1 | [What is unknown about a component, stated as a question] | [What the answer unblocks] | [Named person] |

## Review Checklist

- [ ] Every entry carries exactly one grade from the declared vocabulary
- [ ] Every Evidenced entry names a source and a date
- [ ] Totals are tallied from this revision, not carried forward
- [ ] The unevidenced share is stated, not implied
- [ ] Scope and exclusions are both stated
- [ ] No target state, recommendation or decision has crept in
