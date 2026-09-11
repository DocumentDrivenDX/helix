#!/usr/bin/env node
// render-deck.js — render a HELIX deliverable script (deck) to .pptx.
//
// Usage: render-deck.js <script.md> <out.pptx> [--theme theme.yml] [--patterns slide-patterns.yml] [--look <id>]
//
// Reads the deliverable Markdown script (frontmatter, ## Content units with
// **Pattern**/**Body**/**Visual**/**Notes**/**Sources**, the ## Sources
// table), lays each unit out by its pattern on a 12-column grid using the
// theme's margins and type scale, and writes one slide per unit (plus
// continuation slides when a unit's text cannot fit at the size floor).
// Visuals are drawn from the structured spec on the **Visual** line
// (workflows/deliverables/visual-specs.md). A look (font pairing, surface
// mode, marker shape, dominant hue) comes from the Brief's **Look** line,
// `--look`, or the theme's default. Icons are the SVGs beside this script in
// icons/, rasterized through rsvg-convert (or ImageMagick) and embedded as
// PNG; without either tool badges fall back to numbers. Needs pptxgenjs on
// NODE_PATH.
"use strict";
const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");

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
  console.error("usage: render-deck.js <script.md> <out.pptx> [--theme theme.yml] [--patterns slide-patterns.yml] [--look <id>]");
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

// The script is parsed before the theme resolves because the Brief's **Look** picks the look.
const deck = parseScript(fs.readFileSync(scriptPath, "utf8"));

const hex = (c) => String(c).replace("#", "").toUpperCase();
const LOOKS = theme.looks || {};
const lookId = flags.look || deck.brief.Look || LOOKS.default || "editorial";
const look = LOOKS[lookId] || {};
if (!LOOKS[lookId]) console.error(`render-deck.js: no look '${lookId}' in ${themePath}; using the theme's base typography`);
const SURF = look.surfaces || "sandwich";            // sandwich | light | dark
const DOMINANT = look.dominant || "primary";         // which theme hue leads
const P = theme.palette;
function palette(dark) {
  const src = dark ? P.dark : P;
  const order = [DOMINANT, ...["primary", "secondary", "accent"].filter((h) => h !== DOMINANT)];
  return {
    main: hex(src[order[0]]), support: hex(src[order[1]]), spark: hex(src[order[2]]),
    ink: hex(src.ink), muted: hex(src.muted), surface: hex(src.surface), alt: hex(src.surface_alt), border: hex(src.border),
    white: "FFFFFF", hot: dark ? "3A2622" : "F6E4DF",
  };
}
const PAL = { light: palette(false), dark: palette(true) };
let K = PAL.light;                                    // the palette of the slide being drawn
const FONT = {
  display: (look.display && look.display.family) || theme.typography.display.family,
  body: (look.body && look.body.family) || theme.typography.body.family,
};
const SCALE = Object.assign({}, theme.typography.scale, look.scale || {});
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
const MARKER = Object.assign({ size_in: 0.55, shape: "circle" }, theme.motif.section_marker || {}, look.marker ? { shape: look.marker } : {});
const MIN_PT = 12;                            // no text below this on content slides
const DARK_CONTENT = SURF === "dark";         // content slides on the dark surface
const DARK_ENDS = SURF !== "light";           // title, dividers, statements, and the ask on the dark surface

function grid(col, span) {
  // col is 1-based; returns x and w for `span` columns starting at `col`
  return { x: M + (col - 1) * (CW + G), w: span * CW + (span - 1) * G };
}

// ---------------------------------------------------------------- measuring
// Average glyph width as a fraction of the point size, per typeface.
const WIDTH_FACTOR = { Georgia: 0.58, Arial: 0.5, "Courier New": 0.6, "Times New Roman": 0.46, "Trebuchet MS": 0.53, Verdana: 0.62,
  "Arial Black": 0.66, Cambria: 0.52, Calibri: 0.47, "Century Schoolbook": 0.56, "Bookman Old Style": 0.6 };  // average em per character; bold runs wider
const LINE_HEIGHT = 1.2;

function textWidthIn(str, font, pt, bold) {
  const f = WIDTH_FACTOR[font] || 0.52;
  return (str.length * pt * f * (bold ? 1.2 : 1)) / 72;
}
function wrap(str, font, pt, bold, widthIn) {
  const lines = [];
  let cur = "";
  lines.overwide = false;
  for (const word of String(str).split(/\s+/).filter(Boolean)) {
    const next = cur ? cur + " " + word : word;
    if (textWidthIn(next, font, pt, bold) <= widthIn || !cur) cur = next;
    else { lines.push(cur); cur = word; }
    // a single word wider than the box breaks mid-word in the renderer: that size does not fit, whatever the height
    if (textWidthIn(word, font, pt, bold) > widthIn) lines.overwide = true;
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
    let height = 0, lines = 0, overwide = false;
    paras.forEach((p, k) => {
      const w = wrap(p, font, pt, bold, box.w - indentIn);
      const n = w.length;
      overwide = overwide || w.overwide;
      lines += n;
      height += (n * pt * LINE_HEIGHT) / 72;
      if (k < paras.length - 1) height += (paraGap * pt) / 72;
    });
    last = { pt, fits: height <= box.h && !overwide, height, lines };
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
    color: o.color || K.ink, align: o.align || "left", valign: o.valign || "top", isTextBox: true, margin: 0,
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
    { x: box.x, y: box.y, w: box.w, h: box.h, fontFace: font, fontSize: fit.pt, color: o.color || K.ink, isTextBox: true, margin: 0, valign: "top" }
  );
  return fit;
}
function rect(slide, box, fill, o = {}) {
  slide.addShape(o.round === false ? pres.shapes.RECTANGLE : pres.shapes.ROUNDED_RECTANGLE, {
    x: box.x, y: box.y, w: box.w, h: box.h, rectRadius: o.radius == null ? 0.1 : o.radius,
    fill: { color: fill }, line: { color: o.line || fill, width: o.lineWidth == null ? 0.75 : o.lineWidth },
  });
}
function card(slide, box) {
  rect(slide, box, K.alt, { line: K.border });
}
function circle(slide, x, y, d, fill) {
  slide.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: fill }, line: { color: fill } });
}
// ---------------------------------------------------------------- icons
const ICON_DIR = path.join(__dirname, "icons");
const iconCache = new Map();
let iconToolWarned = false;
function iconData(name, colorHex) {
  // PNG data URI for icons/<name>.svg in the given hue, or null when the icon or a rasterizer is missing.
  const file = path.join(ICON_DIR, String(name).trim() + ".svg");
  if (!fs.existsSync(file)) { console.error(`render-deck.js: no icon '${name}' in ${ICON_DIR}; badge falls back to its number`); return null; }
  const key = name + "#" + colorHex;
  if (iconCache.has(key)) return iconCache.get(key);
  const svg = fs.readFileSync(file, "utf8").replace(/currentColor/g, "#" + colorHex);
  let png = null;
  for (const [cmd, args] of [["rsvg-convert", ["-w", "256", "-h", "256"]], ["magick", ["-background", "none", "-density", "384", "svg:-", "png:-"]]]) {
    try { png = execFileSync(cmd, args, { input: svg, stdio: ["pipe", "pipe", "ignore"] }); break; } catch (e) { png = null; }
  }
  if (!png && !iconToolWarned) { iconToolWarned = true; console.error("render-deck.js: neither rsvg-convert nor magick can rasterize icons; badges fall back to numbers"); }
  const data = png ? "image/png;base64," + png.toString("base64") : null;
  iconCache.set(key, data);
  return data;
}
// A badge: the look's marker shape filled with `fill`, holding an icon when one is named and rasterizes, else the number `n`.
// shape "none" draws the glyph alone in `fill` (for icons on a colored band).
function badge(slide, x, y, d, fill, o = {}) {
  const shape = o.shape || MARKER.shape || "circle";
  if (shape !== "none") slide.addShape(shape === "square" ? pres.shapes.ROUNDED_RECTANGLE : pres.shapes.OVAL,
    { x, y, w: d, h: d, rectRadius: shape === "square" ? d * 0.18 : 0, fill: { color: fill }, line: { color: fill } });
  const glyph = shape === "none" ? fill : K.white;
  const data = o.icon ? iconData(o.icon, glyph) : null;
  if (data) {
    const inset = shape === "none" ? 0 : d * 0.2;
    slide.addImage({ data, x: x + inset, y: y + inset, w: d - 2 * inset, h: d - 2 * inset });
    return true;
  }
  if (o.n != null) slide.addText(String(o.n), { x, y, w: d, h: d, fontFace: FONT.display, fontSize: o.pt || Math.round(d * 30), bold: true,
    color: glyph, align: "center", valign: "middle", isTextBox: true, margin: 0 });
  return false;
}
function numberBadge(slide, n, x, y, d, fill, fontPt, icon) { badge(slide, x, y, d, fill, { n, pt: fontPt, icon }); }
// The hero motif: the marker shape at hero size, hollow, in the support hue; an icon inside when named.
function hero(slide, icon, o = {}) {
  const d = o.size || 3.2, mx = W - M - d, my = o.y == null ? (H - d) / 2 : o.y;
  const shape = MARKER.shape === "square" ? pres.shapes.ROUNDED_RECTANGLE : pres.shapes.OVAL;
  slide.addShape(shape, { x: mx, y: my, w: d, h: d, rectRadius: MARKER.shape === "square" ? d * 0.18 : 0, fill: { color: K.surface }, line: { color: K.support, width: 4 } });
  if (icon) { const id = d * 0.46; badge(slide, mx + (d - id) / 2, my + (d - id) / 2, id, K.support, { icon, shape: "none" }); }
}
function line(slide, x, y, w, h, color, o = {}) {
  slide.addShape(pres.shapes.LINE, { x, y, w, h, line: { color, width: o.width || 1.5, dashType: o.dash || "solid",
    beginArrowType: o.begin || "none", endArrowType: o.end || "none" } });
}
function chevron(slide, box, fill) {
  slide.addShape(pres.shapes.CHEVRON, { x: box.x, y: box.y, w: box.w, h: box.h, fill: { color: fill }, line: { color: K.white, width: 1.5 } });
}

// Chrome shared by content slides: numbered marker, title, footer, notes.
function chrome(slide, unit, o = {}) {
  const dark = o.dark == null ? DARK_CONTENT : !!o.dark;
  K = dark ? PAL.dark : PAL.light;
  slideCount += 1;
  slide.background = { color: K.surface };
  const size = MARKER.size_in || 0.55;
  if (!o.noMarker) numberBadge(slide, unit.n, M, TITLE_Y + 0.12, size, K.support, 16, o.icon);
  const tx = o.noMarker ? M : M + size + 0.3;
  const titleStr = o.titleOverride || unit.title;
  text(slide, titleStr, { x: tx, y: TITLE_Y, w: W - M - tx, h: TITLE_H },
    { font: FONT.display, size: SCALE.slide_title, min: 24, step: 4, bold: true, color: K.ink });
  const mutedC = K.muted;
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
function bareSlide(dark) {
  // a slide without the title chrome (title, divider, statement); sets the palette
  const s = pres.addSlide();
  K = dark ? PAL.dark : PAL.light;
  slideCount += 1;
  s.background = { color: K.surface };
  return s;
}
function footer(slide, unit, o = {}) {
  const cited = (unit.sources.match(/S\d+/g) || []).join(", ");
  if (cited && !o.noSourceFooter) slide.addText("Sources: " + cited + " (appendix)", { x: M, y: FOOTER_Y, w: 8, h: FOOTER_H, fontFace: FONT.body,
    fontSize: theme.motif.footer_source.size_pt || 9, color: K.muted, isTextBox: true, margin: 0, valign: "bottom" });
  slide.addText(String(slideCount), { x: W - M - 0.6, y: FOOTER_Y, w: 0.6, h: FOOTER_H, fontFace: FONT.body,
    fontSize: theme.motif.slide_number.size_pt || 10, color: K.muted, align: "right", isTextBox: true, margin: 0, valign: "bottom" });
  if (unit.notes) slide.addNotes(unit.notes);
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
  const chevH = Math.min(steps.length >= 5 ? 0.8 : 1.15, box.h * 0.3, stepW * 0.42);  // narrower chevrons need a shallower notch so labels fit
  const y = box.y + (box.h > 3 ? 0.9 : 0.2);
  const hasDetails = steps.some((label, k) => details[k] || byLabel.get(label.toLowerCase()));
  const captionY = y + chevH + (hasDetails ? 1.3 : 0.3);
  steps.forEach((label, k) => {
    const x = box.x + k * (stepW + gap);
    const active = k + 1 === hl;
    chevron(slide, { x, y, w: stepW, h: chevH }, active ? K.support : K.main);
    const inset = chevH * 0.55; // clear the notch on the left and the point on the right
    text(slide, label, { x: x + inset, y: y + 0.1, w: stepW - 2 * inset, h: chevH - 0.2 },
      { size: 16, min: 12, bold: true, color: K.white, align: "center", valign: "middle" });
    const detail = details[k] || byLabel.get(label.toLowerCase()) || "";
    if (detail) text(slide, detail, { x: x + 0.1, y: y + chevH + 0.2, w: stepW - 0.2, h: 1.0 },
      { size: 14, min: 12, color: K.muted, align: "center" });
    if (active && spec.caption) {
      const cx = Math.max(box.x, Math.min(x - 0.4, box.x + box.w - (stepW + 0.8)));  // keep the caption inside the box
      text(slide, spec.caption, { x: cx, y: captionY, w: stepW + 0.8, h: 0.6 },
      { size: 14, min: 12, bold: true, color: K.support, align: "center" });
    }
  });
};

visuals.timeline = (slide, box, spec) => {
  const ms = items(spec.milestones).slice(0, 6);
  if (!ms.length) return placeholder(slide, box, spec);
  const now = num(spec.now, 0);
  const mid = box.y + box.h * 0.4;
  const pad = 0.6;
  line(slide, box.x + pad, mid, box.w - 2 * pad, 0, K.border, { width: 3 });
  const segW = (box.w - 2 * pad) / Math.max(ms.length - 1, 1);
  const labelW = Math.min(segW, box.w / 2) - 0.1;
  ms.forEach((label, k) => {
    const cx = box.x + pad + k * segW;
    const active = k + 1 === now;
    circle(slide, cx - 0.15, mid - 0.15, 0.3, active ? K.support : K.main);
    const above = k % 2 === 0;
    const lx = Math.min(Math.max(cx - labelW / 2, box.x), box.x + box.w - labelW);
    const lb = { x: lx, y: above ? mid - 0.95 : mid + 0.25, w: labelW, h: 0.7 };
    text(slide, label, lb, { size: 14, min: 12, bold: active, color: active ? K.support : K.ink, align: "center", valign: above ? "bottom" : "top" });
    if (active && spec.marker) {
      line(slide, cx, mid + 0.95, 0, 0.3, K.support, { dash: "dash", width: 2 });
      const mw = labelW + 0.8, mx = Math.min(Math.max(cx - mw / 2, box.x), box.x + box.w - mw);
      text(slide, spec.marker, { x: mx, y: mid + 1.3, w: mw, h: 0.5 },
        { size: 13, min: 12, bold: true, color: K.support, align: "center" });
    }
  });
  if (spec.caption) text(slide, spec.caption, { x: box.x + 0.2, y: box.y + box.h - 0.55, w: box.w - 0.4, h: 0.5 },
    { size: 12, min: 12, color: K.muted, align: "center", valign: "bottom" });
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
  const icons = items(spec.icons);
  [left, right].forEach((head, side) => {
    const x = box.x + side * (colW + G);
    rect(slide, { x, y: box.y, w: colW, h: cardH }, side === prefer ? K.surface : K.alt, { line: K.border });
    const ix = icons[side] ? 0.6 : 0;
    if (icons[side]) badge(slide, x + padX, box.y + 0.12, 0.45, side === prefer ? K.main : K.muted, { icon: icons[side] });
    text(slide, head, { x: x + padX + ix, y: box.y + 0.2, w: colW - 2 * padX - ix, h: headH - 0.2 },
      { font: FONT.display, size: 20, min: 16, bold: true, color: side === prefer ? K.main : K.muted });
    rows.forEach((r, k) => {
      const ry = box.y + headH + 0.1 + k * rowH;
      const mark = side === prefer;
      if (mark) numberBadge(slide, "✓", x + padX, ry + 0.05, 0.32, K.main, 12);
      text(slide, r[side] || "", { x: x + padX + (mark ? 0.5 : 0), y: ry, w: colW - 2 * padX - (mark ? 0.5 : 0), h: rowH - 0.15 },
        { size: 15, min: 12, color: K.ink });
    });
  });
  if (verdict) text(slide, "Verdict: " + verdict, { x: box.x, y: box.y + cardH + 0.2, w: box.w, h: verdictH },
    { size: 15, min: 12, bold: true, color: K.support, valign: "middle" });
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
      bold: ri === 0 || (k === 0 && o.boldFirst !== false), color: ri === 0 ? K.white : k === 0 ? K.muted : K.ink, fontSize: pt,
      fill: { color: ri === 0 ? K.main : ri === o.highlight ? K.alt : K.surface }, valign: "middle",
    },
  })));
  slide.addTable(data, { x: box.x, y: box.y, w: box.w, colW, rowH: heights.slice(0, keep + 1), fontFace: FONT.body,
    border: { type: "solid", color: K.border, pt: 0.75 }, margin: pad });
  return rows.slice(keep);
}

visuals.stat = (slide, box, spec, unit) => {
  let stats = items(spec.stats).map(cells).slice(0, 3);
  if (!stats.length) stats = unit.body.slice(0, 3).map((b) => { const m = b.match(/^([<>]?\s?\$?\d[\d,.]*\s?[%kKMBx+]*|[<>]\s?\d+)\s*(.*)$/); return m ? [m[1].trim(), m[2]] : [b, ""]; });
  const cardW = (stats.length ? (box.w - G * (stats.length - 1)) / stats.length : box.w);
  const hues = stats.length === 2 ? [K.main, K.support] : [K.main, K.spark, K.support];
  const icons = items(spec.icons);
  const iconH = icons.length ? 0.75 : 0;
  stats.forEach(([value, caption], k) => {
    const x = box.x + k * (cardW + G);
    card(slide, { x, y: box.y, w: cardW, h: box.h });
    const inner = { x: x + 0.25, w: cardW - 0.5 };
    if (icons[k]) badge(slide, x + cardW / 2 - 0.3, box.y + 0.25, 0.6, hues[k], { icon: icons[k] });
    const numH = Math.min(1.6, box.h * 0.4 - iconH * 0.5);
    text(slide, value, { x: inner.x, y: box.y + 0.3 + iconH, w: inner.w, h: numH },
      { font: FONT.display, size: SCALE.stat_callout, min: 28, step: 8, bold: false, color: hues[k], align: "center", valign: "middle" });
    text(slide, caption || "", { x: inner.x, y: box.y + numH + 0.5 + iconH, w: inner.w, h: box.h - numH - 1.2 - iconH },
      { size: 15, min: 12, color: K.ink, align: "center" });
    if (spec.label) text(slide, spec.label.toUpperCase(), { x: inner.x, y: box.y + box.h - 0.55, w: inner.w, h: 0.35 },
      { size: 12, min: 12, bold: true, color: K.muted, align: "center", valign: "bottom" });
  });
};

visuals.panels = (slide, box, spec) => {
  const list = items(spec.items).map(cells).slice(0, 4);
  if (!list.length) return placeholder(slide, box, spec);
  const icons = items(spec.icons);
  const hues = [K.main, K.spark, K.support, K.main];
  const cardW = (box.w - G * (list.length - 1)) / list.length;
  list.forEach(([name, detail], k) => {
    const x = box.x + k * (cardW + G);
    card(slide, { x, y: box.y, w: cardW, h: box.h });
    const d = Math.min(1.0, cardW * 0.45);
    badge(slide, x + (cardW - d) / 2, box.y + 0.5, d, hues[k], { n: k + 1, pt: 24, icon: icons[k] });
    text(slide, name, { x: x + 0.08, y: box.y + d + 0.75, w: cardW - 0.16, h: 0.5 }, { size: 16, min: 12, bold: true, align: "center" });
    text(slide, detail || "", { x: x + 0.15, y: box.y + d + 1.3, w: cardW - 0.3, h: box.h - d - 1.5 }, { size: 13, min: 12, color: K.muted, align: "center" });
  });
};

visuals.boundary = (slide, box, spec) => {
  rect(slide, box, K.alt, { line: K.border, lineWidth: 1 });
  text(slide, spec.outer || "outside", { x: box.x + 0.3, y: box.y + 0.2, w: box.w - 0.6, h: 0.4 }, { size: 14, min: 12, bold: true, color: K.muted, align: "center" });
  if (spec["outer-note"]) text(slide, spec["outer-note"], { x: box.x + 0.3, y: box.y + 0.6, w: box.w - 0.6, h: 0.35 }, { size: 12, min: 12, color: K.muted, align: "center" });
  const iw = Math.min(3.0, box.w * 0.5), ih = 1.5;
  const ix = box.x + (box.w - iw) / 2, iy = box.y + (box.h - ih) / 2 + 0.2;
  rect(slide, { x: ix, y: iy, w: iw, h: ih }, K.main);
  text(slide, spec.inner || "inside", { x: ix + 0.2, y: iy + 0.25, w: iw - 0.4, h: 0.5 }, { font: FONT.display, size: 18, min: 14, bold: true, color: K.white, align: "center" });
  if (spec["inner-note"]) text(slide, spec["inner-note"], { x: ix + 0.2, y: iy + 0.8, w: iw - 0.4, h: 0.5 }, { size: 13, min: 12, color: K.white, align: "center" });
  const arrowW = Math.min(1.0, (ix - box.x) - 0.4);
  line(slide, ix + iw + 0.1, iy + ih / 2, arrowW, 0, K.support, { width: 2, end: "triangle" });
  line(slide, ix - 0.1 - arrowW, iy + ih / 2, arrowW, 0, K.support, { width: 2, begin: "triangle" });
  if (spec.caption) text(slide, spec.caption, { x: box.x + 0.3, y: box.y + box.h - 0.75, w: box.w - 0.6, h: 0.6 }, { size: 12, min: 12, color: K.muted, align: "center", valign: "bottom" });
};

visuals.helix = (slide, box, spec) => {
  card(slide, box);
  const pillW = 0.9, pillH = box.h - 1.7, top = box.y + 0.75;
  const lx = box.x + box.w * 0.22 - pillW / 2, rx = box.x + box.w * 0.78 - pillW / 2;
  rect(slide, { x: lx, y: top, w: pillW, h: pillH }, K.main, { radius: 0.45 });
  rect(slide, { x: rx, y: top, w: pillW, h: pillH }, K.support, { radius: 0.45 });
  const rungs = 3;
  for (let k = 1; k <= rungs; k++) line(slide, lx + pillW, top + (pillH * k) / (rungs + 1), rx - lx - pillW, 0, K.spark, { width: 2.5 });
  const midW = rx - lx - pillW - 0.4;
  if (spec.rungs) text(slide, spec.rungs, { x: lx + pillW + 0.2, y: top + pillH / 2 - 0.4, w: midW, h: 0.35 }, { size: 12, min: 12, bold: true, color: K.spark, align: "center", valign: "bottom" });
  const noteW = Math.max(pillW + 1.2, 2.0);
  text(slide, spec.left || "", { x: lx + pillW / 2 - noteW / 2, y: top + pillH + 0.1, w: noteW, h: 0.35 }, { size: 12, min: 12, bold: true, color: K.main, align: "center" });
  text(slide, spec.right || "", { x: rx + pillW / 2 - noteW / 2, y: top + pillH + 0.1, w: noteW, h: 0.35 }, { size: 12, min: 12, bold: true, color: K.support, align: "center" });
  if (spec["left-note"]) text(slide, spec["left-note"], { x: lx + pillW / 2 - noteW / 2, y: box.y + 0.2, w: noteW, h: 0.4 }, { size: 12, min: 12, color: K.muted, align: "center" });
  if (spec["right-note"]) text(slide, spec["right-note"], { x: rx + pillW / 2 - noteW / 2, y: box.y + 0.2, w: noteW, h: 0.4 }, { size: 12, min: 12, color: K.muted, align: "center" });
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
    rect(slide, { x: gridX + c * cw, y: gridY + r * ch, w: cw, h: ch }, hot ? K.hot : K.alt, { round: false, line: K.border });
  }
  // dots that share a cell spread sideways around the cell's center
  const placed = risks.map(([, lik, imp]) => ({ row: 2 - level(lik), col: level(imp) }));
  const perCell = {}, seen = {};
  placed.forEach((p) => { perCell[p.row + ":" + p.col] = (perCell[p.row + ":" + p.col] || 0) + 1; });
  placed.forEach((p, k) => {
    const key = p.row + ":" + p.col, count = perCell[key], slot = seen[key] = (seen[key] || 0) + 1;
    const d = 0.45, pitch = d + 0.1;
    const cx = gridX + p.col * cw + cw / 2 - d / 2 + (slot - (count + 1) / 2) * pitch;
    numberBadge(slide, k + 1, cx, gridY + p.row * ch + ch / 2 - d / 2, d, K.support, 14);
  });
  ["high", "medium", "low"].forEach((lvl, r) =>
    text(slide, lvl, { x: box.x, y: gridY + r * ch, w: axisW - 0.1, h: ch }, { size: 12, min: 12, color: K.muted, align: "right", valign: "middle" }));
  text(slide, "likelihood (rows) by impact: low, medium, high", { x: gridX, y: gridY + gh + 0.1, w: gw, h: 0.4 }, { size: 12, min: 12, color: K.muted, align: "center" });
};


visuals["layer-stack"] = (slide, box, spec, unit) => {
  // Horizontal bands top to bottom with arrows between them: authority, precedence, a stack.
  const layers = items(spec.layers).slice(0, 6);
  if (!layers.length) return placeholder(slide, box, spec, unit);
  const icons = items(spec.icons), details = items(spec.details);
  const byLabel = new Map(unit.body.map(splitLabel).map(([l, d]) => [l.toLowerCase(), d]));
  const hl = num(spec.highlight, 0);
  const capH = spec.caption ? 0.5 : 0;
  const gap = 0.3;
  const bandH = Math.min(0.95, (box.h - capH - gap * (layers.length - 1)) / layers.length);
  const labelW = Math.min(3.2, box.w * 0.34);
  layers.forEach((label, k) => {
    const y = box.y + k * (bandH + gap);
    const active = k + 1 === hl;
    rect(slide, { x: box.x, y, w: box.w, h: bandH }, active ? K.support : K.main, { radius: 0.08 });
    const d = Math.min(0.5, bandH - 0.3);
    let tx = box.x + 0.25;
    if (icons[k]) { badge(slide, tx, y + (bandH - d) / 2, d, K.white, { icon: icons[k], shape: "none" }); tx += d + 0.15; }
    text(slide, label, { x: tx, y: y + 0.1, w: box.x + labelW - tx, h: bandH - 0.2 },
      { font: FONT.display, size: 18, min: 14, bold: true, color: K.white, valign: "middle" });
    const detail = details[k] || byLabel.get(label.toLowerCase()) || "";
    if (detail) text(slide, detail, { x: box.x + labelW + 0.2, y: y + 0.1, w: box.w - labelW - 0.45, h: bandH - 0.2 },
      { size: 14, min: 12, color: K.white, valign: "middle" });
    if (k < layers.length - 1) slide.addShape(pres.shapes.DOWN_ARROW, { x: box.x + labelW / 2 - 0.16, y: y + bandH + 0.03, w: 0.32, h: gap - 0.06,
      fill: { color: K.muted }, line: { color: K.muted } });
  });
  if (spec.caption) text(slide, spec.caption, { x: box.x, y: box.y + box.h - capH + 0.05, w: box.w, h: capH - 0.05 },
    { size: 13, min: 12, bold: true, color: K.support, align: "center", valign: "bottom" });
};

visuals.cycle = (slide, box, spec, unit) => {
  // Pill nodes on a ring with direction arrows between them: a loop, a cadence, an iteration.
  const steps = items(spec.steps).slice(0, 8);
  if (steps.length < 3) return placeholder(slide, box, spec, unit);
  const icons = items(spec.icons);
  const hl = num(spec.highlight, 0);
  const capH = spec.caption ? 0.45 : 0;
  const pillW = steps.length > 6 ? 1.75 : 1.9, pillH = 0.6, d = 0.36;
  const cx = box.x + box.w / 2, cy = box.y + (box.h - capH) / 2;
  const ry = (box.h - capH) / 2 - pillH / 2 - 0.05;
  const rx = Math.min(box.w / 2 - pillW / 2 - 0.05, ry * 1.7);   // keep the ring a plausible ellipse on a wide box
  // the ring is a guide: it passes behind the pills, so deck-qa skips it (name starts with "guide")
  slide.addShape(pres.shapes.OVAL, { x: cx - rx, y: cy - ry, w: 2 * rx, h: 2 * ry, fill: { type: "none" },
    line: { color: K.border, width: 3, dashType: "dash" }, objectName: "guide ring" });
  const centerW = Math.min(3.0, 2 * rx - pillW - 0.8);
  if (spec.center && centerW > 1) text(slide, spec.center, { x: cx - centerW / 2, y: cy - 0.5, w: centerW, h: 1.0 },
    { font: FONT.display, size: 22, min: 12, bold: true, color: K.main, align: "center", valign: "middle" });
  const arrow = iconData("arrow-right", K.muted);
  steps.forEach((label, k) => {
    const th = -Math.PI / 2 + (2 * Math.PI * k) / steps.length;
    const nx = cx + rx * Math.cos(th), ny = cy + ry * Math.sin(th);
    const active = k + 1 === hl;
    const px = nx - pillW / 2, py = ny - pillH / 2;
    rect(slide, { x: px, y: py, w: pillW, h: pillH }, active ? K.support : K.main, { radius: pillH / 2 });
    let tx = px + 0.18;
    const has = icons[k] && badge(slide, tx, py + (pillH - d) / 2, d, K.white, { icon: icons[k], shape: "none" });
    if (has) tx += d + 0.1;
    else if (!icons[k]) { badge(slide, tx, py + (pillH - d) / 2, d, K.white, { n: k + 1, pt: 12, shape: "none" }); tx += d + 0.1; }
    text(slide, label, { x: tx, y: py + 0.05, w: px + pillW - tx - 0.15, h: pillH - 0.1 },
      { size: 14, min: 12, bold: true, color: K.white, valign: "middle" });
    if (arrow) {
      const tm = th + Math.PI / steps.length, ad = 0.28;
      slide.addImage({ data: arrow, x: cx + rx * Math.cos(tm) - ad / 2, y: cy + ry * Math.sin(tm) - ad / 2, w: ad, h: ad,
        rotate: ((Math.round((tm * 180) / Math.PI + 90) % 360) + 360) % 360, objectName: "guide arrow" });
    }
  });
  if (spec.caption) text(slide, spec.caption, { x: box.x, y: box.y + box.h - capH + 0.05, w: box.w, h: capH - 0.05 },
    { size: 13, min: 12, color: K.muted, align: "center", valign: "bottom" });
};

visuals.hub = (slide, box, spec, unit) => {
  // One center node fanning out to rows: one thing that routes, serves, or governs many.
  const spokes = items(spec.spokes).map(cells).slice(0, 8);
  if (!spokes.length) return placeholder(slide, box, spec, unit);
  const icons = items(spec.icons);
  const hl = num(spec.highlight, 0);
  const capH = spec.caption ? 0.45 : 0;
  const hubW = Math.min(2.4, box.w * 0.32), hubH = 1.1;
  const hx = box.x, hy = box.y + (box.h - capH) / 2 - hubH / 2;
  rect(slide, { x: hx, y: hy, w: hubW, h: hubH }, K.main, { radius: 0.12 });
  text(slide, spec.center || "", { x: hx + 0.2, y: hy + 0.1, w: hubW - 0.4, h: hubH - 0.2 },
    { font: FONT.display, size: 18, min: 13, bold: true, color: K.white, align: "center", valign: "middle" });
  const trunkX = hx + hubW + 0.45, listX = trunkX + 0.45, d = 0.5;
  const rowH = Math.min(0.85, (box.h - capH) / spokes.length);
  const top = box.y + ((box.h - capH) - rowH * spokes.length) / 2;
  line(slide, hx + hubW, hy + hubH / 2, trunkX - hx - hubW, 0, K.border, { width: 1.5 });
  if (spokes.length > 1) line(slide, trunkX, top + rowH / 2, 0, rowH * (spokes.length - 1), K.border, { width: 1.5 });
  spokes.forEach(([label, detail], k) => {
    const y = top + k * rowH, my = y + rowH / 2;
    const active = k + 1 === hl;
    line(slide, trunkX, my, listX - trunkX - 0.03, 0, K.border, { width: 1.5 });
    badge(slide, listX, my - d / 2, d, active ? K.support : K.main, { n: k + 1, icon: icons[k], pt: 13 });
    const tx = listX + d + 0.2, tw = box.x + box.w - tx;
    if (detail) {
      text(slide, label, { x: tx, y: y + 0.02, w: tw, h: rowH * 0.45 }, { size: 15, min: 12, bold: true, color: active ? K.support : K.ink, valign: "bottom" });
      text(slide, detail, { x: tx, y: y + rowH * 0.5, w: tw, h: rowH * 0.48 }, { size: 12, min: 12, color: K.muted });
    } else text(slide, label, { x: tx, y, w: tw, h: rowH }, { size: 15, min: 12, bold: true, color: active ? K.support : K.ink, valign: "middle" });
  });
  if (spec.caption) text(slide, spec.caption, { x: box.x, y: box.y + box.h - capH + 0.05, w: box.w, h: capH - 0.05 },
    { size: 13, min: 12, color: K.muted, align: "center", valign: "bottom" });
};

visuals["icon-list"] = (slide, box, spec, unit) => {
  // Rows of icon, label, detail; two columns when the box is wide and the list is long.
  let rows = items(spec.items).map(cells).slice(0, 8);
  if (!rows.length) rows = unit.body.map(splitLabel).map(([l, d]) => ["", l, d]);
  if (!rows.length) return placeholder(slide, box, spec, unit);
  const cols = num(spec.columns, rows.length > 4 && box.w > 8 ? 2 : 1);
  const per = Math.ceil(rows.length / cols);
  const colW = (box.w - G * (cols - 1)) / cols;
  const roomy = per <= 4 && box.w > 8;                       // few rows on a wide box: larger badges and type, centered vertically
  const rowH = Math.min(roomy ? 1.3 : 1.05, box.h / per);
  const d = Math.min(roomy ? 0.75 : 0.55, rowH - 0.3);
  const top = box.y + (box.h - per * rowH) / 2;
  rows.forEach(([icon, label, detail], k) => {
    const c = Math.floor(k / per), r = k % per;
    const x = box.x + c * (colW + G), y = top + r * rowH;
    badge(slide, x, y + (rowH - d) / 2 - 0.05, d, K.main, { n: k + 1, icon: icon || undefined, pt: 13 });
    const tx = x + d + 0.25, tw = colW - d - 0.25;
    text(slide, label, { x: tx, y, w: tw, h: rowH * 0.45 }, { size: roomy ? 18 : 15, min: 12, bold: true, valign: "bottom" });
    text(slide, detail || "", { x: tx, y: y + rowH * 0.48, w: tw, h: rowH * 0.5 }, { size: roomy ? 14 : 13, min: 12, color: K.muted });
  });
};

visuals.none = () => {};

function placeholder(slide, box, spec, unit) {
  card(slide, box);
  const prose = (spec && spec.text) || (unit && unit.visual) || "";
  text(slide, "Visual to supply", { x: box.x + 0.3, y: box.y + 0.3, w: box.w - 0.6, h: 0.4 }, { size: 13, min: 12, bold: true, color: K.muted });
  text(slide, prose, { x: box.x + 0.3, y: box.y + 0.8, w: box.w - 0.6, h: box.h - 1.1 }, { size: 14, min: 12, italic: true, color: K.muted });
}
function drawVisual(slide, box, unit) {
  const spec = parseVisual(unit.visual || "");
  const fn = spec.kind && visuals[spec.kind];
  if (!fn) return placeholder(slide, box, spec, unit);
  fn(slide, box, spec, unit);
}

// ---------------------------------------------------------------- patterns
const layouts = {};

layouts.title = (unit) => {
  const s = bareSlide(DARK_ENDS);
  const spec = parseVisual(unit.visual || "");
  const tb = grid(1, 8);
  text(s, unit.title, { x: tb.x, y: 1.5, w: tb.w, h: 2.5 }, { font: FONT.display, size: SCALE.deck_title || 40, min: 28, step: 4, bold: true, color: K.ink, valign: "bottom" });
  if (unit.body[0]) text(s, unit.body[0], { x: tb.x, y: 4.2, w: tb.w, h: 1.0 }, { size: SCALE.slide_subtitle, min: 14, color: K.muted });
  const when = new Date().toLocaleDateString("en-US", { month: "long", year: "numeric" });
  text(s, when, { x: M, y: FOOTER_Y - 0.4, w: 6, h: 0.35 }, { size: 12, min: 12, color: K.muted, valign: "bottom" });
  hero(s, spec.icon);
  if (unit.notes) s.addNotes(unit.notes);
};

layouts.agenda = (unit) => {
  const s = newSlide(unit);
  const spec = parseVisual(unit.visual || "");
  const lb = grid(1, 7);
  const rowH = Math.min(0.9, BODY_H / Math.max(unit.body.length, 1));
  const icons = items(spec.icons);
  unit.body.forEach((item, k) => {
    const y = BODY_Y + k * rowH;
    numberBadge(s, k + 1, lb.x, y + 0.05, 0.45, K.support, 14, icons[k]);
    text(s, item, { x: lb.x + 0.7, y, w: lb.w - 0.7, h: rowH - 0.1 }, { size: 18, min: 14, valign: "middle" });
  });
  const rb = grid(9, 4);
  card(s, { x: rb.x, y: BODY_Y, w: rb.w, h: 2.0 });
  text(s, "What we need from you today", { x: rb.x + 0.3, y: BODY_Y + 0.25, w: rb.w - 0.6, h: 0.4 }, { size: 13, min: 12, bold: true, color: K.muted });
  text(s, spec.ask || spec.text || "", { x: rb.x + 0.3, y: BODY_Y + 0.7, w: rb.w - 0.6, h: 1.1 }, { size: 15, min: 12 });
};

layouts["section-divider"] = (unit) => {
  const s = bareSlide(DARK_ENDS);
  const spec = parseVisual(unit.visual || "");
  numberBadge(s, unit.n, M, M, 1.4, K.support, 48, spec.icon);
  text(s, unit.title, { x: M, y: 2.6, w: grid(1, 8).w, h: 2.0 }, { font: FONT.display, size: 36, min: 24, step: 4, bold: true, color: K.ink, valign: "bottom" });
  if (unit.body[0]) text(s, unit.body[0], { x: M, y: 4.8, w: grid(1, 8).w, h: 1.0 }, { size: SCALE.slide_subtitle, min: 14, color: K.muted });
  if (spec.icon) hero(s, spec.icon, { size: 2.6, y: 2.4 });
  if (unit.notes) s.addNotes(unit.notes);
};

layouts.statement = (unit) => {
  // One claim at display size with a supporting line and a hero icon: a pivot in the argument.
  const s = bareSlide(DARK_ENDS);
  const spec = parseVisual(unit.visual || "");
  numberBadge(s, unit.n, M, TITLE_Y + 0.12, MARKER.size_in, K.support, 16);
  const tb = grid(1, 8);
  text(s, unit.title, { x: tb.x, y: 1.5, w: tb.w, h: 2.5 }, { font: FONT.display, size: 44, min: 28, step: 4, bold: true, color: K.ink, valign: "bottom" });
  if (unit.body[0]) text(s, unit.body[0], { x: tb.x, y: 4.2, w: tb.w, h: 1.2 }, { size: SCALE.slide_subtitle, min: 14, color: K.muted });
  if (unit.body[1]) text(s, unit.body[1], { x: tb.x, y: 5.5, w: tb.w, h: 0.6 }, { size: 13, min: 12, color: K.muted, valign: "bottom" });
  hero(s, spec.icon);
  footer(s, unit);
};

layouts["claim-evidence"] = (unit) => {
  // bullets on one side, the visual on the other; `side: left` puts the visual left, `split: narrow|wide` gives the bullets 4 or 6 columns
  const spec = parseVisual(unit.visual || "");
  const bcols = { narrow: 4, wide: 6 }[spec.split] || num(spec.split, 5);
  const lb = spec.side === "left" ? grid(13 - bcols, bcols) : grid(1, bcols);
  const rb = spec.side === "left" ? grid(1, 12 - bcols) : grid(bcols + 1, 12 - bcols);
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

// Full-width figure beneath the title; the Visual line's kind decides what is drawn
// (process-flow, layer-stack, cycle, hub, icon-list, timeline), the body supplies the details.
layouts.diagram = (unit) => {
  const s = newSlide(unit);
  drawVisual(s, { x: M, y: BODY_Y, w: W - 2 * M, h: BODY_H }, unit);
};
layouts.timeline = layouts.diagram;
layouts["process-flow"] = layouts.diagram;

layouts.quote = (unit) => {
  const s = newSlide(unit);
  const [quote = "", attribution = "", claim = ""] = unit.body;
  const qb = grid(2, 10);
  s.addText("“", { x: M, y: BODY_Y - 0.2, w: 1.0, h: 1.2, fontFace: FONT.display, fontSize: 96, bold: true, color: K.spark, isTextBox: true, margin: 0 });
  text(s, quote, { x: qb.x, y: BODY_Y + 0.3, w: qb.w, h: 2.4 }, { font: FONT.display, size: 24, min: 18, step: 2, color: K.ink });
  text(s, attribution, { x: qb.x, y: BODY_Y + 2.9, w: qb.w, h: 0.5 }, { size: 14, min: 12, color: K.muted });
  if (claim) text(s, claim, { x: M, y: BODY_BOTTOM - 0.6, w: W - 2 * M, h: 0.6 }, { size: 15, min: 12, bold: true, color: K.support, valign: "bottom" });
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
    numberBadge(s, k + 1, mb.x, y + 0.05, 0.4, K.support, 13);
    text(s, name, { x: mb.x + 0.6, y, w: mb.w - 0.6, h: 0.45 }, { size: 14, min: 12, bold: true });
    text(s, mits[k] || "", { x: mb.x + 0.6, y: y + 0.45, w: mb.w - 0.6, h: rowH - 0.55 }, { size: 13, min: 12, color: K.muted });
  });
};

layouts["ask-next-steps"] = (unit) => {
  const s = newSlide(unit, { dark: DARK_ENDS });
  const spec = parseVisual(unit.visual || "");
  const icons = items(spec.icons);
  const steps = unit.body.slice(0, -1), consequence = unit.body[unit.body.length - 1] || "";
  const bandH = 0.85;
  rect(s, { x: M, y: BODY_Y, w: W - 2 * M, h: bandH }, K.support);
  text(s, spec.ask || unit.title, { x: M + 0.3, y: BODY_Y, w: W - 2 * M - 0.6, h: bandH }, { size: 18, min: 14, bold: true, color: K.white, valign: "middle" });
  const stepB = grid(1, 8), ownerB = grid(9, 2), dateB = grid(11, 2);
  const headY = BODY_Y + bandH + 0.3;
  [["Step", stepB], ["Owner", ownerB], ["Date", dateB]].forEach(([h, b]) =>
    text(s, h, { x: b.x + (h === "Step" ? 0.7 : 0), y: headY, w: b.w - (h === "Step" ? 0.7 : 0), h: 0.3 }, { size: 12, min: 12, bold: true, color: K.muted }));
  const rowsTop = headY + 0.4, rowsH = BODY_BOTTOM - 0.7 - rowsTop;
  const rowH = Math.min(0.9, rowsH / Math.max(steps.length, 1));
  const owners = items(spec.owners), dates = items(spec.dates);
  steps.forEach((t, k) => {
    const y = rowsTop + k * rowH;
    numberBadge(s, k + 1, stepB.x, y + 0.1, 0.45, K.support, 14, icons[k]);
    text(s, t, { x: stepB.x + 0.7, y, w: stepB.w - 0.7, h: rowH - 0.1 }, { size: 15, min: 12, color: K.ink, valign: "middle" });
    [[ownerB, owners[k]], [dateB, dates[k]]].forEach(([b, val]) => {
      if (val) text(s, val, { x: b.x, y, w: b.w, h: rowH - 0.1 }, { size: 14, min: 12, color: K.ink, valign: "middle" });
      else line(s, b.x, y + rowH - 0.25, b.w, 0, K.muted, { width: 0.75 });
    });
  });
  if (consequence) text(s, consequence, { x: M, y: BODY_BOTTOM - 0.5, w: W - 2 * M, h: 0.5 }, { size: 13, min: 12, color: K.muted, valign: "bottom" });
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
  console.log(`wrote ${outPath} (${slideCount} slides from ${deck.units.length} units; look ${lookId}: ${FONT.display}/${FONT.body}, ${SURF})`);
});
