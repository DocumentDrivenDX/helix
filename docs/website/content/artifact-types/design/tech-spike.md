---
title: "Technical Spike"
linkTitle: "Technical Spike"
slug: tech-spike
activity: "Design"
artifactRole: "supporting"
weight: 18
generated: true
---

## Purpose

Time-boxed investigation that answers one technical question with evidence
before implementation.

Two scopes, set in frontmatter as `ddx.scope`. The default is a project's
spike and ends in a recommendation. `reusable` is a spike published as
knowledge, for example in a technology atlas: it answers one open question
of a component profile (a link of kind `answers` carrying the question's
number), runs on public inputs anyone can obtain, records its test setup
and how to reproduce it, says which reader views the result changes, and
recommends nothing. A profile cites it as a source of class `measured`.

## Example

<details open>
<summary>Show a worked example of this artifact</summary>

``````markdown
---
ddx:
  id: example.tech-spike.depositmatch
  authoring:
    home: repo
  depends_on:
    - example.product-vision.depositmatch
    - example.data-design.depositmatch
    - example.security-architecture.depositmatch
---

# Technical Spike: CSV Formula Neutralization

**Spike ID**: SPIKE-001 | **Lead**: Platform engineer | **Time Budget**: 1 day | **Status**: Completed

## Objective

**Technical Question**: Can DepositMatch safely import and re-export client bank
CSV data without allowing spreadsheet formula injection to survive into exports?

**Goals**:
- [x] Identify the risky cell prefixes and encodings common in CSV injection.
- [x] Test whether import-time normalization alone is enough.
- [x] Compare import-time neutralization with export-time neutralization.

**Success Criteria**: Evidence from fixture files shows which control prevents
formula execution in exported review logs.

**Out of Scope**: Full CSV parser replacement, production import UI, antivirus
scanning, and complete bank-format coverage.

## Hypothesis

**Primary**: Export-time neutralization is required because source values may be
stored for auditability and later exported in a different context.

**Assumptions**:
- Source CSVs are untrusted restricted data.
- Reviewers may open exported logs in spreadsheet software.
- The pilot only needs UTF-8 CSV fixtures from three target bank exports.

**Expected Outcome**: Keep raw source values restricted for audit references,
store normalized values for matching, and neutralize risky cells at every CSV
export boundary.

## Approach

**Method**: Minimal implementation with malicious fixtures.

**Activities**:
| Day | Activity | Objective |
|-----|----------|-----------|
| 1 | Build fixture CSVs with `=`, `+`, `-`, `@`, tab-prefixed, and CR-prefixed values | Exercise known formula-entry patterns |
| 1 | Run import normalization and export generation with and without neutralization | Compare control placement |
| 1 | Open outputs in spreadsheet software and inspect stored values | Confirm whether formulas execute |

## Findings

**FINDING 1**: Import-time schema validation is necessary but insufficient.
- **Evidence**: The parser rejected malformed rows and unsupported encodings,
  but valid text fields containing `=cmd`-style values still remained valid
  strings after normalization.
- **Implications**: Validation protects parser behavior. It does not by itself
  protect downstream spreadsheet interpretation.

**FINDING 2**: Export-time neutralization prevented formula execution in all
pilot fixtures.
- **Evidence**: Prefixing risky exported cells with a single quote caused the
  test spreadsheets to display the value as text for all six fixture patterns.
- **Implications**: Every CSV export path needs the same safe-cell function.

**FINDING 3**: Mutating raw source values at import would weaken auditability.
- **Evidence**: When raw values were rewritten during import, support could no
  longer compare the normalized record against the original bank export without
  a separate source attachment.
- **Implications**: Keep raw source data restricted and retained according to
  policy. Neutralize only when writing customer-controlled CSV output.

### Measurements

| Metric | Import Neutralization | Export Neutralization | Notes |
|--------|-----------------------|-----------------------|-------|
| Blocks formula execution in export fixtures | Yes | Yes | Both worked for tested patterns |
| Preserves raw source evidence | No | Yes | Raw import mutation loses fidelity |
| Centralizes customer-output control | No | Yes | Export helper covers review-log downloads |
| Requires every export path to opt in | No | Yes | Add test coverage for all CSV exporters |

## Analysis

**Hypothesis**: CONFIRMED.
**Rationale**: Formula risk appears when restricted stored values cross into a
customer-controlled spreadsheet context. Export-time neutralization protects
that boundary while preserving raw source evidence for audit and support.

### Risks

| Risk | Prob | Impact | Mitigation |
|------|------|--------|------------|
| Future CSV export bypasses the safe-cell helper | Medium | High | Add a shared export helper and test every CSV exporter |
| Bank-specific encodings introduce new edge cases | Medium | Medium | Expand fixture set when Research Plan sample intake completes |
| Spreadsheet behavior varies by tool/version | Low | Medium | Document tested tools and keep fixture-based regression tests |

## Conclusions

**Primary Conclusion**: DepositMatch should preserve raw source values in
restricted storage and neutralize risky cells at every CSV export boundary.

**Confidence**: Medium.

**Limitations**: The spike used pilot fixture files and two spreadsheet tools.
It did not exhaustively test every bank export format or spreadsheet version.

## Recommendations

**RECOMMENDATION**: Add a shared CSV export helper that neutralizes cells
beginning with formula-risk prefixes, require all CSV exports to use it, and add
security tests for the malicious fixture set.

- **Rationale**: The control sits at the trust boundary where spreadsheet
  interpretation becomes possible and preserves source-data auditability.
- **Next Steps**: Update Security Architecture control mapping, add
  `security-tests` coverage for malicious CSV fixtures, and create a Technical
  Design task for the shared export helper.
- **Concern Impact**: Reinforces the security concern that source CSVs are
  untrusted restricted data. No ADR is needed unless the team chooses to mutate
  source values at import instead.

## Artifacts

- `fixtures/csv/formula-injection/*.csv`: malicious CSV fixture set.
- `notes/csv-export-neutralization.md`: spreadsheet behavior observations and
  tested tool versions.
- `prototype/safe_csv_export.rb`: throwaway export helper used to compare
  neutralization strategies.
``````

</details>

## Reference

<table class="helix-reference-table">
<tbody>
<tr><th>Activity</th><td><a href="../../../reference/glossary/activities/"><strong>Design</strong></a> — Decide how to build it. Capture trade-offs, contracts, and architecture decisions.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/02-design/spikes/</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Informs</th><td><a href="../../../artifact-types/design/architecture/">Architecture</a><br><a href="../../../artifact-types/design/adr/">ADR</a><br><a href="../../../artifact-types/design/solution-design/">Solution Design</a><br><a href="../../../artifact-types/build/implementation-plan/">Implementation Plan</a><br><a href="../../../artifact-types/design/contract/">Contract</a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Technical Spike Generation Prompt&#10;Use the spike to answer one technical question with evidence.&#10;&#10;## Reference Anchors&#10;&#10;Use these local resource summaries as grounding:&#10;&#10;- `docs/resources/safe-spikes.md` grounds spikes as bounded experiments that&#10;  reduce uncertainty before implementation.&#10;- `docs/resources/agile-alliance-sizing-spikes.md` grounds spikes as visible,&#10;  time-boxed learning work rather than hidden delivery work.&#10;&#10;## Create this when&#10;For an **unmatched capability, an active-concern conflict, or an operator-marked&#10;unknown**, the capability&#x27;s **top 1-3 design-defining decisions** (API shape, data&#10;model, pricing/cost, security/permissions, operational guarantees, or&#10;decomposition) are **assumed rather than evidenced**. &quot;known/low-risk&quot; requires&#10;evidence (operator statement, governing artifact, existing implementation,&#10;docs/API proof, or a completed spike), not model familiarity, and not because a&#10;mechanism was picked or a provider named. Spike the assumed decision **even when a&#10;provider is chosen and its live integration is deferred** (deferral de-risks&#10;integration timing, not the decision). An operator-marked &quot;spike/unknown&quot; is&#10;authoritative. See the anti-reframe check in&#10;`workflows/references/concern-resolution.md` (step 3a). For a **business** unknown&#10;a technical spike can&#x27;t answer (e.g. pricing), record guidance-needed or a&#10;blocked spike instead.&#10;&#10;## Focus&#10;- State the question, hypothesis, and method.&#10;- Keep the investigation small and measurable.&#10;- Separate spike evidence from production implementation.&#10;- End with findings, limitations, and a recommendation that updates design,&#10;  creates follow-up work, or stops the approach.&#10;&#10;## Reusable scope&#10;&#10;For `ddx.scope: reusable`, a spike published as knowledge (a technology&#10;atlas keeps them under `spikes/`):&#10;&#10;- **Answer one open question of one profile.** Link the [[component-profile]]&#10;  with kind `answers` and the question&#x27;s number from its Open Questions&#10;  table, pinned to the revision read.&#10;- **Use public inputs only.** Anyone can rerun it from the repository. A&#10;  spike that needs a client&#x27;s systems or data, or names a project, is not&#10;  reusable and stays in that project&#x27;s graph.&#10;- **Record the Test Setup in full,** because the result speaks only for the&#10;  configuration measured: version, environment, settings, data, and date.&#10;- **Report, do not advise.** Findings, the conclusion, and its limits. No&#10;  Recommendations section; a position paper or decision brief draws advice.&#10;- **Say which views the result changes** in the profile: Risk &amp; Compliance,&#10;  Finance, IT Operations, Apps Dev, or No change.&#10;- **Make it reproducible.** Scripts in the repository, commands in order.&#10;  The profile then cites the spike as a source of class `measured`.&#10;&#10;## Completion Criteria&#10;- The uncertainty is reduced.&#10;- Evidence is documented.&#10;- The recommendation is actionable and scoped to the evidence.&#10;- Any remaining uncertainty is named.</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---&#10;ddx:&#10;  id: SPIKE-XXX&#10;  # scope: reusable   # a spike anyone can rerun from public inputs; see Scope kinds&#10;  authoring:&#10;    home: repo&#10;  # links:&#10;  #   - {id: &lt;profile id&gt;, kind: answers, question: &lt;open question number&gt;, rev: &lt;pinned revision&gt;}&#10;---&#10;&#10;# Technical Spike: {{spike_title}}&#10;&#10;**Spike ID**: {{spike_id}} | **Lead**: {{spike_lead}} | **Time Budget**: {{time_budget}} | **Status**: [In Progress | Completed]&#10;&#10;**Scope kinds** (`ddx.scope`). The default is a project&#x27;s spike: this&#10;template without Views Affected, with Test Setup and Reproduction optional.&#10;`reusable` is a spike published as knowledge, for example in a technology&#10;atlas: it runs on public inputs anyone can obtain, names no project or&#10;client, and recommends nothing. It requires Test Setup, Views Affected, and&#10;Reproduction, and omits Recommendations and Artifacts. A profile cites it as&#10;a source of class `measured`.&#10;&#10;## Objective&#10;&#10;**Technical Question**: {{technical_uncertainty}}&#10;&#10;**Goals**:&#10;- [ ] [Specific goal 1]&#10;- [ ] [Specific goal 2]&#10;&#10;**Success Criteria**: Evidence gathered, recommendations with rationale, risks identified.&#10;&#10;**Out of Scope**: Production implementation, comprehensive testing, optimization work.&#10;&#10;## Hypothesis&#10;&#10;**Primary**: [What we think we&#x27;ll discover]&#10;**Assumptions**: [Key assumptions]&#10;**Expected Outcome**: [Anticipated result]&#10;&#10;## Test Setup&#10;&#10;What was measured and on what: the component and exact version, the&#10;hardware or instance type, the configuration that differs from the default,&#10;the data set and its size, and the date. A reader needs all of it to know&#10;which configuration the result speaks for.&#10;&#10;| Item | Value |&#10;|------|-------|&#10;| Component and version | [Name, version] |&#10;| Environment | [Hardware or instance type, operating system] |&#10;| Configuration | [Settings changed from the default, or *Defaults*] |&#10;| Data | [Data set, size, and where it comes from] |&#10;| Run on | [Date] |&#10;&#10;## Approach&#10;&#10;**Method**: [Prototype | Benchmark | Literature Review | Comparative Analysis | Integration Testing]&#10;&#10;**Activities**:&#10;| Day | Activity | Objective |&#10;|-----|----------|-----------|&#10;| 1 | [Activity] | [Goal] |&#10;| 2 | [Activity] | [Goal] |&#10;&#10;## Findings&#10;&#10;**FINDING 1**: [Discovery]&#10;- **Evidence**: [Concrete proof/data]&#10;- **Implications**: [What this means]&#10;&#10;### Measurements&#10;| Metric | Approach A | Approach B | Notes |&#10;|--------|------------|------------|--------|&#10;| [Metric] | [Value] | [Value] | [Context] |&#10;&#10;## Analysis&#10;&#10;**Hypothesis**: CONFIRMED | PARTIALLY CONFIRMED | REJECTED&#10;**Rationale**: [Evidence]&#10;&#10;### Risks&#10;| Risk | Prob | Impact | Mitigation |&#10;|------|------|--------|------------|&#10;| [Risk] | H/M/L | H/M/L | [Strategy] |&#10;&#10;## Conclusions&#10;&#10;**Primary Conclusion**: [Clear answer to the technical question]&#10;**Confidence**: High | Medium | Low&#10;**Limitations**: [What could not be determined]&#10;&#10;## Views Affected&#10;&#10;Reusable scope only. Which reader&#x27;s answer the result changes in the&#10;profile whose question this spike answers. One row per view; a view the&#10;result does not touch says **No change**.&#10;&#10;| View | What changes |&#10;|------|--------------|&#10;| Risk &amp; Compliance | [What the result changes, or *No change*] |&#10;| Finance | [What the result changes, or *No change*] |&#10;| IT Operations | [What the result changes, or *No change*] |&#10;| Apps Dev | [What the result changes, or *No change*] |&#10;&#10;## Recommendations&#10;&#10;Not at reusable scope: a published spike reports what it measured, and a&#10;position paper or decision brief draws the advice.&#10;&#10;**RECOMMENDATION**: [Specific, actionable recommendation]&#10;- **Rationale**: [Why, based on evidence]&#10;- **Next Steps**: [What needs to happen]&#10;- **Concern Impact**: [Does this recommend adopting, rejecting, or modifying a&#10;  concern? If so, an ADR should ratify the decision and the project concern&#10;  document should be updated accordingly.]&#10;&#10;## Reproduction&#10;&#10;How to run it again: where the scripts are in the repository, the inputs&#10;and how to obtain them, the commands in order, and how long a run takes.&#10;At reusable scope every input is public.&#10;&#10;1. [Command or step]&#10;&#10;## Artifacts&#10;&#10;- [Fixture, branch, benchmark, prototype, notes, or other evidence produced by&#10;  the spike]</code></pre></details></td></tr>
</tbody>
</table>
