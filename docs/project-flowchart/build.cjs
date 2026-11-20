/* Render project.dot to SVG and PNG. Requires @viz-js/viz and sharp (via NODE_PATH or local modules).
 * Run: node docs/project-flowchart/build.cjs */
const fs = require('node:fs');
const path = require('node:path');
const { instance } = require('@viz-js/viz');
const sharp = require('sharp');
(async () => {
  const viz = await instance();
  const dot = fs.readFileSync(path.join(__dirname, 'project.dot'), 'utf8');
  const r = viz.render(dot, { format: 'svg', engine: 'dot' });
  if (r.status !== 'success') throw new Error(JSON.stringify(r.errors));
  fs.writeFileSync(path.join(__dirname, 'project.svg'), r.output);
  await sharp(Buffer.from(r.output), { density: 90 }).png().toFile(path.join(__dirname, 'project.png'));
  console.log('rendered', JSON.stringify(r.errors));
})();
