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
