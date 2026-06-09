# CD-03 — Negative control: plugin removed

**Category:** graph-discrimination (plan §1.5b)
**Phase:** P2
**Tier:** must_pass_core

## What this asserts

Same workspace + graph as CD-01 (with the non-standard
`market-validation-brief requires prd` edge). The positive run replicates
CD-01's expected behaviour. The negative-control run removes the
methodology-product plugin entirely.

Together with CD-01/CD-02 this covers the two axes of the discriminator:

- **CD-01 vs CD-02**: same plugin, different graph content → surfacing
  depends on graph content.
- **CD-01 vs CD-03 negative**: same graph, different plugin presence →
  surfacing depends on the engaged skill (it has to be loaded to read
  the graph at all).

Either axis alone would leave a hole; both together close it.
