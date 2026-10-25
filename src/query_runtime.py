"""NumPy-only inference for the selected tanh QueryMLP, using its existing weights.

Export once with the training environment:
  .venv/bin/python src/query_runtime.py --export runs/score/final_Svm/model.joblib \
      --output runs/score/final_Svm/model_numpy.npz

Importing or loading this runtime needs NumPy only, without sklearn or pickle.
It does not fit, prune, quantize, or change the network or its prediction grid.
"""
import argparse
from pathlib import Path

import numpy as np


class QueryRuntime:
    def __init__(self, mean, scale, target_mean, target_scale, strain, weights, biases):
        self.mean = np.array(mean, dtype=np.float64, copy=True)
        self.scale = np.array(scale, dtype=np.float64, copy=True)
        self.strain = np.array(strain, dtype=np.float64, copy=True)
        self.target_mean, self.target_scale = float(target_mean), float(target_scale)
        self.weights = tuple(np.array(w, dtype=np.float64, copy=True) for w in weights)
        self.biases = tuple(np.array(b, dtype=np.float64, copy=True) for b in biases)
        if self.mean.shape != (5,) or self.scale.shape != (5,) or np.any(self.scale <= 0):
            raise ValueError('Expected five scaler features with positive scales.')
        if self.strain.ndim != 1 or len(self.strain) < 2 or np.any(np.diff(self.strain) <= 0):
            raise ValueError('Expected an increasing one-dimensional strain grid.')
        if not self.weights or len(self.weights) != len(self.biases):
            raise ValueError('Expected matching weights and biases.')
        n_nets, width = self.weights[0].shape[0], 5
        for w, b in zip(self.weights, self.biases):
            if w.ndim != 3 or w.shape[:2] != (n_nets, width) or b.shape != (n_nets, w.shape[2]):
                raise ValueError('Incompatible ensemble layer shapes.')
            width = w.shape[2]
        if n_nets < 1 or width != 1 or self.target_scale <= 0:
            raise ValueError('Expected a scalar regression ensemble with positive target scale.')
        arrays = (self.mean, self.scale, self.strain, *self.weights, *self.biases)
        if not all(np.isfinite(a).all() for a in arrays) or not np.isfinite([self.target_mean, self.target_scale]).all():
            raise ValueError('Runtime parameters must be finite.')
        for a in arrays:
            a.flags.writeable = False

    @classmethod
    def from_model(cls, model):
        from data import STRAIN_GRID
        if type(model).__name__ != 'QueryMLP' or model.features is not None:
            raise ValueError('Only the full four-condition QueryMLP is supported.')
        if not model.nets or not all(n.activation == 'tanh' and n.out_activation_ == 'identity' for n in model.nets):
            raise ValueError('Expected tanh hidden layers and a linear scalar output.')
        count = len(model.nets[0].coefs_)
        if not all(len(n.coefs_) == count for n in model.nets):
            raise ValueError('Ensemble architectures must match.')
        weights = [np.stack([n.coefs_[i] for n in model.nets]) for i in range(count)]
        biases = [np.stack([n.intercepts_[i] for n in model.nets]) for i in range(count)]
        return cls(model.xs.mean_, model.xs.scale_, model.ym, model.ys, STRAIN_GRID, weights, biases)

    def predict(self, X):
        X = np.asarray(X, dtype=np.float64)
        if X.ndim != 2 or X.shape[1] != 4 or not np.isfinite(X).all():
            raise ValueError('Expected finite (n_cases, 4) conditions: T, log10(rate), density, G.')
        if len(X) == 0:
            return np.empty((0, len(self.strain)), dtype=np.float64)
        Z = np.column_stack([np.repeat(X, len(self.strain), axis=0), np.tile(self.strain, len(X))])
        Z = (Z - self.mean) / self.scale
        # Each net uses a small matrix multiplication. Avoid repeating sklearn's
        # input validation and estimator dispatch at every network call.
        outputs = []
        for k in range(self.weights[0].shape[0]):
            A = Z
            for i, (w, b) in enumerate(zip(self.weights, self.biases)):
                A = A @ w[k] + b[k]
                if i + 1 < len(self.weights):
                    np.tanh(A, out=A)
            outputs.append(A[:, 0])
        p = np.mean(outputs, axis=0) * self.target_scale + self.target_mean
        return p.reshape(len(X), len(self.strain))

    def save(self, path):
        arrays = dict(format_version=np.array(1), mean=self.mean, scale=self.scale,
                      target_mean=np.array(self.target_mean), target_scale=np.array(self.target_scale),
                      strain=self.strain, layers=np.array(len(self.weights)))
        for i, (w, b) in enumerate(zip(self.weights, self.biases)):
            arrays[f'w{i}'], arrays[f'b{i}'] = w, b
        with Path(path).open('wb') as handle:
            np.savez_compressed(handle, **arrays)

    @classmethod
    def load(cls, path):
        with np.load(path, allow_pickle=False) as z:
            if int(z['format_version']) != 1:
                raise ValueError('Unsupported runtime format version.')
            layers = int(z['layers'])
            if not 1 <= layers <= 16:
                raise ValueError('Invalid layer count.')
            return cls(z['mean'], z['scale'], z['target_mean'], z['target_scale'], z['strain'],
                       [z[f'w{i}'] for i in range(layers)], [z[f'b{i}'] for i in range(layers)])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--export', type=Path, required=True, help='Trusted locally generated joblib model')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    import joblib
    runtime = QueryRuntime.from_model(joblib.load(args.export))
    runtime.save(args.output)
    print(f'Exported existing weights to {args.output}')
