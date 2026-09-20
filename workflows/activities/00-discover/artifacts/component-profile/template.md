---
ddx:
  id: component-profile
  authoring:
    home: repo
---

# Component Profile: [Component Name]

Desk research on one candidate stack component — a technology, a product, or a
managed provider — consolidated from the public record and measured against
this project's vision, concerns and open decisions. **This is research, not a
decision and not an experiment.** The choice among candidates lives in an ADR
that cites the profiles; anything the public record cannot settle is a
[[tech-spike]].

One instance per candidate. When one decision has several candidates, write
one profile each and let the ADR compare them. The factual sections travel
between projects; Scope and Fit Assessment do not — a project reusing another
project's profile rewrites both and re-dates every source.

## Scope

- Component: [Name, edition or version line researched]
- Kind: [Technology | Product | Managed provider]
- Would fill: [The capability, concern slot or architectural role it is a candidate for]
- Feeds: [The ADR, spike or slot decision this profile informs, by id or path]
- Incumbent: [What fills the role today, citing [[current-state-inventory]] where one exists, or *None*]
- Researched: [Date range]
- Excluded: [What this profile deliberately does not cover, and why]

## What It Is

[Two or three sentences a reader can repeat: what the component is, who makes
or maintains it, and the problem it exists to solve. [n]]

Use cases it is built for, per its own material and independent coverage:

- [Use case] [n]

## Capabilities

Features that bear on the role it would fill. Omit the marketing list; keep
what the Fit Assessment will need.

| Capability | What the record says | Source |
|------------|----------------------|--------|
| [Capability] | [Specific, checkable statement] | [n] |
| [Capability] | Not published | — |

## Technology and Operations

| Aspect | What the record says | Source |
|--------|----------------------|--------|
| Hosting model | [Self-hosted, managed, or both; regions] | [n] |
| Integrations | [Protocols, ecosystems and clients that matter for the role] | [n] |
| Data handling | [Residency, encryption, retention, whether customer data trains models] | [n] |
| Certifications | [SOC 2, ISO 27001, HIPAA and the like — as published, with date] | [n] |
| Maturity and cadence | [First release, release cadence, support window] | [n] |
| Governance | [Who controls the roadmap: single vendor, foundation, community] | [n] |

## Pricing and Licensing

Label every figure. **Published** means the maker states it, with source and
date. **Third-party estimate** names who estimated. Otherwise write **Not
published** — never infer a price.

| Item | Figure | Label | Source |
|------|--------|-------|--------|
| Licence | [Licence name and what it permits] | Published | [n] |
| [Tier or unit] | [Figure] | Published / Third-party estimate / Not published | [n] |

## Positioning

The adjacent candidates a reader will ask about, and where this component
overlaps with or diverges from each. Link sibling profiles where they exist.

| Adjacent candidate | Overlap | Divergence that matters here | Profile |
|--------------------|---------|------------------------------|---------|
| [Name] | [Shared ground] | [The difference this project cares about] | [[component-profile-name]] or *none yet* |

## Fit Assessment

Measured against **this project's** artifacts, read before this section was
written. Name each one. A row with no named artifact is an opinion, not a fit.

Verdict vocabulary:

| Verdict | Means |
|---------|-------|
| **Fit** | Every named requirement is met on the public record. |
| **Conditional fit** | Fit if the named conditions hold; each condition is an open question or a spike. |
| **No fit** | A named requirement is contradicted on the public record. |
| **Undetermined** | The public record cannot settle a design-defining requirement; the spike that would is named. |

| Requirement or concern | From | What the record shows | Fit | Source |
|------------------------|------|-----------------------|-----|--------|
| [Requirement] | [[product-vision]] / [[concerns]] / [[principles]] / ADR-nnn | [Specific finding] | Met / Unmet / Unknown | [n] |

**Verdict**: [Fit | Conditional fit | No fit | Undetermined] — [one sentence
naming the conditions or the deciding gap].

## Confidence

One grade for the profile, from this rubric:

| Grade | Means |
|-------|-------|
| **High** | Design-defining claims corroborated by the maker's material *and* at least one independent source. |
| **Medium** | Maker's material, with thin or dated independent coverage. |
| **Low** | Thin public footprint; claims rest on one source or on none. |

**Grade**: [High | Medium | Low]. [Which claims are corroborated, which rest
on the maker alone, and which have no source. Name the weakest area.]

## Sources

Numbered; cited by number above. Each carries the date accessed.

1. [Title](URL) — [maker material | independent | community], accessed [date]

## Open Questions

What the public record cannot answer. Each is a spike candidate, a question for
the maker, or a call for operator guidance — never an assumption carried into
the ADR.

| # | Question | Design-defining because | Route |
|---|----------|-------------------------|-------|
| 1 | [Question] | [Which decision turns on it] | [[tech-spike]] / ask maker / operator guidance |

## Review Checklist

- [ ] Every factual claim cites a numbered source or is marked Not published / Third-party estimate
- [ ] Every figure is labelled Published, Third-party estimate or Not published
- [ ] Every fit row names the project artifact or decision it is measured against
- [ ] Fit Assessment closes with exactly one verdict from the declared vocabulary
- [ ] Confidence grade is justified by naming corroborating and missing sources
- [ ] Every source carries an access date
- [ ] No benchmark, prototype or integration result is claimed
- [ ] No choice among candidates is made here
