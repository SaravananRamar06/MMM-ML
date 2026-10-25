# AlSi10Mg stress–strain prediction for an aircraft wing bracket

We developed a small neural-network surrogate for the simulated stress response of an additively manufactured AlSi10Mg aircraft wing bracket (wing-rib bracket) for the course **Multiscale Modelling of Materials using Machine Learning**. It predicts the material's simulated stress response from temperature, strain rate, density, shear modulus and axial strain.

The completed model returns a 120-point curve of **von Mises stress (`Svm`) against axial strain (`E11`)**. A local Model Studio lets us request and compare curves in plain language. The wider porosity-to-coefficient-of-lift objective for the wing bracket still needs aerodynamic data and a defined connection to the structural FE model.

## Start here

- [Research paper (IEEE)](<project files/Research Paper.pdf>): three-page publication-format research paper on the aircraft wing bracket surrogate model (`paper/paper.tex`).
- [Course report](<project files/Final Course Report.pdf>): fact-checked five-page LaTeX report with corrected figures, references and limitations; source and build record in `report/`.
- [Simple model guide](<project files/My model explained.html>): preparation, training and prediction explained in a personal voice for study and presentation. [Markdown version](<project files/My model explained.md>).
- [Latest test results](<project files/Model test results.md>): fresh checks, error measures and limits, dated 25 October 2026.
- [Presentation](<project files/AlSi10Mg Stress–Strain ML.pptx>): 24 slides with speaker notes. The slides are images; source text is retained in `reports/presentation/slides.md`.
- [Project documents](<project files/README.md>): available guides, research paper and presentation files.

## What we have completed

| Stage | Completed work |
|---|---|
| Data inspection | Inventoried 73 available histories from 108 planned simulations; checked 2,197,000 rows and documented missing cases and unusual curves. |
| Preparation | Matched conditions to simulation IDs, checked source hashes and interpolated every curve to the same 120 strain points. |
| Evaluation design | Saved a fixed seed-42 split of 36 training cases and 37 test cases. All points from a simulation remain together. |
| Model development | Compared the query MLP, a PCA-coefficient MLP, a PCA/Gaussian-process reference and additional variants using saved training-side evaluations. |
| Final predictor | Saved a five-network query MLP ensemble, preprocessing, test predictions and per-case errors in `runs/score/final_Svm/`. |
| Model checks | Recomputed errors, checked training-only scalers, reproduced a frozen-settings refit and checked equivalent NumPy inference. |
| Interface | Built Model Studio with curve comparisons, point queries, tables and range warnings; provided command-line prediction. |
| Documentation | Prepared a 24-slide presentation, a detailed reference guide, a simple personal guide and reproducible verification reports. |

The material prediction workflow is implemented. Experimental validation, verified ANSYS coupling and aerodynamic lift prediction remain open.

## Run Model Studio

From the project root:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python app/server.py
```

Open **http://127.0.0.1:8766**. Try:

```text
stress curve at 100 C, rate 1e-4, density 2619, G 24541
compare 30, 100 and 200 C at 1e-3 /s
stress at 5% strain for 100C, density 2619, G 24541
how accurate is it?
```

The interface uses a deterministic text parser and locally saved predictors. It needs no LLM or API key. Check its displayed defaults when a condition is omitted. The Gaussian-process line is a comparison reference; the MLP is the final material predictor.

To save a prediction directly:

```bash
.venv/bin/python src/predict.py --model mlp --target Svm --temperature 100 --rate 1e-4 --density 2619 --G 24541 --plot curve.png --csv curve.csv
```

Saved models support inference without the raw dataset. Rebuilding prepared data or running the full source audit requires the professor-supplied files, which are excluded from the published repository.

## How the model works

Each file represents one simulation condition. Histories have different lengths, so we interpolate every curve to **120 equally spaced E11 values from 0.0002 to 0.0999**. This gives each case the same number of training examples.

```text
temperature, log10(strain rate), density, shear modulus, E11
                            ↓
               standardise using training statistics
                            ↓
          five networks, each shaped 5 → 16 → 16 → 1
                            ↓
         average outputs and restore the stress scale
                            ↓
                          Svm
```

Each network uses two hidden layers with 16 tanh units and a linear output: **385 weights and biases per network**, or **1,925 across the ensemble**. The saved settings use L-BFGS, L2 penalty 0.001 and initialisation seeds 0–4. Querying all 120 strains produces a curve.

We fit scalers and final weights using the 36 training cases only: 36 × 120 = **4,320 query points**, derived from 36 simulations. These are not 4,320 independent simulations. Internal case folds and condition holdouts were used for comparison. Earlier exploration had used all 73 cases, so the final test set is a previously explored holdout.

## Results checked on 25 October 2026

Errors below are in **source stress units**. MPa is plausible but has not been confirmed by the data owner.

| Fresh check on the existing 37-case test split | Result |
|---|---:|
| Mean per-curve RMSE | **0.05908515** |
| Median per-curve RMSE | 0.05056666 |
| Worst per-curve RMSE | 0.11330618, case 45 |
| Mean per-curve MAE | 0.04899859 |
| RMSE pooled over all test points | 0.06486281 |
| Maximum pointwise absolute error | 0.28832028 |

All 73 source curves reproduce the cached interpolation exactly. Reloaded predictions and NumPy-runtime predictions match the saved model exactly in this environment. A fresh fit with frozen settings reproduced every weight and prediction exactly, without warnings. **13 unit tests and 3 live Model Studio tests passed.** Delivered model files were unchanged.

These checks confirm repeatable software behaviour and agreement with supplied simulations. They do not establish experimental or aerodynamic accuracy. The saved training-side three-fold CV mean curve RMSE is **1.15826321**; the mean over nine held-out temperature/rate groups is **6.79360255**, rising to **23.52512868** for the 200 / 1e-5 group. Those diagnostics were read from saved results, not rerun in this retest.

![Fresh check of case 42 and the worst test case](reports/retests/20261025T172218Z/test_curves.svg)

The random split mostly tests interpolation between related simulated conditions. Hiding an entire temperature/rate group is harder. The low random-split error is not proof of reliable prediction at new operating conditions.

## Data coverage and scientific limits

The matrix plans 108 cases. Available histories cover 27 cases at temperature 30, 27 at 100 and 19 at 200; **none are available at 300**. Temperature is interpreted as °C, rate as s⁻¹, density as kg/m³ and modulus as MPa, subject to confirmation.

| Input | Available levels or operational range |
|---|---|
| Temperature | 30, 100, 200; incomplete coverage at 200 |
| Strain rate | 1e-5, 1e-4, 1e-3 |
| Density | 2488.05, 2619, 2700 |
| Shear modulus G | 23313.95, 24541, 25300 |
| Curve query E11 | 0.0002–0.0999 |

Values between levels are interpolation requests, not independently validated conditions. Outside the range, the model extrapolates. Case 60 is the only available 200 / 1e-5 case and has an irregular response; it remains in the dataset. The histories do not supply a conventional zero-stress elastic loading segment, so we have not established an elastic modulus from their initial slope.

Density and shear modulus are supplied inputs. Neither has been verified as a porosity label. **C_L means aerodynamic coefficient of lift**, not critical flaw length. No lift labels or verified material-to-lift coupling exist in the current data. This predictor is a data-driven surrogate, with no enforced constitutive law or physics-informed loss.

## Reproduce the checks

```bash
# Full audit: requires raw data and prepared caches. Start Studio first.
.venv/bin/python reports/retest_model.py

# Model, parser and runtime checks; some require prepared caches.
.venv/bin/python -m unittest discover -s tests -p 'test_*.py' -v

# Run while Studio is serving on port 8766.
.venv/bin/python -m unittest discover -s tests -p live_model_app_check.py -v
```

The retest writes a new timestamped evidence folder. It refits frozen settings separately and leaves the delivered model unchanged. Reproducibility checks do not create a new independent holdout.

To prepare data in a fresh checkout, place `TEAM_8_extracted_results_set_1/` in the project root, then run `.venv/bin/python src/data.py`. Preserve `data/split.json`. Training and selection scripts are in `src/`; do not resplit or overwrite final artifacts merely to repeat a check. The original final-scoring command refuses to overwrite an existing final result.

## Project layout

| Path | Purpose |
|---|---|
| `src/` | Preparation, models, selection, scoring and prediction |
| `app/` | Model Studio server, parser and page |
| `data/manifest.json`, `data/split.json` | Source checksums and fixed split |
| `runs/score/final_Svm/` | Delivered model, NumPy weights, predictions and metrics |
| `runs/score/` | Candidate scores and condition diagnostics |
| `reports/retests/` | Timestamped checks, logs, per-case errors and plots |
| `project files/` | Guides, results document and presentation |
| `tests/` | Model, parser, runtime and live-service checks |

Research, assumptions, decisions and open questions are retained in the project notes (under `docs/` in the published export). Older reports describe earlier experiment stages; the final Svm artifact and this README describe the delivered predictor. The separate [AI-GroupChat repository](https://github.com/SaravananRamar06/AI-GroupChat) contains the collaboration app.

## Remaining project work

We still need to confirm physical units, strain/stress definitions and the generating setup; establish a defensible porosity mapping; inspect the actual ANSYS files and results; and define the aerodynamic data and coupling needed for C_L prediction. The completed course report keeps these limits explicit; submission-specific review still needs the professor’s format and requirements. Presentation and model guides are available, but the full material-to-lift workflow has not been validated.
