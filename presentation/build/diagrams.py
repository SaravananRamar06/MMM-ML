"""Draw the deck's engineering diagrams from the real bracket geometry.

Input: planform.json (triangles + edges of the z = 0 face of Rib Bracket.STEP,
meshed with gmsh 4.15.2, coordinates in mm). Output: PNGs in ../assets/.
Run: python diagrams.py planform.json
"""
import json
import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.collections import PolyCollection
from matplotlib.patches import Arc, Circle, FancyArrowPatch, Polygon, Rectangle

for f in font_manager.findSystemFonts():
    if "Carlito" in f:
        font_manager.fontManager.addfont(f)
plt.rcParams["font.family"] = "Carlito"

INK = "#14213D"
STEEL = "#2F5D8A"
ORANGE = "#E8590C"
FILL = "#DCE4EC"
MUTED = "#6B7785"
LINE = "#9AA6B2"

OUT = Path(__file__).resolve().parent.parent / "assets"
OUT.mkdir(exist_ok=True)
geo = json.load(open(sys.argv[1]))


def bracket(ax, fill=FILL):
    ax.add_collection(PolyCollection(geo["tris"], facecolors=fill, edgecolors=fill, linewidths=0.3))
    for pts in geo["edges"].values():
        xs, ys = zip(*pts)
        ax.plot(xs, ys, color=INK, lw=1.6, solid_capstyle="round")


def arrow(ax, p0, p1, color, lw=2.6, ms=18, style="-|>"):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle=style, mutation_scale=ms, color=color, lw=lw,
                                 shrinkA=0, shrinkB=0, zorder=6))


def dim(ax, p0, p1, text, off=(0, 0), rot=0, color=MUTED):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="<->", mutation_scale=10, color=color, lw=1.0))
    mx, my = (p0[0] + p1[0]) / 2 + off[0], (p0[1] + p1[1]) / 2 + off[1]
    ax.text(mx, my, text, ha="center", va="center", fontsize=12, color=color, rotation=rotation_safe(rot),
            bbox=dict(fc="white", ec="none", pad=1.5))


def rotation_safe(r):
    return r


def hatch_wall(ax, y0, y1, x=210.0, w=9):
    ax.add_patch(Rectangle((x, y0), w, y1 - y0, fc="white", ec=INK, lw=1.2, hatch="////", zorder=4))


def save(fig, name):
    fig.savefig(OUT / name, dpi=220, transparent=True, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)


# ---------------------------------------------------------------- CAD planform
fig, ax = plt.subplots(figsize=(7.2, 7.0))
bracket(ax)
ax.add_patch(Circle((0, 0), 5, fc="white", ec=INK, lw=1.6, zorder=5))
dim(ax, (-21.5, -52), (210, -52), "231.5 mm")
ax.plot([-21.5, -21.5], [-40, -55], color=LINE, lw=0.8)
ax.plot([210, 210], [-40, -55], color=LINE, lw=0.8)
dim(ax, (228, -37), (228, 193), "230 mm", rot=90, off=(0, 0))
ax.plot([213, 231], [-37, -37], color=LINE, lw=0.8)
ax.plot([213, 231], [193, 193], color=LINE, lw=0.8)
ax.annotate("Ø10 mm bore\n(load point)", xy=(-3.5, 3.5), xytext=(-40, 95), fontsize=13, color=INK,
            ha="center", arrowprops=dict(arrowstyle="-", color=INK, lw=1))
ax.annotate("Mounting face\n50 × 40 mm", xy=(207, 168), xytext=(150, 222), fontsize=13, color=INK,
            ha="center", arrowprops=dict(arrowstyle="-", color=INK, lw=1))
ax.annotate("Mounting face\n50 × 40 mm", xy=(207, -12), xytext=(150, 52), fontsize=13, color=INK,
            ha="center", arrowprops=dict(arrowstyle="-", color=INK, lw=1))
ax.text(95, -12, "Lower arm", fontsize=13, color=STEEL, ha="center", va="center", weight="bold")
ax.text(70, 95, "Diagonal arm", fontsize=13, color=STEEL, ha="center", va="center", weight="bold",
        rotation=39)
ax.set_aspect("equal")
ax.set_xlim(-75, 240)
ax.set_ylim(-62, 245)
ax.axis("off")
save(fig, "cad_planform.png")

# ---------------------------------------------------------------- force diagram
fig, ax = plt.subplots(figsize=(8.6, 7.0))
bracket(ax)
ax.add_patch(Circle((0, 0), 5, fc="white", ec=INK, lw=1.4, zorder=5))
ax.add_patch(Arc((0, 0), 10, 10, theta1=0, theta2=180, color=ORANGE, lw=4.5, zorder=7))
hatch_wall(ax, -37, 13)
hatch_wall(ax, 143, 193)
# applied force on the upper half of the bore
arrow(ax, (0, 6), (0, 62), ORANGE, lw=3.6, ms=26)
ax.text(-6, 66, "F", fontsize=24, color=ORANGE, weight="bold", ha="right", style="italic")
ax.text(-27, 40, "bearing load on the\nupper half of the bore", fontsize=12, color=ORANGE, ha="right", va="top")
# reactions
arrow(ax, (232, 168), (232, 128), INK, lw=2.0, ms=16)
arrow(ax, (232, -12), (232, -52), INK, lw=2.0, ms=16)
ax.text(238, 140, "R", fontsize=15, color=INK, style="italic")
ax.text(238, -40, "R", fontsize=15, color=INK, style="italic")
ax.text(250, -62, "ΣR = F", fontsize=13, color=INK, ha="center")
ax.add_patch(Arc((222, 78), 60, 60, theta1=-65, theta2=65, color=INK, lw=1.8))
arrow(ax, (234.6, 105.2), (230.5, 107.5), INK, lw=1.6, ms=14)
ax.text(258, 78, "M = F × 210 mm", fontsize=13, color=INK, va="center")
ax.text(186, 78, "Fixed support\n(spar mounting\nfaces)", fontsize=12, color=MUTED, ha="center", va="center")
# lever arm
dim(ax, (0, -62), (210, -62), "lever arm 210 mm", color=STEEL)
ax.plot([0, 0], [-8, -66], color=LINE, lw=0.8, ls=(0, (3, 3)))
ax.plot([210, 210], [-40, -66], color=LINE, lw=0.8, ls=(0, (3, 3)))
# member actions
ax.text(110, -12, "lower arm: tension", fontsize=12, color=STEEL, ha="center", va="center", weight="bold")
ax.text(88, 115, "diagonal arm: compression", fontsize=12, color=STEEL, ha="center", va="center",
        weight="bold", rotation=39)
# axes triad
arrow(ax, (-88, -60), (-63, -60), MUTED, lw=1.4, ms=12)
arrow(ax, (-88, -60), (-88, -35), MUTED, lw=1.4, ms=12)
ax.text(-59, -60, "X", fontsize=12, color=MUTED, va="center")
ax.text(-88, -30, "Y", fontsize=12, color=MUTED, ha="center")
ax.text(-88, -80, "Z: 40 mm thick", fontsize=11, color=MUTED, ha="left")
ax.set_aspect("equal")
ax.set_xlim(-100, 330)
ax.set_ylim(-88, 205)
ax.axis("off")
save(fig, "forces.png")

# ---------------------------------------------------------------- bore detail (two panels)
fig, axes = plt.subplots(1, 2, figsize=(9.0, 4.4))
for k, ax in enumerate(axes):
    ax.add_patch(Rectangle((-14, -14), 28, 28, fc=FILL, ec="none"))
    ax.add_patch(Circle((0, 0), 5, fc="white", ec=INK, lw=1.6, zorder=3))
    if k == 0:
        # full bore loaded: arrows all around the circumference
        for a in range(0, 360, 30):
            t = math.radians(a)
            x0, y0 = 5 * math.cos(t), 5 * math.sin(t)
            arrow(ax, (x0, y0), (x0, y0 + 3.2), ORANGE if y0 > 0.1 else MUTED, lw=1.6, ms=10)
        ax.add_patch(Arc((0, 0), 10, 10, theta1=180, theta2=360, color=MUTED, lw=3.5, zorder=4))
        ax.add_patch(Arc((0, 0), 10, 10, theta1=0, theta2=180, color=ORANGE, lw=3.5, zorder=4))
        ax.set_title("Load on the whole bore", fontsize=15, color=MUTED, pad=8)
        ax.text(0, -17.5, "lower half is pulled into the hole", fontsize=12, color=MUTED, ha="center")
    else:
        ax.add_patch(Circle((0, 0.55), 4.4, fc=STEEL, ec="none", alpha=0.9, zorder=4))
        ax.text(0, 0.4, "pin", fontsize=13, color="white", ha="center", va="center", weight="bold", zorder=5)
        for a in range(30, 180, 30):
            t = math.radians(a)
            x0, y0 = 5 * math.cos(t), 5 * math.sin(t)
            arrow(ax, (x0, y0), (x0, y0 + 3.2), ORANGE, lw=1.8, ms=10)
        ax.add_patch(Arc((0, 0), 10, 10, theta1=0, theta2=180, color=ORANGE, lw=4, zorder=6))
        ax.text(0, -6.9, "gap: no contact", fontsize=12, color=MUTED, ha="center")
        ax.set_title("Load on the upper half only", fontsize=15, color=ORANGE, pad=8, weight="bold")
        ax.text(0, -17.5, "pin presses where the load pushes it", fontsize=12, color=INK, ha="center")
    ax.set_aspect("equal")
    ax.set_xlim(-14, 14)
    ax.set_ylim(-19.5, 14)
    ax.axis("off")
save(fig, "bore_detail.png")


# ---------------------------------------------------------------- material curves
def curve_axes(figsize=(4.6, 3.4)):
    fig, ax = plt.subplots(figsize=figsize)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(INK)
        ax.spines[s].set_linewidth(1.2)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel("strain  ε", fontsize=14, color=INK)
    ax.set_ylabel("stress  σ", fontsize=14, color=INK)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.15)
    return fig, ax


eps_y = 0.12
sig_y = 0.55

fig, ax = curve_axes()
e0 = [i / 400 for i in range(401)]
ax.plot(e0, [min(x * sig_y / eps_y, 9) if x <= eps_y else sig_y + 0.45 * (x - eps_y) ** 0.45 for x in e0],
        color=LINE, lw=1.6, ls=(0, (4, 3)))
ax.text(0.98, 0.84, "real alloy yields", fontsize=12, color=MUTED, ha="right")
ax.plot([0, 1.1 * eps_y / sig_y], [0, 1.1], color=STEEL, lw=3.0)
ax.text(0.30, 1.02, "σ = E·ε", fontsize=16, color=INK, weight="bold")
ax.text(0.30, 0.86, "no yield cap", fontsize=12, color=STEEL)
save(fig, "curve_el.png")

fig, ax = curve_axes()
e = [i / 400 for i in range(401)]


def jc(x, scale):
    if x <= eps_y:
        return x * sig_y / eps_y * scale
    p = x - eps_y
    return scale * (sig_y + 0.45 * p ** 0.45)


e = [i / 400 for i in range(0, 281)]
for scale, col, lab in ((1.14, ORANGE, "faster\nloading"), (1.0, STEEL, "reference"), (0.82, LINE, "hotter")):
    ax.plot(e, [jc(x, scale) for x in e], color=col, lw=2.6 if scale == 1.0 else 1.8)
    ax.text(0.72, jc(0.70, scale), lab, fontsize=11.5, color=col if col != LINE else MUTED, ha="left",
            va="center", linespacing=0.9)
ax.text(0.05, 1.05, "yield  →  hardening", fontsize=13, color=INK, weight="bold")
save(fig, "curve_jcb.png")

fig, ax = curve_axes()
pts_x = [0.0, eps_y, 0.2, 0.32, 0.46, 0.62, 0.8, 0.98]
pts_y = [0.0, sig_y] + [jc(x, 1.0) * (1 + 0.03 * ((-1) ** i)) for i, x in enumerate(pts_x[2:])]
ax.plot(pts_x, pts_y, color=STEEL, lw=2.6)
ax.plot(pts_x[1:], pts_y[1:], "o", ms=8, mfc="white", mec=ORANGE, mew=2.2)
ax.text(0.05, 1.05, "our curve, point by point", fontsize=13, color=INK, weight="bold")
ax.text(0.5, 0.36, "(plastic strain, stress)\npairs from our model", fontsize=12, color=MUTED)
save(fig, "curve_jcu.png")

print("written:", sorted(p.name for p in OUT.glob("*.png")))
