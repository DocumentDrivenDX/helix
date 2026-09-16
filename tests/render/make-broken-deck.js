// Writes a two-slide .pptx with known defects so tests/validate-deck-render.sh can prove deck-qa.py catches them:
// slide 1 has two overlapping text boxes (text-collision); slide 2 has a table that runs past the bottom margin.
"use strict";
const pptxgen = require("pptxgenjs");
const out = process.argv[2];
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
const s1 = pres.addSlide();
s1.addText("First text box on the slide", { x: 1, y: 1, w: 5, h: 1, fontSize: 18, isTextBox: true });
s1.addText("Second text box overlapping it", { x: 2, y: 1.3, w: 5, h: 1, fontSize: 18, isTextBox: true });
const s2 = pres.addSlide();
const rows = [["Head", "Value"]];
for (let k = 0; k < 14; k++) rows.push([`Row ${k + 1}`, "a value that is long enough to take a full line of the cell"]);
s2.addTable(rows.map((r) => r.map((c) => ({ text: c, options: { fontSize: 14 } }))), { x: 0.6, y: 2.0, w: 12, colW: [3, 9], rowH: 0.5 });
pres.writeFile({ fileName: out }).then(() => console.log(`wrote ${out}`));
