# T12 — section_aliases extends adr

## Scenario

`helix-library` and `helix` installed. The methodology declares a
`section_aliases` mapping for `library:adr`:
`{Decision: [Outcome, Choice]}`. An existing ADR doc uses the alias
`## Outcome` instead of the canonical `## Decision`.

## Why it matters

Per design §10 (Q2 resolved) and §4.1, `section_aliases` lets
methodologies accept community variants of canonical section names
without forking the library type. The validator must treat the
alias as equivalent to the canonical name.

## What passes

Validator exits 0. The doc validates against `library:adr` because
`## Outcome` resolves to canonical `## Decision`.

## What fails

Validator exits non-zero (alias not honoured) — false rejection of a
correctly-aliased doc.

## Risk

Medium. Validator contract; alias semantics are documented but easy
to get subtly wrong.
