const { JSDOM, VirtualConsole } = require('jsdom');
const BASE = 'http://127.0.0.1:8765';
const errors = [];
const vc = new VirtualConsole(); vc.on('jsdomError', (e) => errors.push(String(e.message || e)));
(async () => {
  const dom = await JSDOM.fromURL(BASE + '/', {
    runScripts: 'dangerously', resources: 'usable', pretendToBeVisual: true, virtualConsole: vc,
    beforeParse(w) {
      w.fetch = (u, o = {}) => {
        if ((o.method || 'GET').toUpperCase() !== 'GET') return Promise.reject(new Error('BLOCKED write in test'));
        return fetch(new URL(u, BASE), o);
      };
      w.matchMedia = (q) => ({ matches: false, media: q, addEventListener() {}, removeEventListener() {}, addListener() {}, removeListener() {} });
      w.HTMLElement.prototype.scrollIntoView = function () {};
      w.HTMLTextAreaElement.prototype.setRangeText = w.HTMLTextAreaElement.prototype.setRangeText || function (t, s, e) { this.value = this.value.slice(0, s) + t + this.value.slice(e); };
    },
  });
  const w = dom.window, d = w.document, wait = (ms) => new Promise((r) => setTimeout(r, ms));
  await wait(3500);
  const check = (name, ok, x = '') => console.log((ok ? 'PASS ' : 'FAIL ') + name + (x ? '  [' + x + ']' : ''));
  check('feed rendered messages', d.querySelectorAll('#feed .message').length > 10);
  check('suggestion chips rendered', d.querySelectorAll('#suggestions .suggest-chip').length === 4);
  check('agent messages get AI badge', d.querySelectorAll('.message.from-agent .agent-tag.is-ai').length > 5);
  check('vendor shown on agent messages', d.querySelectorAll('.vendor-tag').length > 5);
  check('@mentions turned into chips', d.querySelectorAll('.mention-chip').length > 0);
  check('agent activity lines', d.querySelectorAll('#participants .agent-activity').length === 3);
  console.log('   e.g.', [...d.querySelectorAll('#participants .agent-activity')].map((n) => n.textContent).join(' | '));
  const box = d.getElementById('message');
  box.focus(); box.value = '/sta'; box.selectionStart = box.selectionEnd = 4; box.dispatchEvent(new w.Event('input', { bubbles: true }));
  const menu = d.getElementById('ai-menu');
  check('slash menu opens and filters', !!menu && menu.querySelectorAll('.ai-option').length >= 1 && menu.textContent.includes('Status check'));
  menu.querySelector('.ai-option').dispatchEvent(new w.MouseEvent('mousedown', { bubbles: true }));
  check('slash command fills template', box.value.includes('Status check') && box.value.includes('@Codex') && !d.getElementById('ai-menu'));
  box.value = 'hey @Ge'; box.selectionStart = box.selectionEnd = box.value.length; box.dispatchEvent(new w.Event('input', { bubbles: true }));
  const m2 = d.getElementById('ai-menu');
  check('@ autocomplete shows Gemini', !!m2 && m2.textContent.includes('Gemini'));
  m2.querySelector('.ai-option').dispatchEvent(new w.MouseEvent('mousedown', { bubbles: true }));
  check('@ autocomplete inserts mention', box.value === 'hey @Gemini ');
  check('send wakes when text present', d.getElementById('send').classList.contains('ready'));
  d.dispatchEvent(new w.KeyboardEvent('keydown', { key: 'k', ctrlKey: true, bubbles: true }));
  const pal = d.querySelector('.palette');
  check('Ctrl K opens palette', !!pal && pal.querySelectorAll('.ai-option').length > 8);
  const inp = pal.querySelector('input'); inp.value = 'export'; inp.dispatchEvent(new w.Event('input', { bubbles: true }));
  check('palette filters', [...pal.querySelectorAll('.ai-option')].every((o) => /export/i.test(o.textContent)) && pal.querySelectorAll('.ai-option').length >= 1, [...pal.querySelectorAll('.ai-option')].map((o) => o.querySelector('strong').textContent).join(', '));
  inp.dispatchEvent(new w.KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
  check('Esc closes palette', !d.querySelector('.palette'));
  box.value = ''; box.dispatchEvent(new w.Event('input', { bubbles: true }));
  console.log('script errors:', errors.length ? errors : 'none');
  w.close(); process.exit(0);
})().catch((e) => { console.error('TEST CRASH', e); process.exit(1); });
