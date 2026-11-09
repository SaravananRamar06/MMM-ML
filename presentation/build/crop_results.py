"""Tighten the three Workbench contour screenshots: keep the legend block and the model, drop empty background.
Run: python crop_results.py  (reads ../source/results, writes ../assets/result_*.png)"""
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
SRC, OUT = HERE.parent / "source" / "results", HERE.parent / "assets"
jobs = {
    "result_el.png": ("A Elastic - equivalent stress.png", 440),
    "result_jcb.png": ("B Built-in JC - equivalent stress.png", 440),
    "result_jcu.png": ("C User Defined JC - equivalent stress.png", 430),
}
for out, (src, x0) in jobs.items():
    im = Image.open(SRC / src).convert("RGB")
    w, h = im.size
    legend = im.crop((0, 0, 300, 430))
    model = im.crop((x0, 0, min(x0 + 570, w), h))
    # the Ansys background is a vertical gradient: stretch an empty column so the fill matches it
    canvas = im.crop((360, 0, 361, h)).resize((300 + model.width, h))
    canvas.paste(model, (300, 0))
    canvas.paste(legend, (0, 0))
    canvas.save(OUT / out)
    print(out, canvas.size)
