// Screenshot built pages at real viewports: `documentor site --shots` (report.py).
//
//   node shots.mjs <out-dir> <page.html>...      writes <out-dir>/<name>.<view>.png for each page
//
// Needs playwright-core (installed into the documentor cache with Eraser; ERASER_MODULES) and a
// Chromium (CHROMIUM_PATH). Headless Chrome's window has a floor of 500px, so a phone-width shot
// needs an emulated viewport, which is why this is not a plain `chrome --screenshot`.
import {resolve, basename, dirname, relative} from 'node:path';
import {pathToFileURL} from 'node:url';

const [out, base, ...pages] = process.argv.slice(2);
const modules = process.env.ERASER_MODULES || resolve(process.cwd(), 'node_modules');
const {chromium} = await import(pathToFileURL(resolve(modules, 'playwright-core/index.mjs')));
const VIEWS = [
  ['desktop', {width: 1280, height: 900}, 'light', false],
  ['dark', {width: 1280, height: 900}, 'dark', false],
  ['phone', {width: 390, height: 844}, 'light', true],
];
const browser = await chromium.launch({executablePath: process.env.CHROMIUM_PATH});
try {
  for (const page of pages) {
    const name = relative(base, dirname(page)).replaceAll('/', '-') || 'home';
    for (const [view, viewport, colorScheme, isMobile] of VIEWS) {
      const context = await browser.newContext({viewport, colorScheme, isMobile, deviceScaleFactor: isMobile ? 2 : 1});
      const tab = await context.newPage();
      await tab.goto(pathToFileURL(page).href, {waitUntil: 'load'});
      await tab.waitForTimeout(400);
      const overflow = await tab.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
      await tab.screenshot({path: resolve(out, `${name}.${view}.png`)});
      if (overflow > 1) console.log(`overflow ${name} ${view}: ${overflow}px wider than the screen`);
      await context.close();
    }
  }
} finally {
  await browser.close();
}
