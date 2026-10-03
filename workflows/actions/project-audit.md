# HELIX Action: Project Audit

Audit implementation only when the user explicitly requests it. Resolve the
named project, feature, component, or other scope before reviewing. If the
scope is ambiguous, ask. The audit reports findings; edits require separate
authorization.

## Review

1. Read the governing artifacts relevant to the scope and summarize the
   intended behavior.
2. Inspect the implementation and tests that bear on that behavior. Follow
   adjacent paths only when they affect the result.
3. Compare evidence with requirements and accepted design decisions. Check
   acceptance behavior, relevant security and concern practices, and measurable
   targets when they apply.
4. Distinguish implemented, incomplete, divergent, and unverified behavior.
   An accepted decision establishes direction, not implementation status.
5. Report material findings, evidence, scope limits, and the most useful next
   step. Do not create work items or gates automatically.

An audit need not inventory every artifact or surface unless the user asks for
comprehensive coverage. Use the structured form in `modes/_report.md` only when
requested or required by a runtime consumer.
