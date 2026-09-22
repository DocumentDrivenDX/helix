---
ddx:
  id: component-profile
  authoring:
    home: repo
---

# Component Profile: [Component Name]

Desk research on one candidate stack component (a technology, a product, or
a managed provider), consolidated from the public record and measured
against the capabilities this project needs from the role it would fill.
This is research. The choice among candidates lives in an ADR that cites
the profiles; anything the public record cannot settle is a [[tech-spike]].

One instance per candidate. When one decision has several candidates, write
one profile each and let the ADR compare them. Need and Required Capabilities
are shared by every profile for the same decision and are written once,
before any candidate is researched. The factual sections travel between
projects; Scope, Need, Required Capabilities, Capability Alignment, and the
Competitive Landscape do not.

## Scope

- Component: [Name, edition or version line researched]
- Kind: [Technology | Product | Managed provider]
- Would fill: [The role, capability slot, or architectural position it is a candidate for]
- Feeds: [The ADR, spike, or slot decision this profile informs, by id or path]
- Incumbent: [What fills the role today, citing [[current-state-inventory]] where one exists, or *None*]
- Researched: [Date range]
- Excluded: [What this profile deliberately does not cover, and why]

## Summary

Three sentences a brief can lift word for word: the need, the required
capabilities in one clause each, and the verdict with its conditions. Written
last, from the sections below, in the words of a reader outside the project.

[We need a [role] for [use cases] so that [goals]. It must [C1], [C2], and
[C3]. On the public record [component] meets [which], and [which] stay open
pending [what].]

## How to Read This Profile

The vocabularies used below, in one place.

| Word | Where | Means |
|------|-------|-------|
| **Met** | Capability Alignment status | The public record documents the capability as its Required Capabilities row defines it. |
| **Unmet** | Capability Alignment status | The public record contradicts it, or the maker states it is absent. |
| **Unknown** | Capability Alignment status | The record does not settle it; the Open Questions table routes it. |
| **Fit** | Verdict | Every required capability is Met. |
| **Conditional fit** | Verdict | Every required capability is Met or Unknown, and no Unknown is design-defining; each Unknown is an Open Question with a route. |
| **Undetermined** | Verdict | At least one design-defining capability is Unknown; the spike that would settle it is named. |
| **No fit** | Verdict | At least one required capability is Unmet. |
| **Published** | Figures | The maker states it, with source and date. |
| **Third-party estimate** | Figures | Someone other than the maker estimated it; the estimator is named. |
| **Not published** | Figures and claims | Searched and absent; the search is recorded (which pages, which date). |
| **Not researched** | Competitive Landscape cells | Nobody has looked; the sibling profile that would fill the cell is named. |
| **High / Medium / Low** | Confidence | Defined in the Confidence section. |
| **maker / vendor / independent / community** | Sources | Defined in the Sources section. |

## Need

Written before the component is researched, from the project's own
artifacts, in the words a reader outside the project would use: the system
and the role to fill, the use cases it serves, and the goals those use cases
accomplish, each goal cited to its artifact. Then the incumbent and why it no
longer serves. Cite artifacts after the sentence; keep IDs out of the
sentences themselves.

[We need a [role] for [use cases] so that [goals]. The role is filled today
by [incumbent], which [why it no longer serves]. [[product-vision]]
§[section]; [[business-case]] §[section].]

## Required Capabilities

The criteria. One row per capability the role must have, derived from the
Need and the project's artifacts before any candidate is read. Each row says
what evidence in a public record would settle it, so the research has a
target and the reader can check the work. A row cites project artifacts only;
a `[n]` source here means the criteria were written after the research, which
is the failure this order prevents. A capability with no artifact behind it
is a preference and goes under Nice to Have or is dropped.

| # | Capability | Serves | Comes from | Settled by |
|---|------------|--------|------------|------------|
| C1 | [Capability, in one plain sentence] | [Goal from the Need] | [[product-vision]] / [[concerns]] / [[principles]] / ADR-nnn | [The documented fact or independent measurement that would show it: a feature in the maker's docs, a published limit, a licence clause, an audit report] |

Nice to have: [capabilities the project would welcome and no artifact requires, or *None*]

## What It Is

An encyclopedia lead a reader can repeat. First sentence: what the component
is, in its category. Then who makes or governs it, the problem it exists to
solve, and how widely it is used. Then the facts a lead carries: first
release, release cadence and support window, licence in one clause, and the
use cases its own material and independent coverage say it is built for.
Every sentence cites, and a sentence about adoption names the survey and its
population. [n]

- Category and purpose: [n]
- Maker or governing body: [n]
- Adoption, from an independent source, or Not published: [n]
- Release cadence and support window: [n]
- Licence: [n]
- Built-for use cases: [n]

## Capability Alignment

One subsection per required capability, in C-number order. Each states what
the record shows, with the evidence, then closes the "Settled by" plan from
the criteria row and gives the status. Cite at the clause: a version, a
limit, a figure, or a quoted phrase carries its own `[n]`. Mutable facts
(supported versions, regions, prices) carry "as of [date]". When the maker
and independent coverage disagree, record both with dates; the status is
Unknown unless a later maker statement supersedes.

### C1. [Capability]

[What the record shows, two to five sentences, each cited at the clause. Name
the version that introduced the feature, the documented limits and caveats,
and independent coverage of how it behaves in practice, attributed inline
("a 2026 QueryPlane post reports ..."). If a caveat bears on the Need (pooled
connections, a write burst, a region), say so here.] [n]

**Settled by**: [the criteria row's evidence] found in [n] / not found (searched [pages], [date])
**Status**: Met | Unmet | Unknown

Other notable capabilities the record documents and no criterion requires:

| Capability | What the record says | Source |
|------------|----------------------|--------|
| [Capability] | [Specific, checkable statement] | [n] |
| [Capability] | Not published (searched [n], [date]) | none |

**Verdict**: [Fit | Conditional fit | No fit | Undetermined]. [One sentence
naming the conditions or the deciding gap, using the definitions in How to
Read This Profile.]

## Technology and Operations

| Aspect | What the record says | Source |
|--------|----------------------|--------|
| Hosting model | [Self-hosted, managed, or both; regions, as of date] | [n] |
| Integrations | [Protocols, ecosystems and clients that matter for the role] | [n] |
| Data handling | [Residency, encryption, retention, whether customer data trains models] | [n] |
| Certifications | [SOC 2, ISO 27001, HIPAA and the like, as published, with date; or Not published (searched [n], [date])] | [n] |
| Maturity and cadence | [First release, release cadence, support window] | [n] |
| Governance | [Who controls the roadmap: single vendor, foundation, community] | [n] |
| Security process | [Disclosure policy, CVE handling, patch cadence] | [n] |

## Pricing and Licensing

Label every figure. Never infer a price.

| Item | Figure | Label | Source |
|------|--------|-------|--------|
| Licence | [Licence name and what it permits] | Published | [n] |
| [Tier or unit] | [Figure, as of date] | Published / Third-party estimate / Not published (searched [n], [date]) | [n] |

## Competitive Landscape

The alternatives a reader will ask about, scored on the same required
capabilities. One column per capability, one row per alternative, the
candidate itself in the first row. A cell the record fills gets the finding
and its source, from that alternative's own record. A cell nobody has
researched says **Not researched** and the Profile column names the sibling
profile that would fill it. For a managed service running the same software,
a capability the software supplies is "Inherits [n]" with the provider's
page that says which software it runs.

| Candidate | C1 | C2 | C3 | ... | Profile |
|-----------|----|----|----|-----|---------|
| [This component] | Met [n] | ... | | | this profile |
| [Alternative] | [Finding] [n] / Not researched | ... | | | [[component-profile-name]] or *none yet* |

Below the table, one line per alternative: the shared ground and the
divergence this project cares about. [n]

## Confidence

One grade for the profile:

| Grade | Means |
|-------|-------|
| **High** | Every design-defining claim is corroborated by the maker's material *and* at least one independent source, and no design-defining capability is Unknown. |
| **Medium** | Design-defining claims rest on the maker alone, or a design-defining capability is Unknown, or the independent coverage is older than two major versions. |
| **Low** | Thin public footprint; claims rest on one source or on none. |

**Grade**: [High | Medium | Low]. [Which claims are corroborated, which rest
on the maker alone, and which have no source. Name the weakest area.]

## Open Questions

What the public record cannot answer. Each is a spike candidate, a question
for the maker, a call for operator guidance, or a sibling profile's job. An
open question carries no owner, date, duration, or figure that a project
artifact does not state; a scale the project has not set is written as "the
project's tenant count", not as a number.

| # | Question | Design-defining because | Route |
|---|----------|-------------------------|-------|
| 1 | [Question] | [Which decision turns on it] | [[tech-spike]] / ask maker / operator guidance / [[component-profile-name]] |

## Sources

Numbered; cited by number above. Each carries its class, its author or
organisation, its publication or update date when the page shows one, and
the date accessed. For the scoped version, cite the versioned documentation
URL (`/docs/18/`, not `/docs/current/`). Classes:

- **maker**: the component's maker or governing body
- **vendor**: a company that sells hosting or support for the component or a rival
- **independent**: no commercial interest in the component; a named author or organisation and a date
- **community**: a project or forum around the component

A source with no named author or organisation and no date supports a
descriptive claim only, never a design-defining one.

1. [Title](URL), class, author or organisation, published [date], accessed [date]

**Searched**: [the search strings and pages consulted, and which Not
published or Not researched cells each produced]

## Review Checklist

Ticked by a named reviewer, recorded on the line; an author ticking their own
boxes is a draft.

Reviewed by: [name and role from a project artifact, or *unreviewed*]

- [ ] Need and Required Capabilities cite project artifacts only; no `[n]` appears in them
- [ ] Every required capability has a "Settled by" line and a status from How to Read This Profile
- [ ] Every claim cites at the clause or is marked Not published (with the search) or Not researched (with the sibling profile)
- [ ] Every figure carries a label, and every mutable fact an as-of date
- [ ] The verdict follows the definitions in How to Read This Profile
- [ ] The Competitive Landscape scores every named alternative on the same capabilities
- [ ] The confidence grade follows the rubric; a design-defining Unknown caps it at Medium
- [ ] Every source carries class, author or organisation, publication date where shown, and access date; scoped-version docs are version-pinned
- [ ] No benchmark, prototype, or integration result is claimed
- [ ] No owner, date, duration, or figure appears that a project artifact does not state
- [ ] No choice among candidates is made here
