// Print a Vish guide page to an A4 PDF with a consistent footer and page numbers.
// Usage: node render.js /abs/guide.html /abs/out.pdf "Footer title"
const fs = require('fs'), path = require('path');
const { chromium } = require('playwright');
(async () => {
  const [src, out, title = 'Vish | AI Automation · @vish.workflows'] = process.argv.slice(2);
  const font = fs.readFileSync(path.join(__dirname, 'fonts', 'inter-latin-400-normal.woff2')).toString('base64');
  const esc = s => s.replace(/[&<>]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));
  const foot = `<style>@font-face{font-family:InterF;src:url(data:font/woff2;base64,${font}) format("woff2");}</style>
    <div style="width:100%;margin:0 20mm;padding-top:6pt;border-top:0.5pt solid #E2E5EB;display:flex;justify-content:space-between;font-family:InterF,Inter,sans-serif;font-size:8pt;color:#7A808C;">
    <span>${esc(title)}</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>`;
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('file://' + src, { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  await p.pdf({ path: out, format: 'A4', printBackground: true, displayHeaderFooter: true,
    headerTemplate: '<span></span>', footerTemplate: foot,
    margin: { top: '20mm', bottom: '22mm', left: '20mm', right: '20mm' } });
  await b.close();
})();
