# Abstract Lease-Lifecycle Model

This executable specification demonstrates bounded safety analysis. It is an
illustration inspired by worker lease contracts, not DDx implementation evidence.
Run from the repository root with Python 3.9 or later; no packages are required:

```bash
python3 workflows/references/formal-methods/lease_model.py
python3 workflows/references/formal-methods/lease_model.py --variant unfenced
python3 workflows/references/formal-methods/lease_model.py --variant lock-held
```

The safe command must exit 0 with `PASS_BOUNDED`, all three scenario witnesses,
and a complete exploration. The two mutants must exit 1 with `VIOLATION` of
`stale_landing_rejected` and `no_lock_across_wait` respectively, and a replayed
counterexample. Exit 2 / `ERROR` is a checker error, never a property result.
The command reports tool/Python versions, its own SHA-256 digest, bounds,
properties, state/transition counts, elapsed time, witnesses and limitations as
JSON. Arguments select a finite configuration; no depth/resource cutoff is used.

## State, Transitions and Assumptions

One bead, two workers and at most two monotonically numbered claims. Each worker
retains its own token and phase; authority separately records valid leases.
Mutation lock ownership is modeled explicitly. Initial state has no claims,
no valid leases, idle workers, no lock and no landings.
An additional coverage observer records whether worker A returned after worker B
reclaimed; it distinguishes event order without affecting protocol guards.

| Action | Guard | Effect |
|---|---|---|
| claim(i) | Idle worker; no valid lease/lock; claims below bound | Allocate token, validate lease, acquire mutation lock; phase claimed |
| start_wait(i) | Claimed worker owns lock | Release lock, enter harness wait (lock-held mutant retains it) |
| expire(i) | Running/returned worker holds valid lease; no lock | Invalidate lease; retain local token and harness phase |
| return(i) | Running worker | Harness returns; phase returned |
| land(i) | Returned worker; no lock | Accept only current valid token; otherwise reject (unfenced mutant accepts) |

Claim and landing mutations are abstract atomic steps. `start_wait` abstracts
lock release and harness invocation; harness wait/return are separate from lease
authority so a canceled/expired attempt may still return late. Tokens never
repeat within this model. Accepted landing ends the slice, preventing further
claims; expired/rejected attempts may leave the bead available for another worker.

## Properties and Non-Vacuity

- `exclusive_valid_owner`: at most one authoritative valid lease, whose token
  equals the latest claim. This is a representation invariant enforced by claim
  guards, not a distributed consensus proof; workers may retain stale tokens.
- `stale_landing_rejected`: no landing was accepted without a current valid
  lease/token at the instant of acceptance.
- `no_lock_across_wait`: a worker holds no mutation lock during its own harness
  wait. Another worker may perform a short mutation while that harness waits.

Breadth-first search explores every reachable state until the finite queue is
empty, or stops at the first violation with a shortest trace. The same transition
relation replays traces before reporting them. Positive coverage requires a
successful landing, a stale return rejected, and the exact ordered scenario:
claim A → expire A → claim B → return A. These witnesses guard against excluding
meaningful behavior. Tests additionally verify the scenario's tokens/authority
and run the installed catalog-floor copy.

## Assurance Limits and Correspondence

The abstract lease/token/lock states and atomic transitions have **no reviewed
mapping to production code**. Correspondence status is UNMAPPED for every
property. Safety only holds within the finite model and assumptions above.
Two claims expose one reclaim race; more workers/claims or failures may introduce
other behaviors. There are no real clocks, processes, crashes, filesystem locks,
storage failures, ABA/token reuse, or external side effects. The model does not
establish lock hold-time caps, actual lease duration, or exactly-once effects.

Liveness is **NOT_CHECKED**. For example, a running lease eventually expires only
if time advances, the expiry action becomes enabled and the watchdog is scheduled
fairly; return/landing also depend on harness completion and scheduler progress.
The model records expiry as a possible action and does not prove eventual release.
Repeated-wedge parking and queue progress require a separate model.

To adopt this pilot, fill the correspondence table in
`workflows/references/formal-methods.md`, identify real transaction boundaries,
extend the failure model and rerun affected analysis/tests. Capture the observed
results with model/config/source revisions. Model success supplements the
implementation's testing and running-system verification.
