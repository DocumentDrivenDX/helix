#!/usr/bin/env bash
# Keep HELIX's ported title rules in sync with sloptimizer's headline rules.
#
# 1. Every case in the vendored fixture must get the same rule set from
#    check-deliverable.py's title_slop() that sloptimizer expects.
# 2. When the sloptimizer source is present on this machine, the vendored
#    fixture must match it byte for byte; otherwise re-sync (see .SOURCE).
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fixture="$repo_root/tests/fixtures/validate-deliverable/headline-cases.json"
source_note="$repo_root/tests/fixtures/validate-deliverable/headline-cases.SOURCE"
fail() { printf 'headline sync failed: %s\n' "$*" >&2; exit 1; }
[[ -f "$fixture" && -f "$source_note" ]] || fail "vendored fixture or .SOURCE note missing"

python3 - "$repo_root/skills/helix/scripts/check-deliverable.py" "$fixture" <<'PYEOF' || fail "title_slop() disagrees with sloptimizer's headline fixtures"
import importlib.util, json, sys
spec = importlib.util.spec_from_file_location("cd", sys.argv[1])
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
RULES = {"contrastive reversal": "ContrastiveReversal", "colon list": "ColonList", "colon reveal": "ColonReveal",
         "imperative chain": "ImperativeChain", "listicle count": "Listicle", "stacked negation": "StackedNegation",
         "rule-of-three list": "Triplet", "flattery": "Flattery", "pseudo-aphorism": "Aphorism",
         "universal claim": "UniversalClaim", "over-length": "Length", "mannered phrase": "Mannered",
         "inventory count": "InventoryCount", "hedge": "Hedge", "container title": "ContainerTitle",
         "self-justifying": "SelfJustifying", "shouting label": "ShoutingLabel", "invented status": "StatusJargon",
         "taxonomy code": "Taxonomy", "marketing register": "Marketing", "trailing commentary": "TrailingCommentary"}
def rules_for(title, mode):
    out = set()
    msgs = (mod.title_slop(title) if mode == "headline" else
            mod.title_slop(title, slide=True) if mode == "slide-title" else mod.shape_slop(title))
    for msg in msgs:
        for prefix, name in RULES.items():
            if msg.startswith(prefix):
                out.add(name); break
        else:
            out.add("?" + msg[:30])
    return out
# document-mode cases (headings, all-lines, slide) test sloptimizer's CLI layout, not the rules
cases = [c for c in json.load(open(sys.argv[2], encoding="utf-8")) if c.get("mode", "headline") in ("headline", "slide-title", "shape")]
bad = []
for c in cases:
    got, want = rules_for(c["headline"], c.get("mode", "headline")), set(c.get("expected_rules", []))
    if got != want:
        bad.append(f"  {c['name']}: expected {sorted(want)} got {sorted(got)}  <- {c['headline']!r}")
print(f"checked {len(cases)} headline cases")
if bad:
    print("\n".join(bad), file=sys.stderr); sys.exit(1)
PYEOF

upstream=""
for cand in "$HOME/Projects/easel-skills/skills/sloptimizer/tests/fixtures/headline-cases.json" \
            "$HOME"/.claude/plugins/cache/easel/sloptimizer/*/skills/sloptimizer/tests/fixtures/headline-cases.json; do
  [[ -f "$cand" ]] && { upstream="$cand"; break; }
done
if [[ -n "$upstream" ]]; then
  if ! cmp -s "$upstream" "$fixture"; then
    fail "vendored headline-cases.json differs from $upstream; copy it over, update .SOURCE, and make title_slop agree"
  fi
  echo "vendored fixture matches upstream: $upstream"
  styles="$(dirname "$upstream")/../../assets/vale/styles"
  for pair in "_MANNERED:Sloptimizer/ManneredProse.yml" "_STATUS_JARGON:SloptimizerExternal/StatusJargon.yml" \
              "_TAXONOMY:SloptimizerExternal/InternalTaxonomy.yml" "_MARKETING:SloptimizerExternal/MarketingRegister.yml"; do
    attr="${pair%%:*}"; yml="$styles/${pair#*:}"
    [[ -f "$yml" ]] || continue
    python3 - "$repo_root/skills/helix/scripts/check-deliverable.py" "$yml" "$attr" <<'PYEOF' || fail "$attr in check-deliverable.py differs from sloptimizer's ${pair#*:} tokens; re-vendor the list"
import importlib.util, sys
spec = importlib.util.spec_from_file_location("cd", sys.argv[1]); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
tokens, intok = [], False
for raw in open(sys.argv[2], encoding="utf-8").read().splitlines():
    line = raw.strip()
    if not raw.startswith((" ", "-")) and line.endswith(":"):
        intok = line == "tokens:"; continue
    if intok and line.startswith("- "):
        t = line[2:].strip()
        if t[0] == t[-1] and t[0] in "'\"":
            t = t[1:-1].replace("''", "'") if t[0] == "'" else t[1:-1]
        tokens.append(t)
port = list(getattr(mod, sys.argv[3]))
if port != tokens:
    print(f"{sys.argv[3]}: port has {len(port)} tokens, upstream has {len(tokens)}", file=sys.stderr); sys.exit(1)
print(f"{sys.argv[3]} matches upstream ({len(tokens)} tokens)")
PYEOF
  done
else
  echo "sloptimizer source not present; skipped byte comparison (see $(basename "$source_note"))"
fi
echo "OK: HELIX title rules agree with sloptimizer's headline fixtures"
