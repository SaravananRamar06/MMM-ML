"""Fresh single-MLP experiment and exact empirical equation export; no physics loss."""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import platform
import time
import warnings

import joblib
import numpy as np
import scipy
import sklearn
from sklearn.model_selection import KFold
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_cases(raw, ids, grid):
    raw = Path(raw)
    with (raw/'simulation_matrix.csv').open() as f:
        matrix = {int(r['Simulation_ID']):r for r in csv.DictReader(f)}
    X, Y, audit = [], [], []
    for i in ids:
        path = raw/f'simulation_{i:04d}'/'STR_STR.OUT'
        with path.open() as f:
            assert f.readline().split() == 'TIME Evm Svm E11 E22 E33 E23 E13 E12 SCAU11 SCAU22 SCAU33 SCAU23 SCAU13 SCAU12 TEMP'.split()
        a = np.loadtxt(path, skiprows=1, usecols=(2,3))
        if not np.isfinite(a).all() or not np.all(np.diff(a[:,1]) > 0):
            raise ValueError(f'Invalid curve {i}')
        if grid[0] < a[0,1] or grid[-1] > a[-1,1]:
            raise ValueError(f'Curve {i} would require extrapolation')
        r = matrix[i]
        X.append([float(r['temperature']),np.log10(float(r['strain_rate'])),float(r['density']),float(r['shear_modulus'])])
        Y.append(np.interp(grid,a[:,1],a[:,0]))
        audit.append(dict(id=i,sha256=sha(path),rows=len(a)))
    return np.array(X),np.array(Y),audit


def queries(X, grid):
    return np.c_[np.repeat(X,len(grid),axis=0),np.tile(grid,len(X))]


def fit(X,Y,grid,alpha,cfg):
    z = queries(X,grid)
    xs = StandardScaler().fit(z)
    ym,ys = float(Y.mean()),float(Y.std())
    if ys <= 0:
        raise ValueError('Response scale must be positive')
    net = MLPRegressor(hidden_layer_sizes=tuple(cfg['hidden']),activation='tanh',solver='lbfgs',
        alpha=alpha,random_state=cfg['seed'],max_iter=cfg['max_iter'],max_fun=cfg['max_fun'],tol=cfg['tol'])
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        net.fit(xs.transform(z),(Y.ravel()-ym)/ys)
    model = dict(net=net,xs=xs,ym=ym,ys=ys)
    info = dict(alpha=alpha,iterations=int(net.n_iter_),loss=float(net.loss_),
        warnings=[str(w.message) for w in caught],mean=xs.mean_.tolist(),scale=xs.scale_.tolist(),
        target_mean=ym,target_scale=ys)
    return model,info


def predict(model,X,grid):
    return (model['net'].predict(model['xs'].transform(queries(X,grid)))*model['ys']+model['ym']).reshape(len(X),len(grid))


def export_equation(model):
    n = model['net']
    return dict(input_order=['temperature','log10_rate','density','G','E11'],
        mean=model['xs'].mean_.tolist(),scale=model['xs'].scale_.tolist(),
        target_mean=model['ym'],target_scale=model['ys'],
        W1=n.coefs_[0].T.tolist(),b1=n.intercepts_[0].tolist(),
        W2=n.coefs_[1].T.tolist(),b2=n.intercepts_[1].tolist(),
        w3=n.coefs_[2][:,0].tolist(),b3=float(n.intercepts_[2][0]),
        formula='S = target_mean + target_scale * (w3.T @ tanh(W2 @ tanh(W1 @ z + b1) + b2) + b3); z=(x-mean)/scale',
        interpretation='empirical prediction equation, not a physical governing law')


def equation_predict(eq,z):
    z = (np.asarray(z,dtype=float)-np.array(eq['mean']))/np.array(eq['scale'])
    h1 = np.tanh(z@np.array(eq['W1']).T+eq['b1'])
    h2 = np.tanh(h1@np.array(eq['W2']).T+eq['b2'])
    return eq['target_mean']+eq['target_scale']*(h2@np.array(eq['w3'])+eq['b3'])


def lookup(X,Y,V):
    out = []
    for v in V:
        same = (X[:,0]==v[0]) & (X[:,1]==v[1])
        if not same.any(): same[:] = True
        c = X[same]
        d = np.abs(c[:,0]-v[0])/50+np.abs(c[:,1]-v[1])+np.abs(c[:,2]-v[2])/1000+np.abs(c[:,3]-v[3])/1000
        out.append(Y[same][d.argmin()])
    return np.array(out)


def scores(y,p):
    rmse = np.sqrt(np.mean((y-p)**2,axis=1)); mae = np.mean(np.abs(y-p),axis=1)
    norm = rmse/np.sqrt(np.mean(y*y,axis=1))
    return dict(mean_rmse=float(rmse.mean()),median_rmse=float(np.median(rmse)),worst_rmse=float(rmse.max()),
        mean_mae=float(mae.mean()),mean_nrmse=float(norm.mean()),worst_nrmse=float(norm.max()),
        case_rmse=rmse.tolist(),case_mae=mae.tolist())


def select(X,Y,ids,grid,cfg):
    folds = list(KFold(cfg['folds'],shuffle=True,random_state=cfg['seed']).split(X))
    trials = []; base = np.empty_like(Y)
    for alpha in cfg['alphas']:
        p = np.empty_like(Y); records = []
        for tr,va in folds:
            m,info = fit(X[tr],Y[tr],grid,alpha,cfg)
            p[va] = predict(m,X[va],grid); base[va] = lookup(X[tr],Y[tr],X[va])
            records.append(dict(fit_ids=ids[tr].tolist(),validation_ids=ids[va].tolist(),**info))
        trials.append(dict(alpha=alpha,metrics=scores(Y,p),folds=records,prediction=p))
    best = min(trials,key=lambda t:(t['metrics']['mean_rmse'],-t['alpha']))
    return best,trials,base


def run(root,output):
    root,output = Path(root),Path(output)
    output.mkdir(parents=True,exist_ok=False)
    cfg = json.loads((root/'configs/single_mlp.json').read_text())
    split = json.loads((root/'data/split.json').read_text())
    train,test = np.array(split['train']),np.array(split['test'])
    assert len(set(train))==36 and len(set(test))==37 and not set(train)&set(test)
    grid = np.linspace(cfg['strain_min'],cfg['strain_max'],cfg['strain_points'])
    protected = {str(p.relative_to(root)):sha(p) for p in (root/'runs/score/final_Svm').glob('*') if p.is_file()}
    start = time.perf_counter()
    X,Y,audit = load_cases(root/'TEAM_8_extracted_results_set_1',train,grid)
    best,trials,base = select(X,Y,train,grid,cfg)
    print('Training-only selection:',best['alpha'],best['metrics']['mean_rmse'],flush=True)
    groups = []
    for T,rate in sorted(set(map(tuple,X[:,:2]))):
        va = np.flatnonzero((X[:,0]==T)&(X[:,1]==rate)); tr = np.setdiff1d(np.arange(36),va)
        b,ts,_ = select(X[tr],Y[tr],train[tr],grid,cfg)
        m,info = fit(X[tr],Y[tr],grid,b['alpha'],cfg)
        groups.append(dict(temperature=T,log10_rate=rate,fit_ids=train[tr].tolist(),validation_ids=train[va].tolist(),
            alpha=b['alpha'],selection=[{k:v for k,v in t.items() if k!='prediction'} for t in ts],
            fit=info,mlp=scores(Y[va],predict(m,X[va],grid)),baseline=scores(Y[va],lookup(X[tr],Y[tr],X[va]))))
        print('Nested condition check',T,rate,groups[-1]['mlp']['mean_rmse'],flush=True)
    model,fit_info = fit(X,Y,grid,best['alpha'],cfg)
    eq = export_equation(model)
    (output/'equation.json').write_text(json.dumps(eq,indent=2)+'\n')
    joblib.dump(model,output/'model.joblib')
    lock = dict(config=cfg,alpha=best['alpha'],fit_ids=train.tolist(),seed=cfg['seed'],
                equation_sha256=sha(output/'equation.json'),model_sha256=sha(output/'model.joblib'))
    (output/'selection_lock.json').write_text(json.dumps(lock,indent=2)+'\n')
    # No test history is opened until the selected fitted model has been saved and locked.
    V,Z,test_audit = load_cases(root/'TEAM_8_extracted_results_set_1',test,grid)
    p,pb = predict(model,V,grid),lookup(X,Y,V)
    portable = equation_predict(json.loads((output/'equation.json').read_text()),queries(V,grid)).reshape(Z.shape)
    reloaded = predict(joblib.load(output/'model.joblib'),V,grid)
    err = float(np.max(np.abs(portable-p))); reload_err = float(np.max(np.abs(reloaded-p)))
    assert err <= 1e-10 and reload_err == 0.
    for rel,h in protected.items(): assert sha(root/rel)==h
    result = dict(config=cfg,train_ids=train.tolist(),test_ids=test.tolist(),training_audit=audit,test_audit=test_audit,
        trials=[{k:v for k,v in t.items() if k!='prediction'} for t in trials],selected_alpha=best['alpha'],
        cv=best['metrics'],cv_baseline=scores(Y,base),condition_holdouts=groups,final_fit=fit_info,
        test=scores(Z,p),test_baseline=scores(Z,pb),train=scores(Y,predict(model,X,grid)),
        test_by_condition=[dict(temperature=T,log10_rate=rate,metrics=scores(Z[(V[:,0]==T)&(V[:,1]==rate)],p[(V[:,0]==T)&(V[:,1]==rate)])) for T,rate in sorted(set(map(tuple,V[:,:2])))],
        checks=dict(equation_max_error=err,reload_max_error=reload_err,parameters=sum(w.size for w in model['net'].coefs_)+sum(b.size for b in model['net'].intercepts_),
            protected_artifacts_unchanged=protected,selection_saved_before_test=True),
        versions=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,sklearn=sklearn.__version__),
        elapsed_seconds=time.perf_counter()-start,code_sha256=sha(__file__),split_sha256=sha(root/'data/split.json'),
        caveat='Previously explored test set; same-design interpolation, not blind/physical validation. Condition checks use nested training-only alpha selection. No universal-best claim.')
    (output/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    for label,ids,y,pr,bl in [('cv',train,Y,best['prediction'],base),('test',test,Z,p,pb)]:
        with (output/f'{label}_predictions.csv').open('w',newline='') as f:
            w=csv.writer(f);w.writerow(['id','E11','Svm','MLP','lookup'])
            for i,case in enumerate(ids):
                w.writerows(zip([case]*len(grid),grid,y[i],pr[i],bl[i]))
    cache=root/'work/matplotlib';cache.mkdir(parents=True,exist_ok=True);os.environ.setdefault('MPLCONFIGDIR',str(cache))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(11,4),constrained_layout=True)
    worst=int(np.argmax(result['test']['case_rmse']));i=list(train).index(60)
    for ax,e,truth,mp,bp,title in [(axes[0],grid,Z[worst],p[worst],pb[worst],f'Worst test case {test[worst]}'),(axes[1],grid,Y[i],best['prediction'][i],base[i],'Case 60: training-side case validation')]:
        ax.plot(e,truth,label='Supplied curve',color='black');ax.plot(e,mp,label='Single MLP');ax.plot(e,bp,'--',label='Curve-copy baseline')
        ax.set(title=title,xlabel='E11 (source strain coordinate)',ylabel='Svm (source stress units)');ax.legend()
    fig.savefig(output/'comparison.png',dpi=150);plt.close(fig)
    print(json.dumps({k:result[k] for k in ['selected_alpha','cv','test','test_baseline','checks']}),flush=True)
    return result


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=ROOT);ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    with threadpool_limits(limits=1): run(args.root,args.output)
