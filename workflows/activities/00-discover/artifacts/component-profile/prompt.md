# Component Profile Generation Prompt

Consolidate what is publicly known about one candidate stack component, cite
every claim, and measure it against this project's own vision and concerns,
before anyone spikes it or decides on it.

## Storage Location

Store at: `docs/helix/00-discover/component-profile-[component-name].md`

One file per candidate. A decision with six candidates: say PostgreSQL,
MySQL and four managed Postgres providers, is six profiles in six files. Separate files let candidates be researched in parallel, added late,
and revised independently when one maker changes its pricing; a shared file
grows past the point anyone reads it and takes one confidence grade for
claims of very different strength.

## Purpose

Answers: **What does this project need from the role, what does this
component do on each of those needs according to the public record, and how
do the alternatives compare on the same needs?**

The Need gives the reader a way in and tells the research what to look for.
The cited record makes the fit checkable. The landscape lets the ADR compare
candidates from evidence. The Summary, Need, and Required Capabilities
sections are reused word for word by any brief or deck built from the
profile, so they are written for a reader outside the project.

## Role Boundary

A profile reads the public record; a [[tech-spike]] runs something and comes
after it, so the spike is spent only on what reading cannot settle. A
[[competitive-analysis]] positions our product in a market; a profile asks
whether someone else's component belongs in our stack. A
[[current-state-inventory]] records what already runs and supplies the
incumbent. A [[resource-summary]] summarizes one source; a profile
synthesizes many. The ADR that cites the profiles makes the choice among
candidates.

## Ownership and Reuse

A profile belongs to the project whose decision it feeds and lives in that
project's Discover directory. Its factual sections (What It Is,
Technology and Operations, Pricing and Licensing, the evidence paragraphs in
Capability Alignment, Sources) are portable: another project may copy them.
Scope, Need, Required Capabilities, the status words, the verdict, and the
Competitive Landscape are not: they name this project's artifacts and
decisions, and a copy that keeps them asserts a fit nobody measured. A project
that reuses a profile rewrites those, re-grades Confidence, and re-dates every
source it keeps. The graph has no cross-project edge for this; a project copies the file.

## Method

The order matters. Steps 1 to 3 happen before any candidate material is
opened; a profile that starts from the maker's site assesses fit against
whatever the maker chose to advertise.

1. **Write the Need.** Open [[product-vision]], [[business-case]],
   [[principles]], [[concerns]], [[architecture]], and the ADR or spike this
   profile will feed. Write, in a reader's words, the system and the role to
   fill, the use cases the role serves, and the goals those use cases
   accomplish, each goal cited to its artifact after the sentence. Name the
   incumbent from [[current-state-inventory]] and why it no longer serves.
   Cite project artifacts only; a `[n]` in this section means the criteria
   were written after the research.
2. **Derive the Required Capabilities.** From the Need and the same
   artifacts, list the capabilities the role must have. Each row names the
   goal it serves, the artifact it comes from, and what evidence in a public
   record would settle it: a documented feature, a published limit, a licence
   clause, an audit report. This "Settled by" column is the research plan.
   A capability no artifact requires goes under Nice to Have or is dropped.
   When several candidates feed one decision, write these two sections once
   and copy them into every profile unchanged.
3. **Fix the scope.** Name the exact component, edition, version line, and
   hosting form, and what the profile excludes. "Postgres" is not a scope;
   "PostgreSQL 18, community distribution, self-hosted or managed" is.
4. **Research capability by capability.** For each row, search the maker's
   documentation for the feature, the version that introduced it, and its
   documented limits; then search independent coverage (analysts,
   comparisons, conference talks, issue trackers, post-mortems) for how it
   behaves in practice under the conditions the Need names (a pooled
   connection, a write burst, a region). Record each source with its URL,
   its class (maker, vendor, independent, community), its author or
   organisation, its publication date when shown, and the date you read it.
   Cite the versioned documentation URL for the scoped version. Record the
   search strings you used under Sources, so a Not published cell shows
   where you looked. When two sources disagree, keep both with their dates.
5. **Write the lead.** What It Is gives category, maker or governing body,
   purpose, adoption from an independent source, cadence and support window,
   licence, and built-for use cases, each sentence cited. A reader who stops
   here should be able to say what the thing is.
6. **Write Capability Alignment, one subsection per capability.** State
   what the record shows, citing at the clause, with the version, the
   caveats, and the independent coverage attributed inline by organisation
   and year. Close the row's "Settled by" plan (found in [n], or not found
   with the search recorded) and give the status: Met, Unmet, or Unknown.
   Then the verdict, exactly one, by the definitions in How to Read This
   Profile: a design-defining Unknown makes it Undetermined.
7. **Fill the operational and pricing tables.** Every cell cites or says Not
   published. Label every figure. Never derive a price.
8. **Research the alternatives on the same capabilities.** For each
   alternative a reader will ask "why not X?" about, fill one row of the
   Competitive Landscape from that alternative's own record, capability by
   capability. Spend a search on each cell before writing Not researched; a
   licence page, a region list, or a docs page is one fetch. A cell you
   still cannot fill says Not researched and names the sibling profile.
   Below the table, one line per alternative: shared ground and the
   divergence this project cares about.
9. **Grade confidence by the rubric.** A design-defining capability left
   Unknown caps the grade at Medium. Say which claims are corroborated, which
   rest on the maker alone, and which have none. Name the weakest area.
10. **Route what the record cannot answer.** Every Unknown that bears on a
    design-defining decision becomes an Open Question with a route: a spike,
    a question to the maker, operator guidance, or a sibling profile. An
    owner, date, duration, or figure appears only when a project artifact
    states it; a scale the project has not set is written as "the project's
    tenant count".
11. **Write the Summary last.** Three sentences a brief can lift: the need,
    the capabilities in one clause each, the verdict with its conditions.

## Researching Honestly

The model already knows the component, the maker's site is persuasive, and a
confident profile reads as finished. Each of those produces a claim without a
source.

- **Familiarity is not a source.** A fact you know about the component still
  needs a citation. If you cannot find one, it is Not published, with the
  search recorded.
- **A citation supports the clause next to it.** A licence page cited for a
  feature list, or a security page cited for encryption the page does not
  mention, is a mis-cite; the reader who follows the number finds nothing.
  Cite at the clause and check each number against its page once more
  before closing.
- **Maker material is one voice.** A profile with no independent source is
  Medium at best, however thorough the documentation.
- **"Not published" beats a plausible guess.** A guessed price, a guessed
  region list, a guessed certification becomes a fact in the ADR.
- **The verdict is not the decision.** Conditional fit with named conditions
  is a complete, useful result. Do not round it up to Fit to look decisive,
  and do not recommend a candidate: that is the ADR's job.
- **A fit row without an artifact is an opinion.** If nothing in the
  project's own documents requires it, it is not a requirement.
- **Hands-on claims do not belong here.** If you find yourself writing "in
  our test", stop and open a spike.
- **Owners, dates, durations, and scales come from project artifacts.** "The
  platform team needs two weeks" is a plan, and a plan belongs to the
  artifact that owns it. "About 2,000 tenants" is a scale, and it belongs to
  the vision or the business case. A profile names the route.
- **An alternative's cell comes from the alternative's record.** A
  competitor's row filled from memory is a comparison nobody can check.
  Write Not researched when a search found nothing, and record the search.
- **Write the Need for the reader of the brief.** The Need and Required
  Capabilities will be lifted into any deck, brief, or one-pager built from
  this profile. Plain words, no artifact IDs in the sentences, the citation
  after.

## Inputs

- The project's [[product-vision]], [[business-case]], [[principles]],
  [[concerns]], [[architecture]], and the ADR or spike this profile feeds,
  read first
- [[current-state-inventory]], for the incumbent
- Maker documentation, pricing pages, licence texts, security and trust pages,
  release notes and roadmaps
- Independent coverage: analyst notes, comparisons, conference talks,
  incident reports, issue trackers
- Sibling profiles for adjacent candidates

## Quality Checks

- Need and Required Capabilities cite project artifacts only, and every
  capability names its artifact and what would settle it
- Every required capability has a Capability Alignment subsection with a
  Settled by line and a status from How to Read This Profile
- Every claim cites at the clause, or is marked Not published with the
  search recorded, or Not researched with the sibling profile named
- Every figure is labelled, and every mutable fact carries an as-of date
- The verdict follows the definitions in How to Read This Profile; a
  design-defining Unknown makes it Undetermined
- The Competitive Landscape scores every named alternative on the same
  capabilities
- The confidence grade follows the rubric; a design-defining Unknown caps it
  at Medium
- Every source carries class, author or organisation, publication date where
  shown, and access date; scoped-version documentation is version-pinned
- No benchmark, prototype, or integration result is claimed
- No owner, date, duration, or figure appears that a project artifact does
  not state
- No choice among candidates is made
