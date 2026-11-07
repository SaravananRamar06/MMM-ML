# JC-PINN explainer video

`jc_pinn_explainer.mp4`: 2 min 52 s, 1920×1080, 30 fps, H.264 and AAC narration. Burned-in captions are also in `jc_pinn_explainer.srt`.

## Scenes

1. Title
2. The 73 simulated curves
3. The customised Johnson–Cook equation and why it fails alone
4. Backbone × correction
5. A detailed forward pass through the correction network
6. Replay of member 0's real training
7. Selection of the 14 settings
8. The five copies and the test results
9. Validity

## Where the content comes from

Every frame is drawn from real data in `bundle.json`:
* the saved model in `../equation.json`;
* the 73 interpolated curves;
* the recorded training trace in `../training_trace_member0.json`, whose final weights match the saved member 0 exactly;
* the selection results.

## Rebuild

```bash
python build.py mb-en1
NODE_PATH=$(npm root -g) node render.js build/jc_pinn_explainer.mp4
```

* `build.py` synthesises each narration sentence with espeak-ng and the MBROLA `mb-en1` voice (apt packages `espeak-ng`, `mbrola-en1`). It sizes each scene to its speech and writes the caption timings and the stage page.
* `render.js` uses Playwright Chromium to call `renderAt(t)` for every frame and pipes the frames to ffmpeg.
* A more natural neural voice (Piper or Kokoro) needs `huggingface.co` and `github.com`. The session's egress gateway currently blocks both.
