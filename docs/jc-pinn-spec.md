# JC-PINN model specification

Full technical specification of the delivered Johnson–Cook-governed model (run `reports/jc_pinn_20261107`, locked 7 November 2026). Every value is read from `configs/jc_pinn.json` and the saved run files; see [jc-pinn.md](jc-pinn.md) for the explanation and [the run report](../reports/jc_pinn_20261107/README.md) for full tables.

## 1. Identity
| Item | Value |
|---|---|
| Name | JC-PINN: Johnson–Cook-governed physics-informed network |
| Task | Predict von Mises stress `Svm` (MPa, inferred) along axial strain `E11` for AlSi10Mg at given T, strain rate, density (porosity), G |
| Type | Hybrid grey-box regressor: physical-law backbone × neural correction, 5-member ensemble |
| Framework | PyTorch (float64, CPU); inference also in pure NumPy from `equation.json` |
| Version | Run `reports/jc_pinn_20261107`, locked 7 Nov 2026; produced by `src/jc_pinn.py` at commit `c3ee1a6` (sha256 `d3f66db6…`, recorded in `selection_lock.json`). Later commits changed only plotting, wording and reporting helpers, not the model or training. See also [`ERRATA.md`](../reports/jc_pinn_20261107/ERRATA.md). |

## 2. Governing equation (backbone)
`σ_JC = [A − B·ε^n] · [1 + C·ln(ε̇/ε̇0)] · [1 − T*^m] · [G/G0]^q · [1 − φ]^r`

| Constant (fixed) | Value |
|---|---|
| ε̇0 (reference rate) | 1×10⁻⁵ s⁻¹ |
| T_r / T_m | 30 °C / 600 °C, with T* = (T − 30)/570, clipped at 0 |
| G0 | 25 300 MPa |
| ρ0 | 2700 kg/m³, with φ = 1 − ρ/2700 |
| ε_ref | 0.1, with B = A·β/0.1ⁿ |

| Fitted constant | Bounds | Equation 1 alone (calibrated) | Inside JC-PINN (5-member mean) | Per-member range |
|---|---|---:|---:|---|
| A | 1 – 2000 | 148.77 | 87.72 | 81.2 – 94.4 |
| B (via β ∈ [0, 0.99]) | A − Bεⁿ > 0 for ε ≤ 0.1 | 526.23 | 424.64 | 397.0 – 452.8 |
| n | 0.05 – 5 | 0.8276 | 0.9415 | 0.924 – 0.958 |
| C | 0 – 2 | 0.02925 | 0.05179 | 0.017 – 0.082 |
| m | 0.05 – 20 | 1.1132 | 2.742 | 1.02 – 5.38 |
| q | 0 – 10 | 0.7173 | 0.9112 | 0.752 – 1.064 |
| r | 0 – 20 | 0 (at bound) | 2×10⁻⁵ | 2×10⁻⁵ |

Calibration: SciPy `least_squares` (trf, 3-point Jacobian), 8 starts (seed 42), tolerances 1e-12, max 20 000 evaluations.
Bounded constants are mapped through a sigmoid so that training keeps them inside their bounds.

## 3. Neural correction δ
| Item | Value |
|---|---|
| Inputs (5) | T (°C), log₁₀ ε̇ (s⁻¹), ρ (kg/m³), G (MPa), E11 |
| Input scaling | z = (x − μ)/s using training statistics: μ = [107.22, −3.9167, 2598.71, 24371.98, 0.05005], s = [68.094, 0.82916, 89.262, 850.39, 0.029022] |
| Architecture | Linear 5→16, tanh, Linear 16→16, tanh, Linear 16→1 |
| Parameters | 385 per member (W1 16×5 + b1 16 + W2 16×16 + b2 16 + w3 16 + b3 1) |
| Initialisation | PyTorch default for the hidden layers (seed = member seed); **output layer zeros**, so the untrained model = Equation 1 |
| Output | σ = σ_JC(θ) · exp(δ), a relative multiplicative correction that keeps stress positive |

## 4. Ensemble and totals
| Item | Value |
|---|---|
| Members | 5 (seeds 0, 1, 2, 3, 4), each with its own jointly trained θ |
| Combination | Geometric mean: σ = exp( (1/5) Σ_k [ln σ_JC(θ_k) + δ_k] ) |
| Trainable parameters | 5 × (385 + 7) = **1,960** (1,925 network + 35 constants) |
| Stored file | `equation.json`, 71 kB, with every weight, constant and scaler; NumPy-only inference |
| Inference cost | about 2.2k multiply-adds per member per point; a 120-point curve is milliseconds on a CPU or in a browser |

## 5. Training data and protocol
| Item | Value |
|---|---|
| Source | Professor's `TEAM_8_extracted_results_set_1`: 108 planned, 73 available simulations (none at 300 °C) |
| Target / strain | `Svm` / `E11`, interpolated onto 120 points, E11 = 0.0002 – 0.0999 (equal weight per case) |
| Split | Fixed random 50/50 by simulation, seed 42: **36 training / 37 test** (`data/split.json`) |
| Training points | 36 × 120 = 4,320 (from 36 independent simulations) |
| Covered range | T 30 – 200 °C; rate 1e-5 – 1e-3 s⁻¹; φ 0 – 7.85 %; G 23 314 – 25 300 MPa |

## 6. Loss and optimiser
| Item | Value |
|---|---|
| Loss | mean(((σ̂ − σ)/s_y)²) + λ·mean(R²) + (α/N)·Σ‖W‖², with s_y = 27.376 MPa and N = 4320 |
| Physics residual R (tested) | level: δ; trend: ∂δ/∂z for T, rate, ρ, G (autograd), at 4,096 scrambled-Sobol collocation points over T 30–300 °C |
| **Selected** | physics none, **λ = 0**, constants **joint** (trained with the network) |
| Weight decay | α = 1 (weights only, not biases); fixed by a training-fold development check |
| Optimiser | Adam, lr 0.005, 1,500 full-batch steps; then L-BFGS (strong-Wolfe, history 50, max 2,500 iterations, grad tol 1e-10, change tol 1e-14) |
| Final losses (members 0–4) | total 0.00278 – 0.00283; data 0.00039 – 0.00041; weight term 0.00238 – 0.00243; all used 2,500 L-BFGS iterations; 12–17 s per member |
| Determinism | float64, 1 thread per worker, fixed seeds; the notebook's FAST mode reproduces the weights exactly in the same environment |

## 7. Model selection
| Item | Value |
|---|---|
| Candidates | 14 = physics {none: 0; level: 0.001, 0.01, 0.1; trend: 0.0001, 0.001, 0.01} × constants {frozen, joint} |
| Splits | 3 case folds (KFold, seed 42) + 9 temperature/rate group holdouts, training cases only |
| Score | ½ × (case-CV mean curve RMSE + mean group-holdout RMSE); ties prefer larger λ, then frozen |
| Effort | 504 fits (14 × 12 × 3 seeds), 37.1 min on 4 CPU workers |
| Winner | none / λ 0 / joint: CV 2.098, groups 6.235, score 4.166 |
| Lock | `selection_lock.json` with SHA-256 of `equation.json`, written before any test file is read |

## 8. Performance (mean per-curve RMSE, MPa inferred)
| | Training fit | Case CV | Unseen T/rate groups | **Test (37)** |
|---|---:|---:|---:|---:|
| JC-PINN | 0.356 | 2.098 | 6.235 | **0.4386** (median 0.395, worst 0.841, MAE 0.327, 0.42 % of stress) |
| Equation 1 alone | – | 10.24 | 13.95 | 7.366 |
| Equation 1 switched off (control) | – | 1.315 | 5.629 | 0.3375 |
| Single MLP (2 Nov) | – | 2.174 | 11.90 | 0.1427 |
| 5-net MLP ensemble (24 Oct) | – | – | 6.79 | 0.0591 |

* The hardest unseen group is 200 °C / 1e-5 s⁻¹ (case 60): 17.1.
* Mean |δ| on the test set is 0.47 (max 0.92).
* **Sign checks** on 2,579 points in the data region: 0 % violations for ∂σ/∂ε ≤ 0, ∂σ/∂T ≤ 0, ∂σ/∂G ≥ 0 and ∂σ/∂ρ ≥ 0. Between 200 and 300 °C (no data), 2.5 % of points have the wrong density sign.

## 9. Validity and limits
* **Valid range:** 30–200 °C, rate 1e-5 to 1e-3 s⁻¹, φ 0–7.85 %, G 23 314–25 300 MPa, E11 0.0002–0.0999. Values between the levels are interpolated.
* **200–300 °C** is unvalidated extrapolation: there is no data there, and λ = 0 means no physics penalty either.
* **Not a blind test:** the test set was explored in earlier project stages. Group errors are part of the selection score, so they are slightly optimistic.
* **Units and validation:** units are inferred as MPa. The model reproduces the simulations, not experiments.
* **Constants:** quote the "Equation 1 alone" set as the calibrated law. The joint constants only mean something together with the network.
* **Control result:** the same network without Equation 1 is more accurate, so the separable equation adds interpretability, not accuracy.

## 10. Files and reproduction
* **Model and run:**
  * code `src/jc_pinn.py`;
  * settings `configs/jc_pinn.json`;
  * saved model `reports/jc_pinn_20261107/equation.json`;
  * Equation 1 alone `equation_only.json`;
  * metrics `results.json`;
  * verifier `scripts/verify_jc_pinn.py` (all checks pass, reproduction 2.6e-13);
  * tests `tests/test_jc_pinn.py` (12; 51 in the whole suite).
* **Notebooks:** `notebooks/jc_pinn_explained.ipynb` (full explanation, saved with outputs) and `notebooks/jc_pinn_colab.ipynb` (PREDICT / FAST / FULL).
* **Viewer:** `reports/jc_pinn_20261107/model_viewer.html`.
* **Software of the run:** Python 3.13.18, torch 2.15.0, numpy 2.5.4, scipy 1.18.1, scikit-learn 1.7.2, matplotlib 3.11.2.
