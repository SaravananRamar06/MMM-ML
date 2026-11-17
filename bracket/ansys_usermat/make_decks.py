"""Write MAPDL batch decks for the bracket from the committed Workbench decks.

The Workbench project in bracket/ansys/ is not changed. This script reads its solver input
files (ds.dat) and writes three decks into an output folder outside the repository:

  elastic/  SYS-2 deck as written by Workbench (material "AlSi10Mg - E")
  ep_miso/  SYS deck as written by Workbench (material "AlSi10Mg - EP", TB,PLAS MISO)
  usermat/  SYS-2 deck with the JC-PINN USERMAT added after the materials, as the
            Workbench command snippet in umat/README.md does, plus OUTRES,SVAR,ALL

Mesh, supports, imposed UX = -2 mm, substeps and solver settings are the same in all three.
The element block is rewritten from the 2026 R1 COMPACT format to the standard SOLID format
so that MAPDL 2024 R1 can read it (same elements, same nodes).
Each deck ends with post_bracket.mac, which writes bracket_history.csv.

USERMAT constants are the study point of umat/README.md: 100 degC, 1e-4 /s, density 2592,
G 24541 MPa, nu 0.33 (assumed), ITEMP 0 (use constant 1, not the analysis temperature).

Usage: python bracket/ansys_usermat/make_decks.py OUTPUT_DIR
"""
import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DP0 = HERE.parent / 'ansys' / 'Elastic_files' / 'dp0'
SOURCES = {'elastic': DP0 / 'SYS-2' / 'MECH' / 'ds.dat',
           'ep_miso': DP0 / 'SYS' / 'MECH' / 'ds.dat',
           'usermat': DP0 / 'SYS-2' / 'MECH' / 'ds.dat'}

USERMAT_SNIPPET = """\
/com,*********** JC-PINN USERMAT (inserted by bracket/ansys_usermat/make_decks.py) ***********
! Study point: 100 degC, 1e-4 /s, density 2592 kg/m3 (phi = 4 %), G 24541 MPa, nu 0.33 (assumed).
! The solver uses the USERMAT stiffness (E = 2G(1+nu) = 65279 MPa), not MP,EX above.
TB,USER,1,1,7
TBTEMP,0
TBDATA,1,100,1.0E-4,2592,24541,0.33,0
TBDATA,7,0
TB,STATE,1,,4
"""


def expand_compact_eblocks(lines):
    """Rewrite 'eblock,21,COMPACT' (written by Workbench 2026 R1, not read by MAPDL 2024 R1)
    as the standard 'eblock,19,SOLID' layout with the same element numbers and nodes.

    COMPACT rows hold: element number, then the nodes. SOLID rows hold: mat, type, real, secnum,
    esys, birth/death, solid-model ref, shape flag, number of nodes, unused, element number,
    nodes 1-8, then nodes 9-20 on the next line. Attributes come from the 'MAT,.. $ TYPE,..'
    line that Workbench writes before each block.
    """
    out, attrs, i = [], {'MAT': 1, 'TYPE': 1, 'REAL': 1, 'SECNUM': 1, 'ESYS': 0}, 0
    while i < len(lines):
        line = lines[i]
        if line.startswith('MAT,') and '$' in line:
            for part in line.split('!')[0].split('$'):
                key, _, val = part.strip().partition(',')
                if key.upper() in attrs:
                    attrs[key.upper()] = int(val)
        if line.lower().startswith('eblock,') and 'compact' in line.lower():
            count = int(line.split(',')[4])
            assert lines[i + 1].strip().lower() == '(21i9)', lines[i + 1]
            out += [f'eblock,19,solid,,{count}     ! rewritten from COMPACT by make_decks.py', '(19i9)']
            i += 2
            n = 0
            while lines[i].strip() != '-1':
                vals = [int(v) for v in lines[i].split()]
                elem, nodes = vals[0], vals[1:]
                assert len(nodes) == 20, (elem, len(nodes))
                head = [attrs['MAT'], attrs['TYPE'], attrs['REAL'], attrs['SECNUM'], attrs['ESYS'], 0, 0, 0, 20, 0, elem]
                out.append(''.join(f'{v:9d}' for v in head + nodes[:8]))
                out.append(''.join(f'{v:9d}' for v in nodes[8:]))
                i += 1
                n += 1
            assert n == count, (n, count)
            out.append('-1')
            i += 1
            continue
        out.append(line)
        i += 1
    return out


def build(kind, text):
    lines = expand_compact_eblocks(text.split('\n'))
    out = []
    for line in lines:
        out.append(line)
        if kind == 'usermat' and line.startswith('/wb,mat,end'):
            out[-1:-1] = USERMAT_SNIPPET.rstrip('\n').split('\n')
        if kind == 'usermat' and line.strip().lower().startswith('outres,eppl,all'):
            out.append('outres,svar,all     ! state variables of the USERMAT (inserted)')
    if kind == 'usermat':
        assert any(l.startswith('TB,USER') for l in out), 'material block not found'
        assert any(l.startswith('outres,svar') for l in out), 'outres block not found'
    post = (HERE / 'post_bracket.mac').read_text()
    out += ['', '/com,*********** Post-processing (bracket/ansys_usermat/post_bracket.mac) ***********',
            f'_USERMAT = {1 if kind == "usermat" else 0}', post]
    return '\n'.join(out)


def main():
    dest = Path(sys.argv[1]).resolve()
    if HERE.parent.parent.resolve() in dest.parents or dest == HERE.parent.parent.resolve():
        sys.exit('write the decks outside the repository')
    for kind, src in SOURCES.items():
        text = src.read_text()
        (dest / kind).mkdir(parents=True, exist_ok=True)
        deck = build(kind, text)
        (dest / kind / 'bracket.dat').write_text(deck, newline='\n')
        print(kind, src.relative_to(HERE.parent.parent), 'sha256', hashlib.sha256(src.read_bytes()).hexdigest()[:16],
              '->', dest / kind / 'bracket.dat')


if __name__ == '__main__':
    main()
