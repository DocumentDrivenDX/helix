#!/usr/bin/env python3
"""Genie verify scenario wrapper.

Delegates to `scripts/verify-genie.py`. Inherits all env requirements
from that script.

Usage:
    python tests/install/genie/verify.py [--target WORKSPACE_PATH]
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
VERIFY_SCRIPT = REPO_ROOT / "scripts" / "verify-genie.py"


def main() -> int:
    cmd = [str(VERIFY_SCRIPT)]
    cmd.extend(sys.argv[1:])
    print(f"→ delegating to {' '.join(cmd)}")
    return subprocess.run(cmd, env=os.environ.copy()).returncode


if __name__ == "__main__":
    sys.exit(main())
