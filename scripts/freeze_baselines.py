"""One-off: freeze the earlier models' numbers used for comparison into reports/jc_pinn_20261107/baselines.json.

Run once at commit ee1f001 (archived as branch archive/pre-final-2026-11-07) before the old model files were removed.
Every value is copied or recomputed from the original files, whose paths and SHA-256 hashes are recorded.
"""
import csv, hashlib, json
from pathlib import Path
import numpy as np

root = Path(__file__).resolve().parents[1]
run = root / 'reports/jc_pinn_20261107'
sha = lambda p: hashlib.sha256((root / p).read_bytes()).hexdigest()
src = {k: v for k, v in dict(single_results='reports/single_mlp_20261102/results.json', single_test='reports/single_mlp_20261102/test_predictions.csv',
       single_cv='reports/single_mlp_20261102/cv_predictions.csv', ensemble_metrics='runs/score/final_Svm/metrics.json',
       ensemble_selection='runs/score/select_mlp_Svm.json').items()}
S = json.loads((root / src['single_results']).read_text())
pred, truth = {}, {}
with (root / src['single_test']).open() as f:
    for r in csv.DictReader(f):
        pred.setdefault(int(r['id']), []).append(float(r['MLP'])); truth.setdefault(int(r['id']), []).append(float(r['Svm']))
single_case = {str(i): float(np.sqrt(np.mean((np.array(pred[i]) - np.array(truth[i])) ** 2))) for i in pred}
E = json.loads((root / src['ensemble_metrics']).read_text())
ES = json.loads((root / src['ensemble_selection']).read_text())
# identity of the 120-point curves used by every model (checked at freeze time)
R = json.loads((run / 'results.json').read_text())
curves_2nov = {}
for name in ('single_cv', 'single_test'):
    with (root / src[name]).open() as f:
        for r in csv.DictReader(f):
            curves_2nov.setdefault(int(r['id']), []).append(float(r['Svm']))
run_truth = {}
for name in ('cv_predictions.csv', 'test_predictions.csv'):
    with (run / name).open() as f:
        for r in csv.DictReader(f):
            run_truth.setdefault(int(r['id']), []).append(float(r['Svm']))
identical = all(np.array_equal(np.array(curves_2nov[i]), np.array(run_truth[i])) for i in run_truth)
assert identical
out = dict(
    purpose='Earlier models on the same 36/37 split, frozen for comparison before their files were removed from the repository.',
    archive=dict(branch='archive/pre-final-2026-11-07', commit='ee1f001d29dc285867a46030e945ea3c1bf36644'),
    sources={k: dict(path=v, sha256=sha(v)) for k, v in src.items()},
    curves_identical_to_2nov_hash_checked_curves=identical,
    single_mlp=dict(description='single 5-16-16-1 tanh scikit-learn MLP, alpha 0.001 (2 Nov 2026)',
                    test={k: S['test'][k] for k in ('mean_rmse', 'median_rmse', 'worst_rmse', 'mean_mae', 'mean_nrmse')},
                    cv=S['cv']['mean_rmse'],
                    groups=[dict(temperature=g['temperature'], log10_rate=g['log10_rate'], mean_rmse=g['mlp']['mean_rmse']) for g in S['condition_holdouts']],
                    test_case_rmse=single_case),
    ensemble_mlp=dict(description='five-network query MLP ensemble, scikit-learn (24 Oct 2026); CV used different folds',
                      test=dict(mean_rmse=E['test_mean_rmse'], median_rmse=E['test_median_rmse'], worst_rmse=E['test_worst_rmse']),
                      test_case_rmse=E['per_case'], cv=ES['cv_mean_rmse'], loco_mean_rmse=ES['loco_mean_rmse'], loco_by_condition=ES['loco_by_condition']))
(run / 'baselines.json').write_text(json.dumps(out, indent=1) + '\n', newline='\n')  # LF on every OS: reports/** is byte-checked (.gitattributes)
print('written; single test', round(out['single_mlp']['test']['mean_rmse'], 4), 'ensemble test', round(out['ensemble_mlp']['test']['mean_rmse'], 4), 'curves identical', identical)
