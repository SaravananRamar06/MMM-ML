const { chromium } = require('playwright');
const { spawn } = require('child_process');
(async () => {
  const FPS = 30, out = process.argv[2];
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  const errs = []; p.on('pageerror', e => errs.push(String(e)));
  await p.goto('file://' + __dirname + '/build/stage_built.html', { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  const total = await p.evaluate(() => TOTAL), n = Math.ceil(total * FPS);
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
    '-i', __dirname + '/build/narration.wav', '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p',
    '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const t0 = Date.now();
  for (let i = 0; i < n; i++) {
    await p.evaluate(t => renderAt(t), i / FPS);
    const buf = await p.screenshot({ type: 'jpeg', quality: 92 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 600 === 0) console.log(`frame ${i}/${n} ${((Date.now() - t0) / 1000).toFixed(0)} s`);
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r));
  console.log('done', n, 'frames', ((Date.now() - t0) / 1000).toFixed(0), 's; page errors', errs);
  await b.close();
})();
