"""Plot saved Svm training-half condition diagnostics; performs no model fitting."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'runs/score/select_mlp_Svm.json'
data=json.loads(source.read_text())
conditions=[f'{t}C_1e{r}' for t in [30,100,200] for r in [-5,-4,-3]]
values=np.array([data['loco_by_condition'][k] for k in conditions])
assert len(values)==9 and np.isfinite(values).all()
np.testing.assert_allclose(values.mean(),data['loco_mean_rmse'],rtol=1e-12)
fig,ax=plt.subplots(figsize=(9,4.8),layout='constrained')
x=np.arange(len(values))
ax.bar(x,values,color='#536878',width=.65,label='Query MLP, saved training-half diagnostics')
ax.axhline(values.mean(),color='#b45d38',ls='--',label=f'Mean over 9 groups: {values.mean():.4f}')
ax.set_xticks(x,[f'{t}\n$10^{{{r}}}$' for t in [30,100,200] for r in [-5,-4,-3]])
ax.set_xlabel('Held-out temperature / strain-rate group (source input units)')
ax.set_ylabel('Mean curve RMSE (source stress units)')
ax.set_title('Svm condition-holdout errors on the 36-case training half')
ax.grid(axis='y',alpha=.18);ax.set_axisbelow(True)
ax.legend(fontsize=8)
for i,v in enumerate(values):
 ax.text(i,v+.35,f'{v:.2f}',ha='center',va='bottom',fontsize=8)
ax.set_ylim(0,float(values.max())+4)
fig.supxlabel('Source: runs/score/select_mlp_Svm.json. Saved results; no retraining. Physical units remain unconfirmed.',fontsize=8)
out=ROOT/'report/figures';out.mkdir(parents=True,exist_ok=True)
for ext in ['png','pdf']:
 fig.savefig(out/f'condition_holdout_Svm.{ext}',dpi=140)
print(f'Chart written. Mean={values.mean():.10f}; hot/slow={data["loco_by_condition"]["200C_1e-5"]:.10f}')
