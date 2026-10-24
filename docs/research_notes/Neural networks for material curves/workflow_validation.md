# Practical model development and validation

Research date: 24 October 2026. This is an implementation recommendation, not a trained result. It combines official ML guidance with the local audit; proposed design choices are identified as inferences. No model, split, or preprocessing artifact was created.

## How should the task and dataset be prepared?

### Takeaway

Build a material-curve surrogate with simulation cases as the independent units. Preserve the separate, unresolved coefficient-of-lift task rather than inventing aerodynamic labels.

### Cited Findings

- The local audit found 73 finite histories; every `E11` increases and agrees with prescribed rate multiplied by time within 4e-8. Exact common support is `[0.0001, 0.09999996]`. Every case ends below its initial `Svm`; case 60 has reversing `Evm`, and units/generating law remain uncertain. — [Local dataset notes](dataset_fit.md), [audit output](curve_inspection.json).
- Learned transformations must be fitted on training data only and then applied unchanged to validation/test samples. This includes standardisation and PCA; pipelines help prevent accidental refitting or inconsistent prediction-time preparation. — [Official preprocessing guidance](https://scikit-learn.org/stable/common_pitfalls.html).

### Inferences

- Prediction contract: `(temperature, log10(strain_rate), density, shear_modulus, E11) -> Svm`, initially restricted to the observed fixed loading family and measured strain support. Use source stress units until verified. `E11` is the defensible initial coordinate; do not claim it equals plastic strain.
- Preserve raw histories and make a case manifest containing ID, conditions, flags, file hash, support, and row count. Retain case 60 and explain its unusual shape rather than deleting it to improve scores.
- For model 1, sample the same number of strain queries from each case or weight each curve equally. A 100,000-row case must not outweigh a 1,000-row case simply because its integration output is denser. Check interpolation fidelity against the raw curves, especially case 60; avoid extrapolating to zero strain or inventing an elastic segment.
- Log-transform the positive prescribed rates because they span decades, then standardise candidate inputs and target using each training fold. Keep density initially, but do not rename it porosity. Feature importance/ablation must use training-side validation and account for strongly similar curves.

### Gaps

The material-to-aerodynamic coupling, lift labels, confirmed physical units, and generating constitutive model remain absent. The data supports an empirical material surrogate, not a demonstrated general constitutive law or coefficient-of-lift predictor.

## How should two small candidate models be trained and selected?

### Takeaway

Use one permanent 36/37 random case holdout and a small training-side validation exercise. Compare representations rather than escalating to a large architecture without evidence.

### Cited Findings

- Official guidance warns against selecting hyperparameters on final test performance. Group-aware splitters keep observations from the same group together, and `GroupShuffleSplit` provides random group holdouts. — [Official cross-validation guidance](https://scikit-learn.org/stable/modules/cross_validation.html).
- MLPs perform nonlinear regression, are sensitive to scaling and random initialisation, and support L2 weight regularisation. Official guidance recommends starting with few layers/neurons; it notes L-BFGS can perform well on small datasets and Adam is robust on larger sample sets. That observation does not establish the winning optimiser for this dataset. — [Official MLP guide](https://scikit-learn.org/stable/modules/neural_networks_supervised.html).

### Inferences

- Persist one random split with 36 training cases and 37 final test cases, seed chosen before training. Do not retry the split for better scores. Full-dataset EDA has already occurred: disclose that the eventual test curves were descriptively inspected, while committing to exclude them from fitting and performance-driven selection going forward.
- Use three internal case folds on the 36 training cases: approximately 24 fit cases and 12 validation cases per fold. This avoids an elaborate nested-CV exercise while retaining the professor's final holdout. Fit all scalers, curve means/bases, feature choices, and losses inside the fitting side of each fold.
- Candidate 1: compact query MLP, provisionally `5–16–16–1`, smooth hidden activations and scalar regression output. Select a small, predetermined regularisation/training-budget search; do not imply these exact widths are theoretically optimal. Monitor case-averaged training and validation losses. Any early-stopping split must be case-based: automatic random-row validation would violate the design.
- Candidate 2, conditional on acceptable training-only reconstruction: four conditions -> small MLP -> PCA coefficients -> whole stress curve. Choose PCA rank through training-fold reconstruction and prediction errors, including local/worst-case errors. Fit the basis again on all 36 training cases after selection. The all-73 exploratory PCA is not a final basis or a validation score.
- Compare candidates on identical folds and curve metrics. A simple training-mean-curve predictor provides a reference without being a third neural network. Track convergence and a small predeclared set of initialisation seeds inside training; do not select seeds against the test half.
- Once settings are frozen, refit the selected pipeline on the complete 36-case training partition. Use a training budget determined by internal validation, then evaluate the final holdout without iterative redesign around its scores.

### Gaps

No experiment establishes a winner, appropriate PCA rank, activation, optimiser, regularisation strength, or accuracy. The tentative two-model limit still needs precise course interpretation.

## What would count as a successful, usable model?

### Takeaway

Success means accurate unseen-case curves within stated scope, with a reproducible prediction artifact. A high pooled R2 alone is insufficient.

### Cited Findings

- The local audit found a weak density effect and much stronger rate/temperature effects, so random case splitting may separate almost matching curves. It also found no 300-temperature outputs. — [Local dataset notes](dataset_fit.md).
- Official persistence guidance recommends recording the training-data reference, source code, dependency versions and training-side validation results so a model can be rebuilt. It warns that loading across different library versions is unsupported. — [Official persistence guidance](https://scikit-learn.org/stable/model_persistence.html).

### Inferences

- Calculate MAE and RMSE per case in original stress units, then report their mean, median, worst value and condition-wise breakdown. Show observed/predicted curves and residuals, including case 60. Pooled R2 can mainly reward large differences between temperature/rate groups while hiding failure on one curve; report it only alongside these errors. Avoid percentage errors when stress approaches zero.
- For the PCA model report basis-reconstruction error separately from coefficient-prediction error. High retained variance is not equivalent to accurate prediction.
- Plot case-level learning curves within training to distinguish underfitting from overfitting and to assess whether additional independent simulations would help. Optional training-side holdout of a temperature/rate level can probe harder generalisation without replacing the required random final split.
- Save model weights, scalers, feature order, target definition, grid/basis if relevant, units/status, split IDs, seeds, configuration, dependency versions and predictions. Test reload in a fresh process and ensure that a documented input reproduces the saved result.
- Publish an applicability statement: fixed observed loading path, available condition levels and strain interval; no validated unloading/cyclic response, 300-temperature extrapolation, porosity mapping, or aerodynamic lift prediction. This is a scientifically defensible model even if its limits are narrower than the old presentation claimed.

### Gaps

An acceptable engineering error tolerance must be agreed or justified from the intended use. There is no independent experimental material validation available in the current folder.
