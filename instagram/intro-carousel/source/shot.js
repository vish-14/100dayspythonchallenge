const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1350 } });
  await p.goto('file://' + process.argv[2], { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  console.log('fonts', await p.evaluate(() => ['900 40px Montserrat','600 40px Inter','500 20px "JetBrains Mono"'].map(f => document.fonts.check(f))));
  for (let i = 1; i <= 5; i++) await (await p.$('#s' + i)).screenshot({ path: `${process.argv[3]}/vish-intro-${i}.png` });
  await b.close();
})();
