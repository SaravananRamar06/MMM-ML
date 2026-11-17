/* Render editable Graphviz sources. Requires @viz-js/viz and sharp.
 * Resolve them from NODE_PATH (Codex bundled dependencies) or local npm modules.
 * Run from any directory: node docs/ansys-flowchart/build.cjs
 */
const fs = require('node:fs');
const path = require('node:path');
const { instance } = require('@viz-js/viz');
const sharp = require('sharp');

async function main() {
  const directory = __dirname;
  const viz = await instance();
  const pages = [
    ['01-ansys', 'A · ANSYS global solution'],
    ['02-usermat', 'B · USERMAT stress update'],
    ['03-jc-pinn', 'C · JC-PINN flow stress'],
    ['04-return-mapping', 'D · Plastic return mapping'],
  ];
  const rendered = [];
  for (const [name, title] of pages) {
    const dot = fs.readFileSync(path.join(directory, `${name}.dot`), 'utf8');
    const result = viz.render(dot, { format: 'svg', engine: 'dot' });
    if (result.status !== 'success' || result.errors.some(e => e.level === 'error')) {
      throw new Error(`${name}: ${JSON.stringify(result.errors)}`);
    }
    fs.writeFileSync(path.join(directory, `${name}.svg`), result.output);
    await sharp(Buffer.from(result.output), { density: 125 })
      .png().toFile(path.join(directory, `${name}.png`));
    const svg = result.output.slice(result.output.indexOf('<svg'))
      .replace(/\bid="([^"]+)"/g, (_, id) => `id="${name}-${id}"`)
      .replace(/\bhref="#([^"]+)"/g, (_, id) => `href="#${name}-${id}"`);
    rendered.push({ name, title, svg });
    console.log(`${name}: rendered; Graphviz diagnostics ${JSON.stringify(result.errors)}`);
  }
  const html = `<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>JC-PINN / USERMAT / ANSYS — complete workflow</title>
<style>
body{font:16px/1.5 system-ui,sans-serif;color:#182c3c;background:#fff;margin:0}
header,main{max-width:1500px;margin:auto;padding:24px}h1{font-size:26px;margin:0 0 8px}
p{margin:6px 0 16px}nav{display:flex;gap:10px;flex-wrap:wrap;margin:20px 0}
button,a{color:#174d78}button{font:inherit;padding:10px 16px;border:1px solid #9aaebd;border-radius:5px;background:#fff;cursor:pointer}
button[aria-selected=true]{background:#174d78;color:#fff}button:focus-visible,a:focus-visible{outline:3px solid #936818;outline-offset:3px}
.controls{display:flex;align-items:center;gap:12px;flex-wrap:wrap}.viewport{overflow:auto;border-top:1px solid #ccd5dd;margin-top:16px}
.diagram{width:100%;min-width:700px}.diagram svg{width:100%;height:auto;display:block}article[hidden]{display:none}
.links{display:flex;gap:18px;flex-wrap:wrap}footer{margin-top:20px;color:#405260}
@media print{nav,.controls,.links{display:none}header{padding:10px}article[hidden]{display:block}.viewport{overflow:visible;border:0}.diagram{min-width:0;width:100%!important}article{break-before:page}}
</style>
<header><h1>JC-PINN + USERMAT in ANSYS</h1>
<p>Four linked flowcharts: the global bracket solve, the local stress update, the locked neural material evaluator, and the detailed plastic return mapping. These describe the implemented workflow, not experimental validation.</p>
<nav role="tablist" aria-label="Flowchart views">${rendered.map((p,i)=>`<button type="button" role="tab" id="tab-${i}" aria-controls="panel-${i}" aria-selected="${i===0}" data-page="${i}">${p.title}</button>`).join('')}</nav>
<div class="controls"><label for="zoom">Diagram width</label><select id="zoom"><option value="100">Fit</option><option value="150">150%</option><option value="200">200%</option></select><span>SVG text stays selectable and sharp when zoomed. Print includes all four views.</span></div></header>
<main>${rendered.map((p,i)=>`<article id="panel-${i}" role="tabpanel" aria-labelledby="tab-${i}" ${i?'hidden':''}><div class="links"><a href="${p.name}.svg">Open vector SVG</a><a href="${p.name}.png">PNG</a><a href="${p.name}.dot">Editable Graphviz source</a></div><div class="viewport"><div class="diagram">${p.svg}</div></div></article>`).join('')}
<footer>Read <a href="README.md">source references, scope and verification notes</a>. No invented bracket geometry is shown.</footer></main>
<script>
const tabs=Array.from(document.querySelectorAll('[role=tab]'));
function selectPage(index){tabs.forEach((tab,i)=>{tab.setAttribute('aria-selected',String(i===index));document.getElementById('panel-'+i).hidden=i!==index;});}
tabs.forEach((tab,i)=>{tab.addEventListener('click',()=>selectPage(i));tab.addEventListener('keydown',event=>{let next;if(event.key==='ArrowRight')next=(i+1)%tabs.length;if(event.key==='ArrowLeft')next=(i+tabs.length-1)%tabs.length;if(next!==undefined){event.preventDefault();selectPage(next);tabs[next].focus();}});});
document.getElementById('zoom').addEventListener('change',event=>{document.querySelectorAll('.diagram').forEach(element=>element.style.width=event.target.value+'%');});
</script></html>`;
  fs.writeFileSync(path.join(directory, 'index.html'), html);
}
main().catch(error => { console.error(error); process.exitCode = 1; });
