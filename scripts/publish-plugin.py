#!/usr/bin/env python3
"""Copy the built plugin package into a DocumentDrivenDX/plugins checkout.

Replaces plugins/helix there with the package that
scripts/build-plugin-package.sh wrote. It changes nothing else in that checkout
(other plugins and the marketplace file stay as they are), and it commits and
pushes nothing.

The release workflow runs this on every release tag and commits the result.

Usage:
    just publish-plugin <path to the DocumentDrivenDX/plugins checkout>
"""
import argparse
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
MARKETPLACE = "documentdrivendx"
PLUGIN_SOURCE = "./plugins/helix"
# The package carries HELIX's own marketplace file, which does not belong inside
# another marketplace.
OMITTED = {".claude-plugin/marketplace.json"}
# Names the commit the package was built from, so it differs between builds of
# the same content and does not by itself make a new release.
PROVENANCE = "PACKAGE-SOURCE.json"


def contents(root):
    """The bytes of every published file under root, except build provenance."""
    found = {}
    for path in root.rglob("*"):
        name = path.relative_to(root).as_posix()
        if path.is_file() and name not in OMITTED and name != PROVENANCE:
            found[name] = path.read_bytes()
    return found


def version_in(root):
    return json.loads((root / ".claude-plugin/plugin.json").read_text())["version"]


def ordering(version):
    return tuple(int(part) for part in version.split("."))


def publish_into(checkout, package):
    """Write the package to plugins/helix; return (version, changed).

    Installed copies update only when the version changes, so different content
    under the published version is an error and nothing is written.
    """
    manifest = checkout / ".claude-plugin/marketplace.json"
    if not manifest.is_file():
        raise ValueError(f"{checkout} holds no marketplace file")
    marketplace = json.loads(manifest.read_text())
    entry = next((p for p in marketplace.get("plugins", []) if p.get("name") == "helix"), None)
    if marketplace.get("name") != MARKETPLACE or not entry or entry.get("source") != PLUGIN_SOURCE:
        raise ValueError(f"the marketplace file must be named {MARKETPLACE} and list helix at {PLUGIN_SOURCE}")
    version = version_in(package)
    target = checkout / "plugins/helix"
    if target.exists():
        if contents(target) == contents(package):
            return version, False
        # Re-running an older release must not roll installed copies back.
        if ordering(version) < ordering(version_in(target)):
            raise ValueError(f"version {version_in(target)} is published; refusing to replace it with older {version}")
        if version_in(target) == version:
            raise ValueError(f"version {version} is already published with different content; release a new version")
        shutil.rmtree(target)
    for name in [*contents(package), PROVENANCE]:
        destination = target / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(package / name, destination)
    return version, True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkout", type=Path, help="DocumentDrivenDX/plugins checkout")
    parser.add_argument("--package", type=Path, default=ROOT / "dist/plugin-package/helix")
    args = parser.parse_args()
    try:
        version, changed = publish_into(args.checkout, args.package)
    except (ValueError, KeyError, OSError) as error:
        print(str(error), file=sys.stderr)
        return 1
    print(f"{'wrote' if changed else 'unchanged:'} plugins/helix {version}. Nothing was committed or pushed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
