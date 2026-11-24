#!/usr/bin/env node
// exportar-pdf.js — slides.html -> slides.pdf (1920×1080 por página)
//
//   npm i -D playwright && npx playwright install chromium   (uma vez)
//   node exportar-pdf.js                 # cria slides.pdf ao lado
//   node exportar-pdf.js outro-nome.pdf
//
// Precisa de rede: as fontes vêm do Google Fonts. Sem rede, o PDF sai com
// Arial no lugar da Space Grotesk e fica com ar de relatório de contas.
const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const destino = path.resolve(__dirname, process.argv[2] || 'slides.pdf');
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  await page.goto('file://' + path.join(__dirname, 'slides.html'), { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  await page.emulateMedia({ media: 'print' });
  await page.pdf({ path: destino, preferCSSPageSize: true, printBackground: true });
  const n = await page.evaluate(() => document.querySelectorAll('.slide').length);
  console.log(`PDF criado: ${destino} (${n} slides)`);
  await browser.close();
})();
