# T2 — helix only (library missing) [HIGH RISK]

## Scenario

`helix` (the methodology) is installed but `helix-library` is NOT.
Existing helix documents are on disk. The user tries to (a) read an
existing PRD and (b) author a new one.

## Why it matters

This is the **degraded but recoverable** state. A user can take the
helix methodology plugin alone from the marketplace without the
library. We promised in the design (§7.2):

- Existing documents on disk remain **read-only-OK** — the methodology
  must not blow up on first read.
- New authoring is **blocked with a setup-gap message** pointing the
  user at `claude plugin install helix-library`.
- The methodology must NOT improvise a template from memory.

If this fails, the failure mode is silent template improvisation —
users get PRDs that look real but don't match the library schema.

## What passes

- Prompt 01 (read existing PRD): returns a summary of the doc; no
  setup-gap message.
- Prompt 02 (author new PRD): returns the documented setup-gap
  message, no `# Problem` template heading, no `Write` `tool_use`
  against a new file.

## What fails

- Prompt 02 produces a PRD-shaped file via `Write` (template
  improvisation). HIGH SEVERITY.
- Prompt 01 refuses to read an existing doc (over-aggressive
  setup-gap). MEDIUM severity (false positive).

## Risk

HIGH. Silent template improvisation is the worst-case failure mode for
the family.
