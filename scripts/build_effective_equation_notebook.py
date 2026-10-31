"""Export the tested equation checker as a self-contained, physics-only notebook."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = (ROOT/'src/effective_equation.py').read_text()
config = json.loads((ROOT/'configs/effective_equation.json').read_text())
split = json.loads((ROOT/'data/split.json').read_text())


def md(text):
    return dict(cell_type='markdown', metadata={}, source=text.splitlines(keepends=True))


def code(text):
    return dict(cell_type='code', execution_count=None, metadata={}, outputs=[], source=text.splitlines(keepends=True))


cells = [md('''# Check the effective governing equation before MLP/PINN

This notebook fits no neural network. It checks two **assumed effective response laws**
using only the fixed **36 training cases**. The other 37 cases remain excluded.

Candidate: `Svm = R + A exp(-k (E11/0.1)^n)`; simple version fixes n=1.
The decreasing branch and E11 coordinate are our adaptation of an exponential-power
constitutive family, not a recovered source law or established pore mechanism.
Reference: https://doi.org/10.1016/0022-5096(75)90018-6
VPSC definition lead: https://github.com/lanl/VPSC_code

Upload the professor's existing ZIP to Google Drive. Set its path below.
The extractor reads only the matrix and 36 whitelisted histories from that ZIP.
All results are saved to a new Drive folder. Porosity 4% stays assumed metadata.
The final test partition has historical exposure; it is not a new blind test.

Run the cells in order. Hosted Colab execution has not been verified by the author;
the embedded checker and its mathematical/isolation tests were run locally.
'''), code('''%pip install -q numpy==2.2.6 scipy==1.15.3 scikit-learn==1.7.2 matplotlib==3.10.9
'''), md('Restart the runtime if Colab requests it after installing, then continue here.'), code('''from google.colab import drive
drive.mount('/content/drive')
'''), code('''from pathlib import Path
from datetime import datetime, timezone
ZIP_SOURCE = Path('/content/drive/MyDrive/MMM-ML/TEAM_8_extracted_results_set_1.zip')
LOCAL_ROOT = Path('/content/mmm_equation_check')
OUTPUT = Path('/content/drive/MyDrive/MMM-ML/equation_checks') / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
'''), md('''## Reproduce the frozen checker and case split

Scalers and coefficients are fitted within each fitting fold. Three case folds,
three initializations and alpha values 0.0001, 0.01, 1 are compared. Selection uses
development CV, so these scores are not an unbiased final accuracy estimate.
Condition-group holdouts are additional diagnostics using the selected alpha.
Screening limits: mean case-normalized RMSE <5%, worst <10%, improvement over
the fitting-mean-curve reference, optimizer convergence, and numerical checks.
These research screening limits were fixed before this qualification run.
'''), code(f'''import json, sys, zipfile, hashlib
LOCAL_ROOT.mkdir(parents=True, exist_ok=True)
for name, content in {repr({'configs/effective_equation.json':config, 'data/split.json':split})}.items():
    path = LOCAL_ROOT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and json.loads(path.read_text()) != content:
        raise ValueError(f'Existing configuration differs: {{path}}')
    path.write_text(json.dumps(content, indent=2)+'\\n')
source = {source!r}
assert hashlib.sha256(source.encode()).hexdigest() == {hashlib.sha256(source.encode()).hexdigest()!r}
module_dir = LOCAL_ROOT/'src'
module_dir.mkdir(exist_ok=True)
(module_dir/'effective_equation.py').write_text(source)
sys.path.insert(0, str(module_dir))
import effective_equation as equation
'''), code('''split = json.loads((LOCAL_ROOT/'data/split.json').read_text())
raw = LOCAL_ROOT/'TEAM_8_extracted_results_set_1'
members = ['simulation_matrix.csv'] + [f'simulation_{i:04d}/STR_STR.OUT' for i in split['train']]
with zipfile.ZipFile(ZIP_SOURCE) as archive:
    names = archive.namelist()
    for relative in members:
        matches = [name for name in names if name.replace('\\\\','/').rstrip('/').endswith('/'+relative)
                   or name.replace('\\\\','/') == relative]
        if len(matches) != 1:
            raise ValueError(f'Expected one archive member for {relative}: {matches}')
        destination = raw/relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(archive.read(matches[0]))
assert sorted(int(p.name.split('_')[1]) for p in raw.glob('simulation_*') if p.is_dir()) == sorted(split['train'])
print('Extracted matrix and exactly 36 training histories. No test history extracted.')
'''), code('''result = equation.run(LOCAL_ROOT, OUTPUT)
assert set(result['raw_history_ids_opened']) == set(split['train'])
assert not set(result['raw_history_ids_opened']) & set(split['test'])
print('Decision:', result['decision'])
print('Saved to:', OUTPUT)
'''), code('''from IPython.display import display, Image
for family, record in result['families'].items():
    scores = record['cv']
    print(f"{family}: mean normalized RMSE {100*scores['mean_nrmse']:.2f}%; worst {100*scores['worst_nrmse']:.2f}%")
    print('Screening:', record['screening'])
display(Image(filename=str(OUTPUT/'case_validation.png')))
'''), md('''## Interpret the decision

A passing fit would support only an effective equation within the observed loading
family and E11 interval 0.0002–0.0999. It would not identify the original constitutive
law, establish experimental validity, or demonstrate a porosity effect.

The local qualification failed both candidates. In particular, case 60 is the only
training case at matrix temperature 200 and rate 1e-5; the remaining data did not
predict it reliably. Retain it and report the limitation. If a repeat run also fails,
continue equation research before constructing the MLP/PINN comparison.

The differential residual is
`dSvm/dE11 + (k*n/0.1)*(E11/0.1)^(n-1)*(Svm-R) = 0`.
An initial value at E11=0.0002 must come from the condition-dependent equation,
never from a validation/test case's measured stress. E11 is not renamed plastic strain.
''')]
notebook = dict(cells=cells, metadata=dict(kernelspec=dict(display_name='Python 3', language='python', name='python3'),
    language_info=dict(name='python'), equation_source_sha256=hashlib.sha256(source.encode()).hexdigest()),
    nbformat=4, nbformat_minor=5)
for i, cell in enumerate(cells):
    cell['id'] = f'equation-{i:02d}'
out = ROOT/'notebooks/effective_equation_check.ipynb'
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(notebook, indent=1)+'\n')
print(out)
