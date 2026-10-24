"""The three models compared. All share fit(X, Y) / predict(X) on whole curves.

X: (n_cases, 4) conditions [T, log10 rate, density, G].  Y: (n_cases, 120) stress on STRAIN_GRID.
Every scaler and PCA basis is fitted inside fit(), i.e. on training cases only.
"""
import numpy as np
from sklearn.decomposition import PCA
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel, WhiteKernel
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler

from data import STRAIN_GRID


class LookupBaseline:
    """No learning: copy the training curve with the same (T, rate) and nearest G, density.

    If a trained model cannot beat this, it has not learned anything useful.
    """

    def fit(self, X, Y):
        self.X, self.Y = X, Y
        return self

    def predict(self, X):
        out = []
        for x in X:
            same = (self.X[:, 0] == x[0]) & (self.X[:, 1] == x[1])
            if not same.any():  # unseen condition: fall back to all cases
                same[:] = True
            cand = self.X[same]
            dist = (np.abs(cand[:, 0] - x[0]) / 50 + np.abs(cand[:, 1] - x[1])
                    + np.abs(cand[:, 2] - x[2]) / 1000 + np.abs(cand[:, 3] - x[3]) / 1000)
            out.append(self.Y[same][dist.argmin()])
        return np.array(out)


class QueryMLP:
    """Main model. Inputs (T, log10 rate, density, G, strain) -> one stress value.

    Querying all 120 strains for a fixed condition draws the whole curve. Small network
    (two hidden layers of 16 tanh units) because there are only 36 training curves.

    This is an ENSEMBLE: n_init networks of identical shape, trained from different random
    starts, whose predictions are averaged. Each 5-16-16-1 network has 385 weights and biases;
    the default 5-network ensemble therefore stores 1,925. Whether an ensemble counts as one
    "model" under the course's model limit is unresolved.
    """

    def __init__(self, hidden=(16, 16), alpha=1e-4, n_init=5, seed=0, features=None):
        self.hidden, self.alpha, self.n_init, self.seed = hidden, alpha, n_init, seed
        self.features = features  # column indices to use, e.g. drop density for ablation

    def _inputs(self, X):
        if self.features is not None:
            X = X[:, self.features]
        n, m = len(X), len(STRAIN_GRID)
        return np.column_stack([np.repeat(X, m, axis=0), np.tile(STRAIN_GRID, n)])

    def fit(self, X, Y):
        Z = self._inputs(X)
        self.xs = StandardScaler().fit(Z)
        self.ym, self.ys = Y.mean(), Y.std()
        t = (Y.ravel() - self.ym) / self.ys
        self.nets = [
            MLPRegressor(hidden_layer_sizes=self.hidden, activation="tanh", solver="lbfgs", alpha=self.alpha,
                         max_iter=5000, tol=1e-9, random_state=self.seed + k).fit(self.xs.transform(Z), t)
            for k in range(self.n_init)
        ]
        return self

    def predict(self, X):
        Z = self.xs.transform(self._inputs(X))
        p = np.mean([net.predict(Z) for net in self.nets], axis=0)
        return (p * self.ys + self.ym).reshape(len(X), len(STRAIN_GRID))


class PcaGP:
    """Comparison model. Compress each curve to k PCA coefficients, predict each with a GP.

    predict(return_std=True) also returns the GP's model-conditional standard deviation.
    It is NOT calibrated: on held-out 200 C conditions only 0-37 % of true points fell inside
    ±2σ (src/gp_calibration.py), so it must not be used as an extrapolation warning.
    PCA truncation error is not included in it.
    """

    def __init__(self, n_components=4):
        self.k = n_components

    def fit(self, X, Y):
        self.pca = PCA(self.k).fit(Y)
        C = self.pca.transform(Y)
        self.xs = StandardScaler().fit(X)
        A = self.xs.transform(X)
        kernel = (ConstantKernel(1.0) * RBF(np.ones(X.shape[1]), (1e-2, 1e3))
                  + WhiteKernel(1e-4, (1e-10, 1e-1)))
        self.gps = [GaussianProcessRegressor(kernel, normalize_y=True, n_restarts_optimizer=3,
                                             random_state=0).fit(A, C[:, j]) for j in range(self.k)]
        return self

    def predict(self, X, return_std=False):
        A = self.xs.transform(X)
        res = [gp.predict(A, return_std=True) for gp in self.gps]
        C = np.column_stack([m for m, _ in res])
        Y = self.pca.inverse_transform(C)
        if not return_std:
            return Y
        # Propagate coefficient std through the (orthonormal) PCA basis.
        S = np.column_stack([s for _, s in res])
        std = np.sqrt((S[:, :, None] ** 2 * self.pca.components_[None] ** 2).sum(1))
        return Y, std


MODELS = {"lookup baseline": LookupBaseline, "query MLP": QueryMLP, "PCA + GP": PcaGP}


class PhysQueryMLP(QueryMLP):
    """Query MLP with physics-style inputs: 1000/T(K) (Arrhenius), log10 rate, G; density dropped.

    Thermally activated flow usually depends on rate and temperature through exp(-Q/RT), so
    1/T (in kelvin) is a more natural input than T in °C. Density is dropped because it
    changes stress by only ~0.2 % across its whole range (factor-effect analysis).
    """

    def _inputs(self, X):
        X = np.column_stack([1000.0 / (X[:, 0] + 273.15), X[:, 1], X[:, 3]])
        n, m = len(X), len(STRAIN_GRID)
        return np.column_stack([np.repeat(X, m, axis=0), np.tile(STRAIN_GRID, n)])


class Blend:
    """Average of two fitted models' curves (here: query MLP + PCA/GP)."""

    def __init__(self, *factories):
        self.factories = factories

    def fit(self, X, Y):
        self.models = [f().fit(X, Y) for f in self.factories]
        return self

    def predict(self, X):
        return np.mean([m.predict(X) for m in self.models], axis=0)


from pca_mlp import PcaMLP  # noqa: E402  (Codex's component, reviewed by Claude 2026-10-24)

# Named candidates for src/score.py. Each value builds a fresh, unfitted model.
CANDIDATES = {
    "pca_mlp4": lambda: PcaMLP(n_components=4, hidden=(16, 16), alpha=1e-3, n_init=5),
    "pca_mlp6": lambda: PcaMLP(n_components=6, hidden=(16, 16), alpha=1e-3, n_init=5),
    "mlp": lambda: QueryMLP(hidden=(16, 16), alpha=1e-3),
    "gp6": lambda: PcaGP(n_components=6),
    "mlp_phys": lambda: PhysQueryMLP(hidden=(16, 16), alpha=1e-3),
    "blend_mlp_gp6": lambda: Blend(lambda: QueryMLP(hidden=(16, 16), alpha=1e-3),
                                   lambda: PcaGP(n_components=6)),
    "blend_phys_gp6": lambda: Blend(lambda: PhysQueryMLP(hidden=(16, 16), alpha=1e-3),
                                    lambda: PcaGP(n_components=6)),
}
