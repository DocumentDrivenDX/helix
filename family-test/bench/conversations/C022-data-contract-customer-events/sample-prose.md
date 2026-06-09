Helix-data is active, so I'm engaging the 01-contract activity. "Data
contract" for "customer events" maps to the `data-contract` library
type — the artifact that pins event schema, partition keys, and PII
fields before any consumers depend on the shape. I don't see a producer
or consumer named in the workspace yet — who emits these events
(checkout service? billing webhook?) and who consumes them downstream
(warehouse mart, analytics, ops dashboards)? Once I have those, I'll
draft the data-contract; I'd rather ask now than guess the boundaries.
