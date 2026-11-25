// Build the printable PDF of the complete study guide.
//
//   node scripts/build_study_guide.cjs
//
// Reads  docs/exam-preparation/complete-study-guide.md
// Writes output/pdf/complete-study-guide.pdf
//
// Needs pandoc (2.19 or later, for --embed-resources) and Playwright for Node with its
// Chromium. Equations are rendered as MathML with the FreeSerif font (GNU FreeFont), which has
// an OpenType MATH table; install fonts-freefont-ttf if it is missing. The figures are read
// from figures/ through the guide's relative links. Nothing is fetched from the network.

const { execFileSync } = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');
const { chromium } = require('playwright');

const ROOT = path.resolve(__dirname, '..');
const SRC = path.join(ROOT, 'docs/exam-preparation/complete-study-guide.md');
const OUT = path.join(ROOT, 'output/pdf/complete-study-guide.pdf');

const CSS = `
@page { size: A4; margin: 16mm 15mm 18mm 15mm; }
html { font-size: 10.2pt; }
body { font-family: "Liberation Serif", "DejaVu Serif", serif; line-height: 1.38; color: #1b1b1b;
       max-width: none; margin: 0; padding: 0; background: #fff; }
h1, h2, h3, h4 { font-family: "Inter", "Liberation Sans", sans-serif; color: #12325a; line-height: 1.2;
                 break-after: avoid; page-break-after: avoid; }
h1 { font-size: 19pt; margin: 0 0 6pt; border-bottom: 2px solid #12325a; padding-bottom: 4pt; }
h1:not(:first-of-type) { break-before: page; page-break-before: always; }
h2 { font-size: 13.5pt; margin: 14pt 0 5pt; border-bottom: 1px solid #c9d3e0; padding-bottom: 2pt; }
h3 { font-size: 11.2pt; margin: 10pt 0 4pt; }
p { margin: 4pt 0 6pt; }
ul, ol { margin: 3pt 0 6pt; padding-left: 18pt; }
li { margin: 1.5pt 0; }
table { border-collapse: collapse; margin: 6pt 0 9pt; font-family: "Liberation Sans", "Inter", sans-serif;
        font-size: 8.6pt; width: 100%; break-inside: auto; }
tr { break-inside: avoid; page-break-inside: avoid; }
th, td { border: 1px solid #c3ccd8; padding: 2.6pt 4.5pt; vertical-align: top; }
th { background: #e8eef6; font-weight: 600; }
tbody tr:nth-child(even) td { background: #f7f9fc; }
code { font-family: "JetBrains Mono", "DejaVu Sans Mono", monospace; font-size: 8.6pt;
       background: #f2f4f7; padding: 0 2pt; border-radius: 2px; }
pre { background: #f2f4f7; padding: 6pt 8pt; border-radius: 3px; overflow-x: auto; break-inside: avoid; }
pre code { background: none; padding: 0; }
blockquote { margin: 8pt 0; padding: 5pt 10pt; border-left: 4px solid #2f6db5; background: #eef4fb;
             break-inside: avoid; page-break-inside: avoid; }
blockquote p { margin: 3pt 0; }
figure { margin: 8pt 0 10pt; text-align: center; break-inside: avoid; page-break-inside: avoid; }
figure img, p > img { max-width: 100%; max-height: 112mm; }
figcaption { font-family: "Liberation Sans", sans-serif; font-size: 8.4pt; color: #444; margin-top: 3pt;
             text-align: left; }
math { font-family: "FreeSerif", "DejaVu Serif", serif; font-size: 1.08em; }
math[display="block"] { margin: 6pt 0; overflow-x: auto; }
hr { border: none; border-top: 1px solid #c9d3e0; margin: 10pt 0; }
a { color: #1d4f91; text-decoration: none; }
header#title-block-header { display: none; }
`;

function main() {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'study-guide-'));
  const css = path.join(tmp, 'guide.css');
  const html = path.join(tmp, 'complete-study-guide.html');
  fs.writeFileSync(css, CSS);
  execFileSync('pandoc', [
    SRC, '--from', 'markdown', '--to', 'html5', '--standalone', '--mathml', '--embed-resources',
    '--css', css, '--resource-path', path.dirname(SRC),
    '--metadata', 'title=JC-PINN and the AM wing-rib bracket: complete study guide',
    '--metadata', 'lang=en-GB', '--output', html,
  ], { stdio: 'inherit' });
  return (async () => {
    const browser = await chromium.launch();
    const page = await browser.newPage();
    await page.goto('file://' + html, { waitUntil: 'load' });
    await page.evaluate(() => document.fonts.ready);
    fs.mkdirSync(path.dirname(OUT), { recursive: true });
    await page.pdf({
      path: OUT, format: 'A4', printBackground: true, preferCSSPageSize: true,
      displayHeaderFooter: true,
      headerTemplate: '<div></div>',
      footerTemplate: '<div style="width:100%;font-family:Liberation Sans,sans-serif;font-size:7.5pt;color:#666;'
        + 'padding:0 15mm;display:flex;justify-content:space-between;">'
        + '<span>Team 8 · JC-PINN complete study guide</span>'
        + '<span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>',
    });
    await browser.close();
    fs.rmSync(tmp, { recursive: true, force: true });
    console.log('wrote', path.relative(ROOT, OUT));
  })();
}

main().catch((err) => { console.error(err); process.exit(1); });
