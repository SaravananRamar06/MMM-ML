"""Write report/numbers.tex: LaTeX macros for every number quoted in the report, paper and deck.

All values are read from saved files, so no result is typed by hand: the locked run in
reports/jc_pinn_20261107/ (collect), and the post-hoc finite-element work in umat/ and
bracket/ansys_usermat/ (collect_fe; it does not change the model).
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
    n['WinsEq'], n['WinsLookup'], n['WinsSingle'] = (str(c[k]) for k in ('beats_equation_only', 'beats_lookup', 'beats_single_mlp'))
    n['Improvement'] = f'{res["test"]["equation_only"]["mean_rmse"] / t["mean_rmse"]:.0f}'
    n['DeltaMean'], n['DeltaMax'] = f3(res['correction']['test_mean_abs_delta']), f3(res['correction']['test_max_abs_delta'])

    # Baselines and the post-hoc control.
    n['SingleTest'], n['SingleCV'] = f3(base['single_mlp']['test']['mean_rmse']), f2(base['single_mlp']['cv'])
    n['SingleGroups'] = f2(sum(g['mean_rmse'] for g in base['single_mlp']['groups']) / len(base['single_mlp']['groups']))
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

    # Porosity (density) analysis, post-hoc and descriptive.
    pa = load('porosity_analysis.json')
    dv, fr = pa['density_vs_model'], pa['density_vs_model']['full_range']
    n['PorPairs'], n['PorPairsLower'] = str(dv['pairs']), str(dv['pairs_with_lower_density_lower_stress'])
    n['PorSameSign'], n['PorCorr'] = str(dv['model_pairs_same_sign']), f"{dv['correlation_data_model']:.2f}"
    n['PorFullPairs'], n['PorFullCorr'] = str(fr['pairs']), f"{fr['correlation_data_model']:.2f}"
    n['PorData'], n['PorModel'], n['PorMPa'] = f"{fr['data_rel_pct']:.2f}", f"{fr['model_rel_pct']:.2f}", f"{fr['data_MPa']:.2f}"
    for T, key in (('30', 'Thirty'), ('100', 'Hundred'), ('200', 'TwoHundred')):
        n['PorData' + key] = f"{fr['by_temperature'][T]['data_rel_pct']:.2f}"
        n['PorModel' + key] = f"{fr['by_temperature'][T]['model_rel_pct']:.2f}"
    n['PorImpliedR'] = f"{pa['equation1']['implied_r_from_data']:.3f}"
    n['PorG'], n['PorT'] = f"{pa['comparison']['G_full_range_rel_pct']:.2f}", f"{-pa['comparison']['T_30_to_100_rel_pct']:.1f}"
    n['PorRatio'] = f"{pa['comparison']['G_over_density_ratio']:.0f}"

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


def read_json(rel):
    return json.loads((ROOT / rel).read_text())


def read_csv(rel):
    import csv
    with (ROOT / rel).open() as f:
        return [{k.strip(): float(v) for k, v in r.items()} for r in csv.DictReader(f)]


def collect_fe():
    """Post-hoc finite-element work (the model is unchanged): UMAT/USERMAT checks and the bracket runs.

    Sources: umat/verification.json, umat/ansys_test/, bracket/ansys_usermat/{results,porosity,mesh,mesh_ep}_2026-11-17/.
    Macro names use letters only (LaTeX). Signed changes keep their sign, e.g. -7.7.
    """
    import numpy as np
    n = {}
    sci = lambda v: f'{v:.0e}'.replace('e-0', 'e-').replace('e+0', 'e+')
    pct1, pct2 = (lambda v: f'{v:+.1f}'), (lambda v: f'{v:+.2f}')
    kN = lambda v: f'{v / 1e3:.1f}'

    # Offline verification of the generated UMAT and USERMAT (same core; worst case over both).
    ver = read_json('umat/verification.json')
    sv = list(ver['solvers'].values())
    runs = [r for s in sv for c in s['uniaxial'] for r in c['runs'].values()]
    n['VerPassed'] = 'yes' if ver['passed'] and all(s['passed'] for s in sv) else 'no'
    n['VerFlowPoints'] = f"{sv[0]['flow']['points']:,}".replace(',', '{,}')
    n['VerStressErr'] = sci(max(s['flow']['max_rel_stress_error'] for s in sv))
    n['VerSlopeErr'] = sci(max(s['flow']['max_rel_slope_error_vs_fd'] for s in sv))
    n['VerCurveErr'] = sci(max(r['on_flow_curve_rel_error'] for r in runs))
    n['VerIncSpread'] = sci(max(c['increment_size_spread_MPa'] for s in sv for c in s['uniaxial']))
    n['VerTangentErr'] = sci(max(t['rel_error'] for s in sv for t in s['tangent']))
    n['VerFlagChecks'] = str(len(sv[0]['flags']))

    # MAPDL 2024 R1 single-element test (USERMAT): compared as in umat/ansys_test/compare.py.
    got = read_csv('umat/ansys_test/results_2026-11-17/jcpinn_single_element.csv')
    ref = read_csv('umat/ansys_test/expected_single_element.csv')
    want = np.interp([g['eps11'] for g in got], [r['eps11'] for r in ref], [r['S11_MPa'] for r in ref])
    n['SePoints'] = str(len(got))
    n['SeMaxDiff'] = f"{max(abs(g['S11_MPa'] - w) for g, w in zip(got, want)):.1e}".replace('e-0', 'e-')
    n['SeTol'] = '0.1'  # tolerance fixed in compare.py
    n['SeSFinal'], n['SeEqpsFinal'], n['SeFlagFinal'] = f"{got[-1]['S11_MPa']:.2f}", f"{got[-1]['EQPS']:.4f}", f"{got[-1]['FLAG']:.0f}"

    # Bracket on the 5 mm Workbench mesh: elastic, Workbench EP (MISO) and the USERMAT at the study point.
    br = read_json('bracket/ansys_usermat/results_2026-11-17/summary.json')
    el, ep, um = br['elastic'], br['ep_miso'], br['usermat']
    n['BrElasticStiff'] = f"{el['initial_stiffness_N_per_mm'] / 1e3:.1f}"
    n['BrUsermatStiff'] = f"{um['initial_stiffness_N_per_mm'] / 1e3:.1f}"
    n['BrStiffRatio'] = f"{um['initial_stiffness_N_per_mm'] / el['initial_stiffness_N_per_mm']:.3f}"
    n['BrElasticFinalkN'], n['BrEpFinalkN'] = kN(el['final_RFX_N']), kN(ep['final_RFX_N'])
    n['BrUsermatPeakkN'], n['BrUsermatPeakUX'] = kN(um['peak_RFX_N']), f"{-um['peak_at_ux_mm']:.3f}"
    n['BrUsermatFinalkN'] = kN(um['final_RFX_N'])
    n['BrEpEqps'], n['BrUsermatEqps'] = f"{ep['final_eppl_eqv_max_elem']:.3f}", f"{um['final_svar1_max_elem']:.2f}"
    n['BrUsermatFlagged'] = str(um['final_n_elem_flag'])
    hist = read_csv('bracket/ansys_usermat/results_2026-11-17/usermat_history.csv')
    n['BrUsermatPeakStress'] = f"{max(h['seqv_max_elem_MPa'] for h in hist):.1f}"
    n['BrElasticFinalStress'] = f"{el['final_seqv_max_elem_MPa']:.0f}"
    n['BrEpFinalStress'] = f"{ep['final_seqv_max_elem_MPa']:.0f}"

    # Porosity on the bracket: density only at fixed G, plus the G sensitivity (porosity_2026-11-17).
    po = read_json('bracket/ansys_usermat/porosity_2026-11-17/porosity_summary.json')
    n['PorBrPhiZeroPeakkN'] = kN(po['phi0']['peak_RFX_N'])
    n['PorBrDensMinPeakkN'] = kN(po['phi785']['peak_RFX_N'])
    n['PorFourPeakChangePct'] = f"{po['phi4']['peak_RFX_change_vs_phi0_pct']:+.2f}"
    n['PorDensPeakChangePct'] = f"{po['phi785']['peak_RFX_change_vs_phi0_pct']:+.2f}"
    n['PorDensFinalChangePct'] = f"{po['phi785']['RFX_at_final_change_vs_phi0_pct']:+.2f}"
    n['PorGLowPeakChangePct'], n['PorGHighPeakChangePct'] = (f"{po[c]['peak_RFX_change_vs_phi0_pct'] - po['phi4']['peak_RFX_change_vs_phi0_pct']:+.2f}" for c in ('G_lo', 'G_hi'))
    n['PorGLowStepPct'] = f"{100 * (po['G_lo']['G_MPa'] / po['phi4']['G_MPa'] - 1):+.1f}"
    n['PorGHighStepPct'] = f"{100 * (po['G_hi']['G_MPa'] / po['phi4']['G_MPa'] - 1):+.1f}"
    n['PorDensStepPct'] = f"{100 * (po['phi785']['density_kg_m3'] / po['phi0']['density_kg_m3'] - 1):+.2f}"
    # change in peak force per 1 % change of the input: G (G_lo vs phi4) against density (phi785 vs phi0)
    g_per = abs((po['G_lo']['peak_RFX_N'] / po['phi4']['peak_RFX_N'] - 1) / (po['G_lo']['G_MPa'] / po['phi4']['G_MPa'] - 1))
    d_per = abs((po['phi785']['peak_RFX_N'] / po['phi0']['peak_RFX_N'] - 1) / (po['phi785']['density_kg_m3'] / po['phi0']['density_kg_m3'] - 1))
    n['PorBrGOverDens'] = f'{g_per / d_per:.0f}'
    exp = read_csv_mixed('bracket/ansys_usermat/porosity_2026-11-17/expected_flow_stress.csv')
    pick = lambda case, e: next(r for r in exp if r['case'] == case and abs(float(r['eqps']) - e) < 1e-12)
    n['PorSeDensYieldPct'] = f"{float(pick('phi785', 0.0002)['change_vs_phi0_pct']):+.2f}"
    n['PorSeDensLimitPct'] = f"{float(pick('phi785', 0.0999)['change_vs_phi0_pct']):+.2f}"

    # Mesh study: 5 mm vs uniform 2x2x2 refinement (mesh_2026-11-17, mesh_ep_2026-11-17).
    ms = read_json('bracket/ansys_usermat/mesh_2026-11-17/mesh_summary.json')
    me = read_json('bracket/ansys_usermat/mesh_ep_2026-11-17/mesh_ep_summary.json')
    c, f = ms['5mm'], ms['2p5mm']
    n['MeshElemCoarse'], n['MeshElemFine'] = (f"{s['elements']:,}".replace(',', '{,}') for s in (c, f))
    n['MeshNodesFine'] = f"{f['nodes']:,}".replace(',', '{,}')
    n['MeshStiffChangePct'] = f"{f['pct_vs_5mm']['initial_stiffness_N_per_mm']:+.2f}"
    n['BrMeshPeakChangePct'] = pct1(f['pct_vs_5mm']['peak_RFX_N'])
    n['MeshPeakFinekN'], n['MeshPeakFineUX'] = kN(f['peak_RFX_N']), f"{-f['peak_at_ux_mm']:.3f}"
    um_p = me['usermat']['2p5mm']['pct_vs_5mm']
    n['MeshForceMidChangePct'] = pct1(um_p['RFX_at_ux_0.455mm_N'])
    n['MeshForceOneChangePct'] = pct1(um_p['RFX_at_ux_1mm_N'])
    n['MeshFinalChangePct'] = pct1(f['pct_vs_5mm']['RFX_at_final_N'])
    n['MeshEqpsCoarse'], n['MeshEqpsFine'] = f"{c['max_elem_eqps_svar1']:.2f}", f"{f['max_elem_eqps_svar1']:.2f}"
    n['MeshFlagFine'] = f"{f['n_elem_flagged']:,}".replace(',', '{,}')
    ep_p = me['ep_miso']['2p5mm']['pct_vs_5mm']
    ep_force = [k for k in ep_p if k.startswith('RFX') or k == 'peak_RFX_N']
    n['MeshEpMaxChangePct'] = f"{max(abs(ep_p[k]) for k in ep_force):.1f}"
    n['MeshEpStrainRatio'] = f"{me['ep_miso']['2p5mm']['max_elem_eppl_eqv'] / me['ep_miso']['5mm']['max_elem_eppl_eqv']:.2f}"
    n['MeshUmStrainRatio'] = f"{me['usermat']['2p5mm']['max_elem_eppl_eqv'] / me['usermat']['5mm']['max_elem_eppl_eqv']:.2f}"
    share = [100 * (1 - abs(ep_p[k]) / abs(um_p[k])) for k in ('peak_RFX_N', 'RFX_at_ux_0.455mm_N', 'RFX_at_ux_1mm_N')]
    n['MeshSofteningShareMin'], n['MeshSofteningShareMax'] = f'{min(share):.0f}', f'{max(share):.0f}'
    n['MeshFineWallMin'] = f"{f['wall_time_s'] / 60:.0f}"

    # Porosity with density and G coupled by decision D5, G = 25300 (1 - phi) (porosity_gphi_2026-11-17).
    gp = read_json('bracket/ansys_usermat/porosity_gphi_2026-11-17/porosity_gphi_summary.json')
    n['GphiGFour'] = f"{gp['gphi4']['G_MPa']:.0f}"
    n['GphiPeakZerokN'], n['GphiPeakMaxPorkN'] = kN(gp['gphi0']['peak_RFX_N']), kN(gp['gphi785']['peak_RFX_N'])
    n['GphiStiffChangePct'] = f"{gp['gphi785']['pct_vs_gphi0']['initial_stiffness_N_per_mm']:+.2f}"
    n['GphiPeakChangePct'] = f"{gp['gphi785']['pct_vs_gphi0']['peak_RFX_N']:+.2f}"
    n['GphiFourPeakChangePct'] = f"{gp['gphi4']['pct_vs_gphi0']['peak_RFX_N']:+.2f}"
    n['GphiFinalChangePct'] = f"{gp['gphi785']['pct_vs_gphi0']['RFX_at_final_N']:+.2f}"
    gexp = read_csv_mixed('bracket/ansys_usermat/porosity_gphi_2026-11-17/expected_flow_stress.csv')
    gpick = lambda e: next(r for r in gexp if r['case'] == 'gphi785' and abs(float(r['eqps']) - e) < 1e-12)
    n['GphiSeYieldPct'] = f"{float(gpick(0.0002)['change_vs_phi0_pct']):+.2f}"
    n['GphiSeLimitPct'] = f"{float(gpick(0.0999)['change_vs_phi0_pct']):+.2f}"

    # Q5: Irwin plastic zone r_p = (1/2pi)(K/sigma_y)^2 at the bracket's peak element stress (the flow stress),
    # for the range of K_IC reported for LPBF AlSi10Mg (20 to 60 MPa m^0.5; docs/proposals/open-items-2026-11-17.md).
    sy = max(h['seqv_max_elem_MPa'] for h in hist)
    rp = lambda k: 1e3 * (k / sy) ** 2 / (2 * np.pi)  # mm
    n['ClPlasticZoneMin'], n['ClPlasticZoneMax'] = f'{rp(20.0):.0f}', f'{rp(60.0):.0f}'
    return n


def read_csv_mixed(rel):
    import csv
    with (ROOT / rel).open() as f:
        return list(csv.DictReader(f))


def main():
    n = collect()
    fe = collect_fe()
    clash = set(n) & set(fe)
    assert not clash, f'macro names used twice: {clash}'
    assert all(k.isalpha() for k in fe), [k for k in fe if not k.isalpha()]
    n.update(fe)
    lines = ['% Generated by scripts/write_latex_numbers.py from reports/jc_pinn_20261107/. Do not edit by hand.']
    lines += [f'\\newcommand{{\\n{k}}}{{{v}}}' for k, v in sorted(n.items())]
    out = ROOT / 'report/numbers.tex'
    out.parent.mkdir(exist_ok=True)
    out.write_text('\n'.join(lines) + '\n', newline='\n')  # LF on every OS (committed files are LF)
    (ROOT / 'report/numbers.json').write_text(json.dumps(n, indent=1, sort_keys=True) + '\n', newline='\n')
    print(f'wrote {len(n)} macros to {out.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
