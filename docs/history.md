# How we got here

The final model is the JC-PINN of 7 November 2026. Everything before it is preserved, unchanged, on branch **`archive/pre-final-2026-11-07`** (commit `ee1f001`).

```bash
git fetch origin archive/pre-final-2026-11-07
git checkout archive/pre-final-2026-11-07
```

| Date (2026) | Stage | Outcome | Where it is now |
|---|---|---|---|
| 24 Oct | Data audit; split of 36 training and 37 test cases (seed 42); first models compared: query MLP, PCA + Gaussian process, PCA-coefficient MLPs, blends. | **Five-network query MLP ensemble** (scikit-learn, 5–16–16–1 tanh, α 0.001) selected; test 0.059 MPa, unseen groups 6.79. | Archive: `runs/score/`, `src/` |
| 24–25 Oct | Model Studio web app, presentation deck, retests, documentation. | First submission materials. | Archive: `app/`, `project files/`, `reports/retests/` |
| 26–27 Oct | Porosity workflow, ANSYS Workbench project, bracket geometry report. CL corrected from "coefficient of lift" to **critical flaw length**. | Bracket tools; the lift path withdrawn. | `bracket/` (ported to the JC-PINN) |
| 31 Oct | Effective-equation qualification: can a closed-form law fit the data? | Both tested families failed qualification. | Archive: `reports/effective_equation_*` |
| 2 Nov | **Single MLP** on the same split, with a Colab notebook. | Test 0.143 MPa, unseen groups 11.90. | Frozen as a baseline in `reports/jc_pinn_20261107/baselines.json` |
| 7 Nov | **JC-PINN**: Equation 1 × learned correction, physics residuals, training-only selection, lock, single test. | Test 0.439 MPa, unseen groups 6.23. | This repository |
| 7 Nov | Post-hoc control, improvement screen, the decision to submit as locked; repository rewritten around the final model. | Final state. | This repository |

## Why the final model is not the most precise one

The five-network MLP of 24 October is more precise on the random test split (0.059 against 0.439 MPa). The final model was chosen for two other reasons:
- it uses the user's governing equation, as the project now requires;
- it was selected by a criterion that also rewards prediction at unseen conditions.

On that criterion, its unseen-group error is about half the single MLP's. It is close to the ensemble's 6.79, although the ensemble's figure was measured on different folds. The earlier models' numbers are kept, with source hashes, in [`baselines.json`](../reports/jc_pinn_20261107/baselines.json), so every comparison in the report can be checked.
