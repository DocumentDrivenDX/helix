#!/usr/bin/env python3
"""corpus-inventory — what a corpus contains, before anyone decides what to say.

Scans a declared scope of Markdown files and prints an inventory the present
mode distills from: one row per document (authority rank, type, title, the
claims its headings make, size) and a corpus-level concept list (terms that
recur across documents, weighted by authority and spread). The script is
deterministic and dumb on purpose: it surfaces candidates and counts; the
mode does the synthesis and must account for every top concept as covered
or omitted.

Usage:
    corpus-inventory.py <path-or-glob> [<path-or-glob> ...] [--top N]
                        [--format md|json] [--min-docs 2]

Authority rank comes from the HELIX activity directory (00-discover highest)
and from the document kind (a README or principles file ranks with frame);
anything else ranks last. Ranks are 1 (highest) to 9.
"""
from __future__ import annotations

import argparse
import glob
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

STOP = set("""a an the and or but of to in on at by for with from into than that this these those it its is are was
were be been as if when once while before after not no so you your we our they their one each every any all can
will now then here there what who how per own back up out under over more less most much very just only also
which where why does do did done has have had may might must should would could shall let use used using via
between within without across about above below same other such than too both either neither into onto upon
whether while yet still even ever never often always sometimes already again against along among around because
through during until since toward towards off down new old first last next same own like new per""".split())
KIND_RANK = {"00-discover": 1, "01-frame": 2, "02-design": 3, "03-test": 4, "04-build": 5, "05-deploy": 6, "06-iterate": 7}
GENERIC = set("""section overview summary introduction purpose background references notes example examples
template checklist review status details detail context document documents artifact artifacts file files page
pages activity activities table list item items part parts step steps type types md yml yaml current points
given state changes change source sources content reference owner owners project problem problems install
claude codex genie grok ddx feat- helix-feat helix work works working need needs needed provide provides
provided include includes including support supports supported related relevant specific general single
multiple following existing required optional level levels number name names value values field fields
line lines text description descriptions data information way ways time times case cases""".split())


def frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    fm: dict = {}
    for line in text[4:end].splitlines():
        m = re.match(r"^\s{0,4}(id|type|status|kind|activity):\s*(.+)$", line)
        if m and m.group(1) not in fm:
            fm[m.group(1)] = m.group(2).strip().strip('"')
    return fm, text[end + 5:]


def rank_for(path: Path) -> int:
    for part in path.parts:
        if part in KIND_RANK:
            return KIND_RANK[part]
    name = path.name.lower()
    if name in ("readme.md", "principles.md", "product-vision.md"):
        return 2
    if name in ("conventions.md", "ratchets.md", "artifact-hierarchy.md", "artifact-schema.md"):
        return 3
    return 9


def phrases(text: str) -> Counter:
    """Candidate concept phrases: 1- to 3-word runs of content words."""
    c: Counter = Counter()
    for sentence in re.split(r"[.!?\n|]", text):
        words = [w.lower() for w in re.findall(r"[A-Za-z][A-Za-z-]{2,}", sentence)]
        for n in (1, 2, 3):
            for i in range(len(words) - n + 1):
                run = words[i:i + n]
                if run[0] in STOP or run[-1] in STOP or any(w in GENERIC for w in run):
                    continue
                if n == 1 and (len(run[0]) < 6 or run[0] in GENERIC):
                    continue
                # phrases carry meaning; single words mostly carry noise
                c[" ".join(run)] += {1: 0.35, 2: 1.0, 3: 1.2}[n]
    return c


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--top", type=int, default=40)
    ap.add_argument("--min-docs", type=int, default=2, help="a concept must appear in at least this many documents")
    ap.add_argument("--format", choices=["md", "json"], default="md")
    args = ap.parse_args()

    files: list[Path] = []
    for pat in args.paths:
        p = Path(pat)
        if p.is_dir():
            files += sorted(p.rglob("*.md"))
        else:
            files += [Path(x) for x in sorted(glob.glob(pat, recursive=True))]
    files = [f for f in dict.fromkeys(files) if f.is_file()]
    if not files:
        print("no files in scope", file=sys.stderr)
        return 2

    docs = []
    doc_terms: dict[str, set[str]] = defaultdict(set)
    weighted: Counter = Counter()
    for f in files:
        text = f.read_text(encoding="utf-8", errors="ignore")
        fm, body = frontmatter(text)
        title = next((l[2:].strip() for l in body.splitlines() if l.startswith("# ")), f.stem)
        h2 = [l[3:].strip() for l in body.splitlines() if l.startswith("## ")]
        words = len(re.findall(r"\w+", body))
        first = next((p.strip() for p in body.split("\n\n") if p.strip() and not p.strip().startswith(("#", "|", "-", "```", "<", "!", "*"))), "")
        rank = rank_for(f)
        # concept candidates come from headings, bold terms, and the first paragraph (where authors state claims)
        claim_text = " ".join([title] + h2 + re.findall(r"\*\*([^*]{3,60})\*\*", body) + [first])
        c = phrases(claim_text)
        # body phrases at a lower weight, capped so long documents do not drown short authoritative ones
        cb = phrases(body)
        for term, n in cb.most_common(200):
            c[term] += min(n, 5) * 0.2
        weight = {1: 3.0, 2: 3.0, 3: 2.0, 4: 1.5, 5: 1.5, 6: 1.2, 7: 1.2, 9: 1.0}[rank]
        for term, n in c.items():
            weighted[term] += n * weight
            doc_terms[term].add(str(f))
        docs.append({"path": str(f), "rank": rank, "type": fm.get("type") or fm.get("kind") or "", "id": fm.get("id", ""),
                     "status": fm.get("status", ""), "title": title, "h2": h2, "words": words, "first": first[:240]})

    concepts = []
    for term, score in weighted.most_common():
        spread = len(doc_terms[term])
        if spread < args.min_docs:
            continue
        concepts.append({"concept": term, "score": round(score * (1 + 0.15 * spread), 1), "documents": spread})
    concepts.sort(key=lambda x: -x["score"])
    # drop near-duplicates: a shorter term contained in a higher-ranked longer one, or vice versa with lower spread
    kept: list[dict] = []
    for c in concepts:
        if any(c["concept"] in k["concept"] or k["concept"] in c["concept"] for k in kept):
            continue
        kept.append(c)
        if len(kept) >= args.top:
            break

    docs.sort(key=lambda d: (d["rank"], d["path"]))
    if args.format == "json":
        print(json.dumps({"documents": docs, "concepts": kept}, indent=2))
        return 0
    print(f"# Corpus inventory: {len(docs)} documents, {sum(d['words'] for d in docs):,} words\n")
    print("## Documents by authority\n")
    print("| Rank | Path | Type | Title | Words | Sections |")
    print("|---|---|---|---|---|---|")
    for d in docs:
        print(f"| {d['rank']} | {d['path']} | {d['type']} | {d['title'][:60]} | {d['words']} | {'; '.join(d['h2'])[:160]} |")
    print("\n## Concepts by weighted recurrence (top %d, in at least %d documents)\n" % (len(kept), args.min_docs))
    print("| # | Concept | Score | Documents |")
    print("|---|---|---|---|")
    for i, c in enumerate(kept, 1):
        print(f"| {i} | {c['concept']} | {c['score']} | {c['documents']} |")
    print("\nThe mode clusters these into concept groups, ranks the groups against the audience's decision, and marks every group covered or omitted in the deliverable's Story section.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
