#!/usr/bin/env python3
"""check-deliverable — deterministic gate for a HELIX deliverable script.

Checks a deck / one-pager / brief script (the `deliverable` artifact type)
for the things a person would otherwise catch on the first read: label
titles, HELIX vocabulary in bodies, unsourced numbers, placeholders, missing
or generic visuals, pattern limits and density rules from
deliverables/slide-patterns.yml, deck ordering, and an inspected render.

Usage:
    check-deliverable.py <script.md> [--catalog DIR] [--format text|json]

Exit 0 when no blocking findings; 1 when there are; 2 on usage errors.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    print("check-deliverable.py needs PyYAML (python3 -m pip install pyyaml)", file=sys.stderr)
    sys.exit(2)

LABEL_TITLES = {
    "overview", "background", "results", "agenda", "summary", "introduction",
    "next steps", "risks", "timeline", "recommendation", "conclusion",
    "questions", "thank you", "appendix", "sources", "context", "problem",
    "solution", "status", "update", "roadmap", "team", "about us",
}
HELIX_VOCAB = re.compile(
    r"\b(?:FR|US|FEAT|ADR|TD|SD|TP|PRD|DEL|CONTRACT|WS)-\d+"
    r"|\bbeads?\b|\bratchets?\b|\bwork items?\b|\bacceptance criteri(?:a|on)\b"
    r"|\bAC\d+\b|\bartifact graph\b|\b(?:discover|frame|build|deploy|iterate) activity\b"
    r"|\bddx\b",
    re.I,
)
PLACEHOLDER = re.compile(r"\[NEEDS CLARIFICATION|\[TODO\]|\bTBD\b|\[Fill in\]|<placeholder>|\[\.\.\.\]|\[[A-Z][a-z]+(?: [a-z]+)*\]")
NUMBER = re.compile(r"(?<![\w.])(?:\$?\d[\d,]*(?:\.\d+)?\s?(?:%|k|K|M|B|x)?)(?![\w.])")
GENERIC_VISUALS = {"chart", "diagram", "image", "table", "graph", "picture", "photo", "screenshot", "none", "n/a"}


def load_patterns(catalog: Path | None, script_path: Path) -> dict:
    candidates = []
    if catalog:
        candidates += [catalog / "deliverables" / "slide-patterns.yml",
                       catalog / "workflows" / "deliverables" / "slide-patterns.yml"]
    for parent in [script_path.resolve()] + list(script_path.resolve().parents):
        candidates.append(parent / "workflows" / "deliverables" / "slide-patterns.yml")
    here = Path(__file__).resolve().parent
    candidates += [here.parent / "references" / "deliverables" / "slide-patterns.yml",
                   here.parent.parent.parent / "workflows" / "deliverables" / "slide-patterns.yml"]
    for c in candidates:
        if c.is_file():
            data = yaml.safe_load(c.read_text(encoding="utf-8")) or {}
            return {"path": c, "patterns": {p["id"]: p for p in data.get("patterns", [])},
                    "density": data.get("density", {})}
    return {"path": None, "patterns": {}, "density": {}}


def split_frontmatter(text: str) -> tuple[dict, str, int]:
    if not text.startswith("---\n"):
        return {}, text, 0
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text, 0
    fm = yaml.safe_load(text[4:end]) or {}
    body = text[end + 5:]
    return fm, body, text[:end + 5].count("\n")


def sections(body: str) -> dict[str, tuple[int, str]]:
    """H2 title -> (line offset, text)."""
    out: dict[str, tuple[int, str]] = {}
    current, start, buf = None, 0, []
    for i, line in enumerate(body.splitlines()):
        if line.startswith("## "):
            if current is not None:
                out[current] = (start, "\n".join(buf))
            current, start, buf = line[3:].strip(), i, []
        else:
            buf.append(line)
    if current is not None:
        out[current] = (start, "\n".join(buf))
    return out


def units(content: str, offset: int) -> list[dict]:
    out: list[dict] = []
    cur = None
    for i, line in enumerate(content.splitlines()):
        m = re.match(r"^### (\d+)\.\s+(.*)$", line)
        if m:
            cur = {"n": int(m.group(1)), "title": m.group(2).strip(), "line": offset + i + 1,
                   "fields": {}, "raw": []}
            out.append(cur)
            continue
        if cur is None:
            continue
        cur["raw"].append(line)
        fm = re.match(r"^\*\*(Pattern|Body|Visual|Notes|Sources)\*\*:\s*(.*)$", line)
        if fm:
            cur["fields"][fm.group(1)] = {"line": offset + i + 1, "text": fm.group(2).strip(), "lines": []}
            cur["_last"] = fm.group(1)
        elif cur.get("_last") and line.strip():
            cur["fields"][cur["_last"]]["lines"].append(line)
    for u in out:
        u.pop("_last", None)
    return out


def words(s: str) -> int:
    return len(re.findall(r"[A-Za-z0-9$%][\w$%.,'-]*", s))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("script")
    ap.add_argument("--catalog")
    ap.add_argument("--format", choices=["text", "json"], default="text")
    args = ap.parse_args()
    path = Path(args.script)
    if not path.is_file():
        print(f"no such file: {path}", file=sys.stderr)
        return 2
    text = path.read_text(encoding="utf-8")
    fm, body, fm_lines = split_frontmatter(text)
    pats = load_patterns(Path(args.catalog) if args.catalog else None, path)
    findings: list[dict] = []

    def add(sev: str, check: str, msg: str, line: int | None = None) -> None:
        findings.append({"severity": sev, "check": check, "message": msg, "line": line})

    ddx = fm.get("ddx", {}) if isinstance(fm, dict) else {}
    kind = (ddx.get("kind") or "deck") if isinstance(ddx, dict) else "deck"
    secs = sections(body)
    for required in ("Brief", "Story", "Content", "Sources", "Assumptions and gaps", "Render"):
        if required not in secs:
            add("BLOCKING", "section", f"missing '## {required}'")
    if "Content" not in secs:
        return report(findings, args.format, path)

    for m in PLACEHOLDER.finditer(body):
        line = fm_lines + body.count("\n", 0, m.start()) + 1
        # allow bracket tokens inside the Sources table path column? no: placeholders anywhere block
        add("BLOCKING", "placeholder", f"placeholder text {m.group(0)!r}", line)

    sources_text = secs.get("Sources", (0, ""))[1]
    source_ids = set(re.findall(r"^\|\s*(S\d+)\s*\|", sources_text, re.M))
    if not source_ids:
        add("BLOCKING", "sources", "Sources table has no S<n> rows")

    content_off = fm_lines + secs["Content"][0]
    us = units(secs["Content"][1], content_off)
    if not us:
        add("BLOCKING", "units", "no '### <n>. <claim title>' units under ## Content")

    prev_pattern, run = None, 0
    limit_consec = int(pats["density"].get("consecutive_same_pattern_max", 2))
    for u in us:
        t = u["title"]
        f = u["fields"]
        pattern = f.get("Pattern", {}).get("text", "")
        if pattern != "appendix-sources" and (t.lower().strip(" .:") in LABEL_TITLES or words(t) < 3):
            add("BLOCKING", "title.claim", f"unit {u['n']} title is a label, not a claim: {t!r}", u["line"])
        for name in ("Pattern", "Body", "Visual", "Notes", "Sources"):
            if name not in f:
                add("BLOCKING", f"unit.{name.lower()}", f"unit {u['n']} has no **{name}** line", u["line"])
        if pats["patterns"] and pattern and pattern not in pats["patterns"]:
            add("BLOCKING", "pattern.unknown", f"unit {u['n']} pattern {pattern!r} not in slide-patterns.yml", u["line"])
        if pattern == prev_pattern:
            run += 1
        else:
            prev_pattern, run = pattern, 1
        if run > limit_consec:
            add("WARNING", "density.consecutive", f"unit {u['n']}: more than {limit_consec} consecutive {pattern!r} units", u["line"])
        vis = f.get("Visual", {})
        vtext = (vis.get("text", "") + " " + " ".join(vis.get("lines", []))).strip()
        if vis and (vtext.lower().strip(" .") in GENERIC_VISUALS or words(vtext) < 6):
            add("BLOCKING", "visual.generic", f"unit {u['n']} visual is not specified (say what it shows, its series, and source)", vis.get("line"))
        bodyf = f.get("Body", {})
        btext = "\n".join([bodyf.get("text", "")] + bodyf.get("lines", []))
        notes = f.get("Notes", {})
        ntext = "\n".join([notes.get("text", "")] + notes.get("lines", []))
        for label, txt, ln in (("body", btext, bodyf.get("line")), ("notes", ntext, notes.get("line")), ("title", t, u["line"])):
            for m in HELIX_VOCAB.finditer(txt):
                add("BLOCKING", "vocabulary", f"unit {u['n']} {label} uses HELIX vocabulary {m.group(0)!r}; move it to Sources", ln)
        bullets = [l for l in bodyf.get("lines", []) if l.strip().startswith(("-", "*", "•"))]
        spec = pats["patterns"].get(pattern, {}).get("limits", {}) if pats["patterns"] else {}
        if spec:
            if "bullets" in spec and len(bullets) > spec["bullets"]:
                add("WARNING", "limits.bullets", f"unit {u['n']}: {len(bullets)} bullets, {pattern} allows {spec['bullets']}", bodyf.get("line"))
            if "words_per_bullet" in spec:
                for b in bullets:
                    if words(b) > spec["words_per_bullet"]:
                        add("WARNING", "limits.words_per_bullet", f"unit {u['n']}: bullet over {spec['words_per_bullet']} words: {b.strip()[:60]!r}", bodyf.get("line"))
            if "body_words" in spec and words(btext) > spec["body_words"]:
                add("WARNING", "limits.body_words", f"unit {u['n']}: body {words(btext)} words, {pattern} allows {spec['body_words']}", bodyf.get("line"))
            if "title_words" in spec and words(t) > spec["title_words"]:
                add("WARNING", "limits.title_words", f"unit {u['n']}: title over {spec['title_words']} words", u["line"])
        # numbers in body must appear in Sources
        for m in NUMBER.finditer(btext):
            num = m.group(0).strip()
            if re.fullmatch(r"\d", num):  # single digits are usually list counts
                continue
            if num not in sources_text:
                add("BLOCKING", "numbers.sourced", f"unit {u['n']}: figure {num!r} is not in the Sources table", bodyf.get("line"))
        cited = set(re.findall(r"S\d+", f.get("Sources", {}).get("text", "")))
        for c in cited - source_ids:
            add("BLOCKING", "sources.dangling", f"unit {u['n']} cites {c} which is not in the Sources table", f["Sources"]["line"])
        if f.get("Sources") and not cited:
            add("BLOCKING", "sources.empty", f"unit {u['n']} cites no S<n> source", f["Sources"]["line"])

    if kind == "deck" and us:
        first = us[0]["fields"].get("Pattern", {}).get("text")
        if first != "title":
            add("BLOCKING", "deck.order", "first unit of a deck must use the 'title' pattern", us[0]["line"])
        tail = [u["fields"].get("Pattern", {}).get("text") for u in us[-2:]]
        if tail != ["ask-next-steps", "appendix-sources"]:
            add("BLOCKING", "deck.order", "a deck ends with 'ask-next-steps' then 'appendix-sources'", us[-1]["line"])
        content_units = [u for u in us if u["fields"].get("Pattern", {}).get("text") not in ("title", "agenda", "section-divider", "appendix-sources")]
        if len(content_units) > 12:
            add("WARNING", "deck.length", f"{len(content_units)} content slides; more than 12 needs an explicit exception in Brief")

    render = secs.get("Render", (0, ""))[1]
    if "Render" in secs:
        if "inspected" not in render.lower():
            add("BLOCKING", "render.inspected", "Render section must record that every slide/page was rendered to an image and inspected")
        if not re.search(r"\.(pptx|html|pdf|docx)\b", render):
            add("BLOCKING", "render.targets", "Render section lists no rendered target path")
    exports = (ddx.get("authoring", {}) or {}).get("export") if isinstance(ddx, dict) else None
    if not exports:
        add("WARNING", "frontmatter.export", "ddx.authoring.export lists no rendered files")

    return report(findings, args.format, path)


def report(findings: list[dict], fmt: str, path: Path) -> int:
    blocking = sum(1 for f in findings if f["severity"] == "BLOCKING")
    warning = sum(1 for f in findings if f["severity"] == "WARNING")
    if fmt == "json":
        print(json.dumps({"script": str(path), "findings": findings,
                          "summary": {"blocking": blocking, "warning": warning}}, indent=2))
    else:
        for f in findings:
            loc = f"  [line {f['line']}]" if f.get("line") else ""
            print(f"{f['severity']:<9} {f['check']:<24} {f['message']}{loc}")
        status = "FAIL" if blocking else "OK"
        print(f"{status}: {path} blocking={blocking} warning={warning}")
    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main())
