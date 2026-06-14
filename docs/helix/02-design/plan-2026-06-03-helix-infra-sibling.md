# Plan: helix-infra sibling repo

Status: revised post-codex-review, ready to implement
Author: claude (Opus 4.7)
Reviewer: codex (gpt-5, 2026-06-03)

> **Supersession note (2026-06-14):** This is a historical plan document.
> The `helix-infra` sibling repo was not adopted. The current architecture
> is a single `helix` plugin. Preserved as a record of the IaC methodology
> design work.

## Codex-driven revisions applied (summary)

1. `03-apply` → `03-apply-verify`. Verification is an explicit gate inside the
   activity, not implicit. Required sections include provider-specific
   probes, not just "tofu plan shows no changes."
2. Concern set reworked from generic-IaC names to synaptiq-infra-grounded
   ones; `provider-pinning` and `import-before-modify` folded into broader
   concerns:
   - `state-boundaries` (was state-isolation)
   - `blast-radius-and-rollout` (was blast-radius-control)
   - `credentials-and-state-secrets` (was credentials-management)
   - `resource-ownership-boundary` (NEW — biggest gap codex caught:
     authoritative vs imported vs audit-mirror vs ignore_changes resources)
   - `privileged-access-impact` (NEW — auth, PIM, Graph permissions,
     breakglass paths)
   - `drift-and-verification` (was drift-detection — verification merged in)
3. `runbook` → `module-guide`. Carries module purpose, providers, state key,
   backend, inputs, outputs, remote-state deps, ownership boundaries, import
   rules, apply command, rollback, verification probes. 5 artifacts total.
4. "Tag everything" principle dropped (doesn't fit Entra/Cloudflare-Access
   SaaS surfaces). Replaced with "Verify after apply" — pairs with "plan
   before apply" to close the loop.
5. ADR template lives at `02-plan/artifacts/adr/`; instances are written to
   the consuming repo's `docs/adr/`, not into helix-infra itself.
6. Intent/plan/apply-verify boundaries tightened (see Activities section).
7. synaptiq-infra is the worked example, not baked-in defaults. The example
   is scrubbed of tenant/account IDs and security posture details.
8. Repo stays local (no GitHub push) until exercised on a real change.
9. README + SKILL.md must position helix-infra as "IaC/operator methodology"
   not "HELIX with fewer folders" — needed to resolve activation ambiguity
   when both skills are installed in the same session.

## Problem

HELIX is shaped for product development: 7 activities, 47 artifact types, 49
concerns. The user surveyed three sibling repos (`synaptiq-infra`,
`synaptiq-sales`, `7thsense-ops`) and asked whether HELIX fits. Verdict:

- `synaptiq-infra` (OpenTofu modules, multi-cloud): partial fit — borrow ADRs +
  concerns, skip the methodology. **This plan addresses that gap.**
- `synaptiq-sales`: split — HELIX fits the Python tool, not the content tree.
  Out of scope here.
- `7thsense-ops`: not HELIX-shaped at all. Out of scope here.

Goal: a sibling repo `helix-infra` that supplies the IaC-adapted methodology
the user can install as a skill alongside HELIX, so agents working in
`synaptiq-infra` (and similar IaC repos) get the right artifacts, concerns,
and procedural discipline.

## What we keep from HELIX, what we cut, why

### Keep

- **Skill packaging shape**: `.claude-plugin/marketplace.json` +
  `.claude-plugin/plugin.json` + `skills/helix-infra/SKILL.md`. Same install
  story (`/plugin marketplace add https://github.com/.../helix-infra` →
  `/plugin install helix-infra@helix-infra`).
- **Concerns**: cross-cutting checklist that any change must consider. IaC
  has its own concern set (state, blast radius, credentials, drift).
- **ADRs**: same artifact, same purpose — record non-obvious decisions.
- **Spec-as-contract discipline**: per-module README + an `intent.md` per
  change. The README is the module's spec; the intent is the change's spec.
- **`meta.yml` artifact-type contract**: each artifact has a meta.yml +
  template.md + prompt.md + example.md, validator-checkable. Same shape that
  let HELIX gate `required_sections` against template H2s.
- **Activities as folders under `workflows/activities/<NN-name>/`**:
  same on-disk shape so familiarity transfers.

### Cut

- **7 activities → 3 activities** (intent, plan, apply). Discover/frame/design
  collapse to "intent + plan"; test/build/deploy collapse to "apply"; iterate
  doesn't exist as a phase (steady-state with periodic edits, not iterative
  loops on the same artifact).
- **47 artifacts → 5 artifacts**: change-intent, change-plan, ADR,
  apply-evidence, runbook. No PRD, no FEAT, no user-stories, no
  technical-design — those are project-shaped and infra work is
  change-shaped.
- **AC-IDs (US-{n}-AC{m}) and the AC-traceability scaffolding**: cut. Infra
  changes have acceptance, but it's "the plan applies cleanly + state matches
  intent + no drift", not user-story-derived AC chains.
- **Build-exit verification gate (Playwright/HTTP harness)**: cut. The IaC
  analog is `tofu plan` parity + post-apply state inspection + (optional)
  Terratest. Verification lives in apply-evidence, not a separate phase.
- **49 concerns**: cut to 6 IaC-shaped ones (see Concerns below).
- **Principles list (8 HELIX principles)**: cut to 5 IaC-shaped principles.

### Why

HELIX's load-bearing differentiator is "spec is the contract, code is the
projection, AC traceability is enforced." For IaC, the *.tf files literally
ARE the spec (declarative), and `tofu plan` IS the AC check. The
HELIX-as-shipped scaffolding around spec/code parity is solved by Terraform
itself. What IaC actually needs methodology for is the things Terraform
doesn't enforce: *why* a change is being made, *whether* it considered the
right concerns, *what* gets recorded as a non-obvious decision, and *how*
operators recover when it goes wrong. That's the 5-artifact slim shape.

## The 3 activities

### 01-intent

The "why" of a change. Answers: what's the desired end-state, why is it
changing, what's the success signal, what's the rollback condition. Replaces
HELIX's discover/frame/design for change-sized work.

**Primary artifact**: `change-intent` (one markdown file per change, lives
under `docs/changes/<YYYY-MM-DD>-<slug>.md` in the consuming repo).
Sections:

- Context: what state are we in now
- Desired end-state: what state do we want
- Why now: trigger (compliance, capacity, security, drift remediation)
- Acceptance: how we'll know it landed (specific resources present,
  specific provider state, specific cross-module ref resolves)
- Rollback condition: what signal triggers an unwind, and the unwind path

### 02-plan

The "how" of a change. Answers: which modules change, which providers
change, what's the dependency order, are there non-obvious decisions worth
ADR-ing, what does `tofu plan` say. Replaces HELIX's design/test/build.

**Primary artifacts**:

- `change-plan` — markdown summary of which modules/files change, the
  dependency order, a paste of the plan summary (resource counts, sensitive
  diffs called out), and a checklist of concerns considered (see Concerns
  below).
- `adr` — one ADR per non-obvious decision (provider choice, state-key
  scheme, cross-module boundary). Reused HELIX ADR template; we copy it,
  not import-by-reference, to keep helix-infra independent.

### 03-apply

The "did it work" of a change. Answers: did apply succeed, does post-apply
state match intent, is the runbook still accurate, is there new drift to
clean up. Replaces HELIX's deploy/iterate.

**Primary artifacts**:

- `apply-evidence` — short markdown noting apply timestamp, operator,
  resources created/changed/destroyed counts, a post-apply `tofu plan`
  showing "No changes", and any state-import steps that were required.
- `runbook` — per-module operational doc (how to import existing
  resources, how to roll back, who owns escalation). Updated as part of
  apply, not created fresh each change. (Most modules already have an
  AGENTS.md-style note; runbook formalizes it.)

## The 6 concerns

Each lives at `workflows/concerns/<slug>/{concern.md, practices.md}`,
matching HELIX's shape.

1. **state-isolation** — every module owns its own remote state. Cross-module
   references go through `terraform_remote_state` data sources, never direct.
   Boundary: state file location, not what's in it.

2. **blast-radius-control** — one module per change, one concern per ADR,
   never apply across multiple environments in a single command, never apply
   without inspecting the plan diff first.

3. **credentials-management** — secrets live in a secret manager (1Password,
   Vault, cloud-native secret store) and inject at runtime; never in
   `.tfvars` checked into git; `.tfvars.example` only.

4. **import-before-modify** — existing resources are imported into state
   before any HCL edit that would target them; never `terraform apply` a
   recreated definition over a resource that already exists.

5. **provider-pinning** — `versions.tf` pins exact provider versions
   (`= 5.4.0`, not `~> 5.0`). Upgrades are intentional, ADR-recorded changes.

6. **drift-detection** — `tofu plan` is run regularly (CI cron is fine) to
   catch out-of-band changes; drift findings are filed as new change-intents,
   not silently absorbed.

The exclusion of common HELIX concerns (auth, ux, testing strategy,
observability-as-code) is deliberate: they're either irrelevant (ux) or
they belong to the underlying cloud's documentation (auth/observability for
the specific provider), not the methodology.

## The 5 principles

Lives at `workflows/principles.md`:

1. **Plan before apply** — read the diff before you commit to the change.
2. **Import before modify** — existing infra is imported, not recreated.
3. **State is precious** — isolated per module, remote-backed, secret-wrapped.
4. **Smallest reversible change** — one module per change; one concern per
   ADR.
5. **Tag everything** — every resource carries env/owner/cost-code tags so
   audit, cost attribution, and drift triage are tractable later.

## Skill activation

`skills/helix-infra/SKILL.md` describes when the skill engages:

- The repo contains `*.tf` or `*.tofu` files at any depth.
- The user prompt includes infra-shaped phrases ("add a module", "change the
  DNS zone", "import the existing project", "plan the change", "rotate the
  provider version").
- An explicit `/helix-infra <activity>` invocation: `intent`, `plan`,
  `apply`, `review`.

The skill activates the methodology: it tells the agent to (a) produce or
update the change-intent artifact, (b) walk the 6 concerns, (c) propose ADRs
for non-obvious decisions, (d) post-apply produce evidence and update the
runbook.

## Repo structure

```
helix-infra/
├── .claude-plugin/
│   ├── marketplace.json
│   └── plugin.json
├── AGENTS.md
├── CLAUDE.md
├── README.md
├── docs/
│   └── why/
│       └── _index.md          # 1-page rationale (the thesis)
├── skills/
│   └── helix-infra/
│       └── SKILL.md
└── workflows/
    ├── principles.md
    ├── activities/
    │   ├── 01-intent/
    │   │   ├── README.md
    │   │   └── artifacts/
    │   │       └── change-intent/
    │   │           ├── meta.yml
    │   │           ├── prompt.md
    │   │           ├── template.md
    │   │           └── example.md
    │   ├── 02-plan/
    │   │   ├── README.md
    │   │   └── artifacts/
    │   │       ├── change-plan/
    │   │       │   ├── meta.yml
    │   │       │   ├── prompt.md
    │   │       │   ├── template.md
    │   │       │   └── example.md
    │   │       └── adr/
    │   │           ├── meta.yml
    │   │           ├── prompt.md
    │   │           ├── template.md
    │   │           └── example.md
    │   └── 03-apply/
    │       ├── README.md
    │       └── artifacts/
    │           ├── apply-evidence/
    │           │   ├── meta.yml
    │           │   ├── prompt.md
    │           │   ├── template.md
    │           │   └── example.md
    │           └── runbook/
    │               ├── meta.yml
    │               ├── prompt.md
    │               ├── template.md
    │               └── example.md
    └── concerns/
        ├── state-isolation/
        │   ├── concern.md
        │   └── practices.md
        ├── blast-radius-control/
        │   ├── concern.md
        │   └── practices.md
        ├── credentials-management/
        │   ├── concern.md
        │   └── practices.md
        ├── import-before-modify/
        │   ├── concern.md
        │   └── practices.md
        ├── provider-pinning/
        │   ├── concern.md
        │   └── practices.md
        └── drift-detection/
            ├── concern.md
            └── practices.md
```

File count: 32 (counting only created files; excludes the implicit dirs).

## Implementation plan (workflow phases)

A workflow drives this end-to-end. Six phases, ~17 agents total.

### Phase 1 — Scaffold (1 agent)

Create the directory tree, write the bootstrap files: `README.md`,
`AGENTS.md`, `CLAUDE.md`, `.claude-plugin/marketplace.json`,
`.claude-plugin/plugin.json`, `docs/why/_index.md`,
`workflows/principles.md`, `skills/helix-infra/SKILL.md`. `git init` + first
commit.

### Phase 2 — Activities (parallel, 3 agents)

One agent per activity (`01-intent`, `02-plan`, `03-apply`). Each writes the
activity's `README.md` + every artifact directory under it (meta.yml +
prompt.md + template.md + example.md, with the example drawn from a
representative real `synaptiq-infra` change scenario).

### Phase 3 — Concerns (parallel, 6 agents)

One agent per concern. Each writes `concern.md` (the rule + boundary +
artifact-impact) and `practices.md` (the activity-keyed checklist:
intent/plan/apply rows). Reference real synaptiq-infra examples where the
concern bit.

### Phase 4 — Schema validator (1 agent)

Port HELIX's `scripts/helix_validate_artifact_meta.py` to validate
helix-infra's artifact-type meta.yml ⇄ template.md H2 contracts. Same
validator semantics, scoped to helix-infra's tree.

### Phase 5 — Worked example (1 agent)

Pick a representative pending change in `synaptiq-infra` (an actual real
example like "add a new module for X") and produce a full change-intent +
change-plan + (if needed) ADR pass against it, committed to
`docs/examples/synaptiq-infra-add-module/`. This proves the methodology is
usable on real material.

### Phase 6 — Verify (1 agent)

Run the schema validator. Walk every concern, confirm each has both
concern.md and practices.md with required structure. Walk every artifact,
confirm meta.yml required_sections matches template.md H2 set. Validate
SKILL.md activation triggers parse cleanly. Final report.

## Verification

A successful helix-infra build means:

- The validator (port of HELIX's) returns 0 across the 5 artifact types.
- A real synaptiq-infra change can be walked through the 3 activities and
  produces all expected artifacts in the right shape.
- The skill installs cleanly via `/plugin marketplace add` (smoke test
  against the marketplace.json once the repo is on a remote — out of scope
  for this build; we stop at "ready for first push").
- The user reads README.md, walks the worked example, and can answer "would
  I use this on a real change?" without needing more explanation.

## Open questions for codex

1. Is 3 activities the right cut, or should "apply" split into "apply +
   verify" to make the post-apply evidence its own step? (Argument for: it
   would mirror HELIX's build/iterate split. Argument against: each apply IS
   the verification — splitting adds ceremony without adding rigor.)

2. Should ADR live under `02-plan/artifacts/` or as a top-level cross-cutting
   artifact (like HELIX does)? HELIX has it at activity level but it's
   referenced everywhere. (Lean: top-level, since ADRs can come out of
   intent OR plan OR apply.)

3. Is the 6-concern set complete enough, or are there obvious omissions for
   IaC? Candidates considered and rejected: cost-awareness (lean: belongs in
   change-intent's "why now" + change-plan checklist, not a standalone
   concern at this scope); compliance-mapping (lean: belongs in
   change-intent as an acceptance row when relevant, not a standalone
   concern at this MVP scope).

4. Is `synaptiq-infra` the right MVP target, or should helix-infra stay
   generic and not bake in synaptiq examples? (Lean: real examples beat
   abstract ones; `synaptiq-infra` examples will be the most useful proof.)

5. Should this repo be public from day one (so it can be marketplace-added
   like HELIX) or stay private until the methodology is exercised? (Lean:
   stay local; only push when the user wants to install it via
   `/plugin marketplace add`.)

## Out of scope

- A separate `helix-sales` or `helix-ops` repo for the other two surveyed
  repos. Conclusions there were "split" and "not HELIX-shaped"; addressing
  those is separate work.
- Genie / Codex / Copilot install pages. helix-infra is initially
  claude-only; multi-runtime parity is later.
- A demo cast or screencast. Not until the methodology is exercised.
- Automated drift-detection scheduling (CI cron). Concern documents the
  practice; the consuming repo's CI implements it.
