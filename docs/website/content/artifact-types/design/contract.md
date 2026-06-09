---
title: "Contract"
linkTitle: "Contract"
slug: contract
activity: "Design"
artifactRole: "core"
weight: 12
generated: true
---

## Purpose

A Contract is the **normative interface artifact**. Its unique job is to define
the exact surface another team, service, test suite, CLI caller, or agent can
implement against without reading the implementation.

Contracts are not feature specs; they do not decide product scope. Contracts
are not architecture or solution designs; they do not explain why the interface
exists or how internals work. Contracts own exact fields, commands, payloads,
status codes, compatibility rules, examples, and error semantics.

## Example

<details open>
<summary>Show a worked example of this artifact</summary>

``````markdown
---
ddx:
  id: example.contract.depositmatch.import-session-api
  depends_on:
    - example.architecture.depositmatch
    - example.feature-specification.depositmatch.csv-import
    - example.user-story.depositmatch.upload-csv
  review:
    self_hash: 0f6f77f7dca5d1d05590440459fe958f9620857ed3968839e537655dce27cd04
    deps:
      example.architecture.depositmatch: 64b7297158175ff16812e401fe093f7624b5ba70b11265a7a4bdf324e50a6bff
      example.feature-specification.depositmatch.csv-import: d85530eb091209cf9989c9cac3bc1f1063358a5b79964ca0e5e7a384fa77c44a
      example.user-story.depositmatch.upload-csv: ae65ec934b10e577641772c711eafec5a15dbb5854327d8240307341e2053f66
    reviewed_at: "2026-05-15T04:11:24Z"
---

# Contract

**Contract ID**: API-001
**Type**: HTTP API
**Version**: v1
**Status**: complete
**Related**: FEAT-001, US-001, ADR-001

## Purpose

This contract defines the HTTP API for creating a draft DepositMatch import
session by uploading one bank deposit CSV and one invoice export CSV for a
client.

## Scope and Boundaries

- In scope: creating one draft import session, accepting two CSV files,
  recording source file metadata, and returning the mapping-review location.
- Out of scope: column mapping, row validation, import confirmation, match
  generation, and accepted source-row storage.
- Owning system or team: DepositMatch API Service.

## Normative Surface

Use MUST, MUST NOT, MAY, and SHOULD intentionally. Every field, command,
message, endpoint, or payload element named here is part of the contract.

| Element | Type / Shape | Required | Rules | Notes |
|---------|--------------|----------|-------|-------|
| `POST /v1/clients/{clientId}/import-sessions` | HTTP operation | yes | MUST accept `multipart/form-data`; MUST authenticate the user; MUST authorize access to `clientId` | Creates a draft session only |
| `clientId` | UUID path parameter | yes | MUST identify a client visible to the authenticated firm user | 404 if not visible |
| `bankFile` | file part | yes | MUST have `.csv` extension; MUST be parsed as UTF-8 text; max 10 MB | Bank deposit export |
| `invoiceFile` | file part | yes | MUST have `.csv` extension; MUST be parsed as UTF-8 text; max 10 MB | Invoice export |
| `sourceType.bank` | enum | yes | MUST be `bank_csv` | Server-assigned in response |
| `sourceType.invoice` | enum | yes | MUST be `invoice_csv` | Server-assigned in response |
| Success response | JSON object | yes | MUST return HTTP 201 and include `importSessionId`, `clientId`, `status`, `files`, and `next.href` | `status` MUST be `draft` |
| `files[].fileId` | UUID | yes | MUST be stable for this uploaded file | Used by later mapping step |
| `files[].originalName` | string | yes | MUST preserve uploaded file name, excluding path | Do not include local client path |
| `files[].sizeBytes` | integer | yes | MUST be greater than 0 and no more than 10,485,760 | Per file |
| `next.href` | URL path | yes | MUST point to the mapping review endpoint for the created session | Relative path allowed |

## Precedence and Compatibility

- Versioning: breaking changes require a new `/v{n}` path.
- Ordering or precedence: server-side authorization and file-type validation
  precede file storage.
- Backward-compatibility rules: v1 clients may ignore unknown response fields.
  The API MUST NOT remove or rename v1 response fields without a new version.
- Deprecation rules: deprecated fields must remain for one paid-release cycle
  after replacement is documented.

## Error Semantics

Errors use `application/problem+json`.

| Condition | Error / Outcome | Retry | Recovery Expectation |
|-----------|------------------|-------|----------------------|
| User cannot access `clientId` | 404 `client-not-found` | no | Choose a client visible to the authenticated user. |
| Missing `bankFile` or `invoiceFile` | 400 `missing-import-file` | yes | Submit both file parts. |
| File is not CSV | 415 `unsupported-import-file-type` | yes | Replace the invalid file with a CSV. |
| File exceeds 10 MB | 413 `import-file-too-large` | yes | Export a smaller date range or split the file. |
| API cannot store the uploaded file | 503 `import-storage-unavailable` | yes | Retry after `Retry-After` if present. |

## Examples

```http
POST /v1/clients/3f9fd8f8-8f65-4e0a-8f21-61f6e19b3df1/import-sessions
Content-Type: multipart/form-data; boundary=depositmatch

--depositmatch
Content-Disposition: form-data; name="bankFile"; filename="acme-bank-2026-05-08.csv"
Content-Type: text/csv

date,amount,description,id
2026-05-08,1200.00,Acme Dental DEP-1001,DEP-1001
--depositmatch
Content-Disposition: form-data; name="invoiceFile"; filename="acme-invoices-2026-05-08.csv"
Content-Type: text/csv

invoice_id,date,amount,customer
INV-104,2026-05-07,1200.00,Acme Dental
--depositmatch--
```

```json
{
  "importSessionId": "b7e4d5aa-0e87-469e-8d79-76af9d5d7890",
  "clientId": "3f9fd8f8-8f65-4e0a-8f21-61f6e19b3df1",
  "status": "draft",
  "files": [
    {
      "fileId": "9e7a64ab-b311-4ea7-8f8f-15a14b77b325",
      "sourceType": "bank_csv",
      "originalName": "acme-bank-2026-05-08.csv",
      "sizeBytes": 74
    },
    {
      "fileId": "5f0de96d-1e03-43e8-bfb8-98949b2db533",
      "sourceType": "invoice_csv",
      "originalName": "acme-invoices-2026-05-08.csv",
      "sizeBytes": 61
    }
  ],
  "next": {
    "href": "/v1/import-sessions/b7e4d5aa-0e87-469e-8d79-76af9d5d7890/mapping"
  }
}
```

```json
{
  "type": "https://docs.depositmatch.example/problems/unsupported-import-file-type",
  "title": "Unsupported import file type",
  "status": 415,
  "detail": "The bankFile part must be a CSV file.",
  "instance": "/v1/clients/3f9fd8f8-8f65-4e0a-8f21-61f6e19b3df1/import-sessions",
  "code": "unsupported-import-file-type",
  "field": "bankFile"
}
```

## Non-Normative Notes

This API creates only a draft import session. Mapping and validation are
separate contracts so clients can recover from upload problems before row-level
processing begins.

## Validation Checklist

- [ ] Normative fields and rules are explicit.
- [ ] Compatibility and precedence rules are explicit.
- [ ] Error handling is explicit.
- [ ] At least one executable test can be derived from this contract.
- [ ] Non-normative notes cannot be mistaken for contract requirements.
``````

</details>

## Reference

<table class="helix-reference-table">
<tbody>
<tr><th>Activity</th><td><a href="../../../reference/glossary/activities/"><strong>Design</strong></a> — Decide how to build it. Capture trade-offs, contracts, and architecture decisions.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/02-design/contracts/CONTRACT-{id}-{name}.md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Informs</th><td><a href="../../../artifact-types/test/test-plan/">Test Plan</a><br><a href="../../../artifact-types/design/technical-design/">Technical Design</a><br><a href="../../../artifact-types/test/test-suites/">Test Suites</a><br><a href="../../../artifact-types/build/implementation-plan/">Implementation Plan</a></td></tr>
<tr><th>HELIX documents</th><td><a href="https://github.com/DocumentDrivenDX/helix/blob/main/docs/helix/02-design/contracts/CONTRACT-001-ddx-helix-boundary.md"><code>docs/helix/02-design/contracts/CONTRACT-001-ddx-helix-boundary.md</code></a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Contract Generation Prompt&#10;&#10;Document the normative interface or schema that another team can implement&#10;against directly.&#10;&#10;## Purpose&#10;&#10;A Contract is the **normative interface artifact**. Its unique job is to define&#10;the exact surface another team, service, test suite, CLI caller, or agent can&#10;implement against without reading the implementation.&#10;&#10;Contracts are not feature specs; they do not decide product scope. Contracts&#10;are not architecture or solution designs; they do not explain why the interface&#10;exists or how internals work. Contracts own exact fields, commands, payloads,&#10;status codes, compatibility rules, examples, and error semantics.&#10;&#10;## Reference Anchors&#10;&#10;Use these local resource summaries as grounding:&#10;&#10;- `docs/resources/openapi-specification.md` grounds exact API surface, schemas,&#10;  responses, examples, and validation.&#10;- `docs/resources/rfc-9457-problem-details.md` grounds structured HTTP error&#10;  semantics and recovery guidance.&#10;&#10;## Focus&#10;- State the contract scope and boundaries clearly.&#10;- Specify exact commands, fields, types, units, enums, ranges, and requiredness&#10;  where relevant.&#10;- Define precedence, ordering, compatibility, and versioning rules explicitly.&#10;- Define failure modes, error codes, retry behavior, and recovery expectations.&#10;- Include concrete examples and a validation checklist.&#10;- Keep the document normative and implementation-independent; rationale belongs&#10;  in ADRs and broader approach belongs in solution or technical designs.&#10;&#10;## Boundary Test&#10;&#10;| If you are writing... | Put it in... |&#10;|---|---|&#10;| User-visible behavior and requirements | Feature Specification |&#10;| Structural rationale or technology choice | Architecture or ADR |&#10;| Exact interface surface, schemas, commands, errors, and compatibility | Contract |&#10;| Component internals or implementation approach | Solution/Technical Design |&#10;| Test fixtures and automation strategy | Test Plan or Story Test Plan |&#10;&#10;## Completion Criteria&#10;- The contract is specific enough for an independent implementation.&#10;- Normative surface details are explicit rather than implied.&#10;- Error semantics and compatibility rules are documented.&#10;- Tests can be derived directly from the contract.</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---&#10;ddx:&#10;  id: CONTRACT-XXX&#10;---&#10;&#10;# Contract&#10;&#10;**Contract ID**: [CONTRACT-XXX | API-XXX]&#10;**Type**: [boundary | HTTP API | CLI | library | protocol | event | schema]&#10;**Version**: [v1]&#10;**Status**: [draft | complete]&#10;**Related**: [ADR / SD / TD / FEAT references]&#10;&#10;## Purpose&#10;&#10;[Why this contract exists and what it governs.]&#10;&#10;## Scope and Boundaries&#10;&#10;- In scope:&#10;- Out of scope:&#10;- Owning system or team:&#10;&#10;## Normative Surface&#10;&#10;Use MUST, MUST NOT, MAY, and SHOULD intentionally. Every field, command,&#10;message, endpoint, or payload element named here is part of the contract.&#10;&#10;| Element | Type / Shape | Required | Rules | Notes |&#10;|---------|---------------|----------|-------|-------|&#10;| [field, command, message, endpoint] | [type] | [yes/no] | [units, enum, constraints] | [notes] |&#10;&#10;## Precedence and Compatibility&#10;&#10;- Versioning:&#10;- Ordering or precedence:&#10;- Backward-compatibility rules:&#10;- Deprecation rules:&#10;&#10;## Error Semantics&#10;&#10;| Condition | Error / Outcome | Retry | Recovery Expectation |&#10;|-----------|------------------|-------|----------------------|&#10;| [condition] | [error] | [yes/no] | [recovery] |&#10;&#10;## Examples&#10;&#10;```text&#10;[Example request / response / payload / invocation]&#10;```&#10;&#10;## Non-Normative Notes&#10;&#10;[Optional rationale or implementation guidance. Nothing in this section changes&#10;the contract.]&#10;&#10;## Validation Checklist&#10;&#10;- [ ] Normative fields and rules are explicit.&#10;- [ ] Compatibility and precedence rules are explicit.&#10;- [ ] Error handling is explicit.&#10;- [ ] At least one executable test can be derived from this contract.&#10;- [ ] Non-normative notes cannot be mistaken for contract requirements.</code></pre></details></td></tr>
</tbody>
</table>
