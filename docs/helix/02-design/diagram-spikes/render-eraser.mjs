import { readFile, writeFile } from 'node:fs/promises';
import { pathToFileURL } from 'node:url';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
const here=dirname(fileURLToPath(import.meta.url));
const modules=process.env.SPIKE_NODE_MODULES || resolve(here,'node_modules');
const {createRenderer}=await import(pathToFileURL(resolve(modules,'@eraserlabs/diagrams/dist/index.js')));
const renderer=await createRenderer({chromiumPath:process.env.CHROMIUM_PATH,deviceScaleFactor:2});
try {
 const diagram=JSON.parse(await readFile(resolve(here,'02-eraser.json'),'utf8'));
 const output=await renderer.render({...diagram,outputs:{png:true,html:true,json:true}});
 await writeFile(resolve(here,'02-eraser-result.json'),JSON.stringify({ok:output.ok,warnings:output.warnings,errors:output.errors},null,2));
 if(!output.ok)throw new Error(JSON.stringify(output.errors));
 await writeFile(resolve(here,'02-eraser.png'),output.png);
 await writeFile(resolve(here,'02-eraser.html'),output.html);
 await writeFile(resolve(here,'02-eraser-measured.json'),JSON.stringify(output.json,null,2));
 console.log('Eraser rendered PNG, HTML and measured JSON',output.warnings);
} finally {await renderer.close();}
