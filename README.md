# JC-PINN: our Johnson–Cook equation as the governing law of an AlSi10Mg material model.

**Team 8 · Multiscale Modelling of Materials using Machine Learning · November 2026**

We built a material model for additively manufactured AlSi10Mg, the alloy of our aircraft wing-rib bracket. Given temperature, strain rate, density (porosity), shear modulus and axial strain, it predicts the simulated von Mises stress `Svm` along the strain `E11`, as a 120-point curve.

Its governing law is **Equation 1** of our customised Johnson–Cook notes. A small neural network multiplies it by a learned correction, and starts at zero so the untrained model *is* Equation 1:

$$
\hat\sigma=\underbrace{[A-B\varepsilon^{n}]\,[1+C\ln\dot\varepsilon^{*}]\,[1-T^{*m}]\,[G/G_0]^{q}\,[1-\phi]^{r}}_{\text{Equation 1}}\;\cdot\;\exp\big(\delta(T,\dot\varepsilon,\rho,G,\varepsilon)\big)
$$

- **The correction δ:** a 5–16–16–1 tanh network with 385 weights.
- **The ensemble:** five trained copies are averaged.
- **The constants of Equation 1:** ε̇₀ = 10⁻⁵ s⁻¹, T_r = 30 °C, T_M = 600 °C, G₀ = 25300 MPa, φ = 1 − ρ/2700.

## Results

The model was chosen on the 36 training simulations only, then locked before the 37 test simulations were read, and scored once.

| | Mean curve RMSE on 37 test cases | Unseen temperature/rate groups* |
|---|---:|---:|
| Equation 1 alone | 7.37 MPa | 13.95 |
| **JC-PINN (this model)** | **0.439 MPa** | **6.23** |
| Same network, Equation 1 switched off (control) | 0.338 MPa | 5.63 |
| Plain MLP of 2 Nov, 5–16–16–1 with no Equation 1 (the baseline) | 0.143 MPa | 11.90 |

\*Mean error when every training case of one temperature/rate combination is hidden (training cases only).

- **Accurate:**
  - R² = 0.99952 over 4,440 test points;
  - 94.9 % of points within ±1 MPa;
  - median curve error 0.395 MPa, worst 0.841 MPa (case 10);
  - 17 times better than Equation 1 alone.
- **Precise:**
  - mean signed error +0.009 MPa (17 cases high, 20 low);
  - the five copies agree to 0.104 MPa;
  - training fit 0.356 MPa, close to the test error.
- **Trade-off:**
  - On the random test split, the plain MLP baseline is more precise.
  - At conditions it has never seen, the JC-PINN has about half the plain MLP's error.
- **Porosity:** lowering density from 2700 to 2488 (φ 0 → 7.85 %) lowers stress by only 0.34 %, but it does so in every matched case pair. Equation 1's porosity exponent fitted to 0; the network carries the effect (0.31 % predicted). G acts about 16 times more strongly. See the [porosity analysis](reports/jc_pinn_20261107/porosity_analysis.json).
- **Honest control:** the same network without Equation 1 scored better on every measure. Equation 1 gives the model structure and interpretability (named constants, correct trends, a physical starting point), not accuracy.
- **As a finite-element material** (post-hoc; the model is unchanged):
  - An ANSYS user material (USERMAT) is generated from the locked weights ([`umat/`](umat/README.md)). It reproduces the model offline to 2e-15.
  - In MAPDL 2024 R1, a single element matches the offline result to 1.2e-5 MPa.
  - On the wing-rib bracket at φ = 4 %, with the pin load +P_y imposed as UY = +2 mm on the upper half of the bore, the reaction peaks at 100.5 kN and then softens.
  - Density alone (φ 0 → 7.85 %, G fixed) changes that peak by −0.17 %. G acts about 19 times more strongly per percent.
  - With G coupled by the assumed upper bound G = 25300 (1 − φ) (decision D5; the data's G levels follow it exactly), the peak changes by −3.38 % and the force at 2 mm by −5.12 %. This is a lower estimate of the porosity effect.
  - Halving the element size changes the peak by −9.8 %, against at most 0.7 % for a hardening material. The response after yield is therefore mesh dependent, and the bracket forces are not a converged strength.
  - See [`bracket/ansys_usermat/`](bracket/README.md).
- **Limits:**
  - the test cases were explored in earlier project stages, so this is not a blind test;
  - the data are simulations, not experiments, and nothing is experimentally validated;
  - the units were confirmed by the user, but no documentation of the generator was seen;
  - nothing is validated above 200 °C, and no such data will be added;
  - the strain is total, not plastic;
  - G(φ) is an assumed upper bound (D5), not measured;
  - bracket results after yield depend on the mesh;
  - critical flaw length is not predicted.

## Start here

| | |
|---|---|
| 📓 **Run it** | [`notebooks/jc_pinn_colab.ipynb`](notebooks/jc_pinn_colab.ipynb) runs on Colab, Kaggle or locally. It has three modes: `PREDICT` (no data needed), `FAST` (retrains the final model in minutes) and `FULL` (the whole selection). [Open in Colab](https://colab.research.google.com/github/SaravananRamar06/MMM-ML/blob/main/notebooks/jc_pinn_colab.ipynb) |
| 📖 **Understand it** | [`notebooks/jc_pinn_explained.ipynb`](notebooks/jc_pinn_explained.ipynb) covers the data, the equation, the model, training, selection, the test and the control. It computes every number live and is saved with its outputs. |
| 🎬 **Watch it** | [Explainer video](reports/jc_pinn_20261107/video/jc_pinn_explainer.mp4) (3:02) and [test-results video](reports/jc_pinn_20261107/test_report/video/jc_pinn_test_results.mp4) (3:00), both narrated and captioned. |
| 📄 **Read it** | [Course report](report/report.pdf) (21 pages), [IEEE-format paper](paper/paper.pdf) (5 pages), [slides](<presentation/Final Presentation - Porosity in an AM Wing Bracket (corrected).pdf>) (24 slides; [PowerPoint](<presentation/Final Presentation - Porosity in an AM Wing Bracket (corrected).pptx>), with speaker notes). |
| 🔍 **Explore it** | Interactive [model viewer](reports/jc_pinn_20261107/model_viewer.html), [structure](reports/jc_pinn_20261107/model_structure.html) and [training animation](reports/jc_pinn_20261107/model_motion.html). Download them and open in a browser. |
| 🧾 **Check it** | [Model guide](docs/model-guide.md), [full specification](docs/spec.md), [run report](reports/jc_pinn_20261107/README.md), [test report for all 37 cases](reports/jc_pinn_20261107/test_report/README.md), [errata](reports/jc_pinn_20261107/ERRATA.md). |

## Quick start

**Exam, viva and presentation preparation:** the [team preparation pack](docs/exam-preparation/README.md) covers material science, continuum mechanics, FEA/ANSYS, the JC-PINN, advanced questions, worked examples, a mock exam and a timed team rehearsal. It includes printable PDFs and offline viva practice.

**Colab:**
1. Open the notebook with the link above. Colab asks for GitHub access if the repository is private.
2. Keep `MODE = 'PREDICT'` and run all cells. This plots curves, for example at the 4 % porosity study point, from the saved model, without any data.
3. To retrain, put `TEAM_8_extracted_results_set_1` (or its ZIP) in My Drive, set `MODE = 'FAST'` and run again.

**Kaggle:** upload the notebook. Add the data folder as a Dataset input only if you want to retrain.

**Local:**
```bash
pip install -r requirements.txt
```
```bash
python -c "import sys; sys.path.insert(0, 'src'); import jc_pinn as J; eq = J.load_final_equation('.'); e, s = J.predict_curves(eq, [[100, 1e-4, 2592, 24541]]); print(s[0][:5])"
```
To retrain from the raw data (FAST refits the selected setting, FULL repeats the selection):
```bash
python src/jc_pinn.py --raw TEAM_8_extracted_results_set_1 --output reports/my_run --mode fast --selected-from reports/jc_pinn_20261107/results.json
```

## Verify

```bash
pip install -r requirements-dev.txt
```
```bash
python -m pytest -q
```
```bash
python scripts/verify_jc_pinn.py reports/jc_pinn_20261107
```

The verifier is an independent NumPy re-implementation. It:
- checks the lock fingerprint;
- confirms the test set was read after selection;
- rebuilds every prediction from the saved weights, agreeing with PyTorch to about 1e-13;
- recomputes every metric.

The notebook's FAST mode retrained the model and reproduced the locked weights exactly.

## Repository layout

| Path | Contents |
|---|---|
| `src/jc_pinn.py` | The model: Equation 1, the correction network, training, selection, the lock, scoring and prediction helpers. |
| `configs/jc_pinn.json` | Every setting of the run: constants, bounds, network, training, collocation and selection. |
| `data/` | `manifest.json` (73 cases, with hashes) and `split.json` (36/37, seed 42). The raw data are not in Git. |
| `reports/jc_pinn_20261107/` | The locked run: `equation.json`, `selection_lock.json`, `results.json`, predictions, verification, control, improvement screen, baselines, errata, test report, videos and viewers. |
| `notebooks/` | The Colab/Kaggle notebook and the explained notebook. |
| `report/`, `paper/`, `presentation/` | Course report, IEEE paper and slides. `report/numbers.tex` holds every quoted number, generated from the run. |
| `figures/` | Every figure, written by `scripts/make_figures.py`. |
| `scripts/` | Verifier, test report, control, improvement screen, figure and number builders, notebook builders, USERMAT generator and verifier. |
| `tests/` | Unit tests for the model and the bracket tools. |
| `umat/` | The ANSYS USERMAT (`usermat3d`) generated from the locked weights (J2 radial return, JC-PINN flow stress, consistent tangent), its offline test driver, verification and the MAPDL single-element test. See [umat/README.md](umat/README.md). |
| `bracket/` | The structural side: ANSYS Workbench project, CAD, geometry report, an ANSYS material-card writer and a porosity workflow, both using the JC-PINN. See [bracket/README.md](bracket/README.md). |
| `docs/` | [Model guide](docs/model-guide.md), [spec](docs/spec.md), [decisions](docs/decisions.md), [open questions](docs/open-questions.md), [changelog](docs/changelog.md). |

## Rebuild the documents

```bash
python scripts/write_latex_numbers.py && python scripts/make_figures.py
```
```bash
cd report && latexmk -pdf report.tex && cd ../paper && latexmk -pdf paper.tex
```

The slide deck is rebuilt with `presentation/build/build_corrected.js`; see [presentation/README.md](presentation/README.md).

Team 8's submission folders (both uploads and `submission files/`) are built outside the repository by `python scripts/build_submission.py --commit <rev> --presentation <dir with the Canva exports> --latex-bin <MiKTeX bin>`.

The videos are rebuilt from `reports/jc_pinn_20261107/video/` and `test_report/video/`. That needs `requirements-media.txt`, Playwright and ffmpeg.

## Earlier work

Earlier models and materials are kept, unchanged and out of the way, on branch `archive/pre-final-2026-11-07`. Nothing on `main` depends on them. The one earlier model still quoted here is the 2 Nov plain MLP, as a baseline; its numbers are frozen in `reports/jc_pinn_20261107/baselines.json`.
