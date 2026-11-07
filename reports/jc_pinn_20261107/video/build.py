"""Build the JC-PINN explainer inputs: narration (espeak-ng + MBROLA voice), captions, timeline and the stage page.

Run: python build.py [voice]  then  node render.js build/jc_pinn_explainer.mp4  (needs Playwright Chromium and ffmpeg).
bundle.json holds the saved model, the 73 curves, the recorded member-0 training trace and the selection results."""
import json, subprocess, wave, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
VOICE = sys.argv[1] if len(sys.argv) > 1 else 'edge:en-US-AndrewNeural'
RATE = 44100

SCRIPT = [
 ('title', 7, [
   ('This is the J C PINN: a physics-informed neural network for the stress–strain behaviour of an additively manufactured aluminium–silicon–magnesium alloy.',
    'JC-PINN: a physics-informed model for additively manufactured AlSi10Mg.')]),
 ('data', 14, [
   ('The professor supplied seventy-three simulated stress–strain curves.', 'The professor supplied 73 simulated stress–strain curves.'),
   ('They cover three temperatures, three strain rates, three densities and three shear moduli.', 'Three temperatures, three strain rates, three densities, three shear moduli.'),
   ('Every curve softens, and its shape changes with temperature and rate.', 'Every curve softens, and its shape changes with temperature and rate.'),
   ('Thirty-six curves are used to train the model, and thirty-seven are kept back for the final test.', '36 curves train the model; 37 are kept back for the final test.')]),
 ('equation', 14, [
   ('The governing law is our customised Johnson–Cook equation.', 'The governing law is our customised Johnson–Cook equation.'),
   ('It multiplies together a strain term, a strain-rate term, a temperature term, and terms for shear modulus and porosity.', 'Strain, rate, temperature, shear-modulus and porosity terms are multiplied.'),
   ('Fitted on its own, it misses the curves by about ten percent.', 'Fitted on its own, it misses the curves by about 10 %.'),
   ('A product of separate terms gives every condition the same curve shape.', 'A product of separate terms gives every condition the same curve shape.')]),
 ('model', 11, [
   ('So the equation becomes the backbone of the model, and it is multiplied by a learned correction factor: e to the power delta.', 'So the equation becomes the backbone, multiplied by a learned correction e^δ.'),
   ('Before training, delta is zero, so the model starts as exactly the equation.', 'Before training δ = 0, so the model starts as exactly the equation.')]),
 ('network', 21, [
   ('Inside the correction network, the five inputs are first standardised.', 'Inside the network, the five inputs are first standardised.'),
   ('They then pass through two layers of sixteen units.', 'They pass through two hidden layers of 16 units each.'),
   ('Each unit adds up its weighted inputs plus a bias, and then squashes the sum to between minus one and one.', 'Each unit adds its weighted inputs and a bias, then squashes the sum with tanh.'),
   ('Thicker wires carry stronger signals. Blue ones push the result up, and amber ones push it down.', 'Thicker wires carry stronger signals: blue pushes up, amber pushes down.'),
   ('The single output, delta, sets the correction at every strain.', 'The single output δ sets the correction factor at every strain.')]),
 ('training', 16, [
   ('Training starts from the equation alone.', 'Training starts from the equation alone.'),
   ('Fifteen hundred Adam steps learn the curve shapes, and then L-B-F-G-S fine-tunes them.', '1,500 Adam steps learn the curve shapes; L-BFGS then refines them.'),
   ('The mean training error falls from about nine megapascals to just zero point three five.', 'Mean training error falls from 8.95 to 0.35 MPa.')]),
 ('selection', 13, [
   ('Fourteen different settings, including physics penalties, were scored using the training cases only.', '14 settings, including physics penalties, were scored on training cases only.'),
   ('They were tested with cross-validation, and by hiding whole temperature and strain-rate groups.', 'Cross-validation folds, plus whole temperature/rate groups hidden.'),
   ('The best setting was locked before any test file was read.', 'The best setting was locked before any test file was read.')]),
 ('test', 15, [
   ('Five independently trained copies are averaged into one prediction.', 'Five trained copies are averaged into one prediction.'),
   ('On the thirty-seven test cases, the error is zero point four four megapascals: seventeen times better than the equation on its own.', 'Test error: 0.44 MPa on 37 unseen cases, 17× better than the equation alone.'),
   ('The same network without the equation does slightly better.', 'The same network without the equation does slightly better (0.34 MPa).'),
   ('So the equation adds named, physical constants, rather than accuracy.', 'So the equation adds named physical constants, not accuracy.')]),
 ('close', 11, [
   ('The model is valid from thirty to two hundred degrees Celsius, at the simulated strain rates and porosities.', 'Valid for 30–200 °C at the simulated rates and porosities.'),
   ('Above two hundred degrees there is no data, so predictions there have not been verified.', 'Above 200 °C there is no data, so predictions there are unverified.')]),
]

out = HERE / 'build'
out.mkdir(exist_ok=True)


def synth(text, path):
    """edge:<voice> uses Microsoft Edge neural TTS (online, via the session proxy); anything else is an espeak-ng voice."""
    import os
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
        subprocess.run(['espeak-ng', '-v', VOICE, '-s', '158', '-g', '3', '-w', str(raw), text], check=True)
        af = 'highpass=f=70,lowpass=f=7500,loudnorm=I=-18:TP=-2'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(raw), '-ar', str(RATE), '-ac', '1', '-af', af, str(path)], check=True)
    with wave.open(str(path)) as w:
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768


TL, clips, t0 = [], [], 0.0
for si, (key, mindur, sents) in enumerate(SCRIPT):
    local, items = 0.6, []
    for k, (say, show) in enumerate(sents):
        a = synth(say, out / f's{si}_{k}.wav')
        d = len(a) / RATE
        items.append(dict(show=show, start=round(local, 3), end=round(local + d, 3)))
        clips.append((t0 + local, a))
        local += d + 0.45
    dur = max(mindur, local + 0.9)
    TL.append(dict(key=key, dur=round(dur, 3), sentences=items))
    t0 += dur
total = t0
audio = np.zeros(int(total * RATE) + RATE, dtype=np.float32)
for start, a in clips:
    i = int(start * RATE)
    audio[i:i + len(a)] += a
audio = np.clip(audio, -1, 1)
with wave.open(str(out / 'narration.wav'), 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(RATE)
    w.writeframes((audio * 32767).astype(np.int16).tobytes())

# subtitles
def ts(x):
    h, r = divmod(x, 3600); m, s = divmod(r, 60)
    return f'{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s - int(s)) * 1000)):03d}'
srt, acc, n = [], 0.0, 1
for s in TL:
    for it in s['sentences']:
        srt.append(f"{n}\n{ts(acc + it['start'])} --> {ts(acc + it['end'] + 0.25)}\n{it['show']}\n"); n += 1
    acc += s['dur']
(out / 'jc_pinn_explainer.srt').write_text('\n'.join(srt), encoding='utf-8')

# stage page
bundle = json.loads((HERE / 'bundle.json').read_text())
bundle['train_ids'] = json.loads((REPO / 'data/split.json').read_text())['train']
page = (HERE / 'stage.html').read_text().replace('/*NETVIZ*/', (HERE / 'netviz.js').read_text()) \
    .replace('/*DATA*/', json.dumps(bundle, separators=(',', ':'))).replace('/*TIMELINE*/', json.dumps(TL))
(out / 'stage_built.html').write_text(page, encoding='utf-8')
(out / 'timeline.json').write_text(json.dumps(TL, indent=1))
print('scenes', [(s['key'], s['dur']) for s in TL], 'total %.1f s' % total)
