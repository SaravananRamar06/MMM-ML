# Codex check of saved modelling artifacts

Checked 24 October 2026, without retraining or unpickling model files.

## Checks passed

- The saved split contains 36 distinct training IDs and 37 distinct test IDs, with no overlap and exact coverage of the 73 available cases.
- Both saved random-split prediction archives contain the same 37 test IDs, 120 increasing strain queries, and finite truth/prediction arrays.
- Recomputed mean/median/worst per-case RMSE and mean per-case MAE agree with the saved JSON values for all six model/target combinations.
- Both selection files list only training IDs in their inner folds, contain three fold labels, and select the lowest recorded CV error within each model family.

## Recomputed scores

| Saved run | Model | Mean curve RMSE | Worst curve RMSE |
| --- | --- | ---: | ---: |
| 20261024-191653_SCAU11 | lookup baseline | 1.374604 | 4.962626 |
| 20261024-191653_SCAU11 | query MLP | 0.139299 | 0.401929 |
| 20261024-191653_SCAU11 | PCA + GP | 0.152428 | 0.348974 |
| 20261024-192106_Svm | lookup baseline | 1.378978 | 4.978788 |
| 20261024-192106_Svm | query MLP | 0.077926 | 0.187577 |
| 20261024-192106_Svm | PCA + GP | 0.153244 | 0.346303 |

## Limits of this check

These checks verify internal consistency of saved split/prediction/metric artifacts. They do not independently reproduce model fitting, establish source-unit definitions, validate original-data target extraction, or validate coefficient-of-lift prediction.
Case 60 belongs to training in this random split. Predictions and errors use the saved 120-point resampling grid, rather than every original solver row.
Only earlier evaluate.py prediction archives were checked here. Selected-setting models/scores need their own saved weights/predictions aligned with the reported configuration.
Later inner-fold selection does not erase the earlier use of all cases during model exploration. Keep that methodological history explicit.
