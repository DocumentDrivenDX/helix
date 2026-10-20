// lib/yaml.js: enough YAML for theme.yml and slide-patterns.yml (block maps and lists, one-line flow
// lists and maps, quoted scalars, comments). Nothing more; PyYAML reads the same files on the Python side.
"use strict";
// Enough YAML for theme.yml and slide-patterns.yml: block maps and lists,
// flow lists/maps on one line, quoted scalars, comments. Nothing more.
function parseYaml(text) {
  const lines = [];
  for (const raw of text.split("\n")) {
    const stripped = stripComment(raw);
    if (stripped.trim() === "") continue;
    lines.push({ indent: stripped.length - stripped.trimStart().length, text: stripped.trim() });
  }
  if (!lines.length) return {};
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
  // a quote opens a string only at the start of a value (after ": ", "- ", "[", "{", ","); an apostrophe
  // inside a word ("the team's plan") is text, so a trailing "# comment" after it is still a comment
  let quote = null;
  for (let k = 0; k < line.length; k++) {
    const ch = line[k];
    if (quote) { if (ch === quote) quote = null; continue; }
    if ((ch === '"' || ch === "'") && /(?:^|[:\-\[{,]\s*)$/.test(line.slice(0, k))) quote = ch;
    else if (ch === "#" && (k === 0 || /\s/.test(line[k - 1]))) return line.slice(0, k);
  }
  return line;
}
function scalar(s) {
  s = s.trim();
  if (/^"[^"]*"$/.test(s) || /^'[^']*'$/.test(s)) return s.slice(1, -1);   // both ends the same quote
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

module.exports = { parseYaml, stripComment, scalar, splitFlow };
