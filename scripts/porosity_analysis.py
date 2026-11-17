"""Post-hoc, descriptive analysis: how density (porosity, phi = 1 - rho/2700) acts in the data and in the locked JC-PINN.

Nothing is fitted or tuned here and the locked model is unchanged. All 73 committed curves are used only to describe the
data: for every pair of cases that differ in ONE design variable (density, G or temperature) and share the others, the
mean relative stress difference along the 120-point curve is computed, and the same pair is predicted with the locked model.

Writes reports/jc_pinn_20261107/porosity_analysis.json.  Run:  python scripts/porosity_analysis.py
"""
import csv
import itertools
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import jc_pinn as J  # noqa: E402

RUN = ROOT / 'reports/jc_pinn_20261107'
RHO0 = 2700.0
KEYS = ('temperature', 'log10_strain_rate', 'density', 'shear_modulus')


def load():
    man = {m['id']: m for m in json.loads((ROOT / 'data/manifest.json').read_text())}
    curves = defaultdict(list)
    for name in ('cv_predictions.csv', 'test_predictions.csv'):
        with open(RUN / name) as fh:
            for row in csv.DictReader(fh):
                curves[int(row['id'])].append(float(row['Svm']))
    return man, {k: np.array(v) for k, v in curves.items()}


def pairs(man, curves, vary):
    """Pairs differing only in `vary`; returns (high, low) with high = larger value of `vary`."""
    fixed = [k for k in KEYS if k != vary]
    out = []
    for a, b in itertools.combinations(sorted(curves), 2):
        if all(man[a][k] == man[b][k] for k in fixed) and man[a][vary] != man[b][vary]:
            out.append((a, b) if man[a][vary] > man[b][vary] else (b, a))
    return out


def rel_drop(hi, lo):
    """Mean over the curve of (S_hi - S_lo)/S_hi, in percent."""
    return float(100 * np.mean((hi - lo) / hi))


def main():
    man, S = load()
    eq = J.load_final_equation(ROOT)
    res = json.loads((RUN / 'results.json').read_text())

    def predict(i):
        m = man[i]
        return J.predict_curves(eq, [[m['temperature'], 10 ** m['log10_strain_rate'], m['density'], m['shear_modulus']]])[1][0]

    out = {'purpose': 'Post-hoc descriptive analysis of the porosity (density) effect. Uses all 73 committed curves to describe '
                       'the data and the locked model; nothing is fitted, selected or changed.',
           'porosity_definition': 'phi = 1 - density/2700 (user decision M5)',
           'effects': {}}

    # One-variable effects in the data, by level pair.
    for vary in ('density', 'shear_modulus', 'temperature'):
        groups = defaultdict(list)
        for hi, lo in pairs(man, S, vary):
            groups[(man[hi][vary], man[lo][vary])].append((rel_drop(S[hi], S[lo]), float(np.mean(S[hi] - S[lo]))))
        out['effects'][vary] = [{'high': h, 'low': l, 'pairs': len(v),
                                 'mean_rel_pct': float(np.mean([x[0] for x in v])), 'min_rel_pct': float(np.min([x[0] for x in v])),
                                 'max_rel_pct': float(np.max([x[0] for x in v])), 'mean_MPa': float(np.mean([x[1] for x in v]))}
                                for (h, l), v in sorted(groups.items())]

    # Density pairs: data vs locked JC-PINN, per pair.
    dens = []
    for hi, lo in pairs(man, S, 'density'):
        p_hi, p_lo = predict(hi), predict(lo)
        dens.append({'high_id': hi, 'low_id': lo, 'temperature': man[hi]['temperature'], 'log10_rate': man[hi]['log10_strain_rate'],
                     'G': man[hi]['shear_modulus'], 'density_high': man[hi]['density'], 'density_low': man[lo]['density'],
                     'dphi_pct': 100 * (man[hi]['density'] - man[lo]['density']) / RHO0,
                     'data_rel_pct': rel_drop(S[hi], S[lo]), 'model_rel_pct': rel_drop(p_hi, p_lo)})
    d = np.array([[x['data_rel_pct'], x['model_rel_pct']] for x in dens])
    full = [x for x in dens if x['density_high'] == RHO0 and x['density_low'] == min(m['density'] for m in man.values())]
    f = np.array([[x['data_rel_pct'], x['model_rel_pct']] for x in full])
    by_T = {}
    for T in sorted({x['temperature'] for x in full}):
        v = np.array([[x['data_rel_pct'], x['model_rel_pct']] for x in full if x['temperature'] == T])
        by_T[f'{T:g}'] = {'pairs': len(v), 'data_rel_pct': float(v[:, 0].mean()), 'model_rel_pct': float(v[:, 1].mean())}
    phi_max = 1 - min(m['density'] for m in man.values()) / RHO0
    implied_r = float(np.log(1 - f[:, 0].mean() / 100) / np.log(1 - phi_max))

    g_full = [e for e in out['effects']['shear_modulus'] if e['high'] == 25300.0 and e['low'] == min(m['shear_modulus'] for m in man.values())][0]
    t_100 = [e for e in out['effects']['temperature'] if e['high'] == 100.0 and e['low'] == 30.0][0]
    out['density_vs_model'] = {
        'pairs': len(dens), 'pairs_with_lower_density_lower_stress': int(np.sum(d[:, 0] > 0)),
        'model_pairs_same_sign': int(np.sum(np.sign(d[:, 0]) == np.sign(d[:, 1]))),
        'correlation_data_model': float(np.corrcoef(d.T)[0, 1]),
        'full_range': {'phi_pct': 100 * phi_max, 'pairs': len(full), 'data_rel_pct': float(f[:, 0].mean()),
                       'model_rel_pct': float(f[:, 1].mean()), 'data_MPa': float(np.mean(
                           [np.mean(S[x['high_id']] - S[x['low_id']]) for x in full])),
                       'correlation_data_model': float(np.corrcoef(f.T)[0, 1]), 'by_temperature': by_T},
        'pairs_detail': dens}
    out['equation1'] = {'implied_r_from_data': implied_r, 'fitted_r_equation_only': res['equation_only_constants']['r'],
                        'fitted_r_jc_pinn': res['jc_pinn_constants']['r'],
                        'reading': 'The data imply r of about 0.04, but the separable fit set r to its lower bound 0: a ~0.3 MPa porosity '
                                   'effect is far smaller than Equation 1 alone\'s ~10 MPa misfit, so least squares does not resolve it. '
                                   'In the JC-PINN the porosity effect is carried by the correction network through its density input.'}
    out['comparison'] = {'G_full_range_rel_pct': g_full['mean_rel_pct'], 'T_30_to_100_rel_pct': t_100['mean_rel_pct'],
                         'G_over_density_ratio': g_full['mean_rel_pct'] / f[:, 0].mean(),
                         'reading': 'In the simulations density and G vary independently. In a real part both fall with porosity, and '
                                    'the G effect is much larger, so the bracket-level porosity effect depends mainly on the G(phi) '
                                    'relation, which the data do not define (open question Q4).'}
    out['caveats'] = ['Whether the generator intended density to represent porosity is unconfirmed (open question Q3).',
                      'Simulations only; units inferred; descriptive, not a validation of porosity physics.']
    (RUN / 'porosity_analysis.json').write_text(json.dumps(out, indent=1) + '\n', newline='\n')  # LF on every OS: reports/** is byte-checked (.gitattributes)
    fr = out['density_vs_model']['full_range']
    print(f"density pairs {len(dens)}, lower density -> lower stress in {out['density_vs_model']['pairs_with_lower_density_lower_stress']}; "
          f"full range data {fr['data_rel_pct']:.3f}% model {fr['model_rel_pct']:.3f}% corr {fr['correlation_data_model']:.2f}; "
          f"implied r {implied_r:.4f}; G {g_full['mean_rel_pct']:.2f}%; T30->100 {t_100['mean_rel_pct']:.2f}%")


if __name__ == '__main__':
    main()
