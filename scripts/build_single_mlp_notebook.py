"""Package the tested single-MLP module and frozen inputs for Colab."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
def md(s):return dict(cell_type='markdown',metadata={},source=s.splitlines(keepends=True))
def code(s):return dict(cell_type='code',metadata={},execution_count=None,outputs=[],source=s.splitlines(keepends=True))
cells=[md('''# Single MLP and its exact prediction equation
Train one 5-16-16-1 tanh MLP on the fixed 36 training cases, select alpha by
three-case-fold CV, diagnose withheld temperature/rate groups with nested alpha
selection, and finally score 37 test cases. Seed 42. All preprocessing is fitted
within fitting cases. The final model/equation is locked before test measurements
are opened by the modeling code. Historical test exposure remains disclosed.

Upload the professor ZIP to Drive and set ZIP_SOURCE below. Run cells in order;
restart the runtime if requested after installation. Outputs go to a new Drive
folder. The learned equation is empirical, with fixed assumed phi=0.04 metadata.
All numerical coefficients are saved in equation.json; inference requires only NumPy.
Source stress units remain unconfirmed. Hosted Colab execution is not verified.
'''),code('%pip install -q numpy==2.2.6 scipy==1.15.3 scikit-learn==1.7.2 joblib==1.6.0 matplotlib==3.10.9\n'),code('''from google.colab import drive
drive.mount('/content/drive')
from pathlib import Path
from datetime import datetime, timezone
ZIP_SOURCE=Path('/content/drive/MyDrive/MMM-ML/TEAM_8_extracted_results_set_1.zip')
LOCAL_ROOT=Path('/content/single_mlp_study')
OUTPUT=Path('/content/drive/MyDrive/MMM-ML/single_mlp_runs')/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
''')]
files={p:(root/p).read_text(encoding='utf-8') for p in ['src/single_mlp.py','configs/single_mlp.json','data/split.json']}
cells.append(code(f'''import json,sys,zipfile
for relative,content in {files!r}.items():
    p=LOCAL_ROOT/relative
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(content,encoding='utf-8')
split=json.loads((LOCAL_ROOT/'data/split.json').read_text())
raw=LOCAL_ROOT/'TEAM_8_extracted_results_set_1'
with zipfile.ZipFile(ZIP_SOURCE) as archive:
    for relative in ['simulation_matrix.csv']+[f'simulation_{{i:04d}}/STR_STR.OUT' for i in split['train']+split['test']]:
        matches=[p for p in archive.namelist() if p.replace('\\\\','/')==relative or p.replace('\\\\','/').endswith('/'+relative)]
        if len(matches)!=1:raise ValueError(relative)
        p=raw/relative;p.parent.mkdir(parents=True,exist_ok=True)
        p.write_bytes(archive.read(matches[0]))
sys.path.insert(0,str(LOCAL_ROOT/'src'))
import single_mlp
from threadpoolctl import threadpool_limits
with threadpool_limits(limits=1):
    result=single_mlp.run(LOCAL_ROOT,OUTPUT)
print('Saved:',OUTPUT)
'''))
cells.append(code('''from IPython.display import display,Image
print('Training-only CV RMSE:',result['cv']['mean_rmse'])
print('Test RMSE:',result['test']['mean_rmse'])
print('Baseline test RMSE:',result['test_baseline']['mean_rmse'])
print('Equation equivalence:',result['checks']['equation_max_error'])
display(Image(filename=str(OUTPUT/'comparison.png')))
'''))
cells.append(md('''## Use the numerical equation
For raw inputs x=[T, log10(rate), density, G, E11], compute z=(x-mean)/scale,
h1=tanh(W1 z+b1), h2=tanh(W2 h1+b2), and
Svm=target_mean+target_scale*(w3.T h2+b3).
The JSON contains every coefficient. `single_mlp.equation_predict(eq, queries)`
evaluates batches of five-column inputs. This is the exact trained network formula.
No physical governing law, experimental validation or porosity dependence is implied.
Avoid claims beyond the observed loading family and E11=0.0002 to 0.0999.
'''))
for i,c in enumerate(cells):c['id']=f'mlp-{i}'
out=root/'notebooks/single_mlp_equation.ipynb'
out.write_text(json.dumps(dict(cells=cells,nbformat=4,nbformat_minor=5,metadata=dict(kernelspec=dict(name='python3',language='python',display_name='Python 3'))),indent=1)+'\n',encoding='utf-8')
print(out)
