#!/usr/bin/env python3
"""Finite abstract lease safety explorer; no production correspondence/proof."""
from __future__ import annotations

import argparse
from collections import deque
from dataclasses import asdict, dataclass, replace
import hashlib
import json
from pathlib import Path
import platform
import time

MODEL_VERSION = "1"
WORKERS = 2
MAX_CLAIMS = 2
PROPERTIES = (
    "exclusive_valid_owner", "stale_landing_rejected", "no_lock_across_wait",
)
LIMITS = (
    "Abstract atomic mutations; no production code correspondence (UNMAPPED).",
    "One bead, two workers, two claims; safety within this finite model only.",
    "No clocks/crashes/storage failures/token reuse/external effects/wedge parking.",
    "Liveness NOT_CHECKED; expiry and completion require environmental/fairness assumptions.",
)


@dataclass(frozen=True)
class State:
    claims: int = 0
    tokens: tuple[int, ...] = (0, 0)
    phases: tuple[str, ...] = ("idle", "idle")
    valid: tuple[bool, ...] = (False, False)
    lock: int = -1
    landed: bool = False
    stale_landed: bool = False
    late_after_reclaim: bool = False  # Coverage observer; never used by protocol guards.


def put(values: tuple, index: int, value) -> tuple:
    return values[:index] + (value,) + values[index + 1:]


def successors(state: State, variant: str):
    """The single transition relation used by exploration and trace replay."""
    for worker in range(WORKERS):
        phase = state.phases[worker]
        if (phase == "idle" and not state.landed and not any(state.valid)
                and state.lock == -1 and state.claims < MAX_CLAIMS):
            yield f"claim({worker})", replace(
                state, claims=state.claims + 1,
                tokens=put(state.tokens, worker, state.claims + 1),
                phases=put(state.phases, worker, "claimed"),
                valid=put(state.valid, worker, True), lock=worker,
            )
        if phase == "claimed" and state.lock == worker:
            yield f"start_wait({worker})", replace(
                state, phases=put(state.phases, worker, "running"),
                lock=worker if variant == "lock-held" else -1,
            )
        if phase in ("running", "returned") and state.valid[worker] and state.lock == -1:
            yield f"expire({worker})", replace(state, valid=put(state.valid, worker, False))
        if phase == "running":
            yield f"return({worker})", replace(
                state, phases=put(state.phases, worker, "returned"),
                late_after_reclaim=state.late_after_reclaim or (
                    worker == 0 and state.tokens[0] == 1 and state.claims == 2
                    and not state.valid[0] and state.valid[1]),
            )
        if phase == "returned" and state.lock == -1:
            authorized = state.valid[worker] and state.tokens[worker] == state.claims
            accepted = authorized or variant == "unfenced"
            yield f"land({worker})", replace(
                state, phases=put(state.phases, worker, "landed" if accepted else "rejected"),
                valid=put(state.valid, worker, False),
                landed=state.landed or accepted,
                stale_landed=state.stale_landed or (accepted and not authorized),
            )


def violations(state: State) -> list[str]:
    broken = []
    if (sum(state.valid) > 1 or any(
            valid and state.tokens[i] != state.claims for i, valid in enumerate(state.valid))):
        broken.append("exclusive_valid_owner")
    if state.stale_landed:
        broken.append("stale_landing_rejected")
    if state.lock != -1 and state.phases[state.lock] == "running":
        broken.append("no_lock_across_wait")
    return broken


def trace_to(state: State, parents: dict) -> list[str]:
    actions = []
    while parents[state] is not None:
        state, action = parents[state]
        actions.append(action)
    return list(reversed(actions))


def replay(actions: list[str], variant: str) -> list[State]:
    states = [State()]
    for action in actions:
        options = dict(successors(states[-1], variant))
        if action not in options:
            raise ValueError(f"Cannot replay {action}")
        states.append(options[action])
    return states


def witness_names(state: State) -> list[str]:
    names = []
    if state.landed and not state.stale_landed:
        names.append("valid_landing")
    if "rejected" in state.phases:
        names.append("stale_return_rejected")
    if (state.late_after_reclaim and state.claims == 2 and state.tokens == (1, 2)
            and state.phases[0] == "returned" and not state.valid[0] and state.valid[1]):
        names.append("expire_reclaim_late_return")
    return names


def explore(variant: str = "safe") -> dict:
    if variant not in ("safe", "unfenced", "lock-held"):
        raise ValueError("Unknown model variant")
    started = time.perf_counter()
    parents = {State(): None}
    queue = deque(parents)
    witnesses = {}
    visited = edges = 0
    outcome, broken, counterexample = "PASS_BOUNDED", [], None
    while queue:
        state = queue.popleft()
        visited += 1
        broken = violations(state)
        if broken:
            actions = trace_to(state, parents)
            replayed = replay(actions, variant)
            if replayed[-1] != state:
                raise ValueError("Counterexample replay mismatch")
            outcome = "VIOLATION"
            counterexample = {"actions": actions, "states": [asdict(s) for s in replayed],
                              "replayed": True}
            break
        for name in witness_names(state):
            if name not in witnesses:
                actions = trace_to(state, parents)
                if replay(actions, variant)[-1] != state:
                    raise ValueError("Witness replay mismatch")
                witnesses[name] = {"actions": actions, "replayed": True}
        for action, next_state in successors(state, variant):
            edges += 1
            if next_state not in parents:
                parents[next_state] = (state, action)
                queue.append(next_state)
    if outcome == "PASS_BOUNDED" and set(witnesses) != {
            "valid_landing", "stale_return_rejected", "expire_reclaim_late_return"}:
        raise ValueError("Incomplete behavioral coverage; no assurance result")
    return {
        "outcome": outcome, "variant": variant,
        "tool": "helix-abstract-lease-explorer", "tool_version": MODEL_VERSION,
        "python_version": platform.python_version(),
        "model_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "bounds": {"beads": 1, "workers": WORKERS, "claims": MAX_CLAIMS,
                   "depth_cutoff": None},
        "properties": list(PROPERTIES), "violations": broken,
        "complete": outcome == "PASS_BOUNDED", "states_discovered": len(parents),
        "states_checked": visited, "transitions_explored": edges,
        "elapsed_seconds": time.perf_counter() - started,
        "witnesses": witnesses, "counterexample": counterexample,
        "liveness": "NOT_CHECKED", "correspondence": "UNMAPPED",
        "limitations": list(LIMITS),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--variant", choices=("safe", "unfenced", "lock-held"), default="safe")
    args = parser.parse_args()
    try:
        report = explore(args.variant)
    except Exception as error:
        print(json.dumps({"outcome": "ERROR", "complete": False, "error": str(error),
                          "limitations": list(LIMITS)}))
        return 2
    print(json.dumps(report, indent=2))
    return 0 if report["outcome"] == "PASS_BOUNDED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
