"""Independently reload local selected models and verify their saved predictions/metrics.

Run with the project's already-provisioned .venv. Does not fit or change models.
These artifacts were generated locally by the collaborating agent and are trusted here.
"""
import os
from pathlib import Path
import sys
import json

os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import joblib
import numpy as np

rows = []
for target in ('SCAU11', 'Svm'):
    selection = json.loads((ROOT / 'runs' / ('selection_' + target + '.json')).read_text())
    folder = ROOT / 'runs' / ('selected_' + target)
    test_ids = np.load(folder / 'test_ids.npy', allow_pickle=False)
    with np.load(ROOT / 'data' / ('curves_' + target + '.npz'), allow_pickle=False) as data:
        lookup = {int(case): i for i, case in enumerate(data['ids'])}
        positions = [lookup[int(case)] for case in test_ids]
        features, truth = data['X'][positions], data['Y'][positions]
    assert len(test_ids) == 37
    for name, filename in [('query MLP', 'query_MLP'), ('PCA + GP', 'PCA_plus_GP')]:
        selected = selection['chosen'][name]
        model = joblib.load(ROOT / selected['artifact'])
        predicted = model.predict(features)
        saved = np.load(folder / (filename + '_test_predictions.npy'), allow_pickle=False)
        assert np.isfinite(predicted).all() and predicted.shape == truth.shape
        assert np.allclose(predicted, saved, rtol=1e-10, atol=1e-10), (target, name, 'reload')
        errors = np.sqrt(np.mean((predicted - truth) ** 2, axis=1))
        for key, value in [('test_mean_rmse', errors.mean()), ('test_median_rmse', np.median(errors)),
                           ('test_worst_rmse', errors.max())]:
            assert np.isclose(value, selected[key], rtol=1e-10, atol=1e-10), (target, name, key)
        rows.append((target, name, errors.mean(), errors.max()))
        print('PASS', target, name, 'reload + mean/median/worst metrics')

report = ['# Codex selected-model reload check', '',
          'Checked 24 October 2026 using `.venv/bin/python reports/check_selected_artifacts.py`.', '',
          'All four selected model files reproduce their saved 37-case predictions and mean/median/worst RMSE values after reload. No models were fitted or modified.', '',
          '| Target | Model | Mean curve RMSE | Worst curve RMSE |',
          '| --- | --- | ---: | ---: |']
for target, name, mean, worst in rows:
    report.append(f'| {target} | {name} | {mean:.6f} | {worst:.6f} |')
report += ['', 'Stress units remain unconfirmed. Results use the cached 120-point curve grid. This verifies saved inference/metric consistency, not independent training reproduction, source-data extraction, physical validation, or a blind final test. The earlier all-data selection history still applies.', '']
(ROOT / 'reports' / 'codex-selected-model-check.md').write_text('\n'.join(report))
