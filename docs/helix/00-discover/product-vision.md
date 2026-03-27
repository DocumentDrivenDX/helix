# Product Vision

## Mission Statement

HELIX helps teams and agents turn product intent into shipped software through
a supervised autopilot that continuously advances the weakest ready layer of
the development stack until human input is actually needed.

HELIX combines collaborative planning with bounded autonomous execution so
human attention stays focused on judgment, tradeoffs, and approvals rather
than routine orchestration.

## 3-5 Year Vision

| Timeframe | Position | Key Milestones |
|-----------|----------|----------------|
| Year 1 | Trusted workflow for AI-assisted delivery teams | Core workflow, tracker, CLI, and mirrored skills converge on one clear contract; `helix-run` reliably advances work without blind looping |
| Year 3 | Default control system for spec-driven agent software delivery | HELIX coordinates requirement, design, test, implementation, review, and metric refinement with minimal human intervention |
| Year 5 | Reference standard for bounded autonomous software execution | Multi-agent and single-agent development workflows adopt HELIX as the safe default for advancing software from intent to production |

**North Star**: A team should be able to express intent once, collaborate where judgment matters, and let HELIX carry the rest of the workflow forward safely.

## Target Market

| Attribute | Primary Segment | Secondary Segment |
|-----------|-----------------|-------------------|
| Who | Small to medium software teams using AI agents for day-to-day development | Individual technical founders and advanced solo developers using AI as a primary implementation partner |
| Size | Teams with enough complexity that specs, plans, tests, and implementation drift without active coordination | Individuals shipping products quickly who need stronger guardrails than ad hoc prompting |
| Pain | Too much operator effort is spent deciding what the agent should do next and keeping planning artifacts aligned with implementation | AI can generate output quickly, but the user still has to manually orchestrate design, testing, implementation, and cleanup |
| Current Solution | Informal prompting, scattered TODOs, weak issue hygiene, and manual agent steering | Direct chat with a coding agent plus personal notes and memory |

## Key Value Propositions

| Value Proposition | Customer Benefit |
|-------------------|------------------|
| Supervisory autopilot | HELIX keeps work moving across specs, designs, tests, implementation, review, and metrics until human judgment is actually needed |
| Least-power execution | HELIX chooses the smallest sufficient next action instead of overreaching, reducing unnecessary churn and speculative changes |
| Authority-ordered reconciliation | When artifacts disagree, HELIX resolves the conflict by escalating to the governing source instead of guessing from code alone |
| Tracker-first execution | All durable work is captured, refined, and executed through one bounded issue system rather than ad hoc lists or memory |
| Interactive intervention points | Users can step into any layer of the workflow directly without losing the benefits of autopilot orchestration |

## Product Principles

1. **Autopilot by default**
   `helix-run` is HELIX's supervisory autopilot. It continuously selects and
   executes the highest-leverage next bounded action that does not require
   human input.

2. **Human intervention by exception**
   HELIX should escalate only when ambiguity, missing authority, tradeoffs, or
   product judgment block safe forward progress.

3. **Least powerful next action**
   HELIX should restore progress with the smallest sufficient action: refine a
   spec before redesigning a system, sharpen issues before implementing, and
   reconcile artifacts before inventing new ones.

4. **Authority before implementation**
   Requirements, designs, tests, and plans govern code. Implementation is
   evidence of current behavior, not the source of truth for what should exist.

5. **Tracker-first execution**
   Durable work should flow through the HELIX tracker so issue refinement,
   dependencies, and completion remain inspectable and actionable.

6. **Interactive entry at any layer**
   The user should be able to work directly on vision, PRD, specs, tests,
   issues, implementation, review, or metrics while still benefiting from
   HELIX's overall control system.

## Success Definition

| Metric | Target | Timeline |
|--------|--------|----------|
| Autonomous forward progress | From an established vision and PRD, `helix-run` can advance the repo through downstream refinement and bounded execution until input is required | Year 1 |
| Reduced orchestration overhead | Users spend materially less time telling the agent what phase to enter next | Year 1 |
| Artifact alignment | Specs, issues, tests, implementation, and follow-on work remain traceable and mutually consistent after iterative changes | Year 2 |
| Safe escalation | HELIX asks for user input primarily at real judgment boundaries, not because the workflow contract is underspecified | Year 2 |

## Strategic Fit

- **Company Strategy Alignment**: HELIX turns AI-assisted development from ad
  hoc prompting into a durable operating system for software delivery.
- **Resource Availability**: The repo already contains the workflow method,
  tracker, CLI, and skill surfaces needed to make the control loop explicit.
- **Timing**: AI coding tools are already useful, but teams still lack a
  reliable supervisory layer that keeps complex software work coherent over
  time.

## Explicit Non-Goals

- HELIX is not a generic "do everything" agent that replaces product judgment.
- HELIX is not an unbounded autonomous coding loop.
- HELIX is not a chat-only prompt library disconnected from durable tracker
  state.
- HELIX should not force users to remain in autopilot mode when they want to
  intervene directly in a specific workflow layer.
