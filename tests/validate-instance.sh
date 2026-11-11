#!/usr/bin/env bash
# Exercise skills/helix/scripts/validate-instance.py against catalog examples
# (expect exit 0) and a deliberately broken PRD fixture (expect exit 1 with
# specific check ids).
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python3 "$repo_root/tests/test_document_history.py"
python3 "$repo_root/tests/test_living_documents.py"
validator="$repo_root/skills/helix/scripts/validate-instance.py"
fixtures="$repo_root/tests/fixtures/validate-instance"
tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

fail() { echo "FAIL: $*" >&2; exit 1; }

# Every catalog example must satisfy its own type's validation block and
# resolve to the type whose directory it lives in.
count=0
for path in "$repo_root"/workflows/activities/*/artifacts/*/example*.md; do
  type_id="$(basename "$(dirname "$path")")"
  rel="${path#"$repo_root"/workflows/activities/}"
  python3 "$validator" "$path" >"$tmpdir/out" 2>&1 \
    || fail "$rel should validate cleanly:
$(cat "$tmpdir/out")"
  grep -q "type=$type_id " "$tmpdir/out" \
    || fail "$rel should resolve to type $type_id:
$(cat "$tmpdir/out")"
  count=$((count + 1))
done
[ "$count" -ge 50 ] || fail "expected to validate every catalog example, ran $count"

# Optional UX sections: each fixture fills its type's optional sections and must validate.
ux=0
for path in "$fixtures"/ux/*.md; do
  type_id="$(basename "$path" .md)"
  python3 "$validator" "$path" --catalog "$repo_root/workflows" >"$tmpdir/out" 2>&1 \
    || fail "ux/$type_id.md should validate cleanly:
$(cat "$tmpdir/out")"
  grep -q "type=$type_id " "$tmpdir/out" || fail "ux/$type_id.md should resolve to type $type_id"
  ux=$((ux + 1))
done
[ "$ux" -eq 9 ] || fail "expected 9 optional-section fixtures, ran $ux"

# Broken PRD: missing required section, leftover placeholder, failed catalog regex.
if python3 "$validator" "$fixtures/broken-prd.md" --catalog "$repo_root/workflows" >"$tmpdir/broken.out" 2>&1; then
  fail "broken-prd.md should exit 1"
fi
for check in required_sections.success_criteria placeholder pattern_checks.0; do
  grep -Eq "^BLOCKING +$check " "$tmpdir/broken.out" \
    || fail "broken-prd.md output should contain blocking check '$check':
$(cat "$tmpdir/broken.out")"
done

# JSON output carries the same findings and a summary.
python3 - "$validator" "$fixtures/broken-prd.md" <<'PYEOF' || fail "json output shape is wrong"
import json, subprocess, sys
proc = subprocess.run([sys.executable, sys.argv[1], sys.argv[2], "--format", "json"], capture_output=True, text=True)
data = json.loads(proc.stdout)
assert proc.returncode == 1, proc.returncode
assert data["type"] == "prd" and data["catalog"] and data["instance"], data
checks = {f["check"] for f in data["findings"] if f["severity"] == "blocking"}
assert {"required_sections.success_criteria", "placeholder", "pattern_checks.0"} <= checks, checks
assert data["summary"]["blocking"] == len([f for f in data["findings"] if f["severity"] == "blocking"]) >= 3, data["summary"]
assert all(f["check"] == "placeholder" and f["line"] for f in data["findings"] if f["check"] == "placeholder"), "placeholder findings need a line"
PYEOF

# Unresolvable type is a usage error (exit 2), not a validation failure.
printf -- '---\nddx:\n  id: X-1\n  authoring:\n    home: repo\n---\n# untyped\n' >"$tmpdir/untyped.md"
if python3 "$validator" "$tmpdir/untyped.md" --catalog "$repo_root/workflows" >"$tmpdir/untyped.out" 2>&1; then
  fail "untyped instance should not validate"
fi
grep -q "could not resolve the artifact type" "$tmpdir/untyped.out" \
  || fail "untyped instance should report an unresolvable type"

# --type resolves it; the near-empty document then fails on required_sections.
python3 "$validator" "$tmpdir/untyped.md" --catalog "$repo_root/workflows" --type prd >"$tmpdir/typed.out" 2>&1 && \
  fail "--type prd on an empty document should still fail required_sections"
grep -q "type=prd " "$tmpdir/typed.out" || fail "--type should select the prd type"

# Prose audit (workflows/voice.yml limits and phrase lists; workflows/references/writing-pass.md).
# Artifacts are the system of record and are not audited; a deliverable is a projection people read,
# and its example meets its voice profile. Guide pages are checked by documentor
# (tests/validate-publish.sh).
audited=0
for path in "$repo_root"/workflows/activities/*/artifacts/*/example*.md; do
  grep -q "audience: human" "$(dirname "$path")/meta.yml" || continue
  audited=$((audited + 1))
  rel="${path#"$repo_root"/workflows/activities/}"
  python3 "$validator" "$path" --strict-prose >"$tmpdir/strict.out" 2>&1 \
    || fail "$rel should meet its voice profile's prose rules:
$(grep 'prose\.' "$tmpdir/strict.out")"
done
[ "$audited" -ge 1 ] || fail "expected the deliverable example to be audited, ran $audited"

# A breach is a warning by default and blocking with --strict-prose; a quoted phrase and a
# generated block are not read.
prose="$tmpdir/prose.md"
cp "$repo_root/workflows/activities/06-iterate/artifacts/deliverable/example.md" "$prose"
{
  printf '\nThis document serves as the guide, and her token is checked when the gateway and the store and the queue and the cache and the scheduler and the worker and the index all agree on the same request at the same time.\n'
  printf '\nWrite "is", not "serves as".\n'
  printf '\n<!-- architecture-view: context -->\nThis document serves as a generated block.\n<!-- /architecture-view -->\n'
} >>"$prose"
python3 "$validator" "$prose" --catalog "$repo_root/workflows" >"$tmpdir/prose.out" 2>&1 \
  || fail "prose findings should be warnings without --strict-prose:
$(cat "$tmpdir/prose.out")"
for check in prose.sentence; do
  grep -Eq "^WARNING +$check " "$tmpdir/prose.out" || fail "expected warning $check:
$(cat "$tmpdir/prose.out")"
done
for phrase in '"this document"' '"serves as"' '"her"'; do
  grep -F "prose.avoid  $phrase" "$tmpdir/prose.out" >/dev/null || fail "expected avoided phrase $phrase:
$(cat "$tmpdir/prose.out")"
done
[ "$(grep -cF 'prose.avoid  "serves as"' "$tmpdir/prose.out")" -eq 1 ] \
  || fail "a quoted phrase and a generated block must not be matched:
$(cat "$tmpdir/prose.out")"
if python3 "$validator" "$prose" --catalog "$repo_root/workflows" --strict-prose >"$tmpdir/strict.out" 2>&1; then
  fail "--strict-prose should make prose findings blocking"
fi
grep -Eq "^BLOCKING +prose\.sentence " "$tmpdir/strict.out" || fail "--strict-prose should report blocking prose.sentence"

# An agent-read type (an ADR) is not audited; a project's .helix.yml can make findings blocking and
# list paths to skip.
project="$tmpdir/project"
mkdir -p "$project/docs/helix/02-design/adr" "$project/docs/helix/04-build"
decided="$project/docs/helix/02-design/adr/ADR-900-decided.md"
sed 's/^  id: \(.*\)$/  id: \1\
  status: accepted/' "$repo_root/workflows/activities/02-design/artifacts/adr/example.md" >"$decided"
grep -q "^  status: accepted$" "$decided" || fail "test setup: could not mark the ADR accepted"
printf '\nThis document serves as a record that is decided and will not be rewritten by anyone at all for any reason whatsoever in any case.\n' >>"$decided"
python3 "$validator" "$decided" --catalog "$repo_root/workflows" --strict-prose >"$tmpdir/decided.out" 2>&1 \
  || fail "an agent-read type should not be audited:
$(cat "$tmpdir/decided.out")"
grep -q "prose\." "$tmpdir/decided.out" && fail "an agent-read type produced prose findings"
cp "$prose" "$project/docs/helix/02-design/overview.md"
printf 'prose:\n  strict: true\n  exempt:\n    - "docs/helix/04-build/*"\n' >"$project/.helix.yml"
if python3 "$validator" "$project/docs/helix/02-design/overview.md" --catalog "$repo_root/workflows" --type deliverable >"$tmpdir/project.out" 2>&1; then
  fail ".helix.yml prose.strict should make findings blocking"
fi
cp "$prose" "$project/docs/helix/04-build/log.md"
python3 "$validator" "$project/docs/helix/04-build/log.md" --catalog "$repo_root/workflows" --type deliverable >"$tmpdir/exempt.out" 2>&1
grep -q "prose\." "$tmpdir/exempt.out" && fail "a path listed in .helix.yml prose.exempt should not be audited"

# Visual blocks (workflows/references/visuals.md): a well-formed block and a source reference pass; a
# missing or repeated id, a form outside its kind, and a missing question block; a kind and form the
# type does not list warn.
visuals="$tmpdir/ADR-901-visuals.md"
cp "$repo_root/workflows/activities/02-design/artifacts/adr/example.md" "$visuals"
cat >>"$visuals" <<'MD'

```visual id=store-options
kind: comparison
form: matrix
question: Which store holds the session, and why?
```

```visual id=store-from-model
source: architecture-model.toml#deployment
```

```mermaid
%% id: store-context
flowchart LR
  a --> b
```
MD
python3 "$validator" "$visuals" --catalog "$repo_root/workflows" >"$tmpdir/visuals.out" 2>&1 \
  || fail "well-formed visual blocks should pass:
$(cat "$tmpdir/visuals.out")"
grep -q "visual\." "$tmpdir/visuals.out" && fail "well-formed visual blocks produced findings:
$(cat "$tmpdir/visuals.out")"
# Literal samples inside an outer fence (longer backticks or tildes) are text, not visuals: a repeated
# or invalid sample beside the real figures above passes.
literal="$tmpdir/ADR-902-literal.md"
cp "$visuals" "$literal"
cat >>"$literal" <<'MD'

````markdown
```visual id=example
kind: comparison
form: matrix
question: Which store?
```
````

````markdown
```visual id=example
kind: flow
form: matrix
```
````

~~~markdown
```visual id=store-options
kind: comparison
form: matrix
question: Which store?
```

```mermaid
%% id: store-context
flowchart LR
  a --> b
```
~~~
MD
python3 "$validator" "$literal" --catalog "$repo_root/workflows" >"$tmpdir/literal.out" 2>&1 \
  || fail "literal visual samples inside an outer fence should pass:
$(cat "$tmpdir/literal.out")"
grep -q "visual\." "$tmpdir/literal.out" && fail "literal visual samples inside an outer fence produced findings:
$(cat "$tmpdir/literal.out")"
cat >>"$visuals" <<'MD'

```visual
kind: flow
form: network
question: What connects?
```

```visual id=store-options
kind: flow
form: matrix
question: What connects?
```

```visual id=Bad_Id
kind: state
form: machine
```

```visual id=unlisted-flow
kind: flow
form: network
question: What does the store touch?
```

```mermaid
%% id: store-context
flowchart LR
  c --> d
```
MD
if python3 "$validator" "$visuals" --catalog "$repo_root/workflows" >"$tmpdir/visuals.out" 2>&1; then
  fail "malformed visual blocks should block"
fi
for expected in "BLOCKING +visual\.id .*needs .id=" "BLOCKING +visual\.id .*'store-options' is used twice" \
                "BLOCKING +visual\.form .*flow has the forms" "BLOCKING +visual\.id .*'Bad_Id'" \
                "BLOCKING +visual\.question " "WARNING +visual\.unlisted .*flow/network" \
                "BLOCKING +visual\.id .*'store-context' is used twice"; do
  grep -Eq "$expected" "$tmpdir/visuals.out" || fail "expected /$expected/:
$(cat "$tmpdir/visuals.out")"
done

# Structured blocks: an assessment's `assessment:` and a paper's `recommendations:` are checked for
# shape, and assessment-tables.py keeps the Markdown tables equal to them.
tables="$repo_root/skills/helix/scripts/assessment-tables.py"
sb="$tmpdir/structured"
mkdir -p "$sb"
cp "$repo_root/workflows/activities/00-discover/artifacts/criteria.yml" "$sb/"
ta_src="$repo_root/workflows/activities/00-discover/artifacts/technology-assessment/example.md"
pp_src="$repo_root/workflows/activities/00-discover/artifacts/position-paper/example.md"
cp "$ta_src" "$sb/TA-001.md"  # the assessment the paper's weights are checked against
expect_block() {  # file, sed expression, expected finding regex
  local file="$sb/case.md" src="$1"; shift
  sed "$1" "$src" >"$file"
  if python3 "$validator" "$file" --catalog "$repo_root/workflows" ${TIER:-} >"$tmpdir/case.out" 2>&1; then
    fail "structured case /$1/ should block:
$(cat "$tmpdir/case.out")"
  fi
  ! grep -q Traceback "$tmpdir/case.out" || fail "structured case /$1/ crashed instead of reporting:
$(cat "$tmpdir/case.out")"
  grep -Eq "$2" "$tmpdir/case.out" || fail "structured case /$1/ should report /$2/:
$(cat "$tmpdir/case.out")"
}
expect_block "$ta_src" '/subject: component-profile-python-reusable, finding: Brief section Capabilities/d' "BLOCKING +assessment\.ratings .*no rating or gap"
expect_block "$ta_src" 's/criteria: \[script-distribution, text-and-file-handling, dependency-isolation\]/criteria: [script-distribution, text-and-file-handling, speed]/' "BLOCKING +assessment\.criteria .*'speed' is not in criteria.yml"
expect_block "$ta_src" 's/- {id: component-profile-python-reusable, label: Python}/- {id: component-profile-go-reusable, label: Go}/' "BLOCKING +assessment\.subjects .*'component-profile-go-reusable' is not linked"
expect_block "$ta_src" 's/gap: Unknown (not in the brief)}$/gap: Unknown, finding: Both}/' "BLOCKING +assessment\.ratings\.[0-9]+ .*exactly one of"
expect_block "$pp_src" 's/stance: conditional/stance: favourite/' "BLOCKING +recommendations\.0 .*stance must be one of"
expect_block "$pp_src" 's/    review_by: 2027-02-06/    review_by: 2026-01-01/' "BLOCKING +recommendations\.0 .*review_by. is after"
expect_block "$pp_src" 's/    since: 2026-11-06/    since: 2026-11-06\n    approved_by: Someone/' "BLOCKING +recommendations\.0 .*together or not at all"
expect_block "$pp_src" 's/, kind: supported_by, rev: example}$/, kind: informed_by, rev: example}/' "BLOCKING +recommendations\.0 .*linked as supported_by"
expect_block "$pp_src" '/    conditions: /d' "BLOCKING +recommendations\.0 .*conditional stance states its conditions"
# a stance outside a position paper, and a criteria block outside an assessment
expect_block "$ta_src" 's/^assessment:/recommendations: []\nassessment:/' "BLOCKING +recommendations\.placement "
expect_block "$pp_src" 's/^recommendations:/assessment: {}\nrecommendations:/' "BLOCKING +assessment\.placement "

# Weights: a paper says how much a criterion counts on a three-step scale, only for a criterion a
# supported_by assessment has a finding for. A weight is a judgement, so an assessment and
# criteria.yml may not carry one. Limits of the Position holds the table of when the other option wins.
expect_block "$pp_src" 's/    weight: decisive/    weight: 5/' "BLOCKING +weights\.0 .*one of decisive, important, minor"
expect_block "$pp_src" 's/  - criterion: dependency-isolation/  - criterion: speed/' "BLOCKING +weights\.1 .*'speed' is not in criteria.yml"
expect_block "$pp_src" 's/  - criterion: dependency-isolation/  - criterion: script-distribution/' "BLOCKING +weights\.1 .*has a finding for 'script-distribution'"
expect_block "$pp_src" 's/  - criterion: dependency-isolation/  - criterion: text-and-file-handling/' "BLOCKING +weights\.1 .*weighted twice"
expect_block "$pp_src" '/    reason: Tooling scripts here/d' "BLOCKING +weights\.1 .*reason. in one line"
expect_block "$pp_src" 's/^weights:$/weights: []\nunused:/' "BLOCKING +weights\.shape "
expect_block "$pp_src" 's/- {id: TA-001, kind: supported_by, rev: example}/- {id: TA-001, kind: evaluates, rev: example}/' "BLOCKING +weights\.0 .*no assessment linked as supported_by has a finding"
expect_block "$ta_src" 's/^assessment:/weights: []\nassessment:/' "BLOCKING +weights\.placement "
expect_block "$ta_src" 's/^  ratings:$/  weights: []\n  ratings:/' "BLOCKING +assessment\.weights "
expect_block "$ta_src" 's/finding: Brief section Technology and Operations}$/finding: Brief section Technology and Operations, weight: decisive}/' "BLOCKING +assessment\.weights "
printf '    weight: decisive\n' >>"$sb/criteria.yml"
expect_block "$pp_src" 's/^$/&/' "BLOCKING +catalogue .*'dependency-isolation' carries a weight"
cp "$repo_root/workflows/activities/00-discover/artifacts/criteria.yml" "$sb/"
expect_block "$pp_src" 's/^| Condition | Option that wins | Evidence |$/| Condition | Evidence |/' "BLOCKING +limits_table "
sed '/^recommendations:$/,/^weights:$/{/^weights:$/!d;}' "$pp_src" >"$sb/weightsonly.md"
grep -q '^recommendations:' "$sb/weightsonly.md" && fail "test setup: recommendations were not removed"
python3 "$tables" "$sb/weightsonly.md" >"$tmpdir/tables.out" 2>&1 || fail "a paper with weights and no recommendations should generate its Decision Criteria table:
$(cat "$tmpdir/tables.out")"
sed 's/^| Dependency isolation | Minor |/| Dependency isolation | Decisive |/' "$pp_src" >"$sb/wdrift.md"
if python3 "$tables" "$sb/wdrift.md" >"$tmpdir/tables.out" 2>&1; then fail "a drifted Decision Criteria table should fail assessment-tables.py"; fi
python3 "$tables" --write "$sb/wdrift.md" >/dev/null && cmp -s "$sb/wdrift.md" "$pp_src" \
  || fail "assessment-tables.py --write should restore the Decision Criteria table"
rm -f "$sb/weightsonly.md" "$sb/wdrift.md"

# Views: with a views.yml beside criteria.yml, a criterion's `view:` must name a view in it; one id
# or a list. Without views.yml a `view:` is not checked.
sed 's/^    concern: none$/    concern: none\n    view: finance/' "$repo_root/workflows/activities/00-discover/artifacts/criteria.yml" >"$sb/criteria.yml"
python3 "$validator" "$sb/TA-001.md" --catalog "$repo_root/workflows" >/dev/null 2>&1 || fail "a view: without views.yml should not be checked"
printf 'views:\n  - {id: finance, label: Finance}\n  - {id: apps-dev, label: Apps Dev}\n' >"$sb/views.yml"
python3 "$validator" "$sb/TA-001.md" --catalog "$repo_root/workflows" >"$tmpdir/case.out" 2>&1 || fail "a view named in views.yml should validate:
$(cat "$tmpdir/case.out")"
sed -i.bak 's/^    view: finance$/    view: [finance, apps-dev]/' "$sb/criteria.yml"
python3 "$validator" "$sb/TA-001.md" --catalog "$repo_root/workflows" >/dev/null 2>&1 || fail "a list of views named in views.yml should validate"
printf 'views:\n  - {id: apps-dev, label: Apps Dev}\n' >"$sb/views.yml"
expect_block "$ta_src" 's/^$/&/' "BLOCKING +catalogue .*names view 'finance', which is not in views.yml"
printf 'views:\n  - apps-dev\n' >"$sb/views.yml"
expect_block "$ta_src" 's/^$/&/' "BLOCKING +catalogue .*views.yml needs a .views:. list"
rm -f "$sb/views.yml" "$sb/criteria.yml.bak"
cp "$repo_root/workflows/activities/00-discover/artifacts/criteria.yml" "$sb/"

# Malformed shapes are findings, never tracebacks; the table tool refuses a malformed block.
expect_block "$ta_src" 's/^  subjects:$/  subjects:\n    - nodejs/' "BLOCKING +assessment\.shape .*subjects"
expect_block "$ta_src" 's/^  criteria: \[.*\]$/  criteria: 5/' "BLOCKING +assessment\.shape .*criteria"
expect_block "$ta_src" 's/^  criteria: \[.*\]$/  criteria: script-distribution/' "BLOCKING +assessment\.shape .*criteria"
expect_block "$ta_src" 's/^assessment:$/assessment:\n  comparison: [x]/' "BLOCKING +assessment\.shape .*comparison"
expect_block "$ta_src" 's/- {id: component-profile-python-reusable, label: Python}/- {id: component-profile-nodejs-reusable, label: Node.js}/' "BLOCKING +assessment\.subjects .*listed twice"
expect_block "$ta_src" 's/    - {id: component-profile-nodejs-reusable, kind: evaluates, rev: example}/    - {kind: evaluates}/' "BLOCKING +assessment\.subjects "
expect_block "$ta_src" 's/finding: Brief section Capabilities}$/finding: "two\\n\\nlines"}/' "BLOCKING +assessment\.ratings\.[0-9]+ .*one line"
expect_block "$pp_src" 's/subject: component-profile-python-reusable/subject: [a]/' "BLOCKING +recommendations\.0 .*string .subject"
expect_block "$pp_src" 's/stance: conditional/stance: [a]/' "BLOCKING +recommendations\.0 .*stance must be one of"
expect_block "$pp_src" 's/based_on: \[{assessment: TA-001, criteria: \[text-and-file-handling\]}\]/based_on: [TA-001]/' "BLOCKING +recommendations\.0 .*linked as supported_by"
expect_block "$pp_src" 's/    since: 2026-11-06/    since: 20261106/' "BLOCKING +recommendations\.0 .*YYYY-MM-DD"
# Pins are required at the publish tier only; cited criteria need a catalogue.
cp "$pp_src" "$sb/pinless.md"; sed -i.bak 's/- {id: TA-001, kind: supported_by, rev: example}/- {id: TA-001, kind: supported_by}/' "$sb/pinless.md"
python3 "$validator" "$sb/pinless.md" --catalog "$repo_root/workflows" >/dev/null 2>&1 || fail "a paper without a pin should validate at the default tier"
TIER="--tier publish" expect_block "$sb/pinless.md" 's/^$/&/' "BLOCKING +recommendations\.0 .*needs a pinned rev"
nocat="$tmpdir/nocatalogue"; mkdir -p "$nocat"; touch "$nocat/.helix.yml"; cp "$pp_src" "$nocat/PP-001.md"
python3 "$validator" "$nocat/PP-001.md" --catalog "$repo_root/workflows" >"$tmpdir/case.out" 2>&1 && fail "cited criteria without criteria.yml should block"
grep -Eq "BLOCKING +recommendations\.0 .*does not have" "$tmpdir/case.out" || fail "expected the missing-catalogue finding:
$(cat "$tmpdir/case.out")"
# A catalogue entry without a label is a finding, not a KeyError in the table tool.
printf 'criteria:\n  - id: script-distribution\n' >"$sb/criteria.yml"
expect_block "$ta_src" 's/^$/&/' "BLOCKING +catalogue .*string .id. and .label"
if python3 "$tables" "$ta_src" >"$tmpdir/tables.out" 2>&1; then :; fi
cp "$repo_root/workflows/activities/00-discover/artifacts/criteria.yml" "$sb/"

# A pipe in a finding is escaped on write and the table stays well formed.
sed 's/finding: Brief section Capabilities}$/finding: "a | b"}/' "$ta_src" >"$sb/pipe.md"
python3 "$tables" --write "$sb/pipe.md" >/dev/null || fail "writing a finding with a pipe should succeed"
grep -Fq '| Text and file handling | a \| b | a \| b |' "$sb/pipe.md" || fail "a pipe in a finding should be escaped in the table:
$(grep -n 'Text and file' "$sb/pipe.md")"
python3 "$tables" "$sb/pipe.md" >/dev/null || fail "a table with an escaped pipe should check clean"
python3 "$validator" "$sb/pipe.md" --catalog "$repo_root/workflows" >/dev/null || fail "a finding with a pipe should validate"

# Generated tables: current examples pass; a drifted cell fails the check; --write repairs it.
python3 "$tables" "$ta_src" "$pp_src" >"$tmpdir/tables.out" 2>&1 || fail "catalog examples' tables should match their blocks:
$(cat "$tmpdir/tables.out")"
sed 's/^| Script distribution | Unknown (not in the brief) | Unknown/| Script distribution | Fine | Unknown/' "$ta_src" >"$sb/drift.md"
if python3 "$tables" "$sb/drift.md" >"$tmpdir/tables.out" 2>&1; then fail "a drifted table should fail assessment-tables.py"; fi
grep -q "FAIL" "$tmpdir/tables.out" || fail "a drifted table should report FAIL"
python3 "$tables" --write "$sb/drift.md" >/dev/null && cmp -s "$sb/drift.md" "$ta_src" \
  || fail "assessment-tables.py --write should restore the generated table"

# Keys: a short name in a block stands for a document id; ddx.links keep full ids and pins, and the
# document records what each key resolved to, so repointing a key is never a silent change.
printf 'keys:\n  nodejs: component-profile-nodejs-reusable\n  python: component-profile-python-reusable\n' >"$sb/keys.yml"
sed -e 's/^    - {id: component-profile-nodejs-reusable, label: Node.js}/    - {id: nodejs, label: Node.js}/' \
    -e 's/^    - {id: component-profile-python-reusable, label: Python}/    - {id: python, label: Python}/' \
    -e 's/subject: component-profile-nodejs-reusable,/subject: nodejs,/' \
    -e 's/subject: component-profile-python-reusable,/subject: python,/' \
    -e 's/^assessment:/keys:\n  nodejs: component-profile-nodejs-reusable\n  python: component-profile-python-reusable\nassessment:/' "$ta_src" >"$sb/keyed.md"
grep -q 'id: nodejs, label' "$sb/keyed.md" && grep -q 'subject: python,' "$sb/keyed.md" || fail "test setup: keys were not substituted"
python3 "$validator" "$sb/keyed.md" --catalog "$repo_root/workflows" >"$tmpdir/case.out" 2>&1 || fail "a keyed assessment should validate:
$(cat "$tmpdir/case.out")"
python3 "$tables" "$sb/keyed.md" >/dev/null || fail "a keyed assessment should generate the same tables as the full-id one"
sed -e 's/^    - {id: nodejs, label: Node.js}/    - {id: nodejs-unknown, label: Node.js}/' "$sb/keyed.md" >"$sb/case.md"
python3 "$validator" "$sb/case.md" --catalog "$repo_root/workflows" >"$tmpdir/case.out" 2>&1 && fail "an unknown key is taken as an id and must be linked"
grep -Eq "BLOCKING +assessment\.subjects .*'nodejs-unknown' is not linked" "$tmpdir/case.out" || fail "an unknown key should read as an unlinked id:
$(cat "$tmpdir/case.out")"
expect_block "$sb/keyed.md" 's/^    - {id: component-profile-python-reusable, kind: evaluates, rev: example}/    - {id: python, kind: evaluates, rev: example}\n    - {id: component-profile-python-reusable, kind: supported_by, rev: example}/' "BLOCKING +keys .*both a key in keys.yml and a linked document id"
# Repointing a key is caught in every document that used it; a document must record what it used.
printf 'keys:\n  nodejs: component-profile-python-reusable\n  python: component-profile-nodejs-reusable\n' >"$sb/keys.yml"
expect_block "$sb/keyed.md" 's/^$/&/' "BLOCKING +keys .*key 'nodejs' resolves to 'component-profile-python-reusable' in keys.yml, but this document records 'component-profile-nodejs-reusable'"
printf 'keys:\n  nodejs: component-profile-nodejs-reusable\n  python: component-profile-python-reusable\n' >"$sb/keys.yml"
expect_block "$sb/keyed.md" '/^  python: component-profile-python-reusable$/d' "BLOCKING +keys .*key 'python' resolves to .* records None"
expect_block "$sb/keyed.md" 's/^  python: component-profile-python-reusable$/  python: component-profile-python-reusable\n  old: component-profile-go-reusable/' "BLOCKING +keys .*records key 'old', which keys.yml no longer defines"
# keys.yml itself: a repeated key, a key that is a document id, a boolean-looking key, a bad shape.
printf 'keys:\n  nodejs: component-profile-nodejs-reusable\n  nodejs: component-profile-python-reusable\n' >"$sb/keys.yml"
expect_block "$sb/keyed.md" 's/^$/&/' "BLOCKING +keys .*duplicate key 'nodejs'"
printf -- '---\nddx:\n  id: some-doc-id\n---\nstub\n' >"$sb/stub.md"
printf 'keys:\n  some-doc-id: component-profile-nodejs-reusable\n' >"$sb/keys.yml"
expect_block "$sb/keyed.md" 's/^$/&/' "BLOCKING +keys .*key 'some-doc-id' is also a document id"
rm "$sb/stub.md"
printf 'keys:\n  no: component-profile-nodejs-reusable\n' >"$sb/keys.yml"
expect_block "$sb/keyed.md" 's/^$/&/' "BLOCKING +keys .*bare yes, no, on or off as a boolean"
printf 'keys: [a]\n' >"$sb/keys.yml"
expect_block "$sb/keyed.md" 's/^$/&/' "BLOCKING +keys .*needs a .keys:. mapping"
# ...but a malformed keys.yml does not block a document that has no block.
cp "$repo_root/workflows/activities/01-frame/artifacts/prd/example.md" "$sb/prd.md"
python3 "$validator" "$sb/prd.md" --catalog "$repo_root/workflows" >"$tmpdir/case.out" 2>&1 || fail "a bad keys.yml should not block a document without a block:
$(cat "$tmpdir/case.out")"
# A position paper uses keys the same way, for its subject and its based_on assessment.
printf 'keys:\n  python: component-profile-python-reusable\n  ta1: TA-001\n' >"$sb/keys.yml"
sed -e 's/subject: component-profile-python-reusable/subject: python/' \
    -e 's/based_on: \[{assessment: TA-001,/based_on: [{assessment: ta1,/' \
    -e 's/^recommendations:/keys:\n  python: component-profile-python-reusable\n  ta1: TA-001\nrecommendations:/' "$pp_src" >"$sb/ppkeyed.md"
grep -q 'assessment: ta1' "$sb/ppkeyed.md" || fail "test setup: paper keys were not substituted"
python3 "$validator" "$sb/ppkeyed.md" --catalog "$repo_root/workflows" >"$tmpdir/case.out" 2>&1 || fail "a keyed position paper should validate:
$(cat "$tmpdir/case.out")"
python3 "$tables" "$sb/ppkeyed.md" >/dev/null || fail "a keyed position paper should generate the same table"
rm -f "$sb/keys.yml" "$sb/ppkeyed.md" "$sb/keyed.md"

# Figure attributes: {basis=... accessed=... source=...} is checked wherever it appears; code is not.
fig() {  # text placed after the Findings heading (\n = newline), expected regex (empty = must pass)
  sed "s|^## Findings\$|## Findings\n\n$1|" "$ta_src" >"$sb/fig.md"
  if [ -z "$2" ]; then
    python3 "$validator" "$sb/fig.md" --catalog "$repo_root/workflows" >"$tmpdir/case.out" 2>&1 || fail "figure /$1/ should pass:
$(cat "$tmpdir/case.out")"
  else
    if python3 "$validator" "$sb/fig.md" --catalog "$repo_root/workflows" >"$tmpdir/case.out" 2>&1; then fail "figure /$1/ should block"; fi
    grep -Eq "$2" "$tmpdir/case.out" || fail "figure /$1/ should report /$2/:
$(cat "$tmpdir/case.out")"
  fi
}
fig 'Five years. {basis=published accessed=2026-11-06 source="postgresql.org/support"}' ""
fig 'Not stated. {basis=not-published}' ""
fig 'Syntax is `{basis=wrong}` in code and {keys=pg role=evaluates} elsewhere.' ""
fig 'Double ``{basis=wrong}`` backticks, and a path {basis=published accessed=2026-11-06 source="api/{id}/x"}.' ""
fig 'A brace in a value. {basis=published accessed=2026-11-06 source="}price"}' ""
fig 'Spaced. {Basis = published  ACCESSED = 2026-11-06 source = x}' ""
fig 'Wrapped. {basis=published\n  accessed=2026-11-06\n  source=x}' ""
fig 'Docs:\n\n~~~\n{basis=wrong}\n~~~' ""
fig 'Docs:\n\n````markdown\n```\n{basis=wrong}\n```\n````' ""
fig '<!-- {basis=wrong} -->' ""
fig 'See [the page](https://x.example/a "{basis=wrong}").' ""
fig 'Five years. {basis=guess accessed=2026-11-06 source=x}' "BLOCKING +figure\.basis "
fig 'Five years. {BASIS=guess accessed=2026-11-06 source=x}' "BLOCKING +figure\.basis "
fig 'Five years. {basis=published, accessed=2026-11-06 source=x}' "BLOCKING +figure\.basis .*without punctuation"
fig 'Five years. {basis=third-party accessed=2026-11-06}' "BLOCKING +figure\.source "
fig 'Five years. {basis=published source=x}' "BLOCKING +figure\.accessed "
fig 'Five years. {basis=published accessed=2026-13-45 source=x}' "BLOCKING +figure\.accessed .*not a YYYY-MM-DD"
fig 'Five years. {accessed=2026-11-06}' "BLOCKING +figure\.basis "
fig 'Wrapped. {basis=guess\n  accessed=2026-11-06 source=x}' "BLOCKING +figure\.basis "
fig 'Twice. {basis=guess basis=published accessed=2026-11-06 source=x}' "BLOCKING +figure\.duplicate .*basis"
fig 'Quoted brace. {basis=guess source="api/{id}" accessed=2026-11-06}' "BLOCKING +figure\.basis "
# The finding points at the line the attribute list is on.
fig 'Five years. {basis=guess accessed=2026-11-06 source=x}' "BLOCKING +figure\.basis "
want="$(grep -n 'basis=guess' "$sb/fig.md" | head -1 | cut -d: -f1)"
grep -Eq "figure\.basis .*\[line $want\]" "$tmpdir/case.out" || fail "figure finding should be on line $want:
$(cat "$tmpdir/case.out")"
# Under a profile that validates structure only by default, a figure finding is a warning until
# --tier publish, when it blocks.
proj="$tmpdir/atlasproj"; mkdir -p "$proj/knowledge"
printf 'flows:\n  - id: atlas\n    profile: technology-atlas\n    root: knowledge/\n' >"$proj/.helix.yml"
cp "$repo_root/workflows/activities/00-discover/artifacts/criteria.yml" "$proj/knowledge/"
sed -e 's|^## Findings$|## Findings\n\nFive years. {basis=guess accessed=2026-11-06 source=x}|' "$ta_src" >"$proj/knowledge/TA-001.md"
python3 "$validator" "$proj/knowledge/TA-001.md" --catalog "$repo_root/workflows" >"$tmpdir/case.out" 2>&1 \
  && grep -Eq "^WARNING +figure\.basis " "$tmpdir/case.out" || fail "a figure finding should be a warning at the default tier:
$(cat "$tmpdir/case.out")"
if python3 "$validator" "$proj/knowledge/TA-001.md" --catalog "$repo_root/workflows" --tier publish >"$tmpdir/case.out" 2>&1; then
  fail "a figure finding should block at the publish tier"
fi
grep -Eq "^BLOCKING +figure\.basis " "$tmpdir/case.out" || fail "expected a blocking figure.basis at the publish tier:
$(cat "$tmpdir/case.out")"

# Reader views: a reusable brief closes with a Views section of four headings. A brief with none
# predates the section and only warns, at either tier, so it still publishes; a Views section that
# drops or empties a heading blocks.
brief_src="$repo_root/workflows/activities/00-discover/artifacts/component-profile/example-reusable.md"
awk '/^## Views$/{skip=1} /^## Confidence$/{skip=0} !skip' "$brief_src" >"$sb/noviews.md"
grep -q '^## Views$' "$sb/noviews.md" && fail "test setup: the Views section was not removed"
for tier in default publish; do
  python3 "$validator" "$sb/noviews.md" --catalog "$repo_root/workflows" --tier "$tier" >"$tmpdir/case.out" 2>&1 \
    && grep -Eq "^WARNING +views .*no Views section" "$tmpdir/case.out" || fail "a brief with no Views section should warn and pass at the $tier tier:
$(cat "$tmpdir/case.out")"
done
expect_block "$brief_src" 's/^### Finance$/### Money/' "BLOCKING +views .*no .### Finance. heading"
awk '/^### Apps Dev$/{print; skip=1; next} /^## Confidence$/{skip=0} !skip' "$brief_src" >"$sb/emptyview.md"
expect_block "$sb/emptyview.md" 's/^$/&/' "BLOCKING +views .*### Apps Dev. is empty"
sed 's/^### Finance$/### Money/' "$brief_src" >"$proj/knowledge/brief.md"
python3 "$validator" "$proj/knowledge/brief.md" --catalog "$repo_root/workflows" >"$tmpdir/case.out" 2>&1 \
  && grep -Eq "^WARNING +views .*Finance" "$tmpdir/case.out" || fail "a malformed Views section should be a warning at an atlas flow's default tier:
$(cat "$tmpdir/case.out")"

echo "OK: validate-instance.py passes all $count catalog examples and $ux optional-section fixtures, holds the deliverable to its voice profile, rejects the broken PRD fixture, checks visual blocks and structured assessment, recommendation and weight blocks, keys, figure attributes, and reader views, and errors on unresolvable types"
