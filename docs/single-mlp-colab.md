# Fresh single MLP and exact equation - 2 November 2026

User chose the exact MLP prediction equation and requested testing the proposal.
The new experiment is src/single_mlp.py, with configs/single_mlp.json. It trains
one 5-16-16-1 tanh network (385 parameters), seed 42, rather than averaging the
five historical networks. The existing delivered model is preserved.

Inputs: matrix temperature, log10(rate), density, G and E11. Output: Svm.
Each case contributes 120 equally weighted queries on E11=0.0002 to 0.0999.
Fixed assumed porosity 0.04 is metadata and not an informative extra feature.

## Selection and evaluation

Preserve the fixed 36/37 case split. On the 36 training cases, compare alpha
0.0001, 0.001 and 0.01 with three whole-case folds (seed 42). Fit every input
and response scaler within its fitting fold. Select by mean per-case RMSE;
an exact tie favors the stronger alpha. Architecture and initialization are
fixed. Use L-BFGS, max_iter=5000, max_fun=50000, tol=1e-9; retain all warnings.

Compare against the existing temperature/rate-matched curve-copy baseline.
For all nine training temperature/rate groups, withhold that group and reselect
alpha by case CV inside the remaining data. Refit on those remaining cases and
score the omitted group. These diagnostics do not consume final-test targets.

Fit the selected model on all 36 training cases. Save its weights and equation,
and write selection_lock.json before loading/scoring the 37 test histories.
The test set has historical exposure, so this is not a newly blind validation.
Scores describe the supplied loading family and matrix coverage; physical units
and experimental validity remain unresolved. Case 60 stays included and flagged.

## Exact numerical equation

For x=[T,log10(rate),density,G,E11], define z=(x-mean)/scale.

Svm = target_mean + target_scale * (w3.T tanh(W2 tanh(W1 z+b1)+b2)+b3).

The exported equation.json contains every weight, bias and scaling value. W1
is 16x5, W2 is 16x16 and w3 has 16 entries. This empirical equation represents
the trained network; it is not a material governing law. Independent NumPy
inference must match sklearn to 1e-10 source stress units, including JSON reload.

## Run

Run `python src/single_mlp.py --output reports/NEW_DIRECTORY`.
The notebook notebooks/single_mlp_equation.ipynb embeds this same code and split.
Set its Drive ZIP path, then execute in order. Hosted Colab execution and Drive
access are not verified by local execution. The completed local result and verification are recorded in
[reports/single_mlp_20261102/README.md](../reports/single_mlp_20261102/README.md).
Mean test RMSE is 0.142667 versus baseline 1.378978; the exact equation reload
difference is 0.0. Missing-condition performance is weaker (up to 43.236012 RMSE).
Four focused tests and independent saved-result verification pass.
