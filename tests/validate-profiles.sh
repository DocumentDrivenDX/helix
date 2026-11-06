#!/usr/bin/env bash
# Graph profiles (ADR-015): profile files are well-formed and select real
# artifact types, every non-default profile graph is current, and a marker's
# `profile:` keys resolve (absent = software-delivery; unknown = malformed).
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fail() { echo "FAIL: $*" >&2; exit 1; }

python3 - "$repo_root" <<'PYEOF' || fail "profile validation failed"
import sys, subprocess, filecmp, shutil, os, tempfile
from pathlib import Path
import yaml

root = Path(sys.argv[1])
profiles = {p.stem: yaml.safe_load(p.read_text()) for p in sorted((root / "workflows/profiles").glob("*.yml")) if not p.name.endswith(".graph.yml")}
assert "software-delivery" in profiles, "software-delivery profile is required"

types = set()
for meta in (root / "workflows/activities").glob("*/artifacts/*/meta.yml"):
    types.add((yaml.safe_load(meta.read_text()).get("artifact") or {}).get("id") or meta.parent.name)

for pid, prof in profiles.items():
    assert (prof.get("profile") or {}).get("id") == pid, f"{pid}: profile.id must equal file name"
    sel = prof.get("types")
    assert sel == "all" or isinstance(sel, list), f"{pid}: types must be 'all' or a list"
    if sel != "all":
        missing = sorted(set(sel) - types)
        assert not missing, f"{pid}: unknown types {missing}"
        extra = sorted(set(prof.get("locations", {})) - set(sel))
        assert not extra, f"{pid}: locations for unselected types {extra}"
    assert prof["authority"]["cross_graph"] == "advisory", f"{pid}: cross_graph authority must be advisory (ADR-016)"
    assert prof["authority"]["within_graph"] in ("positional", "advisory"), f"{pid}: bad within_graph authority"

# Non-default profile graphs must match what the generator would emit.
for pid in profiles:
    if pid == "software-delivery":
        continue
    committed = root / f"workflows/profiles/{pid}.graph.yml"
    assert committed.is_file(), f"{committed} missing; run scripts/generate_graph.py --profile {pid}"
    backup = tempfile.mktemp()
    shutil.copy(committed, backup)
    subprocess.check_call([sys.executable, str(root / "scripts/generate_graph.py"), "--profile", pid], stdout=subprocess.DEVNULL)
    same = filecmp.cmp(backup, committed, shallow=False)
    shutil.copy(backup, committed)
    assert same, f"DRIFT: {committed.name} is stale; run scripts/generate_graph.py --profile {pid}"

# Marker resolution: absent profile = software-delivery; unknown = malformed.
def resolve(marker):
    errs, ids = [], set()
    for f in marker.get("flows", []):
        if f["id"] in ids: errs.append(f"duplicate id {f['id']}")
        ids.add(f["id"])
        if f.get("profile", "software-delivery") not in profiles:
            errs.append(f"unknown profile {f['profile']}")
    return errs

assert resolve(yaml.safe_load((root / ".helix.yml").read_text())) == [], "repo marker must resolve"
two = {"flows": [{"id": "helix", "root": "docs/helix/"}, {"id": "atlas", "profile": "technology-atlas", "root": "knowledge/"}]}
assert resolve(two) == [], "two-profile marker must resolve"
assert resolve({"flows": [{"id": "x", "profile": "nope", "root": "x/"}]}) == ["unknown profile nope"]
print("OK: profiles")
PYEOF

# Validation tiers (T4): a draft with missing content passes in an atlas flow
# and fails once approved; the same draft is still strict in software-delivery.
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/knowledge" "$tmp/docs/helix"
cat > "$tmp/.helix.yml" <<'YAML'
flows:
  - id: helix
    root: docs/helix/
  - id: atlas
    profile: technology-atlas
    root: knowledge/
YAML
brief() { # status
  printf -- '---\nddx:\n  id: DB-001\n  type: decision-brief\n  status: %s\n  authoring:\n    home: repo\n---\n\n# DB-001: Incomplete\n\n## Context\n\nOnly context so far.\n' "$1"
}
validator="$repo_root/skills/helix/scripts/validate-instance.py"
brief draft > "$tmp/knowledge/draft.md"
brief approved > "$tmp/knowledge/approved.md"
brief draft > "$tmp/docs/helix/draft.md"
python3 "$validator" "$tmp/knowledge/draft.md" --catalog "$repo_root/workflows" >/dev/null || fail "incomplete draft should pass in an atlas flow"
if python3 "$validator" "$tmp/knowledge/approved.md" --catalog "$repo_root/workflows" >/dev/null; then fail "incomplete approved brief should fail"; fi
if python3 "$validator" "$tmp/docs/helix/draft.md" --catalog "$repo_root/workflows" >/dev/null; then fail "incomplete draft should still fail in software-delivery"; fi

# Scope variants: a reusable component-profile is judged by its own section list.
python3 "$validator" "$repo_root/workflows/activities/00-discover/artifacts/component-profile/example-reusable.md" --catalog "$repo_root/workflows" >/dev/null \
  || fail "reusable component-profile example should validate"
sed 's/^  scope: reusable/  scope: contextual/' "$repo_root/workflows/activities/00-discover/artifacts/component-profile/example-reusable.md" > "$tmp/as-contextual.md"
if python3 "$validator" "$tmp/as-contextual.md" --catalog "$repo_root/workflows" >/dev/null; then fail "reusable content labelled contextual should fail"; fi
echo "OK: validation tiers and scope variants"
