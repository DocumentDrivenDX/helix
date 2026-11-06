// Render a presentation that `documentor tour` prepared: Eraser measures every box and
// routes every connector; stage.mjs plays it on one screen, the camera gliding to each step
// of the walkthrough, without redrawing anything (the diagram review's example 6).
//
//   node render.mjs <dir>        reads eraser.json, walkthrough.json, theme.json; writes present.html
//
// Needs @eraserlabs/diagrams (ERASER_MODULES, default ./node_modules) and a Chromium (CHROMIUM_PATH).
import {readFile, writeFile} from 'node:fs/promises';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
import {page} from './stage.mjs';

const dir = resolve(process.argv[2] || '.');
const modules = process.env.ERASER_MODULES || resolve(process.cwd(), 'node_modules');
const {createRenderer, eraserFonts} = await import(pathToFileURL(resolve(modules, '@eraserlabs/diagrams/dist/index.js')));
const read = async name => JSON.parse(await readFile(resolve(dir, name), 'utf8'));
const [diagram, walk, theme] = await Promise.all([read('eraser.json'), read('walkthrough.json'), read('theme.json')]);

// Eraser grows a box to fit its text, so a route from the layout can start inside a box that grew.
// The first pass measures; this moves each route's ends onto the measured edges for the second.
function snapped(diagram, measured) {
  const box = Object.fromEntries(measured.map(e => [e.id, e]));
  const edge = (b, port, p) => ({top: {...p, y: b.y}, bottom: {...p, y: b.y + b.height},
    left: {...p, x: b.x}, right: {...p, x: b.x + b.width}})[port] || p;
  const connections = diagram.connections.map(c => {
    if (!c.points || !box[c.from] || !box[c.to]) return c;
    const points = c.points.map(p => ({...p}));
    const [a, b] = [points[0], points.at(-1)];
    points[0] = edge(box[c.from], c.fromPort, a);
    points[points.length - 1] = edge(box[c.to], c.toPort, b);
    return {...c, points};
  });
  return {...diagram, connections};
}

const fonts = eraserFonts();
fonts.faces = fonts.faces.map(f => ({...f, inline: true}));
const renderer = await createRenderer({chromiumPath: process.env.CHROMIUM_PATH, fonts, deviceScaleFactor: 2});
try {
  const first = await renderer.render({...diagram, outputs: {json: true}});
  if (!first.ok) throw Error(JSON.stringify(first.errors));
  const result = await renderer.render({...snapped(diagram, first.json.entities), outputs: {html: true, json: true}});
  if (!result.ok) throw Error(JSON.stringify(result.errors));
  await writeFile(resolve(dir, 'measured.json'), JSON.stringify({scene: result.json.scene, warnings: result.warnings}, null, 1));
  const html = page(result.html, result.json.scene, walk, theme);
  await writeFile(resolve(dir, 'present.html'), html);
  console.log(`rendered ${resolve(dir, 'present.html')} (${result.warnings.length} warnings)`);
  for (const w of result.warnings) console.log('  warning:', JSON.stringify(w));
} finally {
  await renderer.close();
}
