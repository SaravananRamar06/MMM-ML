/* Render project.dot and simple.dot to SVG and PNG. Requires @viz-js/viz and sharp (via NODE_PATH or local modules).
 * Before rendering, it checks that the critical-flaw-length numbers in both charts match report/numbers.json.
 * Run: node docs/project-flowchart/build.cjs */
const fs = require('node:fs');
const path = require('node:path');
const { instance } = require('@viz-js/viz');
const sharp = require('sharp');

const n = JSON.parse(fs.readFileSync(path.join(__dirname, '..', '..', 'report', 'numbers.json'), 'utf8'));
const required = [
  `${n.ClLimitkN} kN`,
  `CL > ${n.ClCrackMax} mm`,
  `${n.ClKmatLow}–${n.ClKmatHigh} MPa√m`,
];

(async () => {
  const viz = await instance();
  for (const name of ['project', 'simple']) {
    const dot = fs.readFileSync(path.join(__dirname, name + '.dot'), 'utf8');
    const missing = required.filter((s) => !dot.includes(s));
    if (missing.length) throw new Error(`${name}.dot does not match report/numbers.json: missing ${JSON.stringify(missing)}`);
    const r = viz.render(dot, { format: 'svg', engine: 'dot' });
    if (r.status !== 'success') throw new Error(JSON.stringify(r.errors));
    fs.writeFileSync(path.join(__dirname, name + '.svg'), r.output);
    await sharp(Buffer.from(r.output), { density: 90 }).png().toFile(path.join(__dirname, name + '.png'));
    console.log(name, 'rendered');
  }
})();
