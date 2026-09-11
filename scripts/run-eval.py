#!/usr/bin/env python3
"""run-eval — run the HELIX skill headlessly against fixed briefs and score it.

For each brief in evals/briefs.yml: copy the fixture into a fresh workspace,
add a .helix.yml marker, run the host headlessly with the HELIX plugin
loaded, then score deterministic checks (files, validators, report shape,
forbidden edits) and, with --judge, a rubric scored 0-2 per item by a second
headless call. Results land under evals/results/<stamp>/ as JSON plus a
Markdown summary.

Usage:
    scripts/run-eval.py [--briefs id,id] [--judge] [--runner CMD] [--keep]
                        [--dry-run] [--out DIR]

The default runner is Claude Code in print mode with this checkout as the
plugin directory. Override --runner with a template that receives {prompt},
{cwd}, and {repo} (shell-quoted) for another host. The skill body never
names a runtime; this script may.
"""
from __future__ import annotations

import argparse
import datetime as dt
import fnmatch
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
BRIEFS = REPO / "evals" / "briefs.yml"
FIXTURE_BASELINE = REPO / "tests" / "workflows" / "fixtures" / "recipe-app" / "baseline"
VALIDATE = REPO / "skills" / "helix" / "scripts" / "validate-instance.py"
CHECK_DELIVERABLE = REPO / "skills" / "helix" / "scripts" / "check-deliverable.py"
DEFAULT_RUNNER = (
    "claude -p {prompt} --plugin-dir {repo} --output-format json "
    "--permission-mode acceptEdits --max-turns {max_turns} "
    "--allowedTools 'Skill,Read,Write,Edit,Glob,Grep,Bash(ls:*),Bash(cat:*),Bash(find:*),"
    "Bash(grep:*),Bash(python3:*),Bash(git:*)'"
)
JUDGE_RUNNER = "claude -p {prompt} --output-format json --max-turns 1"
MARKER = "flows:\n  - id: helix\n    root: docs/helix/\nautonomy:\n  level: high\n"


def snapshot(root: Path) -> dict[str, str]:
    out = {}
    for p in root.rglob("*"):
        if p.is_file() and ".git" not in p.parts:
            out[str(p.relative_to(root))] = hashlib.sha256(p.read_bytes()).hexdigest()
    return out


def make_workspace(fixture: str, keep_dir: Path | None) -> Path:
    ws = Path(tempfile.mkdtemp(prefix="helix-eval-")) if keep_dir is None else keep_dir
    ws.mkdir(parents=True, exist_ok=True)
    if fixture == "baseline":
        shutil.copytree(FIXTURE_BASELINE, ws, dirs_exist_ok=True)
    elif fixture == "vision":
        src = FIXTURE_BASELINE / "docs" / "helix" / "00-discover" / "product-vision.md"
        dst = ws / "docs" / "helix" / "00-discover" / "product-vision.md"
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        for d in ("01-frame", "02-design", "03-test", "04-build", "05-deploy", "06-iterate"):
            (ws / "docs" / "helix" / d).mkdir(parents=True, exist_ok=True)
    else:
        raise SystemExit(f"unknown fixture {fixture!r}")
    (ws / ".helix.yml").write_text(MARKER, encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=ws, check=True)
    subprocess.run(["git", "add", "-A"], cwd=ws, check=True)
    subprocess.run(["git", "-c", "user.email=eval@helix", "-c", "user.name=helix-eval", "commit", "-qm", "fixture"], cwd=ws, check=True)
    return ws


def run_host(runner: str, prompt: str, cwd: Path, max_turns: int, timeout: int) -> dict:
    cmd = runner.format(prompt=shlex.quote(prompt), cwd=shlex.quote(str(cwd)), repo=shlex.quote(str(REPO)), max_turns=max_turns)
    started = dt.datetime.now()
    try:
        proc = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired as e:
        return {"ok": False, "error": f"timeout after {timeout}s", "stdout": e.stdout or "", "stderr": e.stderr or "", "seconds": timeout}
    seconds = (dt.datetime.now() - started).total_seconds()
    text = proc.stdout
    result = text
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            result = data.get("result", text)
        elif isinstance(data, list):
            finals = [e for e in data if isinstance(e, dict) and e.get("type") == "result"]
            result = finals[-1].get("result", text) if finals else text
    except json.JSONDecodeError:
        data = None
    final = {}
    if isinstance(data, dict):
        final = data
    elif isinstance(data, list):
        finals = [e for e in data if isinstance(e, dict) and e.get("type") == "result"]
        final = finals[-1] if finals else {}
    return {"ok": proc.returncode == 0 and final.get("subtype", "success") == "success", "returncode": proc.returncode,
            "result": result, "raw": data, "stderr": proc.stderr[-4000:], "seconds": round(seconds, 1),
            "cost_usd": final.get("total_cost_usd"), "turns": final.get("num_turns")}


def match(ws: Path, globs: list[str]) -> list[Path]:
    files: list[Path] = []
    for g in globs:
        files += [p for p in ws.glob(g) if p.is_file()]
    return sorted(set(files))


def instance_findings(path: Path) -> set[str]:
    """Blocking finding keys for one artifact (check id + message), empty when it passes."""
    r = subprocess.run([sys.executable, str(VALIDATE), str(path), "--catalog", str(REPO / "workflows"), "--format", "json"], capture_output=True, text=True)
    try:
        data = json.loads(r.stdout)
        return {f"{x['check']}: {x['message']}" for x in data["findings"] if x["severity"] == "BLOCKING"}
    except (json.JSONDecodeError, KeyError):
        return {f"validator error: {r.stderr.strip()[-200:]}"}


def run_checks(brief: dict, ws: Path, before: dict[str, str], after: dict[str, str], result: str, baseline: dict[str, set[str]]) -> list[dict]:
    out = []
    created = [f for f in after if f not in before]
    for c in brief.get("checks", []):
        kind = c["kind"]
        ok, detail = True, ""
        if kind == "files_exist":
            missing = [g for g in c["globs"] if not match(ws, [g])]
            ok, detail = not missing, f"missing {missing}" if missing else f"present {c['globs']}"
        elif kind == "files_unchanged":
            changed = [f for f in before if f in after and after[f] != before[f] and any(fnmatch.fnmatch(f, g) for g in c["globs"])]
            deleted = [f for f in before if f not in after and any(fnmatch.fnmatch(f, g) for g in c["globs"])]
            ok, detail = not changed and not deleted, f"changed {changed} deleted {deleted}" if (changed or deleted) else "unchanged"
        elif kind == "validate_instance":
            # Delta semantics: the run is blamed only for blocking findings that the
            # fixture did not already carry (new files must be fully clean).
            fails = []
            for f in match(ws, c["globs"]):
                rel = str(f.relative_to(ws))
                new = instance_findings(f) - baseline.get(rel, set())
                if new:
                    fails.append(f"{rel}: " + "; ".join(sorted(new))[:300])
            ok, detail = not fails, "; ".join(fails) if fails else f"{len(match(ws, c['globs']))} artifact(s) valid (no new blocking findings)"
        elif kind == "report_block":
            m = re.search(r"helix_report:\s*\n(?:.*\n)*?\s*mode:\s*([a-z-]+)", result)
            ok = bool(m) and m.group(1) == c["mode"]
            detail = f"mode={m.group(1)}" if m else "no helix_report block"
        elif kind == "output_contains":
            missing = [v for v in c["values"] if v.lower() not in result.lower()]
            ok, detail = not missing, f"missing {missing}" if missing else "all present"
        elif kind == "output_not_contains":
            found = [v for v in c["values"] if re.search(r"\b" + re.escape(v) + r"\b", result, re.I)]
            ok, detail = not found, f"found {found}" if found else "clean"
        elif kind == "deliverable_gate":
            fails = []
            for f in match(ws, [c["glob"]]):
                r = subprocess.run([sys.executable, str(CHECK_DELIVERABLE), str(f), "--catalog", str(REPO / "workflows"), "--format", "json"], capture_output=True, text=True)
                try:
                    data = json.loads(r.stdout)
                    blocking = [x for x in data["findings"] if x["severity"] == "BLOCKING" and not x["check"].startswith("render.")]
                    if blocking:
                        fails.append(f"{f.relative_to(ws)}: " + "; ".join(f"{x['check']}: {x['message']}" for x in blocking[:5]))
                except (json.JSONDecodeError, KeyError):
                    fails.append(f"{f.relative_to(ws)}: checker error {r.stderr[-200:]}")
            n = len(match(ws, [c["glob"]]))
            ok, detail = n > 0 and not fails, ("; ".join(fails) if fails else (f"{n} script(s) pass (render checks excluded)" if n else "no deliverable script"))
        elif kind == "max_new_files":
            ok, detail = len(created) <= c["value"], f"{len(created)} new file(s): {created[:8]}"
        else:
            ok, detail = False, f"unknown check kind {kind}"
        out.append({"kind": kind, "ok": ok, "detail": detail})
    return out


def judge(brief: dict, ws: Path, result: str, diff: str, runner: str, timeout: int) -> dict | None:
    items = brief.get("rubric", [])
    if not items:
        return None
    prompt = (
        "You are grading one run of a document-authoring skill. Score each rubric item 0 (absent), 1 (partial), or 2 (fully met), "
        "using only the evidence below. Reply with a single JSON object and nothing else, no prose before or after, no code fence: "
        "{\"scores\": [{\"item\": <n>, \"score\": <0|1|2>, \"reason\": \"<one sentence>\"}]}\n\n"
        f"BRIEF PROMPT:\n{brief['prompt']}\n\nRUBRIC:\n" + "\n".join(f"{i+1}. {t}" for i, t in enumerate(items)) +
        f"\n\nFINAL RESPONSE:\n{result[:12000]}\n\nWORKSPACE DIFF (git):\n{diff[:16000]}\n"
    )
    r = run_host(runner, prompt, ws, 1, timeout)
    text = r.get("result", "") or ""
    m = re.search(r"\{.*\}", text, re.S)
    try:
        data = json.loads(m.group(0)) if m else {}
        scores = data.get("scores", [])
        if not scores:
            return {"scores": [], "total": 0, "max": 2 * len(items), "error": "judge returned no scores", "raw": text[:800]}
        total = sum(int(s.get("score", 0)) for s in scores)
        return {"scores": scores, "total": total, "max": 2 * len(items), "raw": text[:800]}
    except (json.JSONDecodeError, ValueError, AttributeError):
        return {"scores": [], "total": 0, "max": 2 * len(items), "error": "judge output not parseable", "raw": text[:800]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--briefs", help="comma-separated brief ids (default: all)")
    ap.add_argument("--judge", action="store_true", help="also score the rubric with a headless judge call")
    ap.add_argument("--runner", default=DEFAULT_RUNNER)
    ap.add_argument("--judge-runner", default=JUDGE_RUNNER)
    ap.add_argument("--keep", action="store_true", help="keep workspaces under the results dir")
    ap.add_argument("--dry-run", action="store_true", help="list briefs and exit")
    ap.add_argument("--out", help="results directory (default evals/results/<stamp>)")
    ap.add_argument("--rejudge", help="re-run only the judge on a saved results directory (no host runs)")
    ap.add_argument("--summarize", help="rewrite summary.md from a saved results directory (no runs, no judge)")
    args = ap.parse_args()

    spec = yaml.safe_load(BRIEFS.read_text(encoding="utf-8"))
    all_briefs = spec["briefs"]
    briefs = all_briefs
    want = set(args.briefs.split(",")) if args.briefs else set()
    if want:
        briefs = [b for b in all_briefs if b["id"] in want]
        unknown = want - {b["id"] for b in briefs}
        if unknown:
            print(f"unknown brief ids: {sorted(unknown)}", file=sys.stderr)
            return 2
    if args.dry_run:
        for b in briefs:
            print(f"{b['id']:<26} mode={b['mode']:<9} fixture={b['fixture']:<9} checks={len(b.get('checks', []))} rubric={len(b.get('rubric', []))}")
        return 0

    if args.rejudge or args.summarize:
        # Load every saved row; rejudge only the selected briefs (all when none given).
        out_dir = Path(args.rejudge or args.summarize)
        stamp = out_dir.name
        rows = []
        for b in all_briefs:
            f = out_dir / f"{b['id']}.json"
            if not f.is_file():
                continue
            row = json.loads(f.read_text(encoding="utf-8"))
            if args.rejudge and (not want or b["id"] in want):
                print(f"[{b['id']}] rejudging ...", flush=True)
                row["judge"] = judge(b, REPO, row.get("result", ""), row.get("diff") or row.get("diff_stat", ""), args.judge_runner, int(spec.get("defaults", {}).get("timeout_seconds", 900)))
                f.write_text(json.dumps(row, indent=2), encoding="utf-8")
            rows.append(row)
        write_summary(out_dir, stamp, args.runner, rows)
        return 0

    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M")
    out_dir = Path(args.out) if args.out else REPO / "evals" / "results" / stamp
    out_dir.mkdir(parents=True, exist_ok=True)
    defaults = spec.get("defaults", {})
    rows = []
    for b in briefs:
        max_turns = int(b.get("max_turns", defaults.get("max_turns", 80)))
        timeout = int(b.get("timeout_seconds", defaults.get("timeout_seconds", 900)))
        ws = make_workspace(b["fixture"], (out_dir / "workspaces" / b["id"]) if args.keep else None)
        before = snapshot(ws)
        baseline = {str(f.relative_to(ws)): instance_findings(f) for c in b.get("checks", []) if c["kind"] == "validate_instance" for f in match(ws, c["globs"])}
        print(f"[{b['id']}] running in {ws} ...", flush=True)
        run = run_host(args.runner, b["prompt"], ws, max_turns, timeout)
        after = snapshot(ws)
        diff = subprocess.run(["git", "diff", "--stat"], cwd=ws, capture_output=True, text=True).stdout
        untracked = subprocess.run(["git", "status", "--short"], cwd=ws, capture_output=True, text=True).stdout
        full_diff = subprocess.run(["git", "diff"], cwd=ws, capture_output=True, text=True).stdout
        for f in [x for x in after if x not in before]:
            try:
                full_diff += f"\n--- new file: {f}\n" + (ws / f).read_text(encoding="utf-8", errors="ignore")[:6000]
            except OSError:
                pass
        result_text = run.get("result", "") or ""
        checks = run_checks(b, ws, before, after, result_text, baseline) if run.get("ok") else [{"kind": "run", "ok": False, "detail": run.get("error") or f"exit {run.get('returncode')}: {run.get('stderr', '')[-300:]}"}]
        judged = judge(b, ws, result_text, full_diff, args.judge_runner, timeout) if (args.judge and run.get("ok")) else None
        passed = sum(1 for c in checks if c["ok"])
        row = {"id": b["id"], "mode": b["mode"], "seconds": run.get("seconds"), "run_ok": run.get("ok"),
               "cost_usd": run.get("cost_usd"), "turns": run.get("turns"),
               "checks_passed": passed, "checks_total": len(checks), "checks": checks, "judge": judged,
               "diff_stat": diff + untracked, "diff": full_diff[:60000], "result": result_text}
        rows.append(row)
        (out_dir / f"{b['id']}.json").write_text(json.dumps(row, indent=2), encoding="utf-8")
        print(f"[{b['id']}] checks {passed}/{len(checks)}" + (f", rubric {judged['total']}/{judged['max']}" if judged else "") + f", {run.get('seconds')}s", flush=True)
        if not args.keep:
            shutil.rmtree(ws, ignore_errors=True)

    write_summary(out_dir, stamp, args.runner, rows)
    total_checks = sum(r["checks_total"] for r in rows)
    total_passed = sum(r["checks_passed"] for r in rows)
    print(f"checks: {total_passed}/{total_checks}")
    return 0 if total_passed == total_checks else 1


def write_summary(out_dir: Path, stamp: str, runner: str, rows: list[dict]) -> None:
    lines = [f"# HELIX eval run {stamp}", "", f"Runner: `{runner}`", f"Commit: `{subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], cwd=REPO, capture_output=True, text=True).stdout.strip()}`", "",
             "| Brief | Mode | Checks | Rubric | Turns | Seconds | Cost USD |", "|---|---|---|---|---|---|---|"]
    for r in rows:
        rub = f"{r['judge']['total']}/{r['judge']['max']}" if r.get("judge") else "n/a"
        cost = f"{r['cost_usd']:.2f}" if isinstance(r.get("cost_usd"), (int, float)) else "n/a"
        lines.append(f"| {r['id']} | {r['mode']} | {r['checks_passed']}/{r['checks_total']} | {rub} | {r.get('turns') or 'n/a'} | {r['seconds']} | {cost} |")
    lines += ["", "## Failed checks", ""]
    any_fail = False
    for r in rows:
        for c in r["checks"]:
            if not c["ok"]:
                any_fail = True
                lines.append(f"- **{r['id']}** {c['kind']}: {c['detail']}")
    if not any_fail:
        lines.append("None.")
    lines += ["", "## Rubric notes", ""]
    for r in rows:
        if r.get("judge"):
            for s in r["judge"].get("scores", []):
                lines.append(f"- **{r['id']}** item {s.get('item')}: {s.get('score')} — {s.get('reason', '')}")
    for r in rows:
        if r.get("judge") and r["judge"].get("error"):
            lines.append(f"- **{r['id']}** judge: {r['judge']['error']}")
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nresults: {out_dir}/summary.md")


if __name__ == "__main__":
    sys.exit(main())
