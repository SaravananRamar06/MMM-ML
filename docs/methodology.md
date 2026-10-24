# Modelling plan and scientific limits

Status: **proposed workflow, not an implemented or professor-approved architecture**.

Later update: Claude has separately implemented a pipeline and reported experiments, pending independent review. Earlier no-implementation statements in this planning document describe Codex's research-completion snapshot. Read the latest state in `context.md` and coordinate through the room before duplicating work.

The user requested research before implementation. No model or training pipeline has been created. The research-backed recommendation is a compact MLP for the observed material-response loading family, not an empirically proven best model. A physics-informed loss is a training choice and can use an MLP backbone; it is not automatically a separate architecture. See [research.md](research.md) for primary sources, audit evidence, and the complete development workflow.

## Research recommendation as of 2026-10-24

- First candidate: `(temperature, log10(strain_rate), density, shear_modulus, E11) -> Svm`, starting provisionally at `5–16–16–1` (385 parameters).
- Second candidate, only if training-side reconstruction supports it: four conditions -> small MLP -> training-only PCA coefficients -> reconstructed curve.
- All 73 cases have strictly increasing `E11`; case 60 has reversing `Evm`. All histories finish below their initial `Svm`. Retain case 60 and avoid assumed hardening/zero-origin constraints.
- Exact common measured `E11` interval is `[0.0001, 0.09999996]`; verify interpolation fidelity before operational sampling. Units and generating law remain unresolved.
- Proposed experiment: one random 36-training/37-test case split, seed 42, then three internal case folds for preprocessing and model selection. This split/seed is recommended, not executed.
- Equalise curve contributions; assess original-unit per-case MAE/RMSE, worst cases, and condition breakdowns. Use a mean-curve reference, not an unnecessary third neural network.
- All-data EDA/PCA has occurred. Its statistics are descriptive, not prediction accuracy or a reusable PCA basis. Fit operational transforms inside training folds only.

**Target correction, 2026-10-24:** the user explicitly confirmed **CL = coefficient of lift**. Earlier critical-flaw-length planning is superseded. The old deck's fracture calculation is not a method for predicting aerodynamic CL.

## Two intended capabilities

### A. Predict material stress–strain response

Recommended initial formulation: prescribed temperature, log strain rate, density, shear modulus, and an `E11` query go into a compact feed-forward neural network; recorded `Svm` comes out. Evaluating a range of strain queries produces a curve. These are operational column choices supported by the audit; full physical definitions remain unconfirmed.

A small multilayer perceptron (MLP) is a reasonable first candidate for these scalar conditions. A sequence model is not justified solely because each file contains many time rows. Check for history dependence and the actual loading protocol before selecting an architecture.

Alternative: predict coefficients of a reduced curve representation. Compare complexity and data needs before committing. These are candidate formulations, not permission to train an unlimited number of competing models.

### B. Relate porosity to coefficient of lift, C_L

The current files do not directly label porosity or lift coefficient. Before choosing or training a model for this capability, establish:

- How porosity is measured or derived, and whether density/modulus can legitimately encode it.
- The professor's intended aerodynamic problem, geometry, operating conditions, and coefficient definition/reference quantities.
- Where lift-coefficient labels come from: supplied aerodynamic data, new calculations/simulations, or measurements.
- How material conditions/porosity are supposed to connect to aerodynamic response. Do not assume a coupling mechanism without evidence.
- Whether an additional learned model contributes information beyond a deterministic physical calculation.

A porosity-only mapping needs its other conditions specified. Neither the material dataset nor the old fracture deck establishes that mapping. Reconfirm what the professor expects before designing the aerodynamic portion.

## Superseded fracture interpretation

The submitted presentation incorrectly interprets CL as critical flaw length and uses:

`a_c = (1 / pi) * [K_IC / (Y * K_t(phi) * sigma)]^2`

This equation belongs to the **superseded fracture interpretation**, not the current target. Do not use it to create coefficient-of-lift labels or select an aerodynamic model. The submitted PDF is preserved as a record; its CL narrative needs correction before reuse.

The historical porous-cell `K_t(phi)` and Cockcroft–Latham results are not aerodynamic labels. Recovering that code is not a prerequisite to material-surrogate work and will not by itself establish lift prediction.

If new labels are generated from an assumed equation, describe the model as a surrogate of that calculation. Do not claim independent aerodynamic validation merely from fitting calculated labels.

## Data and training workflow

1. Preserve raw data; build a case manifest with ID, conditions, output presence, row count, support, and quality flags.
2. Verify units, meanings, tensor conventions, initial state, and curve shapes. Document any unresolved interpretation.
3. Save one reproducible random case split with the professor's 50/50 proportion. Research recommends 36 training/37 test and seed 42; no split has yet been created or locked.
4. Keep all versions of a case in its partition. Fit normalisation and any learned curve representation on training cases only.
5. Use balanced sampling or a justified common strain grid so 100,000-row cases do not overwhelm 1,000-row cases. Avoid inventing a zero-strain origin or extrapolating truncated curves.
6. Select/tune architectures and early stopping using only the training side, with internal case-level validation or cross-validation. Do not tune against the final test set.
7. Begin with a compact network and clear losses. Physics penalties are optional and must be compatible with observed response; do not enforce monotonic stress without evidence.
8. Evaluate on held-out cases in original units: per-case MAE/RMSE, aggregate errors, representative and worst-case curves, and error by condition. State the effective number of independent cases.
9. Establish the aerodynamic workflow only after the professor's intended connection and target-label source are clear. Decide whether it needs the optional second network or a separate calculation.
10. Save preprocessing, model weights, configuration, seed, split IDs, predictions, dependency versions, and run metadata. Ensure a clean inference command works before reporting completion.

## Model-count constraint

The user recalls **at most two neural-network models**. Treat this as a planning limit pending confirmation. Do not interpret the old deck's five regression candidates or five-fold protocol as current requirements. Research recommends comparing query MLP and conditional PCA-coefficient MLP for the material task. Aerodynamic response still lacks a target definition/data source sufficient for implementation.

## What would justify a multiscale claim?

Describe the source scale of the supplied simulations, what effective quantity is learned, how it is passed to a larger-scale calculation, and what validates that transfer. The generating scale of the professor's simulations is currently unknown. Merely adding a bracket image to a material regression does not establish multiscale coupling.

## Proposed implementation layout

Create only when implementation begins:

```text
src/          parsing, preprocessing, model, training, evaluation, inference
configs/      experiment settings
data/         derived manifests, split IDs, processed data (raw source stays intact)
runs/         configurations, checkpoints, metrics, predictions
figures/      plots backed by saved results
tests/        focused parser, split, unit-conversion, and inference checks
```

No folders or code in this proposed layout have been created as part of the documentation task.
