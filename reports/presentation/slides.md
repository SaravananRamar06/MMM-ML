# Corrected presentation: slide text (for fact-checking)

Draft by Claude, 24 October 2026; corrected after Codex's and Gemini's fact-checks. This replaces the submitted deck, which treated CL as critical flaw length and used synthetic porous cells instead of the professor's data. Every number is listed with its source in `numbers.md`.

## 1. Cover
**Learning the stress–strain response of AlSi10Mg from simulations**
A neural-network surrogate trained on the professor's simulation data. This is a corrected presentation, October 2026.
Multiscale Modelling of Materials using Machine Learning. Team: Pranav Parasuram C (ME24B1061), R Saravanan (ME24I1006), Dinesh Y (ME24B1043), Amit Narayan K (ME24I1024).

## 2. What changed since the first presentation
- **CL means coefficient of lift**, not critical flaw length. The first deck answered the wrong question.
- The first deck's numbers came from synthetic porous cells that never used the professor's data.
- This deck uses only the professor's 73 simulations. Every number comes from a saved, re-runnable file.

## 3. The data
- 108 simulations planned: 4 temperatures × 3 strain rates × 3 densities × 3 shear moduli. The 73 available cover only 3 of the temperatures.
- Available: 30 °C 27/27, 100 °C 27/27, 200 °C 19/27, 300 °C 0/27.
- Each file is one uniaxial loading history up to strain 0.1, with 1,000, 10,000 or 100,000 rows.

## 4. What drives the curve
Average largest stress change when one input moves by one level (Svm):
- temperature 22.1 MPa;
- strain rate 17.5 MPa;
- shear modulus 3.4 MPa;
- density 0.19 MPa.

Density barely changes the response in these simulations. Whether density or G represents porosity is unconfirmed. (Units inferred.)

## 5. Curves start high and decline; one drops irregularly
- Each record starts at substantial stress from the first strain step and generally declines. No initial elastic segment is visible.
- Case 60, the only 200 °C / 1e-5 simulation, has an irregular drop between strain 0.05 and 0.08. Whether that is physical failure or a numerical issue is not established.

## 6. The prediction task
- Input: temperature, strain rate, density, shear modulus, and a strain value. Output: the von Mises stress at that strain.
- Each curve is resampled to 120 strain points, so every case counts equally.
- Professor's protocol: a random half of the cases for training (36) and the other half for testing (37), seed 42.
- Early exploration used all 73 cases; settings were then re-chosen by cross-validation inside the 36 training cases, and the final fixed model was scored on the test set in one step. Because exploration came first, the test set is not fully blind.

## 7. The model
- A query MLP: 5 inputs → 16 → 16 → 1 stress value; ask it 120 times to get a curve.
- Five networks trained from different random starts, averaged. Each has 385 trainable parameters (weights and biases); together they have 1,925.
- It is kept small on purpose: with 36 training curves, the larger 32×32 networks did worse in validation.

## 8. How the model was chosen
Training half only: 3-fold case cross-validation, and hiding one temperature/rate combination at a time.

| Approach | 3-fold CV RMSE (training half, per-case RMSE, mean over cases) | Hide-one-condition RMSE (training half, mean over 9 conditions) |
|---|---|---|
| Query MLP | 1.16 | 6.8 (lowest) |
| PCA + Gaussian process | 0.66 (lowest) | 11.0 |
| MLP + GP average | 0.87 | 8.0 |
| MLP with 1/T input | 1.54 | 8.6 |
| PCA-coefficient MLP | 2.00 | 11.2 |

The course asks for a neural network. Among the networks tested, the query MLP had the lowest errors, and it was lowest of all five on the training-half hide-one-condition test. The GP stays as an interpolation reference.

## 9. Result on the 37 test cases
- **0.059 MPa** mean RMSE per test curve; worst curve RMSE 0.113 MPa (units inferred).
- A "copy the closest training curve" baseline scores 1.38 MPa, about 23× worse.
- Figure: best, median and worst test curves.

## 10. The harder question: a condition never seen
Hiding one temperature/rate combination entirely (a diagnostic over all 73 cases with the chosen settings, so a different aggregation from slide 8) gives mean errors of:
- 30 °C: 1.5–4.3 MPa;
- 100 °C: 1.9–7.6 MPa;
- 200 °C: 8.0–24.8 MPa.

The random split mostly tests filling in between known conditions, which is easy here. Predicting new conditions is harder.

## 11. Model Studio
- A local chat page: type "compare 30 and 200 C at 1e-3" and get the curves, a table and warnings.
- It runs offline. Its parser is fixed rules, not an AI model.
- It warns outside the trained ranges. At 300 °C the network predicts negative stress, and the page says so.

## 12. What it cannot do
- **No 300 °C:** there is no data, and the model breaks down.
- **Case 60:** with its condition held out, the query MLP's error on case 60 is 24.8 MPa.
- **GP uncertainty:** the ±2σ band held 0 % of the truth at 200 °C / 1e-3, so it is not a warning signal.
- **Units:** MPa, °C and 1/s are inferred from the numbers, not documented.
- **Test exposure:** settings were explored on all 73 cases before the formal selection, so the test set is not fully blind.

## 13. Coefficient of lift: what is missing
- These simulations contain no lift values and no visible elastic segment; G is only a supplied input.
- A porosity → coefficient-of-lift model would need lift data or an agreed calculation.
- Needed from the professor: the intended CL calculation or data, the operating conditions, and the meaning of porosity in the data.

## 14. Next steps
- Ask the professor the four CL/data questions and what "two models" counts.
- Viva guide built from these saved results.
- Connect to the bracket (ANSYS) only after stress/strain definitions and the material model are confirmed.
- A G-sensitivity study; its connection to porosity requires confirmation.

## 15. Where every number came from
- Data: the professor's 73 simulation files (checksums in `data/manifest.json`).
- Code, models and results: github.com/SaravananRamar06/MMM-ML (private).
- Built with AI coding agents. Claude analysed the data, trained the models and built the app. Codex researched the approach and checked saved-model reloads, metrics and the deck's numbers. Gemini (Antigravity) independently reviewed the deck.

## 25 October update: full 20-slide deck

New order: 1 cover · 2 changed · 3 data · 4 drivers · 5 shape · 6 task · 7 model · 8 choice · 9 result · **10 verified** · **11 demo** · 12 unseen · **13 runtime** · 14 studio · 15 limits · 16 lift · **17 built** · **18 workflow** · 19 next · 20 provenance. Studio slide now says "inferred units" and mentions the NumPy runtime; provenance credits updated.

### 10. Checked three ways, by a second agent
- Data audit: all 73 curves, 2,197,000 source rows, match the cache exactly (max diff 0.0). Split disjoint; scaler fitted on 36 training runs only.
- Saved-model reload reproduces every saved test prediction and the 0.0591 mean test RMSE (max diff 0.0).
- Retrain from scratch, same five seeds, 25 s: identical weights and predictions for all 73 runs (max diff 0.0).
- Same machine and libraries; shows the pipeline is correct and repeatable, not that the physics is validated.

### 11. Case 42: the prediction lies on the simulation
- Curve RMSE 0.106 (inferred units). 100 °C, rate 1e-4, density 2619, G 23,314; a test run.
- Error stays between about −0.21 and +0.03, against stresses of 70–135.

### 13. Same weights, lighter code: six times faster to start
- Fresh start (launch + load + one curve) 976 → 163 ms; one warm curve 0.51 → 0.22 ms (2.3×); model file 63 → 18 KB, NumPy arrays instead of pickle.
- All 73 predictions identical. Model Studio now runs on it.
- Batch of 73 curves was slower (21.8 vs 17.3 ms): speed-up claimed for single queries only.

### 17. Six pieces, all in one repository
Trained model · Model Studio · checks and tests (verification/retraining scripts, 13 automated tests, 3 live app checks) · model guide (LaTeX/PDF) · this deck with its number index · AI GroupChat (separate repo).

### 18. One room, several AI agents, every claim checked
- Shared local chat room for the team and the agents (Claude, Codex, Gemini, OpenCode); ownership claimed per file; independent review before work counts as done.
- Example: the first model-guide draft said 64 × 64 ReLU; review of the saved model found 16 × 16 tanh; corrected before delivery.
