"""Verify the generated user materials against the locked JC-PINN, without Abaqus or ANSYS.

Compiles each of umat/jc_pinn_umat.f (Abaqus UMAT) and umat/jc_pinn_usermat3d.F (ANSYS usermat3d)
with gfortran and the offline driver (umat/test/umat_driver.F, -DANSYS for ANSYS) and checks:
  1. generated files are up to date with equation.json and the templates;
  2. flow stress and its slope at 2000 random points vs the NumPy model (jc_pinn.equation_predict) and
     a central finite difference;
  3. single-element uniaxial stress (3D and 4-component) at several conditions and increment sizes:
     elastic slope, stress on the flow curve, strain split eps = p + sigma/E, increment-size independence;
  4. the consistent tangent DDSDDE vs a central finite difference of the stress update;
  5. the range flags (STATEV 3);
  6. ANSYS only: the plastic strain tensor epsPl returned by usermat3d (uniaxial: p, -p/2).
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

SOURCES = {kind: out for kind, (_, out) in write_umat.TARGETS.items()}
DRIVER = ROOT / 'umat/test/umat_driver.F'
REPORT = ROOT / 'umat/verification.json'
NU = 0.33                                   # assumed Poisson's ratio used in the checks only
CONDITIONS = [                              # T degC, rate 1/s, density, G MPa
    (30.0, 1e-5, 2700.0, 25300.0),
    (100.0, 1e-4, 2592.0, 24541.0),        # study point, phi = 4 %
    (200.0, 1e-3, 2488.05, 23313.95),
    (250.0, 1e-4, 2592.0, 24541.0),        # physics-only band, flag 4
]


def compile_driver(workdir, kind='abaqus'):
    fc = shutil.which('gfortran')
    if fc is None:
        raise RuntimeError('gfortran not found')
    exe = Path(workdir) / f'umat_driver_{kind}'
    flags = ['-DANSYS'] if kind == 'ansys' else []
    cmd = [fc, '-O2', '-ffixed-form', *flags, f'-I{ROOT / "umat/test"}', str(DRIVER), str(SOURCES[kind]),
           '-o', str(exe)]
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


def check_uniaxial(exe, eq, emax=0.12, plastic_tensor=False):
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
                if plastic_tensor:
                    finals[f'ntens{ntens}_steps{nstep}']['plastic_tensor_error'] = float(max(
                        np.max(np.abs(U[:, 9] - p)), np.max(np.abs(U[:, 10] + p / 2))))
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


def check_solver(kind, eq, workdir):
    exe = compile_driver(workdir, kind)
    return dict(source=str(SOURCES[kind].relative_to(ROOT)), flow=check_flow(exe, eq),
                uniaxial=check_uniaxial(exe, eq, plastic_tensor=kind == 'ansys'),
                tangent=check_tangent(exe), flags=check_flags(exe))


TOL = dict(stress=1e-12, slope=1e-6, curve=1e-9, split=1e-10, spread=1e-8, tangent=1e-6, plastic_tensor=1e-12)


def solver_passed(r):
    runs = [run for c in r['uniaxial'] for run in c['runs'].values()]
    return bool(r['flow']['max_rel_stress_error'] < TOL['stress']
                and r['flow']['max_rel_slope_error_vs_fd'] < TOL['slope'] and r['flow']['errors_flagged'] == 0
                and all(x['on_flow_curve_rel_error'] < TOL['curve'] and x['strain_split_error'] < TOL['split']
                        and (x['elastic_slope_rel_error'] or 0) < TOL['curve']
                        and x.get('plastic_tensor_error', 0) < TOL['plastic_tensor'] for x in runs)
                and all(c['increment_size_spread_MPa'] < TOL['spread'] for c in r['uniaxial'])
                and all(x['rel_error'] < TOL['tangent'] for x in r['tangent'])
                and all(f['expected'] == f['got'] for f in r['flags'].values()))


def run():
    eq = J.load_final_equation(ROOT)
    up_to_date = {kind: SOURCES[kind].read_text() == write_umat.render(kind) for kind in SOURCES}
    fc = subprocess.run(['gfortran', '--version'], capture_output=True, text=True).stdout.splitlines()[0]
    with tempfile.TemporaryDirectory() as tmp:
        solvers = {kind: check_solver(kind, eq, tmp) for kind in SOURCES}
    for r in solvers.values():
        r['passed'] = solver_passed(r)
    result = dict(generated_files_up_to_date=up_to_date, compiler=fc, python=platform.python_version(),
                  solvers=solvers, tolerances=TOL,
                  note=('Offline checks with a test driver and gfortran; not run inside Abaqus or ANSYS. Poisson ratio '
                        '0.33 is an assumption of the checks. The model strain is E11 taken as equivalent plastic '
                        'strain (decision M4).'))
    result['passed'] = bool(all(up_to_date.values()) and all(r['passed'] for r in solvers.values()))
    return result


def main():
    result = run()
    REPORT.write_text(json.dumps(result, indent=2) + '\n')
    for kind, r in result['solvers'].items():
        print(kind, json.dumps(dict(passed=r['passed'], flow=r['flow'],
                                    tangent_max=max(x['rel_error'] for x in r['tangent']),
                                    spread_max=max(c['increment_size_spread_MPa'] for c in r['uniaxial']))))
    print('passed' if result['passed'] else 'FAILED')
    print(f'wrote {REPORT.relative_to(ROOT)}')
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
