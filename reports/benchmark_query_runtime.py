"""Compare identical fitted weights on alternating timing runs, single BLAS thread.

No fitting or accuracy selection. Measures in-process prediction separately from
fresh-process import/load/predict time. Run with .venv/bin/python.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import time

for key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import joblib
import numpy as np
from query_runtime import QueryRuntime


def main():
    source = ROOT / 'runs/score/final_Svm/model.joblib'
    output = source.with_name('model_numpy.npz')
    model = joblib.load(source)
    runtime = QueryRuntime.from_model(model)
    runtime.save(output)
    with np.load(ROOT / 'data/curves_Svm.npz', allow_pickle=False) as z:
        X = z['X']
    difference = float(np.max(np.abs(model.predict(X) - runtime.predict(X))))
    np.testing.assert_allclose(runtime.predict(X), model.predict(X), rtol=1e-12, atol=1e-11)
    result = {'max_abs_difference_73_cases': difference, 'blas_threads': 1, 'prediction': {},
              'source_bytes': source.stat().st_size, 'numpy_export_bytes': output.stat().st_size}
    for count in (1, 3, 37, 73):
        samples = {'sklearn': [], 'numpy': []}
        for _ in range(5):
            model.predict(X[:count])
            runtime.predict(X[:count])
        repeats = 100 if count < 4 else 30
        for i in range(repeats):
            pairs = [('sklearn', model), ('numpy', runtime)]
            for key, obj in pairs if i % 2 == 0 else pairs[::-1]:
                start = time.perf_counter_ns()
                obj.predict(X[:count])
                samples[key].append((time.perf_counter_ns() - start) / 1e6)
        stats = {k: {'median_ms': float(np.median(v)), 'p95_ms': float(np.percentile(v, 95))}
                 for k, v in samples.items()}
        stats['median_speedup'] = stats['sklearn']['median_ms'] / stats['numpy']['median_ms']
        result['prediction'][str(count)] = stats
    start_samples = {'sklearn': [], 'numpy': []}
    for i in range(5):
        for name in ('sklearn', 'numpy') if i % 2 == 0 else ('numpy', 'sklearn'):
            code = ("import sys;sys.path.insert(0,'src');" +
                    ("import joblib; m=joblib.load('runs/score/final_Svm/model.joblib');"
                     if name == 'sklearn' else
                     "from query_runtime import QueryRuntime;m=QueryRuntime.load('runs/score/final_Svm/model_numpy.npz');") +
                    "m.predict([[100,-4,2619,24541]])")
            start = time.perf_counter()
            subprocess.run([sys.executable, '-c', code], cwd=ROOT, check=True, capture_output=True)
            start_samples[name].append(1000 * (time.perf_counter() - start))
    result['fresh_process_median_ms'] = {k: float(np.median(v)) for k, v in start_samples.items()}
    result['notes'] = ['Local repeated warm timings; hardware and load affect results.',
                       'Fresh-process timings include interpreter startup/import/load and one curve.',
                       'Same fitted float64 weights; no retraining or change in accuracy claimed.',
                       'GP reference and HTTP rendering overhead are not included.']
    (ROOT / 'reports/query_runtime_benchmark_20261025.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
