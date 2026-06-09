# CI-01 — Cross-instance stale-target detection

A multi-instance marker (`helix.api` + `helix.admin`) carries an
api-instance feature with `informed_by` against an admin-instance PRD
that has been superseded. The validator must emit `I131` flagging the
stale target, and the skill must surface the stale lineage in prose so
the operator can re-pin the link.

**Paired negative**: CI-03 (happy path) — same workspace shape but the
target PRD is healthy; the stale-target prose MUST NOT fire.

**Validator self-check** (plan §6.10c acceptance):

```
python3 family-test/library/scripts/helix_check.py marker \
  workspace/.helix.yml \
  --methodology helix=family-test/methodology-product \
  --library-types family-test/library/types
```

should report `I131` (cross-instance target `helix.admin:PRD-007` is
`status: superseded`) within 100ms.
