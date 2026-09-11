---
type: plan
status: proposed
created: 2026-05-30
owner: erik
revisions:
  - codex-review-2026-05-30
  - codex-review-2026-05-30-pass-2
  - opus-review-2026-05-30
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
- Orthogonality (after subtracting by-design slot competition — architecture-style, language-runtime, e2e-framework, demo-framework — and the phase-sibling hierarchy/slice patterns under test, deploy, and iterate): ~12 artifact pairs and ~10 concern pairs are real scope-bleed candidates worth a synthesis pass.
- Systemic issues that affect many items (worth a single sweep, not per-slug fixes):
  - `dependencies.yaml` absent for 48/48 artifact types; `meta.yml.relationships` carries the data instead. Either ratify the convention or generate the file. **Read-time vs write-time consideration**: consumers (`helix_align_check`, `reconcile-alignment`) currently expect a flat dependencies projection; either decision needs a consumer-side compatibility note.
  - `meta.yml.validation.required_sections` drifts from `template.md` headings in at least 8 artifact types (`data-prd`, `feasibility-study`, `parking-lot`, `security-requirements`, `proof-of-concept`, `tech-spike`, `validation-checklist`, `metrics-dashboard`). A schema lint would catch every instance.
  - 14 concerns ship an empty `ADR References` section header — either drop the header or populate it with real ADR IDs.
  - 10 concerns organize `practices.md` by topic instead of by HELIX activity (`auth-local-sessions`, `caching-strategy`, `classic-layered`, `cqrs`, `domain-driven-design`, `enterprise-application-patterns`, `hexagonal-architecture`, `mcp-server`, `onion-architecture`, `sample-data`). Decide whether activity-keying is required or whether topic + quality-gates suffices.
  - **Structural verbosity root cause**: the concern file shape (`concern.md` Boundary + `practices.md` "Boundary with neighbors" + Constraints/Drift Signals/Quality Gates) mandates three sections that naturally restate the boundary. Editorial trimming partially regresses without a shape fix. The catalog contract must define section ownership so the boundary is stated once and the other sections reference-not-restate.

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

- All 48 artifact types lack `dependencies.yaml`. Either codify "relationships live in `meta.yml.relationships`" as the convention (preferred — single source) and update the rubric, or generate a `dependencies.yaml` projection from `meta.yml` as part of `helix_align_check`. Either way, document the consumer-side compatibility note.
- `concerns` artifact-type meta validation requires `active_concerns`/`area_labels` sections — template headings read `Active Concerns`/`Area Labels`. Confirm whether the schema validator slugifies before comparing; if not, this is silent drift.
- `data-prd` and `data-architecture` reference Databricks resource docs under inconsistent filenames (`databricks-lakehouse-medallion-architecture.md` vs `databricks-medallion-architecture.md`). Pick one and update both.
- Orphan file: `workflows/artifact-types/security-tests/security-test.go.template` (17k) sits beside `template.md` unreferenced from meta. Either wire it in (multi-template artifact) or delete.
- Orphan files: `workflows/artifact-types/test-suites/{unit,integration}-test.go.template` — same problem, language-biased to Go.

### Concerns completeness items

- 14 concerns have an empty `ADR References` section header (`a11y-wcag-aa`, `demo-asciinema`, `demo-playwright`, `design-patterns-gof`, `e2e-kind`, `e2e-playwright`, `go-std`, `hugo-hextra`, `i18n-icu`, `k8s-kind`, `o11y-otel`, `python-uv`, `rust-cargo`, `scala-sbt`). Decide policy: drop the header when empty, or require at least one anchor ADR per concern.
- `monitoring-setup` declares `informs: metrics-dashboard` but `metrics-dashboard` is an iterate-phase artifact type, not a deploy sibling. Verify the cross-phase link is intentional.
- `stakeholder-map` meta references a `communication-plan` artifact that does not exist in any phase. Either create it or drop the reference (handled in Phase 1 catalog contract).

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

The recurring root cause: meta.yml carries taxonomies and process metadata that duplicate prompt/template content. The fix is structural — define what meta.yml is for (machine validation + relationships only) and move guidance/taxonomy back to prompt/template. **This is contract work, not editorial cleanup**, and lives in Phase 1.

### Concerns worth tightening

The verbosity pattern in concerns is uniform: Boundary section in `concern.md` is restated in `practices.md`'s "Boundary with neighbors" section, then Constraints / Drift Signals / Quality Gates restate the same MUSTs in three formats. Per the structural diagnosis in Findings, this is a file-shape problem the contract must fix — not an editorial pass.

Highest-leverage targets (once the file shape is fixed, these regress without per-doc editing):
- `authorization-model`, `multi-tenancy`, `resilience`, `enterprise-integration-patterns`, `relational-data-modeling`, `verification`, `usage-metering`, `ux-radix`, `twelve-factor`, `event-sourcing`, `deployment-topology` — all suffer the same Boundary-restated-3x pattern.
- `demo-asciinema` (~350 lines with full Dockerfile/tmux script examples) and `hugo-hextra` (extensive Hugo config + spacing-rules + CSS) cross from concern-spec into tutorial.
- `api-style`, `concurrency-model`, `enterprise-application-patterns` over-explain textbook concepts; trim to load-bearing distinctions.

## Orthogonality concerns

The raw mutual-suspicion lists (63 artifact pairs, 64 concern pairs) are misleading because most pairs are by-design slot competition (architecture-style: `onion`/`clean`/`hexagonal`/`classic-layered`; language-runtime: `go-std`/`python-uv`/`rust-cargo`/`scala-sbt`/`typescript-bun`; e2e-framework: `e2e-kind`/`e2e-playwright`; demo-framework: `demo-asciinema`/`demo-playwright`). These are intentional and mutually exclusive at composition time. Below are the pairs that aren't slot-competition and where the descriptions confirm shared scope.

Each remaining overlap is classified as one of:

- **Slot**: mutually exclusive at composition time; readers pick one. No action.
- **Inheritance**: one is a specialization (is-a) of the other (e.g., `k8s-kind` of `deployment-topology`). Express the inheritance; don't restate the parent's body.
- **Slice**: one is a scoped view onto the other, or they are zoom levels / consumers of a shared substrate (e.g., `security-metrics` is a metrics-dashboard slice; `architecture` / `solution-design` / `technical-design` are zoom levels of the same system; `resilience` and `verification` consume `o11y-otel`'s telemetry). Link, don't restate.
- **Defect**: real ambiguity that needs an ADR-grade decision (e.g., `parking-lot` vs `feature-registry` — merge with status enum?).

The exit criterion for the orthogonality phases below is that every remaining overlap is classified as one of the four; defect-class items each have an ADR or a recorded merge/split decision.

### Real artifact-type orthogonality concerns

| Pair | Phase | Class | Overlap | Recommendation |
|---|---|---|---|---|
| `prd` / `data-prd` | frame | defect (likely inheritance after ADR) | data-prd is a PRD specialization; both define problem/goals/requirements. data-prd's `required_sections` even drift from template. The variant-vs-sibling question is open until an ADR lands | Phase 2 ADR decides; then either restructure data-prd as a delta document or collapse with a `kind: data` switch |
| `feature-specification` / `user-stories` | frame | defect (AC ownership ambiguity) | Both carry acceptance criteria with stable IDs; the AC-ID requirement is restated 5× in user-stories alone. The boundary "FEAT owns FR-n; stories own AC-IDs" isn't load-bearing today — that's an ownership defect, not a slice | Phase 2 ADR confirms AC lives in user-stories; restructure feature-specification to declare functional areas and decomposition only, not AC. Then Phase 3 removes AC-ID restatement from FEAT prompt and template |
| `feature-registry` / `parking-lot` | frame | defect | Registry of FEATs vs registry of deferred FEATs — same shape, different status | Phase 2 ADR: merge into one registry with status enum, or keep separate with explicit lifecycle |
| `risk-register` / `threat-model` | frame | slice | Both score uncertain bad events with owners and mitigations; threat-model is the security slice | scope-split (already declared): make the cross-link load-bearing — threat-model entries auto-feed risk-register security-class rows |
| `compliance-requirements` / `security-requirements` / `threat-model` | frame | slice | Triangle: regs→controls→threats. data classification + risk tables overlap | narrow each: compliance = regs+controls map; security-requirements = testable control ACs; threat-model = STRIDE+mitigation owners. Document the traceability chain (regs → controls → threats) in each prompt |
| `architecture` / `solution-design` / `technical-design` | design | slice | Three-level zoom (system→feature→story). A TD does not substitute for an architecture, so this is not inheritance — they are scoped views of the same system at different granularity. Boundary asserted but template content blurs (architecture mentions feature decomposition; solution-design mentions component changes) | keep three levels; add a "what belongs at each level" matrix to the design-phase README; enforce via reconcile-alignment |
| `data-architecture` / `data-design` | design | inheritance | Pipeline-level (medallion/governance) vs entity-level (model/store/access) — boundary asserted but template ventures across | narrow data-architecture to platform/pipeline; data-design to logical model. Trim data-architecture template |
| `proof-of-concept` / `tech-spike` | design | slice | PoC = working evidence, spike = investigation answer. Prompt disambiguates well; meta required_sections drift confuses it | keep distinct; fix the meta/template drift in both |
| `contract` / `technical-design` | design | slice | Contract is interface; TD is implementation of one story. Both declare interfaces | narrow: contract is implementation-independent and shared across consumers; TD's interface section references-not-defines the contract |
| `test-plan` / `story-test-plan` / `test-suites` / `test-procedures` | test | slice | Four-way: strategy / per-story / suite inventory / runner procedures — each a different scope of the same testing surface | scope-split is fine; cut the role-restating preambles |
| `monitoring-setup` / `runbook` | deploy | defect (resolved by edit) | Both currently define incident-response routing — an ownership collision, not a scoped view | Phase 2 ADR confirms monitoring-setup does not own incident-response routing; Phase 3 removes the "Incident Response" section from monitoring-setup template. monitoring-setup owns detection/SLI/SLO/routing inputs; runbook owns response/recovery procedures |
| `metric-definition` / `metrics-dashboard` / `security-metrics` / `improvement-backlog` | iterate | slice | Four-way is healthy if metric = contract, dashboard = current values, security-metrics = security slice of dashboard, backlog = next actions | confirm security-metrics is a dashboard slice (not parallel); document in the 06-iterate README |

### Real concern orthogonality concerns

| Pair | Class | Overlap | Recommendation |
|---|---|---|---|
| `auth` / `auth-local-sessions` / `authorization-model` / `multi-tenancy` / `security-owasp` | inheritance + slice (with `admin-console` and `unity-catalog` as material neighbors) | Five-way cluster with mutual suspicion across every pair, plus two cross-tree neighbors. The real ownership lines are clear but currently restated 3× per file with overlapping coverage. Two items currently fall through the gaps: **audit-logging policy** (what gets logged on authz denial) and **session-token semantics** (issuance / rotation / revocation) sit between auth, authorization-model, and security-owasp without a clear owner | Family README with an **explicit ownership table**: `auth` owns principal/session/account bootstrap **and session-token semantics**; `authorization-model` owns permission semantics (RBAC/ABAC/ReBAC); `multi-tenancy` owns the tenant predicate; `security-owasp` owns hardening **and audit-logging policy** (what to log on authz denial). `admin-console` references `auth` for operator-workflow gates; `unity-catalog` references `authorization-model` for catalog grants composing with app-layer authz. Keep the concerns separate so ownership stays distinct; the README replaces the restated per-concern boundary prose |
| `testing` / `verification` | slice | Both about evidence of correctness; boundary asserted (testing = strategy, verification = end-to-end evidence gate). Both verbose with boundary restatements | keep distinct; remove restated boundary prose; cross-link by ID |
| `e2e-playwright` / `demo-playwright` | slice | Both Playwright-driven recording; e2e is verification, demo is reel. They occupy different concern families and can compose, so this is not slot competition | scope-split is correct; the demo-reel content in `e2e-playwright` should be removed (delegated to demo-playwright) |
| `frontend-architecture` / `react-nextjs` / `ux-radix` / `a11y-wcag-aa` | inheritance + defect | Four-way frontend cluster: structural patterns / framework slot / interaction primitives / accessibility. `react-nextjs` and `ux-radix` both prescribe shadcn/Radix usage | confirmed scope-split, plus a defect: Phase 2 ADR picks one owner of the shadcn/Radix prescription |
| `concurrency-model` / `resilience` | slice | Both about graceful degradation under load; idempotency/bounding repeated in both | narrow: concurrency-model = in-process execution; resilience = cross-process call-path. Already asserted; remove neighbor-restatement prose |
| `caching-strategy` / `resilience` | slice | Cache as fallback overlaps with resilience timeout/bulkhead patterns | confirm cache is a performance/staleness concern, not a stability one; remove resilience cross-references |
| `o11y-otel` / `resilience` / `verification` | slice | Telemetry is consumed by resilience signals and verification evidence; the two consumers are slices on the telemetry pipeline, not specializations of observability | o11y owns the telemetry pipeline as canonical; resilience and verification reference-and-cite the telemetry it produces. Document the consumer relationship in o11y-otel's Boundary section |
| `enterprise-integration-patterns` / `event-sourcing` / `cqrs` | slice | Three messaging-flavored concerns with shared idempotency/correlation MUSTs. Event-sourcing and CQRS compose, so treating them as a slot would mislead | keep distinct (different decision levels); cut the duplicated MUST lists; document the composition explicitly |
| `databricks-apps` / `databricks-declarative-pipelines` / `unity-catalog` | slice | Platform cluster — apps run on the runtime, pipelines produce data into UC, UC governs access. These compose; UC is not a parent of apps | document the composition in each concern's Boundary once; reference-not-restate |
| `deployment-topology` / `k8s-kind` (inheritance) plus `twelve-factor` (cross-cutting neighbor) | mixed: inheritance + cross-cutting | Topology decides units; k8s-kind is the local-K8s implementation (true inheritance). Twelve-factor governs per-process operability regardless of topology choice — that's cross-cutting, not a child of topology | document `deployment-topology` → `k8s-kind` as the implementation arrow; cite `twelve-factor` as a neighbor concern, not a child; cut twelve-factor's deployment-topology restatement |

### Slot competition (NOT orthogonality concerns)

These are correctly designed mutual-exclusion sets and need no action beyond documenting the slot in each concern (already done):

- architecture-style slot: `onion-architecture` / `clean-architecture` / `hexagonal-architecture` / `classic-layered`
- language-runtime slot: `go-std` / `python-uv` / `rust-cargo` / `scala-sbt` / `typescript-bun`
- e2e-framework slot: `e2e-kind` / `e2e-playwright`
- demo-framework slot: `demo-asciinema` / `demo-playwright`

## Remediation plan

Three phases ordered by leverage. Each phase is independently shippable. Earlier shapes (5 phases → 4 phases) were revised after two codex passes and an opus review: the dedicated concision phase was cut because once the catalog contract codifies "stated once" and ownership tables eliminate the structural cause of restatement, what remains is an editorial PR, not a phase; ADRs were moved BEFORE mechanical edits because the boundary tables and prose trims depend on the ownership decisions the ADRs land.

### Phase 1 — Catalog contract

Goal: define and enforce the catalog's machine-readable contract — `meta.yml` shape, `template.md` validation rules, dependencies encoding, concern file shape, resource references — as a single coherent policy. The contract folds in the editorial rules earlier plans deferred to a separate concision phase, so the contract itself prevents the restatement that phase was going to clean up.

The phase has two tracks that run in parallel: catalog policy ADRs (may take time to settle) and mechanical schema-and-housekeeping fixes (can ship without waiting on the ADRs).

**Track A — Catalog policy ADRs**:

- **Dependencies encoding**: ratify `meta.yml.relationships` as canonical (preferred — single source) and update the rubric, or generate `dependencies.yaml` from `meta.yml` as a build step. The ADR must include a consumer-side compatibility note for `helix_align_check` and `reconcile-alignment`, which currently expect a flat dependencies projection.
- **Practices format**: HELIX-activity-keyed `practices.md`, or topic + quality-gates. The 10 currently-topic-keyed concerns (`auth-local-sessions`, `caching-strategy`, `classic-layered`, `cqrs`, `domain-driven-design`, `enterprise-application-patterns`, `hexagonal-architecture`, `mcp-server`, `onion-architecture`, `sample-data`) await this decision.
- **Concern file shape**: define section ownership across `concern.md` and `practices.md` so the boundary is stated once. Today's shape mandates three places that all restate it (concern.md Boundary, practices.md "Boundary with neighbors", and the Constraints/Drift Signals/Quality Gates that re-encode the same MUSTs). The contract should pick a canonical home (Boundary in `concern.md`; Constraints / Drift Signals / Quality Gates in `practices.md` reference-not-restate) and enforce it.
- **Editorial rules folded in from the dropped concision phase**: `meta.yml` is for machine validation + relationships only — no taxonomies, no process metadata duplicated from prompt/template. Prompt Quality Checklist and template Review Checklist are not both present. Tutorial-grade code blocks (Dockerfiles, full configs, CSS) move to resource docs, not concern.md.
- **Empty `ADR References` headers**: policy — drop when empty, or require at least one anchor ADR per concern.

**Track B — Mechanical contract enforcement** (no ADR dependency, but minimal validator alignment only — structural edits to artifact types covered by Phase 2 ADRs wait for those ADRs):

- Reconcile `meta.yml.validation.required_sections` ↔ `template.md` H2s across the 8 drifted artifact types (`data-prd`, `feasibility-study`, `parking-lot`, `security-requirements`, `proof-of-concept`, `tech-spike`, `validation-checklist`, `metrics-dashboard`); fix the `concerns` slugification ambiguity. **For `data-prd`**: minimal validator alignment only — the broader structural question (kind-switch vs sibling) waits for the Phase 2 PRD/data-PRD ADR.
- Handle orphan templates (`security-tests/security-test.go.template`, `test-suites/{unit,integration}-test.go.template`): wire into meta as multi-template, or delete.
- Fix resource-doc filename inconsistencies (`databricks-lakehouse-medallion-architecture.md` vs `databricks-medallion-architecture.md`).
- Resolve `stakeholder-map`'s stale reference to a non-existent `communication-plan` artifact: drop or fix the reference. Creating a new `communication-plan` artifact type is out of scope for this plan (see Out of scope); if the concept is needed, that's a separate scoped follow-up.
- Build `scripts/helix_validate_artifact_meta.py` that runs `required_sections` against `template.md` H2s for every artifact type; wire into CI.

Exit criterion: Track A ADRs landed (or explicit deferral with the open question recorded); Track B validator passes for all 48 artifact types; the rubric stops flagging dependencies as missing; CI gate prevents regression; the catalog contract codifies the editorial rules that prior plans treated as a separate concision phase.

### Phase 2 — Design decisions requiring ADRs

Goal: resolve the defect-class overlaps before the mechanical edits in Phase 3 codify boundaries that depend on them.

Scope — defect-class items:

- `prd` / `data-prd`: ADR on whether data-prd is a `kind: data` variant of `prd` or a sibling specialization. Drives Phase 3's data-prd edits.
- `feature-specification` / `user-stories`: ADR confirming AC lives in user-stories (the de-facto state) and removing AC-ID ownership from feature-specification. Drives Phase 3's restatement removal.
- `feature-registry` / `parking-lot`: ADR on whether parking-lot is a status filter on feature-registry (collapse) or remains a separate lifecycle artifact.
- `react-nextjs` / `ux-radix` (shadcn/Radix prescription overlap): ADR on which concern owns the prescription.
- `monitoring-setup` / `runbook`: ADR confirming monitoring-setup does not own incident-response routing. Drives Phase 3's removal of the "Incident Response" section from the monitoring-setup template.
- Cross-phase `informs` edges: ADR on whether `monitoring-setup` → `metrics-dashboard` and similar cross-phase relationships are valid (yes/no/conditional).
- Architecture-style slot occupants: ADR (or explicit deferral) on whether the four concerns stay separate or collapse into one concern with four variants. This one is borderline-out-of-scope (questions the slot model itself) — flag as open.

Exit criterion: each defect has either a landed ADR or an explicit deferral with the open question logged; the ADRs feed directly into Phase 3's edit list.

### Phase 3 — Mechanical boundary reconciliation

Goal: with the catalog contract in place and the ADRs landed, codify the boundaries the audit identified through ownership tables, phase READMEs, and prose trims. With the prior phases complete, this is the "edit phase" — no new ownership debate, just translations from the ADRs and contract into the concern + artifact tree.

Scope — slot, inheritance, and slice cases plus the ADR-driven defect edits:

**Artifact pairs driven by Phase 2 ADRs**: `prd`/`data-prd` (per ADR outcome), `feature-specification`/`user-stories` (per ADR outcome — remove AC-ID restatement from FEAT prompt + template), `feature-registry`/`parking-lot` (per ADR), `monitoring-setup`/`runbook` (remove "Incident Response" section from monitoring-setup template), `react-nextjs`/`ux-radix` (per ADR).

**Artifact pairs not requiring ADRs**: the frame security triangle (`compliance-requirements`/`security-requirements`/`threat-model` — narrow each, link by ID), the design zoom-stack (`architecture`/`solution-design`/`technical-design` — add the "what belongs at each level" matrix to the design-phase README), `data-architecture`/`data-design` (narrow architecture to platform; trim template), `contract`/`technical-design` (TD's interface section references the contract), the test four-way (cut role-restating preambles), the iterate metric four-way (document the slice relationship in the 06-iterate README).

**Concerns**: the auth family — write the family README with the ownership table from the Orthogonality section, including the audit-logging policy and session-token semantics ownership grid. Keep the concerns separate. Then remove the per-concern restated boundary prose. Also:
- `testing`/`verification`: cross-link by ID, remove restated boundary prose.
- `e2e-playwright`/`demo-playwright`: remove demo-reel content from e2e-playwright.
- `concurrency-model`/`resilience`: in-process vs cross-process; remove neighbor-restatement prose.
- `caching-strategy`/`resilience`: remove resilience cross-references; confirm cache is a performance/staleness concern.
- `o11y-otel`/`resilience`/`verification`: document the telemetry pipeline ownership in o11y-otel's Boundary; resilience and verification reference-and-cite.
- The messaging three-way (`enterprise-integration-patterns` / `event-sourcing` / `cqrs`): cut duplicated MUST lists; document the composition explicitly.
- The Databricks three-way (`databricks-apps` / `databricks-declarative-pipelines` / `unity-catalog`): document the composition in each concern's Boundary once.
- The deploy cluster (`deployment-topology` / `k8s-kind` / `twelve-factor`): document the inheritance from `deployment-topology` to `k8s-kind`; cite `twelve-factor` as a cross-cutting neighbor, not a child; cut twelve-factor's deployment-topology restatement.

Exit criterion: every overlap pair listed in the Orthogonality section is classified as slot, inheritance, slice, or defect; slot/inheritance/slice cases each have either a phase-README boundary entry or a one-line cross-reference replacing restated prose; the audit re-run leaves no unclassified mutual-suspicion in these clusters; defect cases have shipped their ADR-driven edits.

## Open questions

1. Is `meta.yml.relationships` the canonical encoding of artifact dependencies, with `dependencies.yaml` either dropped or generated? What's the read-time vs write-time compatibility plan for consumers? (Phase 1 ADR.)
2. Must concern `practices.md` be HELIX-activity-keyed, or is topic + quality-gates acceptable? (Phase 1 ADR.)
3. What is the canonical concern file shape — where does Boundary live, and what reference-not-restates it? (Phase 1 ADR.)
4. Empty `ADR References` headers: drop when empty, or require at least one anchor ADR per concern? (Phase 1 ADR.)
5. Should `parking-lot` collapse into `feature-registry` with a status enum? (Phase 2 ADR.)
6. Cross-phase reference policy: are `informs` edges that span phases valid? (Phase 2 ADR.)
7. Architecture-style slot occupants (onion/clean/hexagonal/classic-layered) sustain substantial content overlap. Is the per-occupant concern doc the right shape, or should the slot have one concern with four variants? (Phase 2 ADR, possibly deferred.)

## Out of scope

- New artifact types or concerns (the inventory is treated as fixed for this pass).
- The frame/design bulge (17 frame + 11 design artifacts vs 1 build, 4 deploy, 4 iterate) is a methodology question, not an audit finding — handled elsewhere.
- Runtime tooling (DDx, ddx try, helix_align_check enhancements) beyond what Phase 1's catalog-contract validator and the dependencies-encoding decision require.
- Concern-of-iterate / concern-of-build composition models — flagged in Phase 2 questions but resolved separately.
- Resource library (`docs/resources/`) audit. Several drift findings (filename mismatches, missing referenced resources) implicate the library, but auditing it is its own task.

## Review log

- **2026-05-30 (opus pass)**: Independent opus review. Findings and disposition:
  - **Reordered phases**: ADRs (now Phase 2) moved before mechanical edits (now Phase 3). The earlier order would have written boundary tables and prose trims in Phase 2 that Phase 3 ADRs could invalidate (auth family README, data-prd structure).
  - **Cut the standalone concision phase**: folded its editorial rules into Phase 1's catalog contract. Once the contract codifies "stated once" and Phase 3's ownership tables eliminate the structural cause of restatement, what remains is an editorial PR, not a phase. The earlier "60% reduction in verbose count" exit criterion was metric theater (the audit's verbose count was a structured-output rating, not a reproducible measurement).
  - **Phase 1 internal split into parallel tracks** (catalog policy ADRs + mechanical contract enforcement). The mechanical fixes no longer wait on the ADRs.
  - **Reclassifications** (four-way):
    - `feature-specification`/`user-stories`: was `slice`. Reclassified as `defect (AC ownership ambiguity)`. The boundary "FEAT owns FR-n; stories own AC-IDs" isn't load-bearing today — AC-IDs are restated 5× in user-stories alone, and the boundary doesn't survive the restatement.
    - `architecture`/`solution-design`/`technical-design`: was `inheritance`. Reclassified as `slice`. A TD does not substitute for an architecture (fails the is-a substitution test); they're zoom levels of the same system.
    - `databricks-apps`/`databricks-declarative-pipelines`/`unity-catalog`: was `inheritance`. Reclassified as `slice`. They compose; UC is not a parent of apps. Same error pattern as the o11y cluster corrected in codex pass 2.
    - `deployment-topology`/`twelve-factor`/`k8s-kind`: was `inheritance` as a single group. Split into `deployment-topology` → `k8s-kind` as true inheritance plus `twelve-factor` as cross-cutting neighbor; the twelve-factor leg isn't a child of topology.
    - `monitoring-setup`/`runbook`: was `slice`. Reclassified as `defect (resolved by edit)`. Both currently define incident-response routing — that's ownership collision, not a scoped view; the recommended edit resolves the defect.
  - **Auth cluster ownership table extended**: added `audit-logging policy` (what gets logged on authz denial — owned by `security-owasp`) and `session-token semantics` (issuance / rotation / revocation — owned by `auth`). Both fell through the gaps in the prior table.
  - **Structural verbosity diagnosis added**: the concern file shape itself mandates three sections that restate the boundary. Editorial trimming partially regresses without a shape fix. Moved from Phase 4 (editorial) to Phase 1 (contract).
  - **Dependencies-encoding ADR scope extended**: must include a consumer-side compatibility note for `helix_align_check` and `reconcile-alignment` which currently expect a flat dependencies projection.
  - **Worst sentences fixed**: dropped the "no methodology debate" claim (which conflicted with the practices-format prerequisite); rephrased the "~80% content overlap by necessity" Open Questions framing; dropped the "60% reduction in verbose count" theater metric along with the concision phase.

- **2026-05-30 (codex pass 2)**: confirmed all prior six findings addressed. Six new sharper issues incorporated:
  - `prd`/`data-prd` was inheritance in the table but defect in Phase 3 routing. Reclassified as `defect (likely inheritance after ADR)`.
  - `o11y-otel`/`resilience`/`verification` was misclassified as inheritance. Telemetry is consumed by the others, not specialized from observability. Reclassified as `slice`.
  - `enterprise-integration-patterns`/`event-sourcing`/`cqrs` was `slot + slice`. ES and CQRS compose, so `slot` misleads. Now `slice` only.
  - Phase 2 exit criterion partly reintroduced the brittle "no new mutual-suspicion" wording — replaced with "no unclassified mutual-suspicion in these clusters".
  - Phase 2 scope referenced "concern-of-iterate README" while the same area is marked out-of-scope at the bottom. Renamed to "06-iterate README".
  - `stakeholder-map` → missing `communication-plan` reference had no phase assignment. Added to Phase 1 catalog-contract scope.
  - Worst-sentence fix: the systemic-issues list called test/deploy/iterate "phase-sibling slot competition." Those are hierarchy/slice patterns, not slots. Reworded.

- **2026-05-30 (codex pass 1)**: First codex advisory review. Findings and disposition:
  - **Merge old Phases 1 + 2** into "Catalog contract" — adopted. Schema validation, dependencies encoding, orphan templates, and resource references are one policy area, not two streams.
  - **Split old Phase 3** into mechanical-edits vs ADR-grade decisions — adopted. (Subsequently reordered in the opus pass so ADRs come first.)
  - **Drop dedicated Phase 5; fold practices-format decision into Phase 2 as a prerequisite** — adopted. (Subsequently relocated to Phase 1 in the opus pass as a catalog-contract decision.)
  - **Replace brittle "no new mutual-suspicion pairs" exit criterion** with "every remaining overlap classified as slot, inheritance, slice, or defect" — adopted.
  - **Auth cluster recommendation revised**: drop "merge into single identity-and-access concern family doc"; instead, **family README with explicit ownership table** while keeping the concerns separate. Added `admin-console` and `unity-catalog` as material neighbors.
  - **Internal count drift** (58 → 49 concerns, "8 with topic-keyed practices" actually 10) — fixed.
