# Corrected presentation: slide text (for fact-checking)

Draft by Claude, 24 October 2026. This replaces the submitted deck, which treated CL as critical flaw length and used synthetic porous cells instead of the professor's data. Every number is listed with its source in `numbers.md`.

## 1. Cover
**Learning the stress–strain response of AlSi10Mg from simulations**
A neural-network surrogate trained on the professor's simulation data. This is a corrected presentation, October 2026.
Multiscale Modelling of Materials using Machine Learning. Team: Pranav Parasuram C (ME24B1061), R Saravanan (ME24I1006), Dinesh Y (ME24B1043), Amit Narayan K (ME24I1024).

## 2. What changed since the first presentation
- **CL means coefficient of lift**, not critical flaw length. The first deck answered the wrong question.
- The first deck's numbers came from synthetic porous cells that never used the professor's data.
- This deck uses only the professor's 73 simulations. Every number comes from a saved, re-runnable file.

## 3. The data
- 108 simulations planned; 73 available: 3 temperatures × 3 strain rates × 3 densities × 3 shear moduli.
- Available: 30 °C 27/27, 100 °C 27/27, 200 °C 19/27, 300 °C 0/27.
- Each file is one uniaxial loading history up to strain 0.1, with 1,000, 10,000 or 100,000 rows.

## 4. What drives the curve
Average largest stress change when one input moves by one level (Svm):
- temperature 22.1 MPa;
- strain rate 17.4 MPa;
- shear modulus 3.4 MPa;
- density 0.19 MPa.

Density, often used as a stand-in for porosity, barely changes the response in these simulations.

## 5. The curves soften, and one breaks
- Every curve starts at its peak flow stress at the very first strain step and then softens. There is no elastic segment.
- Case 60, the only 200 °C / 1e-5 simulation, collapses unevenly between strain 0.05 and 0.08.

## 6. The prediction task
- Input: temperature, strain rate, density, shear modulus, and a strain value. Output: the von Mises stress at that strain.
- Each curve is resampled to 120 strain points, so every case counts equally.
- Professor's protocol: a random half of the cases for training (36) and the other half for testing (37), seed 42.
- All settings were chosen inside the 36 training cases.

## 7. The model
- A query MLP: 5 inputs → 16 → 16 → 1 stress value; ask it 120 times to get a curve.
- Five networks trained from different random starts, averaged. Each has 385 weights; together they have 1,925.
- It is kept small on purpose: with 36 training curves, the larger 32×32 networks did worse in validation.

## 8. How the model was chosen
Training half only: 3-fold case cross-validation, and hiding one temperature/rate combination at a time.

| Approach | CV error | Unseen-condition error |
|---|---|---|
| Query MLP | 1.16 | 6.8 (best) |
| PCA + Gaussian process | 0.66 (best) | 11.0 |
| MLP + GP average | 0.87 | 8.0 |
| MLP with 1/T input | 1.54 | 8.6 |
| PCA-coefficient MLP | 2.00 | 11.2 |

The course asks for a neural network. The query MLP is the best network and the best model on unseen conditions. The GP stays as an interpolation reference.

## 9. Result on the 37 test cases
- **0.059 MPa** mean error per curve; worst curve 0.113 MPa.
- A "copy the closest training curve" baseline scores 1.38 MPa, about 23× worse.
- Figure: best, median and worst test curves.

## 10. The harder question: a condition never seen
Hiding one temperature/rate combination entirely gives mean errors of:
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
- **Case 60:** every model fails on this collapse, with about 25 MPa error.
- **GP uncertainty:** the ±2σ band held 0 % of the truth at 200 °C / 1e-3, so it is not a warning signal.
- **Units:** MPa, °C and 1/s are inferred from the numbers, not documented.
- **Test exposure:** settings were explored on all 73 cases before the formal selection, so the test set is not fully blind.

## 13. Coefficient of lift: what is missing
- These simulations contain no lift values, and their curves have no elastic segment. G is only a supplied input.
- So no model can learn porosity → coefficient of lift from them.
- Needed from the professor: the intended CL calculation or data, the operating conditions, and the meaning of porosity in the data.

## 14. Next steps
- Ask the professor the four CL/data questions and what "two models" counts.
- Viva guide built from these saved results.
- Connect to the bracket (ANSYS) only after stress/strain definitions and the material model are confirmed.
- A G-sensitivity study, the only porosity-like lever in this data. It is not measured porosity behaviour.

## 15. Where every number came from
- Data: the professor's 73 simulation files (checksums in `data/manifest.json`).
- Code, models and results: github.com/SaravananRamar06/MMM-ML (private).
- Built with two AI coding agents. Claude analysed the data, trained the models and built the app. Codex researched the approach and independently checked the saved models and metrics.
