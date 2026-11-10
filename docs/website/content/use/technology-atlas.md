---
title: Keep a Technology Atlas
weight: 6
---

A technology atlas is a set of HELIX documents about technologies instead of one
product: what each technology can and cannot do, how several compare on stated
criteria, and what a team advises and why. This page is for a team that already
uses HELIX and wants to keep that knowledge as governed, checkable documents.
After reading it, you can set up an atlas flow, write an assessment and a
position paper that the validator checks, and pin the sources a published
document rests on.

## What the profile changes

A flow scope, declared in `.helix.yml`, can name a profile. A profile selects
which artifact types the flow uses, where they live, which link kinds are
allowed, and how strictly each validation tier checks them. A flow with no
profile behaves as before, so nothing changes for a software-delivery flow.

```yaml
flows:
  - id: atlas
    profile: technology-atlas
    root: knowledge/
```

The `technology-atlas` profile uses six types:

| Type | Holds | Lives in |
| --- | --- | --- |
| `component-profile` with `scope: reusable` | What the public record says about one technology, with no project or verdict | `technology/` |
| `technology-assessment` | A comparison of technologies on stated criteria, with findings and no recommendation | `assessments/` |
| `position-paper` | An argued position, or advised stances, for an audience | `positions/` |
| `decision-brief` | A recommendation for one named context | `decisions/` |
| `adr` | A decision record | `decisions/` |
| `deliverable` | A document issued to an audience, with its sources pinned | `publications/` |

Knowledge in an atlas is advisory. A document that cites an atlas document does
not take orders from it, and a link that claims `governing` authority is a
blocking finding under this profile.

## Write an assessment with ratings as data

An assessment can keep its criteria and ratings in front matter, so the tables a
reader sees are generated from data and cannot drift from it.

1. Create `criteria.yml` in the flow root. Each entry has an `id`, a `label`, a
   `definition`, and the `concern` it serves or `none`. One criterion is one entry
   shared by every assessment.
2. In the assessment, add an `assessment:` block beside `ddx:`. It lists the
   criterion ids, the subjects (each a technology brief and the name to show),
   and a rating for every criterion and subject. A rating is a `finding` or a
   stated `gap` such as `Not published`.
3. Link each subject in `ddx.links` as `evaluates` or `supported_by`.
4. Run `assessment-tables.py --write` on the file. It rewrites the Criteria and
   Comparison tables from the block. Without `--write` it reports a table that
   differs from its data, which makes it usable as a CI check.
5. Run `validate-instance.py` on the file. It blocks an unknown criterion, a
   subject that is not linked, and a pair with no rating or gap.

Findings and gaps are one line each, because each fills one table cell.

## Record stances in a position paper

A position paper can record what the team advises as a `recommendations:` list.
Each entry names a subject and a context, and takes one stance: `recommended`,
`conditional`, `watch`, or `avoid`. It also gives a rationale and the
assessments it rests on, with the criteria it cites. A conditional stance states
its conditions.

Each entry carries `since` and `review_by` dates. It reads as proposed until it
also records `approved_by` and `approved_on`, together. The first table under
`## Recommendations` is generated from the list by `assessment-tables.py`.

Only a position paper can carry a stance. Putting `recommendations:` on a brief
or an assessment is a blocking finding, which keeps what is documented apart
from what is advised.

## Record where a figure comes from

A figure can end with an attribute list that says where it came from:

```markdown
| Support window | Five years per major version | {basis=published accessed=2026-11-06 source="postgresql.org/support/versioning"} |
```

`basis` is `published` when the maker states it, `third-party` when someone else
estimated it, or `not-published` when the record was searched and the figure is
absent. Unless the basis is `not-published`, the attribute list needs a `source`
and an `accessed` date in `YYYY-MM-DD` form. `validate-instance.py` checks every
attribute list that names one of these fields, and skips code and comments.

This notation is HELIX's own. It is not part of DITA or its Markdown profiles,
and a DITA processor drops it.

## Use short keys for technologies

Ratings repeat a technology's document id in every row, and ids are long. A
`keys.yml` in the flow root maps a short name to a document id:

```yaml
keys:
  pg: component-profile-postgresql-reusable
```

A subject, a rating's subject, a recommendation's subject, and a `based_on`
assessment can then use `pg`. A document that uses a key also records what it
resolved to in a top-level `keys:` mapping. If `keys.yml` is later edited to
point `pg` somewhere else, every document that used it fails validation until
someone reads what it cites and updates the record. A key is only an alias:
`ddx.links` keep the full id and the pinned revision.

## Pin sources before publishing

A published document must be reproducible from the sources it cited. Under the
publish tier, every `evaluates`, `supported_by`, and `informed_by` link needs a
`rev`: `git:<commit>` or `sha256:<hex>`. In a position paper, each assessment
named in `based_on` needs one too.

1. Commit the sources, then run `pin-sources.py pin` on the document. It writes
   the commit each unpinned link last changed in.
2. Run `validate-instance.py --tier publish` on the document.
3. Later, run `pin-sources.py check` to see whether a source has changed since
   the pin. A changed source never rewrites the document: it keeps the content
   it was written against.

`pin-sources.py pin` needs each link written on several lines, with `id:` and
`kind:` on separate lines.

## What is not checked

The validator reads one document at a time. It does not check that a cited
assessment links the recommended technology, that the assessment has findings
for the criteria a recommendation cites, or that two papers do not give the same
technology conflicting stances in one context. Check those by hand until a
graph-level check exists. A link that points at another graph is recorded and
pinned but not fetched, so the runtime or your own tooling resolves it.

## Next steps

- Read [Multiple Flows and Microsites](/use/multiple-flows/) for how flow scopes pick an owner.
- Browse [Artifact Types](/artifact-types/) for the briefs, assessments, and papers used here.
- See the [release notes](/artifacts/release-notes/) for the versions that added each piece.
