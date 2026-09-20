# Component Profile Generation Prompt

Consolidate what is publicly known about one candidate stack component, cite
every claim, and measure it against this project's own vision and concerns —
before anyone spikes it or decides on it.

## Storage Location

Store at: `docs/helix/00-discover/component-profile-[component-name].md`

One file per candidate. A decision with six candidates — say PostgreSQL,
MySQL and four managed Postgres providers — is six profiles, not one long
file. Separate files let candidates be researched in parallel, added late,
and revised independently when one maker changes its pricing; a shared file
grows past the point anyone reads it and takes one confidence grade for
claims of very different strength.

## Purpose

Answers: **What does this component actually do, according to the public
record, and how well does that record fit what this project needs?**

Both halves matter. Without the first, the fit is opinion. Without the
second, the profile is a brochure summary nobody can act on. The fit verdict
is the reason the profile exists; the cited record is what makes the verdict
trustworthy.

## Role Boundary

A Component Profile is not a [[tech-spike]]. A spike runs something — a
prototype, a benchmark, an integration — to answer one narrow question with
hands-on evidence. A profile reads. It comes first, so the spike is spent
only on what reading cannot settle. When the record alone settles the
question, the profile feeds the ADR directly and no spike is needed.

It is not a [[competitive-analysis]]. That positions *our* product against
rivals in a market. This asks whether *someone else's* component belongs in
our stack. Nothing here is being sold.

It is not a [[current-state-inventory]]. The inventory records what the
organization already runs, graded for evidence. A profile covers a candidate
that may never be adopted. The inventory supplies the profile's incumbent.

It is not a [[resource-summary]]. That summarizes a source that grounds HELIX
guidance. A profile synthesizes many sources about a thing.

It is not an ADR. The profile assesses one candidate's fit. The choice among
candidates, with its consequences, lives in the ADR that cites the profiles.

## Ownership and Reuse

A profile belongs to the project whose decision it feeds, and lives in that
project's Discover directory. Its factual sections — What It Is,
Capabilities, Technology and Operations, Pricing and Licensing, Positioning,
Sources — are portable: another project may copy them. Scope and Fit
Assessment are not: they name this project's artifacts and open decisions, and
a copy that keeps them asserts a fit nobody measured. A project that reuses a
profile rewrites Scope and Fit Assessment, re-grades Confidence, and re-dates
every source it keeps. The graph has no cross-project edge for this; the copy
is the mechanism.

## Method

1. **Read the project before the component.** Open [[product-vision]],
   [[principles]], [[concerns]], [[architecture]] and any ADR or spike this
   profile will feed. Write down, as questions, what they require of the role
   this component would fill. These questions become the Fit Assessment rows.
   A profile written before this step assesses fit against nothing.
2. **Fix the scope.** Name the exact component — edition, version line,
   hosting form — and what the profile excludes. "Postgres" is not a scope;
   "PostgreSQL 18, community distribution, self-hosted or managed" is.
3. **Gather the record.** Maker material first, then independent coverage
   (analysts, comparisons, conference talks, issue trackers, post-mortems),
   then community sources. Record each source with its URL and the date you
   read it, and classify it as maker, independent or community.
4. **Write one claim at a time, with its number.** Every capability, every
   operational fact, every figure cites a source. A claim you cannot source
   is written as **Not published**, and that is a finding, not a gap in your
   work.
5. **Label every figure.** Published, with source and date. Third-party
   estimate, naming the estimator. Or Not published. Never derive a price.
6. **Position against the adjacent candidates.** Name what a reader will ask
   "why not X?" about, and state the divergence *this project* cares about.
   Link sibling profiles where they exist.
7. **Assess fit, row by row, against the questions from step 1.** Each row
   names the artifact it comes from. Then write exactly one verdict from the
   declared vocabulary and one sentence of conditions or deciding gap.
8. **Grade confidence honestly.** One grade from the rubric, then say which
   claims are corroborated, which rest on the maker alone, and which have
   none. Name the weakest area.
9. **Route what the record cannot answer.** Every unknown that bears on a
   design-defining decision becomes an Open Question with a route: a spike, a
   question to the maker, or operator guidance.

## Researching Honestly

The pressure on this artifact is toward fluency: the model already knows the
component, the maker's site is persuasive, and a confident profile reads as
finished. Resist all three.

- **Familiarity is not a source.** A fact you know about the component still
  needs a citation. If you cannot find one, it is Not published.
- **Maker material is one voice.** A profile with no independent source is
  Medium at best, however thorough the documentation.
- **"Not published" beats a plausible guess.** A guessed price, a guessed
  region list, a guessed certification becomes a fact in the ADR.
- **The verdict is not the decision.** Conditional fit with named conditions
  is a complete, useful result. Do not round it up to Fit to look decisive,
  and do not recommend a candidate — that is the ADR's job.
- **A fit row without an artifact is an opinion.** If nothing in the
  project's own documents requires it, it is not a requirement.
- **Hands-on claims do not belong here.** If you find yourself writing "in
  our test", stop and open a spike.

## Inputs

- The project's [[product-vision]], [[principles]], [[concerns]],
  [[architecture]] and the ADR or spike this profile feeds — read first
- [[current-state-inventory]], for the incumbent
- Maker documentation, pricing pages, licence texts, security and trust pages,
  release notes and roadmaps
- Independent coverage: analyst notes, comparisons, conference talks,
  incident reports, issue trackers
- Sibling profiles for adjacent candidates

## Quality Checks

- Every factual claim cites a numbered source or is marked Not published or
  Third-party estimate
- Every figure is labelled Published, Third-party estimate or Not published
- Every fit row names the project artifact or decision it is measured against
- Fit Assessment closes with exactly one verdict from the declared vocabulary
- The confidence grade is justified by naming corroborating and missing
  sources
- Every source carries an access date
- No benchmark, prototype or integration result is claimed
- No choice among candidates is made
