#!/usr/bin/env node
// render-deck.js — render a HELIX deliverable script (deck) to .pptx.
//
// Usage: render-deck.js <script.md> <out.pptx> [--theme theme.yml] [--patterns slide-patterns.yml]
//
// Reads the deliverable Markdown script (frontmatter, ## Content units with
// **Pattern**/**Body**/**Visual**/**Notes**/**Sources**, the ## Sources
// table), lays each unit out by its pattern on a 12-column grid using the
// theme's margins and type scale, and writes one slide per unit (plus
// continuation slides when a unit's text cannot fit at the size floor).
// Visuals are drawn from the structured spec on the **Visual** line
// (workflows/deliverables/visual-specs.md). Needs pptxgenjs on NODE_PATH.
"use strict";
const fs = require("fs");
const path = require("path");

let pptxgen;
try {
  pptxgen = require("pptxgenjs");
} catch (e) {
  console.error("render-deck.js: cannot require('pptxgenjs'); run `npm i pptxgenjs@3.12.0` or set NODE_PATH");
  process.exit(2);
}

// ---------------------------------------------------------------- arguments
const argv = process.argv.slice(2);
const positional = [];
const flags = {};
for (let i = 0; i < argv.length; i++) {
  if (argv[i].startsWith("--")) flags[argv[i].slice(2)] = argv[++i];
  else positional.push(argv[i]);
}
if (positional.length < 2) {
  console.error("usage: render-deck.js <script.md> <out.pptx> [--theme theme.yml] [--patterns slide-patterns.yml]");
  process.exit(2);
}
const [scriptPath, outPath] = positional;
const repoRoot = path.resolve(__dirname, "..", "..", "..");
const themePath = flags.theme || firstExisting([
  path.join(repoRoot, "workflows", "deliverables", "theme.yml"),
  path.join(__dirname, "..", "references", "deliverables", "theme.yml"),
]);
const patternsPath = flags.patterns || firstExisting([
  path.join(repoRoot, "workflows", "deliverables", "slide-patterns.yml"),
  path.join(__dirname, "..", "references", "deliverables", "slide-patterns.yml"),
]);

function firstExisting(cands) {
  for (const c of cands) if (fs.existsSync(c)) return c;
  return cands[0];
}

// ---------------------------------------------------------------- tiny YAML
// Enough YAML for theme.yml and slide-patterns.yml: block maps and lists,
// flow lists/maps on one line, quoted scalars, comments. Nothing more.
function parseYaml(text) {
  const lines = [];
  for (const raw of text.split("\n")) {
    const stripped = stripComment(raw);
    if (stripped.trim() === "") continue;
    lines.push({ indent: stripped.length - stripped.trimStart().length, text: stripped.trim() });
  }
  let i = 0;
  function block(indent) {
    return lines[i].text.startsWith("- ") ? list(indent) : map(indent);
  }
  function map(indent) {
    const obj = {};
    while (i < lines.length && lines[i].indent === indent && !lines[i].text.startsWith("- ")) {
      const m = lines[i].text.match(/^([^:]+):\s*(.*)$/);
      i++;
      if (!m) continue;
      const key = m[1].trim();
      if (m[2] === "") obj[key] = i < lines.length && lines[i].indent > indent ? block(lines[i].indent) : null;
      else obj[key] = scalar(m[2]);
    }
    return obj;
  }
  function list(indent) {
    const arr = [];
    while (i < lines.length && lines[i].indent === indent && lines[i].text.startsWith("- ")) {
      const rest = lines[i].text.slice(2).trim();
      if (/^[^:{["']+:(\s|$)/.test(rest)) {
        lines[i] = { indent: indent + 2, text: rest };
        arr.push(map(indent + 2));
      } else {
        i++;
        arr.push(scalar(rest));
      }
    }
    return arr;
  }
  return block(lines[0].indent);
}
function stripComment(line) {
  let quote = null;
  for (let k = 0; k < line.length; k++) {
    const ch = line[k];
    if (quote) { if (ch === quote) quote = null; continue; }
    if (ch === '"' || ch === "'") quote = ch;
    else if (ch === "#" && (k === 0 || /\s/.test(line[k - 1]))) return line.slice(0, k);
  }
  return line;
}
function scalar(s) {
  s = s.trim();
  if (/^["'].*["']$/.test(s)) return s.slice(1, -1);
  if (s.startsWith("[") && s.endsWith("]")) return splitFlow(s.slice(1, -1)).map(scalar);
  if (s.startsWith("{") && s.endsWith("}")) {
    const obj = {};
    for (const part of splitFlow(s.slice(1, -1))) {
      const m = part.match(/^([^:]+):\s*(.*)$/);
      if (m) obj[m[1].trim()] = scalar(m[2]);
    }
    return obj;
  }
  if (s === "true") return true;
  if (s === "false") return false;
  if (/^-?\d+(\.\d+)?$/.test(s)) return Number(s);
  return s;
}
function splitFlow(s) {
  const out = [];
  let depth = 0, cur = "", quote = null;
  for (const ch of s) {
    if (quote) { cur += ch; if (ch === quote) quote = null; continue; }
    if (ch === '"' || ch === "'") { quote = ch; cur += ch; continue; }
    if (ch === "[" || ch === "{") depth++;
    if (ch === "]" || ch === "}") depth--;
    if (ch === "," && depth === 0) { out.push(cur); cur = ""; continue; }
    cur += ch;
  }
  if (cur.trim()) out.push(cur);
  return out;
}

// ---------------------------------------------------------------- theme
const theme = parseYaml(fs.readFileSync(themePath, "utf8"));
const patterns = parseYaml(fs.readFileSync(patternsPath, "utf8"));
const limitsOf = {};
for (const p of patterns.patterns || []) limitsOf[p.id] = p.limits || {};

const hex = (c) => String(c).replace("#", "").toUpperCase();
const P = theme.palette;
const C = {
  primary: hex(P.primary), secondary: hex(P.secondary), accent: hex(P.accent),
  ink: hex(P.ink), muted: hex(P.muted), surface: hex(P.surface), alt: hex(P.surface_alt), border: hex(P.border),
  white: "FFFFFF",
  dark: Object.fromEntries(Object.entries(P.dark).map(([k, v]) => [k === "surface_alt" ? "alt" : k, hex(v)])),
};
const FONT = { display: theme.typography.display.family, body: theme.typography.body.family };
const SCALE = theme.typography.scale;
const L = theme.layout.slide;
const W = L.width_in, H = L.height_in, M = L.margin_in, G = L.gutter_in;
const COLS = 12;
const CW = (W - 2 * M - (COLS - 1) * G) / COLS;
const FOOTER_H = 0.3;
const FOOTER_Y = H - M - FOOTER_H;            // footer sits inside the margin
const TITLE_Y = M, TITLE_H = 1.3;
const BODY_Y = TITLE_Y + TITLE_H + 0.25;      // 2.15
const BODY_BOTTOM = FOOTER_Y - 0.25;          // 6.35
const BODY_H = BODY_BOTTOM - BODY_Y;
const MARKER = theme.motif.section_marker || { size_in: 0.55 };
const MIN_PT = 12;                            // no text below this on content slides

function grid(col, span) {
  // col is 1-based; returns x and w for `span` columns starting at `col`
  return { x: M + (col - 1) * (CW + G), w: span * CW + (span - 1) * G };
}

// ---------------------------------------------------------------- measuring
// Average glyph width as a fraction of the point size, per typeface.
const WIDTH_FACTOR = { Georgia: 0.58, Arial: 0.5, "Courier New": 0.6 };  // average em per character; Arial bold runs wider still;
const LINE_HEIGHT = 1.2;

function textWidthIn(str, font, pt, bold) {
  const f = WIDTH_FACTOR[font] || 0.52;
  return (str.length * pt * f * (bold ? 1.2 : 1)) / 72;
}
function wrap(str, font, pt, bold, widthIn) {
  const lines = [];
  let cur = "";
  for (const word of String(str).split(/\s+/).filter(Boolean)) {
    const next = cur ? cur + " " + word : word;
    if (textWidthIn(next, font, pt, bold) <= widthIn || !cur) cur = next;
    else { lines.push(cur); cur = word; }
    // a single word wider than the box breaks mid-word in the renderer; count the
    // extra lines it would take so the fit step shrinks the size instead
    const ww = textWidthIn(word, font, pt, bold);
    if (ww > widthIn) for (let k = 1; k < Math.ceil(ww / widthIn); k++) lines.push("");
  }
  if (cur) lines.push(cur);
  return lines.length ? lines : [""];
}
// Pick the largest size from `sizes` at which every paragraph fits the box.
// Returns { pt, fits, height, lines }.
function fitParagraphs(paras, box, opts) {
  const { font, bold = false, sizes, paraGap = 0.5, indentIn = 0 } = opts;
  let last = null;
  for (const pt of sizes) {
    let height = 0, lines = 0;
    paras.forEach((p, k) => {
      const n = wrap(p, font, pt, bold, box.w - indentIn).length;
      lines += n;
      height += (n * pt * LINE_HEIGHT) / 72;
      if (k < paras.length - 1) height += (paraGap * pt) / 72;
    });
    last = { pt, fits: height <= box.h, height, lines };
    if (last.fits) return last;
  }
  return last;
}
function sizesDown(from, floor, step = 2) {
  const out = [];
  for (let s = from; s >= floor; s -= step) out.push(s);
  if (out[out.length - 1] !== floor) out.push(floor);
  return out;
}

// ---------------------------------------------------------------- script parsing
function parseScript(md) {
  const fm = {};
  let body = md;
  const fmMatch = md.match(/^---\n([\s\S]*?)\n---\n/);
  if (fmMatch) {
    body = md.slice(fmMatch[0].length);
    try { Object.assign(fm, parseYaml(fmMatch[1])); } catch (e) { /* frontmatter is optional here */ }
  }
  const title = (body.match(/^# (.+)$/m) || [, ""])[1].trim();
  const sections = {};
  let cur = null;
  for (const line of body.split("\n")) {
    const h = line.match(/^## (.+)$/);
    if (h) { cur = h[1].trim(); sections[cur] = []; continue; }
    if (cur) sections[cur].push(line);
  }
  const units = [];
  let unit = null, field = null;
  for (const line of sections.Content || []) {
    const h = line.match(/^### (\d+)\.\s+(.*)$/);
    if (h) { unit = { n: Number(h[1]), title: h[2].trim(), body: [], visual: "", notes: "", sources: "" }; units.push(unit); field = null; continue; }
    if (!unit) continue;
    const f = line.match(/^\*\*(Pattern|Body|Visual|Notes|Sources)\*\*:\s*(.*)$/);
    if (f) {
      field = f[1].toLowerCase();
      const rest = f[2].trim();
      if (field === "body") { if (rest) unit.body.push(rest.replace(/^[-*]\s+/, "")); }
      else unit[field] = rest;
      continue;
    }
    if (!field || !line.trim()) continue;
    if (field === "body") unit.body.push(line.trim().replace(/^[-*•]\s+/, ""));
    else unit[field] += " " + line.trim();
  }
  const brief = {};
  for (const line of sections.Brief || []) {
    const m = line.match(/^- \*\*(.+?)\*\*:\s*(.*)$/);
    if (m) brief[m[1]] = m[2].trim();
  }
  const sources = [];
  for (const line of sections.Sources || []) {
    const cells = line.split("|").map((s) => s.trim());
    if (cells.length >= 4 && /^S\d+$/.test(cells[1])) sources.push([cells[1], cells[2], cells[3]]);
  }
  return { fm, title, brief, units, sources };
}

// Visual spec: `kind: x | field: a; b | field: c / d; e / f. prose`
function parseVisual(line) {
  const m = line.match(/^kind:\s*/);
  if (!m) return { kind: null, text: line };
  let specText = line, prose = "";
  const end = line.search(/\.\s|\.$/);
  if (end >= 0) { specText = line.slice(0, end); prose = line.slice(end + 1).trim(); }
  const spec = { text: prose };
  for (const part of specText.split(/\s\|\s/)) {
    const kv = part.match(/^([\w-]+):\s*(.*)$/);
    if (kv) spec[kv[1]] = kv[2].trim();
  }
  return spec;
}
const items = (v) => (v ? String(v).split(";").map((s) => s.trim()).filter(Boolean) : []);
const cells = (v) => String(v).split(" / ").map((s) => s.trim());
const num = (v, d) => (v && /^\d+$/.test(v) ? Number(v) : d);
function splitLabel(bullet) {
  // "Label: detail" -> ["Label", "detail"]; otherwise [bullet, ""]
  const m = bullet.match(/^([^:]{2,60}):\s+(.*)$/);
  return m ? [m[1].trim(), m[2].trim()] : [bullet, ""];
}

// ---------------------------------------------------------------- drawing helpers
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
let slideCount = 0;

function text(slide, str, box, o = {}) {
  // Fit `str` into box: shrink from o.size to o.min across o.step, then write.
  const font = o.font || FONT.body;
  const sizes = sizesDown(o.size || SCALE.slide_body, o.min || MIN_PT, o.step || 2);
  const fit = fitParagraphs([str], box, { font, bold: !!o.bold, sizes });
  slide.addText(str, {
    x: box.x, y: box.y, w: box.w, h: box.h, fontFace: font, fontSize: fit.pt, bold: !!o.bold, italic: !!o.italic,
    color: o.color || C.ink, align: o.align || "left", valign: o.valign || "top", isTextBox: true, margin: 0,
    fit: "shrink",
  });
  return fit;
}
function bulletList(slide, list, box, o = {}) {
  const font = FONT.body;
  const sizes = sizesDown(o.size || SCALE.slide_body, o.min || 14, 2);
  const fit = fitParagraphs(list, box, { font, sizes, paraGap: 0.6, indentIn: 0.3 });
  slide.addText(
    list.map((t, k) => ({ text: t, options: { bullet: { indent: 18 }, breakLine: k < list.length - 1, paraSpaceAfter: fit.pt * 0.6 } })),
    { x: box.x, y: box.y, w: box.w, h: box.h, fontFace: font, fontSize: fit.pt, color: o.color || C.ink, isTextBox: true, margin: 0, valign: "top" }
  );
  return fit;
}
function rect(slide, box, fill, o = {}) {
  slide.addShape(o.round === false ? pres.shapes.RECTANGLE : pres.shapes.ROUNDED_RECTANGLE, {
    x: box.x, y: box.y, w: box.w, h: box.h, rectRadius: o.radius == null ? 0.1 : o.radius,
    fill: { color: fill }, line: { color: o.line || fill, width: o.lineWidth == null ? 0.75 : o.lineWidth },
  });
}
function card(slide, box, dark) {
  rect(slide, box, dark ? C.dark.alt : C.alt, { line: dark ? C.dark.border : C.border });
}
function circle(slide, x, y, d, fill) {
  slide.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: fill }, line: { color: fill } });
}
function numberBadge(slide, n, x, y, d, fill, fontPt) {
  circle(slide, x, y, d, fill);
  slide.addText(String(n), { x, y, w: d, h: d, fontFace: FONT.display, fontSize: fontPt || Math.round(d * 30), bold: true,
    color: C.white, align: "center", valign: "middle", isTextBox: true, margin: 0 });
}
function line(slide, x, y, w, h, color, o = {}) {
  slide.addShape(pres.shapes.LINE, { x, y, w, h, line: { color, width: o.width || 1.5, dashType: o.dash || "solid",
    beginArrowType: o.begin || "none", endArrowType: o.end || "none" } });
}
function chevron(slide, box, fill) {
  slide.addShape(pres.shapes.CHEVRON, { x: box.x, y: box.y, w: box.w, h: box.h, fill: { color: fill }, line: { color: C.white, width: 1.5 } });
}

// Chrome shared by content slides: numbered marker, title, footer, notes.
function chrome(slide, unit, o = {}) {
  const dark = !!o.dark;
  slideCount += 1;
  slide.background = { color: dark ? C.dark.surface : C.surface };
  const size = MARKER.size_in || 0.55;
  if (!o.noMarker) numberBadge(slide, unit.n, M, TITLE_Y + 0.12, size, dark ? C.dark.secondary : C.secondary, 16);
  const tx = o.noMarker ? M : M + size + 0.3;
  const titleStr = o.titleOverride || unit.title;
  text(slide, titleStr, { x: tx, y: TITLE_Y, w: W - M - tx, h: TITLE_H },
    { font: FONT.display, size: SCALE.slide_title, min: 24, step: 4, bold: true, color: dark ? C.dark.ink : C.ink });
  const mutedC = dark ? C.dark.muted : C.muted;
  const cited = (unit.sources.match(/S\d+/g) || []).join(", ");
  if (cited && !o.noSourceFooter) {
    slide.addText("Sources: " + cited + " (appendix)", { x: M, y: FOOTER_Y, w: 8, h: FOOTER_H, fontFace: FONT.body,
      fontSize: theme.motif.footer_source.size_pt || 9, color: mutedC, isTextBox: true, margin: 0, valign: "bottom" });
  }
  slide.addText(String(slideCount), { x: W - M - 0.6, y: FOOTER_Y, w: 0.6, h: FOOTER_H, fontFace: FONT.body,
    fontSize: theme.motif.slide_number.size_pt || 10, color: mutedC, align: "right", isTextBox: true, margin: 0, valign: "bottom" });
  if (unit.notes && !o.noNotes) slide.addNotes(unit.notes);
}
function newSlide(unit, o) {
  const s = pres.addSlide();
  chrome(s, unit, o);
  return s;
}

// ---------------------------------------------------------------- visuals
// Every visual draws into `box` and must keep its text inside it.
const visuals = {};

visuals["process-flow"] = (slide, box, spec, unit) => {
  const steps = items(spec.steps).slice(0, 5);
  if (!steps.length) return placeholder(slide, box, spec, unit);
  const hl = num(spec.highlight, 0);
  const details = items(spec.details);
  const byLabel = new Map(unit.body.map(splitLabel).map(([l, d]) => [l.toLowerCase(), d]));
  const gap = 0.08;
  const stepW = (box.w - gap * (steps.length - 1)) / steps.length;
  const chevH = Math.min(steps.length >= 5 ? 0.8 : 1.15, box.h * 0.3);  // narrower chevrons need a shallower notch so labels fit
  const y = box.y + (box.h > 3 ? 0.9 : 0.2);
  const hasDetails = steps.some((label, k) => details[k] || byLabel.get(label.toLowerCase()));
  const captionY = y + chevH + (hasDetails ? 1.3 : 0.3);
  steps.forEach((label, k) => {
    const x = box.x + k * (stepW + gap);
    const active = k + 1 === hl;
    chevron(slide, { x, y, w: stepW, h: chevH }, active ? C.secondary : C.primary);
    const inset = chevH * 0.55; // clear the notch on the left and the point on the right
    text(slide, label, { x: x + inset, y: y + 0.1, w: stepW - 2 * inset, h: chevH - 0.2 },
      { size: 16, min: 12, bold: true, color: C.white, align: "center", valign: "middle" });
    const detail = details[k] || byLabel.get(label.toLowerCase()) || "";
    if (detail) text(slide, detail, { x: x + 0.1, y: y + chevH + 0.2, w: stepW - 0.2, h: 1.0 },
      { size: 14, min: 12, color: C.muted, align: "center" });
    if (active && spec.caption) {
      const cx = Math.max(box.x, Math.min(x - 0.4, box.x + box.w - (stepW + 0.8)));  // keep the caption inside the box
      text(slide, spec.caption, { x: cx, y: captionY, w: stepW + 0.8, h: 0.6 },
      { size: 14, min: 12, bold: true, color: C.secondary, align: "center" });
    }
  });
};

visuals.timeline = (slide, box, spec) => {
  const ms = items(spec.milestones).slice(0, 6);
  if (!ms.length) return placeholder(slide, box, spec);
  const now = num(spec.now, 0);
  const mid = box.y + box.h * 0.4;
  const pad = 0.6;
  line(slide, box.x + pad, mid, box.w - 2 * pad, 0, C.border, { width: 3 });
  const segW = (box.w - 2 * pad) / Math.max(ms.length - 1, 1);
  const labelW = Math.min(segW, box.w / 2) - 0.1;
  ms.forEach((label, k) => {
    const cx = box.x + pad + k * segW;
    const active = k + 1 === now;
    circle(slide, cx - 0.15, mid - 0.15, 0.3, active ? C.secondary : C.primary);
    const above = k % 2 === 0;
    const lx = Math.min(Math.max(cx - labelW / 2, box.x), box.x + box.w - labelW);
    const lb = { x: lx, y: above ? mid - 0.95 : mid + 0.25, w: labelW, h: 0.7 };
    text(slide, label, lb, { size: 14, min: 12, bold: active, color: active ? C.secondary : C.ink, align: "center", valign: above ? "bottom" : "top" });
    if (active && spec.marker) {
      line(slide, cx, mid + 0.95, 0, 0.3, C.secondary, { dash: "dash", width: 2 });
      const mw = labelW + 0.8, mx = Math.min(Math.max(cx - mw / 2, box.x), box.x + box.w - mw);
      text(slide, spec.marker, { x: mx, y: mid + 1.3, w: mw, h: 0.5 },
        { size: 13, min: 12, bold: true, color: C.secondary, align: "center" });
    }
  });
  if (spec.caption) text(slide, spec.caption, { x: box.x + 0.2, y: box.y + box.h - 0.55, w: box.w - 0.4, h: 0.5 },
    { size: 12, min: 12, color: C.muted, align: "center", valign: "bottom" });
};

visuals["two-column"] = (slide, box, spec, unit) => {
  const left = spec.left || "Option A", right = spec.right || "Option B";
  let rows = items(spec.rows).map(cells);
  if (!rows.length) rows = rowsFromBody(unit.body, left, right);
  const prefer = spec.prefer === "left" ? 0 : 1;
  const verdict = spec.verdict || (unit.body.find((b) => /^verdict:/i.test(b)) || "").replace(/^verdict:\s*/i, "");
  const verdictH = verdict ? 0.6 : 0;
  const colW = (box.w - G) / 2;
  const headH = 0.7, padX = 0.3;
  const maxCardH = box.h - verdictH - (verdict ? 0.2 : 0);
  const rowH = rows.length ? Math.min(1.3, (maxCardH - headH - 0.3) / rows.length) : 0;
  const cardH = Math.min(maxCardH, headH + 0.3 + rows.length * rowH);
  [left, right].forEach((head, side) => {
    const x = box.x + side * (colW + G);
    rect(slide, { x, y: box.y, w: colW, h: cardH }, side === prefer ? C.white : C.alt, { line: C.border });
    text(slide, head, { x: x + padX, y: box.y + 0.2, w: colW - 2 * padX, h: headH - 0.2 },
      { font: FONT.display, size: 20, min: 16, bold: true, color: side === prefer ? C.primary : C.muted });
    rows.forEach((r, k) => {
      const ry = box.y + headH + 0.1 + k * rowH;
      const mark = side === prefer;
      if (mark) numberBadge(slide, "✓", x + padX, ry + 0.05, 0.32, C.primary, 12);
      text(slide, r[side] || "", { x: x + padX + (mark ? 0.5 : 0), y: ry, w: colW - 2 * padX - (mark ? 0.5 : 0), h: rowH - 0.15 },
        { size: 15, min: 12, color: C.ink });
    });
  });
  if (verdict) text(slide, "Verdict: " + verdict, { x: box.x, y: box.y + cardH + 0.2, w: box.w, h: verdictH },
    { size: 15, min: 12, bold: true, color: C.secondary, valign: "middle" });
};
function rowsFromBody(body, left, right) {
  const l = [], r = [];
  for (const b of body) {
    const [label, detail] = splitLabel(b);
    if (label.toLowerCase() === left.toLowerCase()) l.push(detail);
    else if (label.toLowerCase() === right.toLowerCase()) r.push(detail);
  }
  const n = Math.max(l.length, r.length);
  return Array.from({ length: n }, (_, k) => [l[k] || "", r[k] || ""]);
}

visuals.table = (slide, box, spec, unit, o = {}) => {
  const columns = spec.columns ? cells(spec.columns) : ["Item", "Detail"];
  let rows = items(spec.rows).map(cells);
  if (!rows.length) rows = unit.body.map(splitLabel).filter((r) => r[1]);
  const hl = num(spec.highlight, 0);
  drawTable(slide, box, columns, rows, { highlight: hl, size: o.size || 14 });
};
// Draws header + rows as a native table sized to fit; returns rows that did not fit.
function drawTable(slide, box, columns, rows, o = {}) {
  const n = columns.length;
  const colW = o.colW || columns.map((_, k) => (k === 0 && n > 1 ? box.w * 0.3 : (box.w * 0.7) / (n - 1)));
  const pad = 0.08;
  let pt = o.size || 14, heights = [];
  for (const cand of sizesDown(o.size || 14, MIN_PT, 1)) {
    pt = cand;
    heights = [columns, ...rows].map((r) => {
      const lines = Math.max(...r.map((c, k) => wrap(c, FONT.body, pt, false, colW[k] - 2 * pad).length));
      return Math.max((lines * pt * LINE_HEIGHT) / 72 + 2 * pad + 0.06, o.minRow || 0);
    });
    if (heights.reduce((a, b) => a + b, 0) <= box.h) break;
  }
  let total = heights[0], keep = 0;
  for (let k = 1; k < heights.length; k++) { if (total + heights[k] > box.h + 1e-6) break; total += heights[k]; keep = k; }
  const shown = rows.slice(0, keep);
  const data = [columns, ...shown].map((r, ri) => r.map((c, k) => ({
    text: c, options: {
      bold: ri === 0 || (k === 0 && o.boldFirst !== false), color: ri === 0 ? C.white : k === 0 ? C.muted : C.ink, fontSize: pt,
      fill: { color: ri === 0 ? C.primary : ri === o.highlight ? C.alt : C.white }, valign: "middle",
    },
  })));
  slide.addTable(data, { x: box.x, y: box.y, w: box.w, colW, rowH: heights.slice(0, keep + 1), fontFace: FONT.body,
    border: { type: "solid", color: C.border, pt: 0.75 }, margin: pad });
  return rows.slice(keep);
}

visuals.stat = (slide, box, spec, unit) => {
  let stats = items(spec.stats).map(cells).slice(0, 3);
  if (!stats.length) stats = unit.body.slice(0, 3).map((b) => { const m = b.match(/^([<>]?\s?\$?\d[\d,.]*\s?[%kKMBx+]*|[<>]\s?\d+)\s*(.*)$/); return m ? [m[1].trim(), m[2]] : [b, ""]; });
  const cardW = (stats.length ? (box.w - G * (stats.length - 1)) / stats.length : box.w);
  const hues = stats.length === 2 ? [C.primary, C.secondary] : [C.primary, C.accent, C.secondary];
  stats.forEach(([value, caption], k) => {
    const x = box.x + k * (cardW + G);
    card(slide, { x, y: box.y, w: cardW, h: box.h });
    const inner = { x: x + 0.25, w: cardW - 0.5 };
    const numH = Math.min(1.6, box.h * 0.4);
    text(slide, value, { x: inner.x, y: box.y + 0.3, w: inner.w, h: numH },
      { font: FONT.display, size: SCALE.stat_callout, min: 28, step: 8, bold: false, color: hues[k], align: "center", valign: "middle" });
    text(slide, caption || "", { x: inner.x, y: box.y + numH + 0.5, w: inner.w, h: box.h - numH - 1.2 },
      { size: 15, min: 12, color: C.ink, align: "center" });
    if (spec.label) text(slide, spec.label.toUpperCase(), { x: inner.x, y: box.y + box.h - 0.55, w: inner.w, h: 0.35 },
      { size: 12, min: 12, bold: true, color: C.muted, align: "center", valign: "bottom" });
  });
};

visuals.panels = (slide, box, spec) => {
  const list = items(spec.items).map(cells).slice(0, 4);
  if (!list.length) return placeholder(slide, box, spec);
  const hues = [C.primary, C.accent, C.secondary, C.primary];
  const cardW = (box.w - G * (list.length - 1)) / list.length;
  list.forEach(([name, detail], k) => {
    const x = box.x + k * (cardW + G);
    card(slide, { x, y: box.y, w: cardW, h: box.h });
    const d = Math.min(1.0, cardW * 0.45);
    numberBadge(slide, k + 1, x + (cardW - d) / 2, box.y + 0.5, d, hues[k], 24);
    text(slide, name, { x: x + 0.08, y: box.y + d + 0.75, w: cardW - 0.16, h: 0.5 }, { size: 16, min: 12, bold: true, align: "center" });
    text(slide, detail || "", { x: x + 0.15, y: box.y + d + 1.3, w: cardW - 0.3, h: box.h - d - 1.5 }, { size: 13, min: 12, color: C.muted, align: "center" });
  });
};

visuals.boundary = (slide, box, spec) => {
  rect(slide, box, C.alt, { line: C.border, lineWidth: 1 });
  text(slide, spec.outer || "outside", { x: box.x + 0.3, y: box.y + 0.2, w: box.w - 0.6, h: 0.4 }, { size: 14, min: 12, bold: true, color: C.muted, align: "center" });
  if (spec["outer-note"]) text(slide, spec["outer-note"], { x: box.x + 0.3, y: box.y + 0.6, w: box.w - 0.6, h: 0.35 }, { size: 12, min: 12, color: C.muted, align: "center" });
  const iw = Math.min(3.0, box.w * 0.5), ih = 1.5;
  const ix = box.x + (box.w - iw) / 2, iy = box.y + (box.h - ih) / 2 + 0.2;
  rect(slide, { x: ix, y: iy, w: iw, h: ih }, C.primary);
  text(slide, spec.inner || "inside", { x: ix + 0.2, y: iy + 0.25, w: iw - 0.4, h: 0.5 }, { font: FONT.display, size: 18, min: 14, bold: true, color: C.white, align: "center" });
  if (spec["inner-note"]) text(slide, spec["inner-note"], { x: ix + 0.2, y: iy + 0.8, w: iw - 0.4, h: 0.5 }, { size: 13, min: 12, color: C.white, align: "center" });
  const arrowW = Math.min(1.0, (ix - box.x) - 0.4);
  line(slide, ix + iw + 0.1, iy + ih / 2, arrowW, 0, C.secondary, { width: 2, end: "triangle" });
  line(slide, ix - 0.1 - arrowW, iy + ih / 2, arrowW, 0, C.secondary, { width: 2, begin: "triangle" });
  if (spec.caption) text(slide, spec.caption, { x: box.x + 0.3, y: box.y + box.h - 0.75, w: box.w - 0.6, h: 0.6 }, { size: 12, min: 12, color: C.muted, align: "center", valign: "bottom" });
};

visuals.helix = (slide, box, spec) => {
  card(slide, box);
  const pillW = 0.9, pillH = box.h - 1.7, top = box.y + 0.75;
  const lx = box.x + box.w * 0.22 - pillW / 2, rx = box.x + box.w * 0.78 - pillW / 2;
  rect(slide, { x: lx, y: top, w: pillW, h: pillH }, C.primary, { radius: 0.45 });
  rect(slide, { x: rx, y: top, w: pillW, h: pillH }, C.secondary, { radius: 0.45 });
  const rungs = 3;
  for (let k = 1; k <= rungs; k++) line(slide, lx + pillW, top + (pillH * k) / (rungs + 1), rx - lx - pillW, 0, C.accent, { width: 2.5 });
  const midW = rx - lx - pillW - 0.4;
  if (spec.rungs) text(slide, spec.rungs, { x: lx + pillW + 0.2, y: top + pillH / 2 - 0.4, w: midW, h: 0.35 }, { size: 12, min: 12, bold: true, color: C.accent, align: "center", valign: "bottom" });
  const noteW = Math.max(pillW + 1.2, 2.0);
  text(slide, spec.left || "", { x: lx + pillW / 2 - noteW / 2, y: top + pillH + 0.1, w: noteW, h: 0.35 }, { size: 12, min: 12, bold: true, color: C.primary, align: "center" });
  text(slide, spec.right || "", { x: rx + pillW / 2 - noteW / 2, y: top + pillH + 0.1, w: noteW, h: 0.35 }, { size: 12, min: 12, bold: true, color: C.secondary, align: "center" });
  if (spec["left-note"]) text(slide, spec["left-note"], { x: lx + pillW / 2 - noteW / 2, y: box.y + 0.2, w: noteW, h: 0.4 }, { size: 12, min: 12, color: C.muted, align: "center" });
  if (spec["right-note"]) text(slide, spec["right-note"], { x: rx + pillW / 2 - noteW / 2, y: box.y + 0.2, w: noteW, h: 0.4 }, { size: 12, min: 12, color: C.muted, align: "center" });
};

visuals["risk-grid"] = (slide, box, spec) => {
  const risks = items(spec.risks).map(cells).slice(0, 6);
  if (!risks.length) return placeholder(slide, box, spec);
  const level = (s) => ({ low: 0, medium: 1, med: 1, high: 2 }[String(s || "").toLowerCase()] ?? 1);
  const axisW = 0.9, gridX = box.x + axisW, gridY = box.y + 0.1;
  const gw = box.w - axisW, gh = box.h - 0.6;
  const cw = gw / 3, ch = gh / 3;
  for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++) {
    const hot = r + c >= 3;
    rect(slide, { x: gridX + c * cw, y: gridY + r * ch, w: cw, h: ch }, hot ? "F6E4DF" : C.alt, { round: false, line: C.border });
  }
  // dots that share a cell spread sideways around the cell's center
  const placed = risks.map(([, lik, imp]) => ({ row: 2 - level(lik), col: level(imp) }));
  const perCell = {}, seen = {};
  placed.forEach((p) => { perCell[p.row + ":" + p.col] = (perCell[p.row + ":" + p.col] || 0) + 1; });
  placed.forEach((p, k) => {
    const key = p.row + ":" + p.col, count = perCell[key], slot = seen[key] = (seen[key] || 0) + 1;
    const d = 0.45, pitch = d + 0.1;
    const cx = gridX + p.col * cw + cw / 2 - d / 2 + (slot - (count + 1) / 2) * pitch;
    numberBadge(slide, k + 1, cx, gridY + p.row * ch + ch / 2 - d / 2, d, C.secondary, 14);
  });
  ["high", "medium", "low"].forEach((lvl, r) =>
    text(slide, lvl, { x: box.x, y: gridY + r * ch, w: axisW - 0.1, h: ch }, { size: 12, min: 12, color: C.muted, align: "right", valign: "middle" }));
  text(slide, "likelihood (rows) by impact: low, medium, high", { x: gridX, y: gridY + gh + 0.1, w: gw, h: 0.4 }, { size: 12, min: 12, color: C.muted, align: "center" });
};

visuals.none = () => {};

function placeholder(slide, box, spec, unit) {
  card(slide, box);
  const prose = (spec && spec.text) || (unit && unit.visual) || "";
  text(slide, "Visual to supply", { x: box.x + 0.3, y: box.y + 0.3, w: box.w - 0.6, h: 0.4 }, { size: 13, min: 12, bold: true, color: C.muted });
  text(slide, prose, { x: box.x + 0.3, y: box.y + 0.8, w: box.w - 0.6, h: box.h - 1.1 }, { size: 14, min: 12, italic: true, color: C.muted });
}
function drawVisual(slide, box, unit) {
  const spec = parseVisual(unit.visual || "");
  const fn = spec.kind && visuals[spec.kind];
  if (!fn) return placeholder(slide, box, spec, unit);
  fn(slide, box, spec, unit);
}

// ---------------------------------------------------------------- patterns
const layouts = {};

layouts.title = (unit, deck) => {
  const s = pres.addSlide();
  slideCount += 1;
  s.background = { color: C.dark.surface };
  const tb = grid(1, 8);
  text(s, unit.title, { x: tb.x, y: 1.5, w: tb.w, h: 2.5 }, { font: FONT.display, size: 40, min: 28, step: 4, bold: true, color: C.dark.ink, valign: "bottom" });
  if (unit.body[0]) text(s, unit.body[0], { x: tb.x, y: 4.2, w: tb.w, h: 1.0 }, { size: SCALE.slide_subtitle, min: 14, color: C.dark.muted });
  const when = new Date().toLocaleDateString("en-US", { month: "long", year: "numeric" });
  text(s, when, { x: M, y: FOOTER_Y - 0.4, w: 6, h: 0.35 }, { size: 12, min: 12, color: C.dark.muted, valign: "bottom" });
  // motif: the section marker at hero size, hollow, right of the title column
  const d = 3.2, mx = W - M - d, my = (H - d) / 2;
  s.addShape(pres.shapes.OVAL, { x: mx, y: my, w: d, h: d, fill: { color: C.dark.surface }, line: { color: C.dark.secondary, width: 4 } });
  if (unit.notes) s.addNotes(unit.notes);
};

layouts.agenda = (unit) => {
  const s = newSlide(unit);
  const spec = parseVisual(unit.visual || "");
  const lb = grid(1, 7);
  const rowH = Math.min(0.9, BODY_H / Math.max(unit.body.length, 1));
  unit.body.forEach((item, k) => {
    const y = BODY_Y + k * rowH;
    numberBadge(s, k + 1, lb.x, y + 0.05, 0.45, C.secondary, 14);
    text(s, item, { x: lb.x + 0.7, y, w: lb.w - 0.7, h: rowH - 0.1 }, { size: 18, min: 14, valign: "middle" });
  });
  const rb = grid(9, 4);
  card(s, { x: rb.x, y: BODY_Y, w: rb.w, h: 2.0 });
  text(s, "What we need from you today", { x: rb.x + 0.3, y: BODY_Y + 0.25, w: rb.w - 0.6, h: 0.4 }, { size: 13, min: 12, bold: true, color: C.muted });
  text(s, spec.ask || spec.text || "", { x: rb.x + 0.3, y: BODY_Y + 0.7, w: rb.w - 0.6, h: 1.1 }, { size: 15, min: 12 });
};

layouts["section-divider"] = (unit) => {
  const s = pres.addSlide();
  slideCount += 1;
  s.background = { color: C.dark.surface };
  numberBadge(s, unit.n, M, M, 1.4, C.dark.secondary, 48);
  text(s, unit.title, { x: M, y: 2.6, w: W - 2 * M, h: 2.0 }, { font: FONT.display, size: 36, min: 24, step: 4, bold: true, color: C.dark.ink, valign: "bottom" });
  if (unit.body[0]) text(s, unit.body[0], { x: M, y: 4.8, w: grid(1, 9).w, h: 1.0 }, { size: SCALE.slide_subtitle, min: 14, color: C.dark.muted });
  if (unit.notes) s.addNotes(unit.notes);
};

layouts["claim-evidence"] = (unit) => {
  // bullets on the left (5 columns), the visual on the right (7 columns)
  const lb = grid(1, 5), rb = grid(6, 7);
  let rest = unit.body, page = 0;
  while (rest.length || page === 0) {
    const s = newSlide(unit, page ? { titleOverride: unit.title + " (continued)", noNotes: true } : {});
    const box = { x: lb.x, y: BODY_Y, w: lb.w, h: BODY_H };
    let take = rest.length;
    while (take > 1 && !fitParagraphs(rest.slice(0, take), box, { font: FONT.body, sizes: [14], paraGap: 0.6, indentIn: 0.3 }).fits) take--;
    if (take) bulletList(s, rest.slice(0, take), box);
    drawVisual(s, { x: rb.x, y: BODY_Y, w: rb.w, h: BODY_H }, unit);
    rest = rest.slice(take);
    page++;
  }
};

layouts["stat-callout"] = (unit) => {
  const s = newSlide(unit);
  const spec = parseVisual(unit.visual || "");
  visuals.stat(s, { x: M, y: BODY_Y, w: W - 2 * M, h: BODY_H }, spec, unit);
};

layouts["two-column-comparison"] = (unit) => {
  const s = newSlide(unit);
  const spec = parseVisual(unit.visual || "");
  visuals["two-column"](s, { x: M, y: BODY_Y, w: W - 2 * M, h: BODY_H }, spec, unit);
};

layouts.table = (unit) => {
  const spec = parseVisual(unit.visual || "");
  const columns = spec.columns ? cells(spec.columns) : ["Capability", "What changes"];
  let rows = items(spec.rows).map(cells);
  if (!rows.length) rows = unit.body.map(splitLabel).filter((r) => r[1]);
  let page = 0;
  do {
    const s = newSlide(unit, page ? { titleOverride: unit.title + " (continued)", noNotes: true } : {});
    rows = drawTable(s, { x: M, y: BODY_Y, w: W - 2 * M, h: BODY_H }, columns, rows,
      { highlight: num(spec.highlight, 0), size: 15, minRow: Math.min(0.65, (BODY_H - 0.05) / (rows.length + 1)) });
    page++;
  } while (rows.length && page < 4);
};

layouts.timeline = (unit) => {
  const s = newSlide(unit);
  visuals.timeline(s, { x: M, y: BODY_Y, w: W - 2 * M, h: BODY_H }, parseVisual(unit.visual || ""), unit);
};

layouts["process-flow"] = (unit) => {
  const s = newSlide(unit);
  visuals["process-flow"](s, { x: M, y: BODY_Y, w: W - 2 * M, h: BODY_H }, parseVisual(unit.visual || ""), unit);
};

layouts.quote = (unit) => {
  const s = newSlide(unit);
  const [quote = "", attribution = "", claim = ""] = unit.body;
  const qb = grid(2, 10);
  s.addText("“", { x: M, y: BODY_Y - 0.2, w: 1.0, h: 1.2, fontFace: FONT.display, fontSize: 96, bold: true, color: C.accent, isTextBox: true, margin: 0 });
  text(s, quote, { x: qb.x, y: BODY_Y + 0.3, w: qb.w, h: 2.4 }, { font: FONT.display, size: 24, min: 18, step: 2, color: C.ink });
  text(s, attribution, { x: qb.x, y: BODY_Y + 2.9, w: qb.w, h: 0.5 }, { size: 14, min: 12, color: C.muted });
  if (claim) text(s, claim, { x: M, y: BODY_BOTTOM - 0.6, w: W - 2 * M, h: 0.6 }, { size: 15, min: 12, bold: true, color: C.secondary, valign: "bottom" });
};

layouts["risk-matrix"] = (unit) => {
  const s = newSlide(unit);
  const spec = parseVisual(unit.visual || "");
  const gb = grid(1, 6), mb = grid(8, 5);
  visuals["risk-grid"](s, { x: gb.x, y: BODY_Y, w: gb.w, h: BODY_H }, spec, unit);
  const risks = items(spec.risks).map(cells);
  let mits = items(spec.mitigations);
  if (!mits.length) mits = unit.body.map((b) => splitLabel(b)[1] || b);
  const rowH = BODY_H / Math.max(risks.length || mits.length, 1);
  (risks.length ? risks : mits.map((m) => [m])).forEach(([name], k) => {
    const y = BODY_Y + k * rowH;
    numberBadge(s, k + 1, mb.x, y + 0.05, 0.4, C.secondary, 13);
    text(s, name, { x: mb.x + 0.6, y, w: mb.w - 0.6, h: 0.45 }, { size: 14, min: 12, bold: true });
    text(s, mits[k] || "", { x: mb.x + 0.6, y: y + 0.45, w: mb.w - 0.6, h: rowH - 0.55 }, { size: 13, min: 12, color: C.muted });
  });
};

layouts["ask-next-steps"] = (unit) => {
  const s = newSlide(unit, { dark: true });
  const spec = parseVisual(unit.visual || "");
  const steps = unit.body.slice(0, -1), consequence = unit.body[unit.body.length - 1] || "";
  const bandH = 0.85;
  rect(s, { x: M, y: BODY_Y, w: W - 2 * M, h: bandH }, C.dark.secondary);
  text(s, spec.ask || unit.title, { x: M + 0.3, y: BODY_Y, w: W - 2 * M - 0.6, h: bandH }, { size: 18, min: 14, bold: true, color: C.white, valign: "middle" });
  const stepB = grid(1, 8), ownerB = grid(9, 2), dateB = grid(11, 2);
  const headY = BODY_Y + bandH + 0.3;
  [["Step", stepB], ["Owner", ownerB], ["Date", dateB]].forEach(([h, b]) =>
    text(s, h, { x: b.x + (h === "Step" ? 0.7 : 0), y: headY, w: b.w - (h === "Step" ? 0.7 : 0), h: 0.3 }, { size: 12, min: 12, bold: true, color: C.dark.muted }));
  const rowsTop = headY + 0.4, rowsH = BODY_BOTTOM - 0.7 - rowsTop;
  const rowH = Math.min(0.9, rowsH / Math.max(steps.length, 1));
  const owners = items(spec.owners), dates = items(spec.dates);
  steps.forEach((t, k) => {
    const y = rowsTop + k * rowH;
    numberBadge(s, k + 1, stepB.x, y + 0.1, 0.45, C.dark.secondary, 14);
    text(s, t, { x: stepB.x + 0.7, y, w: stepB.w - 0.7, h: rowH - 0.1 }, { size: 15, min: 12, color: C.dark.ink, valign: "middle" });
    [[ownerB, owners[k]], [dateB, dates[k]]].forEach(([b, val]) => {
      if (val) text(s, val, { x: b.x, y, w: b.w, h: rowH - 0.1 }, { size: 14, min: 12, color: C.dark.ink, valign: "middle" });
      else line(s, b.x, y + rowH - 0.25, b.w, 0, C.dark.muted, { width: 0.75 });
    });
  });
  if (consequence) text(s, consequence, { x: M, y: BODY_BOTTOM - 0.5, w: W - 2 * M, h: 0.5 }, { size: 13, min: 12, color: C.dark.muted, valign: "bottom" });
};

layouts["appendix-sources"] = (unit, deck) => {
  let rows = deck.sources.map((r) => r);
  let page = 0;
  do {
    const s = newSlide(unit, { noMarker: true, noSourceFooter: true, titleOverride: page ? unit.title + " (continued)" : unit.title, noNotes: page > 0 });
    const box = { x: M, y: BODY_Y, w: W - 2 * M, h: BODY_H };
    rows = drawTable(s, box, ["Id", "Claim or figure", "Governing artifact and section"], rows,
      { size: 12, colW: [0.6, (box.w - 0.6) * 0.62, (box.w - 0.6) * 0.38], boldFirst: true });
    page++;
  } while (rows.length && page < 6);
};

// ---------------------------------------------------------------- main
const deck = parseScript(fs.readFileSync(scriptPath, "utf8"));
pres.title = deck.title;
pres.author = "HELIX";
for (const unit of deck.units) {
  const fn = layouts[unit.pattern];
  if (!fn) {
    console.error(`render-deck.js: unit ${unit.n} uses unknown pattern '${unit.pattern}'; rendering as claim-evidence`);
    layouts["claim-evidence"](unit, deck);
    continue;
  }
  fn(unit, deck);
}
pres.writeFile({ fileName: outPath }).then(() => {
  console.log(`wrote ${outPath} (${slideCount} slides from ${deck.units.length} units)`);
});
