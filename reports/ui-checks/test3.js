const { JSDOM, VirtualConsole } = require('jsdom'); const BASE = 'http://127.0.0.1:8765'; const errors = [];
const vc = new VirtualConsole(); vc.on('jsdomError', (e) => errors.push(String(e.message || e)));
(async () => { const dom = await JSDOM.fromURL(BASE + '/', { runScripts: 'dangerously', resources: 'usable', pretendToBeVisual: true, virtualConsole: vc,
  beforeParse(w) { w.fetch = (u, o = {}) => ((o.method || 'GET').toUpperCase() !== 'GET' ? Promise.reject(new Error('BLOCKED')) : fetch(new URL(u, BASE), o)); w.matchMedia = () => ({ matches: false, addEventListener() {}, removeEventListener() {} }); w.HTMLElement.prototype.scrollIntoView = () => {}; } });
  const w = dom.window, d = w.document; await new Promise((r) => setTimeout(r, 3500));
  const ok = (n, c, x = '') => console.log((c ? 'PASS ' : 'FAIL ') + n + (x ? '  [' + x + ']' : ''));
  ok('default palette sage', d.documentElement.dataset.palette === 'sage');
  d.getElementById('view-toggle').click();
  const sw = [...d.querySelectorAll('#color-swatches .swatch')]; ok('picker shows 5 palettes', sw.length === 5, sw.map((s) => s.dataset.key).join(','));
  sw.find((s) => s.dataset.key === 'dusk').click();
  ok('dusk applied + remembered', d.documentElement.dataset.palette === 'dusk' && w.localStorage.getItem('room-palette') === 'dusk');
  d.body.click(); ok('click outside closes View menu', d.getElementById('view-menu').hidden);
  d.dispatchEvent(new w.KeyboardEvent('keydown', { key: 'k', ctrlKey: true, bubbles: true }));
  const inp = d.querySelector('.palette input'); inp.value = 'colours ocean'; inp.dispatchEvent(new w.Event('input', { bubbles: true }));
  const opt = d.querySelector('.palette .ai-option'); ok('Ctrl K lists colours', !!opt && opt.textContent.includes('Ocean'));
  opt.click(); ok('Ctrl K applies ocean', d.documentElement.dataset.palette === 'ocean');
  w.localStorage.removeItem('room-palette');
  console.log('script errors:', errors.length ? errors : 'none'); process.exit(0); })();
