#!/usr/bin/env node
// render-doc.js — render a HELIX deliverable script (kind: brief or one-pager) to a themed HTML
// document, and to PDF when a headless Chrome/Chromium is available.
//
// Usage: render-doc.js <script.md> <out.html> [--theme theme.yml] [--patterns slide-patterns.yml]
//        [--look <id>] [--kind brief|one-pager] [--pdf <out.pdf>] [--chrome <path>]
//
// Reads the same deliverable Markdown script render-deck.js reads (frontmatter, ## Content units
// with **Pattern**/**Body**/**Visual**/**Notes**/**Sources**, the ## Sources table) and lays it out
// as a flowing document instead of slides: one section per unit, in order, using the same Visual
// spec grammar (workflows/deliverables/visual-specs.md) rendered as HTML/SVG instead of pptx shapes.
// `brief` flows normally across as many printed pages as the content needs; `one-pager` packs the
// same units into a dense two-column single page and warns past the theme's word budget. The theme
// (workflows/deliverables/theme.yml) supplies the palette, the type scale (`typography.scale.doc_*`),
// the page geometry (`layout.document`), and the look (font pairing, dominant hue) exactly as
// render-deck.js uses it, so a deck and a document from the same project read as one system. No
// native dependency: the HTML is self-contained (icons inlined as SVG, `currentColor`-tinted, no
// rasterizer needed). PDF export shells out to a local Chrome/Chromium in headless print-to-pdf mode
// when one is found; without one, the HTML is still written and the script says so.
"use strict";
const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");
const { parseYaml } = require("./lib/yaml");
const { parseScript, parseVisual, items, cells, num, splitLabel } = require("./lib/script");

// ---------------------------------------------------------------- arguments
const argv = process.argv.slice(2);
const positional = [];
const flags = {};
for (let i = 0; i < argv.length; i++) {
  if (argv[i].startsWith("--")) flags[argv[i].slice(2)] = argv[++i];
  else positional.push(argv[i]);
}
if (positional.length < 2) {
  console.error("usage: render-doc.js <script.md> <out.html> [--theme theme.yml] [--patterns slide-patterns.yml] [--look <id>] [--kind brief|one-pager] [--pdf <out.pdf>] [--chrome <path>] [--byline <text>]");
  process.exit(2);
}
const [scriptPath, outPath] = positional;
const repoRoot = path.resolve(__dirname, "..", "..", "..");
function firstExisting(cands) { for (const c of cands) if (fs.existsSync(c)) return c; return cands[0]; }
const themePath = flags.theme || firstExisting([
  path.join(repoRoot, "workflows", "deliverables", "theme.yml"),
  path.join(__dirname, "..", "references", "deliverables", "theme.yml"),
]);
const patternsPath = flags.patterns || firstExisting([
  path.join(repoRoot, "workflows", "deliverables", "slide-patterns.yml"),
  path.join(__dirname, "..", "references", "deliverables", "slide-patterns.yml"),
]);
for (const [what, file] of [["theme", themePath], ["patterns", patternsPath]]) {
  if (!fs.existsSync(file)) { console.error(`render-doc.js: no ${what} file at ${file}`); process.exit(2); }
}
const theme = parseYaml(fs.readFileSync(themePath, "utf8"));
const patterns = parseYaml(fs.readFileSync(patternsPath, "utf8"));
const doc = parseScript(fs.readFileSync(scriptPath, "utf8"));

const problems = [];   // dishonest-render defects; reported, exit 1 after writing
const warnings = [];   // worth fixing, reported, exit unchanged

// ---------------------------------------------------------------- kind, look, theme resolution
const KIND = flags.kind || doc.brief.Kind || "brief";
if (KIND !== "brief" && KIND !== "one-pager") { console.error(`render-doc.js: kind must be 'brief' or 'one-pager', got '${KIND}'`); process.exit(2); }

const LOOKS = theme.looks || {};
let lookId = flags.look || doc.brief.Look || LOOKS.default || "editorial";
if (typeof LOOKS[lookId] === "string") lookId = LOOKS[lookId];
if (!LOOKS[lookId] || typeof LOOKS[lookId] !== "object") {
  console.error(`render-doc.js: no look '${lookId}' in ${themePath}; looks: ${Object.keys(LOOKS).filter((k) => typeof LOOKS[k] === "object").join(", ")}`);
  process.exit(2);
}
const look = LOOKS[lookId];
const P = theme.palette;
const DOMINANT = look.dominant || "primary";
const hexOf = (c) => String(c).trim();
const order = [DOMINANT, ...["primary", "secondary", "accent"].filter((h) => h !== DOMINANT)];
const K = {
  main: hexOf(P[order[0]]), support: hexOf(P[order[1]]), spark: hexOf(P[order[2]]),
  ink: hexOf(P.ink), muted: hexOf(P.muted), surface: hexOf(P.surface), alt: hexOf(P.surface_alt), border: hexOf(P.border),
  positive: hexOf(P.semantic.positive), negative: hexOf(P.semantic.negative), warning: hexOf(P.semantic.warning), neutral: hexOf(P.semantic.neutral),
};
const FONT = {
  display: [(look.display && look.display.family) || theme.typography.display.family, ...(theme.typography.display.fallback || [])].join(", "),
  body: [(look.body && look.body.family) || theme.typography.body.family, ...(theme.typography.body.fallback || [])].join(", "),
};
const MARKER_SHAPE = look.marker || (theme.motif.section_marker && theme.motif.section_marker.shape) || "circle";
// classic's own marker is bare numerals, no shape — extend that restraint to cards too: rules and
// whitespace instead of rounded boxes with a colored accent rail (the generic "AI-generated
// design" card chrome), so the page reads as a printed report rather than a web dashboard.
const AUSTERE = MARKER_SHAPE === "none";
const SCALE = theme.typography.scale;
const DOC = theme.layout.document || { page: "Letter", margin_in: 1.0, max_words_one_pager: 450 };
const COMPACT = KIND === "one-pager";
const BODY_PT = (SCALE.doc_body || 11) - (COMPACT ? 2.2 : 0);
const HEAD_PT = (SCALE.doc_heading || 14) - (COMPACT ? 2.5 : 0);
const CAP_PT = (SCALE.doc_caption || 9) - (COMPACT ? 0.8 : 0);

// ---------------------------------------------------------------- helpers
function esc(s) {
  return String(s == null ? "" : s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
function inline(s) {
  // the only inline markup a script body carries: **bold**
  return esc(s).replace(/\*\*(.+?)\*\*/g, "<b>$1</b>");
}
function citeIds(sourcesField) {
  return (String(sourcesField || "").match(/S\d+/g) || []).map((s) => s.slice(1));
}
function citeSup(sourcesField) {
  const ids = citeIds(sourcesField);
  if (!ids.length) return "";
  return `<p class="src-line">Sources <sup class="cite">${ids.map((n) => `<a href="#src-${n}">${n}</a>`).join(", ")}</sup></p>`;
}
let wordCount = 0;
function countWords(s) { wordCount += String(s || "").split(/\s+/).filter(Boolean).length; }

// icons inlined as raw SVG (currentColor picks up the wrapping element's CSS `color`); no rasterizer needed
const ICON_DIR = path.join(__dirname, "icons");
const iconCache = new Map();
function iconSvg(name) {
  name = String(name || "").trim();
  if (!name) return "";
  if (iconCache.has(name)) return iconCache.get(name);
  if (!/^[a-z0-9-]+$/.test(name)) { console.error(`render-doc.js: icon name '${name}' is not a plain name`); iconCache.set(name, ""); return ""; }
  const file = path.join(ICON_DIR, name + ".svg");
  if (!fs.existsSync(file)) { console.error(`render-doc.js: no icon '${name}' in ${ICON_DIR}`); iconCache.set(name, ""); return ""; }
  const svg = fs.readFileSync(file, "utf8");
  iconCache.set(name, svg);
  return svg;
}
function badge(o = {}) {
  // a filled circle/square holding an icon (white glyph) or a number, shaped by the look's marker;
  // `bare` (or the look's own `marker: none`) draws the glyph alone in the hue, no fill
  const fill = o.fill || K.main;
  const inner = o.icon ? `<span class="glyph">${iconSvg(o.icon)}</span>` : `<span class="glyph num">${esc(o.n != null ? o.n : "")}</span>`;
  if (o.bare || MARKER_SHAPE === "none") return `<span class="badge bare" style="color:${fill}">${inner}</span>`;
  const shapeCls = MARKER_SHAPE === "square" ? " badge-square" : "";
  return `<span class="badge${shapeCls}" style="background:${fill}">${inner}</span>`;
}

// status words a table's last column gets pill-styled for, generically (not specific to any one artifact type)
const STATUS = {
  met: "positive", fit: "positive", published: "positive", high: "positive", pass: "positive",
  unmet: "negative", "no fit": "negative", fail: "negative",
  unknown: "warning", undetermined: "warning", conditional: "warning", "conditional fit": "warning", medium: "warning", "not published": "neutral",
  low: "neutral", "third-party estimate": "neutral",
};
function statusPill(text) {
  const key = String(text || "").trim().toLowerCase();
  if (key === "—" || key === "-" || !key) return null;   // a placeholder dash prints plain, no pill
  const sem = STATUS[key];
  if (!sem) return null;
  return `<span class="pill pill-${sem}">${esc(text)}</span>`;
}

// ---------------------------------------------------------------- visual renderers (HTML per Visual-spec kind)
function vTable(spec, unit) {
  const columns = spec.columns ? cells(spec.columns) : [];   // no invented header; the gate wants columns named
  let rows = items(spec.rows).map(cells);
  if (!rows.length) rows = unit.body.map(splitLabel).filter((r) => r[1]);
  const hl = num(spec.highlight, 0);
  const lastCol = columns.length - 1;
  const head = columns.map((c) => `<th>${esc(c)}</th>`).join("");
  const body = rows.map((r, ri) => {
    const cellsHtml = r.map((c, ci) => {
      const pill = ci === lastCol && /status|fit|verdict|confidence|grade|label|result/i.test(columns[lastCol] || "") ? statusPill(c) : null;   // a colored pill only where the column says it is a status
      return `<td>${pill || inline(c)}</td>`;
    }).join("");
    return `<tr${ri + 1 === hl ? ' class="hl"' : ""}>${cellsHtml}</tr>`;
  }).join("");
  return `<table class="doc-table"><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table>`;
}
function vTwoColumn(spec, unit) {
  const left = spec.left || "", right = spec.right || "";   // no invented labels
  let rows = items(spec.rows).map(cells);
  if (!rows.length) {
    const l = [], r = [];
    for (const b of unit.body) { const [label, detail] = splitLabel(b); if (label.toLowerCase() === left.toLowerCase()) l.push(detail); else if (label.toLowerCase() === right.toLowerCase()) r.push(detail); }
    const n = Math.max(l.length, r.length);
    rows = Array.from({ length: n }, (_, k) => [l[k] || "", r[k] || ""]);
  }
  const prefer = spec.prefer === "left" ? 0 : spec.prefer === "right" ? 1 : -1;   // no lead column unless the author says so
  const verdict = spec.verdict || (unit.body.find((b) => /^verdict:/i.test(b)) || "").replace(/^verdict:\s*/i, "");
  const col = (head, side) => `
    <div class="tc-col${side === prefer ? " tc-lead" : ""}">
      <h4>${esc(head)}</h4>
      <ul>${rows.map((r) => `<li${side === prefer ? ' class="tc-check"' : ""}>${inline(r[side] || "")}</li>`).join("")}</ul>
    </div>`;
  return `<div class="two-col">${col(left, 0)}${col(right, 1)}</div>${verdict ? `<p class="tc-verdict">${inline(verdict)}</p>` : ""}`;
}
function vStat(spec, unit) {
  let statsArr = items(spec.stats).map(cells).slice(0, 3);
  if (!statsArr.length) statsArr = unit.body.slice(0, 3).map((b) => { const m = b.match(/^([<>]?\s?\$?\d[\d,.]*\s?[%kKMBx+]*|[<>]\s?\d+)\s*(.*)$/); return m ? [m[1].trim(), m[2]] : [b, ""]; });
  const hl = num(spec.highlight, 0);
  const cards = statsArr.map(([value, caption], k) => `
    <div class="stat-card">
      <div class="stat-value" style="color:${k + 1 === hl ? K.support : K.main}">${esc(value)}</div>
      <div class="stat-caption">${inline(caption)}</div>
      ${spec.label ? `<div class="stat-label">${esc(spec.label)}</div>` : ""}
    </div>`).join("");
  return `<div class="stat-row">${cards}</div>`;
}
// a ring gauge, drawn in place of a panel's badge when its own name reads as a grade
// ("High confidence"): no new visual-spec kind needed, the content already carries the grade
const GRADE_PCT = { high: 0.86, medium: 0.55, low: 0.24 };
function dialSvg(pct, hue, d) {
  const r = d / 2 - 3, c = 2 * Math.PI * r, cx = d / 2, cy = d / 2;
  return `<svg viewBox="0 0 ${d} ${d}" width="${d}" height="${d}" class="dial">
    <circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="var(--border)" stroke-width="3"/>
    <circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="${hue}" stroke-width="3" stroke-linecap="round"
      stroke-dasharray="${c * pct} ${c}" transform="rotate(-90 ${cx} ${cy})"/>
  </svg>`;
}
function vPanels(spec, unit, o = {}) {
  const list = items(spec.items).map(cells).slice(0, 4);
  if (!list.length) return "";
  const icons = items(spec.icons);
  const hl = num(spec.highlight, 0);
  const cls = o.hero ? "panel-row hero" : "panel-row";
  return `<div class="${cls}">${list.map(([name, detail], k) => {
    const grade = String(name).match(/^(high|medium|low)\b/i);
    const hue = k + 1 === hl ? K.support : K.main;
    const mark = grade ? `<span class="panel-grade">${esc(grade[1])}</span>`   // the grade word, never a gauge: a percentage nobody stated
      : badge({ n: k + 1, icon: icons[k], fill: hue });
    return `
    <div class="panel${k + 1 === hl ? " panel-hl" : ""}">
      ${mark}
      <div class="panel-name">${inline(name)}</div>
      ${detail ? `<div class="panel-detail">${inline(detail)}</div>` : ""}
    </div>`;
  }).join("")}</div>`;
}
function vIconList(spec, unit) {
  let rows = items(spec.items).map(cells).slice(0, 8);
  if (!rows.length) rows = unit.body.map(splitLabel).map(([l, d]) => ["", l, d]);
  if (!rows.length) return "";
  const cols = num(spec.columns, rows.length > 4 ? 2 : 1);
  return `<div class="icon-list" style="columns:${cols}">${rows.map(([icon, label, detail], k) => `
    <div class="icon-row">
      ${badge({ n: k + 1, icon })}
      <div><div class="icon-label">${inline(label)}</div>${detail ? `<div class="icon-detail">${inline(detail)}</div>` : ""}</div>
    </div>`).join("")}</div>`;
}
function vRiskGrid(spec, unit) {
  const risks = items(spec.risks).map(cells).slice(0, 6);
  if (!risks.length) return "";
  const level = (s) => ({ low: 0, medium: 1, med: 1, high: 2 }[String(s || "").toLowerCase()] ?? 1);
  const W = 460, H = 190, axisW = 60, padTop = 14, padBottom = 34;
  const gw = W - axisW - 20, gh = H - padTop - padBottom;
  const cw = gw / 3, ch = gh / 3, gx = axisW, gy = padTop;
  // rows are impact (High at the top, r=0) and columns are likelihood (Low at the left, c=0), matching
  // the axis labels below; a cell is "hot" when high impact and high likelihood compound (c - r >= 1)
  let cells_ = "";
  for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++) {
    const hot = c - r >= 1;
    cells_ += `<rect x="${gx + c * cw}" y="${gy + r * ch}" width="${cw}" height="${ch}" fill="${hot ? "var(--hot)" : "var(--surface-alt)"}" stroke="var(--border)"/>`;
  }
  const placed = risks.map(([, lik, imp]) => ({ row: 2 - level(imp), col: level(lik) }));
  const perCell = {}, seen = {};
  placed.forEach((p) => { perCell[p.row + ":" + p.col] = (perCell[p.row + ":" + p.col] || 0) + 1; });
  let dots = "";
  placed.forEach((p, k) => {
    const key = p.row + ":" + p.col, count = perCell[key], slot = seen[key] = (seen[key] || 0) + 1;
    const d = 20, pitch = d + 6;
    const cx = gx + p.col * cw + cw / 2 + (slot - (count + 1) / 2) * pitch, cy = gy + p.row * ch + ch / 2;
    dots += `<circle cx="${cx}" cy="${cy}" r="${d / 2}" fill="var(--accent-${k === 0 ? "main" : "support"})"/><text x="${cx}" y="${cy + 4}" text-anchor="middle" class="dot-n">${k + 1}</text>`;
  });
  const rowLabels = ["High", "Med", "Low"].map((l, r) => `<text x="${gx - 10}" y="${gy + r * ch + ch / 2 + 4}" text-anchor="end" class="axis-l">${l}</text>`).join("");
  const colLabels = ["Low", "Medium", "High"].map((l, c) => `<text x="${gx + c * cw + cw / 2}" y="${gy + gh + 18}" text-anchor="middle" class="axis-l">${l}</text>`).join("");
  const svg = `<svg viewBox="0 0 ${W} ${H}" class="risk-grid" role="img" aria-label="Risk grid plotting likelihood against impact">
    ${cells_}
    <line x1="${gx}" y1="${gy}" x2="${gx}" y2="${gy + gh}" stroke="var(--border)"/>
    <line x1="${gx}" y1="${gy + gh}" x2="${gx + gw}" y2="${gy + gh}" stroke="var(--border)"/>
    ${rowLabels}${colLabels}${dots}
    <text x="${gx - 44}" y="${gy + gh / 2}" text-anchor="middle" class="axis-t" transform="rotate(-90 ${gx - 44} ${gy + gh / 2})">IMPACT</text>
    <text x="${gx + gw / 2}" y="${H - 4}" text-anchor="middle" class="axis-t">LIKELIHOOD</text>
  </svg>`;
  let mits = items(spec.mitigations);
  if (!mits.length) mits = unit.body.map((b) => splitLabel(b)[1] || b);
  const legend = risks.map(([name], k) => `<b>${k + 1}</b> ${inline(name)}`).join(" &middot; ");
  return `<figure class="figure">${svg}<figcaption>${legend}</figcaption></figure>
    <ol class="finding-list">${risks.map(([name], k) => `<li>${badge({ n: k + 1, fill: K.support })}<div>${inline(name)}${mits[k] ? `. ${inline(mits[k])}` : ""}</div></li>`).join("")}</ol>`;
}
function vPlaceholder(spec, unit) {
  const prose = (spec && spec.text) || unit.visual || "";
  return `<div class="placeholder"><b>Visual to supply</b><br>${inline(prose)}</div>`;
}
const VISUALS = { table: vTable, "two-column": vTwoColumn, stat: vStat, panels: vPanels, "icon-list": vIconList, "risk-grid": vRiskGrid, none: () => "" };
function renderVisual(unit) {
  const spec = parseVisual(unit.visual || "");
  if (spec.truncated) problems.push(`unit ${unit.n}: the Visual spec was cut at a period inside a field value`);
  if (spec.kind === "none") return "";   // an authored "no figure": the body carries the unit
  const fn = spec.kind && VISUALS[spec.kind];
  // a Visual caption is authoring guidance for the gate and is not drawn, so it does not count toward the page budget
  if (!fn) {
    warnings.push(`unit ${unit.n}: visual kind '${spec.kind || "(none given)"}' has no document layout; nothing was drawn (the body carries the unit)`);
    return "";
  }
  return fn(spec, unit) || "";
}

// ---------------------------------------------------------------- section renderers (per Pattern)
function heading(n, unit) {
  return `<h2 id="u${unit.n}"><span class="hnum">${n}.</span>${inline(unit.title)}</h2>`;
}
function bullets(list) {
  list.forEach(countWords);
  return `<ul class="doc-list">${list.map((b) => `<li>${inline(b)}</li>`).join("")}</ul>`;
}
const SECTIONS = {};
SECTIONS["claim-evidence"] = (unit, n) => `<section class="sec">${heading(n, unit)}${bullets(unit.body)}${renderVisual(unit)}${citeSup(unit.sources)}</section>`;
SECTIONS.table = (unit, n) => {
  const spec = parseVisual(unit.visual || "");
  countWords(unit.body.join(" "));
  return `<section class="sec">${heading(n, unit)}${unit.body.length ? bullets(unit.body) : ""}${vTable(spec, unit)}${citeSup(unit.sources)}</section>`;
};
SECTIONS["two-column-comparison"] = (unit, n) => {
  const spec = parseVisual(unit.visual || "");
  return `<section class="sec">${heading(n, unit)}${unit.body.length ? bullets(unit.body) : ""}${vTwoColumn(spec, unit)}${citeSup(unit.sources)}</section>`;
};
SECTIONS["stat-callout"] = (unit, n) => {
  const spec = parseVisual(unit.visual || "");
  return `<section class="sec">${heading(n, unit)}${vStat(spec, unit)}${unit.body.length ? bullets(unit.body) : ""}${citeSup(unit.sources)}</section>`;
};
SECTIONS["risk-matrix"] = (unit, n) => {
  const spec = parseVisual(unit.visual || "");
  return `<section class="sec">${heading(n, unit)}${unit.body.length ? bullets(unit.body) : ""}${vRiskGrid(spec, unit)}${citeSup(unit.sources)}</section>`;
};
SECTIONS["ask-next-steps"] = (unit, n) => {
  const spec = parseVisual(unit.visual || "");
  const icons = items(spec.icons), owners = items(spec.owners), dates = items(spec.dates);
  // Every body bullet is a step. A closing line renders only when the Visual spec names one
  // (`consequence: ...`); the human-facing voice ends the ask on its last step, with no slogan tail.
  const steps = unit.body, consequence = spec.consequence || "";
  const askText = spec.ask || unit.title;
  if (!spec.ask) warnings.push(`unit ${unit.n}: the ask has no 'ask:' field, so it repeats the title`);
  steps.forEach(countWords); countWords(consequence);
  const rows = steps.map((s, k) => `<li>${badge({ n: k + 1, icon: icons[k], fill: K.support })}<div class="step-text">${inline(s)}${owners[k] || dates[k] ? `<span class="step-meta">${esc([owners[k], dates[k]].filter(Boolean).join(" · "))}</span>` : ""}</div></li>`).join("");
  return `<section class="sec sec-ask">${heading(n, unit)}<div class="ask-band">${inline(askText)}</div><ol class="finding-list">${rows}</ol>${consequence ? `<p class="ask-consequence">${inline(consequence)}</p>` : ""}</section>`;
};
SECTIONS["appendix-sources"] = (unit, n) => {
  if (!doc.sources.length) return "";
  const rows = doc.sources.map(([id, claim, where]) => `<li id="src-${id.slice(1)}"><span class="src-n">${id.slice(1)}.</span><span>${inline(claim)} <span class="src-where">&middot; ${inline(where)}</span></span></li>`).join("");
  return `<section class="sec sec-sources"><h2>${inline(unit ? unit.title : "Sources")}</h2><ol class="src-list">${rows}</ol></section>`;
};
function renderUnit(unit, n) {
  if (unit.pattern === "title") return "";  // feeds the masthead, not a section
  const fn = SECTIONS[unit.pattern];
  if (!fn) {
    console.error(`render-doc.js: unit ${unit.n} uses pattern '${unit.pattern}' with no document layout; rendering as claim-evidence`);
    return SECTIONS["claim-evidence"](unit, n);
  }
  return fn(unit, n);
}

// ---------------------------------------------------------------- masthead + assembly
const titleUnit = doc.units.find((u) => u.pattern === "title");
const titleBody = (titleUnit && titleUnit.body) || [];
// The title unit's body is the introduction: real authored prose (one sentence per bullet in the
// script, joined into a paragraph here), not a mechanical dump of the Brief's own planning fields
// (Audience, Decision or action sought) — those exist to steer authoring, not to be read verbatim.
// One bullet alone still renders as a short dek line for scripts that have not been given a full
// introduction yet.
const introParas = titleBody.length > 1 ? [titleBody.join(" ")] : [];
const dek = titleBody.length === 1 ? titleBody[0] : "";
// The masthead carries only what the author wrote: the title, the introduction, and an "As of" date when
// the Brief has one (a reference without a date cannot be trusted later). No kind label, no byline.
const asOf = doc.brief["As of"] || doc.brief["Date"] || "";
const kicker = asOf ? `As of ${asOf}` : "";
// No "Prepared for" byline: the Brief's Audience field steers authoring and is not reader-facing prose.
// A byline, when a document wants one, is written into the script (`--byline` or the Brief's `Byline`).
const metaBits = [];
const byline = flags.byline || doc.brief.Byline;
if (byline) metaBits.push(`<span>${esc(byline)}</span>`);
const iconName = (parseVisual((titleUnit && titleUnit.visual) || "").icon) || "document";

const rawContentUnits = doc.units.filter((u) => u.pattern !== "title" && u.pattern !== "appendix-sources");
const appendixUnit = doc.units.find((u) => u.pattern === "appendix-sources");

// The first unit becomes a glanceable hero band under the masthead — not a numbered section —
// when it's a claim-evidence unit whose visual is panels (a verdict/confidence/gap-shaped
// summary): the reader should see the finding before any numbered argument.
let heroUnit = null, contentUnits = rawContentUnits;
const firstUnit = rawContentUnits[0];
if (firstUnit && firstUnit.pattern === "claim-evidence" && parseVisual(firstUnit.visual || "").kind === "panels") {
  heroUnit = firstUnit;
  contentUnits = rawContentUnits.slice(1);
}
countWords(doc.title); countWords(dek); introParas.forEach(countWords);
const heroHtml = heroUnit ? (() => {
  const spec = parseVisual(heroUnit.visual || "");
  return `<div class="hero-band"><p class="hero-kicker">${inline(heroUnit.title)}</p>${vPanels(spec, heroUnit, { hero: true })}${citeSup(heroUnit.sources)}</div>`;
})() : "";
const sectionsHtml = contentUnits.map((u, k) => renderUnit(u, k + 1)).join("\n");
const appendixHtml = appendixUnit ? SECTIONS["appendix-sources"](appendixUnit, contentUnits.length + 1) : "";

// one-pager: a deterministic two-column grid of facts with the ask spanning full width at the
// bottom, never CSS multicol (which balances by available height, not by page — it will not
// reliably hold to one printed page). Every other pattern splits left/right in reading order.
function unitWeight(u) {
  // a rough proxy for rendered height: row/item count dominates over bullet count
  const spec = parseVisual(u.visual || "");
  const rowsN = items(spec.rows).length || items(spec.risks).length || items(spec.items).length;
  if (rowsN) return 2 + rowsN * 1.3;
  return 2 + u.body.length * 0.9;
}
// A pattern whose own visual is already two-part or wide (a comparison, a plotted grid, the ask)
// wastes a half-width column and renders full-width instead, in reading order; only single-column
// "fact" shapes (table, claim-evidence, stat, panels, icon-list) pack into the balanced grid.
const FULL_WIDTH_PATTERNS = new Set(["two-column-comparison", "risk-matrix", "ask-next-steps"]);
let onepagerHtml = "";
if (KIND === "one-pager") {
  const gridUnits = contentUnits.filter((u) => !FULL_WIDTH_PATTERNS.has(u.pattern));
  const fullUnits = contentUnits.filter((u) => FULL_WIDTH_PATTERNS.has(u.pattern));
  // greedy load-balance by weight so a short section doesn't strand a tall column's neighbor with
  // empty space beside it, but walk gridUnits in document order (not sorted by weight) so a lighter
  // unit numbered ahead of a heavier one still lands in the reading-order-first column when weights
  // are close or tied — a reader scans left-column-then-right-column, and "2" above "1" reads as broken
  const col1 = [], col2 = [];
  let w1 = 0, w2 = 0;
  for (const u of gridUnits) {
    const n = contentUnits.indexOf(u) + 1;
    if (w1 <= w2) { col1.push([n, u]); w1 += unitWeight(u); } else { col2.push([n, u]); w2 += unitWeight(u); }
  }
  const order = (col) => col.sort((a, b) => a[0] - b[0]).map(([n, u]) => renderUnit(u, n));
  const fullHtml = fullUnits.map((u) => renderUnit(u, contentUnits.indexOf(u) + 1)).join("\n");
  const gridHtml = gridUnits.length ? `<div class="op-grid"><div class="op-col">${order(col1).join("\n")}</div><div class="op-col">${order(col2).join("\n")}</div></div>` : "";
  onepagerHtml = gridHtml + fullHtml;
}

// The human-facing voice bans em dashes on the page; the script gate catches them in the script, this
// catches the ones a renderer or a Visual spec joiner would add.
{
  const visible = [doc.title, dek, ...introParas, ...doc.units.flatMap((u) => [...(u.body || []), u.visual || ""])].join("\n");
  const dashes = visible.match(/\u2014|\u2013|\s--\s/g);
  if (dashes) warnings.push(`${dashes.length} em dash(es) in rendered text; the human-facing voice uses a period, comma, or colon instead`);
}
if (KIND === "one-pager" && wordCount > (DOC.max_words_one_pager || 450)) {
  warnings.push(`one-pager: ${wordCount} words exceeds the theme's max_words_one_pager (${DOC.max_words_one_pager || 450}); trim body bullets or route detail to a brief instead`);
}

const css = `
  @page { size: ${DOC.page || "Letter"}; margin: ${COMPACT ? Math.max(0.45, (DOC.margin_in || 1.0) - 0.55) : (DOC.margin_in || 1.0)}in; }
  :root{
    --ink:${K.ink}; --muted:${K.muted}; --surface:${K.surface}; --surface-alt:${K.alt}; --border:${K.border};
    --accent-main:${K.main}; --accent-support:${K.support}; --accent-spark:${K.spark};
    --positive:${K.positive}; --negative:${K.negative}; --warning:${K.warning}; --neutral:${K.neutral};
    --hot:#F6E4DF;
    --font-display: ${FONT.display}; --font-body: ${FONT.body};
  }
  *{box-sizing:border-box;}
  body{ margin:0; font-family:var(--font-body); color:var(--ink); font-size:${BODY_PT}pt; line-height:${COMPACT ? 1.4 : 1.55}; background:var(--surface); }
  .page{ max-width:${KIND === "one-pager" ? "980px" : "740px"}; margin:0 auto; padding:${KIND === "one-pager" ? "16px 22px" : "34px 6px"}; }
  a{ color:var(--accent-main); }
  sup.cite{ font-size:0.72em; } sup.cite a{ text-decoration:none; color:var(--accent-main); }

  header.masthead{ display:flex; align-items:flex-start; gap:18px; padding-bottom:${COMPACT ? 10 : 18}px; border-bottom:3px solid var(--accent-main); margin-bottom:${COMPACT ? 14 : 24}px; }
  header.masthead .mark{ flex:0 0 auto; width:44px; height:44px; border-radius:${AUSTERE ? 0 : 9}px; background:var(--surface-alt); display:flex; align-items:center; justify-content:center; color:var(--accent-main); }
  header.masthead .mark svg{ width:24px; height:24px; }
  .kicker{ font-family:var(--font-body); font-size:8.8pt; letter-spacing:.13em; text-transform:uppercase; color:var(--accent-support); font-weight:700; margin:0 0 5px; }
  h1.doc-title{ font-family:var(--font-display); font-size:${SCALE.doc_title || 24}pt; line-height:1.18; margin:0 0 8px; font-weight:${theme.typography.display.weight || 700}; text-wrap:balance; }
  .dek{ font-family:var(--font-body); font-size:${BODY_PT + 0.7}pt; color:var(--muted); margin:0 0 ${COMPACT ? 5 : 10}px; }
  p.intro{ font-family:var(--font-body); font-size:${BODY_PT + 0.4}pt; color:var(--ink); margin:${COMPACT ? "10px" : "16px"} 0 ${COMPACT ? 10 : 20}px; line-height:1.6; }
  .meta-row{ font-family:var(--font-body); font-size:8.6pt; color:var(--muted); display:flex; gap:16px; flex-wrap:wrap; }
  .meta-row b{ color:var(--ink); font-weight:600; }

  h2{ font-family:var(--font-display); font-size:${HEAD_PT}pt; color:var(--ink); margin:${COMPACT ? "8px" : "26px"} 0 6px; padding-bottom:4px; border-bottom:1.5px solid var(--border); font-weight:700; break-after:avoid; text-wrap:balance; }
  .hnum{ color:var(--accent-main); margin-right:7px; }
  p{ margin:0 0 9px; }
  .src-line{ font-size:8pt; color:var(--muted); margin:2px 0 4px; }
  .src-line sup.cite{ font-size:1em; }

  ul.doc-list{ margin:0 0 ${COMPACT ? 5 : 10}px; padding-left:18px; }
  ul.doc-list li{ margin-bottom:${COMPACT ? 1 : 4}px; }

  table.doc-table{ width:100%; border-collapse:collapse; margin:${COMPACT ? "2px 0 6px" : "4px 0 12px"}; font-family:var(--font-body); font-size:${CAP_PT + 0.3}pt; }
  table.doc-table th{ text-align:left; background:var(--surface-alt); color:var(--muted); font-weight:700; padding:${COMPACT ? "3px 6px" : "6px 9px"}; border-bottom:2px solid var(--border); font-size:${CAP_PT}pt; text-transform:uppercase; letter-spacing:.03em; }
  table.doc-table td{ padding:${COMPACT ? "3px 6px" : "7px 9px"}; border-bottom:1px solid var(--border); vertical-align:top; }
  table.doc-table tr.hl td{ background:var(--surface-alt); }
  table.doc-table tr{ break-inside:avoid; }

  .pill{ display:inline-block; font-family:var(--font-body); font-size:7.8pt; font-weight:700; padding:2px 7px; border-radius:99px; white-space:nowrap; }
  .pill-positive{ background:color-mix(in srgb, var(--positive) 16%, white); color:var(--positive); }
  .pill-negative{ background:color-mix(in srgb, var(--negative) 16%, white); color:var(--negative); }
  .pill-warning{ background:color-mix(in srgb, var(--warning) 16%, white); color:var(--warning); }
  .pill-neutral{ background:var(--surface-alt); color:var(--muted); }

  .badge{ display:inline-flex; align-items:center; justify-content:center; width:22px; height:22px; border-radius:50%; color:#fff; flex:0 0 auto; }
  .badge-square{ border-radius:5px; }
  .badge .glyph{ width:12px; height:12px; display:flex; }
  .badge .glyph svg{ width:100%; height:100%; stroke:currentColor; }
  .badge .glyph.num{ font-family:var(--font-display); font-size:10pt; font-weight:700; }
  .badge.bare{ background:none !important; width:auto; height:auto; }
  .badge.bare .glyph{ width:16px; height:16px; }
  .badge.bare .glyph.num{ font-size:${BODY_PT + 2}pt; }

  .two-col{ display:flex; gap:0; margin:${COMPACT ? "6px 0 2px" : "12px 0 4px"}; break-inside:avoid; ${AUSTERE ? "border-top:1px solid var(--border);" : ""} }
  .tc-col{ flex:1 1 0; padding:${COMPACT ? "8px 10px" : "13px 14px"}; ${AUSTERE ? "" : "border:1px solid var(--border); border-radius:6px;"} }
  ${AUSTERE ? ".tc-col + .tc-col{ border-left:1px solid var(--border); }" : ""}
  .tc-col.tc-lead{ ${AUSTERE ? "" : "border-color:var(--accent-main); box-shadow: inset 3px 0 0 var(--accent-main);"} }
  .tc-col h4{ margin:0 0 8px; font-family:var(--font-display); font-size:${BODY_PT+1}pt; }
  .tc-col ul{ margin:0; padding-left:0; list-style:none; font-size:${BODY_PT}pt; color:var(--muted); }
  .tc-col li{ margin-bottom:6px; padding-left:16px; position:relative; }
  .tc-col li.tc-check::before{ content:"\\2713"; position:absolute; left:0; color:var(--accent-main); font-weight:700; }
  .tc-col li:not(.tc-check)::before{ content:"\\2013"; position:absolute; left:0; color:var(--muted); }
  .tc-verdict{ font-style:italic; color:var(--muted); font-size:${BODY_PT-0.6}pt; margin:2px 0 ${COMPACT ? 4 : 14}px; }

  .stat-row{ display:flex; gap:${AUSTERE ? 0 : 14}px; margin:10px 0 14px; break-inside:avoid; ${AUSTERE ? "border-top:1px solid var(--border); border-bottom:1px solid var(--border);" : ""} }
  .stat-card{ flex:1 1 0; padding:12px 14px; ${AUSTERE ? "" : "border:1px solid var(--border); border-radius:6px;"} }
  ${AUSTERE ? ".stat-card + .stat-card{ border-left:1px solid var(--border); }" : ""}
  .stat-value{ font-family:var(--font-display); font-size:20pt; font-weight:700; line-height:1.1; }
  .stat-caption{ font-size:${BODY_PT-1}pt; color:var(--muted); margin-top:3px; }
  .stat-label{ font-size:7.6pt; text-transform:uppercase; letter-spacing:.08em; color:var(--muted); margin-top:5px; font-weight:700; }

  .panel-row{ display:flex; gap:${AUSTERE ? 0 : 12}px; margin:10px 0 14px; break-inside:avoid; ${AUSTERE ? "border-top:1px solid var(--border); border-bottom:1px solid var(--border);" : ""} }
  .panel{ flex:1 1 0; padding:${AUSTERE ? "14px 16px" : "12px"}; text-align:${AUSTERE ? "left" : "center"}; ${AUSTERE ? "" : "border:1px solid var(--border); border-radius:6px;"} }
  ${AUSTERE ? ".panel + .panel{ border-left:1px solid var(--border); }" : ""}
  .panel-hl{ ${AUSTERE ? "" : "border-color:var(--accent-support);"} }
  .panel .badge{ margin-bottom:7px; width:26px; height:26px; }
  .panel .glyph{ width:14px; height:14px; }
  .panel-name{ font-weight:700; font-size:${BODY_PT}pt; }
  .panel-detail{ font-size:${BODY_PT-1.3}pt; color:var(--muted); margin-top:4px; }
  .panel-dial{ display:inline-flex; margin-bottom:7px; }
  .panel-grade{ display:inline-block; font-family:var(--font-display); font-weight:700; font-size:1.15em; color:var(--accent-main); margin-bottom:6px; }
  .dial{ display:block; }

  .hero-band{
    ${AUSTERE
      ? `border-top:2px solid var(--ink); border-bottom:1px solid var(--border); background:none;`
      : `border:1px solid var(--border); border-top:4px solid var(--accent-main); border-radius:8px; background:var(--surface-alt);`}
    padding:${COMPACT ? "12px 0 14px" : "18px 0 20px"}; margin:0 0 ${COMPACT ? 14 : 26}px; break-inside:avoid;
  }
  .hero-kicker{
    font-family:var(--font-display); font-weight:${theme.typography.display.weight || 700}; color:var(--ink);
    font-size:${COMPACT ? HEAD_PT + 1 : HEAD_PT + 4}pt; margin:0 0 ${COMPACT ? 8 : 14}px; text-wrap:balance;
  }
  .hero-band .panel-row{ margin:0; ${AUSTERE ? "border:none;" : ""} }
  .hero-band .panel{ text-align:left; padding:${COMPACT ? "10px 12px" : "14px 16px"}; ${AUSTERE ? "" : "background:var(--surface);"} }
  .hero-band .panel-row.hero .panel-dial{ margin-bottom:9px; }
  .hero-band .panel-row.hero .panel-name{ font-size:${COMPACT ? BODY_PT + 1 : BODY_PT + 2.5}pt; }
  .hero-band .panel-row.hero .panel-detail{ font-size:${COMPACT ? BODY_PT - 1 : BODY_PT}pt; }
  .hero-band .src-line{ margin:${COMPACT ? 8 : 12}px 0 0; }

  .icon-list{ margin:10px 0 14px; column-gap:20px; }
  .icon-row{ display:flex; gap:10px; margin-bottom:10px; break-inside:avoid; }
  .icon-label{ font-weight:700; font-size:${BODY_PT}pt; }
  .icon-detail{ font-size:${BODY_PT-1}pt; color:var(--muted); }

  figure.figure{ margin:12px 0 8px; break-inside:avoid; }
  svg.risk-grid{ width:100%; max-width:460px; height:auto; }
  svg.risk-grid rect{ }
  svg.risk-grid text.axis-l{ font-family:var(--font-body); font-size:8px; fill:var(--muted); }
  svg.risk-grid text.axis-t{ font-family:var(--font-body); font-size:8px; fill:var(--muted); font-weight:700; }
  svg.risk-grid text.dot-n{ font-family:var(--font-body); font-size:9px; fill:#fff; font-weight:700; }
  svg.risk-grid .accent-main{ fill:var(--accent-main); } svg.risk-grid .accent-support{ fill:var(--accent-support); }
  figure.figure figcaption{ font-size:8pt; color:var(--muted); margin-top:6px; }

  .finding-list{ list-style:none; margin:10px 0 14px; padding:0; }
  .finding-list li{ display:flex; gap:10px; align-items:flex-start; padding:${COMPACT ? 3 : 7}px 0; border-bottom:1px solid var(--border); font-size:${BODY_PT}pt; }
  .finding-list li:last-child{ border-bottom:none; }
  .finding-list b{ color:var(--ink); }

  .sec-ask .ask-band{ background:var(--accent-support); color:#fff; font-weight:700; font-family:var(--font-display); padding:${COMPACT ? '7px 12px' : '10px 14px'}; border-radius:${AUSTERE ? 0 : 5}px; margin:${COMPACT ? '4px 0 6px' : '8px 0 12px'}; font-size:${BODY_PT+1}pt; }
  .ask-consequence{ color:var(--muted); font-style:italic; font-size:${BODY_PT-0.7}pt; margin-top:${COMPACT ? 3 : 8}px; }
  .step-text{ flex:1; } .step-meta{ display:block; font-size:8pt; color:var(--muted); margin-top:2px; }

  .sec-sources{ margin-top:${KIND === "one-pager" ? "12px" : "16px"}; }
  ol.src-list{ list-style:none; margin:0; padding:0; font-size:8.6pt; line-height:1.3; color:var(--muted); columns:2; column-gap:24px; }
  ol.src-list li{ display:flex; gap:6px; margin-bottom:3px; break-inside:avoid; }
  .src-n{ color:var(--accent-main); font-weight:700; flex:0 0 auto; }
  .src-where{ color:var(--muted); }

  .placeholder{ border:1px dashed var(--border); border-radius:${AUSTERE ? 0 : 6}px; padding:10px 12px; color:var(--muted); font-size:${BODY_PT-1}pt; margin:8px 0 14px; }

  ${KIND === "one-pager" ? `
  .op-grid{ display:grid; grid-template-columns:1fr 1fr; gap:0 26px; align-items:start; }
  .op-col .sec:first-child h2{ margin-top:0; }
  .sec-ask{ margin-top:${COMPACT ? 6 : 14}px; }
  header.masthead{ break-inside:avoid; }
  ` : ""}
`;

const html = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>${esc(doc.title)}</title>
<style>${css}</style>
</head>
<body>
<div class="page">
  <header class="masthead">
    <div class="mark">${iconSvg(iconName)}</div>
    <div>
      <p class="kicker">${esc(kicker)}</p>
      <h1 class="doc-title">${inline(doc.title)}</h1>
      ${dek ? `<p class="dek">${inline(dek)}</p>` : ""}
      <div class="meta-row">${metaBits.join("")}</div>
    </div>
  </header>
  ${introParas.map((p) => `<p class="intro">${inline(p)}</p>`).join("\n")}
  ${heroHtml}
  ${KIND === "one-pager" ? onepagerHtml : sectionsHtml}
  ${appendixHtml}
</div>
</body>
</html>
`;

fs.writeFileSync(outPath, html, "utf8");
console.log(`wrote ${outPath} (${KIND}, ${contentUnits.length} sections, look ${lookId}: ${FONT.display.split(",")[0]}/${FONT.body.split(",")[0]}, ~${wordCount} words)`);

// ---------------------------------------------------------------- optional PDF export
if (flags.pdf) {
  const candidates = [flags.chrome,
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "google-chrome", "chromium", "chromium-browser"].filter(Boolean);
  let chrome = null;
  for (const c of candidates) {
    try { execFileSync(c.includes("/") ? c : "which", c.includes("/") ? ["--version"] : [c], { stdio: "ignore" }); chrome = c; break; }
    catch (e) { if (c.includes("/") && fs.existsSync(c)) { chrome = c; break; } }
  }
  if (!chrome) {
    warnings.push(`--pdf requested but no Chrome/Chromium found (tried: ${candidates.join(", ")}); the HTML was written, export it yourself`);
  } else {
    try {
      execFileSync(chrome, ["--headless", "--disable-gpu", "--no-pdf-header-footer",
        `--print-to-pdf=${path.resolve(flags.pdf)}`, "file://" + path.resolve(outPath)], { stdio: "ignore" });
      console.log(`wrote ${flags.pdf}`);
    } catch (e) {
      warnings.push(`PDF export failed: ${e.message}`);
    }
  }
}

for (const m of warnings) console.error(`render-doc.js: warning: ${m}`);
if (problems.length) {
  for (const m of problems) console.error(`render-doc.js: ${m}`);
  console.error(`render-doc.js: ${problems.length} problem(s); the file was written but the render is not clean`);
  process.exitCode = 1;
}
