# My AlSi10Mg model, explained simply

## 1. What I built

I built a machine-learning model that predicts the stress response recorded in AlSi10Mg material simulations. AlSi10Mg is an aluminium alloy. My model takes the material conditions and produces a stress–strain curve, so I can examine a response without running a new simulation each time.

**My completed output is a material-response predictor.** The broader project also discusses porosity and aerodynamic coefficient of lift, C_L. That part still needs suitable data and a defined connection to the material response. I cannot obtain lift from the present material files alone.

## 2. The data I started with

I used the professor-supplied simulation data. The matrix lists 108 planned cases, but the supplied folder contains 73 histories, with 2,197,000 rows in total. I kept the original files unchanged.

Each simulation has four conditions: temperature, strain rate, density and shear modulus. Its `STR_STR.OUT` file contains 16 columns, including time, strain components, stress components, temperature and von Mises stress.

For my final model, I use **E11 as the operational axial strain coordinate** and **Svm as the stress target**. Svm is a single measure calculated from the stress components. It differs from axial stress SCAU11, so I do not mix the two targets' evaluation scores.

The available temperatures are 30, 100 and 200, with incomplete data at 200. There are no output histories at 300. The rates are 0.00001, 0.0001 and 0.001. The values suggest engineering units such as MPa and °C, but I still need confirmation from the data owner. I therefore report errors in source stress units.

## 3. How I prepared the curves

Some histories contain 1,000 rows, others 10,000 or 100,000. Training directly on every row would give the longest files much more influence.

I put every curve onto the same grid: **120 equally spaced E11 values between 0.0002 and 0.0999**. I used linear interpolation to find stress at each value. This interval lies inside every available curve's measured range, and every case contributes equally many points.

I matched files to simulation IDs, checked finite values and increasing E11, and saved source checksums. The latest audit confirmed that all 73 prepared curves exactly match interpolation from their source files.

I retained case 60, which has an unusual irregular response. I did not remove it simply to improve the error. It is one reason I treat high-temperature, low-rate predictions cautiously.

## 4. How I separated training and testing

I followed the requested random half-and-half split: **36 training cases and 37 test cases**, using seed 42. The IDs are saved in `data/split.json`.

I split whole simulations. All 120 points from one case remain together. Otherwise, the model could train on part of a curve and be tested on the rest of that same curve, giving a misleading score.

The training half provides 36 × 120 = **4,320 query points**. The underlying evidence is still only 36 simulations. I fitted input and output scaling using training cases only.

I used internal case folds and tests that hide an entire temperature/rate combination for comparison. Earlier exploratory work had already examined all 73 cases, so the final test set is a previously explored holdout, rather than a completely blind test.

## 5. Why I chose this network

I used a **multilayer perceptron**, or MLP. It learns a numerical relationship by adjusting weights and biases. It answers:

> At this temperature, strain rate, density, shear modulus and strain, what Svm value should I predict?

The five inputs are temperature, log10(strain rate), density, shear modulus and E11. Taking the logarithm turns the three rates into −5, −4 and −3, which represents their factor-of-ten spacing clearly.

```text
5 input values → 16 hidden units → 16 hidden units → 1 stress output
```

The hidden layers use tanh, a smooth nonlinear function. The output layer is linear. Each network contains **385 weights and biases**.

I trained five networks with identical structure and different initial seeds, 0–4, and average their predictions. This **ensemble contains 1,925 parameters**. Averaging reduces dependence on one random start; it does not guarantee physical correctness. Whether the course counts the ensemble as one model still needs confirmation.

I compared alternatives, including a network that predicts compressed curve shapes and a PCA/Gaussian-process reference. The final query MLP offered a useful balance of small size and saved condition-holdout performance. The Gaussian process remains a reference in Model Studio. I do not claim the chosen network is universally best.

## 6. What happens during training

I first standardise the five inputs using training means and standard deviations. This puts quantities such as temperature, modulus and strain onto comparable numerical scales. I also standardise the training stresses.

The network predicts stresses and adjusts its weights to reduce squared error. I use **L-BFGS** for optimisation, with **L2 penalty alpha = 0.001** to discourage unnecessarily large weights. Each fit allows up to 5,000 iterations with tolerance 1e-9; the optimiser determines when to stop.

I save the fitted networks and scaling values together. I also keep a NumPy-only copy of the same weights. Both versions produce the same predictions in the checked environment. The NumPy version changes how inference runs, not the trained relationship.

This is a **data-driven surrogate**. I did not enforce a constitutive law, solve physics equations inside the loss, or train a physics-informed network.

## 7. How I get a prediction

For example, I enter:

```text
temperature = 100
strain rate = 0.0001
density = 2619
shear modulus = 24541
```

The program changes the rate to log10(0.0001) = −4. It combines these four conditions with each of the 120 strains, applies the saved scaling and sends the queries through all five networks. It averages their outputs and reverses the stress scaling.

The result is a curve. For this example, predicted stress is about **136.21 at the start of the grid**, **99.42 at E11 = 0.05**, and **75.23 at the end**, in source stress units.

Exactly 0.05 lies between two grid points, so that value is interpolated from the predicted curve. The nearby grid point at E11 ≈ 0.049631 gives 99.63293. Different strain locations explain the different stress values.

Model Studio extracts the conditions from my typed request and passes them to the saved model. Its parser uses fixed rules. It does not use a language model to invent predictions. I check its displayed defaults whenever I omit an input.

## 8. How I tested it again

On 25 October 2026, I reran the source audit and evaluated the saved model on the 37 test cases. For each curve, RMSE is the square root of the average of its 120 squared prediction errors. I then average the 37 curve RMSEs.

| Test measure | Fresh result |
|---|---:|
| Mean curve RMSE | **0.05908515** |
| Median curve RMSE | 0.05056666 |
| Worst curve RMSE | 0.11330618, case 45 |
| Mean absolute error | 0.04899859 |
| Largest absolute error at a test point | 0.28832028 |

These are source stress units. An RMSE of 0.059 is an error magnitude, not “99.941% accuracy.”

I separately refitted the original configuration on the same 36 training cases. It took about **17.3 seconds** on this run and reproduced every saved weight and prediction exactly, without warnings. **All 13 unit tests and 3 live Studio tests passed.** The delivered model files were unchanged.

Studio's checks confirmed the final artifact, a saved test prediction, invalid-rate handling, lift-request handling and extrapolation warnings. These checks establish software behaviour, not physical validity.

## 9. What the score means

The small random-split error means the model closely reproduces these supplied test curves when related conditions are represented in training. New operating conditions are harder.

The saved training-side three-fold CV mean RMSE is **1.1583**. The saved mean across nine held-out temperature/rate groups is **6.7936**, rising to **23.5251** for the 200 / 1e-5 group. These are earlier diagnostic results, not newly refitted condition tests in this audit.

I do not trust extrapolation outside the supplied ranges, especially temperature 300, where there are no outputs. Being inside the numerical range is also not a guarantee: coverage is sparse at some conditions, and the network has no physical constraint preventing unrealistic output.

## 10. What is finished and what remains

I have completed preparation, the fixed split, model comparisons, the saved material predictor, inference, Model Studio, reproducibility checks, plots and presentation files. My current model predicts the supplied Svm response along E11.

I still need confirmation of physical units and strain/stress definitions, a justified porosity interpretation, and the actual ANSYS files and results. These histories do not establish a conventional initial elastic segment. I have not validated transfer into a structural simulation.

For C_L, I need an aerodynamic setup and suitable labels or an agreed physical calculation. I do not use fracture equations as a definition of lift coefficient. The material-to-structure-to-aerodynamics chain remains future work.

## A short explanation I can give aloud

“I used 73 supplied AlSi10Mg simulations and converted each curve into 120 points. I kept 36 whole cases for training and 37 for testing. My model uses temperature, logarithmic strain rate, density, shear modulus and strain to predict von Mises stress. I average five small neural networks to form the curve. The latest mean curve RMSE is 0.0591 in source stress units, and a separate refit reproduces the saved model exactly. It works well on this random split, but errors increase for unseen conditions. Lift prediction and physical validation need additional work.”

## Files I use

- Model and metrics: `runs/score/final_Svm/`
- Start Studio: `.venv/bin/python app/server.py`, then open `http://127.0.0.1:8766`
- Repeat the audit: `.venv/bin/python reports/retest_model.py` (requires raw data, prepared caches and the running Studio for live checks)
- Fresh evidence: `reports/retests/20261025T172218Z/`
- [Readable test results](<Model test results.md>) and the existing `model_guide` files give further detail.
