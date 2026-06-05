# 01-frame

Purpose: turn a vision into a PRD that downstream design + test can build on.

Inputs: opportunity validated upstream.

Outputs: at minimum, a PRD instance. Optional: feature-specification instance.

Exit gate: `prd-validation` node — every required edge per `graph.yml` is
satisfied, every section per `library:prd.required_sections` is present.

This README is a minimal stub for the vertical slice. A production methodology
would carry richer guidance, concerns checklist, and exit-gate procedure.
