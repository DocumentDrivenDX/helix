"""The architecture scripts under test, importable by name as they import each other."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "skills" / "helix" / "scripts"))
