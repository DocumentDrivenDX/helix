# HELIX Action: Backfill HELIX Documentation

Reconstruct missing or incomplete HELIX artifacts from evidence. Distinguish
confirmed facts from inference, preserve existing authority, and ask the user
when uncertainty could change a consequential decision.

## Input and scope

Use the named project or artifact scope. If none is given, ask whether the user
means the whole project before surveying it. Do not treat backfill as an
implementation audit unless the user asks for one.

Read relevant HELIX artifacts first, then consult only the implementation,
tests, operational documents, and other evidence that can clarify the missing
content. Follow relevant relationships; do not inventory unrelated files or
traverse the whole project by default. A user-requested repository-wide
backfill may require broader evidence coverage.

## Authority and evidence

Use this order when evidence conflicts: vision, requirements, features and
stories, architecture and ADRs, designs, tests, implementation plans, then
code. Code and tests describe current behavior; they do not authorize changing
desired state. Existing canonical artifacts take precedence over inferences
from lower layers.

For factual claims, identify the source. Mark uncertain claims as inference and
state confidence when it helps the user decide whether to adopt them. Never
present low-confidence requirements or design choices as settled fact. Ask for
guidance before canonizing an inference that would materially affect the
system.

## Procedure

1. **Locate the gap.** Identify the missing or incomplete artifact and the
   specific content needed for the user's request.
2. **Gather relevant evidence.** Read the governing artifacts and the evidence
   needed to resolve that gap. Keep assumptions separate from observations.
3. **Draft the artifact.** Use the resolved type template and authoring
   contract. Preserve existing content and identifiers; do not fill optional
   sections with `N/A`.
4. **Check consistency.** Compare the draft with relevant higher-authority
   artifacts and active concerns. Surface conflicts instead of silently
   choosing between them.
5. **Report the result.** Name the artifact created or updated, evidence used,
   important uncertainty, and any needed user decision. Keep the response
   conversational by default.

Create tracker items only when the user requests durable follow-up or the
runtime requires them. A tracker or durable report is not a prerequisite for
drafting. When requested, use `workflows/templates/backfill-report.md` and
include only sections that help explain the evidence, assumptions, and result.

## Optional structured result

When requested by the user or required by a runtime consumer, report status,
scope, artifacts changed, unresolved guidance, and evidence in the consumer's
format. Do not emit a machine-readable trailer in ordinary conversation.
