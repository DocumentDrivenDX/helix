# HELIX Action: Evolve

Thread a requested requirement change through the artifacts it affects. This
procedure preserves intended behavior and decision authority; it does not
assume that an accepted decision has been implemented.

## Input and authority

Use the named entry artifact and requested change. If either is ambiguous,
clarify before editing. Apply the authority order in
`workflows/actions/reconcile-alignment.md`.

Read the entry artifact's relevant `ddx.links` and directly referenced
documents. Follow a relationship only when it can change the requested result.
When links are absent, use the activity hierarchy to find likely affected
documents. Do not enumerate the entire project or infer that every reachable
artifact is in scope. Preserve legacy relationship fields; migration is a
separate requested change.

## Procedure

1. **Understand the change.** Identify the requirement or decision being added,
   changed, or removed. Preserve its stated strength, limits, and exceptions.
2. **Find affected artifacts.** Read the relevant authorities and downstream
   documents. Include code or tests only when the user requests implementation
   work or an audit.
3. **Resolve conflicts.** State any conflict with higher-authority content.
   Do not silently overwrite it or change desired state to match existing
   implementation. Ask for a decision when the user's intent does not resolve
   the conflict.
4. **Make authorized edits.** Update only the affected artifacts, from higher
   authority to lower. Preserve unrelated content and frontmatter.
5. **Report the result.** Name changed artifacts, important related artifacts
   left unchanged, unresolved conflicts, and evidence. Use a conversational
   response unless a durable or structured result was requested.

Create tracker work, dependency links, or new gates only when the user requests
them or a runtime consumer requires them. When requested, describe each item in
terms of its affected artifact and verifiable outcome. Do not make a gate from
every review finding.

## Output

Summarize the requirement change, artifact edits, and remaining decisions. Do
not include pull request numbers, commit hashes, or repository-history
citations in the artifact or report. A structured report remains available
when requested by a user or runtime consumer.
