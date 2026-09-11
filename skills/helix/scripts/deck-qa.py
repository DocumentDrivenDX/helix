#!/usr/bin/env python3
"""deck-qa — geometry and visual QA for a rendered .pptx deck.

Usage:
    deck-qa.py <deck.pptx> [--out DIR] [--format text|json] [--no-raster]

Reads every slide's shapes straight from the OOXML (stdlib only) and reports:
text boxes that collide with other text, shapes off the slide or inside the
0.5" margin, estimated text overflow (a per-font width heuristic, honoring
autofit shrink down to a floor), tables that grow past the bottom margin,
type below 12 pt outside the footer band, and consecutive slides with the
same layout signature. When LibreOffice and pdftoppm are available it also
rasterizes the deck to DIR/slide-NN.png and a labeled DIR/contact.png
(Pillow if importable, else ImageMagick `montage`).

Exit 0 with no blocking findings, 1 with blocking findings, 2 on usage errors.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

EMU = 914400
NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main",
      "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
WIDTH_FACTOR = {"Georgia": 0.56, "Arial": 0.47, "Helvetica": 0.47, "Courier New": 0.60, "Times New Roman": 0.46}
LINE_HEIGHT = 1.2
MARGIN = 0.5          # inches; the slide's safe area
MIN_PT = 12.0         # readable floor on content slides
SHRINK_FLOOR = 0.75   # autofit may shrink to this fraction of the nominal size
SOFFICE_CANDIDATES = ["soffice", "/Applications/LibreOffice.app/Contents/MacOS/soffice", "libreoffice"]
FONT_FILES = ["/System/Library/Fonts/Supplemental/Arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
              "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"]


# ---------------------------------------------------------------- reading the deck
def inches(v: str | None, default: float = 0.0) -> float:
    return int(v) / EMU if v is not None else default


def slide_paths(z: zipfile.ZipFile) -> list[str]:
    """Slide part names in presentation order (falls back to numeric order)."""
    try:
        pres = ET.fromstring(z.read("ppt/presentation.xml"))
        rels = ET.fromstring(z.read("ppt/_rels/presentation.xml.rels"))
        target = {r.get("Id"): r.get("Target") for r in rels}
        out = []
        for sid in pres.find("p:sldIdLst", NS):
            t = target[sid.get("{%s}id" % NS["r"])]
            out.append("ppt/" + t.lstrip("/").removeprefix("ppt/"))
        if out:
            return out
    except (KeyError, ET.ParseError, TypeError):
        pass
    names = [n for n in z.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)]
    return sorted(names, key=lambda n: int(re.search(r"(\d+)", n).group(1)))


def slide_size(z: zipfile.ZipFile) -> tuple[float, float]:
    sz = ET.fromstring(z.read("ppt/presentation.xml")).find("p:sldSz", NS)
    return inches(sz.get("cx")), inches(sz.get("cy"))


def paragraphs(tx_body) -> list[dict]:
    """[{text, pt, font, bold, spc_after_pt}] for one txBody; runs collapse to the largest size."""
    out = []
    for p in tx_body.findall("a:p", NS):
        text = "".join(t.text or "" for t in p.iter("{%s}t" % NS["a"]))
        pts, fonts, bold = [], [], False
        for rpr in p.iter("{%s}rPr" % NS["a"]):
            if rpr.get("sz"):
                pts.append(int(rpr.get("sz")) / 100)
            latin = rpr.find("a:latin", NS)
            if latin is not None and latin.get("typeface"):
                fonts.append(latin.get("typeface"))
            bold = bold or rpr.get("b") == "1"
        ppr = p.find("a:pPr", NS)
        spc = ppr.find("a:spcAft/a:spcPts", NS) if ppr is not None else None
        out.append({"text": text.strip(), "pt": max(pts) if pts else 18.0, "font": fonts[0] if fonts else "Arial",
                    "bold": bold, "spc_after_pt": int(spc.get("val")) / 100 if spc is not None else 0.0})
    return out


def read_shapes(xml: bytes) -> list[dict]:
    root = ET.fromstring(xml)
    shapes = []
    tree = root.find("p:cSld/p:spTree", NS)
    for el in tree:
        tag = el.tag.split("}")[1]
        name = (el.find(".//p:cNvPr", NS).get("name") if el.find(".//p:cNvPr", NS) is not None else tag)
        xfrm = el.find("p:spPr/a:xfrm", NS) if tag in ("sp", "cxnSp", "pic") else el.find("p:xfrm", NS)
        if xfrm is None:
            continue
        off, ext = xfrm.find("a:off", NS), xfrm.find("a:ext", NS)
        s = {"name": name, "kind": tag, "x": inches(off.get("x")), "y": inches(off.get("y")),
             "w": inches(ext.get("cx")), "h": inches(ext.get("cy")), "paras": [], "table": None,
             "autofit": False, "insets": (0.1, 0.05, 0.1, 0.05)}
        geom = el.find("p:spPr/a:prstGeom", NS)
        if tag == "cxnSp" or (geom is not None and geom.get("prst") == "line"):
            s["kind"] = "line"
        body = el.find("p:txBody", NS)
        if body is not None:
            bp = body.find("a:bodyPr", NS)
            if bp is not None:
                s["insets"] = tuple(inches(bp.get(k), d) for k, d in (("lIns", 0.1), ("tIns", 0.05), ("rIns", 0.1), ("bIns", 0.05)))
                s["autofit"] = bp.find("a:normAutofit", NS) is not None
            s["paras"] = [p for p in paragraphs(body) if p["text"]]
        tbl = el.find(".//a:tbl", NS)
        if tbl is not None:
            cols = [inches(g.get("w")) for g in tbl.findall("a:tblGrid/a:gridCol", NS)]
            rows = []
            for tr in tbl.findall("a:tr", NS):
                cells = []
                for tc in tr.findall("a:tc", NS):
                    pr = tc.find("a:tcPr", NS)
                    ins = (inches(pr.get("marL"), 0.1) + inches(pr.get("marR"), 0.1),
                           inches(pr.get("marT"), 0.05) + inches(pr.get("marB"), 0.05)) if pr is not None else (0.2, 0.1)
                    cells.append({"paras": [p for p in paragraphs(tc.find("a:txBody", NS)) if p["text"]], "ins": ins})
                rows.append({"h": inches(tr.get("h")), "cells": cells})
            s["table"] = {"cols": cols, "rows": rows}
            s["kind"] = "table"
        shapes.append(s)
    return shapes


# ---------------------------------------------------------------- geometry
def text_width(text: str, font: str, pt: float, bold: bool) -> float:
    return len(text) * pt * WIDTH_FACTOR.get(font, 0.52) * (1.06 if bold else 1.0) / 72


def wrapped_lines(text: str, font: str, pt: float, bold: bool, width: float) -> int:
    lines, cur = 0, ""
    for word in text.split():
        nxt = (cur + " " + word) if cur else word
        if text_width(nxt, font, pt, bold) <= width or not cur:
            cur = nxt
        else:
            lines, cur = lines + 1, word
    return lines + (1 if cur else 0)


def needed_height(paras: list[dict], width: float, scale: float = 1.0) -> float:
    total = 0.0
    for k, p in enumerate(paras):
        pt = p["pt"] * scale
        total += wrapped_lines(p["text"], p["font"], pt, p["bold"], width) * pt * LINE_HEIGHT / 72
        if k < len(paras) - 1:
            total += p["spc_after_pt"] * scale / 72
    return total


def has_text(s: dict) -> bool:
    return bool(s["paras"]) or s["kind"] == "table"


def overlap_area(a: dict, b: dict) -> float:
    w = min(a["x"] + a["w"], b["x"] + b["w"]) - max(a["x"], b["x"])
    h = min(a["y"] + a["h"], b["y"] + b["h"]) - max(a["y"], b["y"])
    return w * h if w > 0 and h > 0 else 0.0


def contains(outer: dict, inner: dict, tol: float = 0.02) -> bool:
    return (outer["x"] - tol <= inner["x"] and outer["y"] - tol <= inner["y"]
            and outer["x"] + outer["w"] + tol >= inner["x"] + inner["w"]
            and outer["y"] + outer["h"] + tol >= inner["y"] + inner["h"])


def signature(shapes: list[dict]) -> tuple:
    q = lambda v: round(v * 4) / 4
    return tuple(sorted((s["kind"], q(s["x"]), q(s["y"]), q(s["w"]), q(s["h"])) for s in shapes))


def label(s: dict) -> str:
    snippet = s["paras"][0]["text"][:40] if s["paras"] else s["name"]
    return f"'{snippet}' at ({s['x']:.2f},{s['y']:.2f}) {s['w']:.2f}x{s['h']:.2f}in"


# ---------------------------------------------------------------- checks
def check_slide(n: int, shapes: list[dict], W: float, H: float, add) -> None:
    footer_band = H - 1.0   # slide number and source footer live here at caption size
    for s in shapes:
        full_bleed = s["w"] * s["h"] >= 0.95 * W * H
        if s["x"] < -0.01 or s["y"] < -0.01 or s["x"] + s["w"] > W + 0.01 or s["y"] + s["h"] > H + 0.01:
            add(n, "BLOCKING", "off-slide", f"{label(s)} extends past the slide edge")
        elif not full_bleed and (s["x"] < MARGIN - 0.01 or s["y"] < MARGIN - 0.01
                                 or s["x"] + s["w"] > W - MARGIN + 0.01 or s["y"] + s["h"] > H - MARGIN + 0.01):
            add(n, "WARNING", "margin", f"{label(s)} sits inside the {MARGIN}in margin")
        if s["paras"] and s["kind"] != "table":
            l, t, r, b = s["insets"]
            width, height = s["w"] - l - r, s["h"] - t - b
            need = needed_height(s["paras"], width)
            if need > height + 0.02:
                if s["autofit"] and needed_height(s["paras"], width, SHRINK_FLOOR) <= height + 0.02:
                    add(n, "WARNING", "text-autofit", f"{label(s)} needs {need:.2f}in for {height:.2f}in; relies on autofit shrink")
                else:
                    add(n, "BLOCKING", "text-overflow", f"{label(s)} needs {need:.2f}in of height, has {height:.2f}in")
            for p in s["paras"]:
                if p["pt"] < MIN_PT and not (s["y"] >= footer_band and s["h"] <= 0.45):
                    add(n, "WARNING", "small-type", f"{label(s)} uses {p['pt']:g} pt (floor {MIN_PT:g})")
                    break
        if s["table"]:
            total = 0.0
            for row in s["table"]["rows"]:
                need = max((needed_height(c["paras"], cw - c["ins"][0]) + c["ins"][1]
                            for c, cw in zip(row["cells"], s["table"]["cols"])), default=0.0)
                total += max(row["h"], need)
                for c in row["cells"]:
                    if any(p["pt"] < MIN_PT for p in c["paras"]):
                        add(n, "WARNING", "small-type", f"table cell '{c['paras'][0]['text'][:30]}' below {MIN_PT:g} pt")
                        break
            declared = sum(r["h"] for r in s["table"]["rows"])
            if s["y"] + total > H - MARGIN + 0.02:
                add(n, "BLOCKING", "table-overflow", f"table at y={s['y']:.2f} grows to {total:.2f}in and crosses the bottom margin")
            elif total > declared + 0.05:
                add(n, "WARNING", "table-grows", f"table rows need {total:.2f}in, declared {declared:.2f}in; rows below will shift")
    # Two text-bearing shapes may not overlap at all; a text box may sit on a
    # text-free backing shape (card, chevron, band) that fully contains it.
    texts = [s for s in shapes if has_text(s)]
    for i, a in enumerate(texts):
        for b in texts[i + 1:]:
            if overlap_area(a, b) > 0.02:
                add(n, "BLOCKING", "text-collision", f"{label(a)} overlaps {label(b)}")
    for a in texts:
        for b in shapes:
            if b is a or has_text(b) or b["kind"] == "line":
                continue
            if overlap_area(a, b) > 0.05 and not contains(a, b) and not contains(b, a):
                add(n, "WARNING", "text-crosses-shape", f"{label(a)} crosses the edge of {b['name']}")
        for ln in (s for s in shapes if s["kind"] == "line"):
            box = {"x": ln["x"] - 0.01, "y": ln["y"] - 0.01, "w": ln["w"] + 0.02, "h": ln["h"] + 0.02}
            if overlap_area(a, box) > 0.001 and not contains(a, ln, 0):
                add(n, "WARNING", "line-crosses-text", f"line {ln['name']} passes through {label(a)}")


# ---------------------------------------------------------------- raster
def find_soffice() -> str | None:
    for c in SOFFICE_CANDIDATES:
        p = shutil.which(c) or (c if os.path.isfile(c) else None)
        if p:
            return p
    return None


def rasterize(deck: Path, out: Path, count: int) -> list[str]:
    """PDF via soffice, PNGs via pdftoppm, contact.png via Pillow or montage. Returns notes."""
    notes = []
    soffice, pdftoppm = find_soffice(), shutil.which("pdftoppm")
    if not soffice or not pdftoppm:
        return [f"raster skipped: soffice={'ok' if soffice else 'missing'} pdftoppm={'ok' if pdftoppm else 'missing'}"]
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("slide-*.png"):
        old.unlink()
    r = subprocess.run([soffice, "--headless", "--convert-to", "pdf", "--outdir", str(out), str(deck)],
                       capture_output=True, text=True, timeout=300)
    pdf = out / (deck.stem + ".pdf")
    if r.returncode != 0 or not pdf.is_file():
        return [f"raster failed: soffice exit {r.returncode}: {r.stderr.strip()[:200]}"]
    subprocess.run([pdftoppm, "-png", "-r", "80", str(pdf), str(out / "slide")], check=True, timeout=300)
    pngs = sorted(out.glob("slide-*.png"))
    for k, png in enumerate(pngs, 1):     # normalize pdftoppm's padding to slide-NN.png
        png.rename(out / f"slide-{k:02d}.png")
    pngs = sorted(out.glob("slide-*.png"))
    notes.append(f"rasterized {len(pngs)} slides to {out}")
    if len(pngs) != count:
        notes.append(f"raster page count {len(pngs)} differs from slide count {count}")
    contact = out / "contact.png"
    try:
        from PIL import Image, ImageDraw
        tiles = [Image.open(p).convert("RGB") for p in pngs]
        tw, th, cols = 480, 270, 3
        rows = (len(tiles) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * (tw + 16), rows * (th + 40)), "white")
        draw = ImageDraw.Draw(sheet)
        for k, t in enumerate(tiles):
            x, y = (k % cols) * (tw + 16) + 8, (k // cols) * (th + 40) + 8
            sheet.paste(t.resize((tw, th)), (x, y))
            draw.text((x, y + th + 6), f"slide {k + 1:02d}", fill="black")
        sheet.save(contact)
        notes.append(f"contact sheet (Pillow): {contact}")
    except ImportError:
        montage = shutil.which("montage")
        if not montage:
            notes.append("contact sheet skipped: neither Pillow nor ImageMagick montage available")
            return notes
        font = next((f for f in FONT_FILES if os.path.isfile(f)), None)
        cmd = [montage] + (["-font", font] if font else []) + ["-label", "%f", "-pointsize", "20", "-tile", "3x",
                                                                "-geometry", "480x270+8+8"] + [str(p) for p in pngs] + [str(contact)]
        r = subprocess.run(cmd, capture_output=True, text=True)
        notes.append(f"contact sheet (montage): {contact}" if r.returncode == 0 else f"montage failed: {r.stderr.strip()[:200]}")
    return notes


# ---------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("deck")
    ap.add_argument("--out", help="directory for slide PNGs and contact.png (default: <deck>-qa/)")
    ap.add_argument("--format", choices=["text", "json"], default="text")
    ap.add_argument("--no-raster", action="store_true", help="geometry checks only")
    args = ap.parse_args()
    deck = Path(args.deck)
    if not deck.is_file():
        print(f"no such file: {deck}", file=sys.stderr)
        return 2
    findings: list[dict] = []

    def add(slide: int, sev: str, check: str, msg: str) -> None:
        findings.append({"slide": slide, "severity": sev, "check": check, "message": msg})

    with zipfile.ZipFile(deck) as z:
        W, H = slide_size(z)
        paths = slide_paths(z)
        prev_sig = None
        for n, part in enumerate(paths, 1):
            shapes = read_shapes(z.read(part))
            check_slide(n, shapes, W, H, add)
            sig = signature(shapes)
            if sig == prev_sig:
                add(n, "WARNING", "repeated-layout", "same layout signature as the previous slide")
            prev_sig = sig
    notes = [] if args.no_raster else rasterize(deck, Path(args.out) if args.out else deck.with_name(deck.stem + "-qa"), len(paths))

    blocking = sum(1 for f in findings if f["severity"] == "BLOCKING")
    warning = len(findings) - blocking
    if args.format == "json":
        print(json.dumps({"deck": str(deck), "slides": len(paths), "findings": findings, "notes": notes,
                          "summary": {"blocking": blocking, "warning": warning}}, indent=2))
    else:
        for f in findings:
            print(f"slide {f['slide']:02d}  {f['severity']:<9} {f['check']:<18} {f['message']}")
        for note in notes:
            print(note)
        print(f"{'FAIL' if blocking else 'OK'}: {deck} slides={len(paths)} blocking={blocking} warning={warning}")
    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main())
