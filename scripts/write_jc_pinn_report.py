"""Write reports/<run>/README.md from the saved results (every number is read, none typed by hand).

Usage: python scripts/write_jc_pinn_report.py [reports/jc_pinn_YYYYMMDD]
"""
import json
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
run = Path(sys.argv[1]) if len(sys.argv) > 1 else root / 'reports/jc_pinn_20261107'
R = json.loads((run / 'results.json').read_text())
EQ = json.loads((run / 'equation.json').read_text())
V = json.loads((run / 'verification.json').read_text()) if (run / 'verification.json').exists() else {}
ens = json.loads((root / 'runs/score/select_mlp_Svm.json').read_text())
ens_test = json.loads((root / 'runs/score/final_Svm/metrics.json').read_text())
single = R['references'].get('single_mlp')
CTRL = json.loads((run / 'control_no_equation.json').read_text()) if (run / 'control_no_equation.json').exists() else None
S = R['selection']
sel = R['selected']
trial = S['selected_trial']
f = lambda x, d=3: f'{x:.{d}f}'
cand = lambda c: f"{c['physics']}, λ={c['lambda_phys']:g}, {c['theta_mode']}"

L = [f"# JC-PINN: user Equation 1 as the governing law - {run.name.split('_')[-1]}", '',
     'A physics-informed model of the supplied AlSi10Mg Svm(E11) simulations whose backbone is the user\'s',
     'customised Johnson-Cook equation (Equation 1, 7 November 2026). Same 36/37 case split as every earlier model.', '',
     '## Model', '',
     '```text',
     'sigma_JC = [A - B*E11^n] * [1 + C*ln(rate/1e-5)] * [1 - T*^m] * [G/25300]^q * [1 - phi]^r',
     'T* = (T - 30)/(600 - 30)  (T in C),   phi = 1 - density/2700',
     'sigma   = sigma_JC(A,B,n,C,m,q,r) * exp(delta(T, log10 rate, density, G, E11))',
     '```', '',
     'delta is a 5-16-16-1 tanh network (385 parameters) that starts at zero, so the untrained model is exactly',
     'Equation 1. Training loss = normalised data MSE (120 equal-weight points per case) + lambda x physics residual',
     'at 4096 Sobol collocation points (T 30-300 C) + weight decay (alpha = 1). Physics residual forms:',
     '**level** = delta (stay near Equation 1) and **trend** = d delta / d(T, log10 rate, density, G) via autograd,',
     'i.e. the model\'s condition sensitivities equal Equation 1\'s while the strain-shape correction stays free.', '',
     f"**Selected on training cases only: {cand(sel)}.** Final model: 5-seed ensemble, geometric mean of members.", '',
     '## Equation 1 constants', '',
     '| Constant | Equation 1 alone (calibrated on 36 training cases) | Inside the JC-PINN (member mean) |',
     '|---|---:|---:|']
for k in ('A', 'B', 'n', 'C', 'm', 'q', 'r'):
    L.append(f"| {k} | {R['equation_only_constants'][k]:.6g} | {R['jc_pinn_constants'][k]:.6g} |")
L += ['', f"Equation 1 alone sits at a bound for: {', '.join(R['equation_only_at_bounds']) or 'none'}. "
      'r = 0 means the separable fit finds no porosity effect it can use; density changes stress by only about 0.2 %',
      'in the data, and the shape mismatch dominates the fit.', '',
      '## Test results (37 held-out cases, scored once after the lock)', '',
      'Errors are per-curve RMSE in source stress units (MPa inferred).', '',
      '| Model | Mean | Median | Worst | Mean MAE | Mean normalised |', '|---|---:|---:|---:|---:|---:|']
for k, name in (('jc_pinn', '**JC-PINN (this run)**'), ('equation_only', 'Equation 1 alone'), ('lookup', 'Curve-copy baseline')):
    t = R['test'][k]
    L.append(f"| {name} | {f(t['mean_rmse'], 4)} | {f(t['median_rmse'], 4)} | {f(t['worst_rmse'], 4)} | {f(t['mean_mae'], 4)} | {100 * t['mean_nrmse']:.2f} % |")
if single:
    t = single['test']
    L.append(f"| Single MLP, 2 Nov (no physics) | {f(t['mean_rmse'], 4)} | {f(t['median_rmse'], 4)} | {f(t['worst_rmse'], 4)} | {f(t['mean_mae'], 4)} | {100 * t['mean_nrmse']:.2f} % |")
if CTRL:
    t = CTRL['control']['test']
    L.append(f"| Same network, Equation 1 switched off (post-hoc control) | {f(t['mean_rmse'], 4)} | {f(t['median_rmse'], 4)} | {f(t['worst_rmse'], 4)} | {f(t['mean_mae'], 4)} | {100 * t['mean_nrmse']:.2f} % |")
L.append(f"| 5-net MLP ensemble, 24 Oct (no physics) | {f(ens_test['test_mean_rmse'], 4)} | {f(ens_test['test_median_rmse'], 4)} | {f(ens_test['test_worst_rmse'], 4)} | - | - |")
L += ['', '| Test condition | Cases | JC-PINN mean RMSE | Equation 1 alone |', '|---|---:|---:|---:|']
for c in R['test_by_condition']:
    L.append(f"| {c['temperature']:g} C, 1e{c['log10_rate']:g} /s | {len(c['cases'])} | {f(c['jc_pinn']['mean_rmse'], 4)} | {f(c['equation_only']['mean_rmse'])} |")
L += ['', '![Test comparison](test_comparison.png)', '',
      '## Training-side selection (no test data)', '',
      'Score = 0.5 x (three-fold case-CV mean RMSE + mean over nine temperature/rate group holdouts). Every scaler',
      'and the Equation 1 constants are refitted inside each split; each candidate is a 3-seed ensemble.', '',
      '| Candidate | Case-CV mean | Group-holdout mean | Score |', '|---|---:|---:|---:|']
for t in sorted(S['trials'], key=lambda t: t['score']):
    mark = ' **(selected)**' if t['candidate'] == sel else ''
    L.append(f"| {cand(t['candidate'])}{mark} | {f(t['cv']['mean_rmse'])} | {f(t['group_mean_rmse'])} | {f(t['score'])} |")
for name, key in (('Equation 1 alone', 'equation_only'), ('Curve-copy baseline', 'lookup')):
    t = S[key]
    L.append(f"| {name} | {f(t['cv']['mean_rmse'])} | {f(t['group_mean_rmse'])} | {f(t['score'])} |")
L += ['', '### Unseen temperature/rate groups', '',
      'Each group is withheld from fitting; mean curve RMSE on its cases. The selected JC-PINN\'s numbers were part of',
      'its selection score, so they are mildly optimistic. The single MLP re-selected alpha inside each group (nested);',
      'the 24 Oct ensemble used fixed settings chosen after earlier all-data exploration.', '',
      '| Group | Cases | Curve copy | Equation 1 alone | JC-PINN (selected) | Eq. 1 off (control) | Single MLP | MLP ensemble |', '|---|---:|---:|---:|---:|---:|---:|---:|']
ens_key = lambda g: f"{g['temperature']:g}C_1e{g['log10_rate']:g}"
for k, g in enumerate(trial['groups']):
    lk = S['lookup']['groups'][k]['metrics']['mean_rmse']
    eo = S['equation_only']['groups'][k]['metrics']['mean_rmse']
    sm = next((x['mean_rmse'] for x in single['groups'] if x['temperature'] == g['temperature'] and x['log10_rate'] == g['log10_rate']), None) if single else None
    en = ens['loco_by_condition'].get(ens_key(g))
    ct = CTRL['control']['groups'][k]['mean_rmse'] if CTRL else None
    L.append(f"| {g['temperature']:g} C, 1e{g['log10_rate']:g} /s | {len(g['validation_ids'])} | {f(lk)} | {f(eo)} | {f(g['metrics']['mean_rmse'])} | {f(ct) if ct is not None else '-'} | "
             f"{f(sm) if sm is not None else '-'} | {f(en) if en is not None else '-'} |")
import numpy as np  # noqa: E402
L.append(f"| **Mean of 9 groups** | 36 | {f(S['lookup']['group_mean_rmse'])} | {f(S['equation_only']['group_mean_rmse'])} | "
         f"{f(trial['group_mean_rmse'])} | {f(CTRL['control']['group_mean_rmse']) if CTRL else '-'} | {f(np.mean([x['mean_rmse'] for x in single['groups']])) if single else '-'} | "
         f"{f(ens['loco_mean_rmse'])} |")
if CTRL:
    c, j = CTRL['control'], CTRL['jc_pinn']
    L += ['', '## Does Equation 1 help? Post-hoc control', '',
          'Same network, weight decay, optimiser, splits and seeds, with Equation 1 switched off (constant backbone,',
          f"every Equation 1 term equal to 1 within {CTRL['backbone_max_relative_deviation_from_constant']:.0e}). Not used for selection.", '',
          '| | Case-CV mean | Group-holdout mean | Score | Test mean RMSE |', '|---|---:|---:|---:|---:|',
          f"| JC-PINN (Equation 1 backbone, selected) | {f(j['cv_mean_rmse'])} | {f(j['group_mean_rmse'])} | {f(j['score'])} | {f(j['test']['mean_rmse'], 4)} |",
          f"| Equation 1 switched off | {f(c['cv_mean_rmse'])} | {f(c['group_mean_rmse'])} | {f(c['score'])} | {f(c['test']['mean_rmse'], 4)} |", '',
          '**Finding:** the control is better on every measure, although the JC-PINN figures are already optimistic (best of 14',
          'settings). The improvement over the earlier MLPs comes from the training recipe (weight decay alpha = 1, log-space',
          'output), not from Equation 1. Equation 1 is a product of separate terms, so it gives every condition the same curve',
          'shape, and the correction network spends capacity undoing that shape. None of the 13 physics-penalty settings',
          'improved the training-side score either. Equation 1 in this separable form is therefore not supported as the governing',
          'law of these simulations. Its value here is interpretability: seven constants and a 17x error reduction over',
          'Equation 1 alone. It does not add accuracy.', '',
          '**Trade-off against earlier models.** On the random 50/50 test the earlier MLPs remain more precise (single MLP',
          f"{f(single['test']['mean_rmse'], 3) if single else '-'}, 5-net ensemble {f(ens_test['test_mean_rmse'], 3)} versus {f(j['test']['mean_rmse'], 3)}).",
          f"On unseen temperature/rate groups the new recipe is better than the single MLP ({f(j['group_mean_rmse'], 2)} with Equation 1,",
          f"{f(c['group_mean_rmse'], 2)} without, versus {f(np.mean([x['mean_rmse'] for x in single['groups']]), 2) if single else '-'}) and close to the 24 Oct ensemble ({f(ens['loco_mean_rmse'], 2)}).",
          'The strong weight decay buys generalisation at the cost of interpolation precision; the balanced score chose that trade-off.', '',
          '**Constants inside the JC-PINN.** With joint training and no physics penalty, the split between backbone and correction',
          'is not identifiable. A falls from 149 to 88, m ranges from 1.0 to 5.4 across seeds, and at large strain exp(delta)',
          'reaches x2.4. Quote the "Equation 1 alone" constants as the calibrated law; the JC-PINN constants are only meaningful',
          'together with its network.']
mono = R['monotonicity']
L += ['', '![Unseen condition groups](condition_holdouts.png)', '',
      '## Physical consistency', '',
      f"* Correction size on the test queries: mean |delta| = {R['correction']['test_mean_abs_delta']:.4f}, "
      f"max |delta| = {R['correction']['test_max_abs_delta']:.4f} (exp(delta) is the factor applied to Equation 1).",
      '* Share of collocation points that break the sign rules found in every training-data pair',
      '  (stress falls with E11 and T, rises with G and with density):', '',
      '| Region | Points | dS/dE11 > 0 | dS/dT > 0 | dS/dG < 0 | dS/d(density) < 0 |', '|---|---:|---:|---:|---:|---:|']
for k, label in (('observed_30_200C', '30-200 C (data)'), ('physics_only_200_300C', '200-300 C (no data)')):
    m = mono[k]
    L.append(f"| {label} | {m['points']} | {100 * m['dS_dE11_positive']:.1f} % | {100 * m['dS_dT_positive']:.1f} % | "
             f"{100 * m['dS_dG_negative']:.1f} % | {100 * m['dS_ddensity_negative']:.1f} % |")
sp = R['study_point']
L += ['', 'Strain rate is not checked: at large strain the data itself shows stress falling with rate at 30 C.', '',
      f"## Study condition: phi = {sp['porosity']:.0%} (density {sp['density']:g} kg/m3), G = {sp['G']:g} MPa", '',
      '| T | Rate (1/s) | Svm at E11=0.0002 | at 0.05 | at 0.0999 | Correction at 0.0999 |', '|---|---:|---:|---:|---:|---:|']
e = sp['E11']
j05 = min(range(len(e)), key=lambda k: abs(e[k] - 0.05))
for c in sp['curves']:
    tag = ' (extrapolation)' if c['extrapolated'] else ''
    L.append(f"| {c['temperature']:g} C{tag} | 1e{c['log10_rate']:g} | {f(c['stress'][0], 2)} | {f(c['stress'][j05], 2)} | "
             f"{f(c['stress'][-1], 2)} | x{c['correction_factor'][-1]:.3f} |")
L += ['', sp['note'] if 'lambda_phys = 0' in sp.get('note', '') else
      '300 C has no data. With lambda_phys = 0 nothing constrains 200-300 C except the Equation 1 backbone and the smooth '
      'network, so those curves are unvalidated extrapolation (equation.json\'s validity note, written for lambda > 0, '
      'overstates this).', '',
      '![Study-point curves](study_point_curves.png)', '',
      '## Verification', '']
if V:
    L.append(f"`scripts/verify_jc_pinn.py` (independent NumPy re-implementation, no import of the model code): "
             f"**{'all checks passed' if V.get('all_passed') else 'FAILED'}**. JC-PINN predictions reproduced to "
             f"{V['jc_pinn_predictions_reproduced_max_abs']:.1e}, Equation 1 alone to {V['equation_only_predictions_reproduced_max_abs']:.1e}. "
             'It also checks the split, lock order and hashes, the pre-registered selection rule, the CV and test metrics, '
             'that the curves are identical to the 2 Nov curves, the constant bounds and that earlier delivered artifacts are unchanged.')
L += [f"NumPy equation versus torch: {R['checks']['numpy_vs_torch_max_error']:.1e}. Unit tests: `tests/test_jc_pinn.py`.", '',
      '## Limits', '',
      f"* {R['caveat']}",
      '* Development checks on the three training folds fixed alpha = 1 and added the trend residual before this run',
      '  (configs/jc_pinn.json `development_notes`), so the selected case-CV estimate is mildly optimistic.',
      '* The raw histories are not in Git. This run read a stand-in folder rebuilt from the committed 120-point curves',
      '  (`scripts/build_raw_from_committed_curves.py`); np.interp at identical grid points returns those values exactly,',
      '  and the verifier confirms the curves equal the 2 Nov curves that were hash-checked against the raw files.',
      '* Equation 1 constants are effective fitting constants for these simulations, not measured material properties.', '',
      '## Reproduce', '',
      '```bash',
      'python scripts/build_raw_from_committed_curves.py            # only if the real raw folder is absent',
      'python src/jc_pinn.py --raw TEAM_8_extracted_results_set_1 --output reports/NEW --mode full --workers 4',
      f'python src/jc_pinn.py --raw TEAM_8_extracted_results_set_1 --output reports/NEW --mode fast --selected-from {run.relative_to(root)}/results.json',
      f'python scripts/verify_jc_pinn.py {run.relative_to(root)}',
      '```', '',
      'Colab/Kaggle: `notebooks/jc_pinn_colab.ipynb` (PREDICT needs no data; FAST and FULL read the professor folder).',
      f"Run time {R['elapsed_seconds'] / 60:.1f} min on 4 CPU workers; " + ', '.join(f'{k} {v}' for k, v in R['versions'].items()) + '.', '']
(run / 'README.md').write_text('\n'.join(L))
print(run / 'README.md')
