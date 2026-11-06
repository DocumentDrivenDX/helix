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

# Pinned publications (T6): an approved deliverable needs pinned sources, and a
# pinned deliverable keeps its sources' content after the living source changes.
pinner="$repo_root/skills/helix/scripts/pin-sources.py"
repo="$tmp/pinrepo"
mkdir -p "$repo/knowledge" "$repo/publications"
export GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@t GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@t
git -C "$repo" init -q
printf -- '---\nddx:\n  id: pg-brief\n  authoring:\n    home: repo\n---\n# PG\n\nversion one\n' > "$repo/knowledge/pg.md"
git -C "$repo" add . && git -C "$repo" commit -q -m v1
cat > "$repo/publications/pub.md" <<'MD'
---
ddx:
  id: DEL-001
  type: deliverable
  status: approved
  authoring:
    home: repo
  links:
    - id: pg-brief
      kind: informed_by
    - id: other-graph-doc
      graph: other-atlas
      kind: informed_by
      rev: sha256:0000000000000000000000000000000000000000000000000000000000000000
---
# Publication
MD
git -C "$repo" add . && git -C "$repo" commit -q -m pub
pin_findings() { python3 "$validator" "$repo/publications/pub.md" --catalog "$repo_root/workflows" --format json | python3 -c 'import json,sys; print(",".join(sorted(f["check"] for f in json.load(sys.stdin)["findings"] if f["check"].startswith("pin_links"))))' || true; }
[ "$(pin_findings)" = "pin_links.0" ] || fail "approved deliverable with an unpinned link should report pin_links.0, got '$(pin_findings)'"
python3 "$pinner" pin "$repo/publications/pub.md" >/dev/null || fail "pin should succeed"
grep -q 'rev: git:' "$repo/publications/pub.md" || fail "pin should write a git rev"
[ -z "$(pin_findings)" ] || fail "pinned deliverable should have no pin_links findings"
git -C "$repo" commit -qam pinned
printf 'version two, edited after approval\n' >> "$repo/knowledge/pg.md"
git -C "$repo" commit -qam "assessment evolves"
python3 "$pinner" check "$repo/publications/pub.md" | grep -q "source has changed since the pin" || fail "check should report source drift"
python3 "$pinner" materialize "$repo/publications/pub.md" "$tmp/materialized" >/dev/null || fail "materialize should succeed"
grep -q "version one" "$tmp/materialized/knowledge/pg.md" && ! grep -q "version two" "$tmp/materialized/knowledge/pg.md" \
  || fail "materialized source must be the pinned version, not the edited one"
python3 "$pinner" pin "$repo/publications/pub.md" >/dev/null && git -C "$repo" diff --quiet -- publications/pub.md \
  || fail "re-pinning must not move an existing pin"
echo "OK: pinned publications"
