// validate_paste.js — Verify that generated HTML actually pastes cleanly into
// the live wangEditor OMS editor (no flatten-to-<br>).
//
// Requires Playwright (Chromium). Run with NODE_PATH pointing at a playwright install, e.g.
//   npx --yes playwright@1.61 install chromium      # once
//   PWPATH=$(find "$(npm config get cache)/_npx" -maxdepth 3 -name playwright -type d -path '*node_modules*' | head -1)
//   NODE_PATH=$(dirname "$PWPATH") node validate_paste.js <editorUrl> <file1.html> [file2.html ...]
//
// A headed Chromium opens; LOG IN once (session persists in C:/tmp/oms_profile).
// For each file: opens it, Ctrl+A/C, switches to a fresh editor tab, Ctrl+A/Delete/Ctrl+V,
// then reports tag counts. PASS = br<5 AND (h2>0 || strong>0). FAIL = flattened.
const { chromium } = require('playwright');

const EDITOR = process.argv[2];
const FILES = process.argv.slice(3);
const PROFILE = process.env.OMS_PROFILE || 'C:/tmp/oms_profile';
if (!EDITOR || !FILES.length) {
  console.error('usage: node validate_paste.js <editorUrl> <file.html> [...]'); process.exit(2);
}
async function waitEditor(pg) {
  for (let i = 0; i < 60; i++) {
    await pg.waitForTimeout(2000);
    if (await pg.evaluate(() => !!document.querySelector('.w-e-text')).catch(() => false)) return true;
  }
  return false;
}
(async () => {
  const ctx = await chromium.launchPersistentContext(PROFILE, {
    headless: false, viewport: { width: 1400, height: 900 },
    permissions: ['clipboard-read', 'clipboard-write'],
  });
  for (const path of FILES) {
    const ed = await ctx.newPage();
    await ed.goto(EDITOR, { waitUntil: 'domcontentloaded' });
    if (!await waitEditor(ed)) { console.log(path, '-> editor not found (log in?) url=', ed.url()); await ed.close(); continue; }
    await ed.waitForTimeout(1000);
    const src = await ctx.newPage();
    await src.goto('file:///' + encodeURI(path.replace(/\\/g, '/')));
    await src.keyboard.press('Control+A'); await src.keyboard.press('Control+C');
    await src.waitForTimeout(300); await src.close();
    await ed.bringToFront(); await ed.click('.w-e-text');
    await ed.keyboard.press('Control+A'); await ed.keyboard.press('Delete'); await ed.waitForTimeout(200);
    await ed.keyboard.press('Control+V'); await ed.waitForTimeout(1500);
    const r = await ed.evaluate(() => {
      const h = document.querySelector('.w-e-text').innerHTML, c = re => (h.match(re) || []).length;
      return { h1: c(/<h1[ >]/gi), h2: c(/<h2[ >]/gi), h3: c(/<h3[ >]/gi), strong: c(/<strong[ >]/gi), p: c(/<p[ >]/gi), br: c(/<br/gi) };
    });
    const pass = r.br < 5 && (r.h2 > 0 || r.strong > 0);
    console.log((pass ? 'PASS' : 'FAIL') + '  ' + path + '  ' + JSON.stringify(r));
    await ed.close(); // NOTE: paste is not saved; close discards it
  }
  await ctx.close();
})().catch(e => { console.error('ERR', e.message); process.exit(1); });
