# Dataset evidence for architecture selection

Inspection date: 24 October 2026. Read-only audit; no neural network trained, no case split saved, and no source files changed. Reproduce with `OPENBLAS_NUM_THREADS=1 python3 'research_notes/Neural networks for material curves/inspect_curves.py'` from the project root. Numerical evidence is in [curve_inspection.json](</home/sarvn/Documents/MMM-ML/research_notes/Neural networks for material curves/curve_inspection.json>) and the [inspection script](</home/sarvn/Documents/MMM-ML/research_notes/Neural networks for material curves/inspect_curves.py>). Files are in the stated notes folder.

## What do the actual curves imply about the input representation?

### Takeaway

A scalar query network using prescribed axial `E11` and the four material conditions is the most defensible first formulation. The available histories show strictly increasing axial loading, not evidence of the varied loading paths that would establish a need for recurrent memory; this does not prove the underlying material is path-independent.

### Cited Findings

- All **73** available histories were parsed, covering **2,197,000 rows**; every numerical entry was finite and every `E11` series was strictly increasing. `E11 = strain_rate × TIME` agrees within maximum absolute error **4.0e-8**. First `E11` values are 1e-6, 1e-5, or 1e-4; final values are 0.1 except case 60 at 0.09999996. Thus exact common measured `E11` support is **[0.0001, 0.09999996]**. The descriptive analysis uses 501 points on **[0.0001, 0.0999999]**, entirely within all cases. — [Local audit](</home/sarvn/Documents/MMM-ML/research_notes/Neural networks for material curves/curve_inspection.json>).
- Every history ends at lower `Svm` than it begins. Initial `Svm` spans **105.374–160.3209**, final values **6.289917–95.39303**, in unconfirmed source stress units. Peak stress occurs at axial strain no later than 0.0001. These are observed softening/decreasing-response histories, not the monotone-hardening picture in the historical deck. — [Local audit](</home/sarvn/Documents/MMM-ML/research_notes/Neural networks for material curves/curve_inspection.json>).
- Applying the standard von-Mises combination to the recorded Cauchy components reproduces `Svm` within maximum relative error **9.85e-7**. Applying a naive deviatoric tensor equivalent-strain formula to recorded strain components does **not** reproduce `Evm` (worst relative mismatch about 17%). Case **60** has **237 negative Evm increments**, despite strictly increasing `E11`; no other case does. — [Script and formula](</home/sarvn/Documents/MMM-ML/research_notes/Neural networks for material curves/inspect_curves.py>), [results](</home/sarvn/Documents/MMM-ML/research_notes/Neural networks for material curves/curve_inspection.json>).
- There are no exactly identical curves on the inspected common grid. One-factor matched-pair median curve RMSEs are roughly **12.93** for temperature, **8.54** for rate, **3.06** for modulus, and **0.184** for density, in source stress units. These comparisons hold other matrix parameters fixed and are descriptive, not causal estimates. — [Local audit](</home/sarvn/Documents/MMM-ML/research_notes/Neural networks for material curves/curve_inspection.json>).

### Inferences

- Recommend a compact MLP, provisionally `(T, log10(rate), density, shear_modulus, E11) -> Svm`, limited to this observed loading family. Current evidence does not justify LSTM/GRU just because the files have time rows.
- Prefer `E11` as the first query axis over blindly using `Evm`: it is demonstrably monotonic, prescribed, and common across cases. Choice of axes is still a modelling convention pending scientific definitions.
- Do not impose positive stress slope, a zero-stress origin, or an old Johnson–Cook curve as a physics penalty: the supplied histories contradict those assumptions or do not cover that origin.
- Keep density as a candidate feature initially, but do not call it porosity. Its comparatively weak effect also means a random case split can put almost matching curves on both sides, so good interpolation scores do not establish robust extrapolation.

### Gaps

Stress units, actual strain definition, initial state, generating law, and why the response softens remain unconfirmed. Case 60 is conspicuous (minimum `Svm` 1.031385 and final 6.289917), but the audit does not identify it as a failed solve. Retain and flag it; do not silently delete it.

## Is a reduced curve-coefficient network a meaningful second candidate?

### Takeaway

Yes: the curves have strong descriptive low-rank structure. This supports investigating a small conditions-to-PCA-coefficients MLP as a second model, but **does not** prove it generalises or fix the final number of components.

### Cited Findings

- Mean-centred SVD of all **73** resampled `Svm(E11)` curves gives cumulative variance **85.13% / 98.94% / 99.964%** for one/two/three components. These are **full-dataset exploratory reconstruction statistics**, not train-only estimates, validation results, or prediction accuracy. — [Local audit](</home/sarvn/Documents/MMM-ML/research_notes/Neural networks for material curves/curve_inspection.json>).
- With a rank-two full-data reconstruction, worst-case curve RMSE is **10.67**, belonging to case 60, despite aggregate variance capture of 98.94%. Rank-three worst reconstruction RMSE is **0.831**, belonging to case 72. Explaining aggregate variance alone can conceal a problematic case. — [Local audit](</home/sarvn/Documents/MMM-ML/research_notes/Neural networks for material curves/curve_inspection.json>).
- Official guidance identifies PCA, scaling, and feature selection as transforms that must be fitted using training data only, with the learned transform subsequently applied to held-out cases. — [Scikit-learn common pitfalls, accessed 24 October 2026](https://scikit-learn.org/stable/common_pitfalls.html).

### Inferences

- A meaningful two-model comparison is **query MLP** versus **PCA-coefficient MLP**, because they represent a curve differently and exploit the small number of independent conditions differently.
- The coefficient model would have four condition inputs and a small coefficient output, followed by reconstruction on the common strain grid. Fit the curve mean/basis only within each training fold; select rank by training-side curve reconstruction and prediction validation, not these exploratory percentages.
- Keep case 60 in the primary comparison and show its error separately. A basis learned without a representative version of its unusual shape might reconstruct it badly.

### Gaps

No coefficient predictor has been trained and no train-only PCA basis evaluated. The exploratory SVD is expressly **not** a reusable final preprocessing artifact. All-curve inspection has occurred before a final holdout was locked; disclose this EDA rather than describing the later test set as never previously inspected.

## What is a defensible model-selection experiment?

### Takeaway

Use the requested random 50/50 split at the simulation-case level, preserving a separate final evaluation. Select architecture details using internal case-level validation on the training half.

### Cited Findings

- Grouped samples violate a simple independent-row assumption; grouped cross-validation keeps every group's samples outside the paired training fold. `GroupShuffleSplit` supports random group holdouts. For this dataset, the appropriate group identifier is the simulation ID. — [Scikit-learn grouped cross-validation](https://scikit-learn.org/stable/modules/cross_validation.html#cross-validation-iterators-for-grouped-data).
- Tuning parameters using the final test set leaks information; training-side cross-validation can choose settings while preserving a final test evaluation. — [Scikit-learn evaluation guidance](https://scikit-learn.org/stable/modules/cross_validation.html).

### Inferences

- With 73 cases, document 36 training/37 test (or the opposite), persist one random seed/manifest, and do not retry seeds to improve scores.
- Inside the training partition use case-level folds, preferably 3–5 folds given the limited case count; all preprocessing, PCA, architecture/loss choices, and stopping decisions stay inside that partition.
- Balance curves by equal resampling or case-normalised losses: a slow-rate case has up to 100 times more rows than a fast-rate case, without providing 100 independent loading histories.
- Compare models on the same retained cases with per-case MAE/RMSE and condition-wise errors, giving worst-case plots alongside averages. An optional leave-condition-level-out analysis on training data probes extrapolation without replacing the professor's required split.

### Gaps

No saved split or evaluated model exists. No 300-temperature outputs are available. No coefficient-of-lift labels or aerodynamic input fields are present, so this architecture recommendation addresses the material-response subproblem only.
