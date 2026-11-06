// catalog.js — where the renderers find theme.yml and slide-patterns.yml.
// In order: $DOCUMENTOR_CATALOG/deliverables/, the HELIX checkout above this file
// (workflows/deliverables/), then documentor's packaged copy (catalog/helix/deliverables/).
"use strict";
const fs = require("fs");
const path = require("path");

const deliverable = path.resolve(__dirname, "..");

function catalogFile(name) {
  const cands = [];
  if (process.env.DOCUMENTOR_CATALOG) cands.push(path.join(process.env.DOCUMENTOR_CATALOG, "deliverables", name));
  for (let dir = deliverable; ; dir = path.dirname(dir)) {
    if (fs.existsSync(path.join(dir, "workflows", "deliverables", "theme.yml"))) {
      cands.push(path.join(dir, "workflows", "deliverables", name));
      break;
    }
    if (path.dirname(dir) === dir) break;
  }
  cands.push(path.join(deliverable, "..", "catalog", "helix", "deliverables", name));
  for (const c of cands) if (fs.existsSync(c)) return c;
  return cands[0];
}

module.exports = { catalogFile };
