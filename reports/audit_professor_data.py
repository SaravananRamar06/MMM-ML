"""Audit supplied raw histories without modifying data or delivered models."""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[k]='1'
import csv, hashlib, json, sys, time, warnings, zipfile
from pathlib import Path
from datetime import datetime, timezone
import numpy as np
import joblib
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from data import STRAIN_GRID, COLS
from models import QueryMLP, LookupBaseline
raw=ROOT/'TEAM_8_extracted_results_set_1'
out=ROOT/'reports/audits'/('professor-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
out.mkdir(parents=True)
matrix={int(r['Simulation_ID']):r for r in csv.DictReader((raw/'simulation_matrix.csv').open())}
manifest={m['id']:m for m in json.loads((ROOT/'data/manifest.json').read_text())}
folder=ROOT/'runs/score/final_Svm'
protected={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.iterdir() if p.is_file()}
cases=[]; ids=[]; xs=[]; ys=[]; headers=set()
for n,path in enumerate(sorted(raw.glob('simulation_*/STR_STR.OUT')),1):
    sid=int(path.parent.name.split('_')[1]); meta=matrix[sid]
    headers.add(tuple(path.open().readline().split()))
    a=np.loadtxt(path,skiprows=1)
    assert a.ndim==2 and a.shape[1]==16 and np.isfinite(a).all(),sid
    strain=a[:,3]; stress=a[:,2]
    assert np.all(np.diff(strain)>0) and strain[0]<=STRAIN_GRID[0]<STRAIN_GRID[-1]<=strain[-1],sid
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    assert digest==manifest[sid]['sha256'],(sid,'source hash mismatch')
    x=[float(meta['temperature']),np.log10(float(meta['strain_rate'])),float(meta['density']),float(meta['shear_modulus'])]
    np.testing.assert_array_equal(x,[manifest[sid][k] for k in ('temperature','log10_strain_rate','density','shear_modulus')])
    s11,s22,s33,s23,s13,s12=a[:,9:15].T
    vm=np.sqrt(0.5*((s11-s22)**2+(s22-s33)**2+(s33-s11)**2)+3*(s23*s23+s13*s13+s12*s12))
    cases.append(dict(id=sid,rows=len(a),initial_stress=float(stress[0]),final_stress=float(stress[-1]),
                      strain_start=float(strain[0]),strain_end=float(strain[-1]),
                      rate_time_max_abs_difference=float(np.max(np.abs(strain-float(meta['strain_rate'])*a[:,0]))),
                      von_mises_max_relative_difference=float(np.max(np.abs(stress-vm)/np.maximum(np.abs(stress),1e-12))),
                      equivalent_strain_decreases=int(np.sum(np.diff(a[:,1])<0)),
                      temperature_range=[float(a[:,-1].min()),float(a[:,-1].max())]))
    ids.append(sid);xs.append(x);ys.append(np.interp(STRAIN_GRID,strain,stress))
    if n%10==0:print(f'Checked raw histories: {n}',flush=True)
assert len(headers)==1 and next(iter(headers))==tuple(COLS)
ids,X,Y=np.array(ids),np.array(xs),np.array(ys)
assert set(ids)==set(manifest)
split=json.loads((ROOT/'data/split.json').read_text())
tr,te=np.isin(ids,split['train']),np.isin(ids,split['test'])
assert (int(tr.sum()),int(te.sum()))==(36,37) and not np.any(tr&te)
saved=joblib.load(folder/'model.joblib')
Z=saved._inputs(X[tr])
np.testing.assert_allclose(saved.xs.mean_,Z.mean(0),rtol=1e-12)
np.testing.assert_allclose(saved.xs.var_,Z.var(0),rtol=1e-12)
np.testing.assert_allclose([saved.ym,saved.ys],[Y[tr].mean(),Y[tr].std()],rtol=1e-12)
P=saved.predict(X[te])
with np.load(folder/'test_predictions.npz',allow_pickle=False) as z:
    np.testing.assert_array_equal(z['test_ids'],ids[te])
    truth_difference=float(np.max(np.abs(Y[te]-z['truth'])))
    np.testing.assert_allclose(Y[te],z['truth'],rtol=0,atol=1e-12)
    prediction_difference=float(np.max(np.abs(P-z['prediction'])))
    np.testing.assert_allclose(P,z['prediction'],rtol=1e-12,atol=1e-10)
rmse=np.sqrt(np.mean((P-Y[te])**2,axis=1))
baseline=LookupBaseline().fit(X[tr],Y[tr]).predict(X[te])
effects={}
for j,key in enumerate(('temperature','log10_rate','density','G')):
    contrasts=[]
    for i in range(len(X)):
        for l in range(i+1,len(X)):
            same=X[i]==X[l];same[j]=True
            if same.all() and X[i,j]!=X[l,j]:contrasts.append(float(np.sqrt(np.mean((Y[i]-Y[l])**2))))
    effects[key]={'matched_pairs':len(contrasts),'median_curve_difference_rmse':float(np.median(contrasts)),
                  'max_curve_difference_rmse':float(np.max(contrasts))}
print('Raw data, preprocessing and saved predictions checked; refitting frozen settings separately...',flush=True)
tick=time.perf_counter()
with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter('always')
    refit=QueryMLP(hidden=saved.hidden,alpha=saved.alpha,n_init=saved.n_init,seed=saved.seed).fit(X[tr],Y[tr])
seconds=time.perf_counter()-tick
refit_test=refit.predict(X[te])
refit_difference=float(np.max(np.abs(refit.predict(X)-saved.predict(X))))
weight_difference=max(float(np.max(np.abs(a-b))) for n1,n2 in zip(saved.nets,refit.nets) for a,b in zip(n1.coefs_+n1.intercepts_,n2.coefs_+n2.intercepts_))
assert protected=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.iterdir() if p.is_file()}
archive=ROOT/'TEAM_8_extracted_results_set_1.zip'
with zipfile.ZipFile(archive) as z:
    archive_files=[i.filename for i in z.infolist() if not i.is_dir()]
result=dict(completed_at=datetime.now(timezone.utc).isoformat(),
    archive_files=archive_files,matrix_columns=list(next(iter(matrix.values())).keys()),
    output_columns=list(next(iter(headers))),planned_cases=len(matrix),available_cases=len(ids),
    total_rows=sum(c['rows'] for c in cases),all_finite=True,all_source_hashes_match_manifest=True,
    missing_ids=sorted(set(matrix)-set(map(int,ids))),
    temperature_counts={str(t):int(np.sum(X[:,0]==t)) for t in sorted({float(r['temperature']) for r in matrix.values()})},
    raw_vs_saved_test_truth_max_difference=truth_difference,saved_prediction_max_difference=prediction_difference,
    final_test_mean_curve_rmse=float(rmse.mean()),worst_curve_rmse=float(rmse.max()),
    lookup_baseline_mean_curve_rmse=float(np.sqrt(np.mean((baseline-Y[te])**2,axis=1)).mean()),
    constant_training_mean_curve_baseline_rmse=float(np.sqrt(np.mean((Y[tr].mean(0)[None]-Y[te])**2,axis=1)).mean()),
    train_input_and_target_scalers_verified=True,
    max_von_mises_relative_difference=max(c['von_mises_max_relative_difference'] for c in cases),
    all_curves_end_below_initial=all(c['final_stress']<c['initial_stress'] for c in cases),
    equivalent_strain_decreasing_cases=[c['id'] for c in cases if c['equivalent_strain_decreases']],
    descriptive_factor_contrasts=effects,
    refit={'elapsed_seconds':seconds,'max_weight_difference':weight_difference,
           'max_prediction_difference_all_cases':refit_difference,
           'test_mean_curve_rmse':float(np.sqrt(np.mean((refit_test-Y[te])**2,axis=1)).mean()),
           'warnings':[str(w.message) for w in caught],
           'iterations':[n.n_iter_ for n in refit.nets]},
    delivered_artifacts_unchanged=True,cases=cases,
    limitations=['The refit uses frozen settings and existing data, not an independent blind validation.',
                 'Factor contrasts are descriptive differences, not causal porosity effects.',
                 'Source units, pore interpretation and generating constitutive law are not supplied.'])
(out/'results.json').write_text(json.dumps(result,indent=2))
# Reconstructed labels stay in ignored local scratch space, not the evidence commit.
cache=ROOT/'work'/out.name
cache.mkdir(parents=True,exist_ok=True)
np.savez_compressed(cache/'audited_curves.npz',ids=ids,X=X,Y=Y,strain=STRAIN_GRID)
print(json.dumps({k:v for k,v in result.items() if k not in ('cases','archive_files')},indent=2),flush=True)
print('Evidence: '+str(out),flush=True)
