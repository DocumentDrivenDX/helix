// lib/measure.js: text measuring and fitting. Average glyph widths per face (an em fraction), a word
// wrapper that flags a word wider than its box (that size does not fit, whatever the height), and a
// fitter that steps a size list down until every paragraph fits.
"use strict";
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

module.exports = { WIDTH_FACTOR, LINE_HEIGHT, textWidthIn, wrap, fitParagraphs, sizesDown };
