"""Build notebooks/jc_pinn_explained.ipynb: the complete, explained JC-PINN notebook.

It embeds the tested module, config, split, the verified run (equation, constants, selection summary,
control) and the 73 interpolated 120-point curves, so every explanation cell computes its numbers and
figures live, with no raw data needed. Optional final cells retrain from the professor folder.
Usage: python scripts/build_jc_pinn_explained_notebook.py [reports/jc_pinn_YYYYMMDD]
"""
import csv
import json
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
run = Path(sys.argv[1]) if len(sys.argv) > 1 else root / 'reports/jc_pinn_20261107'
R = json.loads((run / 'results.json').read_text())
CTRL = json.loads((run / 'control_no_equation.json').read_text())
man = {m['id']: m for m in json.loads((root / 'data/manifest.json').read_text())}
curves = {}
for name in ('cv_predictions.csv', 'test_predictions.csv'):
    with (run / name).open() as f:
        for r in csv.DictReader(f):
            curves.setdefault(int(r['id']), []).append(float(r['Svm']))
cases = {i: dict(T=man[i]['temperature'], lr=man[i]['log10_strain_rate'], rho=man[i]['density'], G=man[i]['shear_modulus'],
                 rows=man[i]['rows'], S=curves[i]) for i in sorted(curves)}
sel = R['selection']
summary = dict(
    selected=R['selected'], trials=[dict(candidate=t['candidate'], cv=t['cv']['mean_rmse'], groups=t['group_mean_rmse'], score=t['score'])
                                     for t in sel['trials']],
    equation_only=dict(cv=sel['equation_only']['cv']['mean_rmse'], groups=sel['equation_only']['group_mean_rmse'],
                       group_rows=[g['metrics']['mean_rmse'] for g in sel['equation_only']['groups']]),
    lookup=dict(cv=sel['lookup']['cv']['mean_rmse'], groups=sel['lookup']['group_mean_rmse'],
                group_rows=[g['metrics']['mean_rmse'] for g in sel['lookup']['groups']]),
    selected_groups=[dict(T=g['temperature'], lr=g['log10_rate'], ids=g['validation_ids'], rmse=g['metrics']['mean_rmse'])
                     for g in sel['selected_trial']['groups']],
    selected_cv=sel['selected_trial']['cv']['mean_rmse'], cv_case_rmse=sel['selected_trial']['cv']['case_rmse'],
    test=R['test'], monotonicity=R['monotonicity'], final_fit=R['final_fit'],
    single_mlp=dict(test=R['references']['single_mlp']['test']['mean_rmse'], cv=R['references']['single_mlp']['cv']['mean_rmse'],
                    groups=[g['mean_rmse'] for g in R['references']['single_mlp']['groups']]),
    ensemble_mlp=dict(test=R['references']['ensemble_mlp']['metrics']['test_mean_rmse']),
    control=CTRL, elapsed_minutes=R['elapsed_seconds'] / 60, versions=R['versions'], fingerprints=R['fingerprints'])
files = {p: (root / p).read_text(encoding='utf-8') for p in ['src/jc_pinn.py', 'configs/jc_pinn.json', 'data/split.json']}
files['reference/equation.json'] = (run / 'equation.json').read_text()
files['reference/equation_only.json'] = (run / 'equation_only.json').read_text()
files['reference/summary.json'] = json.dumps(summary)
files['reference/curves.json'] = json.dumps(cases)


def md(s):
    return dict(cell_type='markdown', metadata={}, source=s.strip('\n').splitlines(keepends=True))


def code(s):
    return dict(cell_type='code', metadata={}, execution_count=None, outputs=[], source=s.strip('\n').splitlines(keepends=True))


C = []
C.append(md(r'''
# The JC-PINN material model, explained from data to prediction

**Course:** Multiscale Modelling of Materials using Machine Learning. **Material:** additively manufactured AlSi10Mg
(aircraft wing-rib bracket). **Date of the verified run:** 7 November 2026.

This notebook is the complete account of the model. It covers what the model is, the physics it is built on,
how it was trained and chosen without looking at the test data, and what it predicts. Every number and figure below is
computed in this notebook from the saved model and the 73 simulation curves embedded in it. You can run it top to bottom
on Google Colab, Kaggle or a laptop without the raw data. Part 9 can optionally retrain everything from the professor's
folder.

| Part | What it covers |
|---|---|
| 1 | Setup |
| 2 | The data: 73 simulated stress–strain curves |
| 3 | The governing equation (our customised Johnson–Cook law) |
| 4 | Why the equation alone is not enough |
| 5 | The model: equation backbone × neural-network correction |
| 6 | The loss function and the physics (PINN) terms |
| 7 | Training and choosing the settings without seeing the test data |
| 8 | The output: test results, unseen conditions, the control experiment and predictions |
| 9 | Optional: retrain from the professor's data |
| 10 | Limits and viva questions |
'''))
C.append(md(r'''
## 1. Setup

The next cell detects the platform and writes the embedded files into a work folder:
* the model code `src/jc_pinn.py`, the frozen settings and the 36/37 case split;
* the verified run: the saved equation, the constants and the selection results;
* the 73 curves.

Colab and Kaggle already include every package needed: PyTorch, NumPy, SciPy, scikit-learn and Matplotlib.
'''))
C.append(code(f'''
import importlib, importlib.util, json, os, sys, time
from pathlib import Path

def has_module(name):
    try:
        return importlib.util.find_spec(name) is not None
    except (ImportError, ValueError):
        return False

IN_COLAB = 'COLAB_RELEASE_TAG' in os.environ or has_module('google.colab')
IN_KAGGLE = 'KAGGLE_KERNEL_RUN_TYPE' in os.environ or Path('/kaggle/input').exists()
WORK = Path('/content/jc_pinn') if IN_COLAB else Path('/kaggle/working/jc_pinn') if IN_KAGGLE else Path.cwd() / 'jc_pinn_work'
missing = [m for m in ('torch', 'scipy', 'sklearn', 'matplotlib') if not has_module(m)]
if missing:
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q', 'torch', 'scipy', 'scikit-learn', 'matplotlib'])

EMBEDDED = {files!r}
for rel, text in EMBEDDED.items():
    p = WORK / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding='utf-8')
sys.path.insert(0, str(WORK / 'src'))
import numpy as np
import matplotlib.pyplot as plt
import jc_pinn as J
importlib.reload(J)

CFG = json.loads((WORK / 'configs/jc_pinn.json').read_text())
SPLIT = json.loads((WORK / 'data/split.json').read_text())
EQ = json.loads((WORK / 'reference/equation.json').read_text())
EQ_ONLY = json.loads((WORK / 'reference/equation_only.json').read_text())
SUM = json.loads((WORK / 'reference/summary.json').read_text())
CASES = {{int(k): v for k, v in json.loads((WORK / 'reference/curves.json').read_text()).items()}}
GRID = J.strain_grid(CFG)
TRAIN, TEST = np.array(SPLIT['train']), np.array(SPLIT['test'])
cond = lambda ids: np.array([[CASES[i]['T'], CASES[i]['lr'], CASES[i]['rho'], CASES[i]['G']] for i in ids])
curv = lambda ids: np.array([CASES[i]['S'] for i in ids])
X_train, Y_train, X_test, Y_test = cond(TRAIN), curv(TRAIN), cond(TEST), curv(TEST)
plt.rcParams.update({{'figure.dpi': 110, 'axes.grid': True, 'grid.alpha': 0.3}})
print('Platform:', 'Colab' if IN_COLAB else 'Kaggle' if IN_KAGGLE else 'local', '| work folder:', WORK)
import torch, scipy, sklearn, matplotlib
print('numpy', np.__version__, '| torch', torch.__version__, '| scipy', scipy.__version__, '| sklearn', sklearn.__version__)
print(len(CASES), 'curves loaded:', len(TRAIN), 'training and', len(TEST), 'test cases')
'''))

C.append(md(r'''
## 2. The data: 73 simulated stress–strain curves

The professor supplied the folder `TEAM_8_extracted_results_set_1`. It holds a design matrix
(`simulation_matrix.csv`) and one history file `simulation_XXXX/STR_STR.OUT` per completed simulation.

* **Design:** 4 temperatures × 3 strain rates × 3 densities × 3 shear moduli = **108 planned cases**. **73** have
  outputs. There is none at 300 °C, and 8 of the 27 cases at 200 °C are missing.
* **Each file** is a time history with 16 columns. We use the axial strain `E11` as the strain and the von Mises stress
  `Svm` as the stress.
* **Equal weighting:** the files have 1,000, 10,000 or 100,000 rows, because slower rates were written with more steps.
  So that long files don't dominate, every curve is interpolated onto the same **120 strain points**
  (E11 = 0.0002 to 0.0999). Each simulation then counts the same.
* **The split:** we keep the professor's random 50/50 split by *simulation*, with seed 42: **36 training** and
  **37 test** cases. All points of one curve stay on the same side.
'''))
C.append(code(r'''
import collections
T_levels = sorted({c['T'] for c in CASES.values()})
print('Cases available per temperature:', {T: sum(c['T'] == T for c in CASES.values()) for T in T_levels})
print('Rows per file:', dict(collections.Counter(c['rows'] for c in CASES.values())))
print('Strain grid:', len(GRID), 'points from', GRID[0], 'to', GRID[-1])
print('Training IDs:', TRAIN.tolist())
print('Test IDs:    ', TEST.tolist())

fig, axes = plt.subplots(1, 3, figsize=(15, 4.2), sharey=True)
colours = {30.0: 'tab:blue', 100.0: 'tab:green', 200.0: 'tab:red'}
for ax, lr in zip(axes, (-5.0, -4.0, -3.0)):
    for i in TRAIN:
        c = CASES[i]
        if c['lr'] == lr:
            ax.plot(GRID, c['S'], color=colours[c['T']], lw=1.4, alpha=0.85)
    ax.set(title=f'Training curves, strain rate 1e{lr:g} /s', xlabel='E11 (axial strain)')
axes[0].set_ylabel('Svm (MPa, inferred)')
for T, col in colours.items():
    axes[0].plot([], [], color=col, label=f'{T:g} °C')
axes[0].legend()
plt.tight_layout(); plt.show()
'''))
C.append(md(r'''
**What to notice:**
* Every curve *falls* as strain grows. The material softens; it never hardens.
* Higher temperature gives lower stress.
* The **shape** changes with temperature and rate: some curves stay almost straight, while 200 °C at 1e-5 /s collapses.
  The table below measures that shape change as end stress ÷ start stress. Section 4 shows why it matters.
'''))
C.append(code(r'''
print(f"{'T (°C)':>7} {'rate':>6} {'cases':>6} {'end/start stress':>18}")
for T in T_levels:
    for lr in (-5.0, -4.0, -3.0):
        ids = [i for i in TRAIN if CASES[i]['T'] == T and CASES[i]['lr'] == lr]
        if ids:
            ratio = np.mean([CASES[i]['S'][-1] / CASES[i]['S'][0] for i in ids])
            print(f'{T:7g} {"1e%g" % lr:>6} {len(ids):6d} {ratio:18.3f}')
'''))

C.append(md(r'''
## 3. The governing equation: our customised Johnson–Cook law

$$
\sigma_{JC}=\underbrace{\left[A-B\,\varepsilon^{\,n}\right]}_{\text{strain softening}}
\;\underbrace{\left[1+C\ln\dot\varepsilon^*\right]}_{\text{strain rate}}
\;\underbrace{\left[1-T^{*m}\right]}_{\text{temperature}}
\;\underbrace{\left[\tfrac{G}{G_0}\right]^{q}}_{\text{shear modulus}}
\;\underbrace{\left[1-\phi\right]^{r}}_{\text{porosity}}
$$

| Quantity | Definition used | Values in the data |
|---|---|---|
| strain $\varepsilon$ | axial strain `E11` | 0.0002 – 0.0999 |
| rate ratio $\dot\varepsilon^*$ | $\dot\varepsilon/\dot\varepsilon_0$, with $\dot\varepsilon_0=10^{-5}$ s⁻¹ | $\ln\dot\varepsilon^*$ = 0, 2.30, 4.61 |
| homologous temperature $T^*$ | $(T-T_r)/(T_m-T_r)$, with $T_r=30$ °C and $T_m=600$ °C | 0, 0.123, 0.298 |
| modulus ratio $G/G_0$ | $G_0=25300$ MPa | 1, 0.970, 0.9215 |
| porosity $\phi$ | $1-\rho/\rho_0$, with $\rho_0=2700$ kg/m³ | 0, 3 %, 7.85 % (our study point is 4 %) |

* **The minus sign.** Classic Johnson–Cook has $A+B\varepsilon^n$ (hardening). We use $A-B\varepsilon^n$ because all 73 curves soften.
* **Bounds.** The seven constants are kept physical:
  * $B$ is written as $B=A\beta/0.1^n$ with $0\le\beta\le0.99$, so $A-B\varepsilon^n>0$ up to $\varepsilon=0.1$;
  * $C,q,r\ge0$, because in every training pair stress rises with G and with density, i.e. falls with porosity.

  Without the bounds, a plain fit returned r = −0.027, which would mean stress rises with porosity.

The cell below evaluates the equation in code (`J.jc_numpy`) and checks one value by hand.
'''))
C.append(code(r'''
c = CFG['constants']
print('Constants of the definitions:', c)
for T in (30, 100, 200, 300):
    print(f'T = {T:3d} °C  ->  T* = {(T - c["T_ref"]) / (c["T_melt"] - c["T_ref"]):.4f}')
for lr in (-5, -4, -3):
    print(f'rate 1e{lr} /s  ->  ln(rate*) = {np.log(10.0**lr / c["rate0"]):.4f}')
for rho in (2700, 2619, 2592, 2488.05):
    print(f'density {rho:7.2f}  ->  phi = {100 * (1 - rho / c["rho0"]):.2f} %')

theta = [150.0, 400.0, 0.8, 0.03, 1.1, 0.7, 0.05]          # an example set of A, B, n, C, m, q, r
x = np.array([[100.0, -4.0, 2619.0, 24541.0, 0.05]])         # T, log10 rate, density, G, E11
A, B, n, C_, m, q, r = theta
by_hand = (A - B * 0.05**n) * (1 + C_ * np.log(10)) * (1 - (70 / 570)**m) * (24541 / 25300)**q * (2619 / 2700)**r
print('\nEquation 1 in code:', J.jc_numpy(theta, x, c)[0], '| by hand:', by_hand)
'''))

C.append(md(r'''
## 4. Why the equation alone is not enough

First we fit **only** the seven constants to the 36 training curves, with no neural network. The fit is bounded nonlinear
least squares (SciPy `least_squares`) started from 8 points; the lowest error wins. This is exactly the calibration used
inside the model code (`J.calibrate_jc`).

Equation 1 is a **product of separate terms**. Temperature, rate, G and porosity can therefore only scale a curve up or down;
they cannot change its *shape*, because $A-B\varepsilon^n$ is the same for every condition. Section 2 showed that the shape
does change, so even the best possible constants leave a large error. That error is a property of the equation, not of
the fit.
'''))
C.append(code(r'''
Xq, yq = J.queries(X_train, GRID), Y_train.ravel()
x_mean, x_scale, y_scale = J.scalers(Xq, Y_train)
t0 = time.time()
v, cal = J.calibrate_jc(Xq, yq, CFG, y_scale)
theta_alone = J.theta_from_cal(v, c)
print(f'Calibrated in {time.time() - t0:.1f} s. Constants at a bound: {cal["at_bounds"]}')
for k, a, b in zip(J.PARAMS, theta_alone, EQ_ONLY['theta'].values()):
    print(f'  {k} = {a:12.6g}   (saved run: {b:.6g})')
p_alone = J.jc_numpy(theta_alone, Xq, c).reshape(Y_train.shape)
s = J.scores(Y_train, p_alone)
print(f'\nEquation 1 alone on its own training curves: mean RMSE {s["mean_rmse"]:.2f} MPa '
      f'({100 * s["mean_nrmse"]:.1f} % of the stress), worst {s["worst_rmse"]:.1f} MPa (case {TRAIN[np.argmax(s["case_rmse"])]})')

fig, axes = plt.subplots(1, 3, figsize=(15, 4), sharey=False)
for ax, i in zip(axes, (2, 46, 60)):
    k = list(TRAIN).index(i)
    ax.plot(GRID, Y_train[k], 'k', lw=2, label='simulation')
    ax.plot(GRID, p_alone[k], '--', color='tab:orange', lw=2, label='Equation 1 alone')
    ax.set(title=f'Case {i}: {CASES[i]["T"]:g} °C, 1e{CASES[i]["lr"]:g} /s', xlabel='E11')
axes[0].set_ylabel('Svm (MPa)'); axes[0].legend(); plt.tight_layout(); plt.show()
'''))
C.append(md(r'''
**Reading the result.**
* **r = 0:** the separable fit finds no porosity effect it can use. In these simulations density changes stress by only
  about 0.2 %, much less than the shape mismatch.
* **The calibrated law** (these are the constants to quote for Equation 1) is:

  **A ≈ 148.8, B ≈ 526.2, n ≈ 0.83, C ≈ 0.029, m ≈ 1.11, q ≈ 0.72, r = 0.**
'''))

C.append(md(r'''
## 5. The model: equation backbone × neural-network correction

$$
\hat\sigma(T,\dot\varepsilon,\rho,G,\varepsilon)=\sigma_{JC}(A,B,n,C,m,q,r)\cdot\exp\!\big(\delta(z)\big),\qquad
z=\frac{x-\mu}{s}
$$

* **Backbone:** Equation 1 with its seven bounded constants.
* **Correction δ:** a small multilayer perceptron. It has 5 inputs (T, log₁₀ rate, ρ, G, E11, each standardised with the training
  mean μ and standard deviation s), two hidden layers of 16 tanh units and one linear output: **385 weights and biases**.
  * Its output layer starts at **zero**, so before training δ = 0 and the model *is* Equation 1.
  * exp(δ) is a multiplicative correction: exp(δ) = 0.9 means "10 % below Equation 1".
  * The exponential also keeps the predicted stress positive.
* **Ensemble:** five such networks with different random starts (seeds 0–4), combined by a geometric mean:
  $\hat\sigma=\exp\big(\tfrac15\sum_k[\ln\sigma_{JC}(\theta_k)+\delta_k]\big)$.
* **Constants frozen or joint:** "frozen" keeps the calibrated constants fixed. "Joint" lets training adjust them
  together with the network, which is the "alter the weights" option. Both were tested; joint won (Section 7).

The cell builds one untrained model and checks the two claims above: 385 parameters, and output identical to Equation 1.
'''))
C.append(code(r'''
torch = J._torch()
model = J.build_model(v, CFG, x_mean, x_scale, joint=True, seed=0)
n_net = sum(p.numel() for name, p in model.named_parameters() if name != 'u')
print(model.l1, model.l2, model.l3, sep='\n')
print('Network weights and biases:', n_net, '| trainable Equation 1 variables:', model.u.numel())
with torch.no_grad():
    s0, base0, d0 = model(torch.tensor(Xq))
start_theta = model.theta().detach().numpy()
print('Untrained model vs Equation 1 at its starting constants, max difference:',
      float(np.max(np.abs(s0.numpy() - J.jc_numpy(start_theta, Xq, c)))), 'MPa')
print('Starting constants vs calibrated ones, max relative difference:',
      float(np.max(np.abs(start_theta - theta_alone) / np.maximum(np.abs(theta_alone), 1e-3))),
      '(the trainable bound mapping holds a constant sitting exactly on a bound, here r = 0, a hair inside it)')
print('Untrained correction delta: max |delta| =', float(d0.abs().max()))
'''))

C.append(md(r'''
## 6. The loss function and the physics (PINN) terms

Training minimises

$$
\mathcal L=\underbrace{\frac1N\sum_i\Big(\frac{\hat\sigma_i-\sigma_i}{s_y}\Big)^2}_{\text{data: 36 curves × 120 points}}
+\lambda\,\underbrace{\frac1M\sum_{j}R_j^2}_{\text{physics residual}}
+\underbrace{\frac{\alpha}{N}\sum W^2}_{\text{weight decay}}
$$

* **Data term:** the mean squared stress error, scaled by the training stress spread $s_y$, so it has no units. Every curve
  contributes 120 equally weighted points.
* **Physics term:** evaluated at **M = 4,096 collocation points**. These are input combinations spread evenly (a scrambled
  Sobol sequence) over the whole planned design box: 30–300 °C, all rates, densities, G values and strains. They include
  conditions that have no simulation file. No stress values are used there; the points only say "obey the equation here".
  Two residual forms were tested:
  * **level:** $R=\delta=\ln\hat\sigma-\ln\sigma_{JC}$, so the prediction should stay close to Equation 1;
  * **trend:** $R=\partial\delta/\partial z_c$ for the four conditions (T, rate, ρ, G), computed by **automatic
    differentiation**. The model's *sensitivities* to the conditions should equal Equation 1's, while the strain-shape
    correction stays free.
* **λ** sets how strongly the physics is enforced. λ = 0 is a pure data fit; a huge λ returns Equation 1 exactly.
* **Weight decay α = 1** keeps the network smooth. It was fixed beforehand from a check on the training folds only, because
  a weak α let exp(δ) blow up when extrapolating (fold error 25 against 2.4).
'''))
C.append(code(r'''
Cq = J.collocation(CFG)
print('Collocation points:', Cq.shape, '- columns T, log10 rate, density, G, E11 (inputs only, no stresses)')
fig, axes = plt.subplots(1, 2, figsize=(12, 3.8))
axes[0].scatter(Cq[:, 0], Cq[:, 4], s=3, alpha=0.4, label='collocation points')
for T in (30, 100, 200):
    axes[0].axvline(T, color='k', lw=1)
axes[0].axvspan(200, 300, color='tab:red', alpha=0.08, label='no simulation data')
axes[0].set(xlabel='T (°C)', ylabel='E11', title='Where the physics term is evaluated'); axes[0].legend(loc='upper right', fontsize=8)
axes[1].scatter(Cq[:, 2], Cq[:, 3], s=3, alpha=0.4)
axes[1].scatter(X_train[:, 2], X_train[:, 3], s=60, c='k', marker='x', label='training conditions')
axes[1].set(xlabel='density (kg/m³)', ylabel='G (MPa)', title='Density × shear modulus'); axes[1].legend(fontsize=8)
plt.tight_layout(); plt.show()

for form in ('level', 'trend'):
    print(f'{form:>5} residual of the untrained model (equal to Equation 1):', J.physics_residual(model, torch.tensor(Cq), form).item())
'''))

C.append(md(r'''
## 7. Training and choosing the settings without seeing the test data

### 7.1 How one network is trained
Each network is trained on the whole training set at once (full batch, float64, CPU, fixed seed, so runs are
repeatable): **1,500 Adam steps** (learning rate 0.005) to get close, then up to **2,500 L-BFGS iterations** with a
strong-Wolfe line search to settle precisely. The next cell trains member 0 of the final model live with the selected
settings and compares it with the saved member. On this exact software it matches bit for bit; on other hardware tiny
rounding differences can grow slightly through L-BFGS.
'''))
C.append(code(r'''
chosen = SUM['selected']
print('Selected settings:', chosen)
t0 = time.time()
member, info = J.train_member(Xq, yq, Cq, v, CFG, x_mean, x_scale, y_scale, chosen, seed=0)
print(f"Trained in {time.time() - t0:.0f} s: loss after Adam {info['loss_after_adam']:.3e}, final {info['loss']:.3e} "
      f"(data {info['data_loss']:.3e}, weight decay {info['weight_loss']:.3e}), L-BFGS iterations {info['lbfgs_iterations']}")
saved = EQ['members'][0]
diff = max(np.max(np.abs(np.array(member[k]) - np.array(saved[k]))) for k in ('W1', 'W2', 'w3', 'theta'))
print('Largest difference from the saved member 0:', diff)
'''))
C.append(md(r'''
### 7.2 Choosing the settings
We do **not** pick settings by looking at test results. Each candidate setting is scored on the 36 training cases in two ways:
1. **Case cross-validation:** split the 36 cases into 3 folds; train on two, predict the third, and repeat.
2. **Unseen-condition holdouts:** for each of the 9 temperature/rate groups, hide *all* its cases, train on the rest and predict
   them. This tests prediction for a condition the model has never seen.

The **balanced score** we chose is ½ × (case-CV error + mean group-holdout error). The candidates were the physics form
(none / level / trend), λ, and frozen or joint constants: **14 settings**.
* Every split refits the scalers and the Equation 1 constants on its own fitting cases.
* Each setting is a 3-seed ensemble.
* In total: 14 × 12 splits × 3 seeds = **504 trained networks**.
'''))
C.append(code(r'''
sp = J.splits(X_train, TRAIN, CFG)
for s_ in sp:
    print(f"{s_['name']:>14}: fit on {len(s_['fit_ids']):2d} cases, predict {len(s_['val_ids']):2d} -> {s_['val_ids']}")
print()
rows = sorted(SUM['trials'], key=lambda t: t['score'])
print(f"{'physics':>8} {'lambda':>7} {'constants':>9} {'case-CV':>8} {'unseen':>8} {'score':>7}")
for t in rows:
    cd = t['candidate']
    mark = '  <- selected' if cd == chosen else ''
    print(f"{cd['physics']:>8} {cd['lambda_phys']:7g} {cd['theta_mode']:>9} {t['cv']:8.3f} {t['groups']:8.3f} {t['score']:7.3f}{mark}")
print(f"{'Equation 1 alone':>26} {SUM['equation_only']['cv']:8.3f} {SUM['equation_only']['groups']:8.3f}")
print(f"{'Curve-copy baseline':>26} {SUM['lookup']['cv']:8.3f} {SUM['lookup']['groups']:8.3f}")
'''))
C.append(md(r'''
**Reading the selection.**
* The winner is **the Equation 1 backbone with jointly trained constants and no extra physics penalty (λ = 0)**.
* Every level or trend penalty made *both* errors worse. Equation 1 is about 10 % off in level, and its fixed shape is wrong for
  hot or slow conditions, so pulling the model toward it, or toward its trends, moves predictions away from the simulations.
* A PINN penalty only helps when the governing equation is right where the data are missing.

### 7.3 Lock, then test once
The selected setting is retrained on all 36 training cases as a 5-seed ensemble. Its complete equation is saved, and its
SHA-256 fingerprint is written to `selection_lock.json` **before** the code opens any of the 37 test files. The test score
is computed once. An independent script (`scripts/verify_jc_pinn.py`) re-implements the equation in plain NumPy and
reproduces every prediction to 2.6e-13 MPa.
'''))

C.append(md(r'''
## 8. The output

### 8.1 Test results on the 37 held-out simulations
The next cell recomputes the test predictions from the saved equation (NumPy only) and checks that they equal the verified run.
'''))
C.append(code(r'''
Vq = J.queries(X_test, GRID)
p_test = J.equation_predict(EQ, Vq).reshape(Y_test.shape)
p_eq1 = J.jc_numpy(list(EQ_ONLY['theta'].values()), Vq, c).reshape(Y_test.shape)
m_pinn, m_eq1 = J.scores(Y_test, p_test), J.scores(Y_test, p_eq1)
assert abs(m_pinn['mean_rmse'] - SUM['test']['jc_pinn']['mean_rmse']) < 1e-9
ctl = SUM['control']['control']
table = [('Equation 1 alone', m_eq1['mean_rmse'], m_eq1['mean_nrmse']),
         ('Curve-copy baseline', SUM['test']['lookup']['mean_rmse'], SUM['test']['lookup']['mean_nrmse']),
         ('JC-PINN (this model)', m_pinn['mean_rmse'], m_pinn['mean_nrmse']),
         ('Same network, Equation 1 switched off (control)', ctl['test']['mean_rmse'], ctl['test']['mean_nrmse']),
         ('Single MLP (2 Nov, no physics)', SUM['single_mlp']['test'], None)]
print(f"{'Model':<50}{'mean RMSE (MPa)':>16}{'% of stress':>13}")
for name, e, nr in table:
    print(f"{name:<50}{e:16.4f}{('%.2f %%' % (100 * nr)) if nr is not None else '-':>13}")
print(f"\nJC-PINN median {m_pinn['median_rmse']:.4f}, worst {m_pinn['worst_rmse']:.4f} MPa (case {TEST[np.argmax(m_pinn['case_rmse'])]});"
      f" {m_eq1['mean_rmse'] / m_pinn['mean_rmse']:.0f}x lower error than Equation 1 alone")

order = np.argsort(m_pinn['case_rmse'])
picks = [order[0], order[len(order) // 2], order[-1]]
fig, axes = plt.subplots(1, 3, figsize=(15, 4))
for ax, k, lab in zip(axes, picks, ('best', 'median', 'worst')):
    ax.plot(GRID, Y_test[k], 'k', lw=2.2, label='simulation')
    ax.plot(GRID, p_eq1[k], '--', color='tab:orange', label='Equation 1 alone')
    ax.plot(GRID, p_test[k], color='tab:blue', lw=1.8, label='JC-PINN')
    i = TEST[k]
    ax.set(title=f'{lab} test case {i} ({CASES[i]["T"]:g} °C, 1e{CASES[i]["lr"]:g}): {m_pinn["case_rmse"][k]:.3f} MPa', xlabel='E11')
axes[0].set_ylabel('Svm (MPa)'); axes[0].legend(); plt.tight_layout(); plt.show()
'''))
C.append(md(r'''
### 8.2 Unseen temperature/rate conditions
Each bar is the error when that whole condition was hidden during training. The JC-PINN's own numbers are slightly
optimistic, because the selection score used them.
'''))
C.append(code(r'''
G_ = SUM['selected_groups']
labels = [f"{g['T']:g} °C\n1e{g['lr']:g}" for g in G_]
series = [('Equation 1 alone', SUM['equation_only']['group_rows'], 'tab:orange'),
          ('JC-PINN', [g['rmse'] for g in G_], 'tab:blue'),
          ('Equation 1 off (control)', [g['mean_rmse'] for g in SUM['control']['control']['groups']], 'tab:gray'),
          ('Single MLP', SUM['single_mlp']['groups'], 'tab:green')]
w = 0.2
fig, ax = plt.subplots(figsize=(13, 4))
for k, (lab, vals, col) in enumerate(series):
    ax.bar(np.arange(9) + (k - 1.5) * w, vals, w, label=f'{lab} (mean {np.mean(vals):.2f})', color=col)
ax.set_xticks(range(9), labels); ax.set_ylabel('mean curve RMSE (MPa)'); ax.legend(); ax.set_title('Error on a hidden condition')
plt.tight_layout(); plt.show()
'''))
C.append(md(r'''
### 8.3 The control experiment: does Equation 1 help?
To test the equation's contribution, the identical network and training were run with Equation 1 **switched off**: the
backbone was made constant. This control was not used to choose anything; the delivered model is unchanged.
'''))
C.append(code(r'''
j, ctl = SUM['control']['jc_pinn'], SUM['control']['control']
print(f"{'':<36}{'case-CV':>9}{'unseen':>9}{'test':>9}")
print(f"{'JC-PINN (Equation 1 backbone)':<36}{j['cv_mean_rmse']:9.3f}{j['group_mean_rmse']:9.3f}{j['test']['mean_rmse']:9.4f}")
print(f"{'Same network, Equation 1 off':<36}{ctl['cv_mean_rmse']:9.3f}{ctl['group_mean_rmse']:9.3f}{ctl['test']['mean_rmse']:9.4f}")
'''))
C.append(md(r'''
**What the comparison shows.**
* **Accuracy comes from the network and the training recipe, not from the equation.** The control is better on every
  measure. Equation 1's separable form forces one curve shape on every condition, and the network spends part of its
  capacity undoing that.
* **Against the baseline:** on unseen conditions the new recipe (strong weight decay, log-space output) beats the
  plain single MLP of 2 Nov (6.2 against 11.9). On the professor's random 50/50 test, the single MLP remains more precise
  (0.143 against 0.439). The balanced criterion we chose traded some interpolation precision for better
  behaviour on new conditions.
* **What Equation 1 gives us:**
  * seven named, physically bounded constants;
  * a model that starts from a stated physical law;
  * a 17-fold error reduction over that law alone.

  It does **not** make the predictions more accurate. The data say that its separable form is not the governing law of
  these simulations, and that is a valid scientific result.

### 8.4 Physical sanity checks
Using autograd on the collocation points, we count how often the model breaks the sign rules seen in every training-data
pair:
* stress falls with strain and with temperature;
* stress rises with G and with density.

Strain rate is not checked, because the data itself is mixed: at large strain, stress falls with rate at 30 °C.
'''))
C.append(code(r'''
mono = J.monotonicity(EQ, CFG)
for region in ('observed_30_200C', 'physics_only_200_300C'):
    m_ = mono[region]
    print(f"{region:>24}: {m_['points']} points | dS/dE11>0 {100*m_['dS_dE11_positive']:.1f} % | dS/dT>0 {100*m_['dS_dT_positive']:.1f} % | "
          f"dS/dG<0 {100*m_['dS_dG_negative']:.1f} % | dS/drho<0 {100*m_['dS_ddensity_negative']:.1f} %")
'''))
C.append(md(r'''
### 8.5 Using the model: predict any condition
`predict_curve` evaluates the saved equation with NumPy. Give a temperature (°C), a strain rate (1/s) and either a porosity
`phi` (fraction) or a `density`; G is in MPa.
* **Valid range:** 30–200 °C, rates 1e-5 to 1e-3 /s, φ = 0–7.85 %, G from 23,314 to 25,300 MPa, E11 up to 0.0999.
* **Above 200 °C** there is no data and no physics penalty, so those curves are **unvalidated extrapolation**.

The figure shows our study condition, φ = 4 % (ρ = 2592 kg/m³) with G = 24,541 MPa. The final cell of this part saves the
curves to a CSV file.
'''))
C.append(code(r'''
def predict_curve(T, rate, phi=None, density=None, G=24541.0, eq=EQ):
    rho = density if density is not None else 2700.0 * (1 - (0.04 if phi is None else phi))
    X5 = np.c_[np.tile([T, np.log10(rate), rho, G], (len(GRID), 1)), GRID]
    return J.equation_predict(eq, X5)

fig, axes = plt.subplots(1, 3, figsize=(15, 4), sharey=True)
rows_out = []
for ax, rate in zip(axes, (1e-5, 1e-4, 1e-3)):
    for T, col in ((30, 'tab:blue'), (100, 'tab:green'), (200, 'tab:red'), (300, 'tab:gray')):
        s_ = predict_curve(T, rate, phi=0.04)
        ax.plot(GRID, s_, '--' if T > 200 else '-', color=col, label=f'{T} °C' + (' (extrapolation)' if T > 200 else ''))
        rows_out += [(T, rate, e, v_) for e, v_ in zip(GRID, s_)]
    ax.set(title=f'φ = 4 %, rate {rate:g} /s', xlabel='E11')
axes[0].set_ylabel('predicted Svm (MPa)'); axes[0].legend(fontsize=8); plt.tight_layout(); plt.show()

s_ = predict_curve(100, 1e-4, phi=0.04)
print('100 °C, 1e-4 /s, phi = 4 %:', ', '.join(f'E11={GRID[k]:.3f}: {s_[k]:.2f} MPa' for k in (0, 60, 119)))
'''))
C.append(code(r'''
import csv as _csv
out_csv = WORK / 'predictions_phi4.csv'
with open(out_csv, 'w', newline='') as f:
    w_ = _csv.writer(f); w_.writerow(['T_C', 'rate_per_s', 'E11', 'Svm_MPa'])
    w_.writerows(rows_out)
print('Saved', len(rows_out), 'rows to', out_csv)
'''))

C.append(md(r'''
## 9. Optional: retrain from the professor's data

Set `RUN_TRAINING = True` and choose a mode:
* `'FAST'` retrains the selected setting on the 36 training cases, locks it and scores the 37 test cases. It takes about
  2–5 minutes on Colab.
* `'FULL'` repeats the whole 504-network selection. It takes about 1–2 hours on Colab's 2 CPUs, or 37 minutes on 4 cores.

**Where the data must be:**
* **Colab:** `TEAM_8_extracted_results_set_1`, or its ZIP, anywhere in My Drive. If the folder was shared with you, add a shortcut to My Drive first.
* **Kaggle:** add it as a Dataset input.
* **Local:** next to this notebook, or set `DATA_PATH`.

The code reads the training files first, saves and locks the model, and only then reads the test files. It also checks that
the curves it reads match the verified run.
'''))
C.append(code(r'''
RUN_TRAINING = False      # set True to retrain
MODE = 'FAST'             # 'FAST' or 'FULL'
DATA_PATH = ''            # optional: folder or ZIP path
WORKERS = None            # None = all CPU cores
'''))
C.append(code(r'''
import zipfile

def find_data(hint=''):
    if hint:
        p = Path(hint)
        if p.is_dir():
            return p
        return unzip(p)
    roots = []
    if IN_COLAB:
        from google.colab import drive
        drive.mount('/content/drive')
        roots += [Path('/content/drive/MyDrive'), Path('/content/drive/Shareddrives')]
    if IN_KAGGLE:
        roots.append(Path('/kaggle/input'))
    roots += [Path.cwd(), Path.cwd().parent]
    for root_ in roots:
        if not root_.exists():
            continue
        for depth in range(5):
            for h in sorted(root_.glob('/'.join(['*'] * depth + ['simulation_matrix.csv']))):
                if any(h.parent.glob('simulation_0*')):
                    return h.parent
        for z in sorted(root_.glob('TEAM_8*.zip')) + sorted(root_.glob('*/TEAM_8*.zip')):
            return unzip(z)
    raise FileNotFoundError('TEAM_8_extracted_results_set_1 not found: set DATA_PATH')

def unzip(z):
    target = WORK / 'raw'
    with zipfile.ZipFile(z) as archive:
        names = [n.replace('\\', '/') for n in archive.namelist()]
        for rel in ['simulation_matrix.csv'] + [f'simulation_{i:04d}/STR_STR.OUT' for i in SPLIT['train'] + SPLIT['test']]:
            hit = [archive.namelist()[k] for k, n in enumerate(names) if n == rel or n.endswith('/' + rel)]
            if len(hit) != 1:
                raise ValueError(f'{rel}: {len(hit)} matches in {z}')
            out = target / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(archive.read(hit[0]))
    return target

if RUN_TRAINING:
    RAW = find_data(DATA_PATH)
    base = (Path('/content/drive/MyDrive/MMM-ML/jc_pinn_runs') if IN_COLAB else
            Path('/kaggle/working/jc_pinn_runs') if IN_KAGGLE else WORK / 'runs')
    OUT = base / time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())
    result = J.run(WORK, RAW, OUT, mode=MODE.lower(), workers=WORKERS,
                   selected=dict(selected=SUM['selected']) if MODE == 'FAST' else None, expected=SUM['fingerprints'])
    print('Saved to', OUT)
    print('Test mean RMSE this run:', result['test']['jc_pinn']['mean_rmse'], '| verified run:', SUM['test']['jc_pinn']['mean_rmse'])
    from IPython.display import Image, display
    for name in ('test_comparison.png', 'condition_holdouts.png', 'study_point_curves.png'):
        if (OUT / name).exists():
            display(Image(filename=str(OUT / name)))
else:
    print('Retraining skipped (RUN_TRAINING = False). Every result above comes from the verified saved model.')
'''))

C.append(md(r'''
## 10. Limits and questions to expect in the viva

**Limits**
* **Not a blind test.** The 37 test cases were explored in earlier project stages. The group-holdout errors were part of the
  selection score, so the selected model's group errors are slightly optimistic.
* **Units.** Stress units are inferred as MPa. The model reproduces the professor's simulations; it is not validated
  against experiments.
* **Above 200 °C** there is no data, so 300 °C curves are unvalidated extrapolation.
* **Case 60** (200 °C, 1e-5 /s) collapses abruptly. Every model misses it when it is held out.
* **Two sets of constants.** The constants inside the JC-PINN are trained together with the network, so they only mean something
  together with it. Quote the "Equation 1 alone" constants as the calibrated law.

**Likely questions**
* **Is this a PINN?** It is a constitutive (material-point) physics-informed network. The physics is built into the model's
  structure, and physics residuals at collocation points were tested in its loss. The selection found that this equation's
  residuals did not help. It is not a 3D equilibrium PINN, because the data have no spatial fields.
* **Why multiply by exp(δ)?** It is a relative correction that keeps stress positive, and with δ = 0 the model is exactly the
  physical law.
* **Why 120 points per curve?** So that every simulation counts equally, whatever its number of output rows.
* **How do you know you didn't tune on the test set?** Every setting was chosen with training-only scores. The model's
  fingerprint was saved before the test files were opened, and an independent script re-checks this order.
* **What would improve the physics?** Let B and n depend on temperature and rate, so the equation itself can change the curve
  shape. That would be a new, extended law, to be qualified the same way.
'''))
for i, cell in enumerate(C):
    cell['id'] = f'jcx-{i:02d}'
nb = dict(cells=C, nbformat=4, nbformat_minor=5,
          metadata=dict(kernelspec=dict(name='python3', language='python', display_name='Python 3'), language_info=dict(name='python')))
out = root / 'notebooks/jc_pinn_explained.ipynb'
out.write_text(json.dumps(nb, indent=1) + '\n', encoding='utf-8')
print(out)
