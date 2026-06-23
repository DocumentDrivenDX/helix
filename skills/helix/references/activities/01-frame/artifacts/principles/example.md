---
ddx:
  id: example.principles.depositmatch
  depends_on:
    - example.product-vision.depositmatch
    - example.prd.depositmatch
  review:
    self_hash: bb37a1addd5c152f068dd5c416b6a4ae217847242d0d1b7f9e64406b671de0ed
    deps:
      example.prd.depositmatch: c9c24e1694af4548a6deaad8d92059e365da110148bd9adc44d8640dff9770a4
      example.product-vision.depositmatch: 8abbb2fcb552b536f07829f57d91ef3ae8dbf52a6066955222e83d196b59b5ae
    reviewed_at: "2026-05-15T04:11:24Z"
---

# Project Principles

These principles guide DepositMatch decisions when the Product Vision and PRD
do not prescribe an exact answer. They are not product requirements, concerns,
ADRs, workflow rules, or process enforcement.

## Principles

1. **Trust beats automation.** Prefer reviewable suggestions over invisible
   automation when the two conflict. This changes decisions when a faster match
   flow would hide evidence from the reviewer.

2. **Exceptions are first-class work.** Prefer an owned exception over an
   unresolved deposit that sits outside the product. This changes decisions
   when an edge case could be deferred to a spreadsheet or email thread.

3. **Reviewer speed comes from preserved context.** Prefer workflows that keep
   deposits, invoices, evidence, and decisions together over workflows that
   minimize screen count. This changes decisions when a shorter path would make
   the reviewer rebuild context later.

4. **Start with CSV reality.** Prefer robust import and column-mapping behavior
   over early accounting-platform integrations. This changes decisions when
   integration work competes with making pilot firms successful on exported
   data.

5. **Auditability is part of usability.** Prefer visible history and correction
   paths over destructive edits. This changes decisions when a direct edit would
   be simpler but would weaken month-end review.

## Tension Resolution

| When these pull against each other | Resolve by |
|---|---|
| **Trust beats automation** vs. **Reviewer speed comes from preserved context** | Show enough evidence for confident review before optimizing batch speed. Speed that reduces trust will not survive pilot use. |
| **Start with CSV reality** vs. **Reviewer speed comes from preserved context** | Make CSV import dependable first, then improve the review surface with the context those imports provide. |
| **Exceptions are first-class work** vs. **Auditability is part of usability** | Treat exception assignment, status changes, and follow-up notes as auditable decisions, not lightweight comments. |

## Size Guidance

Keep this file focused on choices the team expects to make repeatedly. If a
principle becomes a product behavior, move it into the PRD or a feature spec. If
it becomes a technology decision, move it into Concerns or an ADR.
