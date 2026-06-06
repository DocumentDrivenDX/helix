Helix-data is active, so I'm engaging the 03-validate activity for the
orders pipeline. Quality checks for orders fall into two artifacts:
`data-quality-expectations` (the rules the data must satisfy) and
`data-quality-tests` (the executable assertions that prove it). For an
orders pipeline I'd start with EXPECT-style rules — `order_id` not-null
and unique, `total_cents` > 0, `currency` in ISO-4217, `created_at`
within freshness SLA (e.g. < 1h lag), and referential integrity against
the customers contract. Want me to draft the expectations first so you
can sign off on the rule set before I author the executable tests?
