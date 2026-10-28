const { chromium } = require('playwright');
(async () => {
  const [src, out] = process.argv.slice(2);
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('file://' + src, { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  const foot = `<div style="width:100%;margin:0 20mm;padding-top:6pt;border-top:0.5pt solid #E2E5EB;display:flex;justify-content:space-between;font-family:Inter,sans-serif;font-size:8pt;color:#7A808C;">
    <span>The 4-Task Workflow · Vish | AI Automation · @vish.workflows</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>`;
  await p.pdf({ path: out, format: 'A4', printBackground: true, displayHeaderFooter: true,
    headerTemplate: '<span></span>', footerTemplate: foot,
    margin: { top: '20mm', bottom: '22mm', left: '20mm', right: '20mm' } });
  await b.close();
})();
