"""Write the *_out_key_lines.txt evidence file for one MAPDL bracket run.

Usage: python bracket/ansys_usermat/extract_key_lines.py RUN_DIR LABEL OUT_TXT
RUN_DIR holds bracket.dat and bracket.out. The file lists the deck headers (mesh, material, node sets, load),
the solver lines that matter (user library, model size, substeps, bisections, messages, version, wall time)
with their line numbers, then the last 60 lines of bracket.out. plot_mesh.py and plot_mesh_ep.py read it.
"""
import re
import sys
from pathlib import Path

DECK = re.compile(r'^(nblock|eblock|TBDATA|CMBLOCK|d,all,u[xy]|nsel,r,loc)', re.I)
KEY = re.compile(r'User Link path|linked by Licensee|Total number of (nodes|elements)|LOAD STEP .* SUBSTEP|'
                 r'BISECTION|\*\*\* ERROR|MESSAGES ENCOUNTERED|Release:|Compiler:|Elapsed Time')


def main():
    run, label, out = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
    deck = (run / 'bracket.dat').read_text().split('\n')
    lines = (run / 'bracket.out').read_text(errors='replace').split('\n')
    txt = [f'# bracket.out ({label}), MAPDL 2024 R1 batch - deck headers, key lines, then the last 60 lines',
           f'# full file: {len(lines)} lines']
    txt += [f'deck: {l}' for l in deck if DECK.match(l.strip())]
    txt.append('')
    txt += [f'{i + 1:6d}: {l}' for i, l in enumerate(lines) if KEY.search(l)]
    txt += ['', '# last 60 lines'] + lines[-60:]
    out.write_text('\n'.join(txt) + '\n', newline='\n')


if __name__ == '__main__':
    main()
