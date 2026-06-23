# Contract Generation Prompt

Document the normative interface or schema that another team can implement
against directly.

## Purpose

A Contract is the **normative interface artifact**. Its unique job is to define
the exact surface another team, service, test suite, CLI caller, or agent can
implement against without reading the implementation.

Contracts are not feature specs; they do not decide product scope. Contracts
are not architecture or solution designs; they do not explain why the interface
exists or how internals work. Contracts own exact fields, commands, payloads,
status codes, compatibility rules, examples, and error semantics.

## Reference Anchors

Use these local resource summaries as grounding:

- `docs/resources/openapi-specification.md` grounds exact API surface, schemas,
  responses, examples, and validation.
- `docs/resources/rfc-9457-problem-details.md` grounds structured HTTP error
  semantics and recovery guidance.

## Focus
- State the contract scope and boundaries clearly.
- Specify exact commands, fields, types, units, enums, ranges, and requiredness
  where relevant.
- Define precedence, ordering, compatibility, and versioning rules explicitly.
- Define failure modes, error codes, retry behavior, and recovery expectations.
- Include concrete examples and a validation checklist.
- Keep the document normative and implementation-independent; rationale belongs
  in ADRs and broader approach belongs in solution or technical designs.

## Boundary Test

| If you are writing... | Put it in... |
|---|---|
| User-visible behavior and requirements | Feature Specification |
| Structural rationale or technology choice | Architecture or ADR |
| Exact interface surface, schemas, commands, errors, and compatibility | Contract |
| Component internals or implementation approach | Solution/Technical Design |
| Test fixtures and automation strategy | Test Plan or Story Test Plan |

## Completion Criteria
- The contract is specific enough for an independent implementation.
- Normative surface details are explicit rather than implied.
- Error semantics and compatibility rules are documented.
- Tests can be derived directly from the contract.
