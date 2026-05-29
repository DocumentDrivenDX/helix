#!/usr/bin/env python3
"""Capture a real claude session and translate it to a HELIX demo session.jsonl.

Wraps `claude -p --output-format=stream-json` against an optional fixture
directory, parses the Anthropic streaming event format, and writes a
`session.jsonl` that the deterministic renderer
(`scripts/demos/render_session.py`) can replay.

Usage:
    capture_session.py <slug> --prompt "..." [--fixture path/]
    capture_session.py <slug> --prompt-file prompt.txt --fixture path/

The captured session is written to `docs/demos/<slug>/session.jsonl` and
includes a `meta` header derived from the slug. Review the capture, then
render it with:

    python3 scripts/demos/render_session.py docs/demos/<slug>/session.jsonl

Capture once, verify by hand (the agent's outputs may need light
editing for clarity), then commit. The renderer never reaches the live
agent; once the session.jsonl exists, the asciicast rebuild is
deterministic.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

CLAUDE_BIN = shutil.which("claude") or "claude"

ALLOWED_SCENARIO_KEYS = {
    "adopt",
    "brief",
    "align",
    "plan",
    "evolve",
    "concerns",
    "review",
    "execute",
    "install",
    "smoke",
}


def slug_to_scenario(slug: str) -> str:
    base = slug.removeprefix("helix-")
    return base if base in ALLOWED_SCENARIO_KEYS else base


def open_session(slug: str, prompt: str, out: list[dict]) -> None:
    out.append(
        {
            "meta": {
                "title": f"HELIX {slug_to_scenario(slug)}: captured session",
                "width": 100,
                "height": 30,
                "scenario": slug_to_scenario(slug),
                "timestamp": int(time.time()),
            }
        }
    )
    out.append({"narration": "Captured from a real Claude session — edit narrations to taste."})
    out.append({"prompt": prompt})


def translate_event(raw: dict, out: list[dict]) -> None:
    """Map one Anthropic stream-json event to one or more session.jsonl events."""
    kind = raw.get("type")
    if kind == "assistant":
        message = raw.get("message", {})
        for block in message.get("content", []):
            btype = block.get("type")
            if btype == "text":
                text = block.get("text", "").strip()
                if text:
                    out.append({"assistant": text, "pace_ms": 18})
            elif btype == "tool_use":
                name = block.get("name", "Tool")
                args = block.get("input", {}) or {}
                # Trim long values for visual fit
                trimmed = {
                    k: (v if isinstance(v, (int, float, bool)) else str(v)[:80])
                    for k, v in args.items()
                }
                out.append({"tool_call": {"name": name, "args": trimmed}})
    elif kind == "user":
        message = raw.get("message", {})
        for block in message.get("content", []):
            if block.get("type") == "tool_result":
                content = block.get("content", "")
                if isinstance(content, list):
                    text_parts = [c.get("text", "") for c in content if c.get("type") == "text"]
                    text = "\n".join(text_parts)
                else:
                    text = str(content)
                lines = text.count("\n") + 1 if text else 0
                if lines > 8:
                    out.append({"tool_result": "", "lines": lines})
                else:
                    out.append({"tool_result": text or "(no output)"})
    elif kind == "result":
        # Final summary event from the SDK; nothing user-visible.
        pass


def parse_stream(stdout: str) -> list[dict]:
    events: list[dict] = []
    for line in stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError as e:
            print(f"warn: skipping unparseable event: {e.msg}", file=sys.stderr)
    return events


def capture(prompt: str, cwd: Path) -> list[dict]:
    cmd = [
        CLAUDE_BIN,
        "-p",
        "--output-format=stream-json",
        "--verbose",
        "--no-session-persistence",
        "--dangerously-skip-permissions",
        prompt,
    ]
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(cwd),
        check=False,
    )
    if proc.returncode != 0:
        print(f"claude exited {proc.returncode}: {proc.stderr}", file=sys.stderr)
        raise SystemExit(proc.returncode)
    return parse_stream(proc.stdout)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("slug", help="demo slug, e.g. helix-align")
    parser.add_argument("--prompt", help="prompt text passed to claude -p")
    parser.add_argument(
        "--prompt-file",
        type=Path,
        help="file containing the prompt text (alternative to --prompt)",
    )
    parser.add_argument(
        "--fixture",
        type=Path,
        help="path to a fixture directory the session runs in (copied to a tmp workdir)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="output session.jsonl path (default: docs/demos/<slug>/session.jsonl)",
    )
    parser.add_argument(
        "--from-stream",
        type=Path,
        help="read a previously-captured stream-json file instead of spawning claude (smoke testing)",
    )
    args = parser.parse_args(argv)

    if args.prompt and args.prompt_file:
        print("error: pass either --prompt or --prompt-file, not both", file=sys.stderr)
        return 2
    if args.prompt_file:
        prompt = args.prompt_file.read_text(encoding="utf-8").strip()
    elif args.prompt:
        prompt = args.prompt
    else:
        print("error: provide --prompt or --prompt-file", file=sys.stderr)
        return 2

    repo_root = Path(__file__).resolve().parent.parent.parent
    out_path: Path = args.output or repo_root / "docs" / "demos" / args.slug / "session.jsonl"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if args.from_stream:
        raw_events = parse_stream(args.from_stream.read_text(encoding="utf-8"))
    else:
        with tempfile.TemporaryDirectory(prefix="helix-demo-") as tmp:
            workdir = Path(tmp)
            if args.fixture:
                for entry in args.fixture.iterdir():
                    dest = workdir / entry.name
                    if entry.is_dir():
                        shutil.copytree(entry, dest)
                    else:
                        shutil.copy2(entry, dest)

            raw_events = capture(prompt, workdir)

    translated: list[dict] = []
    open_session(args.slug, prompt, translated)
    for event in raw_events:
        translate_event(event, translated)

    with out_path.open("w", encoding="utf-8") as f:
        for ev in translated:
            f.write(json.dumps(ev, ensure_ascii=False) + "\n")

    print(
        f"captured {len(raw_events)} raw events → "
        f"{len(translated)} session events at {out_path}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
