# CI-02 — Cross-instance rename impact analysis

The admin instance renamed `PRD-007` → `PRD-008`. The api instance has
two features (FEAT-014, FEAT-015) still declaring `informed_by` against
the old id. The validator must emit `I131` for each orphan downstream
(target not found in scope), and the skill must report both ids in its
impact list so the operator can re-pin in one pass.

**Paired negative**: CI-03 (happy path) — only FEAT-014 references the
healthy PRD-007, so the "two ids" regex cannot fire.

**Validator self-check** (plan §6.10c acceptance):

```
python3 family-test/library/scripts/helix_check.py marker \
  workspace/.helix.yml \
  --methodology helix=family-test/methodology-product \
  --library-types family-test/library/types
```

should emit `I131` for both FEAT-014 and FEAT-015 within 100ms.
