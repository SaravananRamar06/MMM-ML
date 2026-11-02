"""Recompute saved single-MLP evidence and write its human-readable result."""
import csv
import json
from pathlib import Path
import sys
import joblib
import numpy as np
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'src'))
from single_mlp import scores,predict,equation_predict,queries,lookup,sha
out=root/'reports/single_mlp_20261102'
r=json.loads((out/'results.json').read_text());split=json.loads((root/'data/split.json').read_text())
assert r['train_ids']==split['train'] and r['test_ids']==split['test']
assert r['code_sha256']==sha(root/'src/single_mlp.py') and r['split_sha256']==sha(root/'data/split.json')
with (root/'TEAM_8_extracted_results_set_1/simulation_matrix.csv').open() as f:
    matrix={int(a['Simulation_ID']):a for a in csv.DictReader(f)}
def conditions(ids):
    return np.array([[float(matrix[i]['temperature']),np.log10(float(matrix[i]['strain_rate'])),float(matrix[i]['density']),float(matrix[i]['shear_modulus'])] for i in ids])
saved={}
for partition,ids in [('cv',r['train_ids']),('test',r['test_ids'])]:
    with (out/f'{partition}_predictions.csv').open() as f: rows=list(csv.DictReader(f))
    assert len(rows)==len(ids)*120
    assert [int(rows[i*120]['id']) for i in range(len(ids))]==ids
    grid=np.array([float(v['E11']) for v in rows[:120]])
    saved[partition]={k:np.array([float(v[k]) for v in rows]).reshape(len(ids),120) for k in ['Svm','MLP','lookup']}
    for key,target in [('MLP',partition),('lookup',partition+'_baseline')]:
        actual=scores(saved[partition]['Svm'],saved[partition][key])
        for metric,value in actual.items():np.testing.assert_allclose(value,r[target][metric],rtol=1e-12,atol=1e-12)
X=conditions(r['train_ids']);V=conditions(r['test_ids']);Y=saved['cv']['Svm']
for trial in r['trials']:
    seen=[]
    for f in trial['folds']:
        assert not set(f['fit_ids'])&set(f['validation_ids']);seen+=f['validation_ids']
        ix=[r['train_ids'].index(i) for i in f['fit_ids']]
        np.testing.assert_allclose(f['mean'],queries(X[ix],grid).mean(0),rtol=1e-13)
        np.testing.assert_allclose(f['target_mean'],Y[ix].mean(),rtol=1e-13)
        np.testing.assert_allclose(f['target_scale'],Y[ix].std(),rtol=1e-13)
    assert sorted(seen)==sorted(r['train_ids'])
for g in r['condition_holdouts']:
    assert not set(g['fit_ids'])&set(g['validation_ids'])
    for trial in g['selection']:
        for f in trial['folds']:
            assert set(f['fit_ids']+f['validation_ids'])==set(g['fit_ids'])
            assert not set(f['fit_ids'])&set(f['validation_ids'])
eq=json.loads((out/'equation.json').read_text());model=joblib.load(out/'model.joblib')
p=predict(model,V,grid);q=equation_predict(eq,queries(V,grid)).reshape(p.shape)
np.testing.assert_allclose(p,saved['test']['MLP'],rtol=0,atol=1e-10)
np.testing.assert_allclose(q,p,rtol=0,atol=1e-10)
np.testing.assert_array_equal(lookup(X,Y,V),saved['test']['lookup'])
for rel,h in r['checks']['protected_artifacts_unchanged'].items():assert sha(root/rel)==h
for a in r['training_audit']+r['test_audit']:
    assert a['sha256']==sha(root/f"TEAM_8_extracted_results_set_1/simulation_{a['id']:04d}/STR_STR.OUT")
nb=json.loads((root/'notebooks/single_mlp_equation.ipynb').read_text(encoding='utf-8'))
for c in nb['cells']:
    s=''.join(c['source'])
    if c['cell_type']=='code' and not s.startswith('%'):compile(s,'notebook-cell','exec')
assert repr((root/'src/single_mlp.py').read_text(encoding='utf-8')) in ''.join(nb['cells'][3]['source'])
verification=dict(passed=True,metric_reconstruction=True,fold_scaler_isolation=True,nested_group_isolation=True,
    model_and_equation_reload_max_difference=float(np.max(np.abs(q-p))),source_and_original_artifact_hashes_match=True,
    notebook_cells_compile_and_embed_tested_source=True,hosted_colab_verified=False)
(out/'verification.json').write_text(json.dumps(verification,indent=2)+'\n')
worst=r['test_ids'][int(np.argmax(r['test']['case_rmse']))]
warnings_total=sum(len(f['warnings']) for t in r['trials'] for f in t['folds'])
report=f'''# Single MLP test - 2 November 2026

Fresh single 5-16-16-1 tanh network, seed 42, **385 learned parameters**.
Alpha selected on the 36 training cases: **{r['selected_alpha']}**.
This is a new fit, distinct from the earlier delivered five-network ensemble.

- Three-fold training-case validation mean curve RMSE: **{r['cv']['mean_rmse']:.6f}**.
- Same-fold curve-copy baseline mean RMSE: **{r['cv_baseline']['mean_rmse']:.6f}**.
- Final 37-case test mean/median/worst RMSE: **{r['test']['mean_rmse']:.6f} / {r['test']['median_rmse']:.6f} / {r['test']['worst_rmse']:.6f}**.
- Test mean MAE: **{r['test']['mean_mae']:.6f}**. Worst test case: **{worst}**.
- Curve-copy baseline test mean RMSE: **{r['test_baseline']['mean_rmse']:.6f}**.

All errors above are in source stress units, whose physical units remain unconfirmed.
The split stays 36/37 simulation cases, never rows. Each curve contributes 120
E11 queries from 0.0002 to 0.0999. All scalers are fitted on fitting cases only.
The architecture and seed are fixed before test scoring. Alpha candidates are
0.0001, 0.001 and 0.01; three case folds use seed 42. The objective is standard
scikit-learn MLP regression with L2 regularization. Optimizer: L-BFGS, max_iter=5000,
max_fun=50000, tol=1e-9. Training-side selection warnings: {warnings_total};
final fit warnings: {r['final_fit']['warnings']}.

## Generalization checks

These group holdouts use only the 36 training cases. Alpha is reselected inside
the remaining cases for each holdout; no omitted-condition targets enter fitting
or selection. Each group reports mean curve RMSE, followed by the lookup baseline:

'''
for g in r['condition_holdouts']:
    report+=f"- T={g['temperature']:g}, log10(rate)={g['log10_rate']:g}: **{g['mlp']['mean_rmse']:.6f}**, baseline {g['baseline']['mean_rmse']:.6f}; {len(g['validation_ids'])} omitted cases.\n"
report+=f'''
Case 60 stays included; it is the sole training example in its temperature/rate
group. Random-case interpolation scores and new-condition scores answer different
questions. The final test set has historical exposure, so it is not a new blind
test. Neither the scores nor the equation establish experimental or physical
validation, universal model superiority, or a porosity response.

![Test and difficult-case comparison](comparison.png)

## Exact prediction equation

For x=[T,log10(rate),density,G,E11], let z=(x-mean)/scale.

`Svm = target_mean + target_scale * (w3.T tanh(W2 tanh(W1 z+b1)+b2)+b3)`

Every numerical coefficient is in [equation.json](equation.json). W1 is 16x5,
W2 is 16x16 and w3 has 16 entries. This empirical equation exactly represents the
trained MLP; it is not a constitutive law derived from physics. Fixed porosity
0.04 is assumed metadata, not a learned input. No missing physical constants are
invented. Use the source stress/strain conventions and observed loading family.

Equation reload maximum difference from sklearn: {r['checks']['equation_max_error']:.3g}.
Joblib reload maximum difference: {r['checks']['reload_max_error']:.3g}.
Existing delivered artifact hashes are unchanged. All source hashes, saved metrics,
fold scaler statistics, nested holdout isolation and numerical equation predictions
were independently verified by scripts/verify_single_mlp.py.

## Reproduce

Run `python src/single_mlp.py --output reports/NEW_DIRECTORY` from the repository.
Run `python scripts/verify_single_mlp.py` to check this saved run.
The new notebook is `notebooks/single_mlp_equation.ipynb`; set its Drive ZIP path
and run in order. Its embedded computation is the tested local module. Hosted
Colab execution and Drive access were not verified here.

Versions: {r['versions']}. Fit/selection/diagnostic runtime: {r['elapsed_seconds']:.1f} seconds.
'''
(out/'README.md').write_text(report,encoding='utf-8')
print(json.dumps(verification,indent=2))
