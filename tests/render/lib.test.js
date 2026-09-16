// node --test tests/render/lib.test.js
// Unit tests for the renderer's pure libraries: the tiny YAML parser, the script and Visual grammar, and text fitting.
"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const path = require("path");
const lib = path.resolve(__dirname, "../../skills/helix/scripts/lib");
const { parseYaml } = require(path.join(lib, "yaml"));
const { parseScript, parseVisual, items, cells } = require(path.join(lib, "script"));
const { wrap, fitParagraphs, sizesDown } = require(path.join(lib, "measure"));

test("yaml: block maps, lists, flow values, comments, apostrophes", () => {
  const y = parseYaml("a: the team's plan   # comment\nb: \"x\" and 'y'\nc: [1, two]\nd:\n  - e: 1\n    f: 2\n  - plain\n");
  assert.deepEqual(y, { a: "the team's plan", b: "\"x\" and 'y'", c: [1, "two"], d: [{ e: 1, f: 2 }, "plain"] });
});
test("yaml: empty and comment-only files parse to an empty map", () => {
  assert.deepEqual(parseYaml(""), {});
  assert.deepEqual(parseYaml("# nothing\n\n"), {});
});
test("visual: fields, lists, cells, prose", () => {
  const v = parseVisual("kind: two-column | left: A | right: B | rows: a1 / b1; a2 / b2 | prefer: left. Two columns from the source");
  assert.equal(v.kind, "two-column");
  assert.deepEqual(items(v.rows).map(cells), [["a1", "b1"], ["a2", "b2"]]);
  assert.equal(v.text, "Two columns from the source");
  assert.equal(v.truncated, undefined);
});
test("visual: a period inside a value truncates the spec and is flagged", () => {
  const v = parseVisual("kind: process-flow | steps: Draft; Review, e.g. by a partner; Ship | highlight: 3. Three steps");
  assert.equal(v.highlight, undefined);
  assert.equal(v.truncated, true);
});
test("visual: prose-only line has no kind", () => {
  assert.equal(parseVisual("A chart of revenue by quarter").kind, null);
});
test("script: units, wrapped bullets join, brief fields, sources", () => {
  const md = "# T\n\n## Brief\n\n- **Look**: bold\n\n## Content\n\n### 1. First claim here\n\n**Pattern**: claim-evidence\n**Body**:\n- one bullet that\n  wraps onto a second line\n- two\n**Visual**: kind: none. Prose\n**Notes**: n\n**Sources**: S1\n\n## Sources\n\n| Id | Claim | Section |\n|---|---|---|\n| S1 | c | s |\n";
  const d = parseScript(md);
  assert.equal(d.units.length, 1);
  assert.deepEqual(d.units[0].body, ["one bullet that wraps onto a second line", "two"]);
  assert.equal(d.brief.Look, "bold");
  assert.deepEqual(d.sources, [["S1", "c", "s"]]);
});
test("measure: a word wider than the box marks the size unfit whatever the height", () => {
  const box = { w: 1.0, h: 3.0 };
  const fit = fitParagraphs(["Requirements"], box, { font: "Arial", bold: true, sizes: sizesDown(24, 12, 2) });
  assert.ok(fit.pt < 24, "shrank");
  const w = wrap("Requirements", "Arial", 24, true, 1.0);
  assert.equal(w.overwide, true);
});
test("measure: sizes step down to the floor and stop", () => {
  assert.deepEqual(sizesDown(18, 12, 2), [18, 16, 14, 12]);
  assert.deepEqual(sizesDown(15, 12, 2), [15, 13, 12]);
});
test("measure: paragraphs that fit at the first size return it", () => {
  const fit = fitParagraphs(["short"], { w: 5, h: 1 }, { font: "Arial", sizes: [18, 16] });
  assert.equal(fit.pt, 18); assert.equal(fit.fits, true);
});
