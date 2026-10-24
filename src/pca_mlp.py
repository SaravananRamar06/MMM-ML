"""Training-only curve compression followed by a compact coefficient regressor.

Shared component for the material pipeline. X contains per-case conditions; Y
contains stress on the common strain grid. No holdout targets, global PCA basis,
hardening law, or porosity mapping are used by this estimator.
"""
import numbers

import numpy as np
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.decomposition import PCA
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.utils.validation import check_array, check_is_fitted


class PcaMLP(RegressorMixin, BaseEstimator):
    """Predict whole curves from conditions via training-fitted PCA coefficients.

    Default inputs are [temperature, log10(rate), density, G]. A case is one
    training sample. Coefficients are standardised component by component before
    regression; evaluation must still use reconstructed stress in source units.
    n_init networks are averaged in coefficient space. The entire fitted PCA,
    scalers, and networks are retained for reproducible reload/inference.
    """

    def __init__(self, n_components=4, hidden=(16, 16), alpha=1e-3,
                 n_init=5, seed=0, max_iter=5000):
        self.n_components = n_components
        self.hidden = hidden
        self.alpha = alpha
        self.n_init = n_init
        self.seed = seed
        self.max_iter = max_iter

    def fit(self, X, Y):
        X = check_array(X, dtype=float)
        Y = check_array(Y, dtype=float)
        if len(X) != len(Y):
            raise ValueError('X and Y must contain the same simulation cases.')
        if not isinstance(self.n_components, numbers.Integral) or not 1 <= self.n_components <= min(Y.shape):
            raise ValueError('n_components must be an integer within the training matrix dimensions.')
        if not isinstance(self.n_init, numbers.Integral) or self.n_init < 1:
            raise ValueError('n_init must be a positive integer.')
        self.n_features_in_ = X.shape[1]
        self.n_outputs_ = Y.shape[1]
        self.n_fit_cases_ = len(X)
        self.x_scaler_ = StandardScaler().fit(X)
        self.pca_ = PCA(n_components=self.n_components, svd_solver='full').fit(Y)
        coefficients = self.pca_.transform(Y)
        self.coefficient_scaler_ = StandardScaler().fit(coefficients)
        inputs = self.x_scaler_.transform(X)
        targets = self.coefficient_scaler_.transform(coefficients)
        if self.n_components == 1:
            targets = targets.ravel()
        self.nets_ = []
        for offset in range(self.n_init):
            network = MLPRegressor(hidden_layer_sizes=self.hidden, activation='tanh',
                                   solver='lbfgs', alpha=self.alpha, max_iter=self.max_iter,
                                   tol=1e-9, random_state=self.seed + offset)
            self.nets_.append(network.fit(inputs, targets))
        reconstructed = self.pca_.inverse_transform(coefficients)
        self.training_reconstruction_rmse_ = float(np.sqrt(np.mean((Y - reconstructed) ** 2)))
        self.nn_parameter_count_ = sum(array.size for net in self.nets_
                                       for array in net.coefs_ + net.intercepts_)
        return self

    def predict(self, X):
        check_is_fitted(self, ['pca_', 'nets_', 'x_scaler_', 'coefficient_scaler_'])
        X = check_array(X, dtype=float)
        if X.shape[1] != self.n_features_in_:
            raise ValueError('Prediction inputs have a different feature count from training.')
        inputs = self.x_scaler_.transform(X)
        predictions = [np.asarray(net.predict(inputs)).reshape(len(X), self.n_components)
                       for net in self.nets_]
        coefficients = self.coefficient_scaler_.inverse_transform(np.mean(predictions, axis=0))
        return self.pca_.inverse_transform(coefficients)
