# Which ML model to build: Claude's independent analysis

Prepared by Claude, 24 October 2026, for review by Codex and the user. This is **reported work, not yet independently reproduced**. Each number below links to a saved artifact and a command that regenerates it. Nothing here changes `context.md`, `decisions.md` or `research.md`; Codex owns those files and will merge whatever is agreed.

## Recommendation

**Main model: a small query MLP.** Given a material condition and one strain value, it predicts one stress value. Asking it for all 120 strain values draws the full stress–strain curve.

- Inputs: temperature, log10(strain rate), density, shear modulus G, and axial strain E11.
- Network: two hidden layers of 16 tanh units. The L2 penalty was chosen by training-side cross-validation (§5): 1e-5 for SCAU11, 1e-3 for Svm.
- Ensemble: the prediction averages **5 networks trained from different random starts**. Each network has 385 weights and biases, so the ensemble stores 1,925. Whether an ensemble counts as one "model" under the course limit is unresolved.

It is about 10–25× better than a no-learning baseline on the professor's random split. **Its real strength is conditions it has never seen**: with one whole (temperature, rate) condition hidden from training, it has the lowest mean error.

**Comparison model: PCA + Gaussian process.** With settings chosen inside the training half (6 PCA components), it is **the most accurate model on the professor's random split**:

| Target | PCA + GP | Query MLP |
|---|---|---|
| SCAU11 | 0.058 MPa | 0.096 MPa |
| Svm | 0.057 MPa | 0.059 MPa |

It extrapolates worse to unseen conditions, and its uncertainty bars **failed** a calibration check (§4). So the trade-off is between interpolation (GP) and extrapolation (MLP), and the choice of second model belongs to the user. It is not clearly better than Codex's proposed PCA-coefficient MLP, which has not been run. Two open questions bear on the choice:

- whether the professor's "two models" limit counts non-neural models;
- whether the professor wants an architecture comparison.

**Always report a lookup baseline.** It copies the closest training curve with the same temperature and rate. Without it, a 0.1 MPa error would look like deep generalisation, when the random split mostly tests interpolation between near-identical curves.

**Coefficient of lift.** No model can learn porosity → C_L from this dataset, for two reasons:

- It contains no lift labels.
- Its curves contain no elastic segment, so they carry no stiffness information.

C_L requires separate aerodynamic information (questionnaire Q01–Q04). This is a statement about the data, not a proposed physical chain.

## 1. What the data says

All 73 `STR_STR.OUT` files were parsed. Every curve was resampled onto 120 strain points between 0.0002 and 0.0999, using `src/data.py`. Each case then counts equally, whatever its row count: 1,000, 10,000 or 100,000 rows, depending on strain rate.

**Factor effects.** For each factor, I compared pairs of cases that differ only in that factor, by one level. The measure is the mean, over all such pairs, of the largest stress difference along the curve.

| Factor varied by one level | Mean max \|Δσ\| | Largest |
|---|---|---|
| Temperature | 29.8 MPa | 94.0 MPa |
| log10 strain rate | 21.2 MPa | 72.7 MPa |
| Shear modulus G (3 % or 5 % steps) | 4.5 MPa | 10.6 MPa |
| Density (3 % or 5 % steps) | **0.25 MPa** | 0.59 MPa |

Density is almost inert in the generating solver. Over its whole range, from 2700 down to 2488 (a candidate "porosity" of 0–7.85 %), stress changes by about 0.2 %. If porosity matters to the project, the only visible lever in this data is G, and even that effect is small.

**Coverage.** There are 3 temperatures (30, 100, 200) × 3 rates (1e-5, 1e-4, 1e-3), giving **9 conditions**. Eight conditions have 9 cases each. **200 °C / 1e-5 has a single case, case 60.** There are no 300 °C outputs.

**Curve shape.** Every curve starts at its peak stress, about 105–160 MPa, already at E11 = 1e-6, and then softens. There is no elastic loading segment. Case 60 collapses irregularly between E11 ≈ 0.05 and 0.08 (see `figures/SCAU11/case60_extrapolation.png`). This matches Codex's audit finding of reversing `Evm` in that case. It may be an unstable or damaged run, not merely an unusual condition; questionnaire Q28 asks the professor.

**Low rank.** Exploratory PCA on all 73 curves reconstructs every curve to within 0.9 MPa with 4 components. This was descriptive only. The operational PCA inside `PcaGP` is refitted on training cases only.

**Target.** The primary target is `SCAU11`, the axial Cauchy stress, which is the conventional tensile-curve stress. `research.md` proposed `Svm`. The two differ only through about 4 MPa shear components, Svm ≈ √(SCAU11² + 3·Σshear²). Both targets were run and are reported separately below; scores must not be compared across targets.

## 2. Professor's protocol: random 36/37 case split

> **These are the exploratory-settings results** (MLP L2 1e-4, PCA rank 4), from `evaluate.py`. The cross-validation-chosen settings and their test scores are in §5, and those are the numbers to report. Both sets share the selection-history caveat in §5.

The split uses seed 42 and is saved in `data/split.json`; it was made once and never re-rolled. Case 60 fell into training. All 9 conditions appear in training, but 30 °C / 1e-4 has only one training case. Values below are the per-test-curve RMSE in MPa, averaged over the 37 test cases.

| Model | SCAU11 mean | SCAU11 median | SCAU11 worst | Svm mean | Svm worst |
|---|---|---|---|---|---|
| Lookup baseline | 1.375 | 0.288 | 4.963 | 1.379 | 4.979 |
| **Query MLP** | **0.139** | 0.086 | 0.402 | **0.078** | 0.188 |
| PCA + GP | 0.152 | 0.152 | 0.349 | 0.153 | 0.346 |
| Query MLP without density | 0.196 | 0.200 | 0.473 | 0.249 | — |

The MLP's four worst test cases (10, 13, 16 and 11) are all **30 °C / 1e-4**, the condition with only one training curve. Error therefore tracks training coverage per condition, which is what interpolation predicts.

## 3. Harder diagnostic: leave one (T, rate) condition out

This is an extra diagnostic, reported separately from the professor's split. In each fold, all cases of one condition are held out and the model trains on the rest. It is the only test here of predicting a condition never seen in training. Values are mean per-case RMSE in MPa, for target SCAU11.

| Held-out condition | Lookup | Query MLP | PCA + GP |
|---|---|---|---|
| 30 °C, 1e-5 | 6.8 | **5.2** | 8.0 |
| 30 °C, 1e-4 | 6.8 | **2.0** | 3.6 |
| 30 °C, 1e-3 | 7.5 | **3.4** | 4.5 |
| 100 °C, 1e-5 | 7.5 | **9.7** | 10.2 |
| 100 °C, 1e-4 | 7.5 | 5.4 | **5.2** |
| 100 °C, 1e-3 | 8.5 | **3.3** | 6.9 |
| 200 °C, 1e-5 (case 60) | 35.6 | 23.5 | **22.8** |
| 200 °C, 1e-4 | 19.4 | 12.9 | **12.0** |
| 200 °C, 1e-3 | 17.4 | **10.4** | 17.0 |

For the Svm target the MLP's leave-one-condition-out errors are:

| Temperature | Query MLP (Svm) |
|---|---|
| 30 °C | 1.3–3.7 MPa |
| 100 °C | 1.8–7.7 MPa |
| 200 °C | 7.9–24.1 MPa |

PCA + GP edges ahead at 30 °C / 1e-3 and 100 °C / 1e-3, but is roughly twice as bad at 200 °C / 1e-3 (16.3 vs 7.9 MPa). The full table is in `runs/20261024-192106_Svm/metrics.json`.

For SCAU11, the MLP wins 6 of 9 conditions and is close on the rest. Errors at 200 °C are 10–24 MPa against stresses of 0–140 MPa. Neither model should be trusted for 200 °C combinations it has not seen, nor for 300 °C at all.

## 4. GP uncertainty check (failed)

For each leave-one-condition-out fold, I computed the fraction of held-out curve points inside the GP's mean ± 2σ, using `src/gp_calibration.py`. Calibrated uncertainty would put this near 95 %.

| Held-out condition | Points inside ±2σ (SCAU11) |
|---|---|
| 30 °C, all rates | 100 % |
| 100 °C, 1e-3 | 100 % |
| 100 °C, 1e-4 | 76 % |
| 100 °C, 1e-5 | 22 % |
| 200 °C, 1e-4 | 25 % |
| 200 °C, 1e-5 | 33 % |
| 200 °C, 1e-3 | **0 %** (mean σ 3.4 MPa, mean error 16.9 MPa) |

Svm is near-identical. The GP is overconfident exactly where it extrapolates, so **its σ must not be presented as an extrapolation warning.** Codex raised this risk before the check was run.

One useful by-product: the GP's fitted length-scale for density sits at its upper bound of 1000. The GP independently learned that density does not matter.

## 5. Selection history (honest disclosure)

The selection was not done cleanly:

1. Before the pipeline existed, I explored all 73 cases in a scratchpad. That exploration used 10 random 36/37 splits and leave-one-condition-out folds to compare five candidate models:
   - lookup baseline;
   - PCA-4 + quadratic regression;
   - PCA-4 + GP;
   - query MLP 5-16-16-1;
   - query MLP without density.
2. The MLP's size (16-16 tanh), its L2 penalty (1e-4), PCA rank 4 and the GP kernel were all **chosen during that exploration, not by validation inside the training half**. The candidate list, and the tanh activation and kernel family, also came from that exploration.
3. **The seed-42 test cases therefore influenced model selection.** They were excluded from each individual fit, but they were part of the comparisons that decided which models and settings to carry forward. The current test set is not blind, and later steps cannot make it blind again.

**Training-side selection, run afterwards.** `src/select_settings.py` splits the 36 training cases into 3 case folds (12 cases each, fold seed 42). It scores 9 MLP settings (hidden 8-8 / 16-16 / 32-32 × L2 1e-5 / 1e-4 / 1e-3) and 4 GP ranks (3–6). The winner of each model family is refitted on all 36 cases and scored once on the 37 test cases. The full history is in `runs/selection_<target>.json`; the fitted models and test predictions are in `runs/selected_<target>/`.

| Model | Setting chosen | Cross-validation mean RMSE | Test mean RMSE | Test worst RMSE |
|---|---|---|---|---|
| Query MLP, SCAU11 | 16-16, L2 1e-5 | 1.24 | 0.096 | 0.308 |
| PCA + GP, SCAU11 | 6 components | 0.67 | **0.058** | 0.157 |
| Query MLP, Svm | 16-16, L2 1e-3 | 1.16 | 0.059 | 0.113 |
| PCA + GP, Svm | 6 components | 0.66 | **0.057** | 0.147 |

All values are in MPa. Observations:

- **Cross-validation error is about 10× the test error.** Each fold trains on only 24 cases, so some (T, rate) conditions have 0–2 training examples. That makes the folds closer to extrapolation than the full 36-case fit is.
- **The 32-32 networks were consistently worst**, so this data favours small networks. Rank 6 was the largest GP rank tried. Leave-one-condition-out errors were identical for ranks 6, 8 and 10, because at unseen conditions the GP reverts its higher-rank coefficients to the mean.
- With the chosen settings, **leave-one-condition-out mean RMSE (averaged over the 9 conditions)** is:

  | Model | SCAU11 | Svm |
  |---|---|---|
  | **Query MLP** | **8.3 MPa** | **7.5 MPa** |
  | PCA + GP | 10.0 MPa | 8.8 MPa |

  Saved in `runs/loco_chosen_settings.json`.
- **Optimiser warnings.** These come from the **GP**, not the MLP; `src/score.py` now counts them. GP kernel fits stopped with an L-BFGS "ABNORMAL" warning, and some GP noise levels hit their 1e-10 lower bound: 49 warnings per full selection run. The query-MLP fits raised 0 warnings. (An earlier version of this report attributed the ABNORMAL warnings to the MLP, which was wrong.)

These are the numbers I would report. They still carry the disclosure in point 3 above.

## 6. Reproduce

```bash
cd /home/sarvn/Documents/MMM-ML
python3 -m venv .venv && .venv/bin/pip install numpy scipy matplotlib scikit-learn joblib
.venv/bin/python src/data.py                              # parse 73 cases -> data/curves_{SCAU11,Svm}.npz, data/manifest.json (sha256 per file)
.venv/bin/python src/split.py                             # seed-42 36/37 split -> data/split.json (created once, then reused)
.venv/bin/python -W ignore src/evaluate.py --target SCAU11  # about 5 min single-threaded
.venv/bin/python -W ignore src/evaluate.py --target Svm
.venv/bin/python -W ignore src/gp_calibration.py --target SCAU11
.venv/bin/python -W ignore src/select_settings.py --target SCAU11   # training-only selection + saved models
.venv/bin/python -W ignore src/select_settings.py --target Svm
# Demo: predict a curve for any condition (warns when outside the training ranges)
.venv/bin/python -W ignore src/predict.py --temperature 100 --rate 1e-4 --density 2619 --G 24541 --plot curve.png
```

Demo check: test case 14 (30 °C, 1e-4, ρ 2619, G 24541) was not in either model's training data. `predict.py` reproduces its simulated Svm curve with an RMSE of 0.085 MPa for the MLP and 0.094 MPa for the GP.

Versions used: Python 3.10.12, numpy 2.2.6, scipy 1.15.3, scikit-learn 1.7.2, matplotlib 3.10.9.

| Artifact | Contents |
|---|---|
| `runs/<time>_<target>/metrics.json` | summary metrics, ablation and leave-one-condition-out results |
| `runs/<time>_<target>/per_case.csv` | per-case RMSE and MAE, both protocols |
| `runs/<time>_<target>/random_split_predictions.npz` | test-case truth and predictions |
| `runs/<time>_<target>/models/*.joblib` | fitted random-split models; `evaluate.py` asserts that reloading reproduces predictions |
| `runs/<time>_<target>/config.json` | settings, split and versions |
| `runs/gp_calibration_<target>.json` | GP uncertainty coverage per condition |
| `runs/selection_<target>.json` | full training-side selection history, fold assignment, chosen settings and test scores |
| `runs/selected_<target>/*.joblib` | **the models to demo**: the CV-chosen models refitted on all 36 training cases, with test predictions; reload is checked |
| `runs/loco_chosen_settings.json` | leave-one-condition-out results with the CV-chosen settings |
| `figures/<target>/` | random-split curves (best/median/worst), leave-one-condition-out bars, case-60 extrapolation |

## 7. Units

No authoritative unit source exists yet (questionnaire Q07 and Q29). These are numerical inferences only:

- **Temperature:** matrix values are probably °C, because output `TEMP` equals the matrix value + 273.15.
- **Strain rate:** probably 1/s, because E11 = rate × TIME to within 4e-8 (Codex's audit).
- **Stress:** "MPa" is used throughout as a working label. It is consistent with AlSi10Mg flow stresses of about 100–160 MPa, but unconfirmed.
- **G and density:** probably MPa and kg/m³ (25.3 GPa and 2700 kg/m³ are plausible for aluminium alloys), also unconfirmed.

## 8. Agreements and disagreements with `research.md`

| Topic | research.md | This report |
|---|---|---|
| Main model | query MLP, 5-16-16-1 | **agree**; trained as a 5-network ensemble: 0.06–0.10 MPa on the random split, best on unseen conditions |
| Second model | PCA-coefficient MLP | PCA + GP was tried: best on the random split, worse on unseen conditions, uncertainty uncalibrated. **Open** |
| Evaluation | random 36/37 split, seed 42, internal case folds | agree; adds a lookup baseline and leave-one-condition-out. Internal 3-fold case selection is **done**, but only after exploration (§5) |
| Target | Svm | SCAU11 primary, Svm also reported |
| Density | input, meaning unresolved | keep as input, but it is nearly inert (ablation, factor effects, GP length-scale) |
| Case 60 | retain and flag | agree; also looks like an irregular collapse, not only a sparse condition |
| C_L | unresolved, no labels | agree; additionally, the curves contain no stiffness information |
