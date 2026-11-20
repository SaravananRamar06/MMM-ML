"""Residual strength and critical flaw length (CL) of the cracked bracket by the BS 7910 Option 1 FAD.

Post-hoc analysis (the locked JC-PINN is used unchanged as the USERMAT). Inputs, made by make_crack_decks.py runs
and copied into RUNS_DIR (one folder per run):
  elastic_a<a>/crack_result.csv           K_I by interaction integral (contours 1-6, MPa*sqrt(mm)) and the
                                          reaction FY (N per mm of thickness), linear elastic, UY = 0.1 mm
  usermat_<case>_a<a>/crack_history.csv   reaction history (N/mm) of the JC-PINN USERMAT run, UY ramped to 2 mm
  usermat_<case>_a<a>/crack_history_partial.csv
                                          the same, read back by post_history.mac from a run that stopped
                                          converging; its last set is MAPDL's unconverged debug state and is dropped
Per crack length a, porosity phi and toughness K_mat:
  k(a)       = K_I / P (MPa*sqrt(m) per kN of total load on the 40 mm thick bracket; median of contours 2-6;
               independent of E, hence of porosity)
  P_C(a,phi) = collapse load: a peak of the USERMAT reaction x 40 mm (kN). Two definitions are reported:
               'first'  - the first maximum after which the reaction falls by >= 1 % (in every run here it is also
                          the highest);
               'second' - the highest later maximum after such a fall, where one exists (else equal to 'first')
  Kr = k(a) P / K_mat,  Lr = P / P_C(a,phi),  f(Lr) = (1 + 0.5 Lr^2)^-0.5 [0.3 + 0.7 exp(-mu Lr^6)],
  mu = min(0.001 E / sigma_y, 0.6), Lr_max = 1 (softening material: no load above the peak)
  P_f(a,phi,K_mat) = residual strength: the load at which (Lr, Kr) reaches the FAD
  CL(P) = crack length at which P_f falls to P (None: no modelled crack, up to 30 mm, fails at P)
Loads (decision of the user, 20 Nov 2026): limit load 35.9 kN (14 CFR 25.571(b) residual strength), limit x 1.15
fitting factor = 41.3 kN (sensitivity), and 50-80 kN (sensitivity above limit load, CL against load).
Usage: python fad_cl.py RUNS_DIR OUT_DIR
Writes OUT_DIR/fad_cl.json, residual_strength.csv, cl_vs_load.csv.
"""
import csv
import json
import math
import sys
from pathlib import Path

THICK = 40.0
NU = 0.33
# phi, G (MPa, decision D5), flow stress at first yield (MPa; printed by scripts/check_limit_load.py, step 4)
CASES = {'gphi0': (0.0, 25300.0, 137.32), 'gphi4': (0.04, 24288.0, 135.69), 'gphi785': (0.0785, 23313.95, 134.20)}
K_BAND = [36.0, 40.0, 50.0]          # MPa*sqrt(m): user decision, literature range for LPBF AlSi10Mg
LIMIT = 35.9                         # kN, capability-based limit pin load (user decision)
LIMIT_FF = round(LIMIT * 1.15, 1)    # kN, limit x fitting factor (sensitivity)
LOW_K = [20.0, 25.0, 30.0]           # MPa*sqrt(m): sensitivity below the chosen band (not a decision)
SENS_LOADS = [45.0, 50.0, 55.0, 60.0, 65.0, 70.0, 75.0, 80.0]
PEAKS = ['first', 'second']


def rows(p):
    with open(p) as f:
        r = list(csv.reader(f))
    return [[float(v) for v in x] for x in r[1:] if x]


def peaks(fy, drop=0.01):
    """(first, second) peak indices; see the module docstring."""
    first = None
    for i in range(len(fy)):
        for k in range(i + 1, len(fy)):
            if fy[k] > fy[i]:
                break
            if fy[k] < (1 - drop) * fy[i]:
                first = i
                break
        if first is not None:
            break
    if first is None:
        first = max(range(len(fy)), key=lambda j: fy[j])
        return first, first
    # after the first fall: local maxima that are followed by a fall or by the end of the converged history
    k = next(k for k in range(first + 1, len(fy)) if fy[k] < (1 - drop) * fy[first])
    later = [j for j in range(k + 1, len(fy)) if fy[j] >= fy[j - 1] and (j == len(fy) - 1 or fy[j] >= fy[j + 1])]
    return first, (max(later, key=lambda j: fy[j]) if later else first)


def f_fad(lr, mu):
    return (1 + 0.5 * lr * lr) ** -0.5 * (0.3 + 0.7 * math.exp(-mu * lr ** 6))


def failure_load(k, pc, kmat, mu):
    """Load at which (Lr, Kr) = (P/pc, k P/kmat) reaches the FAD, cut off at Lr = 1."""
    g = lambda p: k * p / kmat - f_fad(p / pc, mu)
    if g(pc) < 0:
        return pc, 'collapse'
    lo, hi = 0.0, pc
    for _ in range(80):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if g(mid) < 0 else (lo, mid)
    return (lo + hi) / 2, 'fracture'


def crit_length(A, pf, load):
    if pf[0] <= load:
        return 0.0
    for i in range(len(A) - 1):
        if pf[i] > load >= pf[i + 1]:
            return A[i] + (pf[i] - load) / (pf[i] - pf[i + 1]) * (A[i + 1] - A[i])
    return None


def main():
    runs, out = Path(sys.argv[1]), Path(sys.argv[2])
    el = {}
    for d in runs.glob('elastic_a*'):
        a, fy, *kc = rows(d / 'crack_result.csv')[0]
        p_kn = fy * THICK / 1e3
        k = sorted(kc[1:])[2] / math.sqrt(1000) / p_kn if a else 0.0
        el[a] = {'P_kN_at_0.1mm': p_kn, 'K1_contours_MPa_sqrtmm': kc, 'k_MPa_sqrtm_per_kN': k}
    A = sorted(el)
    res = {'loads_kN': {'limit': LIMIT, 'limit_x_1.15': LIMIT_FF, 'sensitivity': SENS_LOADS},
           'K_mat_band_MPa_sqrtm': K_BAND, 'thickness_mm': THICK,
           'elastic': {f'{a:g}': el[a] for a in A}, 'cases': {}}
    table = []
    for case, (phi, g, sy) in CASES.items():
        E = 2 * g * (1 + NU)
        mu = min(0.001 * E / sy, 0.6)
        c = {'phi': phi, 'G_MPa': g, 'E_MPa': E, 'sigma_y_MPa': sy, 'mu': mu, 'per_a': {}, 'CL_mm': {},
             'min_reserve_factor_at_limit': {}}
        for a in A:
            d = runs / f'usermat_{case}_a{a:g}'
            full = (d / 'crack_history.csv').exists()
            h = rows(d / 'crack_history.csv') if full else rows(d / 'crack_history_partial.csv')[:-1]
            fy = [r[3] * THICK / 1e3 for r in h]
            i1, i2 = peaks(fy)
            pa = {'run_reached_2mm': full, 'u_last_converged_mm': h[-1][2],
                  'P_C_first_kN': fy[i1], 'u_first_mm': h[i1][2], 'P_C_second_kN': fy[i2], 'u_second_mm': h[i2][2]}
            for pk in PEAKS:
                for km in K_BAND:
                    pf, mode = failure_load(el[a]['k_MPa_sqrtm_per_kN'] or 1e-12, pa[f'P_C_{pk}_kN'], km, mu)
                    pa[f'P_f_{pk}_K{km:g}'] = pf
                    pa[f'mode_{pk}_K{km:g}'] = mode
                    pa[f'RF_{pk}_K{km:g}'] = pf / LIMIT
                    table.append({'case': case, 'phi': phi, 'a_mm': a, 'peak': pk, 'K_mat': km,
                                  'k_MPa_sqrtm_per_kN': round(el[a]['k_MPa_sqrtm_per_kN'], 5),
                                  'P_C_kN': round(pa[f'P_C_{pk}_kN'], 3), 'P_f_kN': round(pf, 3), 'mode': mode,
                                  'RF_limit': round(pf / LIMIT, 4), 'RF_limit_x_1.15': round(pf / LIMIT_FF, 4)})
            c['per_a'][f'{a:g}'] = pa
        for pk in PEAKS:
            for km in K_BAND:
                pf = [c['per_a'][f'{a:g}'][f'P_f_{pk}_K{km:g}'] for a in A]
                for load in [LIMIT, LIMIT_FF] + SENS_LOADS:
                    c['CL_mm'][f'{pk}_K{km:g}_P{load:g}'] = crit_length(A, pf, load)
                c['min_reserve_factor_at_limit'][f'{pk}_K{km:g}'] = min(pf) / LIMIT
        res['cases'][case] = c
    # worked example: a = 30 mm, phi = 7.85 %, K_mat = 36, first peak
    c = res['cases']['gphi785']
    pa = c['per_a']['30']
    k30, pc = el[30.0]['k_MPa_sqrtm_per_kN'], pa['P_C_first_kN']
    ex = {'a_mm': 30, 'phi': 0.0785, 'K_mat': 36.0, 'k_MPa_sqrtm_per_kN': k30, 'P_C_kN': pc, 'mu': c['mu']}
    for name, p in (('at_limit', LIMIT), ('at_limit_x_1.15', LIMIT_FF), ('at_failure', pa['P_f_first_K36'])):
        lr, kr = p / pc, k30 * p / 36.0
        ex[name] = {'P_kN': p, 'K_I_MPa_sqrtm': k30 * p, 'Kr': kr, 'Lr': lr, 'f_Lr': f_fad(lr, c['mu'])}
    res['worked_example'] = ex
    # outside the chosen band: K_IC as low as 20-30 MPa*sqrt(m) is also reported for LPBF AlSi10Mg (Paul et al. 2021)
    low = {}
    for case, cc in res['cases'].items():
        for km in LOW_K:
            pf = [failure_load(el[a]['k_MPa_sqrtm_per_kN'] or 1e-12, cc['per_a'][f'{a:g}']['P_C_first_kN'], km,
                               cc['mu'])[0] for a in A]
            low[f'{case}_K{km:g}'] = {'P_f_kN': pf, 'CL_mm_at_limit': crit_length(A, pf, LIMIT)}
    res['low_K_sensitivity'] = low
    out.mkdir(parents=True, exist_ok=True)
    (out / 'fad_cl.json').write_text(json.dumps(res, indent=1) + '\n', newline='\n')
    with open(out / 'residual_strength.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(table[0]))
        w.writeheader()
        w.writerows(table)
    with open(out / 'cl_vs_load.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['load_kN', 'peak', 'K_mat'] + list(CASES))
        for load in [LIMIT, LIMIT_FF] + SENS_LOADS:
            for pk in PEAKS:
                for km in K_BAND:
                    v = [res['cases'][cs]['CL_mm'][f'{pk}_K{km:g}_P{load:g}'] for cs in CASES]
                    w.writerow([load, pk, km] + ['>30' if x is None else round(x, 2) for x in v])
    for case, c in res['cases'].items():
        print(case, 'min RF at limit:', {k: round(v, 3) for k, v in c['min_reserve_factor_at_limit'].items()})
    print('worked example', json.dumps(ex, indent=1))


if __name__ == '__main__':
    main()
