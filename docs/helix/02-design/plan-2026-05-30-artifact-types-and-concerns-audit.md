---
type: plan
status: proposed
created: 2026-05-30
owner: erik
revisions:
  - codex-review-2026-05-30
---

# Artifact-type and concern audit — gaps and remediation plan

## Why

A first-pass audit rated every HELIX artifact type and concern on file completeness, prose concision, and orthogonality against siblings. The audit confirmed there are no stub artifacts and no missing files, but it surfaced (a) systemic schema drift between `meta.yml` validation and `template.md` headings, (b) a near-universal absence of `dependencies.yaml` though `meta.yml.relationships` already encodes the same data, (c) practices files in the concerns tree that organize by topic instead of by HELIX activity, and (d) a small set of real orthogonality questions distinct from the many "expected" slot-sibling overlaps. This plan turns those into a sequenced cleanup.

## Inventory

- 48 artifact types across 7 phases (00-discover: 5, 01-frame: 17, 02-design: 11, 03-test: 5, 04-build: 1, 05-deploy: 4, 06-iterate: 4 — confirming the long-known frame/design bulge).
- 49 concerns (architecture-style: 4 slot occupants; language-runtime: 5 slot occupants; e2e-framework: 2; demo: 2; auth/authz/multi-tenancy/security cluster: 5; Databricks cluster: 3; the rest cross-cutting).

## Findings overview

- Completeness: 48/48 artifact types rated `complete`. 49/49 concerns rated `complete`. There are no stubs.
- Concision: 11/48 artifact types rated `verbose`; 22/49 concerns rated `verbose`. Nothing rated `bloated`.
- Orthogonality (raw): 63 mutually-suspected artifact pairs and 64 mutually-suspected concern pairs.
- Orthogonality (after subtracting by-design slot competition — architecture-style, language-runtime, e2e-framework, demo-framework, phase-sibling test/deploy/iterate clusters): ~12 artifact pairs and ~10 concern pairs are real scope-bleed candidates worth a synthesis pass.
- Systemic issues that affect many items (worth a single sweep, not per-slug fixes):
  - `dependencies.yaml` absent for 48/48 artifact types; `meta.yml.relationships` carries the data instead. Either ratify the convention or generate the file.
  - `meta.yml.validation.required_sections` drifts from `template.md` headings in at least 8 artifact types (`data-prd`, `feasibility-study`, `parking-lot`, `security-requirements`, `proof-of-concept`, `tech-spike`, `validation-checklist`, `metrics-dashboard`). A schema lint would catch every instance.
  - 14 concerns ship an empty `ADR References` section header — either drop the header or populate it with real ADR IDs.
  - 10 concerns organize `practices.md` by topic instead of by HELIX activity (`auth-local-sessions`, `caching-strategy`, `classic-layered`, `cqrs`, `domain-driven-design`, `enterprise-application-patterns`, `hexagonal-architecture`, `mcp-server`, `onion-architecture`, `sample-data`). Decide whether activity-keying is required or whether topic + quality-gates suffices.

## Completeness gaps

No artifact or concern was rated `thin` or `stub`. The gaps that matter are not "missing content" — they are schema/format gaps that risk silent rot. Worth addressing:

### Schema drift between meta.yml.validation and template.md (artifact types)

| Slug | Phase | Drift | Severity | Remediation |
|---|---|---|---|---|
| `data-prd` | frame | `required_sections` names (`executive_summary`, `goals_and_objectives`) don't map to template H2s; resource references disagree between meta and prompt | moderate | Reconcile section IDs against template; pick one resource-doc name |
| `feasibility-study` | frame | meta requires `Decision Framework` section; template omits it (example has it) | moderate | Add `Decision Framework` H2 to template |
| `parking-lot` | frame | meta lists `purpose` section; template has none (example does) | minor | Add `Purpose` H2 to template, or drop from meta |
| `security-requirements` | frame | meta requires `Security User Stories`, `Acceptance Criteria`, `Risk Assessment`; template has `Required Controls`, `Security Risks` | moderate | Rename meta sections to match template (or vice versa) |
| `proof-of-concept` | design | meta requires `testing`/`findings`/`conclusions`/`artifacts`; template uses `Results`/`Analysis` | moderate | Align names; add missing `Artifacts` section |
| `tech-spike` | design | template `Analysis` not in meta required_sections | minor | Add `analysis` to meta or rename template heading |
| `validation-checklist` | frame | meta requires 6 sections that don't match template's `Go/No-Go Gates`/`Result`/`Required Follow-Up` | major | Rewrite meta validation to match template (schema lint would fail today) |
| `metrics-dashboard` | iterate | template has `Interpretation Rules`; meta required_sections omits it | minor | Add to meta required_sections |

Severity rule: `major` = schema lint would fail in current state if it ran; `moderate` = consumer would have to special-case; `minor` = cosmetic.

### Cross-cutting completeness items

- All 48 artifact types lack `dependencies.yaml`. Either codify "relationships live in `meta.yml.relationships`" as the convention (preferred — single source) and update the rubric, or generate a `dependencies.yaml` projection from `meta.yml` as part of `helix_align_check`.
- `concerns` artifact-type meta validation requires `active_concerns`/`area_labels` sections — template headings read `Active Concerns`/`Area Labels`. Confirm whether the schema validator slugifies before comparing; if not, this is silent drift.
- `data-prd` and `data-architecture` reference Databricks resource docs under inconsistent filenames (`databricks-lakehouse-medallion-architecture.md` vs `databricks-medallion-architecture.md`). Pick one and update both.
- Orphan file: `workflows/artifact-types/security-tests/security-test.go.template` (17k) sits beside `template.md` unreferenced from meta. Either wire it in (multi-template artifact) or delete.
- Orphan files: `workflows/artifact-types/test-suites/{unit,integration}-test.go.template` — same problem, language-biased to Go.

### Concerns completeness items

- 14 concerns have an empty `ADR References` section header (`a11y-wcag-aa`, `demo-asciinema`, `demo-playwright`, `design-patterns-gof`, `e2e-kind`, `e2e-playwright`, `go-std`, `hugo-hextra`, `i18n-icu`, `k8s-kind`, `o11y-otel`, `python-uv`, `rust-cargo`, `scala-sbt`). Decide policy: drop the header when empty, or require at least one anchor ADR per concern.
- `monitoring-setup` declares `informs: metrics-dashboard` but `metrics-dashboard` is an iterate-phase artifact type, not a deploy sibling. Verify the cross-phase link is intentional.
- `stakeholder-map` meta references a `communication-plan` artifact that does not exist in any phase. Either create it or drop the reference.

## Concision gaps

Selective — only items where verbosity creates real risk of internal contradiction or maintenance burden.

### Artifact types worth tightening

| Slug | Phase | What to cut | Severity |
|---|---|---|---|
| `data-prd` | frame | Three restatements of focus/role/completion in prompt; Databricks platform-substitution table belongs in resources, not the generation prompt; Quality table + Data Quality Expectations note overlap | moderate |
| `feasibility-study` | frame | meta.yml is 217 lines; `feasibility_dimensions`, `risk_categories`, `decision_framework`, `success_indicators` largely duplicate template/prompt and are not consumed by any tooling | moderate |
| `feature-specification` | frame | Decomposition test concept restated 4+ times across prompt and template; "WHAT not HOW" framing appears in meta quality_checks, prompt Key Principles, Boundary Test, and template Review Checklist | moderate |
| `user-stories` | frame | AC stable-ID requirement restated 5 times (meta quality_checks, meta automated_checks, prompt section, prompt blocking checklist, template) | moderate |
| `stakeholder-map` | frame | meta.yml `engagement_levels`/`raci_rules`/`monitoring`/`review_triggers`/`tags` likely unused by tooling | minor |
| `data-architecture` | design | Template ~340 lines with hardcoded numeric examples ($/GB, DBU counts) that read as filler; Platform Substitution table duplicates resource docs | moderate |
| `proof-of-concept` | design | meta carries 5 `poc_types` variants, `development_phases`, `workflow.approvers` that duplicate prompt/template guidance | minor |
| `data-quality-expectations` | test | Bronze/Silver/Gold structure repeated with near-duplicate SQL snippets per layer; failure-handling table restates per-layer severity | moderate |
| `story-test-plan` | test | `@covers` citation rule restated three times across prompt, template preamble (~24 lines of doctrine), and review checklist | moderate |
| `risk-register` | frame | 190-line meta with monitoring/reporting/dashboards sections likely unused | minor |

The recurring root cause: meta.yml carries taxonomies and process metadata that duplicate prompt/template content. The fix is structural — define what meta.yml is for (machine validation + relationships only) and move guidance/taxonomy back to prompt/template.

### Concerns worth tightening

The verbosity pattern in concerns is more uniform: Boundary section in `concern.md` is restated in `practices.md`'s "Boundary with neighbors" section, then Constraints / Drift Signals / Quality Gates restate the same MUSTs in three formats. Highest-leverage targets:

- `authorization-model`, `multi-tenancy`, `resilience`, `enterprise-integration-patterns`, `relational-data-modeling`, `verification`, `usage-metering`, `ux-radix`, `twelve-factor`, `event-sourcing`, `deployment-topology` — all suffer the same Boundary-restated-3x pattern.
- `demo-asciinema` (~350 lines with full Dockerfile/tmux script examples) and `hugo-hextra` (extensive Hugo config + spacing-rules + CSS) cross from concern-spec into tutorial.
- `api-style`, `concurrency-model`, `enterprise-application-patterns` over-explain textbook concepts; trim to load-bearing distinctions.

A single editorial pass with a "Boundary stated once; Constraints/Drift Signals/Quality Gates do not restate it" rule would resolve most of these.

## Orthogonality concerns

The raw mutual-suspicion lists (63 artifact pairs, 64 concern pairs) are misleading because most pairs are by-design slot competition (architecture-style: `onion`/`clean`/`hexagonal`/`classic-layered`; language-runtime: `go-std`/`python-uv`/`rust-cargo`/`scala-sbt`/`typescript-bun`; e2e-framework: `e2e-kind`/`e2e-playwright`; demo-framework: `demo-asciinema`/`demo-playwright`). These are intentional and mutually exclusive at composition time. Below are the pairs that aren't slot-competition and where the descriptions confirm shared scope.

Each remaining overlap is classified as one of:

- **Slot**: mutually exclusive at composition time; readers pick one. No action.
- **Inheritance**: one is a specialization of the other (e.g., `data-prd` of `prd`). Express the inheritance; don't restate the parent's body.
- **Slice**: one is a scoped view onto the other (e.g., `security-metrics` is a metrics-dashboard slice; `threat-model` is the security slice of `risk-register`). Link, don't restate.
- **Defect**: real ambiguity that needs an ADR-grade decision (e.g., `parking-lot` vs `feature-registry` — merge with status enum?).

The exit criterion for the orthogonality phases below is that every remaining overlap is classified as one of the four; defect-class items each have an ADR or a recorded merge/split decision.

### Real artifact-type orthogonality concerns

| Pair | Phase | Class | Overlap | Recommendation |
|---|---|---|---|---|
| `prd` / `data-prd` | frame | inheritance | data-prd is a PRD specialization; both define problem/goals/requirements. data-prd's `required_sections` even drift from template | Express inheritance: data-prd declares only data-specific deltas; or merge with a `kind: data` switch (defect-class candidate) |
| `feature-specification` / `user-stories` | frame | slice | Both carry acceptance criteria with stable IDs; FEAT decomposition test restated in both | narrow: FEAT owns FR-n + functional areas; stories own AC-IDs and personas. Already mostly asserted; tighten by removing AC-ID restatements from FEAT prompt |
| `feature-registry` / `parking-lot` | frame | defect | Registry of FEATs vs registry of deferred FEATs — same shape, different status | ADR: merge into one registry with status enum, or keep separate with explicit lifecycle |
| `risk-register` / `threat-model` | frame | slice | Both score uncertain bad events with owners and mitigations; threat-model is the security slice | scope-split (already declared): make the cross-link load-bearing — threat-model entries auto-feed risk-register security-class rows |
| `compliance-requirements` / `security-requirements` / `threat-model` | frame | slice | Triangle: regs→controls→threats. data classification + risk tables overlap | narrow each: compliance = regs+controls map; security-requirements = testable control ACs; threat-model = STRIDE+mitigation owners. Document the inheritance chain in each prompt |
| `architecture` / `solution-design` / `technical-design` | design | inheritance | Three-level zoom (system→feature→story). Boundary asserted but template content blurs (architecture mentions feature decomposition; solution-design mentions component changes) | keep three levels; add a "what belongs at each level" matrix in design-phase README; enforce via reconcile-alignment |
| `data-architecture` / `data-design` | design | inheritance | Pipeline-level (medallion/governance) vs entity-level (model/store/access) — boundary asserted but template ventures across | narrow data-architecture to platform/pipeline; data-design to logical model. Trim data-architecture template |
| `proof-of-concept` / `tech-spike` | design | slice | PoC = working evidence, spike = investigation answer. Prompt disambiguates well; meta required_sections drift confuses it | keep distinct; fix the meta/template drift in both |
| `contract` / `technical-design` | design | slice | Contract is interface; TD is implementation of one story. Both declare interfaces | narrow: contract is implementation-independent and shared across consumers; TD's interface section references-not-defines the contract |
| `test-plan` / `story-test-plan` / `test-suites` / `test-procedures` | test | inheritance | Four-way: strategy / per-story / suite inventory / runner procedures. Boundaries asserted; verbose because each restates the others' role | scope-split is fine; cut the role-restating preambles |
| `monitoring-setup` / `runbook` | deploy | slice | Both define incident-response routing | narrow: monitoring-setup owns detection/SLI/SLO/routing inputs; runbook owns response/recovery procedures. Remove "Incident Response" from monitoring-setup template |
| `metric-definition` / `metrics-dashboard` / `security-metrics` / `improvement-backlog` | iterate | slice | Four-way is healthy if metric = contract, dashboard = current values, security-metrics = security slice of dashboard, backlog = next actions | confirm security-metrics is a dashboard slice (not parallel); document in concern-of-iterate README |

### Real concern orthogonality concerns

| Pair | Class | Overlap | Recommendation |
|---|---|---|---|
| `auth` / `auth-local-sessions` / `authorization-model` / `multi-tenancy` / `security-owasp` | inheritance + slice (with `admin-console` and `unity-catalog` as material neighbors) | Five-way cluster with mutual suspicion across every pair, plus two cross-tree neighbors. The real ownership lines are clear but currently restated 3x per file with overlapping coverage | Family README with an **explicit ownership table** — `auth` owns principal/session/account bootstrap; `authorization-model` owns permission semantics (RBAC/ABAC/ReBAC); `multi-tenancy` owns the tenant predicate; `security-owasp` owns hardening. `admin-console` references `auth` for operator-workflow gates; `unity-catalog` references `authorization-model` for catalog grants composing with app-layer authz. Keep the concerns separate so ownership stays distinct; the README replaces the restated per-concern boundary prose |
| `testing` / `verification` | slice | Both about evidence of correctness; boundary asserted (testing = strategy, verification = end-to-end evidence gate). Both verbose with boundary restatements | keep distinct; remove restated boundary prose; cross-link by ID |
| `e2e-playwright` / `demo-playwright` | slot + slice | Both Playwright-driven recording; e2e is verification, demo is reel | scope-split is correct; the demo-reel content in `e2e-playwright` should be removed (delegated to demo-playwright) |
| `frontend-architecture` / `react-nextjs` / `ux-radix` / `a11y-wcag-aa` | inheritance + defect | Four-way frontend cluster: structural patterns / framework slot / interaction primitives / accessibility. `react-nextjs` and `ux-radix` both prescribe shadcn/Radix usage | confirmed scope-split, plus a defect: pick one owner of shadcn/Radix prescription |
| `concurrency-model` / `resilience` | slice | Both about graceful degradation under load; idempotency/bounding repeated in both | narrow: concurrency-model = in-process execution; resilience = cross-process call-path. Already asserted; remove neighbor-restatement prose |
| `caching-strategy` / `resilience` | slice | Cache as fallback overlaps with resilience timeout/bulkhead patterns | confirm cache is a performance/staleness concern, not a stability one; remove resilience cross-references |
| `o11y-otel` / `resilience` / `verification` | inheritance | Telemetry feeds resilience signals and verification evidence | scope-split: o11y owns the telemetry pipeline; resilience consumes it; verification cites it. Document in o11y-otel |
| `enterprise-integration-patterns` / `event-sourcing` / `cqrs` | slot + slice | Three messaging-flavored concerns with shared idempotency/correlation MUSTs | keep distinct (different decision levels); cut the duplicated MUST lists |
| `databricks-apps` / `databricks-declarative-pipelines` / `unity-catalog` | inheritance | Platform cluster — apps run on the runtime, pipelines produce data into UC, UC governs access | confirm three are layered; document the layering in each concern's Boundary once |
| `deployment-topology` / `twelve-factor` / `k8s-kind` | inheritance | Topology decides units, twelve-factor governs per-process operability, k8s-kind is the local-K8s implementation | confirm three-level scope; cut twelve-factor's deployment-topology restatement |

### Slot competition (NOT orthogonality concerns)

These are correctly designed mutual-exclusion sets and need no action beyond documenting the slot in each concern (already done):

- architecture-style slot: `onion-architecture` / `clean-architecture` / `hexagonal-architecture` / `classic-layered`
- language-runtime slot: `go-std` / `python-uv` / `rust-cargo` / `scala-sbt` / `typescript-bun`
- e2e-framework slot: `e2e-kind` / `e2e-playwright`
- demo-framework slot: `demo-asciinema` / `demo-playwright`

## Remediation plan

Four phases ordered by leverage. Each phase is independently shippable. The earlier five-phase shape (Schema sweep → Dependencies policy → Orthogonality → Concision → Practices format) was revised after codex review: phases 1+2 merged into one catalog-contract pass; phase 3 split into the mechanical and ADR-grade slices; phase 5 collapsed into a prerequisite for the orthogonality work.

### Phase 1 — Catalog contract (was Phases 1 + 2)

Goal: define and enforce the catalog's machine-readable contract — `meta.yml` shape, `template.md` validation rules, dependencies encoding, resource references — as a single coherent policy, then bring the 48 artifact types into compliance.

Scope (one phase, multiple deliverables):
- Reconcile `meta.yml.validation.required_sections` ↔ `template.md` H2s across the 8 drifted artifact types (`data-prd`, `feasibility-study`, `parking-lot`, `security-requirements`, `proof-of-concept`, `tech-spike`, `validation-checklist`, `metrics-dashboard`); fix the `concerns` slugification ambiguity.
- Decide the dependencies-encoding question: ratify `meta.yml.relationships` as canonical (preferred — single source) and update the rubric, or generate `dependencies.yaml` from `meta.yml` as a build step. Record the decision in an ADR.
- Handle orphan templates (`security-tests/security-test.go.template`, `test-suites/{unit,integration}-test.go.template`): wire into meta as multi-template, or delete.
- Fix resource-doc filename inconsistencies (`databricks-lakehouse-medallion-architecture.md` vs `databricks-medallion-architecture.md`).
- Add a `scripts/helix_validate_artifact_meta.py` check that runs `required_sections` against `template.md` H2s for every artifact type and exits 0; wire into CI.

Exit criterion: the validator passes for all 48 artifact types; the rubric stops flagging dependencies as missing; ADR records the encoding decision; CI gate prevents regression.

### Phase 2 — Mechanical boundary reconciliation (was the easy half of Phase 3, plus the practices-format prerequisite)

Goal: resolve the orthogonality cases that need no methodology debate — they need a boundary table, prose trims, and cross-references. Includes the prerequisite practices-format decision so the concerns-tree work can land here.

Prerequisite (decide before edits begin): concern `practices.md` is HELIX-activity-keyed, or topic + quality-gates suffices. Codify the decision in the rubric. This unblocks both the boundary-table edits and Phase 3's concision pass on the 10 topic-keyed concerns (`auth-local-sessions`, `caching-strategy`, `classic-layered`, `cqrs`, `domain-driven-design`, `enterprise-application-patterns`, `hexagonal-architecture`, `mcp-server`, `onion-architecture`, `sample-data`).

Scope — items classified as slot, inheritance, or slice (no methodology change required):
- Artifact pairs: `feature-specification`/`user-stories` (AC-ID restatement trim), the frame security triangle (`compliance-requirements`/`security-requirements`/`threat-model` — narrow each, link by ID), the design zoom-stack (`architecture`/`solution-design`/`technical-design` — add "what belongs at each level" matrix in design-phase README), `data-architecture`/`data-design` (narrow architecture to platform; trim template), `contract`/`technical-design` (TD's interface section references contract), `monitoring-setup`/`runbook` (remove "Incident Response" from monitoring-setup template), the test four-way (cut role-restating preambles), the iterate metric four-way (document in concern-of-iterate README).
- Concerns: the auth family — write the **family README with the ownership table** (auth = principal/session/account bootstrap; authorization-model = permission semantics; multi-tenancy = tenant predicate; security-owasp = hardening; admin-console = operator-workflow gates referencing auth; unity-catalog = catalog grants composing with authorization-model). Keep concerns separate. Then remove the per-concern restated boundary prose. Also: `testing`/`verification` (cross-link by ID), `e2e-playwright`/`demo-playwright` (remove demo-reel content from e2e-playwright), `concurrency-model`/`resilience` (in-process vs cross-process), `caching-strategy`/`resilience` (remove resilience cross-refs), `o11y-otel`/`resilience`/`verification` (telemetry pipeline ownership), the messaging three-way (cut duplicated MUSTs), the Databricks three-way (layering note in each Boundary), the deploy three-way (cut twelve-factor's deployment-topology restatement).

Exit criterion: every overlap pair listed in the Orthogonality section is classified as slot, inheritance, slice, or defect; slot/inheritance/slice cases each have either a phase-README boundary entry or a one-line cross-reference replacing restated prose; the audit re-run flags no new mutual-suspicion within these clusters; defect cases are unblocked (handed to Phase 3).

### Phase 3 — Design decisions requiring ADRs (was the hard half of Phase 3)

Goal: resolve the orthogonality cases that require a methodology decision, not just an edit. Each lands an ADR before the edit.

Scope — defect-class overlaps:
- `prd` / `data-prd`: ADR on whether data-prd is a `kind: data` variant of `prd` or a sibling specialization. Then either collapse with a switch or restructure data-prd as a delta-document.
- `feature-registry` / `parking-lot`: ADR on whether parking-lot is a status filter on feature-registry (collapse) or remains a separate lifecycle artifact.
- `react-nextjs` / `ux-radix` (shadcn/Radix prescription overlap): ADR on which concern owns the prescription.
- Cross-phase `informs` edges: ADR on whether `monitoring-setup` → `metrics-dashboard` and similar cross-phase relationships are valid (yes/no/conditional).
- Architecture-style slot shape: ADR on whether the four occupants stay as separate concerns or collapse into one concern with four variants. This one is borderline-out-of-scope (questions the slot model itself) — flag as open.

Exit criterion: each defect has either a landed ADR + executed structural change, or an explicit deferral with the open question logged.

### Phase 4 — Concision pass

Goal: tighten the 11 verbose artifact types and 22 verbose concerns by enforcing a single "stated once" rule per claim. Phases 1 and 2 will have already resolved the structural verbosity (boundary prose, schema/process duplication); this phase handles what remains.

Scope: top targets named in "Concision gaps" above. The auth/identity family practices files become tractable once the family README from Phase 2 exists.

Editorial rules:
- `meta.yml` is for machine validation + relationships only — no taxonomies or process metadata duplicated from prompt/template (codified by Phase 1's ADR).
- Boundary stated once per file; Constraints / Drift Signals / Quality Gates do not restate it.
- Prompt Quality Checklist and template Review Checklist are not both present — pick one home.
- Tutorial-grade code blocks (Dockerfiles, full configs, CSS) move to resource docs, not concern.md.

Exit criterion: re-audit drops `verbose` count by at least 60% across both trees; no remaining `bloated` ratings.

## Open questions

1. Is `meta.yml.relationships` the canonical encoding of artifact dependencies, with `dependencies.yaml` either dropped or generated? (Blocks Phase 1's ADR.)
2. Must concern `practices.md` be HELIX-activity-keyed, or is topic + quality-gates acceptable? (Blocks Phase 2's prerequisite.)
3. Empty `ADR References` headers: drop when empty, or require at least one anchor ADR per concern?
4. Should `parking-lot` collapse into `feature-registry` with a status enum? (Phase 3 ADR.)
5. Cross-phase reference policy: are `informs` edges that span phases valid? (Phase 3 ADR.)
6. Architecture-style slot occupants (onion/clean/hexagonal/classic-layered) sustain ~80% content overlap by necessity. Is the per-occupant concern doc the right shape, or should the slot have one concern with four variants? (Phase 3 ADR; possibly out-of-scope.)

## Out of scope

- New artifact types or concerns (the inventory is treated as fixed for this pass).
- The frame/design bulge (17 frame + 11 design artifacts vs 1 build, 4 deploy, 4 iterate) is a methodology question, not an audit finding — handled elsewhere.
- Runtime tooling (DDx, ddx try, helix_align_check enhancements) beyond what Phase 1's catalog-contract validator and the dependencies-encoding decision require.
- Concern-of-iterate / concern-of-build composition models — flagged in Phase 3 questions but resolved separately.
- Resource library (`docs/resources/`) audit. Several drift findings (filename mismatches, missing referenced resources) implicate the library, but auditing it is its own task.

## Review log

- 2026-05-30: codex advisory review. Findings and disposition:
  - **Merge Phases 1 + 2** into "Catalog contract" — adopted. Schema validation, dependencies encoding, orphan templates, and resource references are one policy area, not two streams.
  - **Split Phase 3** into mechanical-edits vs ADR-grade decisions — adopted. New Phase 2 handles slot/inheritance/slice overlaps; new Phase 3 handles defect-class items with an ADR per decision.
  - **Drop dedicated Phase 5; fold practices-format decision into Phase 2 as a prerequisite** — adopted.
  - **Replace brittle "no new mutual-suspicion pairs" exit criterion** with "every remaining overlap classified as slot, inheritance, slice, or defect" — adopted (the four-way classification is the new orthogonality vocabulary).
  - **Auth cluster recommendation revised**: drop "merge into single identity-and-access concern family doc"; instead, **family README with explicit ownership table** while keeping the concerns separate. Codex argued that merging risks blurring ownership again. Adopted. Added `admin-console` and `unity-catalog` as material neighbors per codex.
  - **Internal count drift** (the earlier user-facing summary said 58 concerns; the plan inventory is 49 and the repo has 49; the "8 concerns with topic-keyed practices" listed 10) — fixed in the inventory line and the findings overview. The "58" came from an incorrect aggregation in the audit workflow's structured output; the plan body was correct.
