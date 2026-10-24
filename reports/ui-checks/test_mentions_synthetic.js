const { JSDOM, VirtualConsole } = require('jsdom');
const BASE = 'http://127.0.0.1:8765';
(async () => {
  const dom = await JSDOM.fromURL(BASE + '/', { runScripts: 'dangerously', resources: 'usable', pretendToBeVisual: true, virtualConsole: new VirtualConsole(),
    beforeParse(w) { w.fetch = (u, o = {}) => ((o.method || 'GET') !== 'GET' ? Promise.reject(new Error('blocked')) : fetch(new URL(u, BASE), o));
      w.matchMedia = (q) => ({ matches: false, addEventListener() {}, removeEventListener() {} }); w.HTMLElement.prototype.scrollIntoView = () => {}; } });
  await new Promise((r) => setTimeout(r, 3500));
  const d = dom.window.document;
  const card = d.createElement('article'); card.className = 'message'; card.dataset.messageId = 'zz_test';
  card.innerHTML = '<span class="avatar codex">CX</span><div class="message-content"><div class="message-meta"><strong>Codex</strong><span class="agent-tag">Agent</span></div><div class="markdown"><p>Thanks @Claude and @You, see <code>@Gemini</code> too.</p></div></div>';
  d.getElementById('feed').append(card);
  await new Promise((r) => setTimeout(r, 100));
  const chips = [...card.querySelectorAll('.mention-chip')].map((c) => c.textContent + (c.classList.contains('to-you') ? '(you)' : ''));
  console.log('chips:', chips, '| code untouched:', card.querySelector('code').textContent === '@Gemini', '| badge:', card.querySelector('.agent-tag').textContent, '| new-msg class:', card.classList.contains('is-new'));
  process.exit(0);
})();
