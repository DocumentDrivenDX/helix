#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["databricks-sdk>=0.30"]
# ///
"""Upload a HELIX Genie skill bundle to a Databricks workspace.

Usage:
    scripts/install-genie.py [--bundle PATH] [--target WORKSPACE_PATH]

Required env:
    DATABRICKS_HOST   workspace URL (https://...)
    DATABRICKS_TOKEN  PAT or OAuth token
Optional env:
    DATABRICKS_PROFILE  overrides host/token via ~/.databrickscfg

Exit codes:
    0  success
    2  missing or invalid env
    3  bundle not present (run scripts/build-genie-bundle.sh first)
    4  upload error
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument(
        "--bundle",
        default="dist/genie-bundle/helix",
        help="path to the assembled bundle directory (default: dist/genie-bundle/helix)",
    )
    p.add_argument(
        "--target",
        default="/Workspace/.assistant/skills/helix",
        help="workspace target path (default: /Workspace/.assistant/skills/helix)",
    )
    p.add_argument(
        "--grant-users-read",
        action="store_true",
        help="after upload, grant `users` group CAN_READ on the skill dir + its parent "
             "(needed on workspaces with admin-only root ACL — auto-on when target starts "
             "with /Workspace/)",
    )
    return p.parse_args()


def fail(code: int, msg: str) -> None:
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(code)


def check_env() -> None:
    profile = os.environ.get("DATABRICKS_PROFILE")
    if profile:
        return
    if not os.environ.get("DATABRICKS_HOST"):
        fail(
            2,
            "DATABRICKS_HOST not set (or set DATABRICKS_PROFILE to a section in ~/.databrickscfg)",
        )
    if not os.environ.get("DATABRICKS_TOKEN"):
        fail(2, "DATABRICKS_TOKEN not set (or use DATABRICKS_PROFILE)")


def grant_users_read(client, path: str) -> bool:
    """Idempotently grant `users` group CAN_READ on a workspace directory.

    Workspace ACL inheritance defaults to admin-only on tightly-scoped
    tenants — non-admins can't see the skill and Genie won't surface it.
    Returns True if the grant is in place (already or after update),
    False on a non-fatal error (logged).
    """
    try:
        from databricks.sdk.service.workspace import (
            WorkspaceObjectAccessControlRequest,
            WorkspaceObjectPermissionLevel,
        )
    except ImportError as exc:
        print(f"  warn: ACL types unavailable in this SDK version ({exc}); skipping",
              file=sys.stderr)
        return False

    try:
        status = client.workspace.get_status(path)
        obj_id = str(status.object_id)
    except Exception as exc:
        print(f"  warn: get-status {path}: {exc}; skipping ACL grant", file=sys.stderr)
        return False

    grant_levels = {
        WorkspaceObjectPermissionLevel.CAN_READ,
        WorkspaceObjectPermissionLevel.CAN_RUN,
        WorkspaceObjectPermissionLevel.CAN_EDIT,
        WorkspaceObjectPermissionLevel.CAN_MANAGE,
    }
    try:
        perms = client.workspace.get_permissions(
            workspace_object_type="directories",
            workspace_object_id=obj_id,
        )
        for acl in (perms.access_control_list or []):
            if acl.group_name != "users":
                continue
            for p in (acl.all_permissions or []):
                if p.permission_level in grant_levels:
                    print(f"  ACL OK on {path}: users already has {p.permission_level.value}")
                    return True
    except Exception as exc:
        print(f"  warn: get-permissions {path}: {exc}; attempting grant anyway",
              file=sys.stderr)

    try:
        client.workspace.update_permissions(
            workspace_object_type="directories",
            workspace_object_id=obj_id,
            access_control_list=[
                WorkspaceObjectAccessControlRequest(
                    group_name="users",
                    permission_level=WorkspaceObjectPermissionLevel.CAN_READ,
                ),
            ],
        )
        print(f"  granted users CAN_READ on {path}")
        return True
    except Exception as exc:
        print(f"  warn: update-permissions {path}: {exc}", file=sys.stderr)
        print(f"  non-admin users may not see HELIX. Grant manually:", file=sys.stderr)
        print(f"    databricks workspace update-permissions directories {obj_id} \\", file=sys.stderr)
        print(f"      --json '{{\"access_control_list\":[{{\"group_name\":\"users\",\"permission_level\":\"CAN_READ\"}}]}}'",
              file=sys.stderr)
        return False


def check_bundle(bundle: Path) -> None:
    if not bundle.is_dir():
        fail(
            3,
            f"bundle dir not found: {bundle}. Run `bash scripts/build-genie-bundle.sh` first.",
        )
    skill_md = bundle / "SKILL.md"
    if not skill_md.is_file():
        fail(3, f"bundle missing SKILL.md at {skill_md}")
    if bundle.name != "helix":
        fail(
            3,
            f"bundle parent dir is '{bundle.name}', must be 'helix' (agentskills.io spec invariant)",
        )


def main() -> int:
    args = parse_args()
    check_env()
    bundle = Path(args.bundle).resolve()
    target = args.target.rstrip("/")
    check_bundle(bundle)

    try:
        from databricks.sdk import WorkspaceClient
        from databricks.sdk.service.workspace import ImportFormat
    except ImportError as exc:
        fail(2, f"databricks-sdk not importable: {exc}")

    print(f"connecting to workspace...")
    w = WorkspaceClient()
    try:
        me = w.current_user.me()
        print(f"  authenticated as {me.user_name}")
    except Exception as exc:
        fail(2, f"workspace auth failed: {exc}")

    print(f"target: {target}")
    print(f"bundle: {bundle}")

    # Collect files relative to bundle root.
    files = [p for p in bundle.rglob("*") if p.is_file()]
    if not files:
        fail(3, f"bundle has no files: {bundle}")

    print(f"  {len(files)} files to upload")
    print()

    # mkdirs for unique parent dirs.
    parent_dirs = sorted({str(Path(target) / p.relative_to(bundle).parent) for p in files})
    for d in parent_dirs:
        # Normalize: convert any '.' segment to just the target.
        d_norm = d.rstrip("/.")
        if not d_norm:
            d_norm = target
        try:
            w.workspace.mkdirs(path=d_norm)
        except Exception as exc:
            print(f"  mkdirs warn {d_norm}: {exc}", file=sys.stderr)

    uploaded = 0
    failed = 0
    for f in files:
        rel = f.relative_to(bundle)
        dest = f"{target}/{rel.as_posix()}"
        try:
            with open(f, "rb") as fp:
                w.workspace.upload(
                    path=dest,
                    content=fp,
                    format=ImportFormat.AUTO,
                    overwrite=True,
                )
            uploaded += 1
            if uploaded % 25 == 0 or uploaded == len(files):
                print(f"  uploaded {uploaded}/{len(files)}")
        except Exception as exc:
            failed += 1
            print(f"  FAIL {dest}: {exc}", file=sys.stderr)

    print()
    print(f"summary: {uploaded} uploaded, {failed} failed, {len(parent_dirs)} dirs")
    if failed > 0:
        return 4

    # Auto-grant read access on workspace-shared installs (target outside /Users/).
    # Explicit --grant-users-read overrides the auto-detect.
    auto_grant = args.grant_users_read or target.startswith("/Workspace/")
    if auto_grant and not target.startswith("/Users/"):
        parent = str(Path(target).parent)
        print()
        print("ensuring skill is readable by all workspace users:")
        grant_users_read(w, parent)
        grant_users_read(w, target)

    print(f"\nNext: python scripts/verify-genie.py --target {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
