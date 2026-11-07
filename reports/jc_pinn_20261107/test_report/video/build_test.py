"""Build the JC-PINN test-results video inputs: neural narration, a quiet synthesised music bed, captions, timeline, stage.

Run: python build_test.py [edge:<voice> | espeak voice]   then   node render.js build/jc_pinn_test_results.mp4
Data: ../video_bundle.json, written by scripts/test_report_jc_pinn.py from the locked model (no refitting).
"""
import json, os, subprocess, sys, wave
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
VOICE = sys.argv[1] if len(sys.argv) > 1 else 'edge:en-US-AndrewNeural'
RATE = 44100

SCRIPT = [
 ('title', 8, [
   ('How good is the J C PINN on simulations it has never seen? This video tests it on the thirty-seven held-out cases.',
    'How good is the JC-PINN on simulations it has never seen?')]),
 ('protocol', 15, [
   ('The seventy-three simulations were split at random. Thirty-six trained the model, and its settings were chosen using those alone.',
    '73 simulations, split at random: 36 trained the model and chose its settings.'),
   ('Then the model was saved and locked, with its fingerprint recorded, before a single test file was opened.',
    'The model was locked, fingerprint recorded, before any test file was opened.'),
   ('So nothing you are about to see was tuned on the test data.', 'Nothing in this video was tuned on the test data.')]),
 ('coverage', 13, [
   ('The test cases cover eight combinations of temperature and strain rate.', 'The test cases cover eight temperature and strain-rate combinations.'),
   ('One of them, thirty degrees at ten to the minus four per second, has eight test cases but only one training case. Keep an eye on it.',
    '30 °C at 1e-4 /s: eight test cases, but only one training case.')]),
 ('all37', 16, [
   ('Here are all thirty-seven predictions, drawn from best to worst, against the simulations.', 'All 37 predictions, best to worst, against the simulations.'),
   ('The average error per curve is zero point four four megapascals, about zero point four percent of the stress.',
    'Average error per curve: 0.44 MPa, about 0.4 % of the stress.')]),
 ('parity', 13, [
   ('Plot every one of the four thousand, four hundred and forty test points against its true value, and they sit right on the diagonal.',
    'All 4,440 test points, predicted against simulated, sit on the diagonal.'),
   ('R squared is zero point nine nine nine five.', 'R² = 0.9995.')]),
 ('histogram', 14, [
   ('Ninety-five percent of the points are within one megapascal, and eighty percent are within half a megapascal.',
    '95 % of points are within ±1 MPa, and 80 % within ±0.5 MPa.'),
   ('The errors are centred on zero: seventeen curves come out slightly high, and twenty slightly low.',
    'Errors are centred on zero: 17 curves slightly high, 20 slightly low.')]),
 ('strain', 12, [
   ('The error is smallest in the middle of the curve. It grows near ten percent strain, where the model tends to under-predict slightly.',
    'Error is smallest mid-curve and grows near 10 % strain, where the model under-predicts slightly.')]),
 ('extremes', 16, [
   ('The best case, number thirty-seven, is off by less than a tenth of a megapascal.', 'Best case, #37: off by less than 0.1 MPa.'),
   ('The eight worst cases are all at thirty degrees and ten to the minus four per second: the combination with a single training example.',
    'The 8 worst cases are all at 30 °C, 1e-4 /s, the condition with one training case.'),
   ('Even there, the error stays below one megapascal.', 'Even there, the error stays below 1 MPa.')]),
 ('members', 13, [
   ('The five independently trained copies agree closely, typically within a tenth of a megapascal, so the result is stable.',
    'The five trained copies agree within about 0.1 MPa: the result is stable.')]),
 ('compare', 16, [
   ('On the same thirty-seven cases, the JC PINN beats the Johnson–Cook equation on its own in every case, and the curve-copy baseline in twenty-four.',
    'It beats Equation 1 alone in all 37 cases, and the curve-copy baseline in 24.'),
   ('But the earlier plain neural networks are more precise on this random split, and so is the same network without the equation.',
    'The earlier plain MLPs, and the same network without Equation 1, are more precise here.')]),
 ('verdict', 14, [
   ('So, within thirty to two hundred degrees, the model reproduces unseen simulations to well under one megapascal, with no systematic bias.',
    'At 30–200 °C it reproduces unseen simulations to well under 1 MPa, with no bias.'),
   ('For new temperature and rate combinations, expect errors of several megapascals. And above two hundred degrees, it is unverified.',
    'New temperature/rate combinations: several MPa. Above 200 °C: unverified.')]),
]

out = HERE / 'build'
out.mkdir(exist_ok=True)


def synth(text, path):
    if VOICE.startswith('edge:'):
        raw = path.with_suffix('.raw.mp3')
        env = dict(os.environ, SSL_CERT_FILE=os.environ.get('SSL_CERT_FILE', '/root/.ccr/ca-bundle.crt'))
        cmd = [str(Path(sys.executable).with_name('edge-tts')), '--voice', VOICE[5:], '--rate=-4%', '--text', text, '--write-media', str(raw)]
        if os.environ.get('HTTPS_PROXY'):
            cmd[1:1] = ['--proxy', os.environ['HTTPS_PROXY']]
        subprocess.run(cmd, check=True, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        af = 'loudnorm=I=-17:TP=-1.5'
    else:
        raw = path.with_suffix('.raw.wav')
        subprocess.run(['espeak-ng', '-v', VOICE, '-s', '158', '-w', str(raw), text], check=True)
        af = 'loudnorm=I=-18:TP=-2'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(raw), '-ar', str(RATE), '-ac', '1', '-af', af, str(path)], check=True)
    with wave.open(str(path)) as w:
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768


TL, clips, t0 = [], [], 0.0
for si, (key, mindur, sents) in enumerate(SCRIPT):
    local, items = 0.7, []
    for k, (say, show) in enumerate(sents):
        a = synth(say, out / f's{si}_{k}.wav')
        d = len(a) / RATE
        items.append(dict(show=show, start=round(local, 3), end=round(local + d, 3)))
        clips.append((t0 + local, a))
        local += d + 0.5
    dur = max(mindur, local + 1.0)
    TL.append(dict(key=key, dur=round(dur, 3), sentences=items))
    t0 += dur
total = t0
n = int(total * RATE) + RATE
voice = np.zeros(n, dtype=np.float32)
for start, a in clips:
    i = int(start * RATE)
    voice[i:i + len(a)] += a

# quiet music bed: slow Am-F-C-G pad of soft sine/triangle partials, low-passed, with gentle swells
t = np.arange(n) / RATE
chords = [[57, 60, 64], [53, 57, 60], [48, 55, 60], [55, 59, 62]]           # MIDI notes
hz = lambda m: 440 * 2 ** ((m - 69) / 12)
pad = np.zeros(n, dtype=np.float64)
bar = 6.0
for c_i in range(int(total / bar) + 2):
    notes = chords[c_i % 4]
    s0, s1 = int(c_i * bar * RATE), int((c_i + 1) * bar * RATE + 1.5 * RATE)
    s1 = min(s1, n)
    if s0 >= n:
        break
    tt = t[s0:s1] - c_i * bar
    env = np.minimum(1, tt / 1.5) * np.minimum(1, np.maximum(0, (bar + 1.5 - tt) / 1.5))
    for m in notes + [notes[0] - 12]:
        f = hz(m)
        pad[s0:s1] += env * (0.6 * np.sin(2 * np.pi * f * tt) + 0.25 * np.sin(2 * np.pi * 2 * f * tt + 0.3) + 0.1 * np.sin(2 * np.pi * 3 * f * tt + 1.1))
pad *= 0.5 + 0.5 * np.sin(2 * np.pi * t / 23.0) ** 2                        # slow swell
k = np.exp(-np.arange(int(0.004 * RATE)) / (0.0012 * RATE)); k /= k.sum()  # soften
pad = np.convolve(pad, k, mode='same')
fade = np.minimum(1, t / 3.0) * np.minimum(1, np.maximum(0, (total - t) / 4.0))
pad = pad / (np.abs(pad).max() + 1e-9) * 0.055 * fade                       # about -25 dB peak, well under the voice
# duck the music slightly while the voice speaks
env_v = np.convolve(np.abs(voice), np.ones(int(0.25 * RATE)) / int(0.25 * RATE), mode='same')
pad *= 1 - 0.45 * np.clip(env_v / (env_v.max() + 1e-9) * 4, 0, 1)
mix = np.clip(voice + pad.astype(np.float32), -1, 1)
with wave.open(str(out / 'soundtrack.wav'), 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(RATE)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())


def ts(x):
    h, r = divmod(x, 3600); m, s = divmod(r, 60)
    return f'{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s - int(s)) * 1000)):03d}'
srt, acc, num = [], 0.0, 1
for s in TL:
    for it in s['sentences']:
        srt.append(f"{num}\n{ts(acc + it['start'])} --> {ts(acc + it['end'] + 0.25)}\n{it['show']}\n"); num += 1
    acc += s['dur']
(out / 'jc_pinn_test_results.srt').write_text('\n'.join(srt), encoding='utf-8')
bundle = (HERE.parent / 'video_bundle.json').read_text()
page = (HERE / 'stage_test.html').read_text().replace('/*DATA*/', bundle).replace('/*TIMELINE*/', json.dumps(TL))
(out / 'stage_built.html').write_text(page, encoding='utf-8')
(out / 'timeline.json').write_text(json.dumps(TL, indent=1))
print('scenes', [(s['key'], s['dur']) for s in TL], 'total %.1f s' % total)
