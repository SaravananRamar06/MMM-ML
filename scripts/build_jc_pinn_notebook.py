"""Package the tested JC-PINN module, its frozen settings and the verified result into one notebook.

The notebook runs on Google Colab, Kaggle or a local Jupyter kernel. It embeds:
  src/jc_pinn.py, configs/jc_pinn.json, data/split.json        (code and protocol)
  <run>/equation.json and the selected settings / fingerprints  (verified reference result)
Usage: python scripts/build_jc_pinn_notebook.py [reports/jc_pinn_YYYYMMDD]
"""
import json
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
run_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else root / 'reports/jc_pinn_20261107'
result = json.loads((run_dir / 'results.json').read_text())
equation = json.loads((run_dir / 'equation.json').read_text())
reference = dict(source=str(run_dir.relative_to(root)), selected=result['selected'], fingerprints=result['fingerprints'],
                 test={k: {m: v[m] for m in ('mean_rmse', 'median_rmse', 'worst_rmse', 'mean_mae', 'mean_nrmse')}
                       for k, v in result['test'].items()},
                 cv=result['selection']['selected_trial']['cv']['mean_rmse'],
                 group_mean=result['selection']['selected_trial']['group_mean_rmse'],
                 equation_only_constants=result['equation_only_constants'], jc_pinn_constants=result['jc_pinn_constants'])
ctrl = json.loads((run_dir / 'control_no_equation.json').read_text()) if (run_dir / 'control_no_equation.json').exists() else None
files = {p: (root / p).read_text(encoding='utf-8') for p in ['src/jc_pinn.py', 'configs/jc_pinn.json', 'data/split.json']}
files['reference/equation.json'] = json.dumps(equation)
files['reference/summary.json'] = json.dumps(reference)


def md(s):
    return dict(cell_type='markdown', metadata={}, source=s.strip('\n').splitlines(keepends=True))


def code(s):
    return dict(cell_type='code', metadata={}, execution_count=None, outputs=[], source=s.strip('\n').splitlines(keepends=True))


sel = result['selected']
t = reference['test']
cells = [md(rf'''
# JC-PINN: your Johnson–Cook equation as the governing law of the AlSi10Mg model

This notebook trains and uses a **physics-informed neural network whose backbone is your customised
Johnson–Cook equation (Equation 1)**:

$$\sigma_{{JC}}=\left[A-B\,\varepsilon_p^{{\,n}}\right]\left[1+C\ln\dot\varepsilon^*\right]\left[1-T^{{*m}}\right]\left[\frac{{G}}{{G_0}}\right]^{{q}}\left[1-\phi\right]^{{r}}$$

with $\dot\varepsilon^*=\dot\varepsilon/10^{{-5}}\,\mathrm{{s^{{-1}}}}$, $T^*=(T-30)/(600-30)$ (°C), $G_0=25300$ MPa,
$\phi=1-\rho/2700$, and $\varepsilon_p$ = the axial strain `E11`. The model is

$$\hat\sigma=\sigma_{{JC}}(A,B,n,C,m,q,r)\cdot\exp\!\big(\delta(T,\log_{{10}}\dot\varepsilon,\rho,G,\varepsilon)\big)$$

where $\delta$ is a small 5-16-16-1 tanh network (385 weights) that starts at zero, so the untrained model **is**
Equation 1. Training minimises the data error plus a physics residual of Equation 1 at collocation points.
The selected setting was **{sel['physics']} physics, λ = {sel['lambda_phys']:g}, {sel['theta_mode']} constants**.

**Three modes** (set `MODE` in the next cell):

| Mode | Needs data? | Time on Colab CPU | What it does |
|---|---|---|---|
| `PREDICT` | no | seconds | Uses the verified saved equation to plot curves for any condition (e.g. 4 % porosity). |
| `FAST` | yes | ~2–5 min | Re-fits the selected setting on the 36 training cases, locks it, then scores the 37 test cases once. |
| `FULL` | yes | ~1–2 h (2 CPUs) | Re-runs the whole training-only selection (14 settings × 12 splits × 3 seeds), then the same final steps. |

**Data.** The professor's folder `TEAM_8_extracted_results_set_1` (with `simulation_matrix.csv` and
`simulation_XXXX/STR_STR.OUT`), or its ZIP.
* *Colab:* put it anywhere in **My Drive**. If it was shared with you, right-click it → *Organise → Add shortcut to My Drive*. The notebook mounts Drive and finds it.
* *Kaggle:* upload the folder or ZIP as a Dataset, then *Add Input*. The notebook searches `/kaggle/input`.
* *Local Jupyter:* put the folder next to this notebook or set `DATA_PATH`.

The notebook checks that the curves it reads match the verified run's curve fingerprints.

Reference result ({reference['source']}): test mean curve RMSE **{t['jc_pinn']['mean_rmse']:.4f}** (JC-PINN) vs
**{t['equation_only']['mean_rmse']:.3f}** (Equation 1 alone) and {t['lookup']['mean_rmse']:.3f} (curve-copy baseline), in source stress units (MPa inferred).
''' + (f'''
**Honest finding.** None of the physics-penalty settings improved the training-side score, so the selected model uses
Equation 1 as its structure only (λ = 0). A post-hoc control with Equation 1 switched off but identical training did
better: test {ctrl['control']['test']['mean_rmse']:.4f} vs {ctrl['jc_pinn']['test']['mean_rmse']:.4f}, unseen-group mean
{ctrl['control']['group_mean_rmse']:.2f} vs {ctrl['jc_pinn']['group_mean_rmse']:.2f}. Equation 1's separable form gives every
condition the same curve shape, so it does not add accuracy here; it adds seven interpretable constants.
See `reports/jc_pinn_20261107/README.md`.
''' if ctrl else '')),
         code('''
MODE = 'PREDICT'          # 'PREDICT', 'FAST' or 'FULL'
DATA_PATH = ''            # optional: folder or ZIP; leave '' to search automatically
WORKERS = None            # None = all CPU cores
'''),
         code(f'''
import importlib.util, json, os, sys, time
from pathlib import Path

def has_module(name):
    try:
        return importlib.util.find_spec(name) is not None
    except (ImportError, ValueError):     # e.g. parent package 'google' missing outside Colab
        return False

IN_COLAB = 'COLAB_RELEASE_TAG' in os.environ or has_module('google.colab')
IN_KAGGLE = 'KAGGLE_KERNEL_RUN_TYPE' in os.environ or Path('/kaggle/input').exists()
WORK = Path('/content/jc_pinn') if IN_COLAB else Path('/kaggle/working/jc_pinn') if IN_KAGGLE else Path.cwd() / 'jc_pinn_work'
print('Platform:', 'Colab' if IN_COLAB else 'Kaggle' if IN_KAGGLE else 'local', '| work folder:', WORK)

missing = [m for m in ('torch', 'scipy', 'sklearn', 'matplotlib') if not has_module(m)]
if missing:   # Colab and Kaggle already include all four
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q', 'torch', 'scipy', 'scikit-learn', 'matplotlib'])

EMBEDDED = {files!r}
for rel, text in EMBEDDED.items():
    p = WORK / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding='utf-8')
sys.path.insert(0, str(WORK / 'src'))
import numpy as np
import jc_pinn
importlib.reload(jc_pinn)
REF = json.loads((WORK / 'reference/summary.json').read_text())
EQ = json.loads((WORK / 'reference/equation.json').read_text())
print('Selected setting:', REF['selected'])
print('Equation 1 constants inside the JC-PINN:', {{k: round(v, 5) for k, v in EQ['theta'].items()}})
'''),
         md('''
## Predict curves from the saved equation (no data needed)

`predict_curve` evaluates the saved equation with NumPy only. Give either porosity `phi` (fraction) or
`density`; G is in MPa. Data cover 30–200 °C, rates 1e-5 to 1e-3 s⁻¹, φ = 0–7.85 % and E11 up to 0.0999.
There is no data between 200 and 300 °C, and the selected model has no physics penalty there (λ = 0), so treat
those curves as **unvalidated extrapolation**.
'''),
         code('''
import matplotlib.pyplot as plt

def predict_curve(T, rate, phi=None, density=None, G=24541.0, eq=None, points=120):
    """Return (E11, Svm, Equation-1 backbone, correction factor) for one condition."""
    eq = eq or EQ
    rho = density if density is not None else 2700.0 * (1 - (0.04 if phi is None else phi))
    e = np.linspace(0.0002, 0.0999, points)
    X5 = np.c_[np.tile([T, np.log10(rate), rho, G], (points, 1)), e]
    s, base, d = jc_pinn.equation_predict(eq, X5, parts=True)
    return e, s, base, np.exp(d)

fig, axes = plt.subplots(1, 3, figsize=(14, 4), sharey=True)
for ax, rate in zip(axes, (1e-5, 1e-4, 1e-3)):
    for T, col in ((30, 'tab:blue'), (100, 'tab:green'), (200, 'tab:red'), (300, 'tab:gray')):
        e, s, base, f = predict_curve(T, rate, phi=0.04)
        ax.plot(e, s, '--' if T > 200 else '-', color=col, label=f'{T} °C' + (' (extrapolation)' if T > 200 else ''))
    ax.set(title=f'φ = 4 %, rate {rate:g} /s', xlabel='E11 (axial strain)'); ax.grid(alpha=.3)
axes[0].set_ylabel('Predicted Svm (MPa, inferred)'); axes[0].legend(fontsize=8); plt.show()

e, s, base, f = predict_curve(100, 1e-4, phi=0.04)
print('Example: 100 °C, 1e-4 /s, phi = 4 %, G = 24541 MPa')
for k in (0, 30, 60, 90, 119):
    print(f'  E11 = {e[k]:.4f}   Svm = {s[k]:8.3f}   Equation 1 alone = {base[k]:8.3f}   correction x{f[k]:.4f}')
'''),
         md('''
## Find the professor's data (FAST / FULL)
'''),
         code('''
import zipfile

def find_data(hint=''):
    if hint:
        p = Path(hint)
        if p.is_dir() and (p / 'simulation_matrix.csv').exists():
            return p
        if p.suffix == '.zip' and p.exists():
            return unzip(p)
        raise FileNotFoundError(hint)
    roots = []
    if IN_COLAB:
        from google.colab import drive
        drive.mount('/content/drive')
        roots += [Path('/content/drive/MyDrive'), Path('/content/drive/Shareddrives')]
    if IN_KAGGLE:
        roots.append(Path('/kaggle/input'))
    roots += [Path.cwd(), Path.cwd().parent]
    for root in roots:
        for depth in range(5):
            pattern = '/'.join(['*'] * depth + ['simulation_matrix.csv']) if depth else 'simulation_matrix.csv'
            hits = sorted(root.glob(pattern)) if root.exists() else []
            hits = [h.parent for h in hits if (h.parent / 'simulation_0001').exists() or any(h.parent.glob('simulation_0*'))]
            if hits:
                return hits[0]
        for z in (sorted(root.glob('TEAM_8*.zip')) + sorted(root.glob('*/TEAM_8*.zip'))) if root.exists() else []:
            return unzip(z)
    raise FileNotFoundError('TEAM_8_extracted_results_set_1 not found: set DATA_PATH')

def unzip(z):
    target = WORK / 'raw'
    split = json.loads((WORK / 'data/split.json').read_text())
    with zipfile.ZipFile(z) as archive:
        names = [n.replace('\\\\', '/') for n in archive.namelist()]
        for rel in ['simulation_matrix.csv'] + [f'simulation_{i:04d}/STR_STR.OUT' for i in split['train'] + split['test']]:
            match = [archive.namelist()[k] for k, n in enumerate(names) if n == rel or n.endswith('/' + rel)]
            if len(match) != 1:
                raise ValueError(f'{rel}: {len(match)} matches in {z}')
            out = target / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(archive.read(match[0]))
    return target

if MODE in ('FAST', 'FULL'):
    RAW = find_data(DATA_PATH)
    print('Data folder:', RAW)
else:
    print('PREDICT mode: no data needed. Set MODE = "FAST" or "FULL" above to train.')
'''),
         md('''
## Train, lock, then test (FAST / FULL)

The code reads the 36 training histories, fits (FAST) or selects and fits (FULL) the model, writes
`equation.json` and `selection_lock.json`, and **only then** reads the 37 test histories. Results go to a
new time-stamped folder: Google Drive `MyDrive/MMM-ML/jc_pinn_runs/` on Colab, `/kaggle/working/jc_pinn_runs/`
on Kaggle. Small numerical differences from the reference are expected on other hardware, because L-BFGS
amplifies last-digit differences between CPU math libraries.
'''),
         code('''
if MODE in ('FAST', 'FULL'):
    base = (Path('/content/drive/MyDrive/MMM-ML/jc_pinn_runs') if IN_COLAB else
            Path('/kaggle/working/jc_pinn_runs') if IN_KAGGLE else WORK / 'runs')
    OUT = base / time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())
    t0 = time.time()
    result = jc_pinn.run(WORK, RAW, OUT, mode=MODE.lower(), workers=WORKERS,
                         selected=dict(selected=REF['selected']) if MODE == 'FAST' else None,
                         expected=REF['fingerprints'])
    EQ = json.loads((OUT / 'equation.json').read_text())
    print(f'Finished in {time.time() - t0:.0f} s. Saved to {OUT}')
    print(f"{'model':<16}{'this run':>12}{'reference':>12}")
    for k in ('jc_pinn', 'equation_only', 'lookup'):
        print(f"{k:<16}{result['test'][k]['mean_rmse']:>12.4f}{REF['test'][k]['mean_rmse']:>12.4f}")
    from IPython.display import Image, display
    for name in ('test_comparison.png', 'condition_holdouts.png', 'study_point_curves.png'):
        if (OUT / name).exists():
            display(Image(filename=str(OUT / name)))
'''),
         md(r'''
## How to read the result

* **Equation 1 constants** (`EQ['theta']`): A, B, n set the strain-softening term, C the rate sensitivity, m the
  thermal softening, q the shear-modulus effect and r the porosity effect. They stay inside physical bounds:
  A − Bεⁿ > 0 and C, q, r ≥ 0.
* **Correction factor** exp(δ): how much the data deviates from Equation 1 at that point. Equation 1 is a product of
  separate terms, so it gives every condition the same curve shape. The data's shape changes with temperature
  and rate, and the network learns that part.
* **Limits:** the 37 test cases were used in earlier project stages, so this is not a blind test. Stress
  units are inferred as MPa. The model describes the supplied simulations, not experiments. Above 200 °C there
  is no data. Case 60 (200 °C, 1e-5 s⁻¹) collapses irregularly and remains the hardest case.
''')]
for i, c in enumerate(cells):
    c['id'] = f'jcpinn-{i}'
nb = dict(cells=cells, nbformat=4, nbformat_minor=5,
          metadata=dict(kernelspec=dict(name='python3', language='python', display_name='Python 3'),
                        language_info=dict(name='python')))
out = root / 'notebooks/jc_pinn_colab.ipynb'
out.write_text(json.dumps(nb, indent=1) + '\n', encoding='utf-8')
print(out)
