---
title: "OWASP Web Security Testing Guide"
slug: owasp-wstg
generated: true
---
> **Source identity**:

```yaml
ddx:
  id: resource.owasp-wstg
```

# OWASP Web Security Testing Guide

## Source

- URL: https://owasp.org/www-project-web-security-testing-guide/
- Accessed: 2026-05-12

## Summary

OWASP describes the Web Security Testing Guide as a comprehensive guide for
testing web applications and web services. It provides a security testing
framework, domain-specific test areas, and stable scenario identifiers that can
be referenced from plans, reports, and tools.

## Relevant Findings

- WSTG covers domains such as configuration, identity, authentication,
  authorization, session management, input validation, error handling,
  cryptography, business logic, client-side behavior, and APIs.
- Test scenarios include objectives, how to test, remediation guidance, tools,
  and references.
- Versioned scenario identifiers help teams trace security tests to stable
  external guidance.
- OWASP Developer Guide guidance says teams should tailor WSTG coverage to
  project needs instead of running every test by default.

## HELIX Usage

This resource informs the Security Tests artifact. HELIX uses it to keep
security verification concrete, traceable, and selected according to the
project's actual threat model and security requirements.

## Authority Boundary

This resource supports web and API security testing. It does not replace
project-specific threat modeling, legal/compliance review, penetration testing
scope approval, or production monitoring.
