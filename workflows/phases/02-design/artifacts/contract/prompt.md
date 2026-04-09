# Contract Generation Prompt
Document the normative interface or schema that another team can implement
against directly.

## Focus
- State the contract scope and boundaries clearly.
- Specify exact commands, fields, types, units, enums, ranges, and requiredness
  where relevant.
- Define precedence, ordering, compatibility, and versioning rules explicitly.
- Define failure modes, error codes, retry behavior, and recovery expectations.
- Include concrete examples and a validation checklist.
- Keep the document normative and implementation-independent; rationale belongs
  in ADRs and broader approach belongs in solution or technical designs.

## Completion Criteria
- The contract is specific enough for an independent implementation.
- Normative surface details are explicit rather than implied.
- Error semantics and compatibility rules are documented.
- Tests can be derived directly from the contract.
