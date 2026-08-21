---
ddx:
  id: roadmap
---

# Roadmap

**Scope**: [product or program this roadmap sequences]
**Owner**: [role]
**Last Revised**: [date — and which revision trigger fired]

## Horizon and Cadence

- **Horizon**: [how far ahead this roadmap commits — e.g. 3 iterations, 2 quarters]
- **Cadence**: [iteration length and review rhythm]
- **Beyond the horizon**: [where unsequenced candidates live — improvement backlog, parking lot]

## Workstreams

Workstreams are the stable cross-iteration groupings of work. The alias is
the identifier: `WS-<n>`, assigned sequentially, never reused or renumbered —
a closed workstream keeps its alias. Iteration plans and runtime work items
reference workstreams by alias; they never mint new ones.

| Alias | Workstream | Scope | Owner | Status |
|-------|------------|-------|-------|--------|
| [WS-1] | [name] | [one line: what belongs in it and what does not] | [name] | [active/closed] |

## Sequenced Outcomes

| Order | Outcome | Workstream | Governing Artifact | Target Iteration | Depends On | Confidence | Why This Order |
|-------|---------|------------|--------------------|------------------|------------|------------|----------------|
| 1 | [outcome] | [WS-1] | [PRD R-n / FEAT-nnn / backlog item] | [iteration id] | [dependency or None] | [high/med/low] | [dependency, risk, or value rationale] |
| 2 | [outcome] | [WS-1] | [ref] | [iteration id] | [1] | [high/med/low] | [rationale] |

## Revision Triggers

- [Event that forces a re-sequence — e.g. a go/no-go finding, a slipped dependency, a backlog re-rank]
- [What stays stable across revisions — e.g. the active iteration's committed outcomes]

## Review Checklist

- [ ] Every workstream has a stable `WS-<n>` alias, a scope line, and an owner
- [ ] Every outcome cites its workstream and its governing artifact
- [ ] Ordering states its rationale
- [ ] The horizon is explicit; nothing beyond it is committed
- [ ] Current-iteration outcomes match the active iteration plan
