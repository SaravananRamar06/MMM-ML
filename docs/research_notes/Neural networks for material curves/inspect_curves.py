"""Read-only architectural data inspection; no model fitting or case split.

Run: python3 'research_notes/Neural networks for material curves/inspect_curves.py'
All generated files stay alongside this script.
"""
from pathlib import Path
import csv
import json
import numpy as np

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
RAW = ROOT / 'TEAM_8_extracted_results_set_1'
rows = list(csv.DictReader((RAW / 'simulation_matrix.csv').open()))
# Small margin below 0.1 avoids extrapolating case 60's rounded E11 endpoint.
grid = np.linspace(0.0001, 0.0999999, 501)
cases, curves, conditions, ids = [], [], [], []
header = None
for meta in rows:
    sid = int(meta['Simulation_ID'])
    file = RAW / f'simulation_{sid:04d}' / 'STR_STR.OUT'
    if not file.exists():
        continue
    current_header = file.open().readline().split()
    if header is None:
        header = current_header
    assert current_header == header
    a = np.loadtxt(file, skiprows=1)
    time, evm, svm, e11 = a[:, 0], a[:, 1], a[:, 2], a[:, 3]
    rate = float(meta['strain_rate'])
    s11, s22, s33, s23, s13, s12 = a[:, 9:15].T
    vm_from_components = np.sqrt(0.5 * ((s11-s22)**2 + (s22-s33)**2 + (s33-s11)**2)
                                 + 3*(s12*s12+s23*s23+s13*s13))
    ee = a[:, 3:9]
    dev = ee[:, :3] - ee[:, :3].mean(axis=1, keepdims=True)
    eq_tensor = np.sqrt((2/3)*(np.sum(dev*dev, axis=1)+2*np.sum(ee[:, 3:]**2, axis=1)))
    c = dict(id=sid, rows=len(a), finite=bool(np.isfinite(a).all()),
             conditions={k:float(v) for k,v in meta.items() if k!='Simulation_ID'},
             time_start=float(time[0]), time_end=float(time[-1]),
             e11_start=float(e11[0]), e11_end=float(e11[-1]),
             e11_nonincreasing=int(np.sum(np.diff(e11)<=0)),
             e11_rate_time_max_abs_error=float(np.max(np.abs(e11-time*rate))),
             evm_start=float(evm[0]), evm_end=float(evm[-1]),
             evm_negative_increments=int(np.sum(np.diff(evm)<-1e-12)),
             svm_initial=float(svm[0]), svm_final=float(svm[-1]),
             svm_min=float(svm.min()), svm_max=float(svm.max()),
             svm_peak_e11=float(e11[svm.argmax()]),
             svm_component_max_rel_error=float(np.max(np.abs(svm-vm_from_components)/np.maximum(np.abs(svm),1e-12))),
             evm_tensor_max_rel_error=float(np.max(np.abs(evm-eq_tensor)/np.maximum(np.abs(evm),1e-12))),
             temp_range=[float(a[:,-1].min()),float(a[:,-1].max())])
    cases.append(c)
    if e11[0] <= grid[0] and e11[-1] >= grid[-1] and np.all(np.diff(e11)>0):
        curves.append(np.interp(grid,e11,svm))
        conditions.append([float(meta[k]) for k in ['temperature','strain_rate','density','shear_modulus']])
        ids.append(sid)
Y=np.array(curves); X=np.array(conditions)
centered=Y-Y.mean(axis=0)
u,s,vt=np.linalg.svd(centered,full_matrices=False)
energy=s*s
cumulative=np.cumsum(energy)/energy.sum()
normal = np.array(ids)!=60
sn = np.linalg.svd(Y[normal]-Y[normal].mean(axis=0),compute_uv=False)
normal_cumulative=np.cumsum(sn*sn)/np.sum(sn*sn)
reconstruction=[]
for rank in range(1,6):
    approx=(u[:,:rank]*s[:rank])@vt[:rank]
    errs=np.sqrt(np.mean((centered-approx)**2,axis=1))
    reconstruction.append(dict(rank=rank,mean_case_rmse=float(errs.mean()),
                               max_case_rmse=float(errs.max()),worst_case=int(ids[errs.argmax()])))
effects={}
for j,key in enumerate(['temperature','strain_rate','density','shear_modulus']):
    pairs=[]
    for k in range(len(ids)):
        for l in range(k+1,len(ids)):
            same=(X[k]==X[l]);same[j]=True
            if same.all() and X[k,j]!=X[l,j]:
                pairs.append([int(ids[k]),int(ids[l]),float(np.sqrt(np.mean((Y[k]-Y[l])**2)))])
    effects[key]={'pairs':len(pairs),'rmse_min':min(x[2] for x in pairs),
                  'rmse_median':float(np.median([x[2] for x in pairs])),
                  'rmse_max':max(x[2] for x in pairs)}
dist=[]
for k in range(len(ids)):
    for l in range(k+1,len(ids)):
        dist.append((float(np.sqrt(np.mean((Y[k]-Y[l])**2))),int(ids[k]),int(ids[l])))
summary=dict(matrix_rows=len(rows),available=len(cases),total_rows=sum(x['rows'] for x in cases),
             header=header,all_finite=all(x['finite'] for x in cases),
             nonmonotonic_e11_ids=[x['id'] for x in cases if x['e11_nonincreasing']],
             nonmonotonic_evm_ids=[x['id'] for x in cases if x['evm_negative_increments']],
             max_rate_time_error=max(x['e11_rate_time_max_abs_error'] for x in cases),
             full_grid_cases=len(ids),common_grid=[float(grid[0]),float(grid[-1]),len(grid)],
             final_below_initial_ids=[x['id'] for x in cases if x['svm_final']<x['svm_initial']],
             svm_component_rel_error_max=max(x['svm_component_max_rel_error'] for x in cases),
             evm_tensor_rel_error_max=max(x['evm_tensor_max_rel_error'] for x in cases),
             exact_curve_duplicates=[x for x in dist if x[0]==0],nearest_curves=sorted(dist)[:5],
             descriptive_full_dataset_pca_cumulative=cumulative[:10].tolist(),
             descriptive_pca_without_case60_cumulative=normal_cumulative[:5].tolist(),
             descriptive_full_dataset_pca_reconstruction=reconstruction,
             condition_effects=effects,cases=cases)
(OUT/'curve_inspection.json').write_text(json.dumps(summary,indent=2)+'\n')
np.savez_compressed(OUT/'curve_inspection_samples.npz',ids=np.array(ids),conditions=X,e11=grid,svm=Y)
print(json.dumps({k:v for k,v in summary.items() if k!='cases'},indent=2))
