# CD-04 — Robustness variant: different non-standard edge

**Category:** graph-discrimination (plan §1.5b)
**Phase:** P2
**Tier:** must_pass_core

## What this asserts

CD-01 declares `market-validation-brief requires prd`. CD-04 declares a
different non-standard edge — `regulatory-impact-assessment requires prd` —
in a regulated-healthcare pretext workspace.

If the skill passed CD-01 by memorising the phrase "market-validation-brief"
rather than by *consulting the graph*, CD-04 catches that defect: the
edge is different, the workspace is different, but the discipline is the
same. A row that passes CD-01 and fails CD-04 is evidence of phrase
memorisation, not graph-consultation behaviour.

Paired with the same kind of `graph_swap` negative control as CD-01:
remove the edge from the graph and the surfacing must disappear.
