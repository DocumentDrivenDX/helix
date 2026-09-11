---
ddx:
  id: helix.workflow.conventions
  authoring:
    home: repo
  depends_on:
    - helix.workflow
  review:
    self_hash: 61c67d01edc02c5c49da4aef8a76346ed131e8b434dd1013bea9c5142212d5f3
    deps:
      helix.workflow: 24bc127a783c568be4813f8a7665c82abc04056dd94718eda32a51fa9191b543
    reviewed_at: "2026-06-11T15:47:44Z"
---
# HELIX Workflow Conventions

## Overview

This document defines conventions for projects using the HELIX workflow, ensuring consistency across implementations while allowing for project-specific needs.

## Scope Boundary

This document defines documentation layout, naming, and traceability
conventions. It does not define queue control, execution-loop behavior, or
tracker semantics.

When conventions and execution guidance disagree, follow:

1. [README.md](README.md)
2. The bounded action prompts under `actions/`
3. The install guide for your runtime (for DDx,
   [docs/install/ddx.md](../docs/install/ddx.md))

## Documentation Voice

HELIX documentation uses the canonical profiles in [voice.yml](voice.yml).
Deliverables for people outside the project (decks, one-pagers, briefs) use
the `human-facing` profile: conciseness 5, claim titles, no HELIX vocabulary
in the body, every number sourced, and a subset-never-contradict rule against
the governing artifact.
Artifact authoring defaults to `artifact-signal`: conciseness 2/10, written for
humans and agents that need to preserve context while making decisions. Public
website copy uses `public-site`: conciseness 3/10, written for smart novice
readers. Machine-facing extracted state uses `machine-facts`: conciseness 1/10.

Use tight vocabulary:

- Prefer the exact artifact, command, field, status, metric, or constraint over
  broad nouns such as "process", "workflow", "system", or "quality" when a
  narrower term exists.
- Reuse canonical HELIX terms consistently: activity, artifact, concern,
  work item, acceptance criterion, ratchet, runtime, and evidence. Do not
  introduce synonyms that force readers or agents to remember extra mappings.
- Name uncertainty as an open question, assumption, risk, or blocker. Do not
  bury it in hedged prose.
- Keep claims scoped to the artifact's authority. A PRD states product scope; an
  ADR records a decision; a test plan names verification strategy; a runtime
  work item tracks execution.
- Replace value language with observable consequences. Say what changes, what
  is blocked, what is measured, or what evidence proves the claim.
- Remove filler that does not carry context. If a sentence can disappear without
  changing a decision, trace link, acceptance criterion, or next action, delete
  it.

Artifact prompts may add type-specific style rules, but they must preserve this
contract. Public website prose may add stricter editorial rules through the
`public-site` profile; it must not weaken the methodology-level requirement for
precise vocabulary and scoped claims.

## Skill Resource Boundary

HELIX content is published as a package containing shared workflow resources
plus one or more skills.

- The package surfaces shared workflow resources at a stable, package-relative
  root (the methodology library).
- Resources used by more than one skill belong in the shared workflow root.
- Resources used by only one skill belong in that skill's directory.
- Skills may assume package-relative access to shared workflow resources only
  when the full package layout is preserved.
- Installers, plugins, and other distribution packages must preserve the
  published skills and shared workflow resources together; copying isolated
  skill folders without shared resources is an invalid HELIX install.

Runtime-specific package layouts (for example the DDx plugin's
`workflows/` and `.agents/skills/` layout) are documented in
the runtime integration appendix; the requirements above apply to every layout.

## Documentation Structure

### Activity-Based Organization

Projects using HELIX should organize their documentation using the `docs/helix/` convention:

```
project-root/
├── docs/
│   ├── helix/                  # HELIX activity artifacts
│   │   ├── 00-discover/        # Optional opportunity validation
│   │   ├── parking-lot.md       # Deferred and future work registry
│   │   ├── 01-frame/          # Problem definition & requirements
│   │   ├── 02-design/         # Architecture & design decisions
│   │   ├── 03-test/           # Test strategies & plans
│   │   ├── 04-build/          # Implementation guidance
│   │   ├── 05-deploy/         # Deployment & operations
│   │   └── 06-iterate/        # Continuous improvement
│   ├── reference/             # Reference documentation
│   ├── operations/            # Operational procedures
│   └── strategy/              # Strategic planning
```

Runtimes may add their own workspace directories alongside `docs/helix/` for
work-item storage, execution evidence, and runtime state. See the runtime
integration appendix for the layout your runtime uses.

### Why This Structure?

1. **Clear Separation**: Activity artifacts are distinct from operational/reference docs
2. **Workflow Alignment**: Numbered directories match HELIX activity order
3. **Execution Separation**: Ephemeral task execution lives in the runtime's
   work-item tracker, not in canonical planning docs
4. **Tool Support**: Consistent structure enables validation and automation
5. **Flexibility**: Non-activity documentation has dedicated locations
6. **Shared skill resources**: The HELIX content package keeps shared workflow
   resources together with the skills that depend on them

### Activity Directory Contents

Each activity directory contains artifacts directly (no `artifacts/` subdirectory):

```
00-discover/
├── README.md
├── product-vision.md
├── business-case.md
├── competitive-analysis.md
└── opportunity-canvas.md

01-frame/
├── README.md
├── prd.md
├── principles.md
├── features/
│   └── FEAT-XXX-*.md
├── feature-registry.md
├── user-stories/
├── stakeholder-map.md
├── compliance-requirements.md
├── security-requirements.md
└── threat-model.md

02-design/
├── README.md
├── architecture.md
├── adr/
├── solution-designs/
│   └── SD-XXX-*.md
├── technical-designs/
│   └── TD-XXX-*.md
├── contracts/
├── data-design.md
└── security-architecture.md

03-test/
├── README.md
├── test-plan.md
├── test-procedures.md
├── test-plans/
└── security-tests.md

04-build/
├── README.md
└── implementation-plan.md

05-deploy/
├── README.md
├── deployment-checklist.md
├── monitoring-setup.md
├── runbook.md
└── release-notes.md

06-iterate/
├── README.md
├── metrics-dashboard.md
├── security-metrics.md
├── improvement-backlog.md
├── metrics/                 # Shared metric definitions (YAML)
├── alignment-reviews/
└── backfill-reports/
```

### Parking Lot Registry

The parking lot is a project-level registry for deferred and future work:
- **Location**: `docs/helix/parking-lot.md`
- **Purpose**: Capture deferred work without adding inline sections to core artifacts
- **Eligibility**: Any HELIX artifact may be parked
- **Tooling**: Mark parked artifacts with `ddx.parking_lot: true` to exclude them from dependency graphs

## Authoring Home

Every artifact declares where it is authored, in `ddx.authoring.home`. The
field definitions are normative in
[artifact-schema.md](artifact-schema.md); this section covers the working
practice.

### Classifying a document

One question decides it: does producing this document require heavy human
manipulation of format or content — the kind of collaborative work a canvas,
board, or deck does well and a Markdown file does badly?

- **No** — `home: repo`. The Markdown file is the document.
- **Yes** — `home: external-tool`. The document is authored in the tool and
  the repository holds its identity and a copy.

| Document | Home | Why |
| --- | --- | --- |
| PRD, ADR, technical design, test plan, runbook | `repo` | Prose and tables. Review happens in diffs. |
| Release notes, status report | `repo` | Text output; no layout work. |
| Architecture diagram iterated live in a workshop | `external-tool` | The artifact is the canvas. |
| Stakeholder review deck | `external-tool` | Format is part of the deliverable. |
| Data model walked through by eight people in a modelling tool | `external-tool` | The tool's affordances are how the work gets done. |
| Feature spec several people contribute to in a shared doc | `repo` | Needing input from several people is not the test. |

That last row is the discipline. The test is not whether collaboration
happens — it happens on nearly everything — but whether the *artifact itself*
depends on a tool's affordances. A document that could have been written in
Markdown belongs in the repository, however many people touched it.

Classify toward `repo` when unsure. A document wrongly marked `repo` costs one
awkward migration if it turns out to need a tool. A document wrongly marked
`external-tool` routes every future edit through a checkout cycle it never
needed, permanently.

### Checked out

The stub enters the repository when the document is created in the tool, not
when it is finished. Downstream artifacts need a resolvable `ddx.id` to point
at, and a checked-out artifact is what blocks their approval.

```markdown
---
ddx:
  id: SD-004
  type: solution-design
  activity: design
  status: draft
  authoring:
    home: external-tool
    state: checked-out
    tool: google-slides
    origin: https://docs.google.com/presentation/d/1AbC.../edit
---

# Prebill Review — Solution Design

> **Not authoritative.** This document is being authored in Google Slides at
> the link above. Do not edit this file; content lands here at check-in.

Covers the prebill review flow: adjudication states, reviewer queue, and the
escalation path to manual billing.
```

The banner is prose, not metadata, because prose is what every runtime reads.
A consumer that does not understand `authoring` must still not edit the file.

### Checked in

```markdown
---
ddx:
  id: SD-004
  type: solution-design
  activity: design
  status: draft
  authoring:
    home: external-tool
    state: checked-in
    tool: google-slides
    origin: https://docs.google.com/presentation/d/1AbC.../edit
    export: docs/helix/02-design/solution-designs/assets/SD-004-prebill-review.pptx
---

# Prebill Review — Solution Design

> **Read here, edit in Google Slides.** This file mirrors the document at
> `authoring.origin`. Editing it directly forks it from its authoring home.
> To change it: set `state: checked-out`, edit in the tool, check in again.

## Adjudication States
...
```

Three representations exist and each has one role:

| Representation | Role |
| --- | --- |
| Markdown body | Read surface. Downstream artifacts, reviews, and agents resolve against it. |
| `authoring.origin` | Write surface. Every edit goes here, for the life of the document. |
| `authoring.export` | Fidelity evidence. The committed original, for formatting the Markdown cannot carry. |

Checking in does not approve the document. It makes approval possible; the
document is still `draft` until it is reviewed like any other.

### Reading through a connector

When the runtime exposes a document connector for the authoring tool, a
mode may read the live document at `authoring.origin` instead of waiting
for a check-in. That read satisfies the rule that governing artifacts are
read before drafting; findings cite the origin and the live section. Three
things do not change: the Markdown body stays the committed copy, a
checked-out artifact stays not dependable for approval until it is checked
in, and nothing writes through the connector. Declare
`authoring.connector` so a reader knows which connector was used. Runtimes
without the connector fall back to the checked-in body.

### Transitions

1. **Create.** Stub and external document in the same change. `state:
   checked-out`.
2. **Check in.** One commit carries the body content, the `export` file,
   and `state: checked-in`. Splitting these leaves a window where the
   frontmatter and the body disagree.
3. **Check out again.** Flip `state` back. Content and `export` from the
   previous check-in stay as the last known copy; the banner changes to say
   a revision is in flight.

`home` never changes in any of these. Reclassifying a document is a migration,
handled deliberately, not one of these transitions.

### Approval blocking

A checked-out artifact is present but not dependable — its ID resolves and its
content is not current in the repository.

- A checked-out artifact must not be `ddx.status: approved`.
- A downstream artifact must not be approved while anything it depends on is
  checked out.

Long-lived checkouts are the failure mode to watch: a document checked out for
a quarter blocks its dependants for a quarter, and nothing in the repository
notices. Review open checkouts when an activity's exit gate is assessed.

## Work-Item Conventions

Work items capture scoped work that can be opened, updated, split, blocked, and
closed without changing the canonical authority stack. The runtime owns the
tracker substrate; HELIX governs which work-item shape counts as ready for
execution and how it relates to canonical artifacts.

### When to Use Work Items

Use tracker work items for:
- Story-level implementation work
- Story-level deployment work
- Prioritized backlog items
- Review and reconciliation tasks
- Follow-up actions derived from reports or retrospectives

Do not use tracker work items as the source of truth for:
- Vision
- Requirements
- Architecture or ADRs
- Solution or technical designs
- Test plans or executable tests
- Project-level implementation strategy

### Required Properties

Every work item should:
1. Use the runtime's native issue types, parents, dependencies, and statuses
2. Reference governing canonical artifacts (via `spec-id` and/or the
   description) so authority is traceable
3. Define a single coherent goal
4. Specify deterministic completion criteria
5. Include verification steps
6. Remain small enough to close independently

### Label Conventions

Labels are organizational conventions for triage and traceability. They are
recommended for runtimes that support labels:

- A `helix` label for discoverability
- A activity label when applicable: `activity:frame`, `activity:design`, `activity:test`,
  `activity:build`, `activity:deploy`, `activity:iterate`, or `kind:review`
- `kind:build`, `kind:deploy`, `kind:backlog`, or `kind:review` when helpful
- Traceability labels such as `story:US-XXX`, `feature:FEAT-XXX`,
  `source:metrics`, or `area:auth`

Runtime-specific tracker commands and conventions are documented in the
runtime integration appendix.

### HELIX Integration

- Project-level implementation plans decompose execution into tracker work items.
- Improvement backlog documents summarize and prioritize backlog work items
  stored in the tracker.
- Iteration plans own commitment membership: they select existing work items
  by ID where items already exist, and their task tables are the source from
  which the runtime creates missing items — each created item's ID is then
  back-referenced in the plan. The tracker owns live status either way, and
  hand-added tracker items never silently widen the plan.
- Reports and retrospectives should emit follow-up work items instead of
  embedding durable task lists in canonical docs. An iteration plan's task
  table is a commitment declaration, not a live task list: its Status column
  records planning-time state and is not maintained after work items derive.

## Naming Conventions

### File Names

1. **README.md**: Each activity directory must have a README explaining its purpose and current status
2. **Artifact Names**: Use descriptive, lowercase names with hyphens (e.g., `threat-model.md`, `api-design.md`)
3. **Numbered Items**: When multiple versions exist, use semantic versioning (e.g., `prd-v1.0.md`, `prd-v1.1.md`)

### Directory Names

1. **Activity Directories**: Always use two-digit numbering (01-frame, not 1-frame)
2. **Artifact Directories**: Use lowercase with hyphens, typically plural (e.g., `user-stories`, `contracts`)
3. **No Nesting**: Avoid deep nesting; keep artifacts at most one level deep within activity directories

### Design Artifact Naming

1. **Feature specifications**: `FEAT-XXX-[name].md`
2. **Solution designs**: `SD-XXX-[name].md`
3. **Technical designs**: `TD-XXX-[name].md`

### Skill and Workflow Resource Placement

1. **Shared resources**: If more than one HELIX skill depends on an asset, it
   belongs in the package's shared workflow resource root.
2. **Skill-local resources**: If only one skill uses an asset, keep it with
   that skill.
3. **Stable references**: Skills should reference shared assets through stable
   package-relative paths and documented locations.
4. **Packaging integrity**: Plugin or enterprise distribution must preserve the
   HELIX package root so those references continue to resolve.

## Cross-References

### Linking Between Activities

Use relative paths to reference artifacts across activities:

```markdown
# In 02-design/architecture.md
See requirements in [../01-frame/prd.md](../01-frame/prd.md)

# In 03-test/test-plan.md
Based on architecture in [../02-design/architecture.md](../02-design/architecture.md)
```

### Traceability

Maintain clear traceability by:
1. Referencing source requirements in design documents
2. Linking designs to test plans
3. Connecting test results to implementation decisions
4. Tracking deployment issues back to design choices

## Non-Activity Documentation

### Reference Documentation

Place in `docs/reference/`:
- User guides
- API documentation
- Integration guides
- Glossaries

### Operational Documentation

Place in `docs/operations/`:
- Incident response procedures
- Monitoring guides
- Performance tuning
- Backup/recovery procedures

### Strategic Documentation

Place in `docs/strategy/`:
- Roadmaps
- Market analysis
- Competitive analysis

Use `docs/helix/00-discover/` for HELIX discovery artifacts that participate in
the canonical authority stack.

## Migration from Existing Documentation

When migrating existing documentation to HELIX structure:

1. **Analyze Current State**: Map existing docs to HELIX activities
2. **Extract Requirements**: Pull requirements from various sources into 01-frame
3. **Consolidate Design**: Gather architecture docs into 02-design
4. **Identify Gaps**: Note missing artifacts for each activity
5. **Create Placeholders**: Add README files marking TODOs for missing content
6. **Maintain References**: Update all cross-references after migration

## Validation

Projects should validate their documentation structure:

```bash
# Check required activity directories exist
test -d docs/helix/01-frame || echo "Missing frame activity"
test -d docs/helix/02-design || echo "Missing design activity"
# ... etc

# Verify README files in each activity
for activity in docs/helix/*/; do
  test -f "$activity/README.md" || echo "Missing README in $activity"
done

# Check for orphaned references
grep -r "\.\./" docs/helix/ | grep -v "helix"
```

## Templates

Use HELIX workflow templates to create consistent artifacts. Each artifact
type under `activities/<activity>/artifacts/<type>/` ships a `prompt.md` (authoring
guidance) and `template.md` (skeleton document). Read the prompt, copy the
template into the corresponding location under `docs/helix/<activity>/`, and fill
it in. Runtime-specific installation paths to those template roots are listed
in the integration appendix.

## Best Practices

1. **Start Early**: Create the structure at project inception
2. **Keep Current**: Update documentation as the project evolves
3. **Review Regularly**: Include doc reviews in activity transitions
4. **Automate Checks**: Add structure validation to CI/CD
5. **Version Control**: Track all documentation changes in git
6. **Link Liberally**: Cross-reference related artifacts
7. **Stay Flat**: Avoid deep directory nesting
8. **Be Consistent**: Follow naming conventions strictly

## FAQ

### Q: Can I add custom directories to activities?
A: Yes, activities can have project-specific subdirectories. Document them in the activity README.

### Q: Should code live in helix/?
A: No, code belongs in the project's source directories. Documentation only in helix.

### Q: How do I handle multiple features in parallel?
A: Keep the shared project docs stable and add separate feature/story files in the canonical activity directories, for example `docs/helix/01-frame/features/FEAT-001-*.md`, `docs/helix/02-design/solution-designs/SD-001-*.md`, and `docs/helix/01-frame/user-stories/US-001-*.md`.

### Q: What about diagrams and images?
A: Store them alongside the documents that reference them, or in a activity-level `images/` directory.

### Q: Can I skip activities?
A: While not recommended, if skipping activities, document why in the project root README.

## Story Refinement Conventions

### Refinement Documentation Structure

Story refinements are tracked in the iterate activity to maintain learning and traceability:

```
docs/helix/06-iterate/refinements/
├── README.md                           # Refinement process overview
├── US-001-refinement-001.md           # First refinement of US-001
├── US-001-refinement-002.md           # Second refinement of US-001
├── US-042-refinement-001.md           # First refinement of US-042
└── refinement-index.md                # Cross-reference index
```

### Refinement Naming Convention

**File Naming Pattern**: `{{STORY_ID}}-refinement-{{NUMBER}}.md`
- `{{STORY_ID}}`: Original user story identifier (e.g., US-001, US-042)
- `{{NUMBER}}`: Zero-padded refinement sequence (001, 002, 003...)

Examples:
- `US-001-refinement-001.md` - First refinement of US-001
- `US-042-refinement-003.md` - Third refinement of US-042

### Refinement Linking Strategy

**Story Updates**: Original user stories reference their refinements:
```markdown
## Refinement History
- [Refinement 001](../06-iterate/refinements/US-001-refinement-001.md) - Bug fixes for error handling
- [Refinement 002](../06-iterate/refinements/US-001-refinement-002.md) - Scope expansion for mobile support
```

**Cross-Activity References**: Refinement logs link to all affected documents:
```markdown
### Updated Documents
- [User Story](../01-frame/user-stories/US-001.md) - Updated acceptance criteria
- [Technical Design](../02-design/architecture/auth-service.md) - Added error handling flows
- [Test Plan](../03-test/test-procedures/US-001-tests.md) - Added regression tests
```

### Refinement Categories

**Standard Categories** for consistent tracking:
- `bugs` - Issues discovered during implementation or testing
- `requirements` - New or evolved business requirements
- `enhancement` - Improvements identified during development
- `mixed` - Combination of multiple refinement types

### Version Control Integration

**Branch Strategy** for refinements:
- Create refinement branches: `refinement/US-001-001`
- Commit refinement log first, then affected documents
- Ensure atomic commits for traceability

**Commit Message Format**:
```
refine(US-001): fix error handling specification gaps

- Add refinement log US-001-refinement-001
- Update acceptance criteria for edge cases
- Add regression test requirements
- Update error handling design patterns

Addresses bugs discovered during implementation activity.
```

### Quality Gates for Refinements

**Pre-Refinement Checklist**:
- [ ] Issues clearly documented and categorized
- [ ] Impact assessment completed
- [ ] Stakeholder approval obtained (if scope changes)
- [ ] Intended artifact change, acceptance impact, and required evidence are
      explicit

**Post-Refinement Validation**:
- [ ] All affected activity documents updated
- [ ] Cross-references verified and functional
- [ ] Traceability maintained from issue to resolution
- [ ] No conflicts introduced between requirements
- [ ] Team communication completed

### Refinement Index Maintenance

**Index Structure** for discoverability:
```markdown
# Story Refinement Index

## Active Stories with Refinements
- US-001: [3 refinements](US-001-refinement-001.md) - Authentication Service
- US-042: [1 refinement](US-042-refinement-001.md) - Workflow Commands

## Refinement Categories
### Bugs (High Impact)
- [US-001-refinement-001](US-001-refinement-001.md) - Critical error handling gaps
- [US-018-refinement-002](US-018-refinement-002.md) - Input validation issues

### Requirements Evolution
- [US-025-refinement-001](US-025-refinement-001.md) - Mobile support addition
- [US-042-refinement-001](US-042-refinement-001.md) - Enhanced command discovery
```

### Template Usage

Use the standard refinement template at `templates/refinement-log.md` in the
HELIX content package. Copy it into
`docs/helix/06-iterate/refinements/<STORY_ID>-refinement-<NUMBER>.md` and fill
it in. The runtime integration appendix lists the concrete package path your
runtime installs.

## Evolution

These conventions will evolve based on usage. To propose changes:

1. Document the issue with current conventions
2. Propose specific changes with rationale
3. Show examples of the new approach
4. Update this document after consensus

## Runtime Integration

The conventions above are runtime-neutral. Each runtime documents its own
workspace layout, shared-resource root, work-item tracker commands, and template
paths in its install guide. For DDx-specific workspace, tracker, and template
details, see [docs/install/ddx.md](../docs/install/ddx.md).

---

*These conventions ensure consistency while maintaining flexibility for project-specific needs. They enable tooling support and make HELIX projects more maintainable and understandable.*
