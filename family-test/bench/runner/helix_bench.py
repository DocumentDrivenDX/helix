#!/usr/bin/env python3
"""helix_bench — conversation-bench runner (Phase 0a: Layer 1 + matchers).

Single-file Python runner per plan §1.4b. Implements the typed assertion DSL
loader, 9 matchers, and T040-T047 rejection codes. PyYAML is the only
non-stdlib dependency (consistent with helix_check.py).

CLI
---
  helix_bench.py --version
  helix_bench.py self-test
  helix_bench.py validate-row <row-dir>
  helix_bench.py run <row-dir> [--determinism N]

Exit codes
----------
  0  success
  1  generic failure
  2  CLI usage error
  T0XX rejection: prints `REJECT TXXX <msg>` to stderr and exits non-zero
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.stderr.write("helix_bench requires PyYAML. Install with `pip install PyYAML`.\n")
    sys.exit(2)


VERSION = "0.1.0"

REPO_ROOT = Path(__file__).resolve().parents[2]  # family-test/bench/runner -> family-test
BENCH_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_WHITELIST = BENCH_ROOT / "library" / "schemas" / "discriminator-whitelist.yml"
SCHEMA_BANNED = BENCH_ROOT / "library" / "schemas" / "banned-matcher-patterns.yml"


# ---------------------------------------------------------------------------
# Rejection / error model
# ---------------------------------------------------------------------------

REJECTION_CODES = {
    "T040": "missing discriminator block",
    "T041": "assertion_id not in whitelist",
    "T042": "vacuous discriminator (expected_in_positive == expected_in_negative)",
    "T043": "observable matcher unparseable",
    "T044": "negative-control modification is a no-op",
    "T046": "new assertion_id not registered in whitelist (schema bump required)",
    "T047": "matcher argument matches banned-pattern (vacuous matcher)",
}


class RowRejection(Exception):
    """Raised when a row fails a load-time T0XX check."""

    def __init__(self, code: str, detail: str):
        super().__init__(f"{code} {REJECTION_CODES.get(code, '')}: {detail}")
        self.code = code
        self.detail = detail


# ---------------------------------------------------------------------------
# Schema loaders
# ---------------------------------------------------------------------------


@dataclass
class Whitelist:
    by_id: dict[str, dict[str, Any]]

    @classmethod
    def load(cls, path: Path = SCHEMA_WHITELIST) -> "Whitelist":
        data = yaml.safe_load(path.read_text())
        by_id = {entry["id"]: entry for entry in data.get("allowed_assertions", [])}
        return cls(by_id=by_id)


@dataclass
class BannedPatterns:
    regex_patterns: list[str] = field(default_factory=list)
    text_patterns: list[str] = field(default_factory=list)
    minimum_lengths: dict[str, int] = field(default_factory=dict)

    @classmethod
    def load(cls, path: Path = SCHEMA_BANNED) -> "BannedPatterns":
        data = yaml.safe_load(path.read_text())
        return cls(
            regex_patterns=list(data.get("banned_regex_patterns", []) or []),
            text_patterns=list(data.get("banned_text_patterns", []) or []),
            minimum_lengths=dict(data.get("minimum_lengths", {}) or {}),
        )

    def check_regex(self, pattern: str) -> str | None:
        """Return banned pattern reason if argument is vacuous, else None."""
        if pattern is None:
            return "regex pattern is None"
        if pattern in self.regex_patterns:
            return f"regex pattern '{pattern}' is in banned_regex_patterns"
        # also reject if regex itself is unparseable
        try:
            re.compile(pattern)
        except re.error as e:
            return f"regex pattern unparseable: {e}"
        return None

    def check_text(self, text: str) -> str | None:
        if text is None:
            return "text pattern is None"
        if text.strip().lower() in {t.strip().lower() for t in self.text_patterns}:
            return f"text '{text}' is in banned_text_patterns"
        return None

    def check_min_length(self, matcher_type: str, value: str) -> str | None:
        floor = self.minimum_lengths.get(matcher_type)
        if floor is None:
            return None
        if value is None or len(value) < floor:
            return f"matcher {matcher_type} argument length {len(value or '')} < minimum {floor}"
        return None


# ---------------------------------------------------------------------------
# Stream-json parser
# ---------------------------------------------------------------------------


@dataclass
class ToolUse:
    index: int
    name: str
    input: dict[str, Any]


@dataclass
class Transcript:
    """Parsed Claude Code stream-json transcript.

    Stream-json is a JSON-lines sequence of events emitted by `claude -p
    --output-format stream-json`. We extract the ordered list of tool_use
    events and the concatenated assistant text. Synthetic transcripts may
    omit fields; we tolerate missing keys.
    """

    tool_uses: list[ToolUse]
    assistant_text: str
    raw_events: list[dict[str, Any]]
    # ordered list of (index, kind, value) so we can ask "did prose X appear
    # before tool Y?". kind is 'text' or 'tool_use'.
    timeline: list[tuple[int, str, Any]]

    @classmethod
    def parse(cls, source: str | Path) -> "Transcript":
        if isinstance(source, Path):
            text = source.read_text()
        else:
            text = source
        events: list[dict[str, Any]] = []
        for line_no, raw in enumerate(text.splitlines(), start=1):
            line = raw.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise ValueError(f"line {line_no}: invalid JSON: {e}") from e
        return cls.from_events(events)

    @classmethod
    def from_events(cls, events: list[dict[str, Any]]) -> "Transcript":
        tool_uses: list[ToolUse] = []
        text_parts: list[str] = []
        timeline: list[tuple[int, str, Any]] = []
        idx = 0
        for ev in events:
            blocks = cls._extract_content_blocks(ev)
            for block in blocks:
                btype = block.get("type")
                if btype == "tool_use":
                    name = block.get("name", "")
                    tu = ToolUse(index=idx, name=name, input=block.get("input", {}) or {})
                    tool_uses.append(tu)
                    timeline.append((idx, "tool_use", tu))
                    idx += 1
                elif btype == "text":
                    txt = block.get("text", "") or ""
                    text_parts.append(txt)
                    timeline.append((idx, "text", txt))
                    idx += 1
        return cls(
            tool_uses=tool_uses,
            assistant_text="\n".join(text_parts),
            raw_events=events,
            timeline=timeline,
        )

    @staticmethod
    def _extract_content_blocks(event: dict[str, Any]) -> list[dict[str, Any]]:
        """Pull content blocks from a single stream-json event.

        Tolerant of three shapes seen in CC stream-json:
          1) {"type":"assistant","message":{"content":[{type:"text"|"tool_use",...}]}}
          2) {"type":"tool_use","name":..,"input":..}        — synthetic flat
          3) {"type":"text","text":..}                       — synthetic flat
        """
        blocks: list[dict[str, Any]] = []
        msg = event.get("message")
        if isinstance(msg, dict):
            content = msg.get("content")
            if isinstance(content, list):
                for c in content:
                    if isinstance(c, dict) and "type" in c:
                        blocks.append(c)
        # flat-shape fallback (synthetic / smoke transcripts)
        if event.get("type") in {"tool_use", "text"} and not blocks:
            blocks.append(event)
        return blocks


# ---------------------------------------------------------------------------
# Matchers
# ---------------------------------------------------------------------------


@dataclass
class MatchResult:
    verdict: str  # "present" | "absent" | "ordered" | "reversed"
    details: dict[str, Any]


Matcher = Callable[[dict[str, Any], Transcript], MatchResult]


def _all_mutation_tools() -> set[str]:
    return {"Write", "Edit", "NotebookEdit", "MultiEdit"}


def matcher_skill_tool_use(params: dict[str, Any], t: Transcript) -> MatchResult:
    skill_id = params.get("skill_id")
    if not skill_id:
        raise RowRejection("T043", "skill_tool_use requires skill_id")
    hits = []
    for tu in t.tool_uses:
        # CC encodes skill calls as a Skill tool_use with input.skill_id or
        # as a tool named Skill with the skill_id in input. Be tolerant.
        if tu.name == "Skill" and tu.input.get("skill_id") == skill_id:
            hits.append(tu.index)
            continue
        if tu.name == f"Skill({skill_id})":
            hits.append(tu.index)
            continue
        if tu.name == skill_id:  # synthetic-friendly: tool named with skill id
            hits.append(tu.index)
    return MatchResult(
        verdict="present" if hits else "absent",
        details={"hit_indices": hits, "skill_id": skill_id},
    )


def matcher_read_before_write(params: dict[str, Any], t: Transcript) -> MatchResult:
    first_tool = params.get("first_tool", "Read")
    second_tool = params.get("second_tool", "Write")
    target_pattern = params.get("target_pattern")
    if not target_pattern:
        raise RowRejection("T043", "read_before_write requires target_pattern")
    try:
        target_re = re.compile(target_pattern)
    except re.error as e:
        raise RowRejection("T043", f"target_pattern unparseable: {e}") from e
    first_idx = None
    second_idx = None
    for tu in t.tool_uses:
        path = (
            tu.input.get("file_path")
            or tu.input.get("path")
            or tu.input.get("filepath")
            or ""
        )
        if tu.name == first_tool and target_re.search(path):
            if first_idx is None:
                first_idx = tu.index
        if tu.name == second_tool or tu.name.startswith(f"{second_tool}("):
            if second_idx is None:
                second_idx = tu.index
    if first_idx is None and second_idx is None:
        return MatchResult("absent", {"first_idx": None, "second_idx": None})
    if first_idx is not None and second_idx is None:
        return MatchResult("ordered", {"first_idx": first_idx, "second_idx": None})
    if first_idx is None and second_idx is not None:
        return MatchResult("reversed", {"first_idx": None, "second_idx": second_idx})
    verdict = "ordered" if first_idx < second_idx else "reversed"
    return MatchResult(verdict, {"first_idx": first_idx, "second_idx": second_idx})


def matcher_graph_edge_observed(params: dict[str, Any], t: Transcript) -> MatchResult:
    graph_path = params.get("graph_path")
    expected_edge = params.get("expected_edge_signature")
    if not graph_path or not expected_edge:
        raise RowRejection(
            "T043",
            "graph_edge_observed requires graph_path and expected_edge_signature",
        )
    try:
        graph_re = re.compile(graph_path)
    except re.error as e:
        raise RowRejection("T043", f"graph_path unparseable: {e}") from e
    read_indices = [
        tu.index
        for tu in t.tool_uses
        if tu.name == "Read"
        and graph_re.search(
            tu.input.get("file_path") or tu.input.get("path") or ""
        )
    ]
    surfaced = expected_edge in t.assistant_text
    if read_indices and surfaced:
        return MatchResult(
            "present", {"read_indices": read_indices, "surfaced": True}
        )
    return MatchResult(
        "absent", {"read_indices": read_indices, "surfaced": surfaced}
    )


def matcher_scope_write_path(params: dict[str, Any], t: Transcript) -> MatchResult:
    allowed_root = params.get("allowed_root")
    forbidden_pattern = params.get("forbidden_pattern")
    if not allowed_root:
        raise RowRejection("T043", "scope_write_path requires allowed_root")
    try:
        allowed_re = re.compile(allowed_root)
    except re.error as e:
        raise RowRejection("T043", f"allowed_root unparseable: {e}") from e
    forbidden_re = None
    if forbidden_pattern:
        try:
            forbidden_re = re.compile(forbidden_pattern)
        except re.error as e:
            raise RowRejection("T043", f"forbidden_pattern unparseable: {e}") from e
    violations: list[dict[str, Any]] = []
    writes: list[dict[str, Any]] = []
    for tu in t.tool_uses:
        if tu.name not in _all_mutation_tools():
            continue
        path = tu.input.get("file_path") or tu.input.get("path") or ""
        writes.append({"index": tu.index, "path": path})
        if not allowed_re.search(path):
            violations.append({"index": tu.index, "path": path, "reason": "not under allowed_root"})
        elif forbidden_re and forbidden_re.search(path):
            violations.append({"index": tu.index, "path": path, "reason": "matches forbidden_pattern"})
    return MatchResult(
        "present" if not violations and writes else "absent" if violations else "present",
        # 'present' = all writes in-scope (including the zero-write case which
        # is trivially in-scope). 'absent' = at least one violation observed.
        {"writes": writes, "violations": violations},
    )


def matcher_next_action_envelope(
    params: dict[str, Any], t: Transcript
) -> MatchResult:
    schema_path = params.get("envelope_schema_path")
    if not schema_path:
        raise RowRejection("T043", "next_action_envelope requires envelope_schema_path")
    # Layer-3 only matcher. We look for a fenced ```json block in
    # assistant_text and confirm it's valid JSON with a `next_action` field.
    # Full schema validation deferred to P8.
    fence_re = re.compile(r"```json\s*\n(.*?)\n```", re.DOTALL)
    for m in fence_re.finditer(t.assistant_text):
        try:
            obj = json.loads(m.group(1))
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and "next_action" in obj:
            return MatchResult(
                "present",
                {"envelope": obj, "schema_ref": schema_path},
            )
    return MatchResult("absent", {"schema_ref": schema_path})


def matcher_confirmation_before_mutation(
    params: dict[str, Any], t: Transcript
) -> MatchResult:
    pattern = params.get("confirmation_marker_pattern")
    mutation_tools = params.get("mutation_tools") or list(_all_mutation_tools())
    if not pattern:
        raise RowRejection(
            "T043", "confirmation_before_mutation requires confirmation_marker_pattern"
        )
    try:
        pat_re = re.compile(pattern, re.IGNORECASE)
    except re.error as e:
        raise RowRejection("T043", f"confirmation_marker_pattern unparseable: {e}") from e
    first_confirmation_idx = None
    first_mutation_idx = None
    for idx, kind, val in t.timeline:
        if kind == "text" and first_confirmation_idx is None:
            if pat_re.search(val):
                first_confirmation_idx = idx
        if kind == "tool_use" and val.name in set(mutation_tools):
            if first_mutation_idx is None:
                first_mutation_idx = idx
    if first_confirmation_idx is None and first_mutation_idx is None:
        return MatchResult("absent", {"confirmation_idx": None, "mutation_idx": None})
    if first_confirmation_idx is not None and first_mutation_idx is None:
        return MatchResult(
            "present", {"confirmation_idx": first_confirmation_idx, "mutation_idx": None}
        )
    if first_confirmation_idx is None and first_mutation_idx is not None:
        return MatchResult(
            "absent", {"confirmation_idx": None, "mutation_idx": first_mutation_idx}
        )
    verdict = "present" if first_confirmation_idx < first_mutation_idx else "absent"
    return MatchResult(
        verdict,
        {
            "confirmation_idx": first_confirmation_idx,
            "mutation_idx": first_mutation_idx,
        },
    )


def matcher_refusal_no_write(
    params: dict[str, Any], t: Transcript
) -> MatchResult:
    pattern = params.get("refusal_text_pattern")
    if not pattern:
        raise RowRejection("T043", "refusal_no_write requires refusal_text_pattern")
    try:
        pat_re = re.compile(pattern, re.IGNORECASE)
    except re.error as e:
        raise RowRejection("T043", f"refusal_text_pattern unparseable: {e}") from e
    mutations = [tu for tu in t.tool_uses if tu.name in _all_mutation_tools()]
    text_match = bool(pat_re.search(t.assistant_text))
    if not mutations and text_match:
        return MatchResult("present", {"mutations": 0, "text_match": True})
    return MatchResult(
        "absent",
        {"mutations": len(mutations), "text_match": text_match},
    )


def matcher_literal_or_banner_text(
    params: dict[str, Any], t: Transcript
) -> MatchResult:
    exact_text = params.get("exact_text")
    regex_pattern = params.get("regex_pattern")
    occurrence_count = int(params.get("occurrence_count", 1) or 1)
    if exact_text is None and regex_pattern is None:
        raise RowRejection(
            "T043", "literal_or_banner_text requires exact_text or regex_pattern"
        )
    count = 0
    if exact_text is not None:
        # raw count of non-overlapping occurrences
        count = t.assistant_text.count(exact_text)
    else:
        try:
            pat_re = re.compile(regex_pattern)
        except re.error as e:
            raise RowRejection("T043", f"regex_pattern unparseable: {e}") from e
        count = len(pat_re.findall(t.assistant_text))
    verdict = "present" if count >= occurrence_count else "absent"
    return MatchResult(
        verdict,
        {"count": count, "expected_min": occurrence_count},
    )


def matcher_route_decision(params: dict[str, Any], t: Transcript) -> MatchResult:
    expected = params.get("expected_flow_instance")
    signal = params.get("routing_signal")
    if not expected or not signal:
        raise RowRejection(
            "T043",
            "route_decision requires expected_flow_instance and routing_signal",
        )
    flow_id, _, instance = (
        expected.partition(":") if isinstance(expected, str) else ("", "", "")
    )
    if signal == "explicit_skill_tool_use":
        for tu in t.tool_uses:
            if tu.name == "Skill" and tu.input.get("skill_id") == flow_id:
                if not instance or tu.input.get("instance") == instance:
                    return MatchResult(
                        "present", {"matched": tu.index, "signal": signal}
                    )
            if tu.name == flow_id:
                return MatchResult("present", {"matched": tu.index, "signal": signal})
        return MatchResult("absent", {"signal": signal})
    if signal == "prose_attribution":
        if expected in t.assistant_text:
            return MatchResult("present", {"signal": signal})
        return MatchResult("absent", {"signal": signal})
    if signal == "first_write_under_root":
        root = instance or flow_id
        for tu in t.tool_uses:
            if tu.name in _all_mutation_tools():
                path = tu.input.get("file_path") or tu.input.get("path") or ""
                if root and root in path:
                    return MatchResult("present", {"signal": signal, "path": path})
                return MatchResult("absent", {"signal": signal, "path": path})
        return MatchResult("absent", {"signal": signal})
    raise RowRejection("T043", f"unknown routing_signal: {signal}")


MATCHER_REGISTRY: dict[str, Matcher] = {
    "skill_tool_use": matcher_skill_tool_use,
    "read_before_write": matcher_read_before_write,
    "graph_edge_observed": matcher_graph_edge_observed,
    "scope_write_path": matcher_scope_write_path,
    "next_action_envelope": matcher_next_action_envelope,
    "confirmation_before_mutation": matcher_confirmation_before_mutation,
    "refusal_no_write": matcher_refusal_no_write,
    "literal_or_banner_text": matcher_literal_or_banner_text,
    "route_decision": matcher_route_decision,
}


# ---------------------------------------------------------------------------
# Discriminator validation (T040-T047)
# ---------------------------------------------------------------------------

# Known methodology plugin prefixes for T044's "no-op negative control" check.
METHODOLOGY_PLUGIN_PREFIXES = ("methodology-", "helix-")


def _check_matcher_vacuity(
    assertion_id: str,
    params: dict[str, Any],
    banned: BannedPatterns,
) -> None:
    """Raise T047 if matcher arguments are banned-vacuous."""
    # text-pattern params
    for key in ("exact_text",):
        if key in params and params[key] is not None:
            reason = banned.check_text(str(params[key]))
            if reason:
                raise RowRejection("T047", f"{assertion_id}.{key}: {reason}")
            length_reason = banned.check_min_length(assertion_id, str(params[key]))
            if length_reason:
                raise RowRejection("T047", f"{assertion_id}.{key}: {length_reason}")

    # regex-pattern params
    regex_keys = (
        "regex_pattern",
        "target_pattern",
        "allowed_root",
        "forbidden_pattern",
        "confirmation_marker_pattern",
        "refusal_text_pattern",
        "graph_path",
    )
    for key in regex_keys:
        if key in params and params[key] is not None:
            reason = banned.check_regex(str(params[key]))
            if reason:
                raise RowRejection("T047", f"{assertion_id}.{key}: {reason}")
            # Length floor applies to assertion-id-level matchers, not per-key.
            if key in {
                "confirmation_marker_pattern",
                "refusal_text_pattern",
            }:
                length_reason = banned.check_min_length(
                    assertion_id, str(params[key])
                )
                if length_reason:
                    raise RowRejection(
                        "T047", f"{assertion_id}.{key}: {length_reason}"
                    )


def validate_discriminator(
    expected: dict[str, Any],
    whitelist: Whitelist,
    banned: BannedPatterns,
) -> dict[str, Any]:
    """Run all T040-T047 load-time checks on an `expected.yml` doc.

    Returns the normalised discriminator block. Raises RowRejection on the
    first failure (the runner exits at the first reject).
    """
    if not isinstance(expected, dict) or "discriminator" not in expected:
        raise RowRejection("T040", "expected.yml has no `discriminator:` block")
    disc = expected.get("discriminator") or {}
    if not isinstance(disc, dict):
        raise RowRejection("T040", "discriminator block is not a mapping")

    assertion_id = disc.get("assertion_id")
    if not assertion_id:
        raise RowRejection("T040", "discriminator.assertion_id missing")
    if assertion_id not in whitelist.by_id:
        # T046 covers the schema-bump intent ("new id not registered"). T041
        # covers user typos / unknown ids. We can only see "new vs typo" from
        # the row; treat any unknown id as both — emit T041 unless the row
        # explicitly opts into T046 via `schema_bump_required: true`.
        if disc.get("schema_bump_required") is True:
            raise RowRejection(
                "T046",
                f"assertion_id '{assertion_id}' not registered in discriminator-whitelist.yml",
            )
        raise RowRejection(
            "T041", f"assertion_id '{assertion_id}' not in whitelist"
        )

    expected_pos = disc.get("expected_in_positive_run")
    expected_neg = disc.get("expected_in_negative_run")
    if expected_pos is None or expected_neg is None:
        raise RowRejection(
            "T042",
            "discriminator requires both expected_in_positive_run and expected_in_negative_run",
        )
    if expected_pos == expected_neg:
        raise RowRejection(
            "T042",
            f"discriminator is vacuous: expected_in_positive_run == expected_in_negative_run ({expected_pos!r})",
        )

    observable = disc.get("observable") or {}
    if not isinstance(observable, dict) or "matcher_type" not in observable:
        raise RowRejection("T043", "discriminator.observable.matcher_type missing")
    matcher_type = observable.get("matcher_type")
    declared_matcher = whitelist.by_id[assertion_id].get("matcher_type")
    if declared_matcher and matcher_type != declared_matcher:
        raise RowRejection(
            "T043",
            f"observable.matcher_type '{matcher_type}' does not match whitelist's '{declared_matcher}' for assertion_id '{assertion_id}'",
        )
    if assertion_id not in MATCHER_REGISTRY:
        raise RowRejection(
            "T043", f"no matcher implementation registered for {assertion_id}"
        )

    # Pull params and validate required params from whitelist.
    required_params = whitelist.by_id[assertion_id].get("matcher_params") or []
    # observable may carry params either as a `params:` sub-mapping or
    # inlined at the observable top level (as the whitelist examples show).
    if "params" in observable and isinstance(observable["params"], dict):
        params = dict(observable["params"])
    else:
        params = {k: v for k, v in observable.items() if k != "matcher_type"}

    # The whitelist sometimes encodes "exact_text | regex_pattern" as a single
    # param. We treat that as "at least one of the named alternatives".
    for required in required_params:
        if isinstance(required, str) and "|" in required:
            alts = [a.strip() for a in required.split("|")]
            if not any(a in params for a in alts):
                raise RowRejection(
                    "T043",
                    f"{assertion_id} requires one of {alts}; got {list(params)}",
                )
        else:
            if required not in params:
                raise RowRejection(
                    "T043",
                    f"{assertion_id} requires param '{required}'; got {list(params)}",
                )

    # Vacuity guard on matcher arguments.
    _check_matcher_vacuity(assertion_id, params, banned)

    # T044: negative_control modification must change the observable's input
    # class. Today we only check plugins_remove (the common modifier). Future
    # modifications: workspace swap (graph.yml mutation), marker edit, autonomy
    # change. We accept those if explicitly declared.
    neg = disc.get("negative_control")
    if not isinstance(neg, dict):
        raise RowRejection("T044", "discriminator.negative_control missing/invalid")
    modifications_seen = []
    plugins_remove = neg.get("plugins_remove") or []
    if plugins_remove:
        methodology_removed = any(
            isinstance(p, str) and p.startswith(METHODOLOGY_PLUGIN_PREFIXES)
            for p in plugins_remove
        )
        if not methodology_removed:
            raise RowRejection(
                "T044",
                f"negative_control.plugins_remove {plugins_remove!r} contains no methodology plugin (no-op for skill engagement)",
            )
        modifications_seen.append("plugins_remove")
    for key in ("workspace_swap", "marker_edit", "autonomy_override", "graph_swap"):
        if neg.get(key):
            modifications_seen.append(key)
    if not modifications_seen:
        raise RowRejection(
            "T044",
            "negative_control has no observable-changing modification (need plugins_remove, marker_edit, graph_swap, workspace_swap, or autonomy_override)",
        )

    return {
        "assertion_id": assertion_id,
        "matcher_type": matcher_type,
        "params": params,
        "expected_in_positive_run": expected_pos,
        "expected_in_negative_run": expected_neg,
        "negative_control": neg,
    }


# ---------------------------------------------------------------------------
# Row I/O
# ---------------------------------------------------------------------------


def load_row(row_dir: Path) -> dict[str, Any]:
    expected_path = row_dir / "expected.yml"
    if not expected_path.exists():
        raise RowRejection("T040", f"missing expected.yml in {row_dir}")
    return yaml.safe_load(expected_path.read_text()) or {}


def validate_row(
    row_dir: Path,
    whitelist: Whitelist | None = None,
    banned: BannedPatterns | None = None,
) -> dict[str, Any]:
    whitelist = whitelist or Whitelist.load()
    banned = banned or BannedPatterns.load()
    expected = load_row(row_dir)
    return validate_discriminator(expected, whitelist, banned)


# ---------------------------------------------------------------------------
# Smoke / self-test
# ---------------------------------------------------------------------------


def _synthetic_transcript(events: list[dict[str, Any]]) -> Transcript:
    return Transcript.from_events(events)


def _smoke_inputs() -> dict[str, tuple[Transcript, dict[str, Any], str]]:
    """One synthetic positive transcript per matcher.

    Returns {assertion_id: (transcript, params, expected_verdict)}.
    """
    return {
        "skill_tool_use": (
            _synthetic_transcript(
                [
                    {"type": "tool_use", "name": "Skill", "input": {"skill_id": "helix"}},
                    {"type": "text", "text": "Drafting product vision."},
                ]
            ),
            {"skill_id": "helix"},
            "present",
        ),
        "read_before_write": (
            _synthetic_transcript(
                [
                    {"type": "tool_use", "name": "Read", "input": {"file_path": "/repo/.helix.yml"}},
                    {"type": "tool_use", "name": "Write", "input": {"file_path": "/repo/docs/helix/prd.md"}},
                ]
            ),
            {"first_tool": "Read", "second_tool": "Write", "target_pattern": r"\.helix\.yml$"},
            "ordered",
        ),
        "graph_edge_observed": (
            _synthetic_transcript(
                [
                    {"type": "tool_use", "name": "Read", "input": {"file_path": "/skill/graph.yml"}},
                    {
                        "type": "text",
                        "text": "Graph says prd informs feature-specification; I'll surface that.",
                    },
                ]
            ),
            {"graph_path": r"graph\.yml$", "expected_edge_signature": "prd informs feature-specification"},
            "present",
        ),
        "scope_write_path": (
            _synthetic_transcript(
                [
                    {
                        "type": "tool_use",
                        "name": "Write",
                        "input": {"file_path": "/repo/docs/helix/01-frame/prd.md"},
                    }
                ]
            ),
            {"allowed_root": r"^/repo/docs/helix/", "forbidden_pattern": r"\.env$"},
            "present",
        ),
        "next_action_envelope": (
            _synthetic_transcript(
                [
                    {
                        "type": "text",
                        "text": "Here is my plan:\n```json\n{\"next_action\": \"draft_prd\", \"reason\": \"vision exists\"}\n```",
                    }
                ]
            ),
            {"envelope_schema_path": "library/schemas/next-action-envelope.json"},
            "present",
        ),
        "confirmation_before_mutation": (
            _synthetic_transcript(
                [
                    {
                        "type": "text",
                        "text": "Should I proceed to draft the PRD now?",
                    },
                    {
                        "type": "tool_use",
                        "name": "Write",
                        "input": {"file_path": "/repo/docs/helix/01-frame/prd.md"},
                    },
                ]
            ),
            {
                "confirmation_marker_pattern": r"(Should I|OK to proceed|Want me to)",
                "mutation_tools": ["Write", "Edit"],
            },
            "present",
        ),
        "refusal_no_write": (
            _synthetic_transcript(
                [
                    {
                        "type": "text",
                        "text": "I cannot proceed: the marker does not authorize helix-infra in this scope.",
                    }
                ]
            ),
            {"refusal_text_pattern": r"marker does not authorize"},
            "present",
        ),
        "literal_or_banner_text": (
            _synthetic_transcript(
                [
                    {
                        "type": "text",
                        "text": "No .helix.yml found. Activating helix by heuristic.",
                    }
                ]
            ),
            {
                "exact_text": "No .helix.yml found. Activating helix by heuristic.",
                "occurrence_count": 1,
            },
            "present",
        ),
        "route_decision": (
            _synthetic_transcript(
                [
                    {
                        "type": "tool_use",
                        "name": "Skill",
                        "input": {"skill_id": "helix-web", "instance": "web"},
                    }
                ]
            ),
            {
                "expected_flow_instance": "helix-web:web",
                "routing_signal": "explicit_skill_tool_use",
            },
            "present",
        ),
    }


def _malformed_rows(tmp_dir: Path) -> dict[str, Path]:
    """Generate one malformed expected.yml per rejection code under tmp_dir.

    Returns {code: row_dir}.
    """
    out: dict[str, Path] = {}

    def write(code: str, expected: dict[str, Any]) -> Path:
        row = tmp_dir / f"reject-{code}"
        row.mkdir(parents=True, exist_ok=True)
        (row / "expected.yml").write_text(yaml.safe_dump(expected, sort_keys=False))
        out[code] = row
        return row

    # T040: missing discriminator block entirely
    write("T040", {"structural": {}})

    # T041: assertion_id not in whitelist (and not opting into T046)
    write(
        "T041",
        {
            "discriminator": {
                "assertion_id": "no_such_id",
                "observable": {"matcher_type": "skill_tool_use", "skill_id": "helix"},
                "expected_in_positive_run": "present",
                "expected_in_negative_run": "absent",
                "negative_control": {"plugins_remove": ["methodology-product"]},
            }
        },
    )

    # T042: positive == negative verdict
    write(
        "T042",
        {
            "discriminator": {
                "assertion_id": "skill_tool_use",
                "observable": {"matcher_type": "skill_tool_use", "skill_id": "helix"},
                "expected_in_positive_run": "present",
                "expected_in_negative_run": "present",
                "negative_control": {"plugins_remove": ["methodology-product"]},
            }
        },
    )

    # T043: matcher_type mismatch with assertion_id
    write(
        "T043",
        {
            "discriminator": {
                "assertion_id": "skill_tool_use",
                "observable": {"matcher_type": "tool_use_order", "skill_id": "helix"},
                "expected_in_positive_run": "present",
                "expected_in_negative_run": "absent",
                "negative_control": {"plugins_remove": ["methodology-product"]},
            }
        },
    )

    # T044: negative_control modification is a no-op (no methodology plugin)
    write(
        "T044",
        {
            "discriminator": {
                "assertion_id": "skill_tool_use",
                "observable": {"matcher_type": "skill_tool_use", "skill_id": "helix"},
                "expected_in_positive_run": "present",
                "expected_in_negative_run": "absent",
                "negative_control": {"plugins_remove": ["some-unrelated-plugin"]},
            }
        },
    )

    # T046: unknown id with explicit schema_bump_required: true
    write(
        "T046",
        {
            "discriminator": {
                "assertion_id": "brand_new_observable",
                "schema_bump_required": True,
                "observable": {
                    "matcher_type": "brand_new_observable",
                    "skill_id": "helix",
                },
                "expected_in_positive_run": "present",
                "expected_in_negative_run": "absent",
                "negative_control": {"plugins_remove": ["methodology-product"]},
            }
        },
    )

    # T047: banned matcher pattern (literal_or_banner_text with banned text 'helix')
    write(
        "T047",
        {
            "discriminator": {
                "assertion_id": "literal_or_banner_text",
                "observable": {
                    "matcher_type": "text_match",
                    "exact_text": "helix",
                    "occurrence_count": 1,
                },
                "expected_in_positive_run": "present",
                "expected_in_negative_run": "absent",
                "negative_control": {"plugins_remove": ["methodology-product"]},
            }
        },
    )

    return out


def write_smoke_fixtures(smoke_dir: Path) -> dict[str, Path]:
    """Persist one synthetic stream-json per matcher under smoke_dir.

    Returns {assertion_id: path}.
    """
    smoke_dir.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}
    for aid, (t, _params, _verdict) in _smoke_inputs().items():
        path = smoke_dir / f"{aid}.jsonl"
        path.write_text(
            "\n".join(json.dumps(ev) for ev in t.raw_events) + "\n"
        )
        paths[aid] = path
    # also write the malformed-row tree under smoke_dir/rejections
    rej_dir = smoke_dir / "rejections"
    if rej_dir.exists():
        for child in rej_dir.iterdir():
            if child.is_dir():
                for f in child.iterdir():
                    f.unlink()
                child.rmdir()
        rej_dir.rmdir()
    rej_dir.mkdir(parents=True, exist_ok=True)
    _malformed_rows(rej_dir)
    return paths


def run_smoke(verbose: bool = True) -> tuple[int, dict[str, Any]]:
    """Run matcher smoke tests + rejection-code smoke tests.

    Returns (exit_code, summary). Summary lists matcher_pass count and
    rejection_codes_fired list.
    """
    whitelist = Whitelist.load()
    banned = BannedPatterns.load()
    summary: dict[str, Any] = {
        "matchers_total": len(_smoke_inputs()),
        "matchers_pass": 0,
        "matchers_fail": [],
        "rejection_codes_expected": sorted(REJECTION_CODES.keys()),
        "rejection_codes_fired": [],
        "rejection_failures": [],
    }

    # Positive: each matcher must return the expected verdict on its synthetic.
    for aid, (transcript, params, expected_verdict) in _smoke_inputs().items():
        try:
            result = MATCHER_REGISTRY[aid](params, transcript)
        except RowRejection as e:
            summary["matchers_fail"].append({"assertion_id": aid, "error": str(e)})
            continue
        if result.verdict != expected_verdict:
            summary["matchers_fail"].append(
                {
                    "assertion_id": aid,
                    "expected": expected_verdict,
                    "got": result.verdict,
                    "details": result.details,
                }
            )
        else:
            summary["matchers_pass"] += 1

    # Rejection: each malformed row must trip exactly its labeled code.
    tmp_dir = BENCH_ROOT / "runner" / "smoke" / "rejections"
    if tmp_dir.exists():
        for child in list(tmp_dir.iterdir()):
            if child.is_dir():
                for f in child.iterdir():
                    f.unlink()
                child.rmdir()
            else:
                child.unlink()
    tmp_dir.mkdir(parents=True, exist_ok=True)
    row_dirs = _malformed_rows(tmp_dir)
    for code, row_dir in row_dirs.items():
        try:
            validate_row(row_dir, whitelist=whitelist, banned=banned)
        except RowRejection as e:
            if e.code == code:
                summary["rejection_codes_fired"].append(code)
            else:
                summary["rejection_failures"].append(
                    {"expected": code, "got": e.code, "detail": e.detail}
                )
        else:
            summary["rejection_failures"].append(
                {"expected": code, "got": "PASS", "detail": "row did not raise"}
            )

    ok = (
        summary["matchers_pass"] == summary["matchers_total"]
        and not summary["matchers_fail"]
        and sorted(summary["rejection_codes_fired"])
        == summary["rejection_codes_expected"]
        and not summary["rejection_failures"]
    )

    if verbose:
        print(
            f"smoke: matchers {summary['matchers_pass']}/{summary['matchers_total']} pass; "
            f"rejection codes fired: {sorted(summary['rejection_codes_fired'])} "
            f"(expected: {summary['rejection_codes_expected']})"
        )
        if summary["matchers_fail"]:
            print("  matcher failures:")
            for f in summary["matchers_fail"]:
                print(f"    - {f}")
        if summary["rejection_failures"]:
            print("  rejection failures:")
            for f in summary["rejection_failures"]:
                print(f"    - {f}")

    return (0 if ok else 1), summary


# ---------------------------------------------------------------------------
# Row run (placeholder for Phase 0a; full CC invocation is Phase 1+)
# ---------------------------------------------------------------------------


def run_row(row_dir: Path, determinism: int = 1) -> int:
    """Phase 0a row-run validates the row but defers CC invocation.

    Returns 0 if the row validates; non-zero on rejection.
    """
    try:
        norm = validate_row(row_dir)
    except RowRejection as e:
        print(f"REJECT {e.code} {row_dir.name}: {e.detail}", file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "row": str(row_dir),
                "status": "validated",
                "discriminator": norm,
                "determinism": determinism,
                "note": "Phase 0a: stream-json invocation deferred to Phase 1+",
            },
            indent=2,
        )
    )
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="helix_bench", description="HELIX conversation-bench runner"
    )
    parser.add_argument("--version", action="store_true", help="print version and exit")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("self-test", help="run matcher + rejection smoke tests")

    p_validate = sub.add_parser("validate-row", help="load + validate a row's expected.yml")
    p_validate.add_argument("row_dir", type=Path)

    p_run = sub.add_parser("run", help="run a row (Phase 0a: validate only)")
    p_run.add_argument("row_dir", type=Path)
    p_run.add_argument("--determinism", type=int, default=1)

    args = parser.parse_args(argv)
    if args.version:
        print(f"helix_bench {VERSION}")
        return 0
    if args.cmd is None:
        parser.print_help()
        return 2

    if args.cmd == "self-test":
        code, _ = run_smoke(verbose=True)
        return code
    if args.cmd == "validate-row":
        try:
            norm = validate_row(args.row_dir)
        except RowRejection as e:
            print(f"REJECT {e.code}: {e.detail}", file=sys.stderr)
            return 1
        print(json.dumps(norm, indent=2))
        return 0
    if args.cmd == "run":
        return run_row(args.row_dir, determinism=args.determinism)
    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
