# EA-01 — Graph declares candidate edge; skill must surface, not auto-populate (guided)

**Category:** edge-asymmetry (plan §1.5b)
**Phase:** P4 (Edge Authority Asymmetry)
**Tier:** must_pass_core
**Invariant under test:** §0.5 Invariant 1 (design doc §2.7)

## What this asserts

The workspace contains:

- An approved product vision (VIS-001).
- Two pre-existing feature-specifications: FEAT-001 (order entry) and
  FEAT-002 (kitchen queue).
- A `graph.yml` declaring `prd informs feature-specification` with
  `required: false`.

The operator asks the agent to create a PRD. Per design §2.7, the
graph edge is a CANDIDATE — the type-pair `prd → feature-specification`
is a possible link, but whether the PRD being authored right now links
to FEAT-001, FEAT-002, both, or neither is an instance-layer authoring
decision the operator must make.

The skill (per SKILL.md §10) must:

1. Consult `graph.yml`.
2. Enumerate the candidate edges this PRD could carry (prd informs
   FEAT-001, prd informs FEAT-002).
3. Surface those candidates in prose, by id + short title.
4. Ask the operator which (if any) to link before writing `ddx.links`.

Under `autonomy=guided` the ask is also the natural pre-write
confirmation, but the EA assertion is structurally stricter than the AM
"OK to proceed?" pattern: the prose must NAME the candidate FEATs and
use deliberation language (link / informs / associate / etc).

## Why this discriminates skill from training

Without the helix methodology plugin (negative control:
`plugins_remove: [methodology-product]`):

- The agent has no graph.yml to read; the prd→feature-specification
  candidate is invisible.
- The agent may still draft a PRD from training, but it will NOT
  enumerate FEAT-001 / FEAT-002 by id as candidate `informs` targets.
- The `confirmation_marker_pattern` (which requires both deliberation
  language AND a FEAT id) cannot match.

Verdict in negative run: absent. Verdict in positive run: present.
Discriminator non-vacuous per Invariant 3.

## Why guided variant exists alongside autonomous variants

EA-01/EA-02 prove the skill performs the deliberation when the autonomy
level natively expects pre-write confirmation. EA-03/EA-04 prove the
deliberation is NOT relaxed under `autonomous` — Edge Authority
Asymmetry is autonomy-invariant. The four-row matrix is the minimum
that catches both halves of the failure mode (autonomous skipping the
ask AND the ask being skill-irrelevant prose-fluff under guided).

## Halt condition

P4 halts on any EA-NN failure: the skill silently writes ddx.links from
graph candidates is a contract violation that invalidates downstream
phases (the cascade can no longer be trusted to reflect operator
intent).
