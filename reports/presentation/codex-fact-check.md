# Codex presentation fact-check

Reviewed 24 October 2026 against the saved data/model artifacts and the corrected `slides.md`. This is a text and numerical review, not visual inspection of the Claude-hosted slide artifact. No models were retrained.

## Verified

- Slide 3: the planned matrix is 4 × 3 × 3 × 3 = 108. Available histories total 73, distributed 27/27/19/0 across the four planned temperatures.
- Slide 7: 5 → 16 → 16 → 1 has 385 trainable parameters including biases; five members total 1,925. Gemini independently checked the loaded architecture and the larger-network CV comparison in `gemini-review.md`.
- Slide 8: saved CV means are 1.158263 (query MLP), 0.664468 (PCA/GP), 0.867100 (blend), 1.535683 (1/T MLP), and 2.004344 (rank-6 PCA MLP). Training-half condition means are respectively 6.793603, 10.961823, 7.983032, 8.609058, and 11.205497. The displayed rounding agrees.
- Independently recomputed the CV means from all 36 saved per-case errors for all six scored candidates, and their condition means from the saved condition summaries. In `src/score.py`, CV averages individual case RMSEs; LOCO first averages cases within each condition, then averages the nine conditions equally. Label both as RMSE, with inferred stress units.
- Slide 9: independently recomputed errors from `runs/score/final_Svm/test_predictions.npz`: 37 cases, mean per-curve RMSE 0.05908515170863245, worst 0.11330617910816165. These agree with `metrics.json`; worst case is 45. This confirms saved predictions/metrics, not a new fit or blind validation.
- Slide 10: the saved all-data Svm/query-MLP diagnostic gives 30: 1.4751–4.2531; 100: 1.9310–7.5917; 200: 7.9976–24.8068. The slide ranges round correctly. This diagnostic differs from training-half selection in slide 8.
- Slide 12: 24.8068 is the query MLP's held-out singleton 200/1e-5 condition (case 60), not a universal error for every model.
- The corrected matrix, parameter terminology, initial-stress wording, model-specific failure, and test-exposure disclosure address the earlier review. The final visual deck must receive these same corrections.

## Remaining changes before final delivery

1. Slide 4 and `numbers.md`: Svm rate effect is **17.45138229448301**, so round to **17.5**, not 17.4. Other effects are 22.114636 (temperature), 3.398966 (G), and 0.188060 (density). Source: `runs/factor_effects.json`. These are discrete adjacent-level matched-pair curve differences; they are not normalised causal importances. The factor step sizes differ.
2. Slides 8–10: use **mean per-curve RMSE**, not undefined “mean error”. Specify slide 8 LOCO as an equal average over condition-level mean RMSEs, distinct from CV's equal case average. The blend beats the query MLP on CV but is not a standalone neural network; say “lowest CV among tested standalone neural-network candidates” rather than an unqualified “among networks”.
3. Slide 6: “test set scored once” must clearly mean the final fixed model's saved scoring step; previous exploratory runs already used these same cases. Keep the early-exposure caveat beside the method.
4. Slides 4, 13, 14: density/G-to-porosity mapping is unconfirmed. Replace “the only porosity-like lever” with “a possible G-sensitivity study; its connection to porosity requires confirmation.” Small density variation alone does not establish porosity insensitivity.
5. Slide 13: prefer “These data alone do not provide targets or a validated physical connection for porosity → lift prediction.” Avoid a universal “no model can learn” claim. G is supplied; absence of a resolved stress-free elastic segment does not imply that no stiffness information exists.
6. Display **units inferred, unconfirmed** near charts/tables or in a consistent footer, as well as the limitations slide. Negative 300-temperature stress is an invalid extrapolation example, not a physical forecast. The numerical example in `numbers.md` needs strain 0.0999 (approximately 0.1) and the density/G settings stated if retained.
7. Credit Gemini's independent review after incorporating it, without attributing model training to Gemini. Keep the numerical source index alongside the deck.

## Verification limits

No experimental material validation, aerodynamic validation, ANSYS verification, unit confirmation, or browser/PowerPoint visual review is established by this check. Earlier full-data exploration means the 37-case result is not a pristine untouched holdout. The material surrogate predicts Svm along the represented loading protocol; it does not supply aerodynamic lift labels.
