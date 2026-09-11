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

# title.slop: headline shapes that read as generated. A title is one sentence
# with a subject, a verb, and one concrete noun; these are the ways it fails
# that the human-facing voice profile names (reversals, rule-of-three padding,
# flattery, generalizations). Ported from sloptimizer's headline rules so the
# gate holds without that skill installed.
_APOS = r"(?:'|’)"
_LISTICLE_NOUNS = (r"(?:things|reasons|ways|lessons|mistakes|signs|secrets|tips|takeaways|truths|myths|"
                   r"ideas|insights|principles|habits|rules|questions|shifts|changes|factors|points|patterns|steps|keys|pillars|traps)")
_GROUP_NOUNS = (r"(?:teams?|people|leaders|engineers|developers|companies|organi[sz]ations|customers|users|"
                r"buyers|founders|executives|managers|businesses|enterprises|startups)")
_GROUP_VERBS = (r"(?:switch|win|lose|choose|prefer|want|need|trust|buy|adopt|leave|stay|succeed|fail|care|love|"
                r"hate|ignore|struggle|expect|demand|know|forget|resist|deserve)")
_IMPERATIVES = {
    "add", "adopt", "align", "ask", "audit", "build", "buy", "call", "check", "choose", "close", "commit",
    "configure", "count", "cut", "decide", "define", "deploy", "design", "document", "draft", "drive", "edit",
    "find", "fix", "follow", "frame", "get", "give", "go", "grow", "hire", "hold", "install", "join", "keep",
    "launch", "lead", "learn", "let", "list", "make", "map", "measure", "merge", "move", "name", "open", "own",
    "pick", "plan", "publish", "push", "put", "read", "release", "remove", "review", "run", "scale", "see",
    "sell", "send", "set", "share", "ship", "show", "sign", "start", "stop", "take", "tell", "test", "track",
    "train", "try", "turn", "use", "validate", "verify", "watch", "write",
}
_REVERSAL = [re.compile(p, re.I) for p in (
    rf"\b(?:(?:is|are|was|were|do|does|did|has|have|had|will|can|could|should)\s+not|(?:isn|aren|wasn|weren|doesn|don|hasn|haven){_APOS}t)\s*[.!]?$",
    r",\s*not\s+(?:a|an|the|your|our|their|just|only|merely|simply|because)\b",
    r"^not\s+(?:a|an|the|just|only|because)\b",
    r"\bnot\s+[^,;.]{1,40}?,?\s+but\s+\w",
    rf"\b(?:isn{_APOS}t|aren{_APOS}t|is not|are not|doesn{_APOS}t|don{_APOS}t)\b[^,;.]{{1,60}}[,;.]\s*(?:it{_APOS}s|it is|they{_APOS}re|they are|but)\b",
    r"^(?:less|fewer|more)\b[^,]{1,40},\s*(?:less|fewer|more)\b",
)]
_FLATTERY = [re.compile(p, re.I) for p in (
    r"\byour best (?:teams?|people|engineers?|work|days?)\b", r"\b(?:teams|people|leaders|companies) like yours?\b",
    r"\bhold(?:s|ing)? (?:ourselves|yourself|yourselves|themselves) to\b", r"\byou deserve\b",
    r"\bthe (?:smartest|best|brightest) (?:teams|people|minds|engineers)\b", r"\byou already (?:know|use|have|do|trust)\b",
    r"\bworld[- ]class\b", r"\bbest[- ]in[- ]class\b", r"\bindustry[- ]leading\b", r"\bthe (?:bar|standard) we (?:set|hold|keep)\b",
)]
_APHORISM = [re.compile(p, re.I) for p in (
    r"\bis the new\b", r"\bthe only \w+ that matters\b", r"\bis everything\b", r"\bmore than ever\b", r"\bdone right\b",
    r"\bis (?:a|the) (?:feature|superpower|multiplier|moat|journey|mindset)\b", r"\bis (?:a|an) (?:nice-to-have|luxury)\b",
    r"\b(?:wins|matters|counts)\s*[.!]?$", r"\bat scale\s*[.!]?$", r"\bthe hard way\b", r"\bchanges everything\b",
    r"\bhere to stay\b", r"\bthe future of\b", r"\bwelcome to\b",
)]
_TITLE_STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "of", "to", "in", "on", "at", "by", "for", "with", "from", "into", "than",
    "that", "this", "these", "those", "it", "its", "is", "are", "was", "were", "be", "been", "as", "if", "when",
    "once", "while", "before", "after", "not", "no", "so", "you", "your", "we", "our", "they", "their", "one",
    "each", "every", "any", "all", "can", "will", "now", "then", "here", "there", "what", "who", "how", "per",
    "own", "back", "up", "out", "under", "over", "more", "less", "most", "much", "very", "just", "only",
}


def title_slop(title: str) -> list[str]:
    """Headline slop findings for one title; each is a short message with the match."""
    t = title.strip()
    out: list[str] = []
    for p in _REVERSAL:
        m = p.search(t)
        if m:
            out.append(f"contrastive reversal {m.group(0).strip()!r}; state the positive claim")
            break
    m = re.search(r"(?<!\d):(?!\d)\s*(.+)$", t)
    if m and m.group(1).strip():
        items = [i for i in re.split(r",\s+|\s+(?:and|or)\s+", m.group(1)) if i.strip()]
        if len(items) >= 2:
            out.append(f"colon list {t[m.start():]!r}; keep the one item the unit proves, the list is body")
        else:
            out.append(f"colon reveal {t[m.start():]!r}; write one sentence with a subject and a verb")
    verbs = []
    for seg in re.split(r"[,;]\s+|\.\s+", t):
        seg = re.sub(r"^(?:and|then|or)\s+", "", seg.strip(), flags=re.I)
        w = re.match(r"[A-Za-z]+", seg)
        if w and w.group(0).lower() in _IMPERATIVES:
            verbs.append(w.group(0))
    if len(verbs) >= 3:
        out.append(f"imperative chain {', '.join(verbs)!r}; one verb per title, the steps are body")
    m = re.search(rf"\b(?:two|three|four|five|six|seven|eight|nine|ten|\d+)\s+(?:[\w-]+\s+){{0,2}}?{_LISTICLE_NOUNS}\b", t, re.I)
    if m:
        out.append(f"listicle count {m.group(0)!r}; name the item that matters")
    neg = re.findall(rf"\b(?:no|not|never|nothing|none|nor|without)\b|n{_APOS}t\b", t, re.I)
    if len(neg) >= 2:
        out.append(f"stacked negation {', '.join(neg)!r}; say what it does or keeps")
    item = r"[\w$%'’-]+(?: [\w$%'’-]+){0,3}"
    m = re.search(rf"\b{item},\s+{item},?\s+(?:and|or)\s+[\w$%'’-]+", t, re.I)
    if m:
        out.append(f"rule-of-three list {m.group(0)!r}; keep one concrete noun")
    for p in _FLATTERY:
        m = p.search(t)
        if m:
            out.append(f"flattery {m.group(0)!r}; replace the compliment with a checkable fact")
            break
    for p in _APHORISM:
        m = p.search(t)
        if m:
            out.append(f"pseudo-aphorism {m.group(0)!r}; replace the slogan with the claim and its number")
            break
    m = re.search(rf"^{_GROUP_NOUNS}\s+{_GROUP_VERBS}\b", t, re.I) or re.search(rf"\b(?:every|all|any)\s+(?:[\w-]+\s+)?{_GROUP_NOUNS}\b", t, re.I)
    if m:
        out.append(f"universal claim {m.group(0)!r}; scope it to which teams, how many, measured where")
    return out


def content_words(title: str) -> set[str]:
    """Crude stems of the content words in a title, for the horizontal-logic check."""
    out: set[str] = set()
    for w in re.findall(r"[a-z0-9]+", title.lower()):
        if w in _TITLE_STOPWORDS or len(w) < 3:
            continue
        for suffix in ("ing", "es", "ed", "s"):
            if len(w) > 4 and w.endswith(suffix):
                w = w[: -len(suffix)]
                break
        out.add(w)
    return out


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
        if pattern != "appendix-sources":
            for msg in title_slop(t):
                add("BLOCKING", "title.slop", f"unit {u['n']} title: {msg}", u["line"])
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

    # horizontal logic: reading only the titles must tell the story, so each
    # title should share at least one content word with the one before it.
    story = [u for u in us if u["fields"].get("Pattern", {}).get("text") != "appendix-sources"]
    for prev, cur in zip(story, story[1:]):
        if not (content_words(prev["title"]) & content_words(cur["title"])):
            add("WARNING", "horizontal_logic",
                f"units {prev['n']} and {cur['n']}: titles share no content word; the titles-only read may not connect "
                f"({prev['title'][:40]!r} -> {cur['title'][:40]!r})", cur["line"])

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
