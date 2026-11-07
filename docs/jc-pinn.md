# JC-PINN: our Johnson–Cook equation as the governing law of the material model

7 November 2026. This guide explains the model built from **Equation 1** of our customised Johnson–Cook
notes: what each part does, why it is built this way, how it was trained and tested, and what we can and
cannot claim. Numbers come from [`reports/jc_pinn_20261107/`](../reports/jc_pinn_20261107/README.md).

## 1. The governing equation

$$
\sigma_{JC}=\underbrace{\left[A-B\,\varepsilon_p^{\,n}\right]}_{\text{strain}}
\underbrace{\left[1+C\ln\dot\varepsilon^*\right]}_{\text{rate}}
\underbrace{\left[1-T^{*m}\right]}_{\text{temperature}}
\underbrace{\left[\tfrac{G}{G_0}\right]^{q}}_{\text{shear modulus}}
\underbrace{\left[1-\phi\right]^{r}}_{\text{porosity}}
$$

| Symbol | Meaning in our model | Value / source |
|---|---|---|
| $\varepsilon_p$ | axial strain `E11` (monotonic in all 73 cases) | user decision, 7 Nov |
| $\dot\varepsilon^*$ | strain-rate ratio $\dot\varepsilon/\dot\varepsilon_0$ | $\dot\varepsilon_0=10^{-5}$ s⁻¹ (slowest rate), so $\ln\dot\varepsilon^*=0,\ 2.30,\ 4.61$ |
| $T^*$ | homologous temperature $(T-T_r)/(T_m-T_r)$ | $T_r=30$ °C, $T_m=600$ °C, so $T^*=0,\ 0.123,\ 0.298$ |
| $G/G_0$ | shear-modulus ratio | $G_0=25300$ MPa, so ratios 1, 0.97, 0.9215 |
| $\phi$ | porosity $1-\rho/\rho_0$ | $\rho_0=2700$ kg/m³, so φ = 0, 3, 7.85 % in the data; study point φ = 4 % (ρ = 2592) |
| A, B, n | strain term: A is the stress scale, B and n set how fast stress falls with strain | fitted |
| C | rate sensitivity | fitted, C ≥ 0 |
| m | thermal-softening exponent | fitted |
| q, r | shear-modulus and porosity exponents | fitted, q, r ≥ 0 |

Note the **minus sign** in $A-B\varepsilon^n$. Classic Johnson–Cook has $A+B\varepsilon^n$ (hardening), but every one of the
73 supplied histories *softens*: its final stress is below its initial stress. Our version matches that.

**Bounds** keep the constants physical. B is written as $B=A\beta/0.1^n$ with $0\le\beta\le0.99$, so $A-B\varepsilon^n>0$ for every strain
up to 0.1. C, q and r are non-negative, because the data never shows stress rising with porosity or falling with G.
Without the bounds the fit returned r = −0.027: a porosity effect of the wrong sign.

## 2. Why Equation 1 alone is not enough

Equation 1 is a **product of separate terms**. Temperature, rate, G and porosity therefore only scale the curve up or
down; they cannot change its *shape*. The data's shape does change. Across the 36 training curves, the stress at 10 % strain divided by the
starting stress is:

| Condition | 30 °C, 1e-5 /s | 30 °C, 1e-3 /s | 200 °C, 1e-4 /s | 200 °C, 1e-5 /s (case 60) |
|---|---:|---:|---:|---:|
| End/start stress | 0.71 | 0.49 | 0.20 | 0.06 |

Calibrated on its own, Equation 1 therefore misses the training curves by about 10 % on average, even when fitted to them
directly (mean RMSE 8.95 MPa, case 60 worse than 70 %). This is a property of the separable form, not a fitting failure.

## 3. How the model uses the equation

$$
\hat\sigma=\sigma_{JC}(A,B,n,C,m,q,r)\cdot\exp\big(\delta(T,\log_{10}\dot\varepsilon,\rho,G,\varepsilon)\big)
$$

* **Backbone.** Equation 1 carries the physics: trends with temperature, rate, G and porosity, and the softening shape.
* **Correction.** δ is a small neural network (5 inputs → 16 → 16 → 1, tanh, **385 weights**). Its last layer starts at zero, so
  before training the model **is exactly Equation 1**. Training lets δ learn only what Equation 1 cannot explain: the
  condition-dependent curve shape. exp(δ) is a multiplicative correction factor (exp(δ) = 0.9 means 10 % below Equation 1)
  and keeps the predicted stress positive.
* **Physics loss (the "PI" in PINN).** Training minimises

  $$\mathcal L=\underbrace{\overline{\left(\tfrac{\hat\sigma-\sigma_{data}}{s_y}\right)^2}}_{\text{data}}+\lambda\,\underbrace{\overline{R^2}}_{\text{physics}}+\underbrace{\tfrac{\alpha}{N}\textstyle\sum W^2}_{\text{weight decay}}$$

  The physics residual R is evaluated at 4,096 *collocation points*. These are input combinations spread over the whole planned design box
  (30–300 °C, all rates, densities, G and strains), including the 35 conditions with no simulation file. No stress values are used there;
  the points only say "obey the equation here". Two residual forms were compared:
  * **level**: R = δ = ln σ̂ − ln σ_JC, so the prediction should stay close to Equation 1;
  * **trend**: R = ∂δ/∂(T, log rate, ρ, G), computed by automatic differentiation. The model's *sensitivities* to temperature, rate, density
    and G should equal Equation 1's, while the strain-shape correction stays free. If selected, it would make the temperature trend beyond 200 °C Equation 1's.
* **Constants frozen or joint.** "Frozen" calibrates A…r on the training cases first and keeps them fixed, so the network learns only δ.
  "Joint" also lets training adjust the constants. Both were tested.

**Why rebuild rather than reuse the old network's weights?** scikit-learn's MLP cannot take a physics loss, and the network's job
changed from "predict stress" to "predict the correction to Equation 1", so the old weights do not transfer. The earlier models are
kept as baselines.

## 4. Training and testing without peeking

1. **Same split as every earlier model:** 36 training and 37 test simulation cases (seed 42). All 120 points of a curve stay together,
   and each curve counts equally.
2. **Selection on the 36 training cases only.** 14 settings: physics none / level (λ = 0.001, 0.01, 0.1) / trend (λ = 0.0001, 0.001, 0.01),
   each with frozen or joint constants. Each setting is scored on:
   * three **case folds**: hide a third of the training cases and predict them;
   * nine **condition holdouts**: hide every case of one temperature/rate combination and predict it.

   The **balanced score** we chose is the average of the two errors, so a setting has to interpolate *and* generalise to unseen
   conditions. Scalers and the Equation 1 constants are refitted inside every split. Each setting is a 3-seed ensemble.
3. **Lock, then test once.** The selected setting is refitted on all 36 training cases as a 5-seed ensemble. Its full equation is saved and
   its SHA-256 hash written to `selection_lock.json` **before** the code reads any of the 37 test files. The test score is computed once.
4. **Independent check.** `scripts/verify_jc_pinn.py` re-implements Equation 1 and the network in plain NumPy, without importing the model code, and
   recomputes every prediction and metric.

Two settings were fixed beforehand from development checks on the training folds only, and are recorded in `configs/jc_pinn.json`:
* weight decay α = 1, because a weak α let exp(δ) blow up when extrapolating;
* the trend residual, added because the level penalty made fold errors worse.

## 5. Results

All errors are mean per-curve RMSE in source stress units (MPa inferred). Full tables:
[`reports/jc_pinn_20261107/README.md`](../reports/jc_pinn_20261107/README.md).

**What the training-only selection chose:** Equation 1 as the backbone, constants trained jointly with the correction,
and **no extra physics penalty** (λ = 0). Every level and trend penalty raised both the case-CV and the unseen-group error.

| Model | Case-CV (training) | Unseen T/rate groups (training) | **Test, 37 cases** |
|---|---:|---:|---:|
| Equation 1 alone (7 constants) | 10.24 | 13.95 | 7.37 |
| **JC-PINN (Equation 1 backbone + correction)** | 2.10 | 6.23 | **0.439** |
| Same network, Equation 1 switched off (control) | 1.32 | 5.63 | 0.338 |
| Single MLP, 2 Nov | 2.17 | 11.90 | 0.143 |
| 5-net MLP ensemble, 24 Oct | (other folds) | 6.79 | 0.059 |

The calibrated law on its own, fitted to the 36 training cases:

**A = 148.77, B = 526.23, n = 0.828, C = 0.0292, m = 1.113, q = 0.717, r = 0.**

What this means:

1. **The JC-PINN is 17 times more accurate than Equation 1 alone.** On the test cases the error falls from 7.37 to 0.44, about 0.4 % of
   the stress. The network has learned the condition-dependent curve shape that the separable equation cannot represent.
2. **The equation itself does not add accuracy.** The control has the same network and training with Equation 1 switched off, and it is
   better on every measure. The JC-PINN's numbers are even slightly optimistic, because it was the best of 14 settings. The gain over the
   earlier MLPs on unseen conditions (6.2 against 11.9 for the single MLP) comes from the training recipe: strong weight decay and log-space
   output. Equation 1 in this separable form is **not supported** as the governing law of these simulations.
3. **Trade-off.** On the professor's random 50/50 test the earlier MLPs remain more precise (0.143 and 0.059 against 0.439). The balanced
   criterion we chose traded some interpolation precision for better behaviour on unseen temperature/rate combinations.
4. **Porosity.** r settles at 0, so Equation 1's porosity term finds no usable effect. Density changes stress by only about 0.2 %
   in these simulations. The small density effect the model does have comes from the network, and it has the physical sign
   (stress falls as porosity rises) at every checked point between 30 and 200 °C.
5. **Physical sign checks:** across 2,579 collocation points between 30 and 200 °C, there are no points where stress rises with strain or temperature,
   or falls with G or density. Between 200 and 300 °C there is no data and no physics penalty. These curves are unvalidated
   extrapolation, and 2.5 % of points there have the wrong density sign.
6. **Constants inside the JC-PINN** (A = 87.7, m between 1.0 and 5.4 across seeds) are only meaningful together with the network. With joint
   training and λ = 0, how the stress is split between the equation and the correction is not unique. Quote the "Equation 1 alone"
   constants as the calibrated law.
7. **Case 60** (200 °C, 1e-5 /s) collapses abruptly. Every model misses it when it is held out: 17.1 for the JC-PINN, against 42.4 for
   Equation 1 alone.

**Reproducibility:**
* `scripts/verify_jc_pinn.py` independently reproduces every prediction (to 2.6e-13) and every metric, and checks the protocol.
* The notebook's FAST mode, run locally with nbclient, reproduced the locked model weight for weight, with test RMSE 0.43862877347121765.
* Hosted Colab and Kaggle runs still need to be done on your account.

## 6. How to run it

* **Read everything in one place:** `notebooks/jc_pinn_explained.ipynb`. It explains the data, the equation, the model, the loss, training, selection, the test results, the control and predictions, computing every number live. It is saved with its outputs and runs in about 20 s without the raw data. Part 9 can retrain from the professor's folder.
* **Google Colab / Kaggle:** open `notebooks/jc_pinn_colab.ipynb`.
  * `MODE = 'PREDICT'` plots curves from the saved equation without any data, e.g. 4 % porosity.
  * `MODE = 'FAST'` refits the selected setting and scores the test cases in a few minutes.
  * `MODE = 'FULL'` repeats the whole selection.

  On Colab, keep `TEAM_8_extracted_results_set_1` (or its ZIP) in My Drive. If it was shared with you, add a shortcut to My Drive.
  On Kaggle, add it as a Dataset input. The notebook finds the folder and checks that the curves match the verified run.
* **Local:** `pip install -r requirements-pinn.txt`, then
  `python src/jc_pinn.py --raw TEAM_8_extracted_results_set_1 --output reports/NEW --mode full`.
  Verify the result with `python scripts/verify_jc_pinn.py reports/NEW`.

## 7. Questions to expect in the viva

* **Is this a PINN?** Yes, a constitutive (material-point) PINN. The loss contains the residual of a governing equation, evaluated at collocation
  points without data, and the trend residual uses automatic-differentiation derivatives. It is not a 3D equilibrium PINN, because the data
  contain no spatial fields.
* **Why not just use Equation 1?** It gives every condition the same curve shape, which costs about 10 % error. The network fixes the shape
  while the equation supplies the trends and the extrapolation behaviour.
* **Why not just use a plain neural network?** Honestly, on these simulations a plain network with the same training was *more*
  accurate (control: test 0.338 against 0.439, unseen groups 5.63 against 6.23). What Equation 1 adds is interpretability: seven named
  constants with physical signs, and a model that starts from a stated law. We tested the equation as a governing law, and the data say
  its separable form is too rigid. That is a result, not a failure of the method.
* **Then why did the physics penalty not help?** Equation 1 is about 10 % off in level, and its fixed curve shape is wrong for hot or
  slow conditions. Pulling the model toward it, or toward its trends, moves predictions away from the simulations. A PINN only helps
  when its governing equation is right where data are missing.
* **What does r tell us about porosity?** In these simulations density changes stress by only about 0.2 %, so the porosity exponent is
  small. The model can say how stress changes between φ = 0 and 7.85 % *in these simulations*; it does not measure real pore effects.
* **Can it predict 300 °C?** It returns a curve, but there is no data above 200 °C. The selected model has no physics penalty, so that curve
  is a free extrapolation of the backbone and network, and it is unvalidated.
* **Limits:**
  * The test cases were explored in earlier project stages, so this is not a blind test.
  * Stress units are inferred as MPa.
  * The model reproduces the supplied simulations; it has not been validated against experiments.
  * Case 60 (200 °C, 1e-5 /s) collapses irregularly and stays the hardest case.
