# Codex selected-model reload check

Checked 24 October 2026 using `.venv/bin/python reports/check_selected_artifacts.py`.

All four selected model files reproduce their saved 37-case predictions and mean/median/worst RMSE values after reload. No models were fitted or modified.

| Target | Model | Mean curve RMSE | Worst curve RMSE |
| --- | --- | ---: | ---: |
| SCAU11 | query MLP | 0.095697 | 0.308257 |
| SCAU11 | PCA + GP | 0.057757 | 0.156833 |
| Svm | query MLP | 0.059085 | 0.113306 |
| Svm | PCA + GP | 0.056517 | 0.146924 |

Stress units remain unconfirmed. Results use the cached 120-point curve grid. This verifies saved inference/metric consistency, not independent training reproduction, source-data extraction, physical validation, or a blind final test. The earlier all-data selection history still applies.
