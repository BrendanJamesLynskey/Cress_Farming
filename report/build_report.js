// Build Cress_Farming.pdf from the presentation (index.html) and report_template.html.
//
//   python3 diagrams/make_diagrams.py
//   NODE_PATH=/path/to/node_modules node report/build_report.js
//
// Every slide except those marked .deck-only (the topics list and the interactive
// simulator) becomes a numbered chapter, so the deck and the report never drift apart.
const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

const root = path.resolve(__dirname, '..');
// Chapters that start a new part of the report get a page break and a part heading.
const PARTS = { 'slide-01': 'Part 1 · The idea', 'slide-03': 'Part 2 · The design', 'slide-09': 'Part 3 · Getting ready',
                'slide-12': 'Part 4 · Building it', 'slide-19': 'Part 5 · Fixing and upgrading',
                'slide-26': 'Part 6 · Safety and summary', 'slide-30': 'Part 7 · Converting a Korody RC combine' };

(async () => {
  const browser = await puppeteer.launch({ headless: 'new', args: ['--no-sandbox'] });
  const page = await browser.newPage();
  await page.setRequestInterception(true);
  page.on('request', r => (/^(file|data):/.test(r.url()) ? r.continue() : r.abort()));

  await page.goto('file://' + path.join(root, 'index.html'), { waitUntil: 'domcontentloaded' });
  const slides = await page.evaluate(() =>
    [...document.querySelectorAll('section.slide:not(.deck-only)')].map(s => {
      const c = s.cloneNode(true);
      c.querySelectorAll('.slide-number, script, .deck-only').forEach(e => e.remove());
      // links to the simulator slide make no sense on paper
      c.querySelectorAll('a[href="#slide-08"]').forEach(a => a.replaceWith(document.createTextNode(a.textContent)));
      return { id: s.id, title: c.querySelector('h2').textContent.trim(), html: c.innerHTML };
    }));

  // Report images live one directory down from the deck.
  const fix = html => html.replace(/src="diagrams\//g, 'src="../diagrams/');
  let n = 0;
  const toc = [], body = [];
  for (const s of slides) {
    n += 1;
    toc.push(`        <li><span class="n">${n}</span>${s.title.replace(/&/g, '&amp;')}</li>`);
    if (PARTS[s.id]) body.push(`<div class="part-title">${PARTS[s.id]}</div>`);
    body.push(`<section class="chapter" id="${s.id}">` +
      fix(s.html).replace('<h2>', `<h2><span class="num">${n}</span>`) + '</section>');
  }

  const date = new Date().toLocaleDateString('en-GB', { month: 'long', year: 'numeric' });
  const html = fs.readFileSync(path.join(__dirname, 'report_template.html'), 'utf8')
    .replace('<!--TOC-->', toc.join('\n'))
    .replace('<!--BODY-->', body.join('\n'))
    .replace('<!--DATE-->', date);
  const built = path.join(__dirname, '_report_built.html');
  fs.writeFileSync(built, html);

  await page.goto('file://' + built, { waitUntil: 'load' });
  await page.pdf({
    path: path.join(root, 'Cress_Farming.pdf'),
    format: 'A4',
    printBackground: true,
    preferCSSPageSize: true,
    displayHeaderFooter: true,
    headerTemplate: '<div></div>',
    footerTemplate: '<div style="width:100%;font-family:DejaVu Sans,sans-serif;font-size:7.5px;color:#5A6673;' +
      'padding:0 16mm;display:flex;justify-content:space-between"><span>Cress Farming</span>' +
      '<span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>',
  });
  fs.unlinkSync(built);
  await browser.close();
  console.log(`Cress_Farming.pdf: ${slides.length} chapters`);
})();
