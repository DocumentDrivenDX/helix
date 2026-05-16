#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["databricks-sdk>=0.30", "PyYAML>=6"]
# ///
"""Verify a HELIX Genie skill install in a Databricks workspace.

Performs offline static checks only — does NOT call any Genie chat API.

Usage:
    scripts/verify-genie.py [--target WORKSPACE_PATH]

Required env:
    DATABRICKS_HOST   workspace URL
    DATABRICKS_TOKEN  PAT or OAuth token
Optional env:
    DATABRICKS_PROFILE  overrides via ~/.databrickscfg

Exit codes:
    0  all checks pass
    2  missing or invalid env
    5  install incomplete or malformed
"""
from __future__ import annotations

import argparse
import io
import os
import sys


EXPECTED_ACTIVITIES = [
    "00-discover",
    "01-frame",
    "02-design",
    "03-test",
    "04-build",
    "05-deploy",
    "06-iterate",
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument(
        "--target",
        default="/Workspace/.assistant/skills/helix",
        help="workspace target path (default: /Workspace/.assistant/skills/helix)",
    )
    return p.parse_args()


def fail(code: int, msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    sys.exit(code)


def check_env() -> None:
    if os.environ.get("DATABRICKS_PROFILE"):
        return
    if not os.environ.get("DATABRICKS_HOST"):
        fail(2, "DATABRICKS_HOST not set")
    if not os.environ.get("DATABRICKS_TOKEN"):
        fail(2, "DATABRICKS_TOKEN not set")


def main() -> int:
    args = parse_args()
    check_env()
    target = args.target.rstrip("/")

    try:
        from databricks.sdk import WorkspaceClient
        from databricks.sdk.service.workspace import ExportFormat
        import yaml
    except ImportError as exc:
        fail(2, f"missing dep: {exc}")

    w = WorkspaceClient()
    try:
        me = w.current_user.me()
        print(f"auth: {me.user_name}")
    except Exception as exc:
        fail(2, f"workspace auth failed: {exc}")

    checks = []

    def record(name: str, ok: bool, detail: str = "") -> None:
        status = "ok" if ok else "FAIL"
        checks.append((name, ok, detail))
        print(f"  [{status}] {name}{(': ' + detail) if detail else ''}")

    print(f"target: {target}")
    print()
    print("checks:")

    # 1. SKILL.md exists.
    try:
        objs = list(w.workspace.list(target))
        names = {o.path.split("/")[-1] for o in objs}
        record("target dir exists", True, f"{len(objs)} entries")
        record("SKILL.md present", "SKILL.md" in names)
    except Exception as exc:
        record("target dir exists", False, str(exc))
        return 5

    # 2. SKILL.md frontmatter.
    try:
        export = w.workspace.export(path=f"{target}/SKILL.md", format=ExportFormat.AUTO)
        import base64
        body = base64.b64decode(export.content).decode("utf-8")
    except Exception as exc:
        record("export SKILL.md", False, str(exc))
        return 5

    if not body.startswith("---\n"):
        record("frontmatter YAML present", False, "no leading ---")
        return 5
    end = body.find("\n---\n", 4)
    if end == -1:
        record("frontmatter YAML terminated", False, "no closing ---")
        return 5
    fm_text = body[4:end]
    try:
        fm = yaml.safe_load(fm_text)
    except yaml.YAMLError as exc:
        record("frontmatter YAML parses", False, str(exc))
        return 5
    record("frontmatter YAML parses", True)

    name = fm.get("name")
    record("frontmatter name == 'helix'", name == "helix", f"got: {name!r}")
    desc = fm.get("description", "")
    record("frontmatter description present", bool(desc), f"{len(desc)} chars")
    record(
        "description within agentskills bounds",
        1 <= len(desc) <= 1024,
        f"{len(desc)} chars (1..1024 expected)",
    )

    # 3. references/activities/ tree.
    activities_path = f"{target}/references/activities"
    try:
        act_objs = list(w.workspace.list(activities_path))
        act_names = {o.path.split("/")[-1] for o in act_objs}
    except Exception as exc:
        record("references/activities present", False, str(exc))
        return 5
    record("references/activities present", True, f"{len(act_objs)} entries")

    for activity in EXPECTED_ACTIVITIES:
        record(f"activity {activity} present", activity in act_names)

    failed = [c for c in checks if not c[1]]
    print()
    if failed:
        print(f"summary: {len(failed)} of {len(checks)} checks FAILED")
        return 5
    print(f"summary: all {len(checks)} checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
