#!/usr/bin/env python3
"""Genie install scenario wrapper.

Builds the bundle (if not already built) and delegates to
`scripts/install-genie.py`. Inherits all env requirements from that script.

Usage:
    python tests/install/genie/install.py [--target WORKSPACE_PATH]
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
BUILD_SCRIPT = REPO_ROOT / "scripts" / "build-genie-bundle.sh"
INSTALL_SCRIPT = REPO_ROOT / "scripts" / "install-genie.py"
BUNDLE = REPO_ROOT / "dist" / "genie-bundle" / "helix"


def main() -> int:
    if not BUNDLE.exists():
        print(f"→ bundle not present at {BUNDLE}; building first")
        rc = subprocess.run(["bash", str(BUILD_SCRIPT)]).returncode
        if rc != 0:
            print(f"FAIL: bundle build exit {rc}", file=sys.stderr)
            return rc

    cmd = [str(INSTALL_SCRIPT), "--bundle", str(BUNDLE)]
    cmd.extend(sys.argv[1:])  # pass-through any --target etc.
    print(f"→ delegating to {' '.join(cmd)}")
    return subprocess.run(cmd, env=os.environ.copy()).returncode


if __name__ == "__main__":
    sys.exit(main())
