#!/usr/bin/env bash
# Graph profiles (ADR-017): profile files are well-formed and select real
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
    assert prof["authority"]["cross_graph"] == "advisory", f"{pid}: cross_graph authority must be advisory (ADR-018)"
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

# Validation tiers (T4): incomplete content passes at the default tier in an atlas
# flow and fails at the publish tier; software-delivery is strict at both.
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
brief() {
  printf -- '---\nddx:\n  id: DB-001\n  type: decision-brief\n  authoring:\n    home: repo\n---\n\n# DB-001: Incomplete\n\n## Context\n\nOnly context so far.\n'
}
validator="$repo_root/skills/helix/scripts/validate-instance.py"
brief > "$tmp/knowledge/incomplete.md"
brief > "$tmp/docs/helix/incomplete.md"
python3 "$validator" "$tmp/knowledge/incomplete.md" --catalog "$repo_root/workflows" >/dev/null || fail "incomplete content should pass at the default tier in an atlas flow"
if python3 "$validator" "$tmp/knowledge/incomplete.md" --catalog "$repo_root/workflows" --tier publish >/dev/null; then fail "incomplete content should fail at the publish tier"; fi
if python3 "$validator" "$tmp/docs/helix/incomplete.md" --catalog "$repo_root/workflows" >/dev/null; then fail "incomplete content should still fail in software-delivery"; fi

# Scope variants: a reusable component-profile is judged by its own section list.
python3 "$validator" "$repo_root/workflows/activities/00-discover/artifacts/component-profile/example-reusable.md" --catalog "$repo_root/workflows" >/dev/null \
  || fail "reusable component-profile example should validate"
sed 's/^  scope: reusable/  scope: contextual/' "$repo_root/workflows/activities/00-discover/artifacts/component-profile/example-reusable.md" > "$tmp/as-contextual.md"
if python3 "$validator" "$tmp/as-contextual.md" --catalog "$repo_root/workflows" >/dev/null; then fail "reusable content labelled contextual should fail"; fi
# A reusable tech-spike (a spike published as knowledge) is judged by its own section list: test
# setup, views affected and reproduction required, no recommendation. Its `answers` link carries
# the number of the open question it answers, and the technology-atlas profile accepts the kind.
spike="$repo_root/tests/fixtures/validate-instance/reusable-spike.md"
mkdir -p "$tmp/knowledge/spikes"
cp "$spike" "$tmp/knowledge/spikes/TS-001-examplestore-restore.md"
for at in "$spike" "$tmp/knowledge/spikes/TS-001-examplestore-restore.md"; do
  python3 "$validator" "$at" --catalog "$repo_root/workflows" --tier publish >"$tmp/spike.out" 2>&1 || fail "the reusable spike fixture should validate at the publish tier:
$(cat "$tmp/spike.out")"
  grep -q "WARNING\|BLOCKING" "$tmp/spike.out" && fail "the reusable spike fixture should have no findings:
$(cat "$tmp/spike.out")"
done
spike_case() {  # sed expression, expected finding regex
  sed "$1" "$spike" >"$tmp/spike-case.md"
  if python3 "$validator" "$tmp/spike-case.md" --catalog "$repo_root/workflows" >"$tmp/spike.out" 2>&1; then fail "spike case /$1/ should block"; fi
  grep -Eq "$2" "$tmp/spike.out" || fail "spike case /$1/ should report /$2/:
$(cat "$tmp/spike.out")"
}
spike_case 's/^## Reproduction$/## Reproduction\n\n**RECOMMENDATION**: Adopt it./' "BLOCKING +no_recommendation "
spike_case 's/^## Test Setup$/## Setup/' "BLOCKING +required_sections\.test_setup "
spike_case 's/^## Views Affected$/## Readers/' "BLOCKING +required_sections\.views_affected "
spike_case 's/, question: 2,/,/' "BLOCKING +links\.0\.question "
spike_case 's/question: 2,/question: two,/' "BLOCKING +links\.0\.question "
spike_case '/^  scope: reusable$/d' "BLOCKING +required_sections\.recommendations "
echo "OK: validation tiers and scope variants"

# Pinned publications (T6): a deliverable validated at the publish tier needs pinned sources, and a
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
pin_findings() { python3 "$validator" "$repo/publications/pub.md" --catalog "$repo_root/workflows" --tier publish --format json | python3 -c 'import json,sys; print(",".join(sorted(f["check"] for f in json.load(sys.stdin)["findings"] if f["check"].startswith("pin_links"))))' || true; }
[ "$(pin_findings)" = "pin_links.0" ] || fail "a deliverable with an unpinned link at the publish tier should report pin_links.0, got '$(pin_findings)'"
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

# Scenario (SD-003 acceptance): Node.js vs Python. Reusable briefs live
# in an atlas repo; a client graph in another repo holds the Decision Brief and
# a publication that cites them by graph and pinned revision.
fx="$repo_root/tests/fixtures/scenario-runtime-choice"
sc="$tmp/scenario"
mkdir -p "$sc"
cp -R "$fx/atlas" "$sc/atlas"; cp -R "$fx/client" "$sc/client"
for r in atlas client; do git -C "$sc/$r" init -q; done
git -C "$sc/atlas" add . && git -C "$sc/atlas" commit -q -m "briefs"
rev="git:$(git -C "$sc/atlas" rev-parse HEAD)"
for f in atlas/technology/nodejs.md atlas/technology/python.md client/decisions/DB-001-test-decision.md client/publications/DEL-001-test-publication.md; do
  python3 "$validator" "$sc/$f" --catalog "$repo_root/workflows" >/dev/null || fail "scenario fixture $f should validate at the default tier"
done
# Approve: unpinned cross-graph links must block, pinned ones pass.
for f in client/decisions/DB-001-test-decision.md client/publications/DEL-001-test-publication.md; do
  if python3 "$validator" "$sc/$f" --catalog "$repo_root/workflows" --tier publish >/dev/null; then fail "$f with unpinned cross-graph links should fail at the publish tier"; fi
  python3 - "$sc/$f" "$rev" <<'PY'
import re, sys
p, rev = sys.argv[1], sys.argv[2]
t = open(p).read()
t = re.sub(r"(kind: (?:evaluates|informed_by))(\}?)\n", lambda m: m.group(0), t)
t = re.sub(r"\{id: ([\w.-]+), graph: ([\w-]+), kind: evaluates\}", r"{id: \1, graph: \2, kind: evaluates, rev: " + rev + "}", t)
t = re.sub(r"(    - id: component-profile-[\w-]+\n      graph: [\w-]+\n      kind: informed_by\n)", r"\1      rev: " + rev + "\n", t)
open(p, "w").write(t)
PY
  python3 "$pinner" check "$sc/$f" | grep -q "external" || fail "pin-sources should report cross-graph links as external"
done
git -C "$sc/client" add . && git -C "$sc/client" commit -q -m "pinned"
# The local DB-001 link is pinned from client history; cross-graph pins came from the atlas.
python3 "$pinner" pin "$sc/client/publications/DEL-001-test-publication.md" >/dev/null || fail "pin should succeed"
for f in client/decisions/DB-001-test-decision.md client/publications/DEL-001-test-publication.md; do
  python3 "$validator" "$sc/$f" --catalog "$repo_root/workflows" --tier publish >/dev/null || fail "pinned $f should validate at the publish tier"
done
# The atlas evolves; the approved publication still resolves its pinned sources.
printf '\nA later edit to the briefs.\n' >> "$sc/atlas/technology/nodejs.md"
git -C "$sc/atlas" commit -qam "briefs evolve"
git -C "$sc/atlas" show "${rev#git:}:technology/nodejs.md" | grep -q "later edit" && fail "pinned atlas revision must not contain the later edit"
git -C "$sc/atlas" show "${rev#git:}:technology/python.md" >/dev/null || fail "pinned atlas revision must resolve"
grep -q "rev: $rev" "$sc/client/publications/DEL-001-test-publication.md" || fail "publication must still carry the original pin"
echo "OK: scenario (Node.js vs Python)"

# Authority and contradictions (ADR-018, T5/T7): a profile that grants only
# advisory authority rejects a governing link; `contradicts` is informational.
authdoc() { # links-yaml
  printf -- '---\nddx:\n  id: DB-009\n  type: decision-brief\n  authoring:\n    home: repo\n  links:\n%s\n---\n\n# DB-009: Links\n' "$1"
}
authdoc '    - {id: A-1, kind: contradicts}' > "$tmp/knowledge/contradicts.md"
authdoc '    - {id: B-1, graph: other-atlas, kind: evaluates, authority: governing}' > "$tmp/knowledge/governing.md"
authdoc '    - {id: B-1, graph: other-atlas, kind: evaluates, authority: advisory}' > "$tmp/knowledge/advisory.md"
authdoc '    - {id: B-1, kind: evaluates, authority: governing}' > "$tmp/docs/helix/governing-in-flow.md"
python3 "$validator" "$tmp/knowledge/contradicts.md" --catalog "$repo_root/workflows" --format json | python3 -c 'import json,sys; d=json.load(sys.stdin); sys.exit(0 if d["summary"]["blocking"]==0 and any(f["check"].endswith("contradicts") and f["severity"]=="info" for f in d["findings"]) else 1)' \
  || fail "contradicts must be surfaced as info and never block"
python3 "$validator" "$tmp/knowledge/advisory.md" --catalog "$repo_root/workflows" >/dev/null || fail "an advisory cross-graph link should validate"
if python3 "$validator" "$tmp/knowledge/governing.md" --catalog "$repo_root/workflows" >/dev/null; then fail "a governing cross-graph link must fail under an advisory-only profile"; fi
{ python3 "$validator" "$tmp/docs/helix/governing-in-flow.md" --catalog "$repo_root/workflows" --format json || true; } | python3 -c 'import json,sys; d=json.load(sys.stdin); sys.exit(1 if any(f["check"].startswith("links.") and f["severity"]=="blocking" for f in d["findings"]) else 0)' \
  || fail "positional authority inside a software-delivery flow must be unchanged"
echo "OK: authority and contradictions"
