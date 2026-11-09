// NetViz: detailed, animated forward pass of one JC-PINN correction network (5-16-16-1, tanh).
// Shared by the web page and the video renderer. Needs globals: el(), css(), hexMix(), clamp(), fmt(), M (model).
function netForward(mem, x) {
  const z = x.map((v, j) => (v - M.x_mean[j]) / M.x_scale[j]);
  const pre1 = mem.W1.map((row, i) => row.reduce((s, w, j) => s + w * z[j], mem.b1[i]));
  const h1 = pre1.map(Math.tanh);
  const pre2 = mem.W2.map((row, i) => row.reduce((s, w, j) => s + w * h1[j], mem.b2[i]));
  const h2 = pre2.map(Math.tanh);
  const d = h2.reduce((s, h, i) => s + h * mem.w3[i], mem.b3);
  return { z, pre: [null, pre1, pre2, [d]], act: [z, h1, h2, [d]] };
}

function NetViz(svg, box, mem, opt = {}) {
  const { x, y, w, h } = box, S = opt.scale || 1;
  const g = el('g', {}, svg);
  const names = ['T', 'log rate', 'ρ', 'G', 'E11'];
  const L = [5, 16, 16, 1];
  const colX = [x + 150 * S, x + w * 0.42, x + w * 0.64, x + w * 0.80];
  const top = y + 52 * S, bot = y + h - 178 * S;
  const ys = n => Array.from({ length: n }, (_, i) => n === 1 ? (top + bot) / 2 : top + i * (bot - top) / (n - 1));
  const P = L.map((n, l) => ys(n).map(yy => [colX[l], yy]));
  const Wt = [null, mem.W1, mem.W2, [mem.w3]];
  // layer titles
  const titles = ['inputs → standardised z', 'hidden 1 · 16 × tanh', 'hidden 2 · 16 × tanh', 'output δ'];
  titles.forEach((t, l) => el('text', { x: colX[l], y: y + 14 * S, 'text-anchor': 'middle', class: 'sub', style: `font-size:${11 * S}px` }, g).textContent = t);
  // wires
  const wires = [];
  const wg = el('g', {}, g);
  for (let l = 1; l < 4; l++) for (let i = 0; i < L[l]; i++) for (let j = 0; j < L[l - 1]; j++) {
    const [x1, y1] = P[l - 1][j], [x2, y2] = P[l][i];
    wires.push({ l, i, j, x1, y1, x2, y2, e: el('line', { x1, y1, x2, y2, 'stroke-linecap': 'round' }, wg) });
  }
  const pulseG = el('g', {}, g);
  const pulses = Array.from({ length: 40 }, () => el('circle', { r: 2.6 * S, opacity: 0 }, pulseG));
  // nodes
  const R = [13 * S, 8 * S, 8 * S, 16 * S];
  const nodes = P.map((col, l) => col.map(([cx, cy]) => el('circle', { cx, cy, r: R[l], 'stroke-width': 1.3 * S }, g)));
  const focusRing = el('circle', { r: 14 * S, fill: 'none', 'stroke-width': 2.4 * S, opacity: 0 }, g);
  // input labels
  const inRaw = [], inZ = [];
  P[0].forEach(([cx, cy], j) => {
    el('text', { x: cx - 26 * S, y: cy - 4 * S, 'text-anchor': 'end', style: `font-size:${12.5 * S}px`, class: 'lab' }, g).textContent = names[j];
    inRaw.push(el('text', { x: cx - 26 * S, y: cy + 11 * S, 'text-anchor': 'end', class: 'sub', style: `font-size:${10.5 * S}px` }, g));
    inZ.push(el('text', { x: cx + 18 * S, y: cy - 12 * S, class: 'sub', style: `font-size:${10 * S}px` }, g));
  });
  const outTxt = el('text', { x: colX[3] + 24 * S, y: (top + bot) / 2 - 6 * S, style: `font-size:${14 * S}px` }, g);
  const facTxt = el('text', { x: colX[3] + 24 * S, y: (top + bot) / 2 + 14 * S, class: 'sub', style: `font-size:${12 * S}px` }, g);
  // focus panel
  const fy = bot + 56 * S, fx = x + 20 * S;
  const fTitle = el('text', { x: fx, y: fy, class: 'lab', style: `font-size:${13 * S}px` }, g);
  const fEq = el('text', { x: fx, y: fy + 24 * S, style: `font-size:${12 * S}px` }, g);
  const fSum = el('text', { x: fx, y: fy + 46 * S, class: 'sub', style: `font-size:${11.5 * S}px` }, g);
  // tanh mini plot
  const tx = x + w - 230 * S, ty = bot + 40 * S, tw = 210 * S, th = 110 * S;
  el('rect', { x: tx, y: ty, width: tw, height: th, fill: 'none', class: 'axis' }, g);
  el('line', { x1: tx, x2: tx + tw, y1: ty + th / 2, y2: ty + th / 2, class: 'gridl' }, g);
  el('line', { x1: tx + tw / 2, x2: tx + tw / 2, y1: ty, y2: ty + th, class: 'gridl' }, g);
  const TX = v => tx + (clamp(v, -3, 3) + 3) / 6 * tw, TY = v => ty + th / 2 - v * (th / 2 - 6 * S);
  el('path', { d: Array.from({ length: 61 }, (_, k) => { const v = -3 + k * 0.1; return (k ? 'L' : 'M') + TX(v).toFixed(1) + ' ' + TY(Math.tanh(v)).toFixed(1); }).join(''), fill: 'none', stroke: 'currentColor', 'stroke-width': 1.4 * S }, g);
  el('text', { x: tx + 6 * S, y: ty + 14 * S, class: 'sub', style: `font-size:${10.5 * S}px` }, g).textContent = 'tanh(sum)';
  el('text', { x: tx + tw - 4 * S, y: ty + th - 6 * S, 'text-anchor': 'end', class: 'sub', style: `font-size:${10 * S}px` }, g).textContent = 'sum →';
  const tDot = el('circle', { r: 5 * S }, g);
  const tGuide = el('path', { fill: 'none', 'stroke-dasharray': `${3 * S} ${3 * S}`, 'stroke-width': 1 * S }, g);

  let manualFocus = null;
  nodes.forEach((col, l) => col.forEach((c, i) => { if (l > 0) { c.style.cursor = 'pointer'; c.addEventListener('click', () => { manualFocus = manualFocus && manualFocus[0] === l && manualFocus[1] === i ? null : [l, i]; if (viz.last) viz.update(viz.last); }); } }));

  const viz = {
    g, setManual(f) { manualFocus = f; },
    // st = { x5, p (0..3: wave progress through layers), focus: 'auto' | [l,i] }
    update(st) {
      viz.last = st;
      const fw = netForward(mem, st.x5), p = st.p;
      const cPos = css('--model'), cNeg = css('--eq'), sur = css('--surface'), ink = css('--ink');
      // contributions per wire
      let maxC = [0, 0, 0, 0];
      for (const wr of wires) { wr.c = Wt[wr.l][wr.i][wr.j] * fw.act[wr.l - 1][wr.j]; maxC[wr.l] = Math.max(maxC[wr.l], Math.abs(wr.c)); }
      for (const wr of wires) {
        const lit = clamp(p - (wr.l - 1), 0, 1), u = Math.abs(wr.c) / (maxC[wr.l] || 1);
        wr.e.setAttribute('stroke', wr.c >= 0 ? cPos : cNeg);
        wr.e.setAttribute('stroke-width', ((0.35 + 2.6 * u * lit) * S).toFixed(2));
        wr.e.setAttribute('stroke-opacity', (0.05 + 0.75 * u * lit).toFixed(3));
      }
      // pulses travel along the strongest wires of the layer currently being computed
      const layer = clamp(Math.floor(p) + 1, 1, 3), frac = p - Math.floor(p);
      const active = p < 3 ? wires.filter(wr => wr.l === layer).sort((a, b) => Math.abs(b.c) - Math.abs(a.c)).slice(0, pulses.length) : [];
      pulses.forEach((pc, k) => {
        const wr = active[k];
        if (!wr) { pc.setAttribute('opacity', 0); return; }
        const f = clamp(frac * 1.15 - (k % 5) * 0.03, 0, 1);
        pc.setAttribute('cx', (wr.x1 + (wr.x2 - wr.x1) * f).toFixed(1)); pc.setAttribute('cy', (wr.y1 + (wr.y2 - wr.y1) * f).toFixed(1));
        pc.setAttribute('fill', wr.c >= 0 ? cPos : cNeg); pc.setAttribute('opacity', (f < 1 ? 0.9 : 0).toString());
      });
      // nodes
      nodes.forEach((col, l) => col.forEach((c, i) => {
        const on = clamp((p - (l - 1)) * 3 - 2, 0, 1) * (l === 0 ? 1 : 1);
        const a = l === 0 ? Math.tanh(fw.act[0][i]) : l === 3 ? Math.tanh(fw.act[3][0]) : fw.act[l][i];
        const lv = l === 0 ? 1 : on;
        c.setAttribute('fill', hexMix(sur, a >= 0 ? cPos : cNeg, Math.min(1, Math.abs(a)) * lv));
        c.setAttribute('stroke', lv > 0.5 ? (a >= 0 ? cPos : cNeg) : css('--line'));
      }));
      fw.z.forEach((v, j) => { inZ[j].textContent = 'z = ' + fmt(v, 2); });
      const raw = [st.x5[0] + ' °C', '1e' + st.x5[1] + ' /s', st.x5[2] + ' kg/m³', st.x5[3] + ' MPa', st.x5[4].toFixed(4)];
      raw.forEach((v, j) => inRaw[j].textContent = v);
      const outOn = clamp((p - 2) * 3 - 2, 0, 1);
      outTxt.textContent = outOn > 0 ? 'δ = ' + fmt(fw.act[3][0], 3) : 'δ = …';
      facTxt.textContent = outOn > 0 ? 'correction e^δ = ×' + fmt(Math.exp(fw.act[3][0]), 3) : '';
      // focus neuron: manual, else the most active unit of the layer just computed
      let f = manualFocus || (Array.isArray(st.focus) ? st.focus : null);
      if (!f) {
        const fl = p < 1.0 ? 1 : p < 2.0 ? 1 : p < 2.6 ? 2 : 3;
        const acts = fw.act[fl];
        let best = 0; acts.forEach((v, i) => { if (Math.abs(v) > Math.abs(acts[best])) best = i; });
        f = [fl, best];
      }
      const [fl, fi] = f, [cx, cy] = P[fl][fi];
      focusRing.setAttribute('cx', cx); focusRing.setAttribute('cy', cy); focusRing.setAttribute('r', R[fl] + 6 * S);
      focusRing.setAttribute('stroke', ink); focusRing.setAttribute('opacity', clamp((p - (fl - 1)) * 2, 0, 1));
      const ws = Wt[fl][fi], src = fw.act[fl - 1], bias = fl === 1 ? mem.b1[fi] : fl === 2 ? mem.b2[fi] : mem.b3;
      const terms = ws.map((wv, j) => ({ j, wv, a: src[j], c: wv * src[j] })).sort((a, b) => Math.abs(b.c) - Math.abs(a.c));
      const srcName = j => fl === 1 ? 'z(' + names[j] + ')' : 'h' + (fl - 1) + '[' + (j + 1) + ']';
      const lname = fl === 3 ? 'Output δ' : `Hidden ${fl}, unit ${fi + 1} of 16`;
      fTitle.textContent = lname + (opt.noHint ? '' : manualFocus ? ' (selected; click again to release)' : ' (click any unit to inspect it)');
      const shown = terms.slice(0, 3).map(t => `${t.wv >= 0 ? '+' : '−'}${Math.abs(t.wv).toFixed(2)}·${srcName(t.j)}`).join(' ');
      const pre = fw.pre[fl][fl === 3 ? 0 : fi];
      fEq.textContent = (fl === 3 ? 'δ = ' : 'sum = ') + shown + ` + ${terms.length - 3} more ${bias >= 0 ? '+' : '−'} ${Math.abs(bias).toFixed(2)} (bias)`;
      const outA = fl === 3 ? pre : Math.tanh(pre);
      fSum.textContent = fl === 3 ? `= ${fmt(pre, 3)}  (linear output, no tanh)` : `sum = ${fmt(pre, 3)}  →  tanh(sum) = ${fmt(outA, 3)}`;
      const showT = fl !== 3;
      tDot.setAttribute('cx', TX(pre)); tDot.setAttribute('cy', TY(showT ? Math.tanh(pre) : clamp(pre, -1, 1)));
      tDot.setAttribute('fill', outA >= 0 ? cPos : cNeg); tDot.setAttribute('opacity', showT ? 1 : 0.25);
      tGuide.setAttribute('d', `M${TX(pre).toFixed(1)} ${(ty + th).toFixed(1)}V${TY(Math.tanh(pre)).toFixed(1)}H${tx.toFixed(1)}`); tGuide.setAttribute('stroke', ink); tGuide.setAttribute('opacity', showT ? .5 : 0);
      return fw;
    }
  };
  return viz;
}
