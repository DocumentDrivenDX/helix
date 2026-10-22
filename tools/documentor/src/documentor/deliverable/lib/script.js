// lib/script.js: the deliverable script (Markdown) parser and the Visual spec grammar
// (workflows/deliverables/visual-specs.md). Pure functions; check-deliverable.py parses the same shape
// and tests/validate-render-lib.sh asserts the two agree on the catalog example.
"use strict";
const { parseYaml } = require("./yaml");
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
    if (field === "body") {
      // a wrapped bullet continues the previous bullet; check-deliverable.py joins the same way
      if (/^[-*•]\s+/.test(line.trim()) || !unit.body.length) unit.body.push(line.trim().replace(/^[-*•]\s+/, ""));
      else unit.body[unit.body.length - 1] += " " + line.trim();
    } else unit[field] += " " + line.trim();
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
  // a field that leaked into the prose means the spec was cut at a period inside a value ("Sept. 2026", "e.g. x")
  if (/\s\|\s|^\s*[a-z;|\d]/.test(prose) && /(?:^|\s\|\s)[\w-]+:\s/.test(prose)) spec.truncated = true;
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

module.exports = { parseScript, parseVisual, items, cells, num, splitLabel };
