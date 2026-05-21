---
ddx:
  id: helix.workflow.conventions
  depends_on:
    - helix.workflow
  review:
    self_hash: a2b087d211b0c27ca2a3cccc2ca481449c9ff6a2d6d08c50572844f7762ea34c
    deps:
      helix.workflow: 1225132b3050598055eacb5462639824d78ac204cca2cbeda3611766532e79c8
    reviewed_at: "2026-05-15T04:11:24Z"
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
3. The runtime integration appendix for your runtime (e.g. the DDx
   reference-runtime integration in [DDX.md](DDX.md) and [EXECUTION.md](EXECUTION.md))

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
`.ddx/plugins/helix/workflows/` and `.agents/skills/` layout) are documented in
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
- Iteration planning selects work-item sets for the next cycle by ID.
- Reports and retrospectives should emit follow-up work items instead of
  embedding durable task lists in canonical docs.

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
- [ ] Current implementation status captured

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

## DDx Integration Appendix

The conventions above are runtime-neutral. The notes below apply to
DDx-managed HELIX installations.

### DDx workspace layout

DDx installs HELIX content at `.ddx/plugins/helix/workflows/` and stores
work items in `.ddx/beads.jsonl`. A DDx-managed HELIX project layout includes
this workspace alongside `docs/helix/`:

```
project-root/
├── .ddx/                    # DDx workspace (beads, plugins, hooks)
│   ├── beads.jsonl          # Work-item tracker storage
│   └── plugins/helix/       # Installed HELIX content
├── .agents/skills/          # Published HELIX skills (project-level)
├── skills/                  # Skill sources for the HELIX package
└── docs/helix/              # Canonical HELIX activity artifacts
```

### DDx shared workflow root

Under DDx, the shared workflow resource root is
`.ddx/plugins/helix/workflows/`. Skills reference shared assets through that
package-relative root. Installers and plugins must preserve `.agents/skills/`,
`skills/`, and `.ddx/plugins/helix/workflows/` together.

### DDx work-item tracker

DDx uses a JSONL-backed tracker. See `ddx bead --help` for the full command
surface. Common tracker introspection:

- `ddx bead ready`, `ddx bead blocked`, and `ddx bead dep tree` replace custom
  HELIX status fields for queue inspection.
- The `helix` label identifies HELIX-managed issues in a DDx tracker.

### DDx template paths

DDx-installed templates live at:

- artifact templates: `.ddx/plugins/helix/workflows/activities/<activity>/artifacts/<type>/template.md`
- refinement template: `.ddx/plugins/helix/workflows/templates/refinement-log.md`

Example artifact bootstrap:

```bash
sed -n '1,120p' .ddx/plugins/helix/workflows/activities/01-frame/artifacts/prd/prompt.md
cp -f .ddx/plugins/helix/workflows/activities/01-frame/artifacts/prd/template.md \
      docs/helix/01-frame/prd.md
```

For DDx execution behavior, queue control, and operator workflow, see
[EXECUTION.md](EXECUTION.md). For methodology background and the DDx authority
model, see [DDX.md](DDX.md).

---

*These conventions ensure consistency while maintaining flexibility for project-specific needs. They enable tooling support and make HELIX projects more maintainable and understandable.*
