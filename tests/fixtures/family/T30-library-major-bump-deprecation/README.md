# T30 — library major bump → in-flight instances warn (I010) [HIGH RISK]

## Scenario

ADR library type ships at version 2.0.0, which adds a new
`required_sections: customer_impact` entry. The workspace has
ADR-001 with `library_type_version: 1.0.0` in frontmatter — pinned
to the prior major. ADR-001's body lacks the `## Customer Impact`
section.

Per §2.1: instance-shape validation uses the currently-resolved
library version (2.0.0) but downgrades NEW required-section
violations to **I010** deprecation warning when the instance pin is
a LOWER major than the resolved version. ADR-001 was authored before
the bump; the user gets one major cycle to migrate.

Companion T30b (deferred to v1.1, captured in implementation plan):
same library, ADR-002 with `library_type_version: 2.0.0` and no
customer_impact section → hard error.

## Why it matters

The S3 review item: "library bumps required_section, marker doesn't
pin → validator silently breaks pre-commit on every uncommitted
ADR." Without this fixture, the verification-exit-gate failure mode
re-emerges every time the library ships a section addition.

## What passes

- Exit 0 (warning, not error).
- `I010` warning citing ADR-001, the prior pin (1.0.0), and the new
  required section (customer_impact).

## What fails

- Hard error (I-class) — breaks the deprecation contract.
- Silent acceptance — drops the migration signal.
- Missing version context in diagnostic — author can't act.

## Risk

HIGH. The grace-cycle contract is what makes the library safely
upgradeable; without the fixture, every section addition is a
breaking change.
