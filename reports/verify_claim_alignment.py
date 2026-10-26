"""Read-only audit of delivered artifacts and supplied STEP metadata."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import json, sys, hashlib, re
from pathlib import Path
import joblib
import numpy as np

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'src'))
from query_runtime import QueryRuntime
manifest=json.loads((root/'data/manifest.json').read_text())
split=json.loads((root/'data/split.json').read_text())
by_id={m['id']:m for m in manifest}
keys=['temperature','log10_strain_rate','density','shear_modulus']
def inputs(ids):return np.array([[by_id[int(i)][k] for k in keys] for i in ids])
assert not set(split['train'])&set(split['test'])
assert set(split['train'])|set(split['test'])==set(by_id)
model=joblib.load(root/'runs/score/final_Svm/model.joblib')
runtime=QueryRuntime.load(root/'runs/score/final_Svm/model_numpy.npz')
with np.load(root/'runs/score/final_Svm/test_predictions.npz',allow_pickle=False) as z:
    P=model.predict(inputs(z['test_ids']))
    np.testing.assert_allclose(P,z['prediction'],atol=1e-10,rtol=1e-12)
    errors=np.sqrt(np.mean((P-z['truth'])**2,axis=1))
    assert set(map(int,z['test_ids']))==set(split['test'])
    actual_rmse=float(errors.mean())
    max_diff=float(np.max(np.abs(P-z['prediction'])))
    np.testing.assert_allclose(runtime.predict(inputs(z['test_ids'])),P,atol=1e-10,rtol=1e-12)
Xtr=inputs(split['train'])
Z=np.column_stack([np.repeat(Xtr,len(runtime.strain),axis=0),np.tile(runtime.strain,len(Xtr))])
np.testing.assert_allclose(model.xs.mean_,Z.mean(0),rtol=1e-12)
np.testing.assert_allclose(model.xs.var_,Z.var(0),rtol=1e-12)
candidates=[]
for path in sorted((root/'runs/score').glob('select_*_Svm.json')):
    s=json.loads(path.read_text())
    np.testing.assert_allclose(np.mean([r['rmse'] for r in s['per_case']['cv']]),s['cv_mean_rmse'])
    np.testing.assert_allclose(np.mean(list(s['loco_by_condition'].values())),s['loco_mean_rmse'])
    assert {r['id'] for r in s['per_case']['cv']}==set(split['train'])
    candidates.append({k:s[k] for k in ('candidate','cv_mean_rmse','loco_mean_rmse')})
steps=[]
for name in ('Rib Bracket.STEP','Bracket support.STEP'):
    path=root/name
    b=path.read_bytes(); text=b.decode('ascii')
    steps.append(dict(name=name,sha256=hashlib.sha256(b).hexdigest(),bytes=len(b),
                      schema='CONFIG_CONTROL_DESIGN' if 'CONFIG_CONTROL_DESIGN' in text else 'unknown',
                      solid_breps=len(re.findall(r'=\s*MANIFOLD_SOLID_BREP\s*\(',text)),
                      length_unit='mm' if 'SI_UNIT ( .MILLI., .METRE. )' in text else 'unknown',
                      keyword_hits={k:len(re.findall(r'\b'+k+r'\b',text,re.I)) for k in ('porosity','density','material','stress','lift','finite_element')}))
train_conditions={tuple(row[[0,1,3]]) for row in Xtr}
near_test=sum(tuple(row[[0,1,3]]) in train_conditions for row in inputs(split['test']))
result=dict(date='2026-10-26',prediction_contract='T, log10(rate), density, G, E11 -> Svm',
    train_cases=len(split['train']),test_cases=len(split['test']),networks=len(model.nets),
    hidden=list(model.hidden),alpha=model.alpha,seeds=[n.random_state for n in model.nets],
    final_model_iterations=[n.n_iter_ for n in model.nets],
    mean_test_curve_rmse=actual_rmse,saved_prediction_max_difference=max_diff,
    test_cases_sharing_T_rate_G_with_training=near_test,
    density_levels=sorted({m['density'] for m in manifest}),
    shear_modulus_levels=sorted({m['shear_modulus'] for m in manifest}),
    density_G_pairs=len({(m['density'],m['shear_modulus']) for m in manifest}),
    candidate_scores=candidates,step_metadata=steps,
    raw_data_present=(root/'TEAM_8_extracted_results_set_1/simulation_matrix.csv').exists(),
    prepared_cache_present=(root/'data/curves_Svm.npz').exists(),
    limits=['No training refit or source audit in this script.',
            'Historical CV and condition scores are checked for aggregation, not refitted.',
            'STEP text metadata inspection is not a CAD-kernel geometry validity check.'])
out=root/'reports/audits/alignment_evidence.json'
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
