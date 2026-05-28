---
title: "RFC 9457 Problem Details for HTTP APIs"
slug: rfc-9457-problem-details
generated: true
---
> **Source identity**:

```yaml
ddx:
  id: resource.rfc-9457-problem-details
```

# RFC 9457 Problem Details for HTTP APIs

## Source

- URL: https://www.rfc-editor.org/rfc/rfc9457
- Accessed: 2026-05-12

## Summary

RFC 9457 defines a standard way for HTTP APIs to return machine-readable error
details. A problem details response can include a type URI, title, status,
detail, instance, and extension members. The format helps clients distinguish
and handle errors without relying on free-form text.

## Relevant Findings

- HTTP API contracts should define structured error semantics, not just success
  payloads.
- Error responses need stable machine-readable fields that clients can depend
  on.
- Problem type definitions should explain status codes and recovery guidance
  where clients can act on the problem.
- Extension members allow API-specific error details without inventing an
  entirely new error envelope.

## HELIX Usage

This resource informs the Contract artifact. HELIX uses it to make error
semantics, retry behavior, and recovery expectations explicit for HTTP API
contracts.

## Authority Boundary

This resource is specific to HTTP API error responses. HELIX contracts for
CLI, events, file formats, or protocols should use the same clarity bar while
choosing a format appropriate to that interface.
