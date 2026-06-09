#!/usr/bin/env python3
"""Stdlib-only stream-json parser + assertion helpers for family-test probes.

Claude Code's `--output-format stream-json` emits one JSON object per line.
Common event shapes (best-effort — schema is not formally pinned):

    {"type": "system", "subtype": "init", ...}
    {"type": "assistant", "message": {"content": [
        {"type": "text", "text": "..."},
        {"type": "tool_use", "name": "Read", "input": {"file_path": "..."}},
        {"type": "tool_use", "name": "Skill", "input": {"skill": "helix"}}
    ]}}
    {"type": "user", "message": {"content": [{"type": "tool_result", ...}]}}
    {"type": "result", "subtype": "success", "result": "...final text..."}

Read once via `events = load_events(path)`, then pass to assertions.

Functions:
    load_events(path) -> list[dict]
    iter_tool_uses(events) -> Iterator[(name, input_dict)]
    assert_skill_activated(events, skill_name) -> bool
    assert_no_writes(events) -> bool
    assert_first_relevant_read(events, path_pattern) -> bool
    extract_prose(events) -> str
    parse_json_response(events) -> dict | None
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Iterable, Iterator


WRITE_TOOLS = {"Write", "Edit", "NotebookEdit", "MultiEdit"}
READ_TOOLS = {"Read", "Glob", "Grep"}


def load_events(path: str | Path) -> list[dict]:
    """Load stream-json events from a file. Skips blank lines and JSON errors."""
    events: list[dict] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return events


def _iter_content_blocks(events: Iterable[dict]) -> Iterator[dict]:
    """Yield every content block from assistant/user messages."""
    for ev in events:
        msg = ev.get("message")
        if not isinstance(msg, dict):
            continue
        content = msg.get("content")
        if not isinstance(content, list):
            continue
        for block in content:
            if isinstance(block, dict):
                yield block


def iter_tool_uses(events: Iterable[dict]) -> Iterator[tuple[str, dict]]:
    """Yield (tool_name, tool_input) for every tool_use block."""
    for block in _iter_content_blocks(events):
        if block.get("type") == "tool_use":
            name = block.get("name") or ""
            inp = block.get("input") or {}
            if not isinstance(inp, dict):
                inp = {}
            yield name, inp


def assert_skill_activated(events: Iterable[dict], skill_name: str) -> bool:
    """True iff a Skill tool_use invoked `skill_name` (exact match)."""
    events = list(events)
    for name, inp in iter_tool_uses(events):
        if name != "Skill":
            continue
        # Skill tool can carry the name under "skill" or "name" depending on
        # the runtime. Accept either.
        called = inp.get("skill") or inp.get("name") or ""
        if called == skill_name:
            return True
    return False


def assert_no_writes(events: Iterable[dict]) -> bool:
    """True iff no write-class tool was invoked."""
    for name, _ in iter_tool_uses(events):
        if name in WRITE_TOOLS:
            return False
    return True


def assert_first_relevant_read(events: Iterable[dict], path_pattern: str) -> bool:
    """True iff the FIRST read-class tool_use targets a path matching `path_pattern`.

    `path_pattern` is a regex matched against the tool's file_path/path/pattern input.
    Returns False if no read tool was used at all.
    """
    pat = re.compile(path_pattern)
    for name, inp in iter_tool_uses(events):
        if name not in READ_TOOLS:
            continue
        target = inp.get("file_path") or inp.get("path") or inp.get("pattern") or ""
        return bool(pat.search(target))
    return False


def extract_prose(events: Iterable[dict]) -> str:
    """Concatenate all assistant text blocks + the final result text.

    Useful for substring assertions (e.g. "response mentions banner").
    """
    parts: list[str] = []
    for ev in events:
        if ev.get("type") == "assistant":
            for block in _iter_content_blocks([ev]):
                if block.get("type") == "text":
                    t = block.get("text") or ""
                    if t:
                        parts.append(t)
        elif ev.get("type") == "result":
            r = ev.get("result")
            if isinstance(r, str) and r:
                parts.append(r)
    return "\n".join(parts)


def parse_json_response(events: Iterable[dict]) -> dict | None:
    """Best-effort: extract a JSON object from the assistant's final prose.

    Tries (in order):
      1. The full prose, parsed as JSON.
      2. The first ```json ... ``` fenced block.
      3. The first {...} substring that parses.
    Returns None on no match.
    """
    prose = extract_prose(events).strip()
    if not prose:
        return None

    # 1. Whole prose.
    try:
        v = json.loads(prose)
        if isinstance(v, dict):
            return v
    except json.JSONDecodeError:
        pass

    # 2. Fenced block.
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", prose, re.DOTALL)
    if m:
        try:
            v = json.loads(m.group(1))
            if isinstance(v, dict):
                return v
        except json.JSONDecodeError:
            pass

    # 3. First brace-balanced object that parses. Naive scan.
    start_idx = prose.find("{")
    while start_idx != -1:
        depth = 0
        for i in range(start_idx, len(prose)):
            c = prose[i]
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    chunk = prose[start_idx : i + 1]
                    try:
                        v = json.loads(chunk)
                        if isinstance(v, dict):
                            return v
                    except json.JSONDecodeError:
                        pass
                    break
        start_idx = prose.find("{", start_idx + 1)

    return None


# CLI: invoke one assertion against an evidence file. Useful for smoke tests.
#
#   python3 assertions.py <evidence-file> contains <substring>
#   python3 assertions.py <evidence-file> no-writes
#   python3 assertions.py <evidence-file> skill-activated <skill-name>
#   python3 assertions.py <evidence-file> first-read <regex>
#   python3 assertions.py <evidence-file> prose
#   python3 assertions.py <evidence-file> json
def _main(argv: list[str]) -> int:
    if len(argv) < 3:
        print("usage: assertions.py <evidence-file> <check> [args...]", file=sys.stderr)
        return 1
    evidence_path = argv[1]
    check = argv[2]
    events = load_events(evidence_path)

    if check == "contains":
        if len(argv) < 4:
            print("contains needs a substring", file=sys.stderr)
            return 1
        needle = argv[3]
        ok = needle in extract_prose(events)
        print("PASS" if ok else "FAIL")
        return 0 if ok else 1
    if check == "no-writes":
        ok = assert_no_writes(events)
        print("PASS" if ok else "FAIL")
        return 0 if ok else 1
    if check == "skill-activated":
        if len(argv) < 4:
            print("skill-activated needs a skill name", file=sys.stderr)
            return 1
        ok = assert_skill_activated(events, argv[3])
        print("PASS" if ok else "FAIL")
        return 0 if ok else 1
    if check == "first-read":
        if len(argv) < 4:
            print("first-read needs a regex", file=sys.stderr)
            return 1
        ok = assert_first_relevant_read(events, argv[3])
        print("PASS" if ok else "FAIL")
        return 0 if ok else 1
    if check == "prose":
        sys.stdout.write(extract_prose(events))
        return 0
    if check == "json":
        v = parse_json_response(events)
        if v is None:
            print("FAIL: no JSON found", file=sys.stderr)
            return 1
        json.dump(v, sys.stdout, indent=2)
        return 0

    print(f"unknown check: {check}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(_main(sys.argv))
