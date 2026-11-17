"""Rebuild and execute both notebooks locally (nbclient), and record the result.

* notebooks/jc_pinn_explained.ipynb is executed in place and saved with its outputs.
* notebooks/jc_pinn_colab.ipynb is saved clean (no outputs, MODE = 'PREDICT'). Copies are executed in PREDICT mode and,
  if a raw-data folder is given, in FAST mode, which must reproduce the locked model weight for weight.
The result is written to reports/jc_pinn_20261107/notebook_execution.json.

Usage:  python scripts/run_notebooks.py [RAW_FOLDER]
RAW_FOLDER defaults to work/raw_from_committed_curves (rebuilt by scripts/build_raw_from_committed_curves.py).
"""
import hashlib
import json
import platform
import subprocess
import sys
import time
from pathlib import Path

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / 'reports/jc_pinn_20261107'
RAW = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'work/raw_from_committed_curves'
WORK = ROOT / 'work/nbrun'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def execute(nb, cwd, timeout=3600):
    t = time.time()
    NotebookClient(nb, timeout=timeout, kernel_name='python3', resources={'metadata': {'path': str(cwd)}}).execute()
    errors = sum(o.get('output_type') == 'error' for c in nb.cells for o in c.get('outputs', []))
    figures = sum('image/png' in o.get('data', {}) for c in nb.cells for o in c.get('outputs', []))
    return {'errors': errors, 'seconds': round(time.time() - t), 'figures': figures}


def main():
    for builder in ('build_jc_pinn_notebook.py', 'build_jc_pinn_explained_notebook.py'):
        subprocess.run([sys.executable, str(ROOT / 'scripts' / builder)], check=True, cwd=ROOT)

    record = {'executed_with': f'nbclient, local {platform.system()} kernel (Python {platform.python_version()}); not hosted Colab/Kaggle',
              'data': str(RAW.relative_to(ROOT)) if RAW.is_relative_to(ROOT) else str(RAW)}

    explained = ROOT / 'notebooks/jc_pinn_explained.ipynb'
    nb = nbformat.read(explained, as_version=4)
    record['explained'] = execute(nb, ROOT / 'notebooks')
    nbformat.write(nb, explained)
    record['explained']['notebook_sha256'] = sha(explained)

    colab = ROOT / 'notebooks/jc_pinn_colab.ipynb'
    record['colab_notebook_sha256'] = sha(colab)
    record['modes'] = {}
    for mode in ('PREDICT', 'FAST'):
        if mode == 'FAST' and not RAW.exists():
            record['modes'][mode] = 'skipped: no raw folder'
            continue
        nb = nbformat.read(colab, as_version=4)
        for cell in nb.cells:
            if cell.cell_type == 'code' and "MODE = 'PREDICT'" in cell.source:
                cell.source = cell.source.replace("MODE = 'PREDICT'", f"MODE = '{mode}'").replace("DATA_PATH = ''", f"DATA_PATH = {str(RAW)!r}")
        cwd = WORK / mode
        cwd.mkdir(parents=True, exist_ok=True)
        record['modes'][mode] = execute(nb, cwd)
        nbformat.write(nb, cwd / 'executed.ipynb')

    fast = sorted((WORK / 'FAST/jc_pinn_work/runs').glob('*/equation.json')) if (WORK / 'FAST').exists() else []
    if fast:
        new, ref = json.loads(fast[-1].read_text()), json.loads((RUN / 'equation.json').read_text())
        res = json.loads((fast[-1].parent / 'results.json').read_text())
        record['fast_reproduction'] = {
            'test_mean_rmse': res['test']['jc_pinn']['mean_rmse'],
            'reference_test_mean_rmse': json.loads((RUN / 'results.json').read_text())['test']['jc_pinn']['mean_rmse'],
            'members_identical_to_locked_equation': new['members'] == ref['members'],
            'theta_identical': new['theta'] == ref['theta']}
    (RUN / 'notebook_execution.json').write_text(json.dumps(record, indent=2) + '\n', newline='\n')  # LF on every OS: reports/** is byte-checked (.gitattributes)
    print(json.dumps(record, indent=2))


if __name__ == '__main__':
    main()
