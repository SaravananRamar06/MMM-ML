"""EDA figure, model GIFs and the blueprint background for the deck.

Inputs (presentation/source/model/): manifest.json (case conditions), test_predictions.csv and
cv_predictions.csv (true Svm on the 120-point E11 grid for the 37 test / 36 training cases, plus the
JC-PINN predictions), training_trace_member0.json (recorded JC-PINN training run, member 0).
All model outputs come from the locked JC-PINN run reports/jc_pinn_20261107 (branch
claude/tender-hamilton-vd2qvm). Nothing is refitted here.
Run: python data_figures.py planform.json
"""
import csv
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import animation, font_manager

for f in font_manager.findSystemFonts():
    if "Carlito" in f:
        font_manager.fontManager.addfont(f)
plt.rcParams["font.family"] = "Carlito"

NAVY, STEEL, ORANGE, CYAN, MUTED, LINE, PALE, GREEN = (
    "#0B2545", "#134074", "#F28C28", "#13A4D8", "#5C6B7A", "#A9B8C6", "#D9E6F2", "#2BB673")
TEMP_COL = {30.0: CYAN, 100.0: STEEL, 200.0: ORANGE}
SUP = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")


def rate(lr):
    return "10" + str(int(lr)).translate(SUP) + " /s"


HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "source" / "model"
OUT = HERE.parent / "assets"

man = {m["id"]: m for m in json.load(open(SRC / "manifest.json"))}
truth, pred, split = {}, {}, {}
for f, part in (("test_predictions.csv", "test"), ("cv_predictions.csv", "train")):
    for r in csv.DictReader(open(SRC / f)):
        i = int(r["id"])
        truth.setdefault(i, []).append((float(r["E11"]), float(r["Svm"])))
        if part == "test":
            pred.setdefault(i, []).append((float(r["E11"]), float(r["JC_PINN"]), float(r["equation_only"])))
        split[i] = part
grid = np.array([e for e, _ in sorted(truth[1])])
T = {i: np.array([s for _, s in sorted(v)]) for i, v in truth.items()}
P = {i: np.array([p for _, p, _ in sorted(v)]) for i, v in pred.items()}
EQ = {i: np.array([q for _, _, q in sorted(v)]) for i, v in pred.items()}


def style(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=12)
    ax.grid(color=PALE, lw=0.8)
    ax.set_axisbelow(True)


# ------------------------------------------------------------------ EDA curves
fig, axes = plt.subplots(1, 2, figsize=(11, 4.3))
ax = axes[0]
for i, y in T.items():
    m = man[i]
    if i == 60:
        continue
    ax.plot(grid * 100, y, color=TEMP_COL[m["temperature"]], lw=1.0, alpha=0.55)
ax.plot(grid * 100, T[60], color=NAVY, lw=2.0, ls=(0, (4, 2)))
ax.annotate("case 60 (200 °C, 10⁻⁵ /s):\nthe only case of its kind", xy=(2.6, T[60][31]), xytext=(0.2, 18),
            fontsize=12, color=NAVY, arrowprops=dict(arrowstyle="-", color=NAVY, lw=1))
for t, c in TEMP_COL.items():
    ax.plot([], [], color=c, lw=3, label=f"{int(t)} °C")
ax.legend(frameon=False, fontsize=12, loc="upper right")
ax.set_title("All 73 curves, coloured by temperature", fontsize=14, color=NAVY, loc="left")
ax.set_xlabel("axial strain E11 (%)", fontsize=13, color=NAVY)
ax.set_ylabel("von Mises stress Svm (MPa)", fontsize=13, color=NAVY)
ax.set_ylim(0, 170)
style(ax)

ax = axes[1]
for lr, c in ((-5.0, LINE), (-4.0, STEEL), (-3.0, ORANGE)):
    i = next(k for k, m in man.items() if m["temperature"] == 30.0 and m["log10_strain_rate"] == lr
             and m["density"] == 2700.0 and m["shear_modulus"] == 25300.0)
    ax.plot(grid * 100, T[i], color=c, lw=2.6, label=rate(lr))
ax.legend(frameon=False, fontsize=12, title="strain rate", title_fontsize=12, loc="upper right")
ax.set_title("Strain-rate effect at 30 °C (ρ = 2700, G = 25300)", fontsize=14, color=NAVY, loc="left")
ax.set_xlabel("axial strain E11 (%)", fontsize=13, color=NAVY)
ax.set_ylim(0, 170)
style(ax)
fig.tight_layout()
fig.savefig(OUT / "eda_curves.png", dpi=200, transparent=True)
plt.close(fig)

# ------------------------------------------------------------------ training GIF
tr = json.load(open(SRC / "training_trace_member0.json"))
e = np.array(tr["E11"]) * 100
hist = np.array([[h[0], h[2]] for h in tr["hist"]], dtype=float)
snaps = tr["snaps"]
cols = [CYAN, STEEL, ORANGE, NAVY]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.6, 4.0), gridspec_kw={"width_ratios": [1.25, 1]})
lines = []
for k, (case, y) in enumerate(zip(tr["cases"], tr["truth"])):
    a1.plot(e, y, "o", ms=3.2, color=cols[k], alpha=0.45)
    ln, = a1.plot(e, snaps[0]["curves"][k], color=cols[k], lw=2.4,
                  label=f"{int(case['T'])} °C, {rate(case['lr'])}")
    lines.append(ln)
a1.set_xlabel("axial strain E11 (%)", fontsize=12, color=NAVY)
a1.set_ylabel("Svm (MPa)", fontsize=12, color=NAVY)
a1.legend(frameon=False, fontsize=10, loc="lower left")
style(a1)
title = a1.set_title("Adam · step 0000 · loss 0.0000", fontsize=13, color=NAVY, loc="left")
a1.text(0.0, -0.3, "dots: simulation   lines: JC-PINN while training", transform=a1.transAxes, fontsize=11, color=MUTED)
x = np.arange(len(hist))
a2.semilogy(x, hist[:, 1], color=LINE, lw=1.5)
dot, = a2.semilogy([0], [hist[0, 1]], "o", color=ORANGE, ms=9)
a2.set_xlabel("recorded step", fontsize=12, color=NAVY)
a2.set_title("training loss", fontsize=13, color=NAVY, loc="left")
style(a2)
fig.tight_layout()
hist_steps = [h[0] for h in tr["hist"]]


def upd(f):
    s = snaps[min(f, len(snaps) - 1)]
    for k, ln in enumerate(lines):
        ln.set_ydata(s["curves"][k])
    title.set_text(f"{'Adam' if s['phase'] == 'adam' else 'L-BFGS'}  ·  step {s['step']}  ·  loss {s['loss']:.4f}")
    j = int(np.argmin([abs(hs - s["step"]) if h[1] == s["phase"] else 1e9 for hs, h in zip(hist_steps, tr["hist"])]))
    dot.set_data([j], [hist[j, 1]])
    return lines + [dot, title]


frames = list(range(len(snaps))) + [len(snaps) - 1] * 6
animation.FuncAnimation(fig, upd, frames=frames, blit=False).save(OUT / "gif_training.gif", writer=animation.PillowWriter(fps=3), dpi=100)
plt.close(fig)

# ------------------------------------------------------------------ test GIF
test_ids = sorted(P)
allt = np.concatenate([T[i] for i in test_ids])
allp = np.concatenate([P[i] for i in test_ids])
r2 = 1 - np.sum((allt - allp) ** 2) / np.sum((allt - allt.mean()) ** 2)
fig, (b1, b2) = plt.subplots(1, 2, figsize=(9.6, 4.0), gridspec_kw={"width_ratios": [1.25, 1]})
tl, = b1.plot(grid * 100, T[test_ids[0]], "o", ms=3.4, color=NAVY, alpha=0.5, label="simulation (unseen)")
pl, = b1.plot(grid * 100, P[test_ids[0]], color=ORANGE, lw=2.6, label="JC-PINN prediction")
ql, = b1.plot(grid * 100, EQ[test_ids[0]], color=LINE, lw=1.6, ls=(0, (4, 2)), label="JC equation alone")
b1.set_xlabel("axial strain E11 (%)", fontsize=12, color=NAVY)
b1.set_ylabel("Svm (MPa)", fontsize=12, color=NAVY)
b1.set_ylim(0, 175)
b1.legend(frameon=False, fontsize=10, loc="lower left")
style(b1)
ttl = b1.set_title("case 00: 000 °C, 10⁻⁵ /s · RMSE 0.00 MPa", fontsize=13, color=NAVY, loc="left")
b2.plot([0, 170], [0, 170], color=LINE, lw=1)
sc = b2.scatter([], [], s=5, color=STEEL, alpha=0.6)
b2.set_xlim(0, 170)
b2.set_ylim(0, 170)
b2.set_xlabel("simulated Svm (MPa)", fontsize=12, color=NAVY)
b2.set_ylabel("predicted Svm (MPa)", fontsize=12, color=NAVY)
style(b2)
ptxt = b2.set_title("37 of 37 unseen cases · R² = 0.0000", fontsize=13, color=NAVY, loc="left")
fig.tight_layout()


def upd2(f):
    k = min(f, len(test_ids) - 1)
    i = test_ids[k]
    m = man[i]
    tl.set_ydata(T[i])
    pl.set_ydata(P[i])
    ql.set_ydata(EQ[i])
    rmse = np.sqrt(np.mean((T[i] - P[i]) ** 2))
    ttl.set_text(f"case {i}: {int(m['temperature'])} °C, {rate(m['log10_strain_rate'])}  ·  RMSE {rmse:.2f} MPa")
    pts = np.c_[np.concatenate([T[j] for j in test_ids[:k + 1]]), np.concatenate([P[j] for j in test_ids[:k + 1]])]
    sc.set_offsets(pts)
    ptxt.set_text(f"{k + 1} of 37 unseen cases" + (f"  ·  R² = {r2:.4f}" if k == len(test_ids) - 1 else ""))
    return [tl, pl, ql, sc, ttl, ptxt]


frames = list(range(len(test_ids))) + [len(test_ids) - 1] * 5
animation.FuncAnimation(fig, upd2, frames=frames, blit=False).save(OUT / "gif_test.gif", writer=animation.PillowWriter(fps=1.5), dpi=100)
plt.close(fig)
print("pooled R2", r2)

# ------------------------------------------------------------------ blueprint background
geo = json.load(open(sys.argv[1]))
fig = plt.figure(figsize=(13.333, 7.5), dpi=150)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_facecolor(NAVY)
fig.patch.set_facecolor(NAVY)
ax.set_xlim(0, 13.333)
ax.set_ylim(0, 7.5)
for xg in np.arange(0, 13.4, 0.25):
    ax.axvline(xg, color="#16335A", lw=0.4 if round(xg * 4) % 4 else 0.9)
for yg in np.arange(0, 7.6, 0.25):
    ax.axhline(yg, color="#16335A", lw=0.4 if round(yg * 4) % 4 else 0.9)
s, ox, oy = 0.022, 8.6, 1.95
for pts in geo["edges"].values():
    xs, ys = zip(*pts)
    ax.plot([ox + s * x for x in xs], [oy + s * y for y in ys], color="#4F8FC0", lw=1.4, alpha=0.75)
c = plt.Circle((ox, oy), 5 * s, fill=False, color=ORANGE, lw=1.6)
ax.add_patch(c)
ax.annotate("", xy=(ox, oy + 1.4), xytext=(ox, oy + 0.15), arrowprops=dict(arrowstyle="-|>", color=ORANGE, lw=2))
ax.text(ox - 0.12, oy + 1.25, "F", color=ORANGE, fontsize=20, ha="right", style="italic", weight="bold")
for y0, y1 in ((-37, 13), (143, 193)):
    ax.plot([ox + 210 * s + 0.08] * 2, [oy + y0 * s, oy + y1 * s], color="#4F8FC0", lw=3, alpha=0.6)
ax.plot([ox - 21.5 * s, ox + 210 * s], [oy - 1.05] * 2, color="#4F8FC0", lw=0.8, alpha=0.6)
ax.text(ox + 94 * s, oy - 1.0, "231.5 mm", color="#4F8FC0", fontsize=11, ha="center", va="bottom", alpha=0.85)
ax.axis("off")
fig.savefig(OUT / "bg_blueprint.png", dpi=150, facecolor=NAVY)
plt.close(fig)
print("written", sorted(p.name for p in OUT.iterdir()))
