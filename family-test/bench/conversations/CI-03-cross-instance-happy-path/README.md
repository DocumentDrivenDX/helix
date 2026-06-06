# CI-03 — Cross-instance happy path

Multi-instance marker (`helix.api` + `helix.admin`). FEAT-014 declares
`informed_by` against the healthy admin-instance PRD-007. The api
graph's `external_edges` authorises the cross-instance `informed_by`
kind. The validator must report a clean exit; the skill must resolve
the lineage and report PRD-007's healthy status.

**Paired negatives**: CI-01 (stale-target — PRD-007 superseded), CI-02
(rename impact — PRD-007 removed). This row is the positive control
for both.

**Validator self-check** (plan §6.10c acceptance):

```
python3 family-test/library/scripts/helix_check.py marker \
  workspace/.helix.yml \
  --methodology helix=family-test/methodology-product \
  --library-types family-test/library/types
```

should exit 0 with no I130/I131 findings.
