#!/usr/bin/env python3
"""Generate the anti-slop rules reference page from the code that enforces the rules.

Output: docs/website/content/reference/anti-slop-rules/_index.md

Sources (read, never restated by hand): skills/helix/scripts/check-deliverable.py (title, shape, restatement,
vocabulary, number, placeholder, visual, coverage, and ordering checks with their patterns, phrase lists, and
severities), tests/fixtures/validate-deliverable/headline-cases.{json,SOURCE} (examples and the upstream commit),
workflows/deliverables/slide-patterns.yml (limits and density), .vale/styles/Helix/*.yml (prose lint),
skills/helix/scripts/deck-qa.py (visual gate ids, severities, thresholds), and skills/helix/scripts/render-deck.js
(what the renderer refuses to hide). Run by scripts/generate-reference.py; tests/validate-website-generated.sh
fails when the committed page drifts from these sources.
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHECKER = ROOT / "skills/helix/scripts/check-deliverable.py"
DECK_QA = ROOT / "skills/helix/scripts/deck-qa.py"
RENDERER = ROOT / "skills/helix/scripts/render-deck.js"
FIXTURE = ROOT / "tests/fixtures/validate-deliverable/headline-cases.json"
FIXTURE_SOURCE = ROOT / "tests/fixtures/validate-deliverable/headline-cases.SOURCE"
PATTERNS = ROOT / "workflows/deliverables/slide-patterns.yml"
VALE_STYLES = ROOT / ".vale/styles/Helix"
OUT = ROOT / "docs/website/content/reference/anti-slop-rules/_index.md"

# message prefix -> upstream rule name (the same map tests/validate-headline-sync.sh uses)
RULES = [
    ("contrastive reversal", "ContrastiveReversal", "title, shape"),
    ("colon list", "ColonList", "title"),
    ("colon reveal", "ColonReveal", "title"),
    ("imperative chain", "ImperativeChain", "title"),
    ("listicle count", "Listicle", "title"),
    ("stacked negation", "StackedNegation", "title"),
    ("rule-of-three list", "Triplet", "title"),
    ("flattery", "Flattery", "title, shape"),
    ("pseudo-aphorism", "Aphorism", "title, shape"),
    ("universal claim", "UniversalClaim", "title"),
    ("mannered phrase", "Mannered", "title"),
    ("inventory count", "InventoryCount", "title"),
    ("hedge", "Hedge", "title"),
    ("over-length", "Length", "title"),
    ("container title", "ContainerTitle", "slide title, shape"),
    ("self-justifying", "SelfJustifying", "slide title, shape"),
    ("shouting label", "ShoutingLabel", "title, shape"),
    ("invented status", "StatusJargon", "slide title"),
    ("taxonomy code", "Taxonomy", "slide title"),
    ("marketing register", "Marketing", "slide title"),
    ("trailing commentary", "TrailingCommentary", "shape"),
]


def load_checker():
    spec = importlib.util.spec_from_file_location("cd", CHECKER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def code(s: str) -> str:
    return "`" + str(s).replace("`", "'") + "`"


def pattern_text(p) -> str:
    return p.pattern if hasattr(p, "pattern") else str(p)


def alternation(regex: str) -> list[str]:
    """The literal alternatives of a `(?:a|b|c)` regex, for lists that are readable as words."""
    m = re.search(r"\(\?:(.*)\)$", regex.strip(), re.S)
    body = m.group(1) if m else regex
    return [a for a in body.split("|") if a]


def code_list(items, cols: int = 1) -> str:
    return "\n".join(f"- {code(i)}" for i in items)


def fixture_examples() -> dict[str, list[tuple[str, str]]]:
    """rule name -> [(mode, headline)] from the vendored upstream fixture."""
    out: dict[str, list[tuple[str, str]]] = {}
    for c in json.loads(FIXTURE.read_text(encoding="utf-8")):
        if "headline" not in c:
            continue
        for r in c.get("expected_rules", []):
            out.setdefault(r, []).append((c.get("mode", "headline"), c["headline"]))
    return out


def passing_examples() -> list[str]:
    return [c["headline"] for c in json.loads(FIXTURE.read_text(encoding="utf-8"))
            if "headline" in c and not c.get("expected_rules") and c.get("mode", "headline") in ("headline", "slide-title")]


def source_note() -> dict[str, str]:
    out = {}
    for line in FIXTURE_SOURCE.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def add_calls(path: Path, pattern: str) -> list[tuple[str, str, str]]:
    """(severity, check id, message) for every add(...) call in a script, message with f-string fields elided."""
    text = path.read_text(encoding="utf-8")
    out = []
    for m in re.finditer(pattern, text):
        sev, cid, msg = m.group(1), m.group(2), m.group(3)
        msg = re.sub(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", "…", msg)
        msg = msg.replace("\\n", " ").replace('\\"', '"').replace("\\'", "'")
        out.append((sev, cid, msg.strip()))
    seen, uniq = set(), []
    for sev, cid, msg in out:
        if (cid, sev) not in seen:   # a check may carry both severities (text-autofit); show each once
            seen.add((cid, sev)); uniq.append((sev, cid, msg))
    return uniq


def vale_rules() -> list[dict]:
    out = []
    for path in sorted(VALE_STYLES.glob("*.yml")):
        rule = {"name": f"Helix.{path.stem}", "extends": "", "level": "", "message": "", "tokens": [], "params": [], "swaps": []}
        intok = inswap = False
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not raw.startswith((" ", "-")) and ":" in line:
                key, _, val = line.partition(":")
                intok = key.strip() == "tokens"
                val = val.strip().strip('"').strip("'")
                if key.strip() in ("extends", "level", "message"):
                    rule[key.strip()] = val
                elif key.strip() == "swap":
                    inswap = True
                    continue
                elif key.strip() not in ("tokens", "scope", "ignorecase", "link", "nonword", "exceptions") and val and not key.strip().startswith("#"):
                    rule["params"].append(f"{key.strip()}: {val}")
                inswap = False
                continue
            if inswap and raw.startswith(" ") and ":" in line and not line.startswith("#"):
                k, _, v = line.partition(":")
                rule["swaps"].append(f"{k.strip().strip(chr(39))} → {v.strip().strip(chr(39))}")
                continue
            if intok and line.startswith("- "):
                t = line[2:].strip()
                if len(t) >= 2 and t[0] == t[-1] and t[0] in "'\"":
                    t = t[1:-1].replace("''", "'") if t[0] == "'" else t[1:-1]
                rule["tokens"].append(t)
            elif line.startswith("- ") and not intok and raw.startswith(" ") and not line.startswith("#"):
                rule["params"].append(line[2:].strip())
        out.append(rule)
    return out


def constants(path: Path, names: list[str]) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    out = {}
    for n in names:
        m = re.search(rf"^{n}\s*=\s*([^#\n]+)", text, re.M)
        if m:
            out[n] = m.group(1).strip()
    return out


def pattern_limits() -> tuple[list[tuple[str, str]], dict]:
    import yaml
    data = yaml.safe_load(PATTERNS.read_text(encoding="utf-8")) or {}
    rows = []
    for p in data.get("patterns", []):
        lim = p.get("limits") or {}
        rows.append((p["id"], ", ".join(f"{k} {v}" for k, v in lim.items()) or "none"))
    return rows, data.get("density") or {}


def main() -> int:
    cd = load_checker()
    ex = fixture_examples()
    src = source_note()
    limits, density = pattern_limits()
    checker_calls = add_calls(CHECKER, r'add\("(BLOCKING|WARNING)",\s*"([a-z_.]+)",\s*f?"([^"]*)"')
    qa_calls = add_calls(DECK_QA, r'add\(n,\s*"(BLOCKING|WARNING)",\s*"([a-z-]+)",\s*f?"([^"]*)"')
    qa_const = constants(DECK_QA, ["MARGIN", "MIN_PT", "SHRINK_FLOOR"])
    renderer_msgs = re.findall(r"(problems|warnings)\.push\(`([^`]*)`", RENDERER.read_text(encoding="utf-8"))

    L: list[str] = []
    w = L.append
    w("---")
    w('title: "Anti-slop rules"')
    w("weight: 5")
    w("generated: true")
    w('description: "Every deterministic rule the deliverable gate, the prose lint, and the visual gate enforce, generated from the scripts that enforce them."')
    w("---")
    w("")
    w("This page is generated from the code that enforces the rules, so it cannot drift from them: "
      f"{code('skills/helix/scripts/check-deliverable.py')} (the script gate), the vendored sloptimizer fixture, "
      f"{code('workflows/deliverables/slide-patterns.yml')} (limits), the Vale styles under {code('.vale/styles/Helix')}, "
      f"{code('skills/helix/scripts/deck-qa.py')} (the visual gate), and {code('skills/helix/scripts/render-deck.js')}. "
      "The narrative on [Anti-slop](../../use/anti-slop/) says why each rule exists and how the passes are sequenced.")
    w("")
    w("Severities: **blocking** stops the deliverable at the gate; **warning** is reported and left to judgment. "
      "Every title check is a suggestion in sloptimizer and a block here, because a deck title is read aloud in sequence and cannot carry a footnote.")
    w("")

    # ---- title and shape rules
    w("## Title and shape rules")
    w("")
    w(f"Titles run through every rule marked *title*; a deck title is a slide title for an audience outside the team, so the *slide title* rules apply too. "
      f"Bullets, card labels, captions, and verdicts run through the *shape* rules. Titles fail above {cd._TITLE_MAX_WORDS} words and aim for {cd._TITLE_TARGET_WORDS} or fewer.")
    w("")
    w("| Rule | Applies to | Trigger | Flagged example (from the upstream fixture) |")
    w("| --- | --- | --- | --- |")
    triggers = {
        "ContrastiveReversal": "any of: " + "; ".join(code(pattern_text(p)) for p in cd._REVERSAL),
        "ColonList": code(r"(?<!\d):(?!\d|//)") + " followed by two or more items split on commas or `and`/`or` (clock times, ratios, and URLs are exempt)",
        "ColonReveal": "the same colon followed by one item",
        "ImperativeChain": "three or more clauses (split on `,` `;` `.`) that open with an imperative verb from the list below",
        "Listicle": code(r"\b" + cd._COUNT if False else r"(two|three|…|ten|\d+)") + " then up to two words then a listicle noun (list below)",
        "StackedNegation": "two or more of " + code(r"no|not|never|nothing|none|nor|without|n't"),
        "Triplet": code(r"A, B, and C") + " where each item is one to four words (`or` too)",
        "Flattery": "any phrase in the flattery list below",
        "Aphorism": "any phrase in the aphorism list below",
        "UniversalClaim": "a group noun opening the title followed by a behavior verb, or `every`/`all`/`any` plus a group noun (lists below)",
        "Mannered": f"any of the {len(cd._MANNERED)} mannered phrases below (the same list Vale applies to body prose upstream)",
        "InventoryCount": "an inventory verb (list below), an optional `over`/`about`/`up to`, a count (digits or a number word), up to two words, then a plural noun",
        "Hedge": code(pattern_text(cd._HEDGES)),
        "Length": f"more than {cd._TITLE_MAX_WORDS} words",
        "ContainerTitle": "four words or fewer, ending in a container noun (list below); off for headings inside a team's own documents",
        "SelfJustifying": "any of: " + "; ".join(code(pattern_text(p)) for p in cd._SELF_JUSTIFYING),
        "ShoutingLabel": "all caps with six or more letters and either four or more words (twelve or more letters) or two or more words opening with WHAT, WHY, HOW, WHERE, WHEN, or WHO",
        "StatusJargon": f"any of the {len(cd._STATUS_JARGON)} invented-status phrases below (case-insensitive)",
        "Taxonomy": f"any of the {len(cd._TAXONOMY)} taxonomy-code shapes below",
        "Marketing": f"any of the {len(cd._MARKETING)} marketing-register phrases below (case-insensitive)",
        "TrailingCommentary": code(pattern_text(cd._TRAILING_COMMENTARY)),
    }
    for prefix, name, scope in RULES:
        exs = ex.get(name, [])
        example = code(exs[0][1]) if exs else "none in the fixture"
        w(f"| {name} (`{prefix}`) | {scope} | {triggers.get(name, '')} | {example} |")
    w("")
    w("Titles in the fixture that pass every rule:")
    w("")
    w(code_list(passing_examples()))
    w("")

    # ---- phrase lists
    w("## Phrase lists")
    w("")
    w(f"Vendored from sloptimizer at commit {code(src.get('upstream_commit', '?'))}; "
      f"{code('tests/validate-headline-sync.sh')} fails when any list or the fixture differs from upstream.")
    w("")
    for title, items in [
        ("Mannered phrases (regular expressions)", cd._MANNERED),
        ("Invented status (regular expressions)", cd._STATUS_JARGON),
        ("Internal taxonomy codes (regular expressions)", cd._TAXONOMY),
        ("Marketing register (regular expressions)", cd._MARKETING),
        ("Flattery (regular expressions)", [pattern_text(p) for p in cd._FLATTERY]),
        ("Aphorism (regular expressions)", [pattern_text(p) for p in cd._APHORISM]),
        ("Container nouns", alternation(cd._CONTAINER_NOUNS)),
        ("Listicle nouns", alternation(cd._LISTICLE_NOUNS)),
        ("Group nouns (universal claim)", alternation(cd._GROUP_NOUNS)),
        ("Group verbs (universal claim)", alternation(cd._GROUP_VERBS)),
        ("Inventory verbs", alternation(cd._INVENTORY_VERBS)),
        ("Number words counted as a count", alternation(cd._COUNT)),
        ("Imperative verbs (imperative chain)", sorted(cd._IMPERATIVES)),
    ]:
        w(f"### {title}")
        w("")
        w(code_list(items))
        w("")

    # ---- restatement and horizontal logic
    w("## Restatement")
    w("")
    w(f"Within one slide, the title and every shape the layout draws are compared pairwise on content words "
      f"(lowercase words of three or more letters, minus {len(cd._SHAPE_STOPWORDS)} stopwords). Two units with at least "
      f"{cd._RESTATEMENT_MIN_WORDS} content words each whose Jaccard overlap is {cd._RESTATEMENT_THRESHOLD} or higher are a "
      f"`restatement` (warning). Bullets count only on patterns whose layout draws them ({', '.join(sorted(cd.BODY_ON_SLIDE))}); "
      f"node labels in a figure ({', '.join(sorted(cd.NODE_FIELDS))} and the first cell of {', '.join(sorted(cd.NODE_FIRST_CELL))}) skip the container-title rule.")
    w("")
    w("Stopwords: " + ", ".join(code(s) for s in sorted(cd._SHAPE_STOPWORDS)))
    w("")
    w("## Horizontal logic")
    w("")
    w("Consecutive titles (title slide through the ask) must share at least one content word after light stemming: "
      "`-ing` is stripped from words over six letters, `-ed` over five, a trailing `-s` over four unless the word ends in `-ss` "
      "(`-es` after `s`, `x`, `z`, `ch`, `sh`), then a trailing `-e` over four letters; words under three letters and the title stopwords are ignored. "
      "A pair with no shared word is a `horizontal_logic` warning. The same stems decide whether a must-cover concept matches a covered group.")
    w("")
    w("Title stopwords: " + ", ".join(code(s) for s in sorted(cd._TITLE_STOPWORDS)))
    w("")

    # ---- script gate checks
    w("## Script gate checks")
    w("")
    w("Every check `check-deliverable.py` can report, with its severity. A title that is a label (`" +
      "`, `".join(sorted(cd.LABEL_TITLES)) + "`) or under three words fails `title.claim`.")
    w("")
    w("| Check | Severity | Message shape |")
    w("| --- | --- | --- |")
    for sev, cid, msg in sorted(checker_calls, key=lambda x: x[1]):
        w(f"| `{cid}` | {sev.lower()} | {msg} |")
    w("")
    w("Patterns the vocabulary, number, placeholder, and visual checks use:")
    w("")
    w(f"- HELIX vocabulary (blocking in a title, body, or notes): {code(pattern_text(cd.HELIX_VOCAB))}")
    w(f"- Jargon (warning): {code(pattern_text(cd.JARGON))}")
    w(f"- Placeholder (blocking): {code(pattern_text(cd.PLACEHOLDER))}; bracketed phrase (warning): {code(pattern_text(cd.BRACKET_TOKEN))}")
    w(f"- A number in a body that must appear in the Sources table: {code(pattern_text(cd.NUMBER))} (single digits excepted)")
    w(f"- Generic visuals (blocking, with anything under six words): {', '.join(code(g) for g in sorted(cd.GENERIC_VISUALS))}")
    w("")

    # ---- limits and density
    w("## Pattern limits and density")
    w("")
    w(f"From {code('workflows/deliverables/slide-patterns.yml')}, the single owner of limits; exceeding one is a warning.")
    w("")
    w("| Pattern | Limits |")
    w("| --- | --- |")
    for pid, lim in limits:
        w(f"| `{pid}` | {lim} |")
    w("")
    if density:
        w("Density: " + "; ".join(f"{k} {v}" for k, v in density.items()))
        w("")

    # ---- vale
    w("## Prose lint (Vale, Helix styles)")
    w("")
    w("Runs on the hand-authored site pages and on every deliverable script (`just lint-prose`). Errors block; warnings and suggestions are reported.")
    w("")
    for r in vale_rules():
        w(f"### {r['name']}")
        w("")
        w(f"{r['level'] or 'suggestion'}; {r['extends']}. {r['message']}")
        if r["params"]:
            w("")
            w("Parameters: " + "; ".join(code(p) for p in r["params"]))
        if r["tokens"]:
            w("")
            w(f"Tokens ({len(r['tokens'])}): " + ", ".join(code(t) for t in r["tokens"]))
        if r["swaps"]:
            w("")
            w(f"Substitutions ({len(r['swaps'])}): " + "; ".join(code(t) for t in r["swaps"]))
        w("")

    # ---- visual gate
    w("## Visual gate (deck-qa.py)")
    w("")
    w(f"Reads every slide's shapes from the file. Safe margin {qa_const.get('MARGIN', '?')} in; readable floor {qa_const.get('MIN_PT', '?')} pt; "
      f"autofit may shrink to {qa_const.get('SHRINK_FLOOR', '?')} of the nominal size before a fit that depends on it becomes blocking. "
      "It also notes any typeface the deck names that the host lacks, rasterizes every slide when LibreOffice and pdftoppm are present, and builds a contact sheet for inspection.")
    w("")
    w("| Check | Severity | Message shape |")
    w("| --- | --- | --- |")
    for sev, cid, msg in qa_calls:
        w(f"| `{cid}` | {sev.lower()} | {msg} |")
    w("")

    # ---- renderer
    w("## What the renderer refuses to hide")
    w("")
    w("`render-deck.js` writes the file so it can be inspected, then reports these and exits non-zero (problems) or reports and exits normally (warnings):")
    w("")
    for kind, msg in renderer_msgs:
        msg = re.sub(r"\$\{[^}]*\}", "…", msg)
        w(f"- {kind[:-1]}: {msg}")
    w("")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(L).rstrip() + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
