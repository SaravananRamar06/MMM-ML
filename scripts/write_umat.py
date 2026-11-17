"""Generate the ANSYS USERMAT (usermat3d) of the locked JC-PINN from its saved weights.

Reads reports/jc_pinn_20261107/equation.json (checked against selection_lock.json; the locked
files are only read, never changed). The output is the ANSYS wrapper template followed by the
core (umat/templates/jc_pinn_core.f.in) filled with the five members' weights, Equation 1
constants and data ranges:

    umat/jc_pinn_usermat3d.F   ANSYS USERMAT, usermat3d  (templates/ansys_usermat3d.F.in)

The output is deterministic, so tests can check that the committed file matches its source.
Run:  python scripts/write_umat.py [--check]
"""
import argparse
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import jc_pinn as J  # noqa: E402

TEMPLATES = ROOT / 'umat/templates'
CORE = TEMPLATES / 'jc_pinn_core.f.in'
TARGETS = {'ansys': ('ansys_usermat3d.F.in', ROOT / 'umat/jc_pinn_usermat3d.F')}
OUTPUT = TARGETS['ansys'][1]
EPMIN, EPMAX = 0.0002, 0.0999          # the model's strain range (the 120-point E11 grid)
TEMP_PHYSICS_MAX = 300.0               # collocation box upper temperature


def fnum(v):
    """Full double precision as a Fortran D literal."""
    return f'{float(v):.17E}'.replace('E', 'D')


def data_stmt(target, values):
    """One DATA statement in fixed form: values two per continuation line (< 20 continuations)."""
    vals = [fnum(v) for v in values]
    lines = [f'      DATA {target} /']
    for i in range(0, len(vals), 2):
        chunk = ', '.join(vals[i:i + 2])
        last = i + 2 >= len(vals)
        lines.append(f'     &  {chunk}{" /" if last else ","}')
    assert len(lines) - 1 <= 19
    return lines


def data_block(eq):
    members = eq['members']
    assert len(members) == 5
    out = []
    for k, m in enumerate(members, start=1):
        assert list(m.get('inputs', range(5))) == [0, 1, 2, 3, 4]
        out.append(f'C     member {k}')
        out += data_stmt(f'(TH(J,{k}),J=1,7)', m['theta'])
        for i, row in enumerate(m['W1'], start=1):
            out += data_stmt(f'(W1({i},J,{k}),J=1,5)', row)
        out += data_stmt(f'(B1(J,{k}),J=1,16)', m['b1'])
        for i, row in enumerate(m['W2'], start=1):
            out += data_stmt(f'(W2({i},J,{k}),J=1,16)', row)
        out += data_stmt(f'(B2(J,{k}),J=1,16)', m['b2'])
        out += data_stmt(f'(W3(J,{k}),J=1,16)', m['w3'])
    out += data_stmt('B3', [m['b3'] for m in members])
    out += data_stmt('XM', eq['x_mean'])
    out += data_stmt('XS', eq['x_scale'])
    return out


def render(kind='ansys'):
    eq = J.load_final_equation(ROOT)                      # raises if the lock fingerprint fails
    sha = hashlib.sha256((ROOT / J.FINAL_RUN / 'equation.json').read_bytes()).hexdigest()
    c, box = eq['constants'], J.DATA_BOX
    subs = {
        '@@SHA@@': sha[:32] + '...',
        '@@EPMIN_TXT@@': f'{EPMIN:g}', '@@EPMAX_TXT@@': f'{EPMAX:g}',
        '@@EPMIN@@': fnum(EPMIN), '@@EPMAX@@': fnum(EPMAX),
        '@@TLO@@': fnum(box['temperature'][0]), '@@THI@@': fnum(TEMP_PHYSICS_MAX),
        '@@TOBS@@': fnum(box['temperature'][1]),
        '@@RLO@@': fnum(box['log10_rate'][0]), '@@RHI@@': fnum(box['log10_rate'][1]),
        '@@DLO@@': fnum(box['density'][0]), '@@DHI@@': fnum(box['density'][1]),
        '@@GLO@@': fnum(box['G'][0]), '@@GHI@@': fnum(box['G'][1]),
        '@@RATE0@@': fnum(c['rate0']), '@@TREF@@': fnum(c['T_ref']), '@@TMELT@@': fnum(c['T_melt']),
        '@@G0@@': fnum(c['G0']), '@@RHO0@@': fnum(c['rho0']),
    }
    text = (TEMPLATES / TARGETS[kind][0]).read_text() + CORE.read_text()
    text = text.replace('@@DATA@@', '\n'.join(data_block(eq)))
    for key, val in subs.items():
        text = text.replace(key, val)
    if '@@' in text:
        raise ValueError('Unfilled placeholder in the UMAT template')
    bad = [i for i, line in enumerate(text.splitlines(), 1) if len(line) > 72 or '\t' in line]
    if bad:
        raise ValueError(f'Fixed-form lines over 72 columns or with tabs: {bad[:10]}')
    return text


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--check', action='store_true', help='fail if a committed file differs from a fresh render')
    a = ap.parse_args()
    status = 0
    for kind, (_, out) in TARGETS.items():
        text = render(kind)
        if a.check:
            same = out.exists() and out.read_text() == text
            print(f'{out.relative_to(ROOT)}: ' + ('up to date' if same else 'out of date; run python scripts/write_umat.py'))
            status |= 0 if same else 1
        else:
            out.write_text(text)
            print(f'wrote {out.relative_to(ROOT)} ({len(text.splitlines())} lines)')
    return status


if __name__ == '__main__':
    sys.exit(main())
