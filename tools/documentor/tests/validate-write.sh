#!/usr/bin/env bash
# Exercise `documentor write` and `build --write` (ADR-003) with a fake agent: written pages are
# stamped, checked, and evaluated by another model; a rerun calls nothing; a bad first answer is
# revised; a failed evaluation leaves the page unreviewed; gaps reach `status`; the writer cannot
# review its own page; a stale page is revised with the sources that moved.
set -euo pipefail

rg="${DOCUMENTOR:-documentor}"
command -v "$rg" >/dev/null 2>&1 || { echo "FAIL: documentor is not on PATH; run the tests with uv (just test)"; exit 1; }
tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT
fail() { echo "FAIL: $*" >&2; exit 1; }

# The fake agent: `fake.py MODEL` answers a writer prompt with a page and an evaluator prompt with a
# verdict; it logs each call as "MODEL KIND PATH [moved]". FAKE_MODE=badfirst cites a missing file
# until it is given feedback; FAKE_MODE=reject fails every evaluation.
cat >"$tmpdir/fake.py" <<'PY'
import os, re, sys
model, prompt = sys.argv[1], sys.stdin.read()
mode = os.environ.get("FAKE_MODE", "")
log = open(os.environ["FAKE_LOG"], "a")
if prompt.startswith("You are evaluating"):
    path = re.search(r"Read the page at (\S+),", prompt).group(1)
    log.write(f"{model} evaluate {path}\n")
    print("VERDICT: fail\n- Overview: the parts are wrong" if mode == "reject" else "VERDICT: pass")
    sys.exit(0)
path = re.search(r"^- Path: (\S+)$", prompt, re.M).group(1)
title = re.search(r"^- Title: (.+)$", prompt, re.M).group(1)
log.write(f"{model} write {path}" + (" moved" if "source moved" in prompt else "") + "\n")
if mode == "badfirst" and "## Feedback to resolve" not in prompt:
    print("<!-- helix:source nowhere/missing.py -->\n# " + title + "\n\nThe tool has one module.")
    sys.exit(0)
index = path.endswith("index.md")  # written first; it links a page written after it
gap = "<!-- helix:gap artifact:architecture -->\n" if index else ""
link = " Read the [walkthrough](walkthrough.md) next." if index else ""
print(f"Here is the page.\n\n{gap}<!-- helix:source src/tool/cli.py -->\n# {title}\n\n"
      f"The tool has one module, `src/tool/cli.py`, which reads a spec and prints it.{link}")
PY
export FAKE_LOG="$tmpdir/calls.log"
: >"$FAKE_LOG"
agent="python3 $tmpdir/fake.py {model}"

project="$tmpdir/project"
mkdir -p "$project/src/tool" "$project/docs/helix/01-frame"
cat >"$project/.helix.yml" <<'EOF'
flows:
  - id: helix
    root: docs/helix/
publish:
  schema: 1
  audiences: [developer]
  out: docs/guide
EOF
printf 'def main():\n    """Read a spec and print it."""\n' >"$project/src/tool/cli.py"
git -C "$project" init -q && git -C "$project" add -A

# --dry-run prints the prompts and calls nothing.
"$rg" write --root "$project" --agent "$agent" --dry-run >"$tmpdir/out"
grep -q "The reader's task" "$tmpdir/out" || fail "a dry run should print the writer's prompt"
[ -s "$FAKE_LOG" ] && fail "a dry run must call no agent"

# The writer and the evaluator must be different models.
status=0
"$rg" write --root "$project" --agent "$agent" --model same --reviewer-model same >/dev/null 2>&1 || status=$?
[ "$status" -eq 2 ] || fail "write should refuse one model as writer and evaluator (exit $status)"

# Every missing written page is written by the writer, checked, and reviewed by the evaluator.
"$rg" write --root "$project" --agent "$agent" >"$tmpdir/out" 2>&1 || { cat "$tmpdir/out"; fail "write should succeed"; }
page="$project/docs/guide/developer/index.md"
[ -f "$page" ] || fail "write should write developer/index.md"
grep -q "written=agent-opus" "$page" || fail "the header should name the writer"
grep -qE "reviewed=[0-9-]+/agent-sonnet/" "$page" || fail "the evaluator's pass should be stamped"
grep -qE "helix:source src/tool/cli.py sha256:[0-9a-f]+" "$page" || fail "the sources should be stamped"
grep -q "Here is the page" "$page" && fail "text before the page should be dropped"
grep -q "^sonnet evaluate docs/guide/developer/index.md$" "$FAKE_LOG" || fail "the evaluator should be the reviewer model"
"$rg" status --root "$project" >"$tmpdir/out"
grep -E "^\s+(MISSING|REVIEW|STALE)" "$tmpdir/out" && fail "every written page should be current"
grep -q "written without artifact:architecture" "$tmpdir/out" || fail "status should report a page's gaps"

# A rerun on a current guide calls nothing.
calls=$(wc -l <"$FAKE_LOG")
"$rg" write --root "$project" --agent "$agent" | grep -q "nothing to write" || fail "a rerun should have nothing to write"
[ "$(wc -l <"$FAKE_LOG")" -eq "$calls" ] || fail "a rerun must call no agent"

# The writer cannot review its own page.
"$rg" review "$page" --by agent-opus --root "$project" 2>/dev/null && fail "review should refuse the page's writer"

# A bad first answer goes back to the writer with the findings.
rm "$project/docs/guide/developer/walkthrough.md"
: >"$FAKE_LOG"
FAKE_MODE=badfirst "$rg" write developer/walkthrough --root "$project" --agent "$agent" >/dev/null 2>&1 \
  || fail "a revised answer should be written"
[ "$(grep -c "^opus write" "$FAKE_LOG")" -eq 2 ] || fail "a bad first answer should be revised once"
grep -q "nowhere/missing.py" "$project/docs/guide/developer/walkthrough.md" && fail "a missing source must not be cited"

# A failed evaluation is revised once, then the page is left unreviewed.
rm "$project/docs/guide/developer/architecture.md"
FAKE_MODE=reject "$rg" write --root "$project" --agent "$agent" >/dev/null 2>"$tmpdir/err" && fail "a rejected page should exit 1"
grep -q "LEFT docs/guide/developer/architecture.md" "$tmpdir/err" || fail "a rejected page should be reported"
"$rg" status --root "$project" | grep -qE "REVIEW\s+architecture" || fail "a rejected page should be left unreviewed"

# An unreviewed page its checks would block goes back to the writer, not only to the evaluator.
printf '\nOne. Two. Three. Four. Five.\n' >>"$project/docs/guide/developer/developer-guide.md"
: >"$FAKE_LOG"
"$rg" write --root "$project" --agent "$agent" >/dev/null 2>&1 || fail "a page blocked by its checks should be revised"
grep -q "^opus write docs/guide/developer/developer-guide.md$" "$FAKE_LOG" || fail "a page with prose findings should go to the writer"

# A stale page is revised with the sources that moved, then evaluated.
printf 'def main():\n    """Read a spec and print it twice."""\n' >"$project/src/tool/cli.py"
: >"$FAKE_LOG"
"$rg" write --root "$project" --agent "$agent" >/dev/null 2>&1 || fail "stale pages should be rewritten"
grep -q "^opus write docs/guide/developer/index.md moved$" "$FAKE_LOG" || fail "the writer should be told which sources moved"

# build --write writes the pages and builds the rest.
rm -rf "$project/docs/guide"
"$rg" build --write --no-site --root "$project" --agent "$agent" >/dev/null 2>&1 || fail "build --write should succeed"
[ -f "$project/docs/guide/developer/developer-guide.md" ] || fail "build --write should write the written pages"
"$rg" check --root "$project" >/dev/null || fail "check should pass after build --write"

echo "OK: write writes, checks, and evaluates the written pages with a separate reader, and touches nothing current"
