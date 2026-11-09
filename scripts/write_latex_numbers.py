"""Write report/numbers.tex: LaTeX macros for every number quoted in the report, paper and deck.

All values are read from the saved run in reports/jc_pinn_20261107/, so no result is typed by hand.
Run from the repository root:  python scripts/write_latex_numbers.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / 'reports/jc_pinn_20261107'


def load(name):
    return json.loads((RUN / name).read_text())


def collect():
    res, test = load('results.json'), load('test_report/test_summary.json')['summary']
    ctrl, base, screen = load('control_no_equation.json'), load('baselines.json'), load('improvement_screen.json')
    sel = res['selection']
    n = {}
    f2, f3 = (lambda v: f'{v:.2f}'), (lambda v: f'{v:.3f}')

    # Equation 1 constants: alone and inside the JC-PINN.
    for prefix, theta in (('Eq', res['equation_only_constants']), ('Pinn', res['jc_pinn_constants'])):
        for k, v in theta.items():
            n[f'{prefix}{k}'] = f'{v:.3g}' if k != 'r' else (f'{v:.1e}' if v > 1e-12 else '0')
    n['EqA'], n['EqB'] = f2(res['equation_only_constants']['A']), f2(res['equation_only_constants']['B'])
    n['PinnA'], n['PinnB'] = f2(res['jc_pinn_constants']['A']), f2(res['jc_pinn_constants']['B'])

    # Selection (training cases only).
    trial = sel['selected_trial']
    n['SelCV'], n['SelGroups'], n['SelScore'] = f3(trial['cv']['mean_rmse']), f3(trial['group_mean_rmse']), f3(trial['score'])
    n['SelCVMedian'], n['SelCVWorst'] = f3(trial['cv']['median_rmse']), f2(trial['cv']['worst_rmse'])
    n['EqCV'], n['EqGroups'] = f2(sel['equation_only']['cv']['mean_rmse']), f2(sel['equation_only']['group_mean_rmse'])
    n['LookupCV'], n['LookupGroups'] = f2(sel['lookup']['cv']['mean_rmse']), f2(sel['lookup']['group_mean_rmse'])
    n['Settings'] = str(len(sel['trials']))

    # Test (37 cases, scored once after the lock).
    t = res['test']['jc_pinn']
    n['TestMean'], n['TestMedian'], n['TestWorst'] = f3(t['mean_rmse']), f3(t['median_rmse']), f3(t['worst_rmse'])
    n['TestMAE'] = f3(t['mean_mae'])
    n['TestWorstCase'], n['TestBest'], n['TestBestCase'] = str(test['curve_rmse']['worst_case']), f3(test['curve_rmse']['best']), str(test['curve_rmse']['best_case'])
    n['TestCases'], n['TestPoints'] = str(test['cases']), f"{test['points']:,}".replace(',', '{,}')
    p = test['points_summary']
    n['TestRsq'], n['TestBias'] = f'{p["r2"]:.5f}', f'{p["mean_signed"]:+.3f}'
    n['TestMaxAbs'], n['TestMeanPct'], n['TestMaxPct'] = f2(p['max_abs']), f2(p['mean_abs_pct']), f'{p["max_abs_pct"]:.1f}'
    n['TestWithinHalf'], n['TestWithinOne'], n['TestWithinTwo'] = (f'{100 * p[k]:.1f}' for k in ('within_0p5', 'within_1', 'within_2'))
    n['CasesHigh'], n['CasesLow'] = str(test['bias']['cases_high']), str(test['bias']['cases_low'])
    m = test['members']
    n['SpreadMean'], n['SpreadMax'] = f3(m['mean_spread']), f3(m['max_spread'])
    n['MemberBest'], n['MemberWorst'] = f3(min(m['single_member_rmse'])), f3(max(m['single_member_rmse']))
    n['TrainFit'] = f3(res['train_fit']['jc_pinn']['mean_rmse'])
    n['TestEq'], n['TestLookup'] = f2(res['test']['equation_only']['mean_rmse']), f3(res['test']['lookup']['mean_rmse'])
    n['TestEqWorst'] = f2(res['test']['equation_only']['worst_rmse'])
    c = test['comparison']
    n['WinsEq'], n['WinsLookup'], n['WinsSingle'], n['WinsEnsemble'] = (str(c[k]) for k in ('beats_equation_only', 'beats_lookup', 'beats_single_mlp', 'beats_ensemble_mlp'))
    n['Improvement'] = f'{res["test"]["equation_only"]["mean_rmse"] / t["mean_rmse"]:.0f}'
    n['DeltaMean'], n['DeltaMax'] = f3(res['correction']['test_mean_abs_delta']), f3(res['correction']['test_max_abs_delta'])

    # Baselines and the post-hoc control.
    n['SingleTest'], n['SingleCV'] = f3(base['single_mlp']['test']['mean_rmse']), f2(base['single_mlp']['cv'])
    n['SingleGroups'] = f2(sum(g['mean_rmse'] for g in base['single_mlp']['groups']) / len(base['single_mlp']['groups']))
    n['EnsTest'], n['EnsGroups'] = f3(base['ensemble_mlp']['test']['mean_rmse']), f2(base['ensemble_mlp']['loco_mean_rmse'])
    n['CtrlCV'], n['CtrlGroups'], n['CtrlScore'] = f3(ctrl['control']['cv_mean_rmse']), f3(ctrl['control']['group_mean_rmse']), f3(ctrl['control']['score'])
    n['CtrlTest'], n['CtrlTestWorst'] = f3(ctrl['control']['test']['mean_rmse']), f3(ctrl['control']['test']['worst_rmse'])

    # Improvement screen (training cases only, after the lock).
    rec = screen['recipe_3fold_cv']
    n['ScrIterLong'] = f3(rec['alpha 1, 8000 iterations'])
    n['ScrAlphaLow'] = f3(rec['alpha 0.3, 8000 iterations'])
    n['ScrWide'] = f3(rec['32-32 network, alpha 1, 8000 iterations'])
    fl = screen['curve_family_floor']
    n['FloorJCMean'], n['FloorJCMedian'] = f2(fl['A - B eps^n (3 constants per curve)']['mean']), f2(fl['A - B eps^n (3 constants per curve)']['median'])
    n['FloorCubicMean'] = f2(fl['cubic polynomial (4 per curve)']['mean'])
    forms = screen['correction_forms_balanced']
    n['ScrBoundedScore'] = f2(forms['bounded exp correction (x1/3..x3), alpha 0.1']['score'])

    # Training and data configuration.
    cfg = res['config']
    tr = cfg['training']
    n['Alpha'], n['AdamLR'], n['AdamSteps'] = f'{tr["alpha"]:g}', f'{tr["adam_lr"]:g}', f"{tr['adam_steps']:,}".replace(',', '{,}')
    n['LbfgsIter'] = f"{tr['lbfgs_max_iter']:,}".replace(',', '{,}')
    n['Colloc'] = f"{cfg['collocation']['points']:,}".replace(',', '{,}')
    n['Params'] = str(res['checks']['parameters_per_member'])
    n['TrainCases'], n['TestCasesSplit'] = str(len(res['train_ids'])), str(len(res['test_ids']))
    n['NumpyTorchErr'] = f'{res["checks"]["numpy_vs_torch_max_error"]:.1e}'
    n['RunMinutes'] = f'{res["elapsed_seconds"] / 60:.0f}'
    return n


def main():
    n = collect()
    lines = ['% Generated by scripts/write_latex_numbers.py from reports/jc_pinn_20261107/. Do not edit by hand.']
    lines += [f'\\newcommand{{\\n{k}}}{{{v}}}' for k, v in sorted(n.items())]
    out = ROOT / 'report/numbers.tex'
    out.parent.mkdir(exist_ok=True)
    out.write_text('\n'.join(lines) + '\n')
    (ROOT / 'report/numbers.json').write_text(json.dumps(n, indent=1, sort_keys=True) + '\n')
    print(f'wrote {len(n)} macros to {out.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
