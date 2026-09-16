#!/usr/bin/env python3
"""Harvest operator prompts from local Claude Code and Codex sessions.

Purpose: gather the prompts a human actually typed at coding agents so we can
study them — which use cases recur (candidates to bake into HELIX) and where the
operator was papering over a ddx/HELIX deficiency (candidates to fix).

This is a *deterministic* extractor. It does no judgement; it produces a clean
corpus (one record per session, prompts in order) for a human or a model to
analyse. Keep it dumb and reproducible.

Session sources (auto-discovered, override with flags):
  - Claude Code: ~/.claude/projects/<encoded-cwd>/<uuid>.jsonl
                 (the projects dir is often a symlink; we follow it)
  - Codex:       ~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl

Examples:
  scripts/harvest_sessions.py --since 4                 # markdown digest, last 4 days
  scripts/harvest_sessions.py --since 7 --format jsonl  # machine corpus, last 7 days
  scripts/harvest_sessions.py --since 4 --project helix # only cwds matching 'helix'
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

# --- defaults; override on the CLI ------------------------------------------
DEFAULT_CLAUDE_ROOTS = [
    Path.home() / ".claude" / "projects",
    Path("/Users/erik/.claude/projects"),
]
DEFAULT_CODEX_ROOT = Path.home() / ".codex" / "sessions"

# Codex injects developer/context messages as role:user; real prompts never
# start with one of these XML-ish wrappers.
INJECTED_PREFIXES = (
    "<environment_context",
    "<permissions instructions",
    "<user_instructions",
    "<system-reminder",
    "<persistent",
    "<codex_internal_context",  # codex goal/continuation re-injection
    "<subagent_notification",   # codex subagent fan-out plumbing
    "# agents.md instructions",  # AGENTS.md injected as a user turn
)
# Claude slash-command / local-command plumbing surfaces as user text.
COMMAND_MARKERS = ("<local-command-caveat>", "<command-name>", "<command-message>")


def _is_real_prompt(text: str) -> bool:
    t = (text or "").strip()
    if not t:
        return False
    low = t.lstrip().lower()
    if low.startswith(INJECTED_PREFIXES):
        return False
    if any(m in t for m in COMMAND_MARKERS):
        return False
    return True


def _text_from_content(content) -> str:
    """Flatten a message 'content' (str | list[block]) to typed user text only."""
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    parts = []
    for block in content:
        if not isinstance(block, dict):
            continue
        # tool_result blocks are not human input
        if block.get("type") in ("tool_result", "tool_use", "image", "thinking"):
            return ""  # this user turn is a tool result, not a prompt
        if block.get("type") == "text" or "text" in block:
            parts.append(block.get("text", ""))
    return "\n".join(p for p in parts if p)


def harvest_claude(path: Path) -> dict | None:
    prompts, cwd, model, branch = [], None, None, None
    start_ts = end_ts = None
    try:
        fh = path.open(encoding="utf-8", errors="replace")
    except OSError:
        return None
    with fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                o = json.loads(line)
            except json.JSONDecodeError:
                continue
            cwd = cwd or o.get("cwd")
            branch = branch or o.get("gitBranch")
            ts = o.get("timestamp")
            if ts:
                start_ts = start_ts or ts
                end_ts = ts
            if o.get("type") == "assistant" and not model:
                model = (o.get("message") or {}).get("model")
            if o.get("type") != "user" or o.get("isSidechain"):
                continue
            msg = o.get("message") or {}
            if msg.get("role") != "user":
                continue
            text = _text_from_content(msg.get("content"))
            if _is_real_prompt(text):
                prompts.append({"ts": ts, "text": text.strip()})
    if not prompts:
        return None
    return {
        "harness": "claude",
        "session_id": path.stem,
        "project": cwd,
        "git_branch": branch,
        "model": model,
        "path": str(path),
        "start_ts": start_ts,
        "end_ts": end_ts,
        "n_prompts": len(prompts),
        "prompts": prompts,
    }


def harvest_codex(path: Path) -> dict | None:
    prompts, cwd, model = [], None, None
    start_ts = end_ts = None
    try:
        fh = path.open(encoding="utf-8", errors="replace")
    except OSError:
        return None
    with fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                o = json.loads(line)
            except json.JSONDecodeError:
                continue
            typ = o.get("type")
            p = o.get("payload") or {}
            if typ == "session_meta":
                cwd = cwd or p.get("cwd")
                start_ts = start_ts or o.get("timestamp")
                model = model or p.get("model")
                continue
            ts = o.get("timestamp")
            if ts:
                end_ts = ts
            if typ != "response_item" or p.get("type") != "message":
                continue
            if p.get("role") != "user":
                continue
            text = "".join(
                b.get("text", "") for b in (p.get("content") or []) if isinstance(b, dict)
            )
            if _is_real_prompt(text):
                prompts.append({"ts": ts, "text": text.strip()})
    if not prompts:
        return None
    return {
        "harness": "codex",
        "session_id": path.stem.replace("rollout-", ""),
        "project": cwd,
        "git_branch": None,
        "model": model,
        "path": str(path),
        "start_ts": start_ts,
        "end_ts": end_ts,
        "n_prompts": len(prompts),
        "prompts": prompts,
    }


def discover(claude_roots, codex_root, cutoff: float):
    files = []
    for root in claude_roots:
        if not root.exists():
            continue
        for f in root.glob("**/*.jsonl"):
            try:
                if f.stat().st_mtime >= cutoff:
                    files.append(("claude", f))
            except OSError:
                continue
    if codex_root.exists():
        for f in codex_root.glob("**/rollout-*.jsonl"):
            try:
                if f.stat().st_mtime >= cutoff:
                    files.append(("codex", f))
            except OSError:
                continue
    return files


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--since", type=float, default=4, help="look back this many days (default 4)")
    ap.add_argument("--format", choices=["md", "jsonl"], default="md", help="output format")
    ap.add_argument("--project", default=None, help="only sessions whose cwd contains this substring")
    ap.add_argument("--harness", choices=["claude", "codex"], default=None, help="limit to one harness")
    ap.add_argument("--claude-root", action="append", type=Path, default=None, help="override Claude projects root (repeatable)")
    ap.add_argument("--codex-root", type=Path, default=DEFAULT_CODEX_ROOT, help="override Codex sessions root")
    args = ap.parse_args(argv)

    claude_roots = args.claude_root or DEFAULT_CLAUDE_ROOTS
    cutoff = time.time() - args.since * 86400
    files = discover(claude_roots, args.codex_root, cutoff)

    sessions = []
    for harness, f in files:
        if args.harness and harness != args.harness:
            continue
        rec = harvest_claude(f) if harness == "claude" else harvest_codex(f)
        if not rec:
            continue
        if args.project and (args.project not in (rec.get("project") or "")):
            continue
        sessions.append(rec)

    sessions.sort(key=lambda r: r.get("start_ts") or "")

    if args.format == "jsonl":
        for rec in sessions:
            sys.stdout.write(json.dumps(rec, ensure_ascii=False) + "\n")
        return 0

    # markdown digest, grouped by project
    by_proj: dict[str, list] = {}
    for rec in sessions:
        by_proj.setdefault(rec.get("project") or "(unknown)", []).append(rec)
    total_prompts = sum(r["n_prompts"] for r in sessions)
    print(f"# Session harvest — last {args.since:g} days")
    print(f"\n{len(sessions)} sessions, {total_prompts} operator prompts, {len(by_proj)} projects\n")
    for proj in sorted(by_proj, key=lambda p: -sum(r["n_prompts"] for r in by_proj[p])):
        recs = by_proj[proj]
        print(f"\n## {proj}  ({sum(r['n_prompts'] for r in recs)} prompts, {len(recs)} sessions)\n")
        for rec in sorted(recs, key=lambda r: r.get("start_ts") or ""):
            hdr = f"### [{rec['harness']}] {rec.get('start_ts','?')}"
            if rec.get("git_branch"):
                hdr += f"  ({rec['git_branch']})"
            print(hdr)
            print(f"`{rec['path']}`\n")
            for pr in rec["prompts"]:
                txt = pr["text"].strip().replace("\r", "")
                # keep each prompt as a quote block; collapse blank runs
                print("> " + txt.replace("\n", "\n> "))
                print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
