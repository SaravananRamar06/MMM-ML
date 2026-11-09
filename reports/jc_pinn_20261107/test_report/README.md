# JC-PINN test report: 37 held-out simulations

The locked model (`../equation.json`, SHA-256 `73cac41864e4599e…`) was used exactly as saved. There was no refitting, and no setting was chosen using these results. The recomputed score equals the score recorded when the model was locked.
* **Script:** `scripts/test_report_jc_pinn.py`
* **Per-case table:** `per_case.csv`
* **Full numbers:** `test_summary.json`

## Headline (MPa, inferred units)

**Per curve:**
* mean RMSE **0.439**, median 0.395;
* best 0.093 (case 37), worst 0.841 (case 10).

**Per point (4,440 points):**
* R² = **0.99952**;
* mean absolute error 0.327 (0.38 % of stress);
* largest single-point error 2.90;
* 80.2 % of points within ±0.5, 94.9 % within ±1, 98.8 % within ±2.

**Bias:** none. The mean signed error is +0.009; 17 curves come out slightly high and 20 slightly low.

**Along the strain axis:** mean |error| is 0.247 / 0.228 / 0.506 in the early, middle and late thirds. It rises near 10 % strain, where the model under-predicts slightly.

**Precision:** the five copies differ by 0.104 on average, 0.338 at most. A single copy alone scores 0.390–0.478.

## By condition

| Condition | Test cases | JC-PINN | Equation 1 alone | Single MLP |
|---|---:|---:|---:|---:|
| 30 °C, 1e-5 /s | 4 | 0.354 | 11.84 | 0.075 |
| 30 °C, 1e-4 /s | 8 | 0.803 | 6.25 | 0.227 |
| 30 °C, 1e-3 /s | 3 | 0.182 | 2.92 | 0.096 |
| 100 °C, 1e-5 /s | 4 | 0.434 | 9.14 | 0.050 |
| 100 °C, 1e-4 /s | 5 | 0.283 | 3.50 | 0.260 |
| 100 °C, 1e-3 /s | 5 | 0.454 | 3.43 | 0.125 |
| 200 °C, 1e-4 /s | 3 | 0.569 | 13.04 | 0.115 |
| 200 °C, 1e-3 /s | 5 | 0.143 | 11.22 | 0.081 |

The eight worst cases are all at 30 °C, 1e-4 /s. The random split put 8 of that condition's 9 cases in the test set and only 1 in training. Even there, every curve's error stays below 0.85 MPa.

## Against the other models (same 37 cases)

| Model | Mean curve RMSE |
|---|---:|
| Equation 1 alone | 7.366 |
| Curve-copy baseline | 1.379 |
| **JC-PINN** | **0.439** |
| Same network, Equation 1 off | 0.338 |
| Single MLP (2 Nov) | 0.143 |
| 5-network MLP (24 Oct) | 0.059 |

**Case-by-case wins for the JC-PINN:**
* against Equation 1 alone: 37/37;
* against the curve-copy baseline: 24/37;
* against the single MLP: 0/37;
* against the 5-network MLP: 0/37.

## Figures and video

* `all_test_cases.png`: all 37 cases, best to worst.
* `parity_histogram_strain.png`: parity plot, error distribution, and error along strain.
* `model_comparison.png`: the model comparison above.
* `video/jc_pinn_test_results.mp4`: 3:00, 1080p30, neural-voice narration, captions (also as `.srt`) and a quiet synthesised music bed.
  * Rebuild with `python video/build_test.py`, then `node video/render.js build/jc_pinn_test_results.mp4`, run inside `video/`.

## Limits

The 37 test cases were explored in earlier project stages, so this is not a blind test. Agreement is with simulations, not experiments; stress units are inferred as MPa. No setting was chosen using these results.
