"""Compute independent training-condition checks; publish complete results atomically.

Workers have private alpha caches. Only an atomically replaced complete group
result is shared with the running experiment, so it can reuse finished groups.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import numpy as np
from threadpoolctl import threadpool_limits

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'src'))
import single_mlp as s

ap=argparse.ArgumentParser();ap.add_argument('--temperature',type=float,required=True)
args=ap.parse_args()
cfg=json.loads((root/'configs/single_mlp.json').read_text())
split=json.loads((root/'data/split.json').read_text())
ids=np.array(split['train']);grid=np.linspace(cfg['strain_min'],cfg['strain_max'],cfg['strain_points'])
X,Y,audit=s.load_cases(root/'TEAM_8_extracted_results_set_1',ids,grid)
signature=hashlib.sha256((s.sha(s.__file__)+s.json_text(cfg)+s.json_text(audit)).encode()).hexdigest()[:16]
cache=root/'work'/f'single_mlp_cache_{signature}'
with threadpool_limits(limits=1):
    for T,rate in sorted(set(map(tuple,X[:,:2]))):
        if T!=args.temperature:continue
        public=cache/f'group_{T}_{rate}'
        if (public/'result.json').exists():continue
        private=cache/f'worker_{T}_{rate}'
        va=np.flatnonzero((X[:,0]==T)&(X[:,1]==rate));tr=np.setdiff1d(np.arange(36),va)
        best,trials,_=s.select(X[tr],Y[tr],ids[tr],grid,cfg,private)
        model,info=s.fit(X[tr],Y[tr],grid,best['alpha'],cfg)
        result=dict(temperature=T,log10_rate=rate,fit_ids=ids[tr].tolist(),validation_ids=ids[va].tolist(),
            alpha=best['alpha'],selection=[{k:v for k,v in t.items() if k!='prediction'} for t in trials],
            fit=info,mlp=s.scores(Y[va],s.predict(model,X[va],grid)),baseline=s.scores(Y[va],s.lookup(X[tr],Y[tr],X[va])),
            worker_source_sha256=s.sha(__file__),core_source_sha256=s.sha(s.__file__))
        public.mkdir(parents=True,exist_ok=True)
        temp=private/'complete_result.json';temp.write_text(s.json_text(result))
        os.replace(temp,public/'result.json')
        print('Published condition',T,rate,result['mlp']['mean_rmse'],flush=True)
