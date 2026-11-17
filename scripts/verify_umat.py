"""Verify the generated Abaqus UMAT (umat/jc_pinn_umat.f) against the locked JC-PINN, without Abaqus.

Compiles the UMAT with gfortran together with the offline driver (umat/test/umat_driver.f) and checks:
  1. generated file is up to date with equation.json and the template;
  2. flow stress and its slope at 2000 random points vs the NumPy model (jc_pinn.equation_predict) and
     a central finite difference;
  3. single-element uniaxial stress (3D and 4-component) at several conditions and increment sizes:
     elastic slope, stress on the flow curve, strain split eps = p + sigma/E, increment-size independence;
  4. the consistent tangent DDSDDE vs a central finite difference of the stress update;
  5. the range flags (STATEV 3).
Writes umat/verification.json.  Run:  python scripts/verify_umat.py
"""
import json
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'scripts'))
import jc_pinn as J  # noqa: E402
import write_umat  # noqa: E402

UMAT = ROOT / 'umat/jc_pinn_umat.f'
DRIVER = ROOT / 'umat/test/umat_driver.f'
REPORT = ROOT / 'umat/verification.json'
NU = 0.33                                   # assumed Poisson's ratio used in the checks only
CONDITIONS = [                              # T degC, rate 1/s, density, G MPa
    (30.0, 1e-5, 2700.0, 25300.0),
    (100.0, 1e-4, 2592.0, 24541.0),        # study point, phi = 4 %
    (200.0, 1e-3, 2488.05, 23313.95),
    (250.0, 1e-4, 2592.0, 24541.0),        # physics-only band, flag 4
]


def compile_driver(workdir):
    fc = shutil.which('gfortran')
    if fc is None:
        raise RuntimeError('gfortran not found')
    exe = Path(workdir) / 'umat_driver'
    cmd = [fc, '-O2', '-ffixed-form', f'-I{ROOT / "umat/test"}', str(DRIVER), str(UMAT), '-o', str(exe)]
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    return exe


def _run(exe, text):
    r = subprocess.run([str(exe)], input=text, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f'driver failed ({r.returncode}): {r.stdout[-400:]}')
    return [[float(t) for t in line.split()] for line in r.stdout.strip().splitlines()]


def flow(exe, X):
    rows = '\n'.join(' '.join(f'{v:.17e}' for v in r) for r in X)
    return np.array(_run(exe, f'1\n{len(X)}\n{rows}\n'))


def uniaxial(exe, props, ntens, nstep, emax):
    return np.array(_run(exe, f"2\n{' '.join(f'{p:.17e}' for p in props)}\n{ntens} {nstep} {emax}\n"))


def tangent(exe, props, ntens, p0, s0, de):
    fmt = lambda v: ' '.join(f'{x:.17e}' for x in v)
    out = _run(exe, f'3\n{fmt(props)}\n{ntens} {p0:.17e}\n{fmt(s0)}\n{fmt(de)}\n')
    statev = np.array(out[0])
    analytic = np.array(out[1:1 + ntens])
    numeric = np.array(out[1 + ntens:]).T
    return statev, analytic, numeric


def check_flow(exe, eq, n=2000, seed=0):
    rng = np.random.default_rng(seed)
    X = np.c_[rng.uniform(30, 300, n), rng.uniform(-5, -3, n), rng.uniform(2488.05, 2700, n),
              rng.uniform(23313.95, 25300, n), rng.uniform(write_umat.EPMIN, write_umat.EPMAX, n)]
    F = flow(exe, X)
    ref = J.equation_predict(eq, X)
    h = 1e-7
    Xp, Xm = X.copy(), X.copy()
    Xp[:, 4] += h
    Xm[:, 4] -= h
    fd = (J.equation_predict(eq, Xp) - J.equation_predict(eq, Xm)) / (2 * h)
    return dict(points=n, max_rel_stress_error=float(np.max(np.abs(F[:, 0] / ref - 1))),
                max_rel_slope_error_vs_fd=float(np.max(np.abs(F[:, 1] - fd) / np.maximum(np.abs(fd), 1.0))),
                errors_flagged=int(F[:, 2].max()))


def check_uniaxial(exe, eq, emax=0.12):
    out = []
    for T, rate, rho, G in CONDITIONS:
        props = [T, rate, rho, G, NU, 0.0, 0.0]
        E = 2 * G * (1 + NU)
        finals = {}
        for ntens in (6, 4):
            for nstep in (20, 1000):
                U = uniaxial(exe, props, ntens, nstep, emax)
                eps, s, p, flag, its = U[:, 1], U[:, 2], U[:, 3], U[:, 5], U[:, 6]
                el = p == 0
                pl = (p > write_umat.EPMIN) & (p < write_umat.EPMAX)
                X = np.c_[np.full(pl.sum(), T), np.full(pl.sum(), np.log10(rate)), np.full(pl.sum(), rho),
                          np.full(pl.sum(), G), p[pl]]
                ref = J.equation_predict(eq, X)
                finals[f'ntens{ntens}_steps{nstep}'] = dict(
                    eps11=float(eps[-1]), sigma11=float(s[-1]), eqps=float(p[-1]), flag=int(flag[-1]),
                    elastic_slope_rel_error=float(np.max(np.abs(s[el] / eps[el] / E - 1))) if el.any() else None,
                    on_flow_curve_rel_error=float(np.max(np.abs(s[pl] / ref - 1))),
                    strain_split_error=float(np.max(np.abs(eps[pl] - (p[pl] + s[pl] / E)))),
                    max_newton_iterations=int(its.max()))
        s_final = [v['sigma11'] for v in finals.values()]
        out.append(dict(T=T, rate=rate, density=rho, G=G, nu=NU, runs=finals,
                        increment_size_spread_MPa=float(max(s_final) - min(s_final))))
    return out


def check_tangent(exe, seed=1):
    rng = np.random.default_rng(seed)
    rows = []
    for ntens in (6, 4):
        for p0 in (0.0, 0.01, 0.05, 0.098):
            props = [100.0, 1e-4, 2592.0, 24541.0, NU, 0.0, 0.0]
            de = rng.normal(0, 4e-3, ntens)
            s0 = rng.normal(0, 30, ntens)
            sv, A, F = tangent(exe, props, ntens, p0, s0, de)
            rows.append(dict(ntens=ntens, eqps0=p0, plastic_increment=float(sv[0] - p0),
                             rel_error=float(np.abs(A - F).max() / np.abs(A).max())))
    # an elastic increment returns the elastic stiffness
    sv, A, F = tangent(exe, [100.0, 1e-4, 2592.0, 24541.0, NU, 0.0, 0.0], 6, 0.0, [0.0] * 6, [1e-5] + [0.0] * 5)
    rows.append(dict(ntens=6, eqps0=0.0, plastic_increment=float(sv[0]), rel_error=float(np.abs(A - F).max() / np.abs(A).max())))
    return rows


def check_flags(exe):
    cases = {'inside data range': ([100.0, 1e-4, 2592.0, 24541.0], 0),
             '250 degC (physics-only band)': ([250.0, 1e-4, 2592.0, 24541.0], 4),
             'G below range': ([100.0, 1e-4, 2592.0, 22000.0], 2),
             'rate above range': ([100.0, 1e-2, 2592.0, 24541.0], 2)}
    out = {}
    for name, (cond, want) in cases.items():
        U = uniaxial(exe, cond + [NU, 0.0, 0.0], 6, 10, 0.05)
        out[name] = dict(expected=want, got=int(U[-1, 5]))
    U = uniaxial(exe, [100.0, 1e-4, 2592.0, 24541.0, NU, 0.0, 0.0], 6, 20, 0.12)
    out['EQPS beyond 0.0999'] = dict(expected=1, got=int(U[-1, 5]))
    return out


def run():
    eq = J.load_final_equation(ROOT)
    up_to_date = UMAT.read_text() == write_umat.render()
    with tempfile.TemporaryDirectory() as tmp:
        exe = compile_driver(tmp)
        fc = subprocess.run(['gfortran', '--version'], capture_output=True, text=True).stdout.splitlines()[0]
        result = dict(
            umat='umat/jc_pinn_umat.f', generated_file_up_to_date=up_to_date, compiler=fc,
            python=platform.python_version(), flow=check_flow(exe, eq), uniaxial=check_uniaxial(exe, eq),
            tangent=check_tangent(exe), flags=check_flags(exe),
            note=('Offline checks with a test driver and gfortran; not run inside Abaqus. Poisson ratio 0.33 is an '
                  'assumption of the checks. The model strain is E11 taken as equivalent plastic strain (decision M4).'))
    tol = dict(stress=1e-12, slope=1e-6, curve=1e-9, split=1e-10, spread=1e-8, tangent=1e-6)
    ok = (up_to_date and result['flow']['max_rel_stress_error'] < tol['stress']
          and result['flow']['max_rel_slope_error_vs_fd'] < tol['slope'] and result['flow']['errors_flagged'] == 0
          and all(r['on_flow_curve_rel_error'] < tol['curve'] and r['strain_split_error'] < tol['split']
                  and (r['elastic_slope_rel_error'] or 0) < tol['curve']
                  for c in result['uniaxial'] for r in c['runs'].values())
          and all(c['increment_size_spread_MPa'] < tol['spread'] for c in result['uniaxial'])
          and all(t['rel_error'] < tol['tangent'] for t in result['tangent'])
          and all(f['expected'] == f['got'] for f in result['flags'].values()))
    result.update(tolerances=tol, passed=bool(ok))
    return result


def main():
    result = run()
    REPORT.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(passed=result['passed'], flow=result['flow'],
                          tangent_max=max(t['rel_error'] for t in result['tangent']),
                          spread=[c['increment_size_spread_MPa'] for c in result['uniaxial']]), indent=2))
    print(f'wrote {REPORT.relative_to(ROOT)}')
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
