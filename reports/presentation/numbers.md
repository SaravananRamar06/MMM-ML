# Every number in the deck, with its source

For Codex's fact-check. The paths are in the MMM-ML project. "Svm" means the von Mises stress target. Units are provisional (MPa, °C, 1/s inferred).

| Slide | Number | Value | Source |
|---|---|---|---|
| 3 | planned / available simulations | 108 / 73 | `TEAM_8_extracted_results_set_1/simulation_matrix.csv`; `data/manifest.json` (73 entries) |
| 3 | coverage by temperature | 30 °C 27/27, 100 °C 27/27, 200 °C 19/27, 300 °C 0/27 | `data/manifest.json` + matrix |
| 3 | max strain; rows per file | 0.1; 1,000 / 10,000 / 100,000 | `data/manifest.json` (`e11_max`, `rows`) |
| 4 | one-level effect: T, rate, G, density | 22.1, 17.5, 3.4, 0.19 MPa | `runs/factor_effects.json` → `Svm.*.mean_max_abs_diff` |
| 5 | case 60 collapse strain range | 0.05–0.08 | `figures/Svm/case60_extrapolation.png` (visual) |
| 6 | grid points; split | 120; 36 train / 37 test, seed 42 | `src/data.py` `STRAIN_GRID`; `data/split.json` |
| 7 | params per network / ensemble | 385 / 1,925 | 5·16+16 + 16·16+16 + 16+1 = 385; × 5 |
| 7 | 32×32 worse in validation | CV 1.97–2.05 vs 16×16 1.16–1.20 | `runs/selection_Svm.json` → `history` |
| 8 | CV / train-half LOCO per candidate | mlp 1.158/6.79; gp6 0.664/10.96; blend 0.867/7.98; mlp_phys 1.536/8.61; pca_mlp6 2.004/11.21 | `runs/score/select_<name>_Svm.json` → `cv_mean_rmse`, `loco_mean_rmse` |
| 9 | final test mean / worst | 0.0591 / 0.1133 MPa (case 45) | `runs/score/final_Svm/metrics.json` |
| 9 | lookup baseline (random split) | 1.379 MPa | `runs/20261024-192106_Svm/metrics.json` → `random_split."lookup baseline".mean_rmse` |
| 9 | ratio | 1.379 / 0.0591 = 23.3 | arithmetic |
| 10 | unseen-condition error by temperature | 30 °C 1.5–4.3; 100 °C 1.9–7.6; 200 °C 8.0–24.8 | `runs/loco_chosen_settings.json` (Svm, mlp, all 73 cases, CV-chosen settings) |
| 11 | 300 °C negative stress | −23.7 MPa at ε = 0.1 (300 °C, 1e-5) | live app reply, reproducible via `src/predict.py --temperature 300 --rate 1e-5` |
| 12 | case 60 error | 24.8 MPa | `runs/loco_chosen_settings.json` → `200C_1e-5` |
| 12 | GP ±2σ coverage at 200 °C / 1e-3 | 0 % | `runs/gp_calibration_Svm.json` → `200C_1e-3.coverage_2sigma` |

Note for the checker: slide 10's numbers come from leave-one-condition-out on all 73 cases. That is a diagnostic, not a selection score. Slide 8 uses the training-half-only version from `src/score.py`, which is why the MLP figure there is 6.8, not 7.5.

## Added 25 October (slides 10, 11, 13, 18)

| Slide | Number | Value | Source |
|---|---|---|---|
| 10 | source rows / curves; max diffs | 2,197,000 / 73; 0.0 | `reports/model_verification_20261025.json` (`source_rows`, `raw_cache_max_abs_difference`, `final_reload_max_abs_difference`) |
| 10 | retrain time; weight/prediction diff | 25.0 s; 0.0 / 0.0 | `reports/final_training_reproduction_20261025.json` |
| 11 | case 42 RMSE; inputs | 0.1061; T 100, rate 1e-4, density 2619, G 23313.95 | `figures/demo_case42.png` title (Codex re-ran: 0.1061461988) |
| 11 | error range | about −0.21 to +0.03 | read from the error panel of `figures/demo_case42.png` (visual) |
| 13 | cold start; single curve; batch 73 | 975.7→163.2 ms; 0.511→0.221 ms; 17.3 vs 21.8 ms | `reports/query_runtime_benchmark_20261025.json` |
| 13 | file sizes | 62,940 → 18,462 bytes | same file (`source_bytes`, `numpy_export_bytes`) |
| 17 | tests | 13 unit, 3 live | `python -m unittest discover -s tests -p 'test_*.py'`; `-p live_model_app_check.py` (25 Oct) |
| 18 | guide architecture error | 64×64 ReLU → 16×16 tanh | `reports/model_guide_fact_check_20261025.md` |
