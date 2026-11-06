---
ddx:
  id: DB-[number]
  type: decision-brief
  status: draft
  authoring:
    home: repo
  links:
    # - {rel: evaluates, target: <technology brief or component profile id>, rev: <pinned revision>}
    # - {rel: addresses, target: <concern id>}
    # - {rel: supported_by, target: <source id>, rev: <pinned revision>}
---

# DB-[number]: [Decision as a question]

## Context

The situation the decision is made in, and what bounds it. Name the
requirements, approved decisions, and concerns that apply, each by id or
path, and the constraints that are fixed. Say what is out of scope,
including any decision that can vary independently of this one.

| Bound | Source | Effect on the choice |
|-------|--------|----------------------|
| [Requirement, decision, concern, or constraint] | [id or path] | [How it narrows the options] |

## Decision

The one decision to be made, as a sentence a reviewer can answer yes or no
to or choose among options for, and who decides.

## Options

Every option, including the status quo. One paragraph each: what it is and
the briefs or profiles it rests on.

- **[Option A]**: [what it is]. Evidence: [reference, pinned revision]
- **[Option B]**: [what it is]. Evidence: [reference, pinned revision]

## Evaluation

All options against the same criteria, drawn from Context. Each cell cites
evidence or says Unknown.

| Criterion | [Option A] | [Option B] |
|-----------|------------|------------|
| [Criterion from Context] | [Finding, source] | [Finding, source] |

[Two to four sentences on what separates the options for this context.]

## Recommendation

**Recommendation**: [Option] for [this context], on these conditions: [the
conditions]. [One to three sentences on why it fits this context better than
the strongest alternative.]

What would change it: [the evidence or change in context that would reverse
the recommendation].

## Risks and Unknowns

| Risk or unknown | Bears on | Route |
|-----------------|----------|-------|
| [Risk or open question] | [Criterion or option] | [Spike, owner decision, or accepted] |

## Evidence

Each reference this brief relies on, with the revision it was read at.

| Reference | Kind | Revision | Used for |
|-----------|------|----------|----------|
| [Technology brief, profile, source] | [kind] | [revision or digest] | [criterion or option] |
