---
ddx:
  id: TS-001
  type: tech-spike
  scope: reusable
  authoring:
    home: repo
  links:
    - {id: component-profile-examplestore-reusable, kind: answers, question: 2, rev: example}
---

# Technical Spike: ExampleStore restore time by database size

**Spike ID**: TS-001 | **Lead**: Maintainer | **Time Budget**: 1 day | **Status**: Completed

Synthetic fixture: ExampleStore is not a real product and these figures were
not measured. It exists to exercise the reusable scope's checks.

## Objective

**Technical Question**: How long does an ExampleStore restore take as the
database grows?

**Goals**:
- [x] Time a restore at three database sizes

**Success Criteria**: A restore time per size, with the run-to-run spread.

**Out of Scope**: Tuning, other versions, other hardware.

## Hypothesis

**Primary**: Restore time grows in proportion to database size.
**Assumptions**: The archive is on local disk.
**Expected Outcome**: A straight line through the three sizes.

## Test Setup

| Item | Value |
|------|-------|
| Component and version | ExampleStore 4.2 |
| Environment | One 8-core virtual machine, 32 GB memory, local SSD |
| Configuration | Defaults |
| Data | The generator in `spikes/TS-001/generate.sh`, at 10, 50 and 100 GB |
| Run on | 2026-11-10 |

## Approach

**Method**: Benchmark

**Activities**:
| Day | Activity | Objective |
|-----|----------|-----------|
| 1 | Generate data, restore three times per size | Time and spread |

## Findings

**FINDING 1**: Restore time grew in proportion to size across the three sizes.
- **Evidence**: The Measurements table; raw timings in `spikes/TS-001/results.csv`
- **Implications**: The brief's open question 2 has an answer for this configuration

### Measurements
| Size | Median restore | Spread over three runs |
|------|----------------|------------------------|
| 10 GB | 4 min | 10 s |
| 50 GB | 21 min | 40 s |
| 100 GB | 43 min | 1 min |

## Analysis

**Hypothesis**: CONFIRMED
**Rationale**: The three medians lie on one line within the spread.

## Conclusions

**Primary Conclusion**: On this configuration a restore took about 26 seconds
per gigabyte.
**Confidence**: Medium
**Limitations**: One version, one machine, default settings, synthetic data.

## Views Affected

| View | What changes |
|------|--------------|
| Risk & Compliance | No change |
| Finance | No change |
| IT Operations | Restore duration is no longer absent from the record for this configuration |
| Apps Dev | No change |

## Reproduction

1. `spikes/TS-001/generate.sh 10 50 100`
2. `spikes/TS-001/restore.sh`, about three hours for all nine runs
