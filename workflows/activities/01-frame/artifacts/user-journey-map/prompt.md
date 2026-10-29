# User Journey Map Generation Prompt

Map one person's experience of one task, phase by phase, and trace each phase
to the acceptance criteria that deliver it.

## Purpose

User Journey Map is the **frame-level experience artifact**, and it is
optional. Its unique job is to show the whole experience a task involves,
including steps outside the product, so the team can see where the stories
cover the experience, where they leave gaps, and which opportunities it owns.

It is not a story, a user flow or a design. Stories own testable behavior; the
user flow owns views and transitions; wireframes own layout and states. The map
links to them by ID.

## Focus

- Create `docs/helix/01-frame/journey-maps/UJM-XXX-[name].md` only when a task
  spans several stories or views and the team needs the whole picture.
- Pick one person from the PRD's User Segments and one task from the feature
  specification's Task Model, and name both. If the PRD has no User Segments
  or the feature has no Task Model, name the person and the task in plain words
  from the PRD's users and the feature's stories instead. A second person or
  task is a second map.
- State goals and expectations before the phases; phases are judged against
  them.
- Name phases as the person's stages ("Notice", "Prepare", "Decide"), not as
  views. Include steps outside the product, such as an email or a phone call.
- Per phase, write the actions, the person's thoughts in their words, one
  emotion (positive, neutral or negative, plus a word) and the touchpoints.
- Ground thoughts and emotions in evidence: a research plan's findings,
  support data or analytics. Mark ungrounded entries "(assumption)". Do not
  invent research.
- Trace every in-product phase to `US-<n>-AC<m>` IDs. Mark a phase no
  criterion delivers as `uncovered:` with a reason; that gap is a finding.
- Give every opportunity one owner and the metric that shows its effect. A
  target is optional: label it a hypothesis unless evidence supports it, and do
  not turn it into a delivery or release gate.
- Name rows by what they say; do not number insights or opportunities.

## Boundary Test

| If you are writing... | Put it in... |
|---|---|
| The person's phases, thoughts, emotions, insights, opportunities | User Journey Map |
| The tasks a feature supports | Feature Specification (Task Model) |
| Testable behavior and Given/When/Then criteria | User Stories |
| Views, transitions and alternate paths | User Flow |
| Layout, states and events of one view | Wireframe |
| Ranked follow-up work | Improvement Backlog |

## Completion Criteria

- One person and one task, with a scenario, goals and expectations.
- Phases run from trigger to end state.
- Every in-product phase names its acceptance criteria or is marked uncovered.
- Every thought and emotion cites evidence or is marked as an assumption.
- Every opportunity has one owner and one metric; any target is supported or labelled a hypothesis.
