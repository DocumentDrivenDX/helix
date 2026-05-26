#!/usr/bin/env python3
"""Deterministic structural checks for the HELIX reconcile-alignment review.

This computes the *reproducible floor* of an impl-vs-spec alignment review: the
per-dimension denominators (how many ADRs / NFRs / ACs / subsystems exist and
how many were structurally accounted for) and the structural findings that can
be decided by parsing files alone. The stochastic, judgement-bearing checks —
does a cited test actually *exercise* that AC, is an ADR's *decision* honored in
code, is a concern's *behavioral* practice realized, is an NFR *target* met —
remain the model's job in reconcile-alignment STEP 3. This tool gives that review
reproducible inputs so the same spec stack yields the same denominators across
runtimes (claude / codex / ddx).

Cross-platform: Python 3 standard library only — no third-party packages, no
runtime/tracker dependency. It reads the spec stack (markdown) and greps the
code tree for `@covers` citations. Any agent platform that can run `python3`
can run it.

Usage:
    helix_align_check.py [--docs-root docs/helix] [--code-root .]
                         [--format json|text] [--strict]

Exit codes: 0 = ran (report-only); 2 = blocking structural findings and --strict.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

# ---- parsing anchors (must match reconcile-alignment.md / it.37 canonical forms)
RE_SUBSYSTEM = re.compile(r"^###\s+Subsystem:\s*(.+?)\s*$", re.MULTILINE)
RE_FR = re.compile(r"\*\*FR-(\d+)\*\*")
RE_FR_REF = re.compile(r"\bFR-(\d+)\b")
RE_COVERED_SUBSYS = re.compile(r"\*\*Covered PRD Subsystem\(s\)\*\*\s*:\s*(.+)")
RE_COVERED_REQS = re.compile(r"\*\*Covered PRD Requirements\*\*\s*:\s*(.+)")
RE_CROSS_RATIONALE = re.compile(r"\*\*Cross-Subsystem Rationale\*\*\s*:\s*(.*)")
RE_US_FEATURE = re.compile(r"\*\*Feature\*\*\s*:\s*(FEAT-\d+)")
RE_AC_ID = re.compile(r"\b(US-\d+-AC\d+)\b")
RE_COVERS = re.compile(r"@covers\s+(US-\d+-AC\d+)")
RE_FEAT_FILE = re.compile(r"^FEAT-(\d{3})-.+\.md$")
RE_US_FILE = re.compile(r"^US-(\d{3})-.+\.md$")
RE_ADR_FILE = re.compile(r"^ADR-(\d{3})-.+\.md$")
RE_ADR_STATUS_KV = re.compile(r"^[\s>*-]*\*{0,2}status\*{0,2}\s*[:=]\s*\*{0,2}([A-Za-z][A-Za-z _-]*)",
                              re.IGNORECASE | re.MULTILINE)
RE_ADR_STATUS_HEAD = re.compile(r"^#{1,6}\s+status\s*$", re.IGNORECASE | re.MULTILINE)
ADR_STATUS_VOCAB = ["superseded", "deprecated", "rejected", "accepted", "proposed", "draft"]
RE_NFR_HEADING = re.compile(r"^#{1,4}\s+.*(non[- ]?functional|NFR).*$", re.IGNORECASE | re.MULTILINE)
RE_NFR_REF = re.compile(r"\bNFR-?\d+\b|\bnon[- ]?functional\b", re.IGNORECASE)

# @covers citations count only when they live in an EXECUTABLE test/source file —
# unit tests, shell/bats tests, gherkin .feature files. Markdown/MDX/YAML are
# deliberately excluded: a `@covers` in a test-plan doc or prose is documentation
# of intent, not an exercising test, and counting it would inflate the citation
# floor — exactly the gameable phantom the exercise-not-just-cite rule guards against.
CODE_EXT = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".py", ".go", ".rs",
            ".java", ".kt", ".rb", ".scala", ".swift", ".cs", ".php",
            ".sh", ".bats", ".feature"}
SKIP_DIRS = {"node_modules", ".git", "dist", "build", ".next", "out", "vendor",
             "target", "__pycache__", ".turbo", "coverage", ".venv",
             # vendored agent/skill trees carry the methodology's own EXAMPLE @covers
             # citations — scanning them yields phantom/dangling citations, so skip them.
             ".agents", ".claude", ".ddx", ".cursor", ".github"}


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().lower()


def read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def find_files(root: Path, pattern: re.Pattern) -> list[Path]:
    out = []
    if not root.exists():
        return out
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for fn in sorted(filenames):
            if pattern.match(fn):
                out.append(Path(dirpath) / fn)
    return sorted(out, key=str)


# ---------------------------------------------------------------- parse the stack
def parse_prd(docs_root: Path) -> tuple[list[str], list[str], Path | None]:
    prd = None
    for cand in (docs_root / "01-frame" / "prd.md",):
        if cand.exists():
            prd = cand
            break
    if prd is None:
        hits = find_files(docs_root, re.compile(r"^prd\.md$"))
        prd = hits[0] if hits else None
    if prd is None:
        return [], [], None
    text = read(prd)
    subsystems = [m.strip() for m in RE_SUBSYSTEM.findall(text)]
    frs = sorted({f"FR-{n}" for n in RE_FR.findall(text)}, key=lambda x: int(x.split("-")[1]))
    return subsystems, frs, prd


def parse_feats(docs_root: Path) -> dict:
    feats = {}
    for f in find_files(docs_root, RE_FEAT_FILE):
        text = read(f)
        fid = "FEAT-" + RE_FEAT_FILE.match(f.name).group(1)
        subs_m = RE_COVERED_SUBSYS.search(text)
        reqs_m = RE_COVERED_REQS.search(text)
        rat_m = RE_CROSS_RATIONALE.search(text)
        subs = [s.strip() for s in re.split(r"[;,]", subs_m.group(1))] if subs_m else []
        subs = [s for s in subs if s]
        reqs = [f"FR-{n}" for n in RE_FR_REF.findall(reqs_m.group(1))] if reqs_m else []
        rationale = bool(rat_m and rat_m.group(1).strip())
        feats[fid] = {"file": str(f), "subsystems": subs, "requirements": reqs,
                      "cross_rationale": rationale}
    return feats


def parse_stories(docs_root: Path) -> dict:
    stories = {}
    for f in find_files(docs_root, RE_US_FILE):
        text = read(f)
        sid = "US-" + RE_US_FILE.match(f.name).group(1)
        feat_m = RE_US_FEATURE.search(text)
        acs = sorted(set(RE_AC_ID.findall(text)))
        stories[sid] = {"file": str(f), "feature": feat_m.group(1) if feat_m else None,
                        "acs": acs}
    return stories


def _to_vocab(value: str) -> str | None:
    v = value.strip().lower()
    for s in ADR_STATUS_VOCAB:
        if re.search(rf"\b{s}\b", v):
            return s
    return None


def extract_adr_status(text: str) -> str:
    """Read an ADR status only from the structured places it is declared — a
    frontmatter / inline `status:` (or `**Status**:`) line, a `## Status`
    heading, or a status-table column — and normalize it to a known status
    vocabulary word. Anything else is `unstated`: we do NOT guess from prose,
    which would misread an 'Alternatives: ... rejected' mention as the decision
    status."""
    m = RE_ADR_STATUS_KV.search(text)
    if m:
        v = _to_vocab(m.group(1))
        if v:
            return v
    h = RE_ADR_STATUS_HEAD.search(text)
    if h:
        for line in text[h.end():].splitlines():
            s = line.strip().strip("*").strip()
            if s:
                return _to_vocab(s) or "unstated"
    rows = [ln for ln in text.splitlines() if ln.count("|") >= 2]
    for i, ln in enumerate(rows[:-1]):
        cells = [c.strip().lower() for c in ln.strip().strip("|").split("|")]
        if "status" in cells:
            idx = cells.index("status")
            for data in rows[i + 1:]:
                dcells = [c.strip() for c in data.strip().strip("|").split("|")]
                if set("".join(dcells)) <= set("-: "):  # separator row
                    continue
                if idx < len(dcells):
                    return _to_vocab(dcells[idx]) or "unstated"
                break
            break
    return "unstated"


def parse_adrs(docs_root: Path) -> tuple[dict, list[str]]:
    adrs, naming = {}, []
    # case-insensitive discovery so lowercase/4-digit names are *found* then flagged
    for dirpath, dirnames, filenames in os.walk(docs_root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for fn in sorted(filenames):
            if re.match(r"^adr[-_].+\.md$", fn, re.IGNORECASE):
                f = Path(dirpath) / fn
                if not RE_ADR_FILE.match(fn):
                    naming.append(f"{fn}: non-canonical (want ADR-NNN-<name>.md, uppercase 3-digit)")
                m = re.match(r"^[Aa][Dd][Rr][-_](\d+)", fn)
                aid = "ADR-" + (m.group(1) if m else "?")
                status = extract_adr_status(read(f))
                adrs[str(f)] = {"id": aid, "file": str(f), "status": status}
    return adrs, sorted(naming)


def scan_covers(code_root: Path) -> dict:
    cited = {}
    if not code_root.exists():
        return cited
    for dirpath, dirnames, filenames in os.walk(code_root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for fn in sorted(filenames):
            if Path(fn).suffix.lower() not in CODE_EXT:
                continue
            f = Path(dirpath) / fn
            for ac in RE_COVERS.findall(read(f)):
                cited.setdefault(ac, []).append(str(f))
    return {ac: sorted(set(files)) for ac, files in cited.items()}


# --------------------------------------------------------------------- run checks
def run(docs_root: Path, code_root: Path) -> dict:
    findings: list[dict] = []

    def add(check, severity, classification, detail):
        findings.append({"check": check, "severity": severity,
                         "classification": classification, "detail": detail})

    subsystems, frs, prd = parse_prd(docs_root)
    feats = parse_feats(docs_root)
    stories = parse_stories(docs_root)
    adrs, adr_naming = parse_adrs(docs_root)
    cited = scan_covers(code_root)

    # --- Decomposition: subsystem -> FEAT
    covered_subs = {norm(s) for ft in feats.values() for s in ft["subsystems"]}
    if subsystems and not feats:
        add("subsystem->FEAT", "blocking", "UNDERSPECIFIED",
            "PRD declares subsystems but the frame has zero FEAT specs (PRD->stories, skipping the feature tier)")
    for s in subsystems:
        if norm(s) not in covered_subs:
            add("subsystem->FEAT", "blocking", "INCOMPLETE",
                f"subsystem '{s}' is named by no FEAT's Covered PRD Subsystem(s)")
    # --- Decomposition: FR -> FEAT
    covered_frs = {fr for ft in feats.values() for fr in ft["requirements"]}
    for fr in frs:
        if fr not in covered_frs:
            add("FR->FEAT", "blocking", "INCOMPLETE",
                f"{fr} is listed in no FEAT's Covered PRD Requirements")
    # --- Decomposition: FEAT -> story
    feats_with_story = {st["feature"] for st in stories.values() if st["feature"]}
    for fid in feats:
        if fid not in feats_with_story:
            add("FEAT->story", "blocking", "INCOMPLETE",
                f"{fid} is named by no user story's **Feature** field")
    # --- Mega-FEAT (advisory)
    for fid, ft in feats.items():
        if len(ft["subsystems"]) > 1 and not ft["cross_rationale"]:
            add("mega-FEAT", "advisory", "UNDERSPECIFIED",
                f"{fid} covers {len(ft['subsystems'])} subsystems with no **Cross-Subsystem Rationale** (likely split)")
    # --- Story Feature header present
    for sid, st in stories.items():
        if not st["feature"]:
            add("story-feature-link", "advisory", "UNDERSPECIFIED",
                f"{sid} has no **Feature**: FEAT-NNN header")
    # --- Naming
    for n in adr_naming:
        add("adr-naming", "advisory", "UNDERSPECIFIED", n)
    mono = find_files(docs_root, re.compile(r"^user-stories\.md$"))
    for m in mono:
        add("story-granularity", "advisory", "UNDERSPECIFIED",
            f"{m}: monolithic user-stories.md (want one file per story US-NNN-<slug>.md)")

    # --- Acceptance: @covers citation inventory (presence only; exercise = stochastic)
    all_acs = sorted({ac for st in stories.values() for ac in st["acs"]})
    acs_cited = [ac for ac in all_acs if ac in cited]
    acs_uncited = [ac for ac in all_acs if ac not in cited]
    dangling = sorted([ac for ac in cited if ac not in set(all_acs)])
    for ac in acs_uncited:
        add("ac-citation", "advisory", "NO_CITATION",
            f"{ac} has no @covers citation in the scanned code tree — deterministic fact only; "
            f"the model classifies UNTESTED vs UNCITED_COVERAGE by checking for an exercising test")
    for ac in dangling:
        add("ac-citation", "blocking", "ASSERTED_UNBACKED",
            f"@covers {ac} cites an AC id that exists in no user story ({', '.join(cited[ac])})")

    # --- ADR inventory
    adr_status = {}
    for a in adrs.values():
        adr_status[a["status"]] = adr_status.get(a["status"], 0) + 1
    adr_status = dict(sorted(adr_status.items()))

    # --- NFR candidate artifacts: a SEARCH POINTER for the model, NOT an NFR-item count.
    #     NFR items are not reliably parseable, so the model extracts and verifies them.
    nfr_files = []
    for f in find_files(docs_root, re.compile(r".+\.md$")):
        text = read(f)
        if RE_NFR_HEADING.search(text) or RE_NFR_REF.search(text):
            nfr_files.append(str(f))

    # --- parser warnings: when canonical anchors are absent, a zero denominator is
    #     INDETERMINATE, not a clean floor — surface that so 0 is never misread as aligned.
    warnings = []
    if not prd:
        warnings.append("No prd.md under docs-root; capability/decomposition denominators are indeterminate.")
    else:
        if not subsystems:
            warnings.append("PRD found but no `### Subsystem:` headings (non-canonical PRD); "
                            "subsystem->FEAT coverage is indeterminate, not clean.")
        if not frs:
            warnings.append("PRD found but no `**FR-n**` requirement IDs; FR->FEAT coverage is indeterminate.")
    if not stories and feats:
        warnings.append("No canonical US-NNN-<slug>.md story files, but FEAT specs exist — stories may be "
                        "inline in feature specs (not parsed); the AC denominator is UNDERSTATED, not zero.")
    elif not stories:
        warnings.append("No canonical US-NNN-<slug>.md story files found; the AC denominator is indeterminate.")

    # --- Coverage-matrix INPUTS (deterministic floor only). These are inputs the model
    #     assembles into the Step-4-classified Dimension Coverage Matrix — the script
    #     assigns NO Step 4 classification and leaves model-only dimensions uncomputed.
    def counts(check_set):
        b = sum(1 for f in findings if f["check"] in check_set and f["severity"] == "blocking")
        a = sum(1 for f in findings if f["check"] in check_set and f["severity"] == "advisory")
        return b, a

    def sstatus(b, a, indeterminate=False):
        if indeterminate:
            return "indeterminate (canonical anchors absent — see parser_warnings)"
        if b:
            return "blocking-findings"
        if a:
            return "advisory-findings"
        return "clean (structural floor)"

    cap_b, cap_a = counts({"FR->FEAT"})
    ac_b, ac_a = counts({"ac-citation"})
    dec_b, dec_a = counts({"subsystem->FEAT", "FEAT->story", "mega-FEAT",
                           "story-feature-link", "story-granularity"})
    frs_covered = len([fr for fr in frs if fr in {x for ft in feats.values() for x in ft["requirements"]}])
    matrix_inputs = [
        {"dimension": "Capability (FR)", "computed": True, "found": len(frs), "checked": len(frs),
         "blocking_findings": cap_b, "advisory_findings": cap_a,
         "structural_status": sstatus(cap_b, cap_a, indeterminate=(not prd) or (bool(prd) and not frs)),
         "detail": f"{len(frs)} FRs; {frs_covered} covered by a FEAT",
         "model_completes": "verify each FR is implemented in code (code->spec surface map)"},
        {"dimension": "Acceptance behavior", "computed": True, "found": len(all_acs), "checked": len(all_acs),
         "blocking_findings": ac_b, "advisory_findings": ac_a,
         "structural_status": sstatus(ac_b, ac_a, indeterminate=not all_acs),
         "detail": f"{len(acs_cited)}/{len(all_acs)} ACs have a @covers citation; {len(dangling)} dangling",
         "model_completes": "verify each cited test EXERCISES that exact AC; classify uncited ACs UNTESTED vs UNCITED_COVERAGE"},
        {"dimension": "Architecture decision (ADR)", "computed": True, "found": len(adrs), "checked": len(adrs),
         "blocking_findings": 0, "advisory_findings": len(adr_naming),
         "structural_status": sstatus(0, len(adr_naming)),
         "detail": f"{len(adrs)} ADRs; status {adr_status or '{}'}",
         "model_completes": "verify each accepted ADR's decision is honored in code; no contradicting surface"},
        {"dimension": "Concern practice", "computed": False, "found": None, "checked": None,
         "blocking_findings": 0, "advisory_findings": 0, "structural_status": "model-required",
         "detail": "this checker does not inspect concern practices",
         "model_completes": "verify each active concern's behavioral practices are realized in code (not just tooling wired)"},
        {"dimension": "Measurable NFR / budget", "computed": False, "found": None, "checked": None,
         "blocking_findings": 0, "advisory_findings": 0, "structural_status": "model-required",
         "detail": f"{len(nfr_files)} candidate artifact(s) mention NFR / non-functional (search pointer, NOT an NFR-item count)",
         "model_completes": "extract stated NFR targets and verify each is met / has evidence"},
        {"dimension": "Decomposition", "computed": True,
         "found": len(subsystems) + len(feats) + len(stories),
         "checked": len(subsystems) + len(feats) + len(stories),
         "blocking_findings": dec_b, "advisory_findings": dec_a,
         "structural_status": sstatus(dec_b, dec_a, indeterminate=(bool(prd) and not subsystems)),
         "detail": f"{len(subsystems)} subsystems / {len(feats)} FEATs / {len(stories)} stories",
         "model_completes": None},
        {"dimension": "Slot / instrument", "computed": False, "found": None, "checked": None,
         "blocking_findings": 0, "advisory_findings": 0, "structural_status": "model-required",
         "detail": "Slot-Registry + Instrument-Integrity read the workflows/concerns tree, not this docs-root",
         "model_completes": "run the deterministic Slot-Registry Integrity check (slots.yml vs concern ## Slot) separately"},
    ]

    blocking = sum(1 for f in findings if f["severity"] == "blocking")
    findings.sort(key=lambda f: (f["severity"] != "blocking", f["check"], f["detail"]))
    return {
        "docs_root": str(docs_root), "code_root": str(code_root),
        "prd": str(prd) if prd else None,
        "parser_warnings": warnings,
        "dimensions": {
            "decomposition": {"subsystems": subsystems, "frs": frs,
                              "feats": dict(sorted(feats.items())),
                              "stories": {k: {"feature": v["feature"], "acs": v["acs"]}
                                          for k, v in sorted(stories.items())}},
            "acceptance": {"acs_found": len(all_acs), "acs_cited": acs_cited,
                           "acs_uncited": acs_uncited, "dangling_citations": dangling},
            "adr": {"found": len(adrs), "by_status": adr_status,
                    "items": sorted(adrs.values(), key=lambda a: a["file"]),
                    "naming_violations": adr_naming},
            "nfr": {"candidate_artifacts": nfr_files},
        },
        "coverage_matrix_inputs": matrix_inputs,
        "findings": findings,
        "blocking_count": blocking,
        "note": "Deterministic structural floor only — these are INPUTS to the Dimension "
                "Coverage Matrix, not the matrix itself. The script assigns no Step 4 "
                "classification. Semantic verdicts (cited-test-exercises-that-AC, "
                "ADR-decision-honored, concern-behavior-realized, NFR-target-met) and the "
                "model-required rows are the model's job in reconcile-alignment STEP 3.",
    }


def to_text(r: dict) -> str:
    lines = [f"HELIX align check — docs={r['docs_root']} code={r['code_root']}",
             f"  PRD: {r['prd']}"]
    if r.get("parser_warnings"):
        lines.append("")
        lines.append("Parser warnings (denominators may be indeterminate):")
        for w in r["parser_warnings"]:
            lines.append(f"  ! {w}")
    lines.append("")
    lines.append("Dimension Coverage Matrix — deterministic INPUTS (model assigns the Step 4 classification):")
    for m in r["coverage_matrix_inputs"]:
        comp = "computed" if m["computed"] else "model-only"
        found = m["found"] if m["found"] is not None else "-"
        lines.append(f"  - {m['dimension']} [{comp}]: found={found} "
                     f"blocking={m['blocking_findings']} advisory={m['advisory_findings']} "
                     f"-> {m['structural_status']}")
        lines.append(f"      {m.get('detail','')}")
        if m.get("model_completes"):
            lines.append(f"      model: {m['model_completes']}")
    lines.append("")
    lines.append(f"Findings ({len(r['findings'])}; {r['blocking_count']} blocking):")
    for f in r["findings"]:
        lines.append(f"  [{f['severity']:>8}] {f['check']} / {f['classification']}: {f['detail']}")
    if not r["findings"]:
        lines.append("  (none — structural floor clean)")
    lines.append("")
    lines.append(r["note"])
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Deterministic structural checks for HELIX reconcile-alignment.")
    ap.add_argument("--docs-root", default="docs/helix", help="HELIX spec stack root (default: docs/helix)")
    ap.add_argument("--code-root", default=None, help="code tree to scan for @covers (default: docs-root's repo)")
    ap.add_argument("--format", choices=["json", "text"], default="json")
    ap.add_argument("--strict", action="store_true", help="exit 2 if any blocking structural finding")
    args = ap.parse_args(argv)

    docs_root = Path(args.docs_root).resolve()
    if not docs_root.exists():
        print(f"error: docs-root not found: {docs_root}", file=sys.stderr)
        return 1
    code_root = Path(args.code_root).resolve() if args.code_root else _infer_code_root(docs_root)

    result = run(docs_root, code_root)
    print(json.dumps(result, indent=2) if args.format == "json" else to_text(result))
    if args.strict and result["blocking_count"]:
        return 2
    return 0


def _infer_code_root(docs_root: Path) -> Path:
    # docs/helix -> repo root (two levels up if the path ends with docs/helix)
    p = docs_root
    if p.name == "helix" and p.parent.name == "docs":
        return p.parent.parent
    return p.parent


if __name__ == "__main__":
    raise SystemExit(main())
