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


VERSION = "0.3.1"

# Default model for conversation rows. Routing-evals always use the cheaper
# Haiku model (the integer-gate decision is binary; cheaper model is
# sufficient — see plan §19.1). Rows may override via `model:` in expected.yml.
DEFAULT_MODEL = "claude-sonnet-4-6"
ROUTING_EVAL_MODEL = "claude-haiku-4-5"

REPO_ROOT = Path(__file__).resolve().parents[2]  # family-test/bench/runner -> family-test
FAMILY_TEST_ROOT = REPO_ROOT  # alias for clarity in Phase 1+ runner code
BENCH_ROOT = Path(__file__).resolve().parents[1]
CONVERSATIONS_DIR = BENCH_ROOT / "conversations"
ROUTING_EVALS_DIR = BENCH_ROOT / "routing-evals"
RUNS_DIR = BENCH_ROOT / "runs"
RUN_PROBE_SH = FAMILY_TEST_ROOT / "docker" / "run-probe.sh"
RUN_PROBE_CODEX_SH = BENCH_ROOT / "runner" / "run-probe-codex.sh"
RUN_PROBE_OPENCODE_SH = BENCH_ROOT / "runner" / "run-probe-opencode.sh"

# Supported runtimes for `invoke_probe` dispatch. Default is claude
# (`run-probe.sh` Docker harness). Codex runs on-host via
# `run-probe-codex.sh`. OpenCode runs on-host via `run-probe-opencode.sh`,
# discovering SKILL.md via the workspace's .claude/skills/ tree.
SUPPORTED_RUNTIMES = ("claude", "codex", "opencode")
DEFAULT_RUNTIME = "claude"
RATCHETS_PATH = BENCH_ROOT / "ratchets.json"
COST_LOG_PATH = BENCH_ROOT / "runner" / "cost-log.jsonl"
SCHEMA_WHITELIST = BENCH_ROOT / "library" / "schemas" / "discriminator-whitelist.yml"
SCHEMA_BANNED = BENCH_ROOT / "library" / "schemas" / "banned-matcher-patterns.yml"
META_TESTS_DIR = BENCH_ROOT / "runner" / "meta-tests"
PROPERTY_TESTS_DIR = BENCH_ROOT / "runner" / "property-tests"
GOLDEN_DIR = BENCH_ROOT / "golden-transcripts"
TRANSCRIPT_SCHEMA = BENCH_ROOT / "runner" / "transcript_schema.yml"
CC_VERSION_LOCK = BENCH_ROOT / "cc-version.lock"
JUDGE_RUBRIC = BENCH_ROOT / "judge" / "rubric-prompt.md"
JUDGE_CALIBRATION = BENCH_ROOT / "judge" / "calibration-set.yml"
JUDGE_RESULTS_DIR = BENCH_ROOT / "judge" / "results"
ENVELOPE_SCHEMA = BENCH_ROOT / "judge" / "next-action-envelope.schema.json"
ENVELOPE_SYSTEM_PROMPT = BENCH_ROOT / "library" / "schemas" / "envelope-system-prompt.md"
ENVELOPE_RESULTS_DIR = BENCH_ROOT / "judge" / "results" / "envelope"


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

    @classmethod
    def parse_codex(cls, source: str | Path) -> "Transcript":
        """Parse a codex `--json` JSONL transcript into the common shape.

        Codex emits a different event shape from claude stream-json:
          {"type":"item.completed","item":{"type":"agent_message","text":...}}
          {"type":"item.completed","item":{"type":"command_execution","command":...}}
          {"type":"item.completed","item":{"type":"file_change","changes":[{path,kind}]}}
        We map:
          agent_message     → text block
          command_execution → tool_use name="Bash" input={"command": ...}
          file_change(kind=add)    → tool_use name="Write" input={"file_path": ...}
          file_change(kind=update) → tool_use name="Edit"  input={"file_path": ...}
          file_change(kind=delete) → tool_use name="Edit"  input={"file_path": ...}

        Only `item.completed` events are considered (in_progress duplicates).
        """
        if isinstance(source, Path):
            text = source.read_text()
        else:
            text = source
        synthetic_events: list[dict[str, Any]] = []
        for line_no, raw in enumerate(text.splitlines(), start=1):
            line = raw.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"line {line_no}: invalid JSON: {e}") from e
            if ev.get("type") != "item.completed":
                continue
            item = ev.get("item") or {}
            itype = item.get("type")
            if itype == "agent_message":
                txt = item.get("text") or ""
                if txt:
                    synthetic_events.append({"type": "text", "text": txt})
            elif itype == "command_execution":
                cmd = item.get("command") or ""
                synthetic_events.append({
                    "type": "tool_use",
                    "name": "Bash",
                    "input": {"command": cmd},
                })
            elif itype == "file_change":
                for change in item.get("changes") or []:
                    if not isinstance(change, dict):
                        continue
                    path = change.get("path") or ""
                    kind = change.get("kind") or ""
                    tool_name = "Write" if kind == "add" else "Edit"
                    synthetic_events.append({
                        "type": "tool_use",
                        "name": tool_name,
                        "input": {"file_path": path},
                    })
        return cls.from_events(synthetic_events)

    @classmethod
    def parse_opencode(cls, source: str | Path) -> "Transcript":
        """Parse an opencode `--format json` NDJSON transcript.

        opencode emits events with the shape:
          {"type":"tool_use","part":{"tool":"skill","state":{"status":"completed","input":{"name":"helix"},"output":"..."}}}
          {"type":"tool_use","part":{"tool":"bash","state":{"input":{"command":"..."}}}}
          {"type":"tool_use","part":{"tool":"read","state":{"input":{"file_path":"..."}}}}
          {"type":"tool_use","part":{"tool":"write","state":{"input":{"file_path":"...","content":"..."}}}}
          {"type":"tool_use","part":{"tool":"edit","state":{"input":{"file_path":"..."}}}}
          {"type":"message_part","part":{"type":"text","text":"..."}}
          {"type":"step_start"} / {"type":"step_finish"} / {"type":"error", ...}

        Mapped to the common transcript shape:
          skill              → tool_use name="Skill" input={"skill_id": <name>}
          bash               → tool_use name="Bash"  input={"command": ...}
          read               → tool_use name="Read"  input={"file_path": ...}
          write              → tool_use name="Write" input={"file_path": ...}
          edit/multi-edit    → tool_use name="Edit"  input={"file_path": ...}
          message_part text  → text block
        """
        if isinstance(source, Path):
            text = source.read_text()
        else:
            text = source
        synthetic_events: list[dict[str, Any]] = []
        for line_no, raw in enumerate(text.splitlines(), start=1):
            line = raw.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"line {line_no}: invalid JSON: {e}") from e
            etype = ev.get("type")
            part = ev.get("part") or {}
            if etype == "tool_use":
                tool = part.get("tool") or ""
                state = part.get("state") or {}
                inp = state.get("input") or {}
                if tool == "skill":
                    skill_name = inp.get("name") or ""
                    if skill_name:
                        synthetic_events.append({
                            "type": "tool_use",
                            "name": "Skill",
                            "input": {"skill_id": skill_name},
                        })
                elif tool == "bash":
                    synthetic_events.append({
                        "type": "tool_use",
                        "name": "Bash",
                        "input": {"command": inp.get("command") or ""},
                    })
                elif tool == "read":
                    synthetic_events.append({
                        "type": "tool_use",
                        "name": "Read",
                        "input": {"file_path": inp.get("file_path") or inp.get("path") or ""},
                    })
                elif tool == "write":
                    synthetic_events.append({
                        "type": "tool_use",
                        "name": "Write",
                        "input": {"file_path": inp.get("file_path") or inp.get("path") or ""},
                    })
                elif tool in ("edit", "multi_edit", "multi-edit"):
                    synthetic_events.append({
                        "type": "tool_use",
                        "name": "Edit",
                        "input": {"file_path": inp.get("file_path") or inp.get("path") or ""},
                    })
            elif etype == "message_part":
                if part.get("type") == "text":
                    txt = part.get("text") or ""
                    if txt:
                        synthetic_events.append({"type": "text", "text": txt})
        return cls.from_events(synthetic_events)


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


def _skill_tool_use_matches(tu: ToolUse, skill_id: str) -> bool:
    """True iff tool_use names the requested skill.

    CC stream-json shapes observed:
      - {"name": "Skill", "input": {"skill_id": "helix"}}            (synthetic)
      - {"name": "Skill", "input": {"skill": "helix"}}               (live)
      - {"name": "Skill", "input": {"skill": "helix:helix"}}         (live, plugin-qualified)
      - {"name": "Skill(helix)"}                                     (synthetic-friendly)
      - {"name": "helix"}                                            (synthetic-friendly)
    """
    if tu.name == f"Skill({skill_id})":
        return True
    if tu.name == skill_id:
        return True
    if tu.name == "Skill":
        sid = tu.input.get("skill_id")
        if sid == skill_id:
            return True
        skill = tu.input.get("skill")
        if isinstance(skill, str):
            # tolerate `<plugin>:<skill>` and plain `<skill>` forms
            parts = skill.split(":")
            if parts[-1] == skill_id or skill == skill_id:
                return True
    return False


def matcher_skill_tool_use(params: dict[str, Any], t: Transcript) -> MatchResult:
    skill_id = params.get("skill_id")
    if not skill_id:
        raise RowRejection("T043", "skill_tool_use requires skill_id")
    hits = [tu.index for tu in t.tool_uses if _skill_tool_use_matches(tu, skill_id)]
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
    expected_edge_regex = params.get("expected_edge_regex")
    if not graph_path or (not expected_edge and not expected_edge_regex):
        raise RowRejection(
            "T043",
            "graph_edge_observed requires graph_path and expected_edge_signature or expected_edge_regex",
        )
    try:
        graph_re = re.compile(graph_path)
    except re.error as e:
        raise RowRejection("T043", f"graph_path unparseable: {e}") from e
    if expected_edge_regex:
        try:
            edge_re = re.compile(expected_edge_regex, re.IGNORECASE)
        except re.error as e:
            raise RowRejection("T043", f"expected_edge_regex unparseable: {e}") from e
    read_indices = [
        tu.index
        for tu in t.tool_uses
        if tu.name == "Read"
        and graph_re.search(
            tu.input.get("file_path") or tu.input.get("path") or ""
        )
    ]
    if expected_edge_regex:
        surfaced = bool(edge_re.search(t.assistant_text))
    else:
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


def _load_envelope_schema(schema_path: str) -> dict[str, Any]:
    """Load the envelope JSON schema. Relative paths resolve from BENCH_ROOT."""
    p = Path(schema_path)
    if not p.is_absolute():
        p = BENCH_ROOT / schema_path
    if not p.exists():
        raise RowRejection("T043", f"envelope_schema_path not found: {p}")
    try:
        return json.loads(p.read_text())
    except json.JSONDecodeError as e:
        raise RowRejection("T043", f"envelope schema invalid JSON: {e}") from e


def _validate_envelope_shape(
    envelope: Any, schema: dict[str, Any]
) -> list[str]:
    """Lightweight JSON-schema shape check (stdlib-only, no jsonschema dep).

    Verifies required top-level keys, type for each declared property, and
    minLength/minItems where the schema declares them. Returns list of
    violation strings (empty = conforming).
    """
    errors: list[str] = []
    if not isinstance(envelope, dict):
        return ["envelope is not a JSON object"]
    required = schema.get("required") or []
    for key in required:
        if key not in envelope:
            errors.append(f"missing required key '{key}'")
    props = schema.get("properties") or {}
    type_map = {
        "string": str,
        "boolean": bool,
        "array": list,
        "object": dict,
        "number": (int, float),
        "integer": int,
    }
    for key, val in envelope.items():
        spec = props.get(key)
        if not spec:
            continue
        expected_type = spec.get("type")
        if expected_type and expected_type in type_map:
            if not isinstance(val, type_map[expected_type]):
                errors.append(f"'{key}' expected {expected_type}, got {type(val).__name__}")
                continue
        if spec.get("type") == "string":
            min_len = spec.get("minLength")
            if min_len is not None and len(val) < min_len:
                errors.append(f"'{key}' length {len(val)} < minLength {min_len}")
        if spec.get("type") == "array":
            min_items = spec.get("minItems")
            if min_items is not None and len(val) < min_items:
                errors.append(f"'{key}' has {len(val)} items < minItems {min_items}")
            item_spec = spec.get("items") or {}
            item_type = item_spec.get("type")
            item_min = item_spec.get("minLength")
            for i, it in enumerate(val):
                if item_type and item_type in type_map and not isinstance(it, type_map[item_type]):
                    errors.append(f"'{key}[{i}]' expected {item_type}, got {type(it).__name__}")
                elif item_type == "string" and item_min is not None and len(it) < item_min:
                    errors.append(f"'{key}[{i}]' length {len(it)} < minLength {item_min}")
    return errors


def _extract_envelopes(assistant_text: str) -> list[dict[str, Any]]:
    """Pull every parseable ```json fenced block from assistant prose."""
    out: list[dict[str, Any]] = []
    fence_re = re.compile(r"```json\s*\n(.*?)\n```", re.DOTALL)
    for m in fence_re.finditer(assistant_text):
        try:
            obj = json.loads(m.group(1))
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            out.append(obj)
    return out


def matcher_next_action_envelope(
    params: dict[str, Any], t: Transcript
) -> MatchResult:
    """Layer-3 matcher: agent must emit a ```json fenced envelope that:
      - parses as JSON
      - has top-level `next_action`
      - conforms to `envelope_schema_path` (shape: required + types + minLen)
      - if `offered_requires` provided, each required descriptor appears in
        envelope.offered
      - if `not_offered_forbids` provided, NONE of the forbidden descriptors
        appears in envelope.offered (and if envelope.not_offered is present,
        they are listed there).
    """
    schema_path = params.get("envelope_schema_path")
    if not schema_path:
        raise RowRejection("T043", "next_action_envelope requires envelope_schema_path")
    schema = _load_envelope_schema(schema_path)
    offered_requires = params.get("offered_requires") or []
    not_offered_forbids = params.get("not_offered_forbids") or []
    if not isinstance(offered_requires, list) or not isinstance(not_offered_forbids, list):
        raise RowRejection(
            "T043",
            "next_action_envelope: offered_requires/not_offered_forbids must be lists",
        )

    envelopes = _extract_envelopes(t.assistant_text)
    if not envelopes:
        return MatchResult(
            "absent",
            {"schema_ref": schema_path, "reason": "no fenced ```json block in prose"},
        )
    # Pick the first envelope whose shape conforms; if none conform, report
    # the closest one's errors.
    best: tuple[dict[str, Any], list[str]] | None = None
    for env in envelopes:
        errs = _validate_envelope_shape(env, schema)
        if best is None or len(errs) < len(best[1]):
            best = (env, errs)
        if not errs:
            envelope = env
            break
    else:
        return MatchResult(
            "absent",
            {
                "schema_ref": schema_path,
                "envelope": best[0] if best else None,
                "schema_errors": best[1] if best else ["no envelopes parsed"],
            },
        )

    offered = envelope.get("offered") or []
    not_offered = envelope.get("not_offered") or []
    missing = [r for r in offered_requires if r not in offered]
    forbidden_present = [f for f in not_offered_forbids if f in offered]
    if missing or forbidden_present:
        return MatchResult(
            "absent",
            {
                "schema_ref": schema_path,
                "envelope": envelope,
                "missing_required_offers": missing,
                "forbidden_offers_present": forbidden_present,
            },
        )
    return MatchResult(
        "present",
        {
            "schema_ref": schema_path,
            "envelope": envelope,
            "offered_satisfied": list(offered_requires),
            "not_offered_satisfied": [f for f in not_offered_forbids if f in not_offered or f not in offered],
        },
    )


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
            if _skill_tool_use_matches(tu, flow_id):
                if not instance or tu.input.get("instance") == instance:
                    return MatchResult(
                        "present", {"matched": tu.index, "signal": signal}
                    )
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


def matcher_route_decision_internal(
    params: dict[str, Any], t: Transcript
) -> MatchResult:
    """Grade the canonical single-skill internal-routing decision.

    Post canonical-promotion (the bench tests skills/helix/SKILL.md with
    internal routing — no sibling Skill ever fires), the routing decision is
    SEPARATE from the Skill tool_use. Skill(helix) ALWAYS fires; the
    mode-specific observable BEHAVIOR after engagement tells us whether the
    skill correctly routed to product / infra / data / web.

    Params:
      mode: one of "product" / "infra" / "data" / "web"

    The matcher checks the mode's behavior conjunction (per skills/helix/
    SKILL.md §"Internal routing modes"). It passes if ANY 2 of the 3 mode-
    specific signals fire — that's tighter than the "prose says routing to
    mode X" surface signal which is gameable.
    """
    mode = params.get("mode")
    if not mode:
        raise RowRejection("T043", "route_decision_internal requires mode")
    if mode not in ("product", "infra", "data", "web"):
        raise RowRejection(
            "T043",
            f"route_decision_internal mode must be one of product/infra/data/web (got {mode!r})",
        )

    text_lc = t.assistant_text.lower()
    read_paths = [
        (tu.input.get("file_path") or tu.input.get("path") or "")
        for tu in t.tool_uses
        if tu.name == "Read"
    ]
    bash_cmds = [
        tu.input.get("command", "")
        for tu in t.tool_uses
        if tu.name == "Bash"
    ]

    def any_read_matches(*needles: str) -> bool:
        return any(any(n in p for n in needles) for p in read_paths)

    def any_bash_matches(*needles: str) -> bool:
        return any(any(n in c for n in needles) for c in bash_cmds)

    # Per-mode signal triples. Pass requires any 2 of 3.
    if mode == "product":
        signals = {
            "read_marker_and_graph": any_read_matches(".helix.yml")
                and any_read_matches("graph.yml"),
            "read_upstream_artifact": any_read_matches(
                "product-vision", "/prd", "feature-spec", "/feat-",
                "/PRD-", "/FEAT-", "/ADR-", "principles",
            ),
            "cite_ddx_links": (
                "ddx.links" in t.assistant_text
                or "informs:" in t.assistant_text
                or "ddx.links:" in t.assistant_text
            ),
        }
    elif mode == "infra":
        signals = {
            "consult_stop_at": any_read_matches("stop-at-triggers")
                or "stop_at" in text_lc
                or "apply trigger" in text_lc
                or "secret_read trigger" in text_lc,
            "read_infra_artifact": any_read_matches(
                "architecture", "runbook", "deployment-checklist",
                "security-architecture", "tofu", "terraform",
            ),
            "confirm_before_apply": (
                ("ok to proceed" in text_lc or "shall i proceed" in text_lc
                 or "should i proceed" in text_lc or "want me to" in text_lc)
                and any_bash_matches(
                    "terraform", "tofu", "kubectl",
                    "rotate", "credentials",
                )
            ) or (
                # Or: explicit "I won't run X without confirmation" prose.
                any(
                    k in text_lc
                    for k in ("apply", "tofu", "terraform", "kubectl",
                              "credentials", "rotate")
                )
                and ("confirmation" in text_lc or "confirm before" in text_lc)
            ),
        }
    elif mode == "data":
        signals = {
            "read_data_artifact": any_read_matches(
                "data-contract", "data-quality-expectations",
                "data-architecture", "data-design",
            ),
            "cite_producer_or_pii": any(
                k in text_lc
                for k in ("producer", "consumer", "pii",
                          "governance", "classification")
            ),
            "defer_schema_change": (
                ("stop_at" in text_lc or "confirmation" in text_lc
                 or "ok to proceed" in text_lc)
                and any(k in text_lc for k in
                        ("schema", "backfill", "ingest", "migrate"))
            ),
        }
    else:  # web
        signals = {
            "read_web_artifact": any_read_matches(
                "architecture", "design-system", "monitoring-setup",
                "runbook", "release-notes",
            ),
            "cite_web_vocab": any(
                k in text_lc
                for k in ("web vitals", "rum", "page error", "page perf",
                          "lcp", "cls", "fid", "ttfb", "checkout flow")
            ),
            "defer_prod_deploy": (
                ("stop_at" in text_lc or "confirmation" in text_lc
                 or "ok to proceed" in text_lc)
                and any(k in text_lc for k in
                        ("deploy", "ship", "production", "rollout"))
            ),
        }

    fired = [k for k, v in signals.items() if v]
    verdict = "present" if len(fired) >= 2 else "absent"
    return MatchResult(
        verdict,
        {"mode": mode, "fired_signals": fired, "all_signals": list(signals.keys())},
    )


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
    "route_decision_internal": matcher_route_decision_internal,
}


# ---------------------------------------------------------------------------
# Discriminator validation (T040-T047)
# ---------------------------------------------------------------------------

# Plugin identifiers accepted by T044's negative-control "observable-changing
# modification" check. Post canonical-promotion the canonical install is
# `helix` (the plugin directory under .claude-plugin/, also valid as the repo
# root path); the legacy `methodology-*` / `helix-*` prefixes are kept so
# existing bench rows continue to validate.
METHODOLOGY_PLUGIN_PREFIXES = ("methodology-", "helix-", "helix")


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
    for key in (
        "workspace_swap",
        "marker_edit",
        "autonomy_override",
        "autonomy_swap",
        "graph_swap",
    ):
        if neg.get(key):
            modifications_seen.append(key)
    if not modifications_seen:
        raise RowRejection(
            "T044",
            "negative_control has no observable-changing modification "
            "(need plugins_remove, marker_edit, graph_swap, workspace_swap, "
            "autonomy_override, or autonomy_swap)",
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


# ---------------------------------------------------------------------------
# Validator-row mode (RC-01..RC-04 family)
#
# A "validator row" exercises helix_check.py directly (not a CC stream-json
# transcript). Shape: `expected.yml` carries `kind: validator-row`, names the
# helix_check.py args, and declares expected exit code + required/forbidden
# codes + required diagnostic phrases. The runner exec's helix_check.py from
# the row dir and asserts.
# ---------------------------------------------------------------------------


HELIX_CHECK_PATH = REPO_ROOT / "library" / "scripts" / "helix_check.py"


def is_validator_row(expected: dict[str, Any]) -> bool:
    return isinstance(expected, dict) and expected.get("kind") == "validator-row"


def validate_validator_row(row_dir: Path, expected: dict[str, Any]) -> dict[str, Any]:
    """Minimal shape-validation for a validator-row's expected.yml.

    Distinct from discriminator validation (T040-T047): validator rows have
    their own schema since they don't carry observable/negative_control.
    """
    args = expected.get("helix_check_args")
    if not isinstance(args, list) or not args:
        raise RowRejection(
            "T040", "validator-row expected.yml missing `helix_check_args:` list"
        )
    target = expected.get("target")
    if target:
        target_path = row_dir / target
        if not target_path.exists():
            raise RowRejection(
                "T040", f"validator-row target `{target}` missing from {row_dir}"
            )
    if "expected_exit_code" not in expected:
        raise RowRejection(
            "T040", "validator-row expected.yml missing `expected_exit_code:`"
        )
    return {
        "kind": "validator-row",
        "helix_check_args": [str(a) for a in args],
        "expected_exit_code": int(expected["expected_exit_code"]),
        "required_codes": list(expected.get("required_codes") or []),
        "forbidden_codes": list(expected.get("forbidden_codes") or []),
        "required_phrases": list(expected.get("required_phrases") or []),
    }


def run_validator_row(row_dir: Path) -> int:
    """Execute helix_check.py against a validator row and check the contract.

    Returns 0 on pass, non-zero on any failed assertion. Prints a JSON
    summary to stdout for parity with `run_row`.
    """
    import subprocess

    try:
        expected = load_row(row_dir)
        norm = validate_validator_row(row_dir, expected)
    except RowRejection as e:
        print(f"REJECT {e.code} {row_dir.name}: {e.detail}", file=sys.stderr)
        return 1

    if not HELIX_CHECK_PATH.exists():
        print(
            f"REJECT R010 {row_dir.name}: helix_check.py not found at {HELIX_CHECK_PATH}",
            file=sys.stderr,
        )
        return 1

    cmd = [sys.executable, str(HELIX_CHECK_PATH)] + norm["helix_check_args"]
    proc = subprocess.run(
        cmd, cwd=str(row_dir), capture_output=True, text=True
    )
    out = proc.stdout + proc.stderr
    actual_exit = proc.returncode

    failures: list[str] = []
    if actual_exit != norm["expected_exit_code"]:
        failures.append(
            f"exit code: expected {norm['expected_exit_code']}, got {actual_exit}"
        )
    for code in norm["required_codes"]:
        # Match the validator's "ERROR <CODE>:" / "warn  <CODE>:" line shape.
        if not re.search(rf"\b{re.escape(code)}\b", out):
            failures.append(f"required code `{code}` not in output")
    for code in norm["forbidden_codes"]:
        if re.search(rf"\b{re.escape(code)}\b", out):
            failures.append(f"forbidden code `{code}` present in output")
    for phrase in norm["required_phrases"]:
        if phrase not in out:
            failures.append(f"required phrase `{phrase}` not in output")

    summary = {
        "row": str(row_dir),
        "kind": "validator-row",
        "cmd": cmd,
        "actual_exit_code": actual_exit,
        "expected_exit_code": norm["expected_exit_code"],
        "status": "pass" if not failures else "fail",
        "failures": failures,
    }
    print(json.dumps(summary, indent=2))
    if failures:
        print("\n--- helix_check.py output ---", file=sys.stderr)
        print(out, file=sys.stderr)
        return 1
    return 0


def validate_row(
    row_dir: Path,
    whitelist: Whitelist | None = None,
    banned: BannedPatterns | None = None,
) -> dict[str, Any]:
    whitelist = whitelist or Whitelist.load()
    banned = banned or BannedPatterns.load()
    expected = load_row(row_dir)
    if is_validator_row(expected):
        return validate_validator_row(row_dir, expected)
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
                        "text": (
                            "Here is my plan:\n```json\n"
                            "{\"next_action\": \"draft_artifact:product-vision\", "
                            "\"offered\": [\"draft_artifact:product-vision\"], "
                            "\"reason\": \"marker absent; graph prereq forces vision first\"}"
                            "\n```"
                        ),
                    }
                ]
            ),
            {
                "envelope_schema_path": "judge/next-action-envelope.schema.json",
                "offered_requires": ["draft_artifact:product-vision"],
            },
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
# Phase 0b — meta-tests, property tests, golden schema, cost + observability
# ---------------------------------------------------------------------------


def run_meta_tests(verbose: bool = True) -> tuple[int, dict[str, Any]]:
    """Walk family-test/bench/runner/meta-tests and grade all 10 cases.

    Reject rows (MT01-MT05) MUST raise the labeled `expected_rejection` code.
    Accept rows (MT06-MT10) MUST validate AND, when a transcript.jsonl is
    present, the matcher's verdict MUST equal `expected_verdict`.
    """
    whitelist = Whitelist.load()
    banned = BannedPatterns.load()
    summary: dict[str, Any] = {
        "total": 0,
        "pass": 0,
        "fail": [],
    }
    if not META_TESTS_DIR.exists():
        return 1, {"error": f"meta-tests dir missing: {META_TESTS_DIR}"}
    for row_dir in sorted(META_TESTS_DIR.iterdir()):
        if not row_dir.is_dir():
            continue
        expected_path = row_dir / "expected.yml"
        if not expected_path.exists():
            continue
        summary["total"] += 1
        try:
            doc = yaml.safe_load(expected_path.read_text()) or {}
        except yaml.YAMLError as e:
            summary["fail"].append({"row": row_dir.name, "err": f"yaml parse: {e}"})
            continue
        meta = doc.get("meta_test") or {}
        expected_rejection = meta.get("expected_rejection")
        expected_acceptance = meta.get("expected_acceptance", False)
        try:
            norm = validate_discriminator(doc, whitelist, banned)
        except RowRejection as e:
            if expected_rejection and e.code == expected_rejection:
                summary["pass"] += 1
            else:
                summary["fail"].append(
                    {
                        "row": row_dir.name,
                        "expected_rejection": expected_rejection,
                        "got_code": e.code,
                        "detail": e.detail,
                    }
                )
            continue
        # Validator accepted the row.
        if expected_rejection:
            summary["fail"].append(
                {
                    "row": row_dir.name,
                    "expected_rejection": expected_rejection,
                    "got_code": "ACCEPTED",
                    "detail": "validator did not raise",
                }
            )
            continue
        if not expected_acceptance:
            summary["fail"].append(
                {"row": row_dir.name, "err": "row missing expected_acceptance/_rejection"}
            )
            continue
        transcript_path = row_dir / "transcript.jsonl"
        if not transcript_path.exists():
            # accept-only row with no transcript: validation alone is the pass condition
            summary["pass"] += 1
            continue
        # Grade matcher against the transcript.
        try:
            transcript = Transcript.parse(transcript_path)
            matcher = MATCHER_REGISTRY[norm["assertion_id"]]
            result = matcher(norm["params"], transcript)
        except Exception as e:  # pragma: no cover (path is exercised below)
            summary["fail"].append(
                {"row": row_dir.name, "err": f"grade error: {e}"}
            )
            continue
        expected_verdict = meta.get("expected_verdict")
        if expected_verdict and result.verdict != expected_verdict:
            summary["fail"].append(
                {
                    "row": row_dir.name,
                    "expected_verdict": expected_verdict,
                    "got_verdict": result.verdict,
                    "details": result.details,
                }
            )
        else:
            summary["pass"] += 1

    ok = summary["pass"] == summary["total"] and not summary["fail"]
    if verbose:
        print(f"meta-tests: {summary['pass']}/{summary['total']} pass")
        for f in summary["fail"]:
            print(f"  FAIL {f}")
    return (0 if ok else 1), summary


def run_property_tests(verbose: bool = True) -> tuple[int, dict[str, Any]]:
    """Run the 4-property property-tests harness (100 cases each)."""
    sys.path.insert(0, str(PROPERTY_TESTS_DIR))
    try:
        import properties  # type: ignore
    finally:
        # leave sys.path mutated for the rest of the process; harmless
        pass
    s = properties.run_all(dump_dir=None)
    ok = s["total_fail"] == 0
    if verbose:
        print(
            f"property-tests: {s['total_pass']}/{s['total_pass'] + s['total_fail']} pass "
            f"({s['cases_per_property']} cases × {len(s['properties'])} properties)"
        )
        for name, p in s["properties"].items():
            if p["fail"]:
                print(f"  FAIL {name}: {p['fail']} cases")
                for f in p["failures"]:
                    print(f"    - {f}")
    return (0 if ok else 1), s


def validate_golden_transcript(jsonl_path: Path, meta_path: Path) -> tuple[bool, str]:
    """Validate one golden against the transcript_schema contract.

    Checks:
      - jsonl parses cleanly as one JSON object per non-empty line
      - every event type is in allowed_event_types
      - the meta-header carries cc_version, assertion_id, expected_verdict, description
      - cc_version equals cc-version.lock claude_code_version
      - assertion_id is in the whitelist
      - the goldens' transcripts produce verdict == expected_verdict when graded
    """
    schema = yaml.safe_load(TRANSCRIPT_SCHEMA.read_text())
    allowed = set(schema.get("allowed_event_types") or [])
    if not jsonl_path.exists():
        return False, f"golden jsonl missing: {jsonl_path}"
    events: list[dict[str, Any]] = []
    for line_no, raw in enumerate(jsonl_path.read_text().splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError as e:
            return False, f"{jsonl_path.name} line {line_no}: invalid JSON: {e}"
        if not isinstance(ev, dict):
            return False, f"{jsonl_path.name} line {line_no}: event not a JSON object"
        etype = ev.get("type")
        if etype not in allowed:
            return False, f"{jsonl_path.name} line {line_no}: event type '{etype}' not in {sorted(allowed)}"
        events.append(ev)
    if not meta_path.exists():
        return False, f"golden meta missing: {meta_path}"
    meta = yaml.safe_load(meta_path.read_text()) or {}
    required_meta = ["cc_version", "assertion_id", "expected_verdict", "description"]
    for key in required_meta:
        if key not in meta:
            return False, f"{meta_path.name}: missing required key '{key}'"
    if len(str(meta.get("description") or "").strip()) < 20:
        return False, f"{meta_path.name}: description must be >= 20 chars"
    pinned = yaml.safe_load(CC_VERSION_LOCK.read_text()) or {}
    if meta["cc_version"] != pinned.get("claude_code_version"):
        return (
            False,
            f"{meta_path.name}: cc_version {meta['cc_version']!r} != pin {pinned.get('claude_code_version')!r}",
        )
    whitelist = Whitelist.load()
    if meta["assertion_id"] not in whitelist.by_id:
        return False, f"{meta_path.name}: assertion_id not in whitelist"
    # Grade the transcript with the declared matcher + params.
    transcript = Transcript.from_events(events)
    matcher = MATCHER_REGISTRY[meta["assertion_id"]]
    try:
        params = meta.get("params") or {}
        result = matcher(params, transcript)
    except RowRejection as e:
        return False, f"{meta_path.name}: matcher rejected: {e}"
    if result.verdict != meta["expected_verdict"]:
        return (
            False,
            f"{meta_path.name}: graded verdict {result.verdict!r} != expected {meta['expected_verdict']!r} (details={result.details})",
        )
    return True, "ok"


def run_golden_schema_check(verbose: bool = True) -> tuple[int, dict[str, Any]]:
    """Validate every golden transcript pair under family-test/bench/golden-transcripts/."""
    summary: dict[str, Any] = {"total": 0, "pass": 0, "fail": []}
    if not GOLDEN_DIR.exists():
        return 1, {"error": f"golden-transcripts dir missing: {GOLDEN_DIR}"}
    for jsonl in sorted(GOLDEN_DIR.glob("*.golden.jsonl")):
        meta = jsonl.with_suffix("").with_suffix(".meta.yml")
        summary["total"] += 1
        ok, msg = validate_golden_transcript(jsonl, meta)
        if ok:
            summary["pass"] += 1
        else:
            summary["fail"].append({"golden": jsonl.name, "err": msg})
    ok = summary["pass"] == summary["total"] and not summary["fail"]
    if verbose:
        print(f"golden-transcripts: {summary['pass']}/{summary['total']} pass")
        for f in summary["fail"]:
            print(f"  FAIL {f}")
    return (0 if ok else 1), summary


def run_model_plumbing_self_test(verbose: bool = True) -> tuple[int, dict[str, Any]]:
    """Verify --model flag is plumbed through to run-probe.sh and per-row override.

    Three checks (all offline; no docker invocation):
      1) `resolve_row_model` honours a per-row `model:` override in expected.yml
      2) `resolve_row_model` falls back to the default when no override
      3) `run-probe.sh` injects `--model <id>` into its in-container claude
         invocation when HELIX_PROBE_MODEL is set (verified by shellcheck-grade
         grep over the script body — the BOOTSTRAP is built from this env var)
    """
    import tempfile

    summary: dict[str, Any] = {"checks": [], "pass": 0, "total": 0}

    # (1) per-row override is respected
    with tempfile.TemporaryDirectory() as td:
        row = Path(td) / "row"
        row.mkdir()
        (row / "expected.yml").write_text("model: claude-haiku-4-5\n")
        observed = resolve_row_model(row, DEFAULT_MODEL)
        check1 = {
            "name": "per_row_override_respected",
            "observed": observed,
            "expected": "claude-haiku-4-5",
            "pass": observed == "claude-haiku-4-5",
        }
        summary["total"] += 1
        if check1["pass"]:
            summary["pass"] += 1
        summary["checks"].append(check1)

    # (2) default applies when no override
    with tempfile.TemporaryDirectory() as td:
        row = Path(td) / "row"
        row.mkdir()
        (row / "expected.yml").write_text("kind: validator-row\n")
        observed = resolve_row_model(row, DEFAULT_MODEL)
        check2 = {
            "name": "default_applies_when_no_override",
            "observed": observed,
            "expected": DEFAULT_MODEL,
            "pass": observed == DEFAULT_MODEL,
        }
        summary["total"] += 1
        if check2["pass"]:
            summary["pass"] += 1
        summary["checks"].append(check2)

    # (3) run-probe.sh references HELIX_PROBE_MODEL and emits `--model`
    probe_text = RUN_PROBE_SH.read_text() if RUN_PROBE_SH.exists() else ""
    plumbed = "HELIX_PROBE_MODEL" in probe_text and "--model" in probe_text
    check3 = {
        "name": "run_probe_plumbs_model_flag",
        "pass": plumbed,
        "detail": (
            "found HELIX_PROBE_MODEL + --model in run-probe.sh"
            if plumbed
            else "missing HELIX_PROBE_MODEL or --model in run-probe.sh"
        ),
    }
    summary["total"] += 1
    if plumbed:
        summary["pass"] += 1
    summary["checks"].append(check3)

    ok = summary["pass"] == summary["total"]
    if verbose:
        print(f"model-plumbing self-test: {summary['pass']}/{summary['total']} checks pass")
        for c in summary["checks"]:
            if not c["pass"]:
                print(f"  FAIL {c}")
    return (0 if ok else 1), summary


def run_phase0b_self_test(verbose: bool = True) -> tuple[int, dict[str, Any]]:
    """Aggregate self-test: smoke (0a) + meta + property + golden + cost + dump."""
    overall: dict[str, Any] = {}
    rc = 0

    code, summary = run_smoke(verbose=verbose)
    overall["smoke"] = summary
    rc = max(rc, code)

    code, summary = run_meta_tests(verbose=verbose)
    overall["meta_tests"] = summary
    rc = max(rc, code)

    code, summary = run_property_tests(verbose=verbose)
    overall["property_tests"] = summary
    rc = max(rc, code)

    code, summary = run_golden_schema_check(verbose=verbose)
    overall["golden_transcripts"] = summary
    rc = max(rc, code)

    # cost tracker self-test (arithmetic round-trip)
    sys.path.insert(0, str(BENCH_ROOT / "runner"))
    import cost_tracker  # type: ignore
    cc = cost_tracker.self_test()
    overall["cost_tracker"] = {"exit_code": cc}
    rc = max(rc, cc)

    # failure-dump scaffold self-test (4 artifacts present)
    import failure_dump  # type: ignore
    fd = failure_dump.scaffold_self_test()
    overall["failure_dump"] = {"exit_code": fd}
    rc = max(rc, fd)

    # Layer 3 envelope-pass + non-contamination self-test
    ec, esum = run_envelope_self_test(verbose=verbose)
    overall["envelope_pass"] = esum
    rc = max(rc, ec)

    # --model flag plumbing (default + per-row override + probe-script wiring)
    mc, msum = run_model_plumbing_self_test(verbose=verbose)
    overall["model_plumbing"] = msum
    rc = max(rc, mc)

    if verbose:
        print(f"self-test overall: {'PASS' if rc == 0 else 'FAIL'}")
    return rc, overall


def run_envelope_self_test(verbose: bool = True) -> tuple[int, dict[str, Any]]:
    """Synthetic-fixture self-test for Layer 3 + non-contamination invariant.

    Builds two transcripts in-memory:
      - no-envelope: a Skill(helix) tool_use + prose (Layer 1 = present)
      - envelope:   same Skill(helix) tool_use + prose + fenced ```json envelope

    Asserts:
      1) envelope-pass matcher verdict == present (envelope conforms; offered
         contains the required descriptor)
      2) Layer 1 verdict identical across the two transcripts (skill_tool_use
         present in BOTH)
      3) negative contamination: a synthetic envelope transcript that drops
         the Skill tool_use causes the non-contamination check to FAIL
         (Layer 1 absent vs present) — proves the check fires when it should.
    """
    summary: dict[str, Any] = {"checks": [], "pass": 0, "total": 0}

    schema_path = "judge/next-action-envelope.schema.json"
    if not ENVELOPE_SCHEMA.exists():
        return 1, {"error": f"envelope schema missing: {ENVELOPE_SCHEMA}"}

    # (1) envelope-pass matcher: positive
    envelope_obj = {
        "next_action": "draft_artifact:product-vision",
        "offered": ["draft_artifact:product-vision", "add_methodology_to_marker:helix"],
        "not_offered": ["draft_artifact:prd"],
        "reason": "Graph says prd informs from product-vision; marker absent so we offer vision first.",
        "requires_confirmation": True,
    }
    env_prose = (
        "I will offer to draft the product vision first.\n```json\n"
        + json.dumps(envelope_obj)
        + "\n```"
    )
    t_env = Transcript.from_events(
        [
            {"type": "tool_use", "name": "Skill", "input": {"skill_id": "helix"}},
            {"type": "text", "text": env_prose},
        ]
    )
    t_no = Transcript.from_events(
        [
            {"type": "tool_use", "name": "Skill", "input": {"skill_id": "helix"}},
            {
                "type": "text",
                "text": "I will offer to draft the product vision first.",
            },
        ]
    )
    res = matcher_next_action_envelope(
        {
            "envelope_schema_path": schema_path,
            "offered_requires": ["draft_artifact:product-vision"],
            "not_offered_forbids": ["draft_artifact:prd"],
        },
        t_env,
    )
    check1 = {"name": "envelope_present", "verdict": res.verdict, "expected": "present"}
    summary["total"] += 1
    if res.verdict == "present":
        summary["pass"] += 1
    else:
        check1["details"] = res.details
    summary["checks"].append(check1)

    # (2) Layer 1 verdicts identical across passes
    l1 = matcher_skill_tool_use({"skill_id": "helix"}, t_no)
    l1_env = matcher_skill_tool_use({"skill_id": "helix"}, t_env)
    check2 = {
        "name": "layer1_identical_across_passes",
        "no_envelope": l1.verdict,
        "envelope": l1_env.verdict,
        "identical": l1.verdict == l1_env.verdict,
    }
    summary["total"] += 1
    if check2["identical"]:
        summary["pass"] += 1
    summary["checks"].append(check2)

    # (3) negative contamination: divergent Layer 1 across passes -> fail signal
    t_env_bad = Transcript.from_events(
        [
            {
                "type": "text",
                "text": "I will offer to draft the product vision.\n```json\n"
                + json.dumps(envelope_obj)
                + "\n```",
            }
        ]
    )
    l1_bad = matcher_skill_tool_use({"skill_id": "helix"}, t_env_bad)
    check3 = {
        "name": "contamination_check_fires_when_divergent",
        "no_envelope": l1.verdict,
        "envelope_bad": l1_bad.verdict,
        "diverged": l1.verdict != l1_bad.verdict,
    }
    summary["total"] += 1
    if check3["diverged"]:
        summary["pass"] += 1
    summary["checks"].append(check3)

    # (4) shape error: missing required field -> absent
    bad_env_prose = (
        "Here is my plan:\n```json\n"
        + json.dumps({"next_action": "draft_artifact:product-vision"})
        + "\n```"
    )
    t_bad = Transcript.from_events([{"type": "text", "text": bad_env_prose}])
    res_bad = matcher_next_action_envelope(
        {
            "envelope_schema_path": schema_path,
            "offered_requires": ["draft_artifact:product-vision"],
        },
        t_bad,
    )
    check4 = {
        "name": "envelope_missing_required_keys_rejected",
        "verdict": res_bad.verdict,
        "expected": "absent",
    }
    summary["total"] += 1
    if res_bad.verdict == "absent":
        summary["pass"] += 1
    else:
        check4["details"] = res_bad.details
    summary["checks"].append(check4)

    ok = summary["pass"] == summary["total"]
    if verbose:
        print(f"envelope-pass self-test: {summary['pass']}/{summary['total']} checks pass")
        for c in summary["checks"]:
            if c.get("verdict") and c["verdict"] != c.get("expected", c["verdict"]):
                print(f"  FAIL {c}")
            elif "identical" in c and not c["identical"]:
                print(f"  FAIL {c}")
            elif "diverged" in c and not c["diverged"]:
                print(f"  FAIL {c}")
    return (0 if ok else 1), summary


# ---------------------------------------------------------------------------
# Row run (placeholder for Phase 0a; full CC invocation is Phase 1+)
# ---------------------------------------------------------------------------


def run_row(row_dir: Path, determinism: int = 1) -> int:
    """Phase 0a row-run validates the row but defers CC invocation.

    For validator-rows (RC-* family) the runner actually executes
    helix_check.py and asserts the contract — no CC required.

    Returns 0 if the row validates; non-zero on rejection.
    """
    # Detect validator-row early so we route to actual execution, not
    # discriminator validation.
    try:
        expected = load_row(row_dir)
    except RowRejection as e:
        print(f"REJECT {e.code} {row_dir.name}: {e.detail}", file=sys.stderr)
        return 1
    if is_validator_row(expected):
        return run_validator_row(row_dir)

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
# Phase 1+ — live CC invocation, multi-turn, determinism aggregation, runs/,
# routing-evals, ratchet integration.
#
# Per-row CC invocation uses family-test/docker/run-probe.sh as the harness:
#   run-probe.sh <fixture-dir> <plugins-spec> <prompt-file> <evidence-file>
# auth is supplied by the script (ANTHROPIC_API_KEY env OR token at
# ~/.cache/family-test-auth/token). Plugins listed in plugins.txt map to
# `<FAMILY_TEST_ROOT>/<name>` (e.g. `methodology-product`, `library`).
# ---------------------------------------------------------------------------


import datetime as _dt
import subprocess
import time as _time
import uuid as _uuid


def new_run_id() -> str:
    """ISO-ish run id used to namespace runs/<run-id>/ directories."""
    ts = _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{ts}-{_uuid.uuid4().hex[:6]}"


def resolve_plugins(plugins_file: Path) -> list[Path]:
    """Read plugins.txt and resolve each entry to a host directory.

    Each line is either:
      - an absolute path (e.g. /Users/erik/Projects/helix) — used as-is;
        this is the canonical-install convention post-promotion
      - a relative name under FAMILY_TEST_ROOT/ (legacy multi-flow research
        layout — `methodology-product`, `library`, etc.) — resolved relative
        to FAMILY_TEST_ROOT

    Empty lines and `#` comments are skipped.
    """
    if not plugins_file.exists():
        return []
    paths: list[Path] = []
    for raw in plugins_file.read_text().splitlines():
        name = raw.strip()
        if not name or name.startswith("#"):
            continue
        if name.startswith("/"):
            candidate = Path(name)
        else:
            candidate = FAMILY_TEST_ROOT / name
        if not candidate.is_dir():
            raise FileNotFoundError(
                f"plugin '{name}' not found at {candidate}"
            )
        paths.append(candidate)
    return paths


def load_conversation(row_dir: Path) -> list[str]:
    """Return ordered list of user-turn prompts from conversation.yml."""
    conv_path = row_dir / "conversation.yml"
    if not conv_path.exists():
        raise FileNotFoundError(f"missing conversation.yml in {row_dir}")
    doc = yaml.safe_load(conv_path.read_text()) or {}
    turns = doc.get("turns") or []
    out: list[str] = []
    for t in turns:
        if not isinstance(t, dict):
            continue
        if "user" in t and t["user"] is not None:
            out.append(str(t["user"]).rstrip())
    return out


def _stitch_multi_turn_prompt(turns: list[str]) -> str:
    """Concatenate multi-turn user turns into a single prompt.

    Headless `claude -p` does not natively replay a turn history. For
    multi-turn rows we serialize the conversation with explicit role
    markers so the model sees the full context in a single pass. The
    final turn carries the assertion target; earlier turns establish
    warm-context state. This is the pragmatic Phase 1 approach.
    """
    if len(turns) == 1:
        return turns[0]
    parts = []
    for i, t in enumerate(turns, start=1):
        parts.append(f"--- Turn {i} (user) ---\n{t}")
    parts.append(
        "--- End of prior turns ---\n"
        "Respond only to the FINAL user turn above; treat earlier turns "
        "as conversation history that already occurred."
    )
    return "\n\n".join(parts)


def invoke_probe(
    fixture_dir: Path,
    plugins: list[Path],
    prompt: str,
    evidence_file: Path,
    cwd_rel: str = "",
    timeout_s: int = 600,
    model: str | None = None,
    runtime: str = DEFAULT_RUNTIME,
) -> tuple[int, str]:
    """Run a probe once and return (returncode, stderr_text).

    The probe writes JSONL events to `evidence_file`. stderr is captured
    separately for diagnostics.

    `model` (if set) is forwarded as HELIX_PROBE_MODEL so the underlying
    probe script appends `--model <id>` to its invocation.

    `runtime` selects the harness:
      - "claude":   family-test/docker/run-probe.sh  (Docker, claude stream-json)
      - "codex":    family-test/bench/runner/run-probe-codex.sh (host, codex --json)
      - "opencode": family-test/bench/runner/run-probe-opencode.sh (host, opencode --format json)
    """
    if runtime not in SUPPORTED_RUNTIMES:
        raise ValueError(f"unknown runtime {runtime!r}; supported: {SUPPORTED_RUNTIMES}")
    if runtime == "claude":
        probe_script = RUN_PROBE_SH
    elif runtime == "codex":
        probe_script = RUN_PROBE_CODEX_SH
    else:  # opencode
        probe_script = RUN_PROBE_OPENCODE_SH
    if not probe_script.exists():
        raise FileNotFoundError(f"probe script not found at {probe_script}")
    fixture_dir = fixture_dir.resolve()
    evidence_file = evidence_file.resolve()
    plugins = [p.resolve() for p in plugins]
    evidence_file.parent.mkdir(parents=True, exist_ok=True)
    prompt_file = evidence_file.with_suffix(evidence_file.suffix + ".prompt.txt")
    prompt_file.write_text(prompt)
    plugins_spec = ",".join(str(p) for p in plugins)
    cmd = [
        "bash",
        str(probe_script),
        str(fixture_dir),
        plugins_spec,
        str(prompt_file),
        str(evidence_file),
    ]
    if cwd_rel:
        cmd.append(cwd_rel)
    env = os.environ.copy()
    if model:
        env["HELIX_PROBE_MODEL"] = model
    else:
        env.pop("HELIX_PROBE_MODEL", None)
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout_s,
            check=False, env=env,
        )
    except subprocess.TimeoutExpired as e:
        return 124, f"timeout after {timeout_s}s: {e}"
    return proc.returncode, proc.stderr or ""


def parse_runtime_transcript(evidence_file: Path, runtime: str) -> Transcript:
    """Parse a probe's evidence file using the correct runtime shape."""
    if runtime == "codex":
        return Transcript.parse_codex(evidence_file)
    if runtime == "opencode":
        return Transcript.parse_opencode(evidence_file)
    return Transcript.parse(evidence_file)


def _stream_json_result_event(events: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Find a `result` event in stream-json (usage + final cost)."""
    for ev in events:
        if ev.get("type") == "result":
            return ev
    return None


def _detect_auth_failure(evidence_text: str) -> bool:
    """Heuristic: stream-json evidence shows auth failure."""
    needles = (
        "authentication_failed",
        "Not logged in",
        "Please run /login",
        "Invalid API key",
        "invalid_api_key",
    )
    return any(n in evidence_text for n in needles)


def _grade_row_transcript(
    row_dir: Path,
    transcript: Transcript,
    runtime: str = DEFAULT_RUNTIME,
) -> dict[str, Any]:
    """Grade a row's parsed transcript against its discriminator.

    For runtimes that lack a Skill tool surface (codex), we degrade
    skill-tool-based assertions to prose_attribution per plan §1.4b: the
    matcher whitelist already allows the route_decision matcher to use
    `routing_signal: prose_attribution` as a runtime-independent fallback.
    """
    norm = validate_row(row_dir)
    aid = norm["assertion_id"]
    params = dict(norm["params"])
    fallback_used: str | None = None
    if runtime == "codex":
        if aid == "skill_tool_use":
            # Reinterpret as prose_attribution against the skill_id.
            skill_id = params.get("skill_id") or ""
            params = {"expected_flow_instance": skill_id, "routing_signal": "prose_attribution"}
            aid = "route_decision"
            fallback_used = "skill_tool_use→route_decision/prose_attribution"
        elif aid == "route_decision" and params.get("routing_signal") == "explicit_skill_tool_use":
            params = dict(params)
            params["routing_signal"] = "prose_attribution"
            fallback_used = "route_decision/explicit_skill_tool_use→prose_attribution"
    matcher = MATCHER_REGISTRY[aid]
    try:
        result = matcher(params, transcript)
    except RowRejection as e:
        return {
            "verdict": "error",
            "error": str(e),
            "assertion_id": aid,
            "details": {},
            "runtime": runtime,
            "fallback_used": fallback_used,
        }
    expected = norm["expected_in_positive_run"]
    return {
        "assertion_id": aid,
        "verdict": result.verdict,
        "expected_verdict": expected,
        "pass": result.verdict == expected,
        "details": result.details,
        "runtime": runtime,
        "fallback_used": fallback_used,
    }


def _log_cost_from_evidence(
    evidence_file: Path,
    row_id: str,
    duration_s: float,
    phase: str = "bench",
    extra_notes: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    """Parse the row's stream-json, log a cost entry, return the result event."""
    if not evidence_file.exists():
        return None
    try:
        text = evidence_file.read_text()
    except Exception:
        return None
    events: list[dict[str, Any]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    result_ev = _stream_json_result_event(events)
    sys.path.insert(0, str(BENCH_ROOT / "runner"))
    try:
        import cost_tracker  # type: ignore
    except ImportError:
        return result_ev
    if result_ev is not None:
        entry = cost_tracker.from_result_event(
            result_ev,
            row_id=row_id,
            phase=phase,
            duration_s=duration_s,
            notes=extra_notes or {},
        )
        cost_tracker.record(entry, path=COST_LOG_PATH)
    return result_ev


def resolve_row_model(row_dir: Path, default_model: str) -> str:
    """Return the model id for a row: per-row override or default.

    A row may declare `model: claude-haiku-4-5` at the top level of
    `expected.yml` to opt into a cheaper model. The runner respects this and
    threads it through to `claude -p --model <id>`.
    """
    expected_path = row_dir / "expected.yml"
    if not expected_path.exists():
        return default_model
    try:
        doc = yaml.safe_load(expected_path.read_text()) or {}
    except yaml.YAMLError:
        return default_model
    override = doc.get("model") if isinstance(doc, dict) else None
    if isinstance(override, str) and override.strip():
        return override.strip()
    return default_model


def run_row_live(
    row_dir: Path,
    run_dir: Path,
    determinism: int = 1,
    timeout_s: int = 600,
    verbose: bool = True,
    model: str = DEFAULT_MODEL,
    runtime: str = DEFAULT_RUNTIME,
) -> dict[str, Any]:
    """Live-execute a row N times, persist transcripts, grade each pass.

    Returns a dict:
      {
        "row_id": str,
        "kind": "validator-row" | "conversation",
        "passes": [ {pass_idx, evidence_file, verdict, pass, ...} ... ],
        "aggregate": "stable-pass" | "flake" | "stable-fail" | "error",
      }
    """
    row_id = row_dir.name
    out: dict[str, Any] = {
        "row_id": row_id,
        "row_dir": str(row_dir),
        "determinism": determinism,
        "passes": [],
        "aggregate": "stable-fail",
    }

    # Validator row: deterministic — run once via helix_check.py.
    expected = load_row(row_dir)
    if is_validator_row(expected):
        rc = run_validator_row(row_dir)
        out["kind"] = "validator-row"
        out["passes"] = [{"pass_idx": 0, "exit_code": rc, "pass": rc == 0}]
        out["aggregate"] = "stable-pass" if rc == 0 else "stable-fail"
        return out

    out["kind"] = "conversation"
    fixture_dir = row_dir / "workspace"
    if not fixture_dir.is_dir():
        out["aggregate"] = "error"
        out["error"] = f"missing workspace dir: {fixture_dir}"
        return out

    try:
        plugins = resolve_plugins(row_dir / "plugins.txt")
    except FileNotFoundError as e:
        out["aggregate"] = "error"
        out["error"] = str(e)
        return out

    turns = load_conversation(row_dir)
    if not turns:
        out["aggregate"] = "error"
        out["error"] = "conversation.yml has no user turns"
        return out
    prompt = _stitch_multi_turn_prompt(turns)

    row_model = resolve_row_model(row_dir, model)
    out["model"] = row_model
    out["runtime"] = runtime

    pass_verdicts: list[bool] = []
    for i in range(determinism):
        evidence_file = run_dir / f"{row_id}.pass{i}.stream.jsonl"
        if verbose:
            print(
                f"[run {row_id} pass {i+1}/{determinism}] runtime={runtime} model={row_model} invoking probe...",
                file=sys.stderr,
            )
        t0 = _time.monotonic()
        rc, stderr = invoke_probe(
            fixture_dir, plugins, prompt, evidence_file,
            timeout_s=timeout_s, model=row_model, runtime=runtime,
        )
        dt = _time.monotonic() - t0
        pass_record: dict[str, Any] = {
            "pass_idx": i,
            "evidence_file": str(evidence_file),
            "probe_rc": rc,
            "duration_s": round(dt, 3),
        }
        # detect auth failure -> bubble up as halt signal
        evidence_text = evidence_file.read_text() if evidence_file.exists() else ""
        if rc != 0 and _detect_auth_failure(evidence_text + "\n" + stderr):
            pass_record["error"] = "auth_failure"
            pass_record["pass"] = False
            pass_record["stderr_tail"] = stderr[-400:]
            out["passes"].append(pass_record)
            out["aggregate"] = "error"
            out["halt_reason"] = "auth_failure"
            return out
        if rc != 0:
            pass_record["error"] = f"probe rc={rc}"
            pass_record["stderr_tail"] = stderr[-400:]
        # log cost regardless of pass/fail (so we still see token burn)
        result_ev = _log_cost_from_evidence(
            evidence_file,
            row_id=row_id,
            duration_s=dt,
            phase="bench",
            extra_notes={"pass_idx": i, "probe_rc": rc, "model": row_model},
        )
        if result_ev is not None:
            pass_record["session_id"] = result_ev.get("session_id")
            pass_record["total_cost_usd"] = result_ev.get("total_cost_usd")
        # parse + grade
        try:
            transcript = parse_runtime_transcript(evidence_file, runtime)
        except Exception as e:
            pass_record["error"] = pass_record.get("error") or f"parse: {e}"
            pass_record["pass"] = False
            out["passes"].append(pass_record)
            pass_verdicts.append(False)
            continue
        grade = _grade_row_transcript(row_dir, transcript, runtime=runtime)
        pass_record.update(grade)
        pass_record["pass"] = bool(grade.get("pass"))
        pass_verdicts.append(pass_record["pass"])
        out["passes"].append(pass_record)
        if verbose:
            mark = "PASS" if pass_record["pass"] else "FAIL"
            print(f"  [{mark}] verdict={grade.get('verdict')} expected={grade.get('expected_verdict')}", file=sys.stderr)

    # determinism aggregation
    if not pass_verdicts:
        out["aggregate"] = "error"
    elif all(pass_verdicts):
        out["aggregate"] = "stable-pass"
    elif not any(pass_verdicts):
        out["aggregate"] = "stable-fail"
    else:
        out["aggregate"] = "flake"
    return out


def _discover_conversation_rows(target: str | None) -> list[Path]:
    """Resolve a row-dir-or-glob argument into a sorted list of row dirs."""
    if target is None:
        return sorted(
            p for p in CONVERSATIONS_DIR.iterdir() if p.is_dir()
        )
    p = Path(target)
    if p.is_dir():
        return [p]
    # treat as glob relative to conversations/
    pattern = target
    if not pattern.startswith("/"):
        matches = sorted(CONVERSATIONS_DIR.glob(pattern))
    else:
        matches = sorted(Path("/").glob(pattern.lstrip("/")))
    return [m for m in matches if m.is_dir()]


def run_rows(
    rows: list[Path],
    determinism: int = 1,
    run_id: str | None = None,
    timeout_s: int = 600,
    verbose: bool = True,
    json_out: Path | None = None,
    model: str = DEFAULT_MODEL,
    runtime: str = DEFAULT_RUNTIME,
) -> tuple[int, dict[str, Any]]:
    """Drive one or more rows live, aggregate, write runs/<run-id>/aggregate.json."""
    run_id = run_id or new_run_id()
    run_dir = RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    aggregate: dict[str, Any] = {
        "run_id": run_id,
        "started_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "determinism": determinism,
        "default_model": model,
        "runtime": runtime,
        "total": 0,
        "stable_pass": 0,
        "flake": 0,
        "stable_fail": 0,
        "error": 0,
        "rows": [],
    }
    rc_overall = 0
    halted = False
    for row_dir in rows:
        try:
            result = run_row_live(
                row_dir, run_dir, determinism=determinism,
                timeout_s=timeout_s, verbose=verbose, model=model,
                runtime=runtime,
            )
        except (RowRejection, FileNotFoundError) as e:
            result = {
                "row_id": row_dir.name,
                "row_dir": str(row_dir),
                "aggregate": "error",
                "error": str(e),
                "passes": [],
            }
        aggregate["rows"].append(result)
        aggregate["total"] += 1
        agg = result.get("aggregate", "error")
        if agg == "stable-pass":
            aggregate["stable_pass"] += 1
        elif agg == "flake":
            aggregate["flake"] += 1
        elif agg == "stable-fail":
            aggregate["stable_fail"] += 1
            rc_overall = max(rc_overall, 1)
        else:
            aggregate["error"] += 1
            rc_overall = max(rc_overall, 1)
        if result.get("halt_reason") == "auth_failure":
            halted = True
            aggregate["halted"] = "auth_failure"
            break
    aggregate["completed_at"] = _dt.datetime.now(_dt.timezone.utc).isoformat()
    total = aggregate["total"] or 1
    aggregate["stable_pass_rate"] = round(aggregate["stable_pass"] / total, 4)
    (run_dir / "aggregate.json").write_text(json.dumps(aggregate, indent=2))
    if json_out:
        json_out.parent.mkdir(parents=True, exist_ok=True)
        json_out.write_text(json.dumps(aggregate, indent=2))
    if verbose:
        print(
            f"\nrun {run_id}: total={aggregate['total']} "
            f"stable_pass={aggregate['stable_pass']} flake={aggregate['flake']} "
            f"stable_fail={aggregate['stable_fail']} error={aggregate['error']} "
            f"stable_pass_rate={aggregate['stable_pass_rate']}",
            file=sys.stderr,
        )
        if halted:
            print(f"HALTED: {aggregate['halted']}", file=sys.stderr)
    return rc_overall, aggregate


# ---------------------------------------------------------------------------
# Routing evals (plan §15b P1: positives >=29/30, negatives 30/30,
# ambiguous >=13/15 with 0 unsafe)
# ---------------------------------------------------------------------------


# Empty/no-op fixture for routing probes: no plugins beyond library + helix
# methodology. We use the consumer/clean fixture if available; else a tmp dir.
def _routing_fixture() -> Path:
    """Resolve the host fixture dir to mount for routing probes."""
    candidate = FAMILY_TEST_ROOT / "consumer" / "clean"
    if candidate.is_dir():
        return candidate
    # fallback: an empty tmp dir under bench/runs/
    tmp = RUNS_DIR / "_routing_fixture"
    tmp.mkdir(parents=True, exist_ok=True)
    return tmp


def _routing_plugins() -> list[Path]:
    """Plugin set for routing probes: the canonical install at the repo root.

    The repo IS the plugin per .claude-plugin/plugin.json — one plugin
    shipping one skill (`helix`) with internal routing to product/infra/data/
    web modes. The bench loads the same install path that users get from
    the marketplace, mounted via --plugin-dir.

    Previous shape (research fork: library/ + methodology-{product,data,
    infra,web}/) is gone after the canonical-promotion refactor. If a future
    multi-plugin layout returns, this function is the only spot that needs
    updating.
    """
    repo_root = FAMILY_TEST_ROOT.parent
    if not (repo_root / ".claude-plugin" / "plugin.json").is_file():
        raise FileNotFoundError(
            f"canonical plugin manifest missing at {repo_root}/.claude-plugin/plugin.json"
        )
    return [repo_root]


def _probe_fired_skill(transcript: Transcript, skill_id: str) -> bool:
    """True iff transcript carries a Skill(skill_id) tool_use."""
    res = matcher_skill_tool_use({"skill_id": skill_id}, transcript)
    return res.verdict == "present"


# §13.6b multi-instance disambiguation banner. Two-line verbatim form:
#   Multiple helix instances declared: <name> (root: <path>), ...
#   Re-run with the explicit prefix /helix:<instance-name> or set HELIX_INSTANCE=<name>.
_MI_BANNER_ANCHORS = (
    "Multiple helix instances declared",
    "Re-run with the explicit prefix",
)
_MI_DOWNSTREAM_MUTATION_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit", "Bash"}


def _multi_instance_banner_pass(transcript: Transcript) -> bool:
    """True iff the transcript carries the §13.6b disambiguation banner AND
    does NOT execute any downstream mutation tool (Write/Edit/MultiEdit/
    NotebookEdit/Bash) after the banner is emitted.

    Used by run_routing_evals to grant PASS to helix-multi-instance rows
    where the skill correctly engaged, read the marker, detected multiple
    helix instances, and safely aborted with the banner instead of guessing.
    """
    text = transcript.assistant_text
    if not all(anchor in text for anchor in _MI_BANNER_ANCHORS):
        return False
    # Banner is present in assistant prose. Now confirm no downstream
    # mutation tool was invoked AFTER the banner appeared. We use the
    # ordered timeline so a Write/Edit/Bash that occurred BEFORE the
    # banner (unlikely but possible during marker inspection — Bash for
    # ls/grep IS a mutation tool in our enumeration) does not falsely
    # disqualify a correct safe-stop. The semantics that matter: once
    # the skill emits the banner, it must stop and not mutate the repo.
    banner_idx: int | None = None
    for idx, kind, val in transcript.timeline:
        if kind == "text" and isinstance(val, str) and all(
            anchor in val for anchor in _MI_BANNER_ANCHORS
        ):
            banner_idx = idx
            break
    if banner_idx is None:
        # Banner anchors are split across multiple text blocks. Treat the
        # first block containing EITHER anchor as the banner index — the
        # joined `assistant_text` already proved both anchors are present.
        for idx, kind, val in transcript.timeline:
            if kind == "text" and isinstance(val, str) and any(
                anchor in val for anchor in _MI_BANNER_ANCHORS
            ):
                banner_idx = idx
                break
    if banner_idx is None:
        return False
    for idx, kind, val in transcript.timeline:
        if idx <= banner_idx:
            continue
        if kind == "tool_use" and getattr(val, "name", "") in _MI_DOWNSTREAM_MUTATION_TOOLS:
            return False
    return True


def run_routing_evals(
    jsonl_paths: list[Path],
    run_id: str | None = None,
    timeout_s: int = 300,
    limit: int | None = None,
    verbose: bool = True,
    model: str = ROUTING_EVAL_MODEL,
    runtime: str = DEFAULT_RUNTIME,
) -> tuple[int, dict[str, Any]]:
    """Run routing probes against the supplied jsonl(s).

    Each line is {id, prompt, expected_skill | candidate_flows / correct_route, ...}.
    For each prompt we invoke `claude -p` once via run-probe.sh and check
    whether the expected Skill tool_use fires.

    Default model is `claude-haiku-4-5` (plan §19.1): the integer-gate
    decision is binary; cheaper model is sufficient.
    """
    run_id = run_id or new_run_id()
    run_dir = RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    fixture = _routing_fixture()
    plugins = _routing_plugins()
    results: list[dict[str, Any]] = []
    summary: dict[str, Any] = {
        "run_id": run_id,
        "started_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "files": [str(p) for p in jsonl_paths],
        "model": model,
        "runtime": runtime,
        "by_set": {},
    }
    halted = False
    for jsonl in jsonl_paths:
        set_name = jsonl.stem
        set_stats = {
            "total": 0, "expected_fire": 0, "fired": 0,
            "expected_no_fire": 0, "no_fire": 0,
            "unsafe": 0, "correct": 0,
        }
        with jsonl.open() as fh:
            for line_no, line in enumerate(fh, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if limit and set_stats["total"] >= limit:
                    break
                set_stats["total"] += 1
                rid = row.get("id", f"{set_name}-{line_no}")
                prompt = row.get("prompt", "")
                expected_skill = row.get("expected_skill")
                correct_route = row.get("correct_route")
                # Negative set: expected_skill is null -> Skill SHOULD NOT fire
                # Positive set: expected_skill = 'helix' -> Skill SHOULD fire with skill_id=helix
                # Ambiguous: correct_route names the target skill_id
                target = expected_skill if expected_skill is not None else correct_route
                evidence_file = run_dir / f"routing-{set_name}-{rid}.stream.jsonl"
                t0 = _time.monotonic()
                rc, stderr = invoke_probe(
                    fixture, plugins, prompt, evidence_file,
                    timeout_s=timeout_s, model=model, runtime=runtime,
                )
                dt = _time.monotonic() - t0
                evidence_text = evidence_file.read_text() if evidence_file.exists() else ""
                if rc != 0 and _detect_auth_failure(evidence_text + "\n" + stderr):
                    results.append({
                        "set": set_name, "id": rid, "error": "auth_failure",
                        "stderr_tail": stderr[-400:],
                    })
                    halted = True
                    break
                _log_cost_from_evidence(
                    evidence_file, row_id=f"routing-{rid}",
                    duration_s=dt, phase="bench",
                    extra_notes={"set": set_name, "probe_rc": rc, "model": model, "runtime": runtime},
                )
                try:
                    transcript = parse_runtime_transcript(evidence_file, runtime)
                except Exception as e:
                    results.append({
                        "set": set_name, "id": rid, "error": f"parse: {e}",
                    })
                    continue
                # Extract any skill ids that fired (Skill tool_use)
                fired_skills: list[str] = []
                for tu in transcript.tool_uses:
                    sid: str | None = None
                    if tu.name == "Skill":
                        sid = tu.input.get("skill_id")
                        if not sid:
                            skill = tu.input.get("skill")
                            if isinstance(skill, str):
                                sid = skill.split(":")[-1]
                    elif tu.name.startswith("Skill("):
                        sid = tu.name[len("Skill("):-1]
                    elif tu.name in ("helix", "helix-web", "helix-infra", "helix-data"):
                        sid = tu.name
                    if sid:
                        fired_skills.append(sid)
                # Codex has no Skill tool. Fall back to prose_attribution:
                # the agent's assistant text naming a known helix-* skill id
                # is the runtime-independent routing signal (plan §1.4b).
                if runtime == "codex":
                    text_lc = transcript.assistant_text.lower()
                    for sid in ("helix-web", "helix-infra", "helix-data", "helix"):
                        # name-match — checked longest-first so "helix-web"
                        # does not get masked by "helix"
                        if sid in text_lc:
                            fired_skills.append(sid)
                            break
                fired_skills = sorted(set(fired_skills))
                if runtime == "codex" and target:
                    fired_target = target in fired_skills
                else:
                    fired_target = bool(target) and _probe_fired_skill(transcript, target)
                fired_any = len(fired_skills) > 0
                record: dict[str, Any] = {
                    "set": set_name,
                    "id": rid,
                    "prompt": prompt,
                    "expected_skill": expected_skill,
                    "correct_route": correct_route,
                    "fired_skills": list(fired_skills),
                    "fired_target": fired_target,
                    "fired_any": fired_any,
                    "duration_s": round(dt, 3),
                    "probe_rc": rc,
                }
                if target is None:
                    # negative set: ANY skill fire = wrong, EXCEPT for the
                    # helix-multi-instance set where the skill is expected to
                    # engage, read the marker, and either resolve OR emit a
                    # disambiguation banner and abort. When the skill engages
                    # AND emits the §13.6b banner AND does NOT execute
                    # downstream mutation tools (Write/Edit/Bash), that is
                    # the correct safe-stop behavior and counts as PASS.
                    mi_banner_exempt = False
                    if set_name == "helix-multi-instance" and fired_any:
                        mi_banner_exempt = _multi_instance_banner_pass(
                            transcript
                        )
                        if mi_banner_exempt:
                            record["multi_instance_banner_pass"] = True
                    record["correct"] = (not fired_any) or mi_banner_exempt
                    set_stats["expected_no_fire"] += 1
                    if record["correct"]:
                        set_stats["no_fire"] += 1
                        set_stats["correct"] += 1
                else:
                    set_stats["expected_fire"] += 1
                    if fired_target:
                        set_stats["fired"] += 1
                        set_stats["correct"] += 1
                    # ambiguous: "unsafe" = fired a *wrong* skill family that
                    # is not in candidate_flows
                    cand = row.get("candidate_flows") or []
                    if cand and fired_any and not fired_target:
                        wrong_fires = [s for s in fired_skills if s not in cand]
                        if wrong_fires:
                            set_stats["unsafe"] += 1
                            record["unsafe"] = True
                    record["correct"] = fired_target
                results.append(record)
                if verbose:
                    mark = "OK" if record.get("correct") else "XX"
                    print(
                        f"[routing {mark}] {set_name}/{rid}: "
                        f"target={target} fired={fired_skills}",
                        file=sys.stderr,
                    )
        summary["by_set"][set_name] = set_stats
        if halted:
            break
    # Compute precision (positives only): correct fires / total positives
    pos_stats = summary["by_set"].get("helix-positive", {})
    precision = 0.0
    if pos_stats.get("expected_fire"):
        precision = pos_stats["fired"] / pos_stats["expected_fire"]
    summary["routing_precision"] = round(precision, 4)
    summary["completed_at"] = _dt.datetime.now(_dt.timezone.utc).isoformat()
    summary["results"] = results
    if halted:
        summary["halted"] = "auth_failure"
    # Plan gates
    gates = {
        "positives_pass": False,
        "negatives_pass": False,
        "ambiguous_pass": False,
        "unsafe_zero": True,
    }
    pos = summary["by_set"].get("helix-positive", {})
    neg = summary["by_set"].get("helix-negative", {})
    amb = summary["by_set"].get("helix-ambiguous", {})
    gates["positives_pass"] = pos.get("correct", 0) >= 29 and pos.get("expected_fire", 0) >= 30
    gates["negatives_pass"] = neg.get("correct", 0) == neg.get("expected_no_fire", 0) and neg.get("expected_no_fire", 0) >= 30
    gates["ambiguous_pass"] = amb.get("correct", 0) >= 13
    gates["unsafe_zero"] = amb.get("unsafe", 0) == 0
    summary["gates"] = gates
    summary["all_gates_pass"] = all(gates.values())
    (run_dir / "routing-eval-results.json").write_text(json.dumps(summary, indent=2))
    if verbose:
        print(
            f"\nrouting-evals {run_id}: precision={summary['routing_precision']}; "
            f"gates={gates}",
            file=sys.stderr,
        )
    rc_overall = 0 if (summary["all_gates_pass"] and not halted) else 1
    return rc_overall, summary


# ---------------------------------------------------------------------------
# Ratchet integration
# ---------------------------------------------------------------------------


def update_ratchets(
    stable_pass_rate: float | None = None,
    routing_precision: float | None = None,
    cost_per_run: float | None = None,
    last_attempt: dict[str, Any] | None = None,
    ratchets_path: Path = RATCHETS_PATH,
    verbose: bool = True,
) -> tuple[int, dict[str, Any]]:
    """Write computed metrics back into ratchets.json with regression check.

    Returns (exit_code, alerts). exit 0 = no >5% regression vs baseline OR
    baseline was null (first run; we seed it). exit 1 = regression alert
    fired on any tracked stream.
    """
    if not ratchets_path.exists():
        raise FileNotFoundError(f"ratchets.json missing at {ratchets_path}")
    doc = json.loads(ratchets_path.read_text())
    alerts: list[str] = []
    streams = doc.get("ratchets") or {}

    def apply(stream_name: str, observed: float, tolerance_key: str = "tolerance_pp", direction: str = "higher_is_better") -> None:
        s = streams.get(stream_name)
        if not s:
            return
        baseline = s.get("baseline")
        tol = s.get(tolerance_key)
        s["last_observed"] = observed
        s["last_observed_at"] = _dt.datetime.now(_dt.timezone.utc).isoformat()
        if baseline is None:
            # seed
            s["baseline"] = observed
            s["seeded_at"] = s["last_observed_at"]
            if verbose:
                print(f"  ratchet {stream_name}: seeded baseline = {observed}")
            return
        if tol is None:
            return
        if direction == "higher_is_better":
            # regression = observed drops by more than tol points/percent
            if tolerance_key == "tolerance_pp":
                regression = (baseline - observed) * 100 > tol
            else:
                regression = (baseline - observed) / max(baseline, 1e-9) * 100 > tol
            if regression:
                alerts.append(
                    f"{stream_name}: REGRESSION baseline={baseline} observed={observed} "
                    f"tolerance={tol} ({tolerance_key})"
                )
        else:  # lower_is_better
            if tolerance_key == "tolerance_pp":
                regression = (observed - baseline) * 100 > tol
            else:
                regression = (observed - baseline) / max(baseline, 1e-9) * 100 > tol
            if regression:
                alerts.append(
                    f"{stream_name}: REGRESSION (higher cost) baseline={baseline} "
                    f"observed={observed} tolerance={tol} ({tolerance_key})"
                )

    if stable_pass_rate is not None:
        apply("stable_pass_rate", stable_pass_rate, "tolerance_pp", "higher_is_better")
    if routing_precision is not None:
        apply("routing_precision", routing_precision, "tolerance_pp", "higher_is_better")
    if cost_per_run is not None:
        apply("cost_per_run", cost_per_run, "tolerance_pct", "lower_is_better")

    doc["updated_at"] = _dt.datetime.now(_dt.timezone.utc).isoformat()
    if last_attempt is not None:
        doc["last_attempt"] = last_attempt
    if alerts:
        doc["alerts"] = alerts
    else:
        doc.pop("alerts", None)
    ratchets_path.write_text(json.dumps(doc, indent=2) + "\n")
    if verbose:
        for a in alerts:
            print(f"ALERT: {a}", file=sys.stderr)
        if not alerts:
            print(f"ratchets: no regressions (updated {ratchets_path.name})", file=sys.stderr)
    return (1 if alerts else 0), {"alerts": alerts, "ratchets_path": str(ratchets_path)}


# ---------------------------------------------------------------------------
# Layer 2 — semantic judge LLM (plan §5.2, §6.7, §18.2)
# ---------------------------------------------------------------------------


@dataclass
class JudgeResult:
    """Verdict returned by the Layer 2 judge LLM.

    matches: assertion verdict (true = assertion holds; false = violated)
    confidence: 0..1; >= 0.8 = stable, 0.5..0.8 = borderline (re-judge), < 0.5
        = genuinely ambiguous
    rationale: 1-2 sentence cited justification
    raw: raw judge stdout (kept for failure-dump)
    """

    matches: bool
    confidence: float
    rationale: str
    raw: str = ""


JUDGE_BACKEND_DEFAULT = os.environ.get("HELIX_BENCH_JUDGE_BACKEND", "claude")
JUDGE_MODEL_DEFAULT = os.environ.get("HELIX_BENCH_JUDGE_MODEL", "haiku")


def _build_judge_input(intent: str, polarity: str, actual_prose: str) -> str:
    """Format the JSON payload the rubric expects."""
    return json.dumps(
        {
            "polarity": polarity,
            "intent": intent,
            "actual_prose": actual_prose,
        },
        ensure_ascii=False,
    )


def _parse_judge_output(raw: str) -> JudgeResult:
    """Extract {matches, confidence, rationale} JSON from judge stdout.

    Tolerant of fenced output or trailing prose; pulls the first JSON object
    whose keys are a superset of {matches, confidence, rationale}.
    """
    # Strip common fence shapes.
    text = raw.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fenced:
        text = fenced.group(1)
    # Find first plausible JSON object.
    candidates = re.findall(r"\{[^{}]*\}", text, re.DOTALL)
    # also try the whole text in case it's a single object containing braces
    candidates = [text] + candidates
    for cand in candidates:
        try:
            obj = json.loads(cand)
        except json.JSONDecodeError:
            continue
        if not isinstance(obj, dict):
            continue
        if {"matches", "confidence", "rationale"}.issubset(obj.keys()):
            return JudgeResult(
                matches=bool(obj["matches"]),
                confidence=float(obj["confidence"]),
                rationale=str(obj["rationale"]),
                raw=raw,
            )
    raise ValueError(f"could not parse judge output: {raw[:400]}")


def invoke_judge(
    intent: str,
    polarity: str,
    actual_prose: str,
    backend: str = JUDGE_BACKEND_DEFAULT,
    model: str = JUDGE_MODEL_DEFAULT,
    timeout_s: int = 120,
    rubric_path: Path = JUDGE_RUBRIC,
) -> JudgeResult:
    """Dispatch one judge call. Backend = 'claude' | 'codex' | 'stub'.

    `stub` is a deterministic offline judge used by self-test: it does a case-
    insensitive substring/keyword match between intent keywords and prose,
    flipped by polarity. It never calls an LLM and is suitable only for unit
    tests / smoke runs.
    """
    if backend == "stub":
        return _stub_judge(intent, polarity, actual_prose)
    if not rubric_path.exists():
        raise FileNotFoundError(f"missing judge rubric at {rubric_path}")
    rubric = rubric_path.read_text()
    payload = _build_judge_input(intent, polarity, actual_prose)
    if backend == "claude":
        return _invoke_claude_judge(rubric, payload, model=model, timeout_s=timeout_s)
    if backend == "codex":
        return _invoke_codex_judge(rubric, payload, timeout_s=timeout_s)
    raise ValueError(f"unknown judge backend: {backend}")


def _invoke_claude_judge(
    rubric: str, payload: str, model: str, timeout_s: int
) -> JudgeResult:
    import subprocess

    # Use the `claude` CLI in headless mode. Temperature is fixed in CC.
    # We compose: system = rubric; user = payload JSON; output = text.
    cmd = [
        "claude",
        "-p",
        payload,
        "--model",
        model,
        "--system-prompt",
        rubric,
        "--output-format",
        "text",
    ]
    proc = subprocess.run(
        cmd, capture_output=True, text=True, timeout=timeout_s, check=False
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"claude judge exited {proc.returncode}: {proc.stderr[:400]}"
        )
    return _parse_judge_output(proc.stdout)


def _invoke_codex_judge(rubric: str, payload: str, timeout_s: int) -> JudgeResult:
    import subprocess

    # codex exec takes a single prompt; we concatenate rubric + payload with a
    # boundary so the judge knows which is which.
    prompt = (
        rubric
        + "\n\n---\n"
        + "INPUT (judge this):\n"
        + payload
        + "\n\nReturn only the JSON object.\n"
    )
    cmd = ["codex", "exec", "--skip-git-repo-check", prompt]
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout_s,
        check=False,
        stdin=subprocess.DEVNULL,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"codex judge exited {proc.returncode}: {proc.stderr[:400]}"
        )
    return _parse_judge_output(proc.stdout)


def _stub_judge(intent: str, polarity: str, actual_prose: str) -> JudgeResult:
    """Deterministic offline judge for self-test.

    Builds a tiny keyword set from `intent` (lowercased nouns/verbs >=4
    chars) and asks: does the prose contain at least one keyword AND not
    contain an obvious negation of it. This is a sanity-grade signal only;
    real judgments require the LLM path.
    """
    stop = {
        "the", "and", "for", "with", "that", "this", "from", "into", "names",
        "name", "active", "first", "before", "after", "would", "could",
        "should", "offers", "offer", "mentions", "mention", "asks", "ask",
        "explicit", "claims", "claim", "marker", "methodology",
    }
    keywords = [
        w for w in re.findall(r"[a-zA-Z][a-zA-Z\-]{3,}", intent.lower())
        if w not in stop
    ]
    prose_l = actual_prose.lower()
    hits = [k for k in keywords if k in prose_l]
    has_meaning = len(hits) >= 1
    # crude negation: "won't" "not " "no need" "don't" "instead of"
    negated = any(
        n in prose_l for n in ["won't", "won’t", "don't", "don’t", "no need",
                              "not now", "instead of", "skip", "cannot",
                              "can't", "can’t"]
    )
    present = has_meaning and not negated
    if polarity == "must_NOT_include":
        matches = not present
    else:
        matches = present
    return JudgeResult(
        matches=matches,
        confidence=0.85 if has_meaning else 0.6,
        rationale=f"stub-judge: keywords matched={hits}, negated={negated}",
        raw="<stub>",
    )


def load_semantic_assertions(row_dir: Path) -> list[dict[str, Any]]:
    """Read a row's Layer 2 assertions.

    Looks for `semantic.yml` in the row dir (preferred — keeps L1 file
    untouched), falling back to a `semantic:` block in `expected.yml`.
    Returns a list of {polarity, intent} dicts.
    """
    out: list[dict[str, Any]] = []
    semantic_path = row_dir / "semantic.yml"
    blob: dict[str, Any] | None = None
    if semantic_path.exists():
        blob = yaml.safe_load(semantic_path.read_text()) or {}
    else:
        expected = row_dir / "expected.yml"
        if expected.exists():
            blob = (yaml.safe_load(expected.read_text()) or {}).get("semantic")
    if not blob:
        return out
    for item in blob.get("prose_must_include", []) or []:
        out.append({"polarity": "must_include", "intent": item.get("intent") or item})
    for item in blob.get("prose_must_NOT_include", []) or []:
        out.append(
            {"polarity": "must_NOT_include", "intent": item.get("intent") or item}
        )
    return out


def extract_actual_prose(transcript_or_text: str | Transcript) -> str:
    if isinstance(transcript_or_text, Transcript):
        return transcript_or_text.assistant_text
    # Try to parse as transcript JSONL first; if that fails, treat as raw text.
    try:
        t = Transcript.parse(transcript_or_text)
        return t.assistant_text or transcript_or_text
    except Exception:
        return transcript_or_text


def judge_with_rejudge(
    intent: str,
    polarity: str,
    actual_prose: str,
    backend: str,
    model: str,
    borderline_low: float = 0.5,
    borderline_high: float = 0.8,
    max_rejudges: int = 2,
) -> dict[str, Any]:
    """Run the judge once; re-judge up to `max_rejudges` more times if the
    confidence falls in (borderline_low, borderline_high). Majority vote on
    `matches` wins; the final confidence is the mean over runs.
    """
    runs: list[JudgeResult] = [
        invoke_judge(intent, polarity, actual_prose, backend=backend, model=model)
    ]
    if borderline_low < runs[0].confidence < borderline_high:
        for _ in range(max_rejudges):
            runs.append(
                invoke_judge(
                    intent, polarity, actual_prose, backend=backend, model=model
                )
            )
    matches_votes = sum(1 for r in runs if r.matches)
    matches_final = matches_votes * 2 >= len(runs)
    mean_conf = sum(r.confidence for r in runs) / len(runs)
    return {
        "matches": matches_final,
        "confidence": mean_conf,
        "rationale": runs[0].rationale,
        "n_runs": len(runs),
        "votes_true": matches_votes,
        "per_run": [
            {"matches": r.matches, "confidence": r.confidence, "rationale": r.rationale}
            for r in runs
        ],
    }


def run_layer2(
    row_dir: Path,
    transcript_path: Path | None = None,
    backend: str = JUDGE_BACKEND_DEFAULT,
    model: str = JUDGE_MODEL_DEFAULT,
    verbose: bool = True,
) -> tuple[int, dict[str, Any]]:
    """Apply Layer 2 to one row.

    Requires either:
      - row_dir / 'transcript.jsonl' (default), OR
      - --transcript pointing at a stream-json file

    For Phase 7 with rows that lack a recorded transcript, we look for
    `row_dir / 'sample-prose.md'` which holds a representative prose sample
    (so the judge can be exercised without invoking CC).
    """
    semantic = load_semantic_assertions(row_dir)
    if not semantic:
        if verbose:
            print(
                f"[layer2] {row_dir.name}: no semantic.yml, skipping",
                file=sys.stderr,
            )
        return 0, {"row": str(row_dir), "skipped": True}
    if transcript_path is None:
        for cand in ("transcript.jsonl", "sample-transcript.jsonl", "sample-prose.md"):
            p = row_dir / cand
            if p.exists():
                transcript_path = p
                break
    if transcript_path is None or not transcript_path.exists():
        raise FileNotFoundError(
            f"no transcript/prose under {row_dir} (looked for transcript.jsonl, "
            "sample-transcript.jsonl, sample-prose.md)"
        )
    raw = transcript_path.read_text()
    if transcript_path.suffix == ".jsonl":
        actual_prose = extract_actual_prose(raw)
    else:
        actual_prose = raw
    per_assertion: list[dict[str, Any]] = []
    all_pass = True
    for sem in semantic:
        result = judge_with_rejudge(
            sem["intent"], sem["polarity"], actual_prose, backend=backend, model=model
        )
        per_assertion.append(
            {
                "intent": sem["intent"],
                "polarity": sem["polarity"],
                **result,
                "verdict": "pass" if result["matches"] else "fail",
            }
        )
        if not result["matches"]:
            all_pass = False
    out = {
        "row": str(row_dir),
        "transcript": str(transcript_path),
        "backend": backend,
        "model": model,
        "assertions": per_assertion,
        "all_pass": all_pass,
    }
    if verbose:
        print(json.dumps(out, indent=2))
    return 0 if all_pass else 1, out


def run_calibration(
    backend: str = JUDGE_BACKEND_DEFAULT,
    model: str = JUDGE_MODEL_DEFAULT,
    calibration_path: Path = JUDGE_CALIBRATION,
    verbose: bool = True,
) -> tuple[int, dict[str, Any]]:
    """Run the calibration set and report judge↔human agreement.

    Plan §18.2 contract: judge must agree with human verdict on >= 18/20
    (90%). Disagreement > 2 halts judge-LLM use until rubric retuned.
    """
    data = yaml.safe_load(calibration_path.read_text()) or {}
    rows = data.get("calibration", [])
    if not rows:
        raise RuntimeError(f"empty calibration set: {calibration_path}")
    per_row: list[dict[str, Any]] = []
    agree = 0
    for row in rows:
        rid = row.get("id", "?")
        intent = row["intent"]
        polarity = row["polarity"]
        prose = row["actual_prose"]
        human = bool(row["human_verdict"])
        try:
            judged = invoke_judge(
                intent, polarity, prose, backend=backend, model=model
            )
            agreed = judged.matches == human
            agree += int(agreed)
            per_row.append(
                {
                    "id": rid,
                    "polarity": polarity,
                    "human": human,
                    "judge": judged.matches,
                    "confidence": judged.confidence,
                    "agreed": agreed,
                    "rationale": judged.rationale,
                }
            )
            if verbose:
                mark = "OK" if agreed else "XX"
                print(
                    f"[calib {mark}] {rid} human={human} judge={judged.matches} "
                    f"conf={judged.confidence:.2f}"
                )
        except Exception as e:
            per_row.append({"id": rid, "error": str(e), "agreed": False})
            if verbose:
                print(f"[calib ER] {rid} error: {e}", file=sys.stderr)
    n = len(rows)
    pass_floor = 18  # plan §18.2 hard gate at n=20
    summary = {
        "backend": backend,
        "model": model,
        "n": n,
        "agreed": agree,
        "agreement_rate": agree / n if n else 0,
        "pass_floor": pass_floor,
        "passed": agree >= pass_floor,
        "rows": per_row,
    }
    if verbose:
        print(
            f"\nCalibration: {agree}/{n} agreed "
            f"({summary['agreement_rate']:.0%}); "
            f"{'PASS' if summary['passed'] else 'FAIL'} (floor {pass_floor})"
        )
    JUDGE_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = JUDGE_RESULTS_DIR / "calibration-latest.json"
    out_path.write_text(json.dumps(summary, indent=2))
    return (0 if summary["passed"] else 1), summary


# ---------------------------------------------------------------------------
# Layer 3 — next-action envelope (plan §1.4, §8)
# ---------------------------------------------------------------------------
#
# Layer 3 wires a JSON envelope contract via a system-prompt injection. The
# anti-contamination rule (§1.4 layer-ordering): each Layer-3 row runs
# TWICE — once without the envelope prompt (the no-envelope pass; counts
# toward Layer 1 + Layer 2 verdicts), once with it (the envelope pass;
# counts toward Layer 3 verdict). Layer 1 outcomes MUST be identical
# across the two passes; if they diverge, the system prompt has changed
# the agent's behaviour and the envelope contract is contaminating the
# floor measurement.
#
# At P8 we do NOT invoke `claude` end-to-end (that lands when the full row
# runner ships in P11). What this module DOES at P8:
#   1) load + validate a row's envelope.yml (Layer 3 spec)
#   2) grade a stream-json transcript against the envelope-aware matcher
#   3) compare per-row Layer 1 verdicts between (no-envelope-transcript,
#      envelope-transcript) and assert verdict equality
# The grading harness reads sample transcripts under the row dir:
#   - transcript.no-envelope.jsonl  (or sample-transcript.jsonl)
#   - transcript.envelope.jsonl     (carries the fenced ```json block)


def load_envelope_spec(row_dir: Path) -> dict[str, Any] | None:
    """Read the row's `envelope.yml` Layer 3 spec.

    Shape:
        envelope:
          assertion_id: next_action_envelope
          schema_path: judge/next-action-envelope.schema.json
          offered_requires:
            - draft_artifact:product-vision
          not_offered_forbids:
            - draft_artifact:prd
        notes: |
          why this row asserts Layer 3

    Returns the inner mapping (with `offered_requires` and `not_offered_forbids`
    coerced to lists), or None if the row does not declare Layer 3.
    """
    envelope_path = row_dir / "envelope.yml"
    if not envelope_path.exists():
        return None
    doc = yaml.safe_load(envelope_path.read_text()) or {}
    env = doc.get("envelope")
    if not isinstance(env, dict):
        raise RowRejection(
            "T043", f"{envelope_path}: missing top-level `envelope:` mapping"
        )
    aid = env.get("assertion_id")
    if aid != "next_action_envelope":
        raise RowRejection(
            "T041",
            f"{envelope_path}: envelope.assertion_id must be 'next_action_envelope', got {aid!r}",
        )
    schema_path = env.get("schema_path") or "judge/next-action-envelope.schema.json"
    out = {
        "assertion_id": aid,
        "envelope_schema_path": schema_path,
        "offered_requires": list(env.get("offered_requires") or []),
        "not_offered_forbids": list(env.get("not_offered_forbids") or []),
        "expected_in_envelope_pass": env.get("expected_in_envelope_pass", "present"),
    }
    if not out["offered_requires"]:
        raise RowRejection(
            "T042",
            f"{envelope_path}: envelope.offered_requires must list >=1 descriptor",
        )
    return out


def grade_envelope_pass(
    row_dir: Path,
    envelope_transcript: Path,
) -> tuple[int, dict[str, Any]]:
    """Run the next_action_envelope matcher against an envelope-pass transcript.

    Returns (exit_code, verdict_dict). exit 0 iff the verdict matches the
    row's `expected_in_envelope_pass` (default 'present').
    """
    spec = load_envelope_spec(row_dir)
    if spec is None:
        return 0, {"row": row_dir.name, "skipped": "no envelope.yml"}
    if not envelope_transcript.exists():
        raise FileNotFoundError(f"envelope transcript missing: {envelope_transcript}")
    t = Transcript.parse(envelope_transcript)
    params = {
        "envelope_schema_path": spec["envelope_schema_path"],
        "offered_requires": spec["offered_requires"],
        "not_offered_forbids": spec["not_offered_forbids"],
    }
    result = matcher_next_action_envelope(params, t)
    expected = spec["expected_in_envelope_pass"]
    ok = result.verdict == expected
    return (0 if ok else 1), {
        "row": row_dir.name,
        "transcript": str(envelope_transcript),
        "expected_verdict": expected,
        "actual_verdict": result.verdict,
        "details": result.details,
        "spec": spec,
    }


def check_no_contamination(
    row_dir: Path,
    no_envelope_transcript: Path,
    envelope_transcript: Path,
) -> tuple[int, dict[str, Any]]:
    """Verify Layer 1 verdicts are identical across no-envelope/envelope passes.

    Per plan §1.4 layer-ordering: the envelope system prompt MUST NOT change
    the agent's Layer 1 behaviour. We grade the row's discriminator matcher
    against both transcripts; verdicts must be equal.
    """
    norm = validate_row(row_dir)
    aid = norm["assertion_id"]
    matcher = MATCHER_REGISTRY[aid]
    params = norm["params"]
    if not no_envelope_transcript.exists():
        raise FileNotFoundError(f"no-envelope transcript missing: {no_envelope_transcript}")
    if not envelope_transcript.exists():
        raise FileNotFoundError(f"envelope transcript missing: {envelope_transcript}")
    t_no = Transcript.parse(no_envelope_transcript)
    t_yes = Transcript.parse(envelope_transcript)
    r_no = matcher(params, t_no)
    r_yes = matcher(params, t_yes)
    same = r_no.verdict == r_yes.verdict
    summary = {
        "row": row_dir.name,
        "assertion_id": aid,
        "no_envelope_verdict": r_no.verdict,
        "envelope_verdict": r_yes.verdict,
        "identical": same,
        "no_envelope_details": r_no.details,
        "envelope_details": r_yes.details,
    }
    return (0 if same else 1), summary


def _row_transcripts(row_dir: Path) -> tuple[Path, Path]:
    """Resolve a row's no-envelope + envelope transcript paths.

    Preference order:
      no-envelope: transcript.no-envelope.jsonl, sample-transcript.jsonl, transcript.jsonl
      envelope:    transcript.envelope.jsonl
    Raises FileNotFoundError if either is missing.
    """
    no_env_candidates = [
        row_dir / "transcript.no-envelope.jsonl",
        row_dir / "sample-transcript.jsonl",
        row_dir / "transcript.jsonl",
    ]
    env_path = row_dir / "transcript.envelope.jsonl"
    no_env = next((p for p in no_env_candidates if p.exists()), None)
    if no_env is None:
        raise FileNotFoundError(
            f"{row_dir.name}: no no-envelope transcript "
            f"(looked for transcript.no-envelope.jsonl, sample-transcript.jsonl, transcript.jsonl)"
        )
    if not env_path.exists():
        raise FileNotFoundError(
            f"{row_dir.name}: missing transcript.envelope.jsonl"
        )
    return no_env, env_path


def run_envelope_pass(
    row_dir: Path,
    no_envelope_transcript: Path | None = None,
    envelope_transcript: Path | None = None,
    verbose: bool = True,
) -> tuple[int, dict[str, Any]]:
    """Apply Layer 3 to one row + verify non-contamination of Layer 1.

    The row MUST declare `envelope.yml`. The runner:
      1) grades the Layer 1 matcher on the no-envelope transcript
      2) grades the Layer 1 matcher on the envelope transcript
      3) asserts (1) and (2) are identical (anti-contamination invariant)
      4) grades the next_action_envelope matcher on the envelope transcript
    """
    spec = load_envelope_spec(row_dir)
    if spec is None:
        if verbose:
            print(
                f"[layer3] {row_dir.name}: no envelope.yml, skipping",
                file=sys.stderr,
            )
        return 0, {"row": row_dir.name, "skipped": True}
    if no_envelope_transcript is None or envelope_transcript is None:
        ne, en = _row_transcripts(row_dir)
        no_envelope_transcript = no_envelope_transcript or ne
        envelope_transcript = envelope_transcript or en
    rc_contam, contam = check_no_contamination(
        row_dir, no_envelope_transcript, envelope_transcript
    )
    rc_l3, l3 = grade_envelope_pass(row_dir, envelope_transcript)
    rc = max(rc_contam, rc_l3)
    out = {
        "row": row_dir.name,
        "row_dir": str(row_dir),
        "spec": spec,
        "non_contamination": contam,
        "layer3": l3,
        "pass": rc == 0,
    }
    if verbose:
        mark = "PASS" if rc == 0 else "FAIL"
        print(
            f"[layer3 {mark}] {row_dir.name}: L1-identical={contam['identical']} "
            f"L3-verdict={l3.get('actual_verdict')} (expected={l3.get('expected_verdict')})"
        )
        if not contam["identical"]:
            print(
                f"  CONTAMINATION: no-envelope={contam['no_envelope_verdict']} "
                f"envelope={contam['envelope_verdict']}",
                file=sys.stderr,
            )
    ENVELOPE_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    (ENVELOPE_RESULTS_DIR / f"{row_dir.name}.json").write_text(json.dumps(out, indent=2))
    return rc, out


def run_envelope_pass_all(
    rows: Iterable[Path], verbose: bool = True
) -> tuple[int, dict[str, Any]]:
    """Apply Layer 3 + non-contamination check across multiple rows.

    The aggregate verdict (plan §8 gate): every row's Layer 1 verdict MUST
    be identical across the two passes; every Layer 3 verdict MUST match
    the row's `expected_in_envelope_pass`.
    """
    summary: dict[str, Any] = {
        "total": 0,
        "pass": 0,
        "fail": [],
        "contamination_failures": [],
        "rows": [],
    }
    rc = 0
    for row_dir in rows:
        spec = load_envelope_spec(row_dir)
        if spec is None:
            continue
        summary["total"] += 1
        try:
            row_rc, out = run_envelope_pass(row_dir, verbose=verbose)
        except (FileNotFoundError, RowRejection) as e:
            summary["fail"].append({"row": row_dir.name, "error": str(e)})
            rc = max(rc, 1)
            continue
        summary["rows"].append(out)
        if row_rc == 0:
            summary["pass"] += 1
        else:
            summary["fail"].append({"row": row_dir.name, "summary": out})
            if not out["non_contamination"]["identical"]:
                summary["contamination_failures"].append(row_dir.name)
            rc = max(rc, 1)
    if verbose:
        print(
            f"envelope-pass: {summary['pass']}/{summary['total']} rows pass; "
            f"contamination_failures={summary['contamination_failures']}"
        )
    return rc, summary


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

    p_run = sub.add_parser("run", help="run row(s) live via Docker harness")
    p_run.add_argument("row_dir", type=str, nargs="?", default=None,
                       help="row dir or glob under conversations/")
    p_run.add_argument("--all", action="store_true",
                       help="run every row under conversations/")
    p_run.add_argument("--determinism", type=int, default=1)
    p_run.add_argument("--json-out", type=Path, default=None,
                       help="write aggregate.json copy to this path")
    p_run.add_argument("--timeout", type=int, default=600,
                       help="per-row probe timeout in seconds")
    p_run.add_argument("--run-id", default=None,
                       help="override the generated run id")
    p_run.add_argument("--validate-only", action="store_true",
                       help="legacy Phase 0a behaviour — validate only, no live CC")
    p_run.add_argument("--model", default=DEFAULT_MODEL,
                       help=f"claude model id forwarded to `claude -p --model` "
                            f"(default: {DEFAULT_MODEL}); per-row override via "
                            "`model:` in expected.yml takes precedence")
    p_run.add_argument("--runtime", default=DEFAULT_RUNTIME,
                       choices=list(SUPPORTED_RUNTIMES),
                       help=f"probe runtime (default: {DEFAULT_RUNTIME}). "
                            "claude → Docker harness + stream-json; codex → "
                            "on-host `codex exec --json`; opencode not "
                            "implemented")
    p_run.add_argument(
        "--layer",
        type=int,
        default=1,
        choices=[1, 2],
        help="layer to grade (1=structural, 2=semantic judge LLM)",
    )
    p_run.add_argument(
        "--transcript",
        type=Path,
        default=None,
        help="stream-json transcript path (Layer 2; defaults to row transcript.jsonl)",
    )
    p_run.add_argument(
        "--judge-backend",
        default=JUDGE_BACKEND_DEFAULT,
        choices=["claude", "codex", "stub"],
        help="Layer 2 judge backend (env HELIX_BENCH_JUDGE_BACKEND)",
    )
    p_run.add_argument(
        "--judge-model",
        default=JUDGE_MODEL_DEFAULT,
        help="Layer 2 judge model id",
    )

    p_layer2 = sub.add_parser(
        "layer2", help="grade Layer 2 (semantic) for a row given a transcript"
    )
    p_layer2.add_argument("row_dir", type=Path)
    p_layer2.add_argument("--transcript", type=Path, default=None)
    p_layer2.add_argument("--judge-backend", default=JUDGE_BACKEND_DEFAULT,
                          choices=["claude", "codex", "stub"])
    p_layer2.add_argument("--judge-model", default=JUDGE_MODEL_DEFAULT)

    p_calib = sub.add_parser(
        "calibrate", help="run judge calibration set (plan §18.2)"
    )
    p_calib.add_argument("--judge-backend", default=JUDGE_BACKEND_DEFAULT,
                         choices=["claude", "codex", "stub"])
    p_calib.add_argument("--judge-model", default=JUDGE_MODEL_DEFAULT)
    p_calib.add_argument(
        "--calibration-set", type=Path, default=JUDGE_CALIBRATION,
        help="path to calibration YAML",
    )

    p_env = sub.add_parser(
        "envelope-pass",
        help="grade Layer 3 next-action envelope + verify Layer 1 non-contamination (plan §1.4 §8)",
    )
    p_env.add_argument(
        "row_dir",
        type=Path,
        nargs="+",
        help="one or more row dirs; each must declare envelope.yml",
    )
    p_env.add_argument(
        "--no-envelope-transcript",
        type=Path,
        default=None,
        help="path to no-envelope-pass stream-json (overrides row default)",
    )
    p_env.add_argument(
        "--envelope-transcript",
        type=Path,
        default=None,
        help="path to envelope-pass stream-json (overrides row default)",
    )

    p_route = sub.add_parser(
        "routing-evals",
        help="run routing-eval prompts and grade Skill(helix) fires",
    )
    p_route.add_argument(
        "--jsonl",
        type=Path,
        action="append",
        default=None,
        help="path to a routing-evals jsonl file (repeatable; default = all 4 sets)",
    )
    p_route.add_argument("--run-id", default=None)
    p_route.add_argument("--timeout", type=int, default=300)
    p_route.add_argument("--limit", type=int, default=None,
                         help="cap rows per jsonl (smoke / fast-path)")
    p_route.add_argument("--model", default=ROUTING_EVAL_MODEL,
                         help=f"claude model id (default: {ROUTING_EVAL_MODEL}, "
                              "cheaper Haiku — routing is a binary gate)")
    p_route.add_argument("--runtime", default=DEFAULT_RUNTIME,
                         choices=list(SUPPORTED_RUNTIMES),
                         help=f"probe runtime (default: {DEFAULT_RUNTIME})")

    p_ratchet = sub.add_parser(
        "update-ratchets",
        help="write computed metrics back to ratchets.json (regression-aware)",
    )
    p_ratchet.add_argument("--stable-pass-rate", type=float, default=None)
    p_ratchet.add_argument("--routing-precision", type=float, default=None)
    p_ratchet.add_argument("--cost-per-run", type=float, default=None)

    args = parser.parse_args(argv)
    if args.version:
        print(f"helix_bench {VERSION}")
        return 0
    if args.cmd is None:
        parser.print_help()
        return 2

    if args.cmd == "self-test":
        code, _ = run_phase0b_self_test(verbose=True)
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
        if args.layer == 2:
            code, _ = run_layer2(
                Path(args.row_dir),
                transcript_path=args.transcript,
                backend=args.judge_backend,
                model=args.judge_model,
            )
            return code
        if args.validate_only:
            if not args.row_dir:
                print("--validate-only requires a row_dir", file=sys.stderr)
                return 2
            return run_row(Path(args.row_dir), determinism=args.determinism)
        # Live mode (Phase 1+)
        if args.all:
            rows = _discover_conversation_rows(None)
        else:
            if not args.row_dir:
                print("run requires <row_dir> or --all", file=sys.stderr)
                return 2
            rows = _discover_conversation_rows(args.row_dir)
            if not rows:
                print(f"no rows matched '{args.row_dir}'", file=sys.stderr)
                return 2
        # Same fallback as routing: codex API rejects claude model ids.
        eff_model = args.model
        if args.runtime == "codex" and eff_model == DEFAULT_MODEL:
            eff_model = ""
        rc, agg = run_rows(
            rows,
            determinism=args.determinism,
            run_id=args.run_id,
            timeout_s=args.timeout,
            json_out=args.json_out,
            model=eff_model,
            runtime=args.runtime,
        )
        if args.all:
            update_ratchets(stable_pass_rate=agg.get("stable_pass_rate"))
        return rc
    if args.cmd == "layer2":
        code, _ = run_layer2(
            args.row_dir,
            transcript_path=args.transcript,
            backend=args.judge_backend,
            model=args.judge_model,
        )
        return code
    if args.cmd == "calibrate":
        code, _ = run_calibration(
            backend=args.judge_backend,
            model=args.judge_model,
            calibration_path=args.calibration_set,
        )
        return code
    if args.cmd == "routing-evals":
        paths = list(args.jsonl) if args.jsonl else sorted(ROUTING_EVALS_DIR.glob("*.jsonl"))
        if not paths:
            print(f"no routing-eval jsonl files found", file=sys.stderr)
            return 2
        # When --runtime codex and --model wasn't explicitly overridden away
        # from the claude default, fall back to "" so the codex probe uses
        # the codex CLI's configured default (claude model ids 400 on the
        # codex API).
        eff_model = args.model
        if args.runtime == "codex" and eff_model == ROUTING_EVAL_MODEL:
            eff_model = ""
        rc, summary = run_routing_evals(
            paths, run_id=args.run_id, timeout_s=args.timeout,
            limit=args.limit, model=eff_model, runtime=args.runtime,
        )
        update_ratchets(routing_precision=summary.get("routing_precision"))
        return rc
    if args.cmd == "update-ratchets":
        rc, _ = update_ratchets(
            stable_pass_rate=args.stable_pass_rate,
            routing_precision=args.routing_precision,
            cost_per_run=args.cost_per_run,
        )
        return rc
    if args.cmd == "envelope-pass":
        if len(args.row_dir) == 1 and (
            args.no_envelope_transcript or args.envelope_transcript
        ):
            code, _ = run_envelope_pass(
                args.row_dir[0],
                no_envelope_transcript=args.no_envelope_transcript,
                envelope_transcript=args.envelope_transcript,
            )
            return code
        code, _ = run_envelope_pass_all(args.row_dir)
        return code
    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
