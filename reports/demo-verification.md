# Model demonstration verification

24 October 2026, Codex. Final saved artifact: `runs/score/final_Svm/model.joblib`. No fitting or hyperparameter changes occurred.

- Direct reload reproduced all 37 archived test predictions with maximum absolute difference 0.0; mean per-curve RMSE 0.05908515170863245.
- Independent case-42 check: temperature 100, rate 1e-4, density 2619, G 23313.95; full 120-point curve RMSE 0.10614619878284123.
- The original demo's “strain 0.05” point used the nearest common-grid strain, 0.049631092436974784: simulation 96.72217941, prediction 96.52044525. Corrected `src/demo.py` interpolates point values to exactly 0.05: simulation 96.50403616, prediction 96.30137966. This changes a display label/calculation, not the curve RMSE.
- `reports/check_demo_case.py` reproduces the independent check and `figures/demo_case42.png`, showing both curves and their residual so small differences remain visible.
- The room now supports named local PNG artifacts. The figure was copied into its ignored artifact directory; actual live PNG response was verified after a coordinated restart. The project figure/script are published separately with the model.

Units remain inferred. These test cases were excluded from final fitting, but earlier exploration involved the eventual holdout. Comparison with supplied simulations is not experimental/physical validation. MLP/GP agreement at an intermediate condition is mutual consistency without known truth there. Case 60's irregularity has no confirmed numerical/physical explanation. Negative stress at 300 is an invalid extrapolation that the app warns about; the model does not refuse to generate it. No lift predictor is demonstrated.

User later asked to continue tomorrow. Pending: a complete presentation and LaTeX report, investigate the reported Model Studio failure, and focused UI refinement without over-engineering. No further work on those items was started during cleanup.
